from src.helper_functions.users.update_user_display_names_in_orgs import (
    update_user_display_names_in_orgs,
)
from src.helper_functions.users.update_user_photo_urls_in_orgs import (
    update_user_photo_urls_in_orgs,
)

from firebase_admin import auth
from firebase_functions import firestore_fn
from firebase_functions.firestore_fn import (
    Event,
    Change,
    DocumentSnapshot,
)


@firestore_fn.on_document_updated(document="users/{userId}")
def monitor_for_user_changes(event: Event[Change[DocumentSnapshot]]) -> None:
    """
    Firestore trigger function that monitors updates to user documents in the 'users' collection.
    When a user document is updated, this function retrieves the user's associated organization IDs
    from their custom claims and updates their display name and photo URL in all relevant organizations.
    """

    uid = event.data.after.get("uid")

    # Get user's Firebase Auth record and extract organization IDs from custom claims
    user = auth.get_user(uid)
    custom_claims = user.custom_claims or {}

    user_org_ids = [
        claim.split("_")[-1]
        for claim in custom_claims.keys()
        if claim.startswith("org_member_") or claim.startswith("org_admin_")
    ]

    # Get updated display name and photo URL from Firestore document
    user_display_name = event.data.after.get("userDisplayName")
    user_photo_url = event.data.after.get("userPhotoURL")

    # Update user's display name and photo URL in all associated organizations
    for user_org_id in user_org_ids:
        update_user_display_names_in_orgs(user_org_id, uid, user_display_name)
        update_user_photo_urls_in_orgs(user_org_id, uid, user_photo_url)
