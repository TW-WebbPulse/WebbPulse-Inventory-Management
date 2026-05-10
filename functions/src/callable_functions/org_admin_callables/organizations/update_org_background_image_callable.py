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
def update_org_background_image_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_org_background_image_callable")
    """
    Firebase Function to update the background image URL for an organization.
    The function ensures that the user is authenticated, their email is verified,
    their token is current, and they are an admin of the organization.
    """

    try:
        org_id = req.data["orgId"]
        org_background_image_url = req.data["orgBackgroundImageURL"]

        # Check authentication, email verification, token validity, and admin status
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_admin(req, org_id)

        # Validate organization ID
        if not org_id:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message="The function must be called with the following argument: orgId",
            )

        # Update organization background image URL
        org_ref = db.collection("organizations").document(org_id)
        org_ref.update(
            {
                "orgBackgroundImageURL": org_background_image_url,
            }
        )

        return {
            "response": f"Organization background image updated to: {org_background_image_url}"
        }

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
