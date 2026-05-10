from src.helper_functions.auth.auth_functions import check_user_is_org_admin, check_user_is_authed, check_user_token_current, check_user_is_email_verified
from src.shared import db, apply_rate_limiting, POSTcorsrules
from src.helper_functions.verkada_integration.utils.update_all_verkada_device_type import update_all_devices_verkada_device_type

from firebase_functions import https_fn
from typing import Any

@https_fn.on_call(cors=POSTcorsrules)
def update_verkada_integration_status_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_verkada_integration_status_callable")
    """
    Firebase Function to update the name of an organization.
    The function ensures the user is authenticated, their email is verified, their token is current, 
    and they are an admin of the organization.
    """

    org_id = req.data.get('orgId')
    enabled = req.data.get('enabled')

    check_user_is_authed(req)
    check_user_is_email_verified(req)
    check_user_token_current(req)
    check_user_is_org_admin(req, org_id)

    try:
        org_ref_main = db.collection('organizations').document(org_id)
        org_ref_main.update({
            'orgVerkadaIntegrationEnabled': enabled
        })

        if enabled:
            # Initialize fields in the main org document
            org_data_to_init = {
                'orgVerkadaOrgShortName': '',
                'orgVerkadaBotEmail': '',
                'orgVerkadaBotPassword': '', # Consider security
                'orgVerkadaProductSiteDesignations': {
                    'Access Control Building': '',
                    'Access Control Floor': '',
                    'Access Control Site': '',
                    'Access Level': '',
                    'Camera Site': '',
                    'Classic Alarm Site': '',
                    'Classic Alarm Zone': '',
                    'Command Connector Site': '',
                    'Desk Station Site': '',
                    'Environmental Sensor Site': '',
                    'Gateway Site': '',
                    'Guest Site': '',
                    'Intercom Site': '',
                    'Mailroom Site': '',
                    'New Alarm Site': '',
                    'Speaker Site': '',
                    'Viewing Station Site': ''
                },
                'orgVerkadaUserGroups': [],
                'orgVerkadaSiteCleanerEnabled': False
            }
            # Check if fields exist before setting to avoid overwriting
            current_org_data = org_ref_main.get()
            if current_org_data.exists:
                current_fields = current_org_data.to_dict()
                update_data = {k: v for k, v in org_data_to_init.items() if k not in current_fields}
                if update_data:
                    org_ref_main.update(update_data)
            else:
                org_ref_main.set(org_data_to_init, merge=True) # Should not happen if org exists

            # Initialize verkadaIntegrationSettings with only orgVerkadaBotUserInfo
            settings_ref = org_ref_main.collection('sensitiveConfigs').document('verkadaIntegrationSettings')
            settings_doc = settings_ref.get()
            if not settings_doc.exists:
                 settings_ref.set({
                    'orgVerkadaBotUserInfo': {} # Initialize as empty or null
                })
            else: # If it exists, ensure only orgVerkadaBotUserInfo is there or it's initialized
                existing_settings = settings_doc.to_dict()
                if 'orgVerkadaBotUserInfo' not in existing_settings:
                    settings_ref.update({'orgVerkadaBotUserInfo': {}})


        return {"response": f"Verkada integration status updated to {enabled}."}
    except Exception as e:
        # logger.error(f"Error updating Verkada integration status: {str(e)}", exc_info=True)
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}"
        )
