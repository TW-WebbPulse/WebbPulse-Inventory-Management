from src.helper_functions.verkada_integration.syncers.sync_verkada_user_groups import sync_verkada_user_groups
from src.helper_functions.verkada_integration.cleaners.clean_verkada_user_groups import clean_verkada_user_groups
from src.helper_functions.verkada_integration.utils.scheduled_function_org_helpers import get_site_cleaner_enabled_orgs_data

from firebase_functions import scheduler_fn
from src.shared import logger




@scheduler_fn.on_schedule(schedule="every 24 hours", timeout_sec=540)
def clean_verkada_user_groups_scheduled(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function to sync Verkada user groups for all enabled organizations every 24 hours.
    """
    logger.info("Starting scheduled Verkada user group sync.")

    try:
        site_cleaner_enabled_orgs = get_site_cleaner_enabled_orgs_data()
        if not site_cleaner_enabled_orgs:
            logger.info("No organizations found with Verkada user group sync enabled.")
            return
        for org_id, verkada_bot_user_info in site_cleaner_enabled_orgs:
            try:
                sync_verkada_user_groups(org_id, verkada_bot_user_info)
                clean_verkada_user_groups(org_id, verkada_bot_user_info)
                logger.info(f"Successfully synced and cleaned Verkada groups for organization {org_id}.")

            except Exception as e:
                logger.error(f"Error processing organization {org_id}: {str(e)}")
                # Continue to the next organization even if one fails

        logger.info("Finished scheduled Verkada groups sync.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the scheduled sync: {str(e)}")