from src.shared import db


def update_user_photo_urls_in_orgs(org_id, uid, org_member_photo_url):
    """
    Updates the photo URL of a user in a specific organization's members collection in Firestore.

    Parameters:
    org_id (str): The organization ID where the user is a member.
    uid (str): The user ID of the organization member whose photo URL is being updated.
    org_member_photo_url (str): The new photo URL to be set for the user.
    """
    try:

        db.collection("organizations").document(org_id).collection("members").document(
            uid
        ).update(
            {
                "orgMemberPhotoURL": org_member_photo_url,  # Set the new photo URL for the user.
            }
        )
    except Exception as e:

        pass
