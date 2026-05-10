from src.helper_functions.auth.auth_functions import check_user_is_authed
from src.helper_functions.users.create_global_user_profile import (
    create_global_user_profile,
)
from src.shared import db, apply_rate_limiting, POSTcorsrules

from firebase_admin import auth
from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules)
def create_global_user_profile_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "create_global_user_profile_callable")
    """
    Firebase Function to create a global user profile in Firestore.
    It checks if the user calling the function is authenticated and if their profile already exists in Firestore.
    If the profile exists, it raises an error; otherwise, it creates the profile.
    """

    try:
        check_user_is_authed(req)
        uid = req.auth.uid

        # Check if user profile already exists
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if user_doc.exists:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.ALREADY_EXISTS,
                message=f"User already exists in the database.",
            )

        # Create the global user profile
        user = auth.get_user(uid)
        create_global_user_profile(user, inviter_display_name=user.email)

        response_message = f"User {user.email} created in database."
        return {"response": response_message}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Error creating user: {str(e)}",
        )
