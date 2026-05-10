import concurrent.futures
from requests.exceptions import RequestException, JSONDecodeError
from .http_utils import requests_with_retry
from src.shared import logger


def grant_all_verkada_permissions(verkada_bot_user_info: dict) -> None:
    """
    Grants all permissions to the Verkada bot user using concurrent requests with retries.
    Args:
        verkada_bot_user_info (dict): A dictionary containing the user token, organization ID, and other relevant information.

    """
    user_id = verkada_bot_user_info.get("user_id")
    org_id = verkada_bot_user_info.get("org_id")
    auth_headers = verkada_bot_user_info.get("auth_headers")
    org_shortname = verkada_bot_user_info.get("org_name")


    def set_camera_site_admin(site_id, user_id, org_id, auth_headers):
        url = f"https://vprovision.command.verkada.com/__v/{org_shortname}/org/set_user_permissions"
        payload = {
            "targetUserId": user_id,
            "organizationId": org_id,
            "returnPermissions": False,
            "grant": [{"entityId": site_id, "roleKey": "SITE_ADMIN", "permission": "SITE_ADMIN"}],
            "revoke": [],
        }
        try:
            response = requests_with_retry('post', url, json=payload, headers=auth_headers)
            logger.info(f"Camera admin permissions set for site {site_id}. Status: {response.status_code}")
        except RequestException as e:
            logger.error(f"Error setting Camera admin permissions for site {site_id} after retries: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error setting Camera admin permissions for site {site_id}: {e}")

    def set_access_site_admin(site_id, user_id, auth_headers):
        url = f"https://vcerberus.command.verkada.com/__v/{org_shortname}/access/v2/user/roles/modify"
        payload = {
            "grants": [{"granteeId": user_id, "entityId": site_id, "roleKey": "ACCESS_CONTROL_SITE_ADMIN", "role": "ACCESS_CONTROL_SITE_ADMIN"}],
            "revokes": [],
        }
        try:
            response = requests_with_retry('post', url, json=payload, headers=auth_headers)
            logger.info(f"Access admin permissions set for site {site_id}. Status: {response.status_code}")
        except RequestException as e:
            logger.error(f"Error setting Access admin permissions for site {site_id} after retries: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error setting Access admin permissions for site {site_id}: {e}")

    def set_alarm_site_admin(site_id, user_id, org_id, auth_headers):
        url = f"https://vprovision.command.verkada.com/__v/{org_shortname}/org/set_user_permissions"
        payload = {
            "targetUserId": user_id,
            "organizationId": org_id,
            "returnPermissions": False,
            "grant": [{"entityId": site_id, "roleKey": "SITE_ALARM_CONTROLLER", "permission": "SITE_ALARM_CONTROLLER"}],
            "revoke": [],
        }
        try:
            response = requests_with_retry('post', url, json=payload, headers=auth_headers)
            logger.info(f"Alarm admin permissions set for site {site_id}. Status: {response.status_code}")
        except RequestException as e:
            logger.error(f"Error setting Alarm admin permissions for site {site_id} after retries: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error setting Alarm admin permissions for site {site_id}: {e}")

    def set_access_system_admin(user_id, org_id, auth_headers):
        url = f"https://vcerberus.command.verkada.com/__v/{org_shortname}/access/v2/user/roles/modify"
        payload = {
            "grants": [{"entityId": org_id, "granteeId": user_id, "roleKey": "ACCESS_CONTROL_SYSTEM_ADMIN", "role": "ACCESS_CONTROL_SYSTEM_ADMIN"}],
            "revokes": [],
        }
        try:
            response = requests_with_retry('post', url, json=payload, headers=auth_headers)
            logger.info(f"Access system admin permissions set for org. Status: {response.status_code}")
        except RequestException as e:
            logger.error(f"Error setting Access system admin permissions after retries: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error setting Access system admin permissions: {e}")

    def set_access_user_admin(user_id, org_id, auth_headers):
        url = f"https://vcerberus.command.verkada.com/__v/{org_shortname}/access/v2/user/roles/modify"
        payload = {
            "grants": [{"entityId": org_id, "granteeId": user_id, "roleKey": "ACCESS_CONTROL_USER_ADMIN", "role": "ACCESS_CONTROL_USER_ADMIN"}],
            "revokes": [],
        }
        try:
            response = requests_with_retry('post', url, json=payload, headers=auth_headers)
            logger.info(f"Access user admin permissions set for org. Status: {response.status_code}")
        except RequestException as e:
            logger.error(f"Error setting Access user admin permissions after retries: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error setting Access user admin permissions: {e}")

    def get_all_site_ids():
        init_url = f'https://vappinit.command.verkada.com/__v/{org_shortname}/app/v2/init'
        init_payload = {"fieldsToSkip": ["permissions"]}
        init_auth_headers = auth_headers
        try:
            init_response = requests_with_retry('post', init_url, json=init_payload, headers=init_auth_headers)
            init_data = init_response.json()
            sites = init_data.get("cameraGroups", [])
            site_ids = [site["cameraGroupId"] for site in sites if "cameraGroupId" in site]
            return site_ids
        except RequestException as e:
            logger.error(f"Error fetching initial site data after retries: {e}")
            return []
        except (JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing site data response: {e}")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error fetching site data: {e}")
            return []


    def set_all_admins_for_site(site_id, user_id, org_id, auth_headers):
        set_camera_site_admin(site_id, user_id, org_id, auth_headers)
        set_access_site_admin(site_id, user_id, auth_headers)
        set_alarm_site_admin(site_id, user_id, org_id, auth_headers)

    # --- Main execution flow ---

    if not all([user_id, org_id, auth_headers]):
        logger.error("Error: Missing required user info (user_id, org_id, or auth_headers). Cannot grant permissions.")
        return

    site_ids = get_all_site_ids()
    if not site_ids:
        logger.warning("Warning: No site IDs found or error fetching sites. Skipping site-specific permissions.")

    # Use ThreadPoolExecutor to run tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        # Submit site-specific tasks only if site_ids were found
        if site_ids:
            futures.extend([executor.submit(set_all_admins_for_site, site_id, user_id, org_id, auth_headers) for site_id in site_ids])

        # Submit org-level tasks
        futures.append(executor.submit(set_access_system_admin, user_id, org_id, auth_headers))
        futures.append(executor.submit(set_access_user_admin, user_id, org_id, auth_headers))

    logger.info("Finished attempting to set all admin permissions.")
