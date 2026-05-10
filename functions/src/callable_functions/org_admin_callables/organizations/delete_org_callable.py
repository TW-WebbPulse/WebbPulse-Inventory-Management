from src.helper_functions.auth.auth_functions import (
    check_user_is_org_admin,
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)
from src.helper_functions.users.update_user_roles import update_user_roles
from src.shared import db, apply_rate_limiting, POSTcorsrules

from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def delete_org_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "delete_org_callable")
    """
    Firebase Function to delete an organization.
    The function checks if the user is authenticated, their email is verified, and they are an admin of the organization.
    If valid, the organization is marked as deleted and the user's roles in the organization are updated accordingly.
    """
    try:
        org_id = req.data["orgId"]

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

        # Remove current user from organization
        uid = req.auth.uid
        update_user_roles(uid, "none", org_id, True)

        # Remove all other users from the organization
        members_ref = (
            db.collection("organizations").document(org_id).collection("members")
        )
        members = members_ref.stream()

        for member in members:
            uid = member.id
            update_user_roles(uid, "none", org_id, True)

        # Mark organization as deleted
        org_ref = db.collection("organizations").document(org_id)
        org_ref.set({"orgDeleted": True}, merge=True)

        return {"response": f"Organization deleted: {org_id}"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
