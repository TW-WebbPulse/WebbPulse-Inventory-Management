from src.helper_functions.auth.auth_functions import (
    check_user_is_org_member,
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
    check_user_is_org_deskstation_or_higher,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules, logger
from src.helper_functions.verkada_integration.utils.rename_device_in_verkada_command import (
    rename_device_in_verkada_command,
)

from firebase_functions import https_fn
from typing import Any
from firebase_admin import firestore


@https_fn.on_call(cors=POSTcorsrules, timeout_sec=540)
def update_device_checkout_status_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_device_checkout_status_callable")
    try:
        org_id = req.data["orgId"]
        device_serial_number = req.data["deviceSerialNumber"]
        is_device_being_checked_out = req.data["isDeviceBeingCheckedOut"]
        device_being_checked_by = req.data["deviceBeingCheckedBy"]
        device_checked_out_note = req.data["deviceCheckedOutNote"]

        if not isinstance(is_device_being_checked_out, bool):
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message="'isDeviceCheckedOut' must be a boolean.",
            )

        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_member(req, org_id)

        if (
            not device_serial_number
            or not org_id
            or is_device_being_checked_out is None
        ):
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message="The function must be called with valid deviceSerialNumber, orgId, and isDeviceCheckedOut parameters.",
            )

        device_snapshot = (
            db.collection("organizations")
            .document(org_id)
            .collection("devices")
            .where("deviceSerialNumber", "==", device_serial_number)
            .get()
        )

        if len(device_snapshot) > 0:
            if is_device_being_checked_out == False:
                device_currently_checked_out_by = (
                    device_snapshot[0].to_dict().get("deviceCheckedOutBy")
                )
                if device_currently_checked_out_by != device_being_checked_by:
                    check_user_is_org_deskstation_or_higher(req, org_id)
            device_id = device_snapshot[0].id

            if is_device_being_checked_out:
                db.collection("organizations").document(org_id).collection(
                    "devices"
                ).document(device_id).update(
                    {
                        "isDeviceCheckedOut": True,
                        "deviceCheckedOutBy": device_being_checked_by,
                        "deviceCheckedOutAt": firestore.SERVER_TIMESTAMP,
                        "deviceCheckedOutNote": device_checked_out_note,
                    }
                )

            else:
                db.collection("organizations").document(org_id).collection(
                    "devices"
                ).document(device_id).update(
                    {
                        "isDeviceCheckedOut": False,
                        "deviceCheckedOutBy": "",
                        "deviceCheckedOutAt": None,
                        "deviceCheckedOutNote": "",
                    }
                )

            org_verkada_integration_enabled = (
                db.collection("organizations")
                .document(org_id)
                .get()
                .get("orgVerkadaIntegrationEnabled")
            )
            if org_verkada_integration_enabled:
                device_doc = (
                    db.collection("organizations")
                    .document(org_id)
                    .collection("devices")
                    .document(device_id)
                    .get()
                )
                verkada_device_id = device_doc.get("deviceVerkadaDeviceId")
                device_verkada_device_type = device_doc.get("deviceVerkadaDeviceType")

                # Only attempt Verkada rename if device has a valid Verkada device ID and type
                if (
                    verkada_device_id
                    and device_verkada_device_type
                    and device_verkada_device_type != "Unknown"
                ):
                    logger.info(
                        f"Attempting to rename Verkada device {device_serial_number} (type: {device_verkada_device_type})"
                    )
                    rename_device_in_verkada_command(
                        device_id, org_id, is_device_being_checked_out
                    )
                else:
                    logger.info(
                        f"Skipping Verkada rename for device {device_serial_number} - deviceVerkadaDeviceId: {verkada_device_id}, deviceVerkadaDeviceType: {device_verkada_device_type}"
                    )

        else:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.NOT_FOUND, message="Device not found"
            )

        return {"response": f"Device {device_serial_number} updated"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Error updating device checkout status: {str(e)}",
        )
