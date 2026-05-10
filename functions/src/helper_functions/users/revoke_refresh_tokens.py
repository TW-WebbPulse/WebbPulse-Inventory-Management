from src.shared import db
from firebase_admin import auth
import time


def revoke_refresh_tokens(org_member_id):
    """
    Revokes the refresh tokens for a given user to force re-authentication.
    This ensures that any updated claims will be included in new tokens.

    Parameters:
    org_member_id (str): The user ID of the organization member whose tokens are being revoked.
    """

    auth.revoke_refresh_tokens(org_member_id)

    db.collection("usersMetadata").document(org_member_id).update(
        {"mostRecentTokenRevokeTime": time.time()}
    )
