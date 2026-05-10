import concurrent.futures
from ..utils.http_utils import requests_with_retry
from requests.exceptions import RequestException
from src.shared import logger

def _process_user(user, verkada_org_shortname, verkada_org_id, auth_headers, verkada_bot_user_id):
    """
    Processes a single user: checks email criteria and deletes if necessary.
    This function is designed to be run in a separate thread.
    """
    user_email = user.get("email")
    user_id = user.get("userId")

    if not user_email or not user_id:
        logger.warning(f"Skipping user with missing email or ID: {user}")
        return

    logger.info(f"Checking user {user_email}")

    # Skip the bot user itself
    if user_id == verkada_bot_user_id:
        logger.info(f"{user_email} is the bot user, skipping")
        return

    # Check if user email matches deletion criteria
    if "@verkada." not in user_email or "+" in user_email:
        logger.info(f"{user_email} does not meet criteria, attempting deletion...")
        delete_user_url = f"https://vcorgi.command.verkada.com/__v/{verkada_org_shortname}/org/{verkada_org_id}/users/delete"
        delete_user_payload = {"userIds": [user_id]}
        try:
            response = requests_with_retry(
                "post",
                url=delete_user_url,
                headers=auth_headers,
                json=delete_user_payload,
            )
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            logger.info(f"User {user_email} deleted successfully. Status: {response.status_code}")
        except RequestException as e:
            # Log specific request errors, including status code if available
            status_code = e.response.status_code if e.response else "N/A"
            logger.error(f"Error deleting user {user_email} (RequestException - Status: {status_code}): {e}")
        except Exception as e:
            # Catch any other unexpected errors during deletion
            logger.error(f"Unexpected error deleting user {user_email}: {e}")
    else:
        logger.info(f"User {user_email} meets criteria, keeping.")


def clean_verkada_user_list(verkada_bot_user_info):
    """
    Cleans the Verkada user list by removing users emails that dont match expected patterns,
    using multithreading for efficiency.

    Args:
        verkada_bot_user_info (dict): Information about the logged-in Verkada bot user.
    """
    # Extract necessary information from verkada_bot_user_info
    verkada_org_shortname = verkada_bot_user_info.get("org_name")
    verkada_org_id = verkada_bot_user_info.get("org_id")
    auth_headers = verkada_bot_user_info.get("auth_headers")
    verkada_bot_user_id = verkada_bot_user_info.get("user_id")

    if not verkada_org_shortname or not verkada_org_id or not auth_headers or not verkada_bot_user_id:
        raise ValueError("Missing required information in verkada_bot_user_info.")

    get_users_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_shortname}/organization/{verkada_org_id}/users/search"
    get_users_payload = {
        "paging": {"pageSize": 2000, "sortOrder": ["full_name:asc", "email:asc"]},
        "isVisitor": False,
        "groupIds": [],
        "organizationId": verkada_org_id,
        "roles": [],
        "status": ["active", "deactivated", "invited"],
        "includeRoleGrants": False,
        "includeGroups": False,
        "useEs": False,
    }

    users_data = [] # Initialize to empty list
    try:
        logger.info("Getting user data...")
        response = requests_with_retry(
            "post",
            url=get_users_url,
            headers=auth_headers,
            json=get_users_payload,
        )
        response.raise_for_status() # Check for HTTP errors
        users_data = response.json().get("users", []) # Default to empty list if 'users' key is missing
        logger.info(f"Retrieved {len(users_data)} users.")
    except RequestException as e:
        logger.error(f"Error getting user data (RequestException): {e}")
        return # Exit if we can't get user data
    except ValueError as e: # Catch JSON decoding errors
        logger.error(f"Error decoding user data JSON: {e}")
        return
    except Exception as e: # Catch other unexpected errors
        logger.error(f"Unexpected error getting user data: {e}")
        return


    # DANGEROUS BLOCK - Now multithreaded
    if not users_data:
        logger.info("No users found to process.")
        return

    max_workers = 10 
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each user to the executor
        future_to_user = {
            executor.submit(
                _process_user,
                user,
                verkada_org_shortname,
                verkada_org_id,
                auth_headers,
                verkada_bot_user_id,
            ): user.get("email", "Unknown") # Map future to email for logging
            for user in users_data
        }

        # Process completed futures as they finish
        for future in concurrent.futures.as_completed(future_to_user):
            user_email = future_to_user[future]
            try:
                future.result()  # Retrieve result or raise exception from the thread
            except Exception as exc:
                # Log exceptions raised within the thread task
                logger.error(f"Thread processing user {user_email} generated an exception: {exc}")

    logger.info("Finished processing all users.")