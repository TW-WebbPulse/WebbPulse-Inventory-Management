from src.helper_functions.auth.auth_functions import (
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules
from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def update_global_user_photo_url_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_global_user_photo_url_callable")
    """
    Firebase Function to update the photo URL of a global user.
    It ensures that the user is authenticated, their email is verified, and their token is current.
    If valid, it updates the 'userPhotoURL' field in Firestore.
    """
    try:
        user_photo_url = req.data["userPhotoURL"]
        uid = req.auth.uid

        # Check authentication, email verification, and token validity
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)

        try:
            # Update user photo URL in Firestore
            db.collection("users").document(uid).update(
                {"userPhotoURL": user_photo_url}
            )
        except Exception as e:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.UNKNOWN,
                message=f"Error updating user photo URL: {str(e)}",
            )

        return {"response": f"User photo URL updated to {user_photo_url}"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Error updating user: {str(e)}",
        )
