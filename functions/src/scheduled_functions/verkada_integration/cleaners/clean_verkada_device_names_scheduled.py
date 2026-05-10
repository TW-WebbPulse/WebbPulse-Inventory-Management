from firebase_functions import scheduler_fn
from src.helper_functions.verkada_integration.cleaners.clean_verkada_device_names import clean_verkada_device_names
from src.helper_functions.verkada_integration.utils.scheduled_function_org_helpers import get_site_cleaner_enabled_orgs_data
from src.shared import logger



@scheduler_fn.on_schedule(schedule="every 24 hours", timeout_sec=540)
def clean_verkada_device_names_scheduled(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function to sync Verkada device names for all enabled organizations every 24 hours.
    """
    logger.info("Starting scheduled Verkada permissions sync.")

    try:
        site_cleaner_enabled_orgs = get_site_cleaner_enabled_orgs_data()

        if not site_cleaner_enabled_orgs:
            logger.info("No organizations found with Verkada site cleaner enabled.")
            return
        for org_id, verkada_bot_user_info in site_cleaner_enabled_orgs:
            try:
                clean_verkada_device_names(org_id, verkada_bot_user_info)
                logger.info(f"Successfully cleaned Verkada device names for organization {org_id}.")
            except Exception as e:
                logger.error(f"Error cleaning Verkada device names for organization {org_id}: {str(e)}")

        logger.info("Finished scheduled Verkada device name cleaning.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the scheduled sync: {str(e)}")