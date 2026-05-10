from src.shared import db
from src.helper_functions.users.send_email import send_email
from src.helper_functions.users.generate_email_login_link import (
    generate_email_login_link,
)

from firebase_functions import https_fn
from sendgrid.helpers.mail import Mail, Asm
from firebase_admin import firestore


def create_global_user_profile(user, inviter_display_name):
    """
    Creates a global user profile in Firestore for a newly registered user.
    The function sets up two documents: one in the 'users' collection and one in the 'usersMetadata' collection.

    Parameters:
    user (AuthUserRecord): The user object from Firebase Authentication containing details like UID and email.
    """
    try:
        # Create user document in 'users' collection
        db.collection("users").document(user.uid).set(
            {
                "createdAt": firestore.SERVER_TIMESTAMP,
                "userEmail": user.email,
                "userOrgIds": [],
                "uid": user.uid,
                "userDisplayName": user.email,
                "userPhotoURL": "",
                "userDeleted": False,
            }
        )

        # Create user metadata document
        db.collection("usersMetadata").document(user.uid).set(
            {"mostRecentTokenRevokeTime": 0}
        )

        email_login_link = generate_email_login_link(user.email)
        try:
            # Send welcome email to user
            message = Mail(
                from_email="no-reply@webbpulse.com",
                to_emails=user.email,
            )
            message.template_id = "d-e68eb082e7514f1bade6d7cca26a60f6"
            message.dynamic_template_data = {
                "inviterDisplayName": inviter_display_name,
                "buttonUrl": email_login_link,
            }
            message.asm = Asm(group_id=26999, groups_to_display=[26999])
            send_email(message)
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")

    except Exception as e:
        # Handle any unexpected exceptions by raising an UNKNOWN error with details of the exception.
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Unknown Error creating user profile: {str(e)}",
        )
