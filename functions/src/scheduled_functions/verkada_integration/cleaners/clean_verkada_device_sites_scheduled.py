from firebase_functions import scheduler_fn, https_fn
from src.shared import logger

from src.helper_functions.verkada_integration.cleaners.clean_verkada_device_sites import clean_verkada_device_sites
from src.helper_functions.verkada_integration.syncers.sync_verkada_site_ids import sync_verkada_site_ids
from src.helper_functions.verkada_integration.utils.scheduled_function_org_helpers import get_site_cleaner_enabled_orgs_data
from src.helper_functions.verkada_integration.cleaners.clean_orphaned_sites import clean_orphaned_sites



@scheduler_fn.on_schedule(schedule="every 24 hours", timeout_sec=540)
def clean_verkada_device_sites_scheduled(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function to sync Verkada device sites for all enabled organizations every 24 hours.
    """
    logger.info("Starting scheduled Verkada device sites sync.")

    try:
        site_cleaner_enabled_orgs = get_site_cleaner_enabled_orgs_data()
        if not site_cleaner_enabled_orgs:
            logger.info("No organizations found with Verkada site cleaner enabled.")
            return
        for org_id, verkada_bot_user_info in site_cleaner_enabled_orgs:
            try:
                clean_verkada_device_sites(org_id, verkada_bot_user_info)
                logger.info(f"Successfully cleaned Verkada device sites for organization {org_id}.")
                sync_verkada_site_ids(org_id, verkada_bot_user_info)
                logger.info(f"Successfully synced Verkada device sites id for organization {org_id}.")
                clean_orphaned_sites(org_id, verkada_bot_user_info)
                logger.info(f"Successfully cleaned orphaned sites for organization {org_id}.")
            except Exception as e:
                logger.error(f"Error processing organization {org_id}: {str(e)}")
                #Continue to the next organization even if one fails
    except Exception as e:
        logger.error(f"Error in scheduled function: {str(e)}")
        # Handle any errors that occur during the scheduled function execution
    logger.info("Finished scheduled Verkada device sites sync.")