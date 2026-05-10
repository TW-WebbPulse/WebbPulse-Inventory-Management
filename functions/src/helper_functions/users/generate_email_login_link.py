from firebase_admin import auth
from firebase_functions import https_fn
from firebase_admin.auth import UserNotFoundError
from typing import Any

def generate_email_login_link(email):
    """
    creates a link to log in to the application.

    Parameters:
    email (str): The email address of the user to whom the login link is being sent.
    """
    try:# Check if the user already exists, if not, create them
        try:
            user = auth.get_user_by_email(email)
        except UserNotFoundError:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.NOT_FOUND,
                message=f"User with email {email} not found."
            )
        

        # Generate a custom token for the user
        custom_token = auth.create_custom_token(user.uid)
        
        # Convert token to a URL-safe format (optional)
        custom_token_url_safe = custom_token.decode("utf-8")


        # Construct a link with the token that your frontend can use
        email_login_link = f"https://inventory.webbpulse.com/#/custom-signin?token={custom_token_url_safe}"
        return email_login_link
    except Exception as e:
        # Handle any unexpected exceptions by raising an UNKNOWN error with details of the exception.
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Unknown Error creating login link: {str(e)}"
        )