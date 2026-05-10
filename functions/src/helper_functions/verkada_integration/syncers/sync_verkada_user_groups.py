from src.shared import db, logger
from ..utils.http_utils import requests_with_retry
from requests.exceptions import RequestException

def sync_verkada_user_groups(org_id, verkada_bot_user_info):
    """
    Syncs user groups from Verkada to the Firestore database.
    """
    logger.info("Syncing Verkada user groups...")
    verkada_org_id = verkada_bot_user_info.get('org_id')
    verkada_bot_user_id = verkada_bot_user_info.get('user_id')
    verkada_bot_headers = verkada_bot_user_info.get('auth_headers')

    def fetch_verkada_user_groups(verkada_org_id, verkada_bot_user_id):
        """
        Fetches user groups from Verkada.
        """
        url = f"https://vauth.command.verkada.com/__v/webbpulse/security_entity_group/list"
        payload = {
            "organizationId": verkada_org_id,
            "includeMembers": False,
            "includeMemberCount": False,
        }
        response = requests_with_retry(
            "post",
            url=url,
            headers=verkada_bot_headers,
            json=payload
        )
        user_groups = response.json().get("securityEntityGroup", [])
        logger.info(f"Fetched {len(user_groups)} user groups from Verkada.")
        if not user_groups:
            logger.warning("No user groups found in the response.")
            return []
        return [
            {
                "groupId": group.get("entityGroupId"),
                "groupName": group.get("name"),
            }
            for group in user_groups
            if group.get("entityGroupId") and group.get("name") is not None
        ]
    def update_firestore_with_user_groups(org_id, new_user_groups):
        """
        Updates Firestore with the fetched user groups.
        """
        org_doc_ref = db.collection('organizations').document(org_id)
        try:
            doc = org_doc_ref.get()
            existing_groups_data = doc.to_dict()
            if existing_groups_data and 'orgVerkadaUserGroups' in existing_groups_data:
                existing_groups = existing_groups_data['orgVerkadaUserGroups']
            else:
                existing_groups = []
        except Exception as e:
            logger.error(f"Error fetching existing Verkada user groups for org {org_id}: {e}")
            existing_groups = []
        
        # Create a map of existing groups by groupId for easy lookup of whitelist status
        existing_groups_map = {group['groupId']: group for group in existing_groups if 'groupId' in group}

        merged_user_groups = []
        
        for new_group in new_user_groups:
            group_id = new_group.get("groupId")
            if group_id:
                # Preserve existing whitelist status if group already exists
                is_whitelisted = existing_groups_map.get(group_id, {}).get('isWhitelisted', False)
                merged_group_data = {
                    "groupId": group_id,
                    "groupName": new_group.get("groupName"),
                    "isWhitelisted": is_whitelisted
                }
                merged_user_groups.append(merged_group_data)
            else:
                logger.warning(f"Skipping group due to missing groupId: {new_group}")
        org_doc_ref.set({
            'orgVerkadaUserGroups': merged_user_groups
        }, merge=True)

    # Fetch user groups from Verkada
    user_groups = fetch_verkada_user_groups(verkada_org_id, verkada_bot_user_id)

    # Update Firestore with the fetched user groups
    update_firestore_with_user_groups(org_id, user_groups)
