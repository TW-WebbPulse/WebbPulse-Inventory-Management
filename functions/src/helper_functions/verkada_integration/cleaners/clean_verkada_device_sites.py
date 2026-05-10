from src.helper_functions.verkada_integration.utils.http_utils import requests_with_retry
from requests.exceptions import RequestException
from src.shared import db, logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def clean_verkada_device_sites(org_id, verkada_bot_user_info):
    logger.info("Moving Verkada devices...")
    
    # Check if verkada_bot_user_info is None
    if verkada_bot_user_info is None:
        raise ValueError("verkada_bot_user_info cannot be None")
    
    verkada_org_id = verkada_bot_user_info.get('org_id')
    verkada_auth_headers = verkada_bot_user_info.get('auth_headers')
    
    # Validate required fields
    if not verkada_org_id:
        raise ValueError("verkada_bot_user_info must contain 'org_id'")
    if not verkada_auth_headers:
        raise ValueError("verkada_bot_user_info must contain 'auth_headers'")
    
    org_verkada_product_site_designations = {}
    try:
        # First try to get from the main organization document
        org_ref = db.collection('organizations').document(org_id).get()
        if not org_ref.exists:
            raise Exception("Organization document not found in Firestore.")
        
        org_data = org_ref.to_dict()
        if org_data is None:
            raise Exception("Organization document is empty or corrupted.")
        
        org_verkada_product_site_designations = org_data.get('orgVerkadaProductSiteDesignations', {})
        
        # Check if org_verkada_product_site_designations is None
        if org_verkada_product_site_designations is None:
            logger.warning("orgVerkadaProductSiteDesignations is None in main org doc, using empty dict")
            org_verkada_product_site_designations = {}
        
            
    except Exception as e:
        logger.error(f"Error retrieving organization settings: {e}")
        raise

    verkada_org_short_name = verkada_bot_user_info.get('org_name')
    
    # Validate org_name
    if not verkada_org_short_name:
        raise ValueError("verkada_bot_user_info must contain 'org_name'")

    verkada_access_control_building_id = org_verkada_product_site_designations.get('Access Controller Building', '' )
    verkada_access_control_floor_id = org_verkada_product_site_designations.get('Access Controller Floor', '' )
    verkada_access_control_site_id = org_verkada_product_site_designations.get('Access Control Site', '' )
    verada_access_level_id = org_verkada_product_site_designations.get('Access Level', '' )
    verkada_camera_site_id = org_verkada_product_site_designations.get('Camera Site', '' )
    verkada_classic_alarm_site_id = org_verkada_product_site_designations.get('Classic Alarm Site', '' )
    verkada_classic_alarm_zone_id = org_verkada_product_site_designations.get('Classic Alarm Zone', '' )
    verkada_command_connector_site_id = org_verkada_product_site_designations.get('Command Connector Site', '' )
    verkada_desk_station_site_id = org_verkada_product_site_designations.get('Desk Station Site', '' )
    verkada_env_sensor_site_id = org_verkada_product_site_designations.get('Environmental Sensor Site', '' )
    verkada_gateway_site_id = org_verkada_product_site_designations.get('Gateway Site', '' )
    verkada_guest_site_id = org_verkada_product_site_designations.get('Guest Site', '' )
    verkada_intercom_site_id = org_verkada_product_site_designations.get('Intercom Site', '' )
    verkada_mailroom_site_id = org_verkada_product_site_designations.get('Mailroom Site', '' )
    verkada_new_alarm_site_id = org_verkada_product_site_designations.get('New Alarm Site', '' )
    verkada_speaker_site_id = org_verkada_product_site_designations.get('Speaker Site', '' )
    verkada_viewing_station_site_id = org_verkada_product_site_designations.get('Viewing Station Site', '' )
    
    
    
    devices = []
    try:
        devices_ref = db.collection('organizations').document(org_id).collection('devices').where('deviceVerkadaDeviceId', '!=', None)
        devices = devices_ref.get()
        logger.info(f"Devices to move: {len(devices)}")
    except Exception as e:
        logger.error(f"Error retrieving devices: {e}")
        raise
    
    def move_camera(device, verkada_camera_site_id):
        if not verkada_camera_site_id:
            logger.error("No site ID provided for camera.")
            return
        
        try:
            camera_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_short_name}/camera/site/batch/set"
            payload = {"cameraIds":[camera_id],
                    "destinationSiteId": verkada_camera_site_id}
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{camera_id} moved successfully to {verkada_camera_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {camera_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {camera_id}: {e}")
    
    def move_controller(device, verkada_access_control_site_id):
        if not verkada_access_control_site_id:
            logger.error("No site ID provided for access controller.")
            return
        
        try:
            controller_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://vcerberus.command.verkada.com/__v/{verkada_org_short_name}/access_controller/move_to_site"
            payload = {"accessControllerId":controller_id,"siteId":verkada_access_control_site_id}
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{controller_id} moved successfully to {verkada_access_control_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {controller_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {controller_id}: {e}")
    

    def move_env_sensor(device, verkada_env_sensor_site_id):
        if not verkada_env_sensor_site_id:
            logger.error("No site ID provided for environmental sensor.")
            return
        
        try:
            env_sensor_id = device.get('deviceVerkadaDeviceId')
            env_sensor_prev_site = device.get('deviceVerkadaSiteId')
            move_url = f"https://vsensor.command.verkada.com/__v/{verkada_org_short_name}/devices/{env_sensor_id}"
            payload = {'currentSiteId': env_sensor_prev_site, 'siteId': verkada_env_sensor_site_id}
            response = requests_with_retry('patch', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{env_sensor_id} moved successfully to {verkada_env_sensor_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {env_sensor_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {env_sensor_id}: {e}")

    def move_intercom(device, verkada_intercom_site_id):
        if not verkada_intercom_site_id:
            logger.error("No site ID provided for intercom.")
            return
        
        try:
            intercom_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://api.command.verkada.com/__v/{verkada_org_short_name}/vinter/v1/user/organization/{verkada_org_id}/intercom/{intercom_id}"
            payload = {"siteId":verkada_intercom_site_id}
            response = requests_with_retry('patch', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{intercom_id} moved successfully to {verkada_intercom_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {intercom_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {intercom_id}: {e}")

    def move_gateway(device, verkada_gateway_site_id):
        if not verkada_gateway_site_id:
            logger.error("No site ID provided for gateway.")
            return
        
        try:
            gateway_prev_site = device.get('deviceVerkadaSiteId')
            gateway_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://vnet.command.verkada.com/__v/{verkada_org_short_name}/devices/{gateway_id}"
            payload = {'currentSiteId': gateway_prev_site, 'siteId': verkada_gateway_site_id}
            response = requests_with_retry('patch', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{gateway_id} moved successfully to {verkada_gateway_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {gateway_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {gateway_id}: {e}")


    def move_command_connector(device, verkada_command_connector_site_id):
        if not verkada_command_connector_site_id:
            logger.error("No site ID provided for Command Connector.")
            return
        
        try:
            cc_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_short_name}/vfortress/update_box"
            payload = {
                'deviceId': cc_id,
                'siteId': verkada_command_connector_site_id
            }
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{cc_id} moved successfully to {verkada_command_connector_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {cc_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {cc_id}: {e}")

    
    def move_viewing_station(device, verkada_viewing_station_site_id):
        if not verkada_viewing_station_site_id:
            logger.error("No site ID provided for Viewing Station.")
            return
        
        try:
            vx_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://vvx.command.verkada.com/__v/{verkada_org_short_name}/viewing_station/update"
            payload = {
                'viewingStationId': vx_id,
                'siteId': verkada_viewing_station_site_id
            }
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{vx_id} moved successfully to {verkada_viewing_station_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {vx_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {vx_id}: {e}")
    
    def move_desk_station(device, verkada_desk_station_site_id):
        if not verkada_desk_station_site_id:
            logger.error("No site ID provided for Desk Station.")
            return
        
        try:
            desk_station_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://api.command.verkada.com/__v/{verkada_org_short_name}/vinter/v1/user/organization/{verkada_org_id}/desk/{desk_station_id}"
            payload = {"siteId": verkada_desk_station_site_id}
            response = requests_with_retry('patch', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{desk_station_id} moved successfully to {verkada_desk_station_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {desk_station_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {desk_station_id}: {e}")


    def move_speaker(device, verkada_speaker_site_id):
        if not verkada_speaker_site_id:
            logger.error("No site ID provided for Speaker.")
            return
        
        try:
            speaker_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://vbroadcast.command.verkada.com/__v/{verkada_org_short_name}/management/speaker/update"
            payload = {
                "deviceId": speaker_id,
                "siteId": verkada_speaker_site_id
            }
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{speaker_id} moved successfully to {verkada_speaker_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {speaker_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {speaker_id}: {e}")

    def move_classic_alarm_hub_device(device, verkada_classic_alarm_site_id):
        if not verkada_classic_alarm_site_id:
            logger.error("No site ID provided for Classic Alarm Hub.")
            return
        
        try:
            hub_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://alarms.command.verkada.com/__v/{verkada_org_short_name}/device/hub/{hub_id}"
            payload = {
                "siteId": verkada_classic_alarm_site_id
            }
            response = requests_with_retry('patch', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{hub_id} moved successfully to {verkada_classic_alarm_site_id}.")
        except RequestException as e:
            logger.error(f"Error moving {hub_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {hub_id}: {e}")

    def move_classic_alarm_keypad(device, verkada_classic_alarm_zone_id):
        if not verkada_classic_alarm_zone_id:
            logger.error("No zone ID provided for Classic Alarm Keypad.")
            return
        
        try:
            keypad_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://alarms.command.verkada.com/__v/{verkada_org_short_name}/keypad/zone/set_associations"
            payload = {
                "keypadId":keypad_id,"zoneIds":[verkada_classic_alarm_zone_id] #target zone
                }
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{keypad_id} moved successfully to {verkada_classic_alarm_zone_id}.")
        except RequestException as e:
            logger.error(f"Error moving {keypad_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {keypad_id}: {e}")

    def move_siren_strobe(device, verkada_new_alarm_site_id):
        logger.warning(f"Cannot move new alarm device 'Siren Strobe' to {verkada_new_alarm_site_id}")
        
    def move_alarm_expander(device, verkada_new_alarm_site_id):
        logger.warning(f"Cannot move new alarm device 'Alarm Expander' to {verkada_new_alarm_site_id}")

    def move_classic_alarm_sensor(device, verkada_classic_alarm_zone_id, device_type):
        if not verkada_classic_alarm_zone_id:
            logger.error("No zone ID provided for classic alarm sensor.")
            return
        
        try:
            sensor_id = device.get('deviceVerkadaDeviceId')
            move_url = f"https://alarms.command.verkada.com/__v/{verkada_org_short_name}/device/sensor/add_to_zone"
            payload = {
                "deviceId": sensor_id,
                "deviceType": device_type,
                "zoneId": verkada_classic_alarm_zone_id
            }
            response = requests_with_retry('post', move_url, headers=verkada_auth_headers, json=payload)
            response.raise_for_status()
            logger.info(f"{sensor_id} moved successfully to {verkada_classic_alarm_zone_id}.")
        except RequestException as e:
            logger.error(f"Error moving {sensor_id} info after retries: {e}")
        except Exception as e:
            logger.error(f"Error moving {sensor_id}: {e}")
    
    
    def move_device(device):
        device_dict = device.to_dict()
        
        # Check if device.to_dict() returned None
        if device_dict is None:
            logger.error("Device document is empty or corrupted, skipping device")
            return
            
        device_type = device_dict.get('deviceVerkadaDeviceType')

        if device_type == "Camera":
            move_camera(device_dict, verkada_camera_site_id)
        elif device_type == 'Access Controller' or device_type == 'Input Output Board':
            move_controller(device_dict, verkada_access_control_site_id)
        elif device_type == 'Environmental Sensor':
            move_env_sensor(device_dict, verkada_env_sensor_site_id)
        elif device_type == 'Intercom':
            move_intercom(device_dict, verkada_intercom_site_id)
        elif device_type == 'Gateway':
            move_gateway(device_dict, verkada_gateway_site_id)
        elif device_type == 'Command Connector':
            move_command_connector(device_dict, verkada_command_connector_site_id)
        elif device_type == 'Viewing Station':
            move_viewing_station(device_dict, verkada_viewing_station_site_id)
        elif device_type == 'Desk Station':
            move_desk_station(device_dict, verkada_desk_station_site_id)
        elif device_type == 'Speaker':
            move_speaker(device_dict, verkada_classic_alarm_site_id)
        elif device_type == 'Classic Alarm Hub Device':
            move_classic_alarm_hub_device(device_dict, verkada_classic_alarm_site_id)
        elif device_type == 'Classic Alarm Keypad':
            move_classic_alarm_keypad(device_dict, verkada_classic_alarm_zone_id)
        elif device_type == 'Classic Alarm Door Contact Sensor':
            move_classic_alarm_sensor(device_dict, verkada_classic_alarm_zone_id, "doorContactSensor")
        elif device_type == 'Classic Alarm Glass Break Sensor':
            move_classic_alarm_sensor(device_dict, verkada_classic_alarm_zone_id, "glassBreakSensor")
        elif device_type == 'Classic Alarm Motion Sensor':
            move_classic_alarm_sensor(device_dict, verkada_classic_alarm_zone_id, "motionSensor")
        elif device_type == 'Classic Alarm Panic Button':
            move_classic_alarm_sensor(device_dict, verkada_classic_alarm_zone_id, "panicButton")
        elif device_type == 'Classic Alarm Water Sensor':
            move_classic_alarm_sensor(device_dict, verkada_classic_alarm_zone_id, "waterSensor")
        elif device_type == 'Classic Alarm Wireless Relay':
            move_classic_alarm_sensor(device_dict, verkada_classic_alarm_zone_id, "wirelessRelay")
        elif device_type == 'Siren Strobe':
            move_siren_strobe(device_dict, verkada_new_alarm_site_id)
        elif device_type == 'BP52 Panel':
            logger.warning('Encountered unhandled device type: BP52')
            pass
        elif device_type == 'Alarm Expander':
            move_alarm_expander(device_dict, verkada_new_alarm_site_id)
            pass
            
        else:
            logger.warning(f"Device type unaccounted for when moving: {device_type}")

    # Multithreading with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        futures = [executor.submit(move_device, device) for device in devices]
        for future in as_completed(futures):
            try:
                future.result()  # Retrieve the result to catch exceptions
            except Exception as e:
                logger.error(f"Error in moving device: {e}")