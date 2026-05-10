from src.helper_functions.auth.auth_functions import check_user_is_org_member, check_user_is_authed, check_user_token_current, check_user_is_email_verified
from src.helper_functions.verkada_integration.utils.check_verkada_device_type import check_verkada_device_type
from src.shared import db, apply_rate_limiting, POSTcorsrules

from firebase_functions import https_fn
from typing import Any
from firebase_admin import firestore
import re

@https_fn.on_call(cors=POSTcorsrules, timeout_sec=540)
def create_devices_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "create_devices_callable")
    try:
        device_serial_numbers = req.data["deviceSerialNumbers"]
        org_id = req.data["orgId"]

        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_member(req, org_id)

        if not device_serial_numbers or not isinstance(device_serial_numbers, list) or not org_id:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The function must be called with a valid list of "deviceSerialNumbers" and a valid "org_id".'
            )
        regex_filter = db.collection('organizations').document(org_id).get().get('orgDeviceRegexString')

        response = {}

        for device_serial_number in device_serial_numbers:
            if not device_serial_number:
                continue
            device_verkada_device_type = check_verkada_device_type(device_serial_number)
            if regex_filter and not re.fullmatch(regex_filter, device_serial_number):
                if 'failure' not in response:
                    response['failure'] = {}
                response['failure'][device_serial_number] = f"Device does not match the regex filter"
                continue
            existing_device_query = db.collection('organizations').document(org_id).collection('devices').where('deviceSerialNumber', '==', device_serial_number).limit(1).get()
            if existing_device_query:
                device_ref = existing_device_query[0].reference
                device_ref.set({
                    'deviceId': device_ref.id,
                    'deviceSerialNumber': device_serial_number,
                    'createdAt': firestore.SERVER_TIMESTAMP,
                    'isDeviceCheckedOut': False,
                    'deviceCheckedOutBy': '',
                    'deviceCheckedOutAt': None,
                    'deviceDeleted': False,
                    'deviceVerkadaDeviceType': device_verkada_device_type,
                }, merge=True)
            else:
                device_ref = db.collection('organizations').document(org_id).collection('devices').document()
                device_ref.set({
                    'deviceId': device_ref.id,
                    'deviceSerialNumber': device_serial_number,
                    'createdAt': firestore.SERVER_TIMESTAMP,
                    'isDeviceCheckedOut': False,
                    'deviceCheckedOutBy': '',
                    'deviceCheckedOutAt': None,
                    'deviceDeleted': False,
                    'deviceVerkadaDeviceType': device_verkada_device_type,
                })

            if 'success' not in response:
                response['success'] = {}
            response["success"][device_serial_number]=f"Device created"

        return response

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Error creating devices: {str(e)}"
        )
