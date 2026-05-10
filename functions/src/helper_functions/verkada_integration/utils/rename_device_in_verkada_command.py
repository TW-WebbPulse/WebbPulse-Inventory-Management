from src.shared import db, logger

from src.helper_functions.verkada_integration.utils.http_utils import (
    requests_with_retry,
)

from requests.exceptions import RequestException


def rename_device_in_verkada_command(
    device_id, org_id, device_being_checked_out, verkada_bot_user_info=None
):
    """
    Renames a device in the Verkada system based on its type and availability status.

    Parameters:
        device_id (str): The ID of the device to be renamed.
        org_id (str): The ID of the organization to which the device belongs.
        device_being_checked_out (bool): Indicates whether the device is being checked out.
        verkada_bot_user_info (dict, optional): A dictionary containing Verkada bot user information.
            - org_id (str): The organization ID for the Verkada bot.
            - auth_headers (dict): Authentication headers for API requests.
            If not provided, the function will retrieve the bot user info using the organization's Verkada integration settings.
    """

    org_verkada_integration_doc = (
        db.collection("organizations")
        .document(org_id)
        .collection("sensitiveConfigs")
        .document("verkadaIntegrationSettings")
        .get()
    )
    if not verkada_bot_user_info:

        verkada_bot_user_info = org_verkada_integration_doc.to_dict().get(
            "orgVerkadaBotUserInfo", {}
        )
    if not verkada_bot_user_info:

        logger.error(f"Verkada bot user info not found for organization {org_id}.")
        return

    verkada_org_short_name = verkada_bot_user_info.get("orgVerkadaOrgShortName")
    verkada_org_id = verkada_bot_user_info.get("org_id")
    verkada_bot_headers = verkada_bot_user_info.get("auth_headers")

    deviceDoc = (
        db.collection("organizations")
        .document(org_id)
        .collection("devices")
        .document(device_id)
        .get()
    )
    device_serial_number = deviceDoc.get("deviceSerialNumber")
    device_verkada_device_id = deviceDoc.get("deviceVerkadaDeviceId")
    device_verkada_device_type = deviceDoc.get("deviceVerkadaDeviceType")

    # Validate that we have the required Verkada device information
    if (
        not device_verkada_device_id
        or not device_verkada_device_type
        or device_verkada_device_type == "Unknown"
    ):
        logger.warning(
            f"Skipping Verkada rename for device {device_serial_number} - missing or invalid Verkada device info (ID: {device_verkada_device_id}, Type: {device_verkada_device_type})"
        )
        return

    if device_being_checked_out:
        device_name = f"{device_serial_number} - Checked Out"
    else:
        device_name = f"{device_serial_number} - Available"
    if device_verkada_device_type == "Camera":
        rename_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_short_name}/camera/name/set"
        payload = {
            "cameraId": device_verkada_device_id,
            "name": device_name,
        }
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif (
        device_verkada_device_type == "Access Controller"
        or device_verkada_device_type == "Input Output Board"
    ):
        rename_url = f"https://vcerberus.command.verkada.com/__v/{verkada_org_short_name}/access_controller/edit"
        payload = {"accessControllerId": device_verkada_device_id, "name": device_name}
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Environmental Sensor":
        rename_url = f"https://vsensor.command.verkada.com/__v/{verkada_org_short_name}/devices/{device_verkada_device_id}"
        payload = {"name": device_name}
        try:
            response = requests_with_retry(
                "patch", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Intercom":
        rename_url = f"https://api.command.verkada.com/__v/{verkada_org_short_name}/vinter/v1/user/organization/{verkada_org_id}/intercom/{device_verkada_device_id}"
        payload = {"name": device_name}
        try:
            response = requests_with_retry(
                "patch", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"Intercom {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(f"Error fetching Intercom info after retries: {e}")
        except Exception as e:
            logger.error(f"Error renaming Intercom {device_serial_number}: {e}")

    elif device_verkada_device_type == "Gateway":
        rename_url = f"https://vnet.command.verkada.com/__v/{verkada_org_short_name}/devices/{device_verkada_device_id}"
        payload = {"name": device_name}
        try:
            response = requests_with_retry(
                "patch", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Command Connector":
        rename_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_short_name}/vfortress/update_box"
        payload = {"deviceId": device_verkada_device_id, "name": device_name}
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    # might not work have to check and test
    elif device_verkada_device_type == "Viewing Station":
        fetch_current_grid_url = (
            f"https://vvx.command.verkada.com/__v/{verkada_org_short_name}/device/list"
        )
        fetch_payload = {
            "organizationId": verkada_org_id,
        }
        try:
            response = requests_with_retry(
                "post",
                fetch_current_grid_url,
                headers=verkada_bot_headers,
                json=fetch_payload,
            )
            response.raise_for_status()
            devices = response.json().get("viewingStations", [])
            device_info = next(
                (
                    device
                    for device in devices
                    if device["viewingStationId"] == device_verkada_device_id
                ),
                None,
            )
            if device_info:
                gridData = device_info.get("gridData")
                gridData["name"] = device_name
            else:
                logger.error(
                    f"Device {device_verkada_device_id} not found in the response."
                )
                return
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
            return
        except Exception as e:
            logger.error(f"Error fetching {device_verkada_device_type} info: {e}")
            return

        rename_url = f"https://vvx.command.verkada.com/__v/{verkada_org_short_name}/viewing_station/grid/update"
        payload = {"gridData": gridData, "viewingStationId": device_verkada_device_id}

        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Desk Station":
        rename_url = f"https://api.command.verkada.com/__v/{verkada_org_short_name}/vinter/v1/user/organization/{verkada_org_id}/desk/{device_verkada_device_id}"
        payload = {"name": device_name}
        try:
            response = requests_with_retry(
                "patch", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Speaker":
        rename_url = f"https://vbroadcast.command.verkada.com/__v/{verkada_org_short_name}/management/speaker/update"
        payload = {
            "deviceId": device_verkada_device_id,
            "name": device_name,
        }
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Classic Alarm Hub Device":
        device_verkada_site_id = deviceDoc.get("deviceVerkadaSiteId")
        rename_url = f"https://alarms.command.verkada.com/__v/{verkada_org_short_name}/device/hub/{device_verkada_device_id}"
        payload = {"siteId": device_verkada_site_id, "name": device_name}
        try:
            response = requests_with_retry(
                "patch", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "Classic Alarm Keypad":
        rename_url = f"https://alarms.command.verkada.com/__v/{device_verkada_device_id}/device/keypad/update"
        payload = {"keypadId": device_verkada_device_id, "name": device_name}
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"Keypad {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(f"Error fetching Keypad info after retries: {e}")
        except Exception as e:
            logger.error(f"Error renaming Keypad {device_serial_number}: {e}")

    # WILL ONLY WORK FOR CLASSIC ALARMS ATM
    # NEXT STEP - TRY CLASSIC ENDPOINT FIRST, IF NOT 200 PROCEED WITH NEW ALARM ENDPOINT
    elif (
        device_verkada_device_type == "Classic Alarm Door Contact Sensor"
        or device_verkada_device_type == "Classic Alarm Glass Break Sensor"
        or device_verkada_device_type == "lassic Alarm Motion Sensor"
        or device_verkada_device_type == "Classic Alarm Panic Button"
        or device_verkada_device_type == "Classic Alarm Water Sensor"
        or device_verkada_device_type == "Classic Alarm Wireless Relay"
        or device_verkada_device_type == "Classic Alarm Motion Sensor"
    ):

        if device_verkada_device_type == "Classic Alarm Door Contact Sensor":
            payload_type = "doorContact"
        elif device_verkada_device_type == "Classic Alarm Glass Break Sensor":
            payload_type = "glassBreakSensor"
        elif device_verkada_device_type == "Classic Alarm Motion Sensor":
            payload_type = "motionSensor"
        elif device_verkada_device_type == "Classic Alarm Panic Button":
            payload_type = "panicButton"
        elif device_verkada_device_type == "Classic Alarm Water Sensor":
            payload_type = "waterSensor"
        elif device_verkada_device_type == "Classic Alarm Wireless Relay":
            payload_type = "wirelessRelay"

        rename_url = f"https://alarms.command.verkada.com/__v/{verkada_org_short_name}/device/sensor/update"
        payload = {
            "deviceId": device_verkada_device_id,
            "name": device_name,
            "deviceType": payload_type,
        }
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    elif device_verkada_device_type == "New Alarms Device":
        rename_url = f"https://vproconfig.command.verkada.com/__v/{verkada_org_short_name}/device/name/set"
        payload = {"deviceId": device_verkada_device_id, "name": device_name}
        try:
            response = requests_with_retry(
                "post", rename_url, headers=verkada_bot_headers, json=payload
            )
            response.raise_for_status()
            logger.info(
                f"{device_verkada_device_type} {device_serial_number} renamed successfully to {device_name}."
            )
        except RequestException as e:
            logger.error(
                f"Error fetching {device_verkada_device_type} info after retries: {e}"
            )
        except Exception as e:
            logger.error(
                f"Error renaming {device_verkada_device_type} {device_serial_number}: {e}"
            )

    else:
        logger.info(
            f"Device type {device_verkada_device_type} not supported for renaming."
        )
