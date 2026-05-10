import requests
import concurrent.futures
from firebase_admin import firestore
from requests.exceptions import RequestException, JSONDecodeError
from ..utils.http_utils import requests_with_retry
from src.shared import db, logger
from functools import partial
from src.helper_functions.verkada_integration.utils.check_verkada_device_type import check_verkada_device_type


# --- Generic Helper to Prepare Write Data ---

def _prepare_device_write_data(device_data: dict, org_id: str, id_field: str, serial_field: str, expected_type: str, extra_fields: dict = None):
    """
    Prepares data for Firestore write (update or create) for a single device.
    Queries Firestore to check existence based on serial number.
    Returns a tuple: (action, target, data) or None.
    action: 'update' or 'create'
    target: DocumentReference for update, serial_number for create
    data: Dictionary of fields to set/update
    """
    verkada_device_id = device_data.get(id_field)
    serial_number = device_data.get(serial_field)
    # Special case for env sensors using 'claimedSerialNumber'
    if serial_field == 'claimedSerialNumber' and not serial_number:
        serial_number = device_data.get('serialNumber') # Fallback if needed, adjust if API guarantees one or the other

    if not (verkada_device_id and serial_number):
        logger.warning(f"Skipping {expected_type} due to missing ID ('{id_field}') or Serial ('{serial_field}'): {device_data}")
        return None

    try:
        devices_ref = db.collection('organizations').document(org_id).collection('devices')
        existing_device_query = devices_ref.where('deviceSerialNumber', '==', serial_number).limit(1).get()

        update_data = {
            'deviceVerkadaDeviceId': verkada_device_id,
            'deviceVerkadaDeviceType': expected_type,
        }
        if extra_fields:
            update_data.update(extra_fields) # Add specific fields like siteId

        if existing_device_query:
            # Device exists, prepare for update
            device_ref = existing_device_query[0].reference
            return ('update', device_ref, update_data)
        else:
            # Device doesn't exist, prepare for creation
            create_data = {
                # 'deviceId' will be added during batch creation
                'deviceSerialNumber': serial_number,
                'deviceVerkadaDeviceId': verkada_device_id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'isDeviceCheckedOut': False,
                'deviceCheckedOutBy': '',
                'deviceCheckedOutAt': None,
                'deviceDeleted': False,
                'deviceVerkadaDeviceType': expected_type,
            }
            if extra_fields:
                create_data.update(extra_fields) # Add specific fields like siteId
            # Return serial number for create case, doc id will be generated later
            return ('create', serial_number, create_data)

    except Exception as e:
        logger.error(f"Error preparing write data for {expected_type} SN {serial_number}: {e}")
        return None

# --- Function to Execute Batches ---

def _execute_firestore_batches(write_data_list: list, org_id: str, batch_size: int = 499):
    """Executes Firestore writes in batches based on prepared data."""
    if not write_data_list:
        return 0

    devices_ref = db.collection('organizations').document(org_id).collection('devices')
    batch = db.batch()
    batch_count = 0
    total_processed = 0

    for action, target, data in write_data_list:
        try:
            if action == 'update':
                doc_ref = target # Target is the DocumentReference
                batch.set(doc_ref, data, merge=True)
                total_processed += 1
                batch_count += 1
            elif action == 'create':
                # Target is the serial_number, data is the full doc data
                # We need to generate a new ID here before adding to batch
                doc_ref = devices_ref.document()
                data['deviceId'] = doc_ref.id # Add the generated ID
                batch.set(doc_ref, data)
                total_processed += 1
                batch_count += 1
            else:
                 logger.warning(f"Unknown action '{action}' in write data list.")
                 continue # Skip unknown actions

            if batch_count >= batch_size:
                logger.info(f"Committing batch of {batch_count} operations...")
                batch.commit()
                logger.info("Batch committed.")
                # Start new batch
                batch = db.batch()
                batch_count = 0

        except Exception as e:
            logger.error(f"Error adding operation to batch or committing batch: {e}")
            batch = db.batch()
            batch_count = 0

    # Commit any remaining items
    if batch_count > 0:
        try:
            logger.info(f"Committing final batch of {batch_count} operations...")
            batch.commit()
            logger.info("Final batch committed.")
        except Exception as e:
            logger.error(f"Error committing final batch: {e}")

    return total_processed

