from src.shared import db, logger
from ..utils.http_utils import requests_with_retry
from requests.exceptions import RequestException


def clean_verkada_user_groups(org_id, verkada_bot_user_info):
    """
    Cleans up the Verkada user groups by removing any groups that are not in the allowed list.
    """
    try:
        # Fetch the allowed groups from Firestore
        verkada_integration_ref = db.collection('organizations').document(org_id).collection('sensitiveConfigs').document('verkadaIntegrationSettings').get()
        if not verkada_integration_ref.exists:
            logger.warning(f"Verkada integration settings not found for organization {org_id}.")
            return
        org_verkada_user_groups = verkada_integration_ref.to_dict().get('orgVerkadaUserGroups', [])
        if not org_verkada_user_groups:
            logger.warning(f"No groups found for organization {org_id}.")
            return
        
        for group in org_verkada_user_groups:
            if not group.get('isWhitelisted'):
                remove_group(verkada_bot_user_info, group)
        
        logger.info(f"Cleaned up user groups for organization {org_id}.")
    
    except Exception as e:
        logger.error(f"Error cleaning up user groups for organization {org_id}: {str(e)}")

def remove_group(verkada_bot_user_info, group):
    """
    Removes a group from the Verkada organization.
    """
    verkada_org_short_name = verkada_bot_user_info.get('org_name')
    bot_auth_headers = verkada_bot_user_info.get('auth_headers')
    group_id = group.get('groupId')
    
    try:
        # Make a request to the Verkada API to remove the group
        delete_url = f"https://vauth.command.verkada.com/__v/{verkada_org_short_name}/security_entity_group/delete"
        response = requests_with_retry(
            'post',
            delete_url,
            headers=bot_auth_headers,
            json={"securityEntityGroupIds":[group_id]},
        )

    except RequestException as e:
        # Handle request exceptions
        logger.error(f"Failed to remove group {group_id} from Verkada: {e}")
        return
    except Exception as e:
        # Handle any other exceptions
        logger.error(f"An unexpected error occurred while removing group {group_id}: {e}")
        return