from firebase_functions import scheduler_fn
from src.shared import logger
from src.helper_functions.verkada_integration.syncers.sync_verkada_site_ids import sync_verkada_site_ids
from src.helper_functions.verkada_integration.utils.scheduled_function_org_helpers import get_verkada_integrated_orgs_data



@scheduler_fn.on_schedule(schedule="every 24 hours", timeout_sec=540)
def sync_verkada_site_ids_scheduled(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function to sync Verkada site IDs for all enabled organizations every 24 horus.
    """
    logger.info("Starting scheduled Verkada device IDs sync.")

    try:
        verkada_integrated_orgs = get_verkada_integrated_orgs_data()
        if not verkada_integrated_orgs:
            logger.info("No organizations found with Verkada integration enabled.")
            return
        for org_id, verkada_bot_user_info in verkada_integrated_orgs:
            try:
                sync_verkada_site_ids(org_id, verkada_bot_user_info)
                logger.info(f"Successfully synced Verkada device IDs for organization {org_id}.")

            except Exception as e:
                logger.error(f"Error processing organization {org_id}: {str(e)}")
                # Continue to the next organization even if one fails

        logger.info("Finished scheduled Verkada device IDs sync.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the scheduled sync: {str(e)}")