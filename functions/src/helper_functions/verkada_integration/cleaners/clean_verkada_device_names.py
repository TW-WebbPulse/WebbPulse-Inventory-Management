import concurrent.futures
from src.shared import db, logger
from ..utils.http_utils import requests_with_retry
from requests.exceptions import RequestException
from src.helper_functions.verkada_integration.utils.rename_device_in_verkada_command import rename_device_in_verkada_command

def _process_device_doc(device_doc, org_id, verkada_bot_user_info):
    """Helper function to process a single device document."""
    try:
        device_data = device_doc.to_dict()
        device_id = device_doc.id
        is_device_checked_out = device_data.get('isDeviceCheckedOut')
        rename_device_in_verkada_command(device_id, org_id, is_device_checked_out, verkada_bot_user_info)
    except Exception as e:
        logger.error(f"Error processing device {device_doc.id} for org {org_id}: {e}", exc_info=True)

def clean_verkada_device_names(org_id, verkada_bot_user_info, max_workers=10):
    """
    Cleans device names in Verkada with the corresponding checkout status in Firestore using multiple threads.
    
    Args:
        verkada_bot_user_info (dict): The Verkada bot user information.
        org_id (str): The organization ID in firestore.
        max_workers (int): The maximum number of threads to use.
    """
    
    logger.info(f"Fetching verkada devices from firestore for organization {org_id}.")
    verkada_devices_ref = db.collection('organizations').document(org_id).collection('devices').where('deviceVerkadaDeviceId', '!=', None).stream()
    
    # Use ThreadPoolExecutor to process documents concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a list of future tasks
        futures = [executor.submit(_process_device_doc, device_doc, org_id, verkada_bot_user_info) for device_doc in verkada_devices_ref]
        
        # Wait for all futures to complete and log any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Raises exceptions from the worker thread if any occurred
            except Exception as e:
                logger.error(f"A thread encountered an error during device sync for org {org_id}: {e}")

    logger.info(f"Finished syncing Verkada device names for organization {org_id}.")