from src.helper_functions.auth.auth_functions import (
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules
from firebase_admin import auth
from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def delete_global_user_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "delete_global_user_callable")
    """
    Firebase Function to handle the removal of a global user.
    It checks if the user is authenticated, their email is verified, and their token is current.
    Then, it removes the user from all associated organizations by updating their status in Firestore.
    """
    try:
        uid = req.auth.uid

        # Check authentication, email verification, and token validity
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)

        # Get user details and extract organization memberships from custom claims
        user = auth.get_user(uid)
        custom_claims = user.custom_claims or {}

        user_org_ids = [
            claim.split("_")[-1]
            for claim in custom_claims.keys()
            if claim.startswith("org_member_") or claim.startswith("org_admin_")
        ]

        # Mark user as deleted in all associated organizations
        for user_org_id in user_org_ids:
            org_member_ref = (
                db.collection("organizations")
                .document(user_org_id)
                .collection("members")
                .document(uid)
            )
            org_member_ref.set({"orgMemberDeleted": True}, merge=True)

        return {"response": f"Global user removed: {uid}"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
