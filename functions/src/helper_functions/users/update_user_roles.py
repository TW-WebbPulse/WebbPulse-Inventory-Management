from src.shared import db
from src.helper_functions.users.revoke_refresh_tokens import revoke_refresh_tokens

from firebase_functions import https_fn
from firebase_admin import auth


def update_user_roles(org_member_id, org_member_role, org_id, revoke_tokens):
    """
    Updates the role of a user in an organization and updates their custom claims in Firebase Auth.
    Optionally revokes the user's refresh tokens to ensure new tokens reflect the updated claims.

    Parameters:
    org_member_id (str): The user ID of the organization member whose role is being updated.
    org_member_role (str): The new role to assign to the user ('admin', 'member', 'deskstation', or 'none').
    org_id (str): The organization ID to which the user belongs.
    revoke_tokens (bool): Whether to revoke the user's refresh tokens after updating the role.
    """

    # Update user's role in Firestore
    db.collection("organizations").document(org_id).collection("members").document(
        org_member_id
    ).update({"orgMemberRole": org_member_role})

    # Get user's existing custom claims
    user = auth.get_user(org_member_id)
    custom_claims = user.custom_claims or {}

    # Update custom claims based on new role
    if org_member_role == "admin":
        custom_claims[f"org_admin_{org_id}"] = True
        custom_claims.pop(f"org_member_{org_id}", None)
        custom_claims.pop(f"org_deskstation_{org_id}", None)
    elif org_member_role == "member":
        custom_claims.pop(f"org_admin_{org_id}", None)
        custom_claims[f"org_member_{org_id}"] = True
        custom_claims.pop(f"org_deskstation_{org_id}", None)
    elif org_member_role == "deskstation":
        custom_claims.pop(f"org_admin_{org_id}", None)
        custom_claims.pop(f"org_member_{org_id}", None)
        custom_claims[f"org_deskstation_{org_id}"] = True
    elif org_member_role == "none":
        custom_claims.pop(f"org_admin_{org_id}", None)
        custom_claims.pop(f"org_member_{org_id}", None)
        custom_claims.pop(f"org_deskstation_{org_id}", None)
    else:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            message=f"Invalid role: {org_member_role}",
        )

    # Update user's custom claims in Firebase Auth
    auth.set_custom_user_claims(org_member_id, custom_claims)

    # Revoke refresh tokens if requested
    if revoke_tokens:
        revoke_refresh_tokens(org_member_id)
