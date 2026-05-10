from firebase_functions import https_fn
from firebase_admin import firestore
from src.shared import db, apply_rate_limiting, POSTcorsrules, logger
from src.helper_functions.auth.auth_functions import (
    check_user_is_authed,
    check_user_is_email_verified,
    check_user_token_current,
    check_user_is_org_admin,
)
from src.helper_functions.verkada_integration.cleaners.clean_verkada_user_list import (
    clean_verkada_user_list,
)
from src.helper_functions.verkada_integration.cleaners.clean_verkada_user_groups import (
    clean_verkada_user_groups,
)
from src.helper_functions.verkada_integration.cleaners.clean_verkada_device_sites import (
    clean_verkada_device_sites,
)
from src.helper_functions.verkada_integration.cleaners.clean_verkada_device_names import (
    clean_verkada_device_names,
)
from src.helper_functions.verkada_integration.syncers.sync_verkada_site_ids import (
    sync_verkada_site_ids,
)
from src.helper_functions.verkada_integration.cleaners.clean_orphaned_sites import (
    clean_orphaned_sites,
)


@https_fn.on_call(cors=POSTcorsrules, timeout_sec=540)
def update_verkada_site_cleaner_status_callable(req: https_fn.CallableRequest) -> any:
    """
    Updates the Verkada Site Cleaner status for a given organization.
    """
    # Apply rate limiting
    apply_rate_limiting(req, "update_verkada_site_cleaner_status_callable")

    try:
        org_id = req.data.get("orgId")
        enabled = req.data.get("enabled")

        check_user_is_authed(req)
        check_user_is_email_verified(req)
        check_user_token_current(req)
        check_user_is_org_admin(req, org_id)

        if not org_id:
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The function must be called with an "orgId" argument.',
            )
        if enabled is None or not isinstance(enabled, bool):
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                message='The function must be called with an "enabled" (boolean) argument.',
            )

        org_settings_ref = db.collection("organizations").document(org_id)
        org_settings_ref.set({"orgVerkadaSiteCleanerEnabled": enabled}, merge=True)

        if enabled:
            # login to Verkada and run the cleaner
            current_verkada_settings = (
                org_settings_ref.collection("sensitiveConfigs")
                .document("verkadaIntegrationSettings")
                .get()
                .to_dict()
            )
            verkada_bot_user_info = current_verkada_settings.get(
                "orgVerkadaBotUserInfo", {}
            )
            if not verkada_bot_user_info:
                raise https_fn.HttpsError(
                    code=https_fn.FunctionsErrorCode.FAILED_PRECONDITION,
                    message="Verkada bot user information is not set. Please ensure the Verkada integration is properly configured.",
                )
            try:
                functions = [
                    (
                        "clean_verkada_user_list",
                        lambda: clean_verkada_user_list(verkada_bot_user_info),
                    ),
                    (
                        "clean_verkada_user_groups",
                        lambda: clean_verkada_user_groups(
                            org_id, verkada_bot_user_info
                        ),
                    ),
                    (
                        "clean_verkada_device_names",
                        lambda: clean_verkada_device_names(
                            org_id, verkada_bot_user_info
                        ),
                    ),
                    (
                        "clean_verkada_device_sites",
                        lambda: clean_verkada_device_sites(
                            org_id, verkada_bot_user_info
                        ),
                    ),
                    (
                        "sync_verkada_site_ids",
                        lambda: sync_verkada_site_ids(org_id, verkada_bot_user_info),
                    ),
                    (
                        "clean_orphaned_sites",
                        lambda: clean_orphaned_sites(org_id, verkada_bot_user_info),
                    ),
                ]

                for func_name, func in functions:
                    func()
                    logger.info(f"Successfully {func_name} for organization {org_id}.")
            except Exception as e:
                logger.error(
                    f"Error cleaning sites for organization: {org_id}, process: {func_name}, error: {e}"
                )

        return {
            "status": "success",
            "message": f"Verkada Site Cleaner status for organization {org_id} updated to {enabled}.",
        }

    except https_fn.HttpsError as e:
        # Re-raise HttpsError exceptions directly
        raise e
    except Exception as e:

        logger.error(f"An error occurred: {e}")
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INTERNAL,
            message=f"An internal error occurred: {str(e)}",
        )
