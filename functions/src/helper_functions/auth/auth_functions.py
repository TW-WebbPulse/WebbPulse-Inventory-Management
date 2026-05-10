from firebase_functions import https_fn
from firebase_admin import auth
from src.shared import db



def check_user_token_current(req: https_fn.CallableRequest):
    """
    Verifies if the user's token is current by checking the 'mostRecentTokenRevokeTime' in Firestore.

    Parameters:
    req (https_fn.CallableRequest): The request object containing authentication info.
    
    Raises:
    https_fn.HttpsError: If the user metadata or token revoke time is not found, or if the token is outdated.
    """
    # Retrieve the 'mostRecentTokenRevokeTime' from the user's metadata in Firestore
    user_metadata_ref = db.collection('usersMetadata').document(req.auth.uid)
    user_metadata = user_metadata_ref.get().to_dict()
    
    if not user_metadata or 'mostRecentTokenRevokeTime' not in user_metadata:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.NOT_FOUND,
            message="User metadata or most recent token revoke time not found."
        )
    
    mostRecentTokenRevokeTime = user_metadata['mostRecentTokenRevokeTime']

    # Compare token's auth_time to the most recent revoke time to ensure the token is current
    if req.auth.token.get('auth_time') < mostRecentTokenRevokeTime:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.FAILED_PRECONDITION,
            message="The function must be called with a valid token."
        )

def check_user_is_authed(req: https_fn.CallableRequest):
    """
    Checks if the user is authenticated.

    Parameters:
    req (https_fn.CallableRequest): The request object containing authentication info.
    
    Raises:
    https_fn.HttpsError: If the user is not authenticated.
    """
    if req.auth is None:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.FAILED_PRECONDITION,
            message="The function must be called while authenticated."
        )

def check_user_is_email_verified(req: https_fn.CallableRequest):
    """
    Checks if the user's email is verified.

    Parameters:
    req (https_fn.CallableRequest): The request object containing authentication info.
    
    Raises:
    https_fn.HttpsError: If the user's email is not verified.
    """
    if not req.auth.token.get('email_verified'):
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.PERMISSION_DENIED,
            message="The function must be called with a verified email."
        )
    
def check_user_is_org_member(req: https_fn.CallableRequest, org_id: str):
    """
    Checks if the user is either a member, admin, or deskstation user for a given organization.

    Parameters:
    req (https_fn.CallableRequest): The request object containing authentication info.
    org_id (str): The ID of the organization.
    
    Raises:
    https_fn.HttpsError: If the user is not a member, admin, or deskstation user for the organization.
    """
    is_member = req.auth.token.get(f"org_member_{org_id}")
    is_admin = req.auth.token.get(f"org_admin_{org_id}")
    is_deskstation = req.auth.token.get(f"org_deskstation_{org_id}")

    if is_member is None and is_admin is None and is_deskstation is None:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.PERMISSION_DENIED,
            message="Unauthorized access. User is not a member or admin of the organization."
        )
    
def check_user_is_org_admin(req: https_fn.CallableRequest, org_id: str):
    """
    Checks if the user has the admin role for a given organization.

    Parameters:
    req (https_fn.CallableRequest): The request object containing authentication info.
    org_id (str): The ID of the organization.
    
    Raises:
    https_fn.HttpsError: If the user is not an admin of the organization.
    """
    if req.auth.token.get(f"org_admin_{org_id}") is None:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.PERMISSION_DENIED,
            message=f"Unauthorized access. User is not an admin of the organization."
        )
        
def check_user_is_org_deskstation_or_higher(req: https_fn.CallableRequest, org_id: str):
    """
    Checks if the user has either the deskstation or admin role for a given organization.

    Parameters:
    req (https_fn.CallableRequest): The request object containing authentication info.
    org_id (str): The ID of the organization.
    
    Raises:
    https_fn.HttpsError: If the user is neither a deskstation user nor an admin of the organization.
    """
    is_deskstation = req.auth.token.get(f"org_deskstation_{org_id}")
    is_admin = req.auth.token.get(f"org_admin_{org_id}")

    if is_deskstation is None and is_admin is None:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.PERMISSION_DENIED,
            message="Unauthorized access. User is not a deskstation or admin of the organization."
        )
        
def check_user_is_at_global_org_limit(uid: str):
    """
    Checks if the user has reached the global limit of 10 organizations.

    Parameters:
    uid (str): The user ID whose organization limit is being checked.
    
    Raises:
    https_fn.HttpsError: If the user has reached the limit of 10 organizations.
    """
    # Retrieve custom claims to check the number of organizations the user is part of
    user = auth.get_user(uid)
    custom_claims = user.custom_claims or {}
    
    # Count the number of organizations where the user has admin, member, or deskstation roles
    org_admin_claims = [claim for claim in custom_claims.keys() if claim.startswith("org_admin_")]
    org_member_claims = [claim for claim in custom_claims.keys() if claim.startswith("org_member_")]
    org_deskstation_claims = [claim for claim in custom_claims.keys() if claim.startswith("org_deskstation_")]
    
    org_count = len(org_admin_claims) + len(org_member_claims) + len(org_deskstation_claims)
    
    # If the user is part of 10 or more organizations, raise an error
    if org_count >= 10:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.FAILED_PRECONDITION,
            message="The user is at the global organization limit."
        )

