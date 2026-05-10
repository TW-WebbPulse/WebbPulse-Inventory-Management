from src.helper_functions.auth.auth_functions import check_user_is_org_admin, check_user_is_authed, check_user_token_current, check_user_is_email_verified
from src.shared import db, apply_rate_limiting, POSTcorsrules
from src.helper_functions.verkada_integration.utils.grant_all_verkada_permissions import grant_all_verkada_permissions
from src.helper_functions.verkada_integration.syncers.sync_verkada_device_ids import sync_verkada_device_ids
from src.helper_functions.verkada_integration.syncers.sync_verkada_user_groups import sync_verkada_user_groups
from src.helper_functions.verkada_integration.syncers.sync_verkada_site_ids import sync_verkada_site_ids




from firebase_functions import https_fn
from typing import Any


@https_fn.on_call(cors=POSTcorsrules, timeout_sec=540)
def sync_with_verkada_callable(req: https_fn.CallableRequest) -> Any:
    # Apply rate limiting
    apply_rate_limiting(req, "sync_with_verkada_callable")
    """
    
    """

    try:
        org_id = req.data.get("orgId", "")
        verkada_org_short_name = req.data.get("orgVerkadaOrgShortName", "")
        verkada_org_id = req.data.get("orgVerkadaOrgId", "")
        verkada_org_bot_user_id = req.data.get("orgVerkadaBotUserId", "")
        verkada_org_bot_user_v2 = req.data.get("orgVerkadaBotUserV2", "")
        

        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_admin(req, org_id)

        if not org_id:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The function must be called with the following arguments: orgId,'
            )
        if verkada_org_short_name and verkada_org_id and verkada_org_bot_user_id and verkada_org_bot_user_v2:
            verkada_bot_auth_headers = {
                "X-Verkada-Auth": verkada_org_bot_user_v2,
                "X-Verkada-User-id": verkada_org_bot_user_id,
                "X-Verkada-Organization-Id": verkada_org_id
            }
            verkada_bot_user_info = {
                "auth_headers": verkada_bot_auth_headers,
                "org_id": verkada_org_id,
                "org_name": verkada_org_short_name,
                "user_id": verkada_org_bot_user_id,
                "v2": verkada_org_bot_user_v2,
                'orgVerkadaOrgShortName': verkada_org_short_name,
            }

            org_ref = db.collection('organizations').document(org_id).collection('sensitiveConfigs').document('verkadaIntegrationSettings')
            org_ref.update({
                'orgVerkadaBotUserInfo': verkada_bot_user_info
            })
        else:
            org_ref = db.collection('organizations').document(org_id).collection('sensitiveConfigs').document('verkadaIntegrationSettings')
            org_data = org_ref.get().to_dict()
            if not org_data or 'orgVerkadaBotUserInfo' not in org_data:
                raise https_fn.HttpsError(
                    code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                    message='The organization does not have Verkada integration settings configured.'
                )
            verkada_bot_user_info = org_data['orgVerkadaBotUserInfo']
        if verkada_bot_user_info:
            grant_all_verkada_permissions(verkada_bot_user_info)
            sync_verkada_device_ids(org_id, verkada_bot_user_info)
            sync_verkada_user_groups(org_id, verkada_bot_user_info)
            sync_verkada_site_ids(org_id, verkada_bot_user_info)
        else:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The organization does not have Verkada bot user info configured.'
            )

        return {"response": f"Organization Verkada permissions synced successfully."}

    except https_fn.HttpsError as e:
        raise e

    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}"
        )
    
