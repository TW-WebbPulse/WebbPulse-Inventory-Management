from src.shared import db
from src.helper_functions.users.send_email import send_email
from src.helper_functions.users.update_user_roles import update_user_roles

from firebase_functions import https_fn
from sendgrid.helpers.mail import Mail, Asm
from firebase_admin import firestore


def add_user_to_organization(
    uid, org_id, org_member_display_name, org_member_email, inviter_display_name
):
    """
    Adds a user to an organization by creating a member record in the organization's 'members' subcollection in Firestore.
    The function assigns the user the role of 'member' and updates their roles in the system.

    Parameters:
    uid (str): The user ID of the member to be added.
    org_id (str): The organization ID to which the user is being added.
    org_member_display_name (str): The display name of the user (can be empty or None).
    org_member_email (str): The email address of the user.
    """
    try:
        # Use email as display name if not provided
        org_member_display_name = org_member_display_name or org_member_email

        # Create member document in organization's members collection
        org_member_ref = (
            db.collection("organizations")
            .document(org_id)
            .collection("members")
            .document(uid)
        )

        org_member_ref.set(
            {
                "orgMemberId": uid,
                "createdAt": firestore.SERVER_TIMESTAMP,
                "orgMemberDisplayName": org_member_display_name,
                "orgMemberEmail": org_member_email,
                "orgMemberPhotoURL": "",
                "orgMemberRole": "member",
                "orgMemberDeleted": False,
            }
        )

        # Update user's roles (don't revoke refresh token)
        update_user_roles(uid, "member", org_id, False)

        # Get organization name for email
        org_doc_ref = db.collection("organizations").document(org_id)
        org_doc = org_doc_ref.get()
        if org_doc.exists:
            org_data = org_doc.to_dict()
            org_name = org_data.get("orgName")
        else:
            org_name = "Organization"
        try:
            # Send welcome email to user
            message = Mail(
                from_email="no-reply@webbpulse.com",
                to_emails=org_member_email,
            )
            message.template_id = "d-0d63e8080ff2402d9a34d3ebbd2d25ed"
            message.dynamic_template_data = {
                "inviterDisplayName": inviter_display_name,
                "orgName": org_name,
            }
            message.asm = Asm(group_id=26999, groups_to_display=[26999])
            send_email(message)
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")


    except Exception as e:
        # Handle any unexpected exceptions by raising an UNKNOWN error with details of the exception.
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Unknown Error adding user to organization: {str(e)}",
        )
