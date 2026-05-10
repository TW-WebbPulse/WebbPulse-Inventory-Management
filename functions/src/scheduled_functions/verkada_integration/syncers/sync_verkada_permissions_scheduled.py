from firebase_functions import scheduler_fn, https_fn
from src.shared import logger
from src.helper_functions.verkada_integration.utils.grant_all_verkada_permissions import grant_all_verkada_permissions
from src.helper_functions.verkada_integration.utils.scheduled_function_org_helpers import get_verkada_integrated_orgs_data




@scheduler_fn.on_schedule(schedule="every 24 hours", timeout_sec=540)
def sync_verkada_permissions_scheduled(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function to sync Verkada permissions for all enabled organizations every 24 hours.
    """
    logger.info("Starting scheduled Verkada permissions sync.")

    try:
        verkada_integrated_orgs = get_verkada_integrated_orgs_data()
        if not verkada_integrated_orgs:
            logger.info("No organizations found with Verkada integration enabled.")
            return
        for org_id, verkada_bot_user_info in verkada_integrated_orgs:
            try:
                grant_all_verkada_permissions(verkada_bot_user_info)
                logger.info(f"Successfully synced Verkada permissions for organization {org_id}.")

            except Exception as e:
                logger.error(f"Error processing organization {org_id}: {str(e)}")
                # Continue to the next organization even if one fails

        logger.info("Finished scheduled Verkada permissions sync.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the scheduled sync: {str(e)}")
