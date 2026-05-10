from src.helper_functions.auth.auth_functions import (
    check_user_is_org_admin,
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules
from src.helper_functions.verkada_integration.utils.update_all_verkada_device_type import (
    update_all_devices_verkada_device_type,
)

from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def update_verkada_user_group_whitelists_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_verkada_user_group_whitelists_callable")
    """
    Firebase Function to update the Verkada user group whitelists for an organization.
    The function checks if the user is authenticated, their email is verified, and they are an admin of the organization.
    It expects a list of group maps in the 'updatedGroups' field.
    """

    try:
        org_id = req.data["orgId"]

        updated_groups = req.data["updatedGroups"]

        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_admin(req, org_id)

        if not org_id or updated_groups is None:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message="The function must be called with the following arguments: orgId, updatedGroups",
            )

        if not isinstance(updated_groups, list):
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The "updatedGroups" argument must be a list.',
            )

        org_ref = db.collection("organizations").document(org_id)
        # Save the received list directly to the 'orgVerkadaUserGroups' field in the main org document
        org_ref.update({"orgVerkadaUserGroups": updated_groups})

        return {
            "response": f"Successfully updated the Verkada user group whitelists for organization {org_id}."
        }

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