# --- Main Sync Function (Modified Structure) ---

def sync_verkada_device_ids(org_id, verkada_bot_user_info: dict, max_workers: int = 10) -> None:
    verkada_org_shortname = verkada_bot_user_info.get("org_name")
    verkada_org_id = verkada_bot_user_info.get("org_id")
    auth_headers = verkada_bot_user_info.get("auth_headers")

    def _sync_generic(api_url: str, api_method: str, api_payload: dict, result_key: str, id_field: str, serial_field: str, device_type_str: str, extra_fields_map: dict = None):
        """Generic function to fetch, prepare, and batch write for a device type."""
        logger.info(f"Starting sync for {device_type_str}...")
        items = []
        try:
            response = requests_with_retry(api_method, api_url, headers=auth_headers, json=api_payload)
            response.raise_for_status()
            json_response = response.json()
            if isinstance(json_response, list):
                items = json_response
            elif isinstance(json_response, dict):
                items = json_response.get(result_key, [])
            else:
                logger.warning(f"Unexpected response format for {device_type_str}. Expected list or dict, got {type(json_response)}")
                items = []

        except RequestException as e:
            logger.error(f"Error fetching {device_type_str} info after retries: {e}")
            return
        except JSONDecodeError as e:
            logger.error(f"Error decoding JSON response for {device_type_str}: {e}")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred during {device_type_str} fetch: {e}")
            return

        if not items:
            logger.info(f"No {device_type_str} found to process.")
            return

        # Filter out intercoms from cameras if applicable
        if device_type_str == "Camera":
            filtered_items = []
            for item in items: # Changed item_data to item
                serial_number = item.get(serial_field)
                if serial_number:
                    actual_type = check_verkada_device_type(serial_number)
                    if actual_type == 'Intercom':
                        logger.info(f"Skipping Camera sync for SN {serial_number} as it's identified as an Intercom.")
                        continue # Skip this item, it will be handled by the Intercom sync task
        
                filtered_items.append(item)
            items = filtered_items

        prepared_writes = []
        worker_func = partial(_prepare_device_write_data,
                              org_id=org_id,
                              id_field=id_field,
                              serial_field=serial_field,
                              expected_type=device_type_str)

        tasks = []
        for item_data in items:
            extra_data = {}
            if extra_fields_map:
                for dest_key, src_key in extra_fields_map.items():
                    val = item_data.get(src_key)
                    if val is not None:
                        extra_data[dest_key] = val
            tasks.append((item_data, extra_data))

        def worker_wrapper(task_args):
            item_data, extra_data = task_args
            return worker_func(device_data=item_data, extra_fields=extra_data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(worker_wrapper, tasks)
            prepared_writes = [result for result in results if result is not None]

        logger.info(f"Prepared {len(prepared_writes)} write operations for {len(items)} fetched {device_type_str}.")
        processed_count = _execute_firestore_batches(prepared_writes, org_id)
        logger.info(f"Finished processing {device_type_str}. Processed {processed_count} Firestore operations.")

    sync_tasks_definitions = [
        {
            "api_url": f"https://vappinit.command.verkada.com/__v/{verkada_org_shortname}/app/v2/init",
            "api_method": "post", "api_payload": {"fieldsToSkip": ["permissions"]}, "result_key": "cameras",
            "id_field": "cameraId", "serial_field": "serialNumber", "device_type_str": "Camera"
        },
        {
            "api_url": f"https://vcerberus.command.verkada.com/__v/{verkada_org_shortname}/access/v2/user/access_controllers",
            "api_method": "get", "api_payload": {}, "result_key": "accessControllers",
            "id_field": "accessControllerId", "serial_field": "serialNumber", "device_type_str": "Access Controller"
        },
        {
            "api_url": f"https://vsensor.command.verkada.com/__v/{verkada_org_shortname}/devices/list",
            "api_method": "post", "api_payload": {"organizationId": verkada_org_id, "favoritesOnly": False}, "result_key": "sensorDevice",
            "id_field": "deviceId", "serial_field": "claimedSerialNumber", "device_type_str": "Environmental Sensor"
        },
        {
            "api_url": f"https://vnet.command.verkada.com/__v/{verkada_org_shortname}/devices/list",
            "api_method": "post", "api_payload": {"organizationId": verkada_org_id}, "result_key": None,
            "id_field": "device_id", "serial_field": "claimed_serial_number", "device_type_str": "Gateway"
        },
        {
            "api_url": f"https://vprovision.command.verkada.com/__v/{verkada_org_shortname}/vfortress/list_boxes",
            "api_method": "post", "api_payload": {'organizationId': verkada_org_id}, "result_key": None,
            "id_field": "deviceId", "serial_field": "claimedSerialNumber", "device_type_str": "Command Connector"
        },
        {
            "api_url": f"https://vvx.command.verkada.com/__v/{verkada_org_shortname}/device/list",
            "api_method": "post", "api_payload": {"organizationId": verkada_org_id}, "result_key": "viewingStations",
            "id_field": "viewingStationId", "serial_field": "claimedSerialNumber", "device_type_str": "Viewing Station"
        },
        {
            "api_url": f"https://vbroadcast.command.verkada.com/__v/{verkada_org_shortname}/management/speaker/list",
            "api_method": "post", "api_payload": {"organizationId": verkada_org_id}, "result_key": "garfunkel",
            "id_field": "deviceId", "serial_field": "serialNumber", "device_type_str": "Speaker"
        },
        {
            "api_url": f"https://alarms.command.verkada.com/__v/{verkada_org_shortname}/device/keypad/get_all",
            "api_method": "post", "api_payload": {"organizationId": verkada_org_id}, "result_key": "keypad",
            "id_field": "deviceId", "serial_field": "claimedSerialNumber", "device_type_str": "Classic Alarm Keypad"
        },
        {
            "api_url": f"https://vproconfig.command.verkada.com/__v/{verkada_org_shortname}/org/get_devices_and_alarm_systems",
            "api_method": "post", "api_payload": {}, "result_key": "devices",
            "id_field": "id", "serial_field": "serialNumber",
            "device_type_str": "New Alarms Device",
            "extra_fields_map": {"deviceVerkadaNewAlarmsSystemId": "alarmSystemId"}
        },
    ]

    def sync_intercom_and_desk_station_ids_combined():
        logger.info("Starting sync for Intercoms and Desk Stations...")
        url = f"https://api.command.verkada.com/__v/{verkada_org_shortname}/vinter/v1/user/organization/{verkada_org_id}/device"
        desk_stations = []
        intercoms = []
        try:
            response = requests_with_retry('get', url, headers=auth_headers, json={})
            response.raise_for_status()
            data = response.json()
            desk_stations = data.get("deskApps", [])
            intercoms = data.get("intercoms", [])
        except Exception as e:
            logger.error(f"Error fetching intercom/desk station data: {e}")
            return

        if desk_stations:
            worker_func_ds = partial(_prepare_device_write_data, org_id=org_id, id_field="deviceId", serial_field="serialNumber", expected_type="Desk Station")
            tasks_ds = [(ds_data, {}) for ds_data in desk_stations]
            def worker_wrapper_ds(task_args):
                item_data, extra_data = task_args
                return worker_func_ds(device_data=item_data, extra_fields=extra_data)

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results_ds = executor.map(worker_wrapper_ds, tasks_ds)
                prepared_writes_ds = [result for result in results_ds if result is not None]
            logger.info(f"Prepared {len(prepared_writes_ds)} write operations for {len(desk_stations)} fetched Desk Stations.")
            processed_count_ds = _execute_firestore_batches(prepared_writes_ds, org_id)
            logger.info(f"Finished processing Desk Stations. Processed {processed_count_ds} Firestore operations.")
        else:
            logger.info("No Desk Stations found to process.")

        if intercoms:
            worker_func_ic = partial(_prepare_device_write_data, org_id=org_id, id_field="deviceId", serial_field="serialNumber", expected_type="Intercom")
            tasks_ic = [(ic_data, {}) for ic_data in intercoms]
            def worker_wrapper_ic(task_args):
                item_data, extra_data = task_args
                return worker_func_ic(device_data=item_data, extra_fields=extra_data)

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results_ic = executor.map(worker_wrapper_ic, tasks_ic)
                prepared_writes_ic = [result for result in results_ic if result is not None]
            logger.info(f"Prepared {len(prepared_writes_ic)} write operations for {len(intercoms)} fetched Intercoms.")
            processed_count_ic = _execute_firestore_batches(prepared_writes_ic, org_id)
            logger.info(f"Finished processing Intercoms. Processed {processed_count_ic} Firestore operations.")
        else:
            logger.info("No Intercoms found to process.")

    def sync_classic_alarms_hub_and_sensors_combined():
        logger.info("Starting sync for Classic Alarm Hubs and Sensors...")
        url = f"https://alarms.command.verkada.com/__v/{verkada_org_shortname}/device/get_all"
        payload = {"organizationId": verkada_org_id}
        all_sensor_types = {}
        try:
            response = requests_with_retry('post', url, headers=auth_headers, json=payload)
            response.raise_for_status()
            data = response.json()
            all_sensor_types = {
                "hubDevice": (data.get("hubDevice", []), "deviceId", "claimedSerialNumber", "Classic Alarm Hub Device", {"deviceVerkadaSiteId": "siteId"}),
                "doorContactSensor": (data.get("doorContactSensor", []), "deviceId", "serialNumber", "Classic Alarm Door Contact Sensor", {}),
                "glassBreakSensor": (data.get("glassBreakSensor", []), "deviceId", "serialNumber", "Classic Alarm Glass Break Sensor", {}),
                "motionSensor": (data.get("motionSensor", []), "deviceId", "serialNumber", "Classic Alarm Motion Sensor", {}),
                "panicButton": (data.get("panicButton", []), "deviceId", "serialNumber", "Classic Alarm Panic Button", {}),
                "waterSensor": (data.get("waterSensor", []), "deviceId", "serialNumber", "Classic Alarm Water Sensor", {}),
                "wirelessRelay": (data.get("wirelessRelay", []), "deviceId", "serialNumber", "Classic Alarm Wireless Relay", {}),
            }
        except Exception as e:
            logger.error(f"Error fetching classic alarm device data: {e}")
            return

        if not any(v[0] for v in all_sensor_types.values()):
             logger.info("No classic alarm devices found to process.")
             return

        for api_key, (items, id_field, serial_field, type_str, extra_map) in all_sensor_types.items():
            if items:
                logger.info(f"Processing {len(items)} {type_str}...")
                worker_func = partial(_prepare_device_write_data, org_id=org_id, id_field=id_field, serial_field=serial_field, expected_type=type_str)
                tasks = []
                for item_data in items:
                    # Check if it's a hubDevice but has a Keypad serial prefix
                    if type_str == "Classic Alarm Hub Device":
                        serial_number = item_data.get(serial_field)
                        if serial_number:
                            actual_type = check_verkada_device_type(serial_number)
                            if actual_type == 'Classic Alarm Keypad':
                                logger.info(f"Skipping hubDevice sync for SN {serial_number} as it's identified as a Keypad.")
                                continue # Skip this item, it will be handled by the Keypad sync task
                    
                    extra_data = {}
                    if extra_map:
                        for dest_key, src_key in extra_map.items():
                            val = item_data.get(src_key)
                            if val is not None:
                                extra_data[dest_key] = val
                    tasks.append((item_data, extra_data))

                def worker_wrapper(task_args):
                    item_data, extra_data = task_args
                    return worker_func(device_data=item_data, extra_fields=extra_data)

                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    results = executor.map(worker_wrapper, tasks)
                    prepared_writes = [result for result in results if result is not None]
                logger.info(f"Prepared {len(prepared_writes)} write operations for {len(items)} fetched {type_str}.")
                processed_count = _execute_firestore_batches(prepared_writes, org_id)
                logger.info(f"Finished processing {type_str}. Processed {processed_count} Firestore operations.")
            else:
                logger.info(f"No {type_str} found to process.")

    all_futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for task_def in sync_tasks_definitions:
            future = executor.submit(_sync_generic, **task_def)
            all_futures.append(future)

        all_futures.append(executor.submit(sync_intercom_and_desk_station_ids_combined))
        all_futures.append(executor.submit(sync_classic_alarms_hub_and_sensors_combined))

        for future in concurrent.futures.as_completed(all_futures):
            try:
                future.result()
            except Exception as exc:
                logger.error(f'A sync task generated an exception: {exc}')

    logger.info(f"Completed all Verkada device sync for org: {org_id}")