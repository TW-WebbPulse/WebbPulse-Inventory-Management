from src.shared import db


def update_user_display_names_in_orgs(org_id, uid, org_member_display_name):
    """
    Updates the display name of a user in a specific organization's members collection in Firestore.

    Parameters:
    org_id (str): The organization ID where the user is a member.
    uid (str): The user ID of the organization member whose display name is being updated.
    org_member_display_name (str): The new display name to be set for the user.
    """
    try:
        db.collection("organizations").document(org_id).collection("members").document(
            uid
        ).update(
            {
                "orgMemberDisplayName": org_member_display_name,  # Set the new display name for the user.
            }
        )
    except Exception as e:
        pass
