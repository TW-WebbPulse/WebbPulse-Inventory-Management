from src.helper_functions.auth.auth_functions import (
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
    check_user_is_at_global_org_limit,
)
from src.helper_functions.users.add_user_to_organization import add_user_to_organization
from src.helper_functions.users.update_user_roles import update_user_roles
from src.shared import db, apply_rate_limiting, POSTcorsrules

from firebase_functions import https_fn
from typing import Any
from firebase_admin import firestore


@https_fn.on_call(cors=POSTcorsrules)
def create_organization_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "create_organization_callable")
    """
    Firebase Function to create a new organization.
    The function ensures the user is authenticated, verifies their email, checks if they are at the organization creation limit,
    and if valid, creates a new organization document in Firestore.
    """
    try:
        org_name = req.data["orgName"]
        uid = req.auth.uid
        org_member_display_name = req.auth.token.get("name", "")
        org_member_email = req.auth.token.get("email", "")

        # Use email as display name if none provided
        if org_member_display_name == "":
            org_member_display_name = org_member_email

        # Check authentication, email verification, token validity, and org creation limit
        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_at_global_org_limit(uid)

        # Validate organization name
        if not org_name:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The function must be called with a valid "organizationCreationName" argument.',
            )

        # Create new organization document
        org_ref = db.collection("organizations").document()
        org_id = org_ref.id

        org_ref.set(
            {
                "orgId": org_id,
                "createdAt": firestore.SERVER_TIMESTAMP,
                "orgName": org_name,
                "orgBackgroundImageURL": "",
                "orgDeleted": False,
                "orgVerkadaIntegrationEnabled": False,
                "orgDeviceRegexString": "",
            }
        )

        # Add user to organization as admin
        add_user_to_organization(
            uid,
            org_id,
            org_member_display_name,
            org_member_email,
            org_member_display_name, #inviter_display_name,
        )
        update_user_roles(uid, "admin", org_id, False)

        return {"response": f"Organization {org_id} created"}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"Error creating organization: {str(e)}",
        )
