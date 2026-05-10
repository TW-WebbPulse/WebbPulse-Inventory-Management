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
def delete_org_member_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "delete_org_member_callable")
    """
    Firebase Function to remove a member from an organization.
    The function ensures the user making the request is authenticated, their email is verified,
    their token is current, and they are an admin of the specified organization.
    It revokes the member's roles and marks them as deleted in Firestore.
    """
    try:
        org_id = req.data["orgId"]
        org_member_id = req.data["orgMemberId"]

        # Check authentication, email verification, token validity, and admin status
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_admin(req, org_id)

        # Validate organization ID and member ID
        if not org_id or not org_member_id:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message="The function must be called with the following arguments: orgId, orgMemberId",
            )

        # Revoke user's roles in the organization
        update_user_roles(org_member_id, "none", org_id, True)

        # Mark user as deleted in organization's members collection
        org_member_ref = (
            db.collection("organizations")
            .document(org_id)
            .collection("members")
            .document(org_member_id)
        )
        org_member_ref.set({"orgMemberDeleted": True}, merge=True)

        return {"response": f"Organization member removed: {org_id}"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
