from src.helper_functions.auth.auth_functions import (
    check_user_is_org_admin,
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules

from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def update_org_name_callable(req: https_fn.CallableRequest) -> Any:
    """
    Firebase Function to update the name of an organization.
    The function ensures the user is authenticated, their email is verified, their token is current,
    and they are an admin of the organization.
    """
    # Apply rate limiting
    apply_rate_limiting(req, "update_org_name_callable")

    try:
        org_id = req.data["orgId"]
        org_name = req.data["orgName"]

        # Check authentication, email verification, token validity, and admin status
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_admin(req, org_id)

        # Validate organization ID and name
        if not org_id or not org_name:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message="The function must be called with the following arguments: orgId, orgName",
            )

        # Update organization name
        org_ref = db.collection("organizations").document(org_id)
        org_ref.update(
            {
                "orgName": org_name,
            }
        )

        return {"response": f"Organization name updated to: {org_name}"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
