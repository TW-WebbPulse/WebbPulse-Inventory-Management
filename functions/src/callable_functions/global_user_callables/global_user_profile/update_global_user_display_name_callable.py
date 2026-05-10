from src.helper_functions.auth.auth_functions import (
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules
from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def update_global_user_display_name_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_global_user_display_name_callable")
    """
    Firebase Function to update the display name of a global user.
    It ensures that the user is authenticated, their email is verified, and their token is current.
    If the provided display name is valid, it updates the 'userDisplayName' field in Firestore.
    """
    try:
        user_display_name = req.data["userDisplayName"]
        uid = req.auth.uid

        # Check authentication, email verification, and token validity
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)

        # Validate display name is not empty
        if not user_display_name:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The function must be called with one argument: "DisplayName".',
            )

        try:
            # Update user display name in Firestore
            db.collection("users").document(uid).update(
                {"userDisplayName": user_display_name}
            )
        except Exception as e:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.UNKNOWN,
                message=f"Error updating user display name: {str(e)}",
            )

        return {"response": f"User display name updated to {user_display_name}"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Error updating user display name: {str(e)}",
        )
