from src.helper_functions.verkada_integration.utils.http_utils import requests_with_retry
from src.shared import db, logger
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor
from google.cloud.firestore import WriteBatch





def sync_verkada_site_ids(org_id, verkada_bot_user_info):
    """
    Sync Verkada site IDs for a given organization.
    Args:
        org_id (str): The organization ID.
        verkada_bot_user_info (dict): The user info dictionary containing authentication headers and other details.
    """

    def write_site_ids_to_firestore(batch, updates):
        """Batch write site IDs to Firestore."""
        for update in updates:
            device_doc_ref = db.collection('organizations').document(org_id).collection('devices').document(update['device_id'])
            batch.update(device_doc_ref, {'deviceVerkadaSiteId': update['site_id']})
        batch.commit()
        logger.info(f"Batch site id write completed for {len(updates)} devices.")

    def process_device(device_id, site_id, updates):
        """Process a single device and prepare it for batch writing."""
        device_ref = db.collection('organizations').document(org_id).collection('devices').where('deviceVerkadaDeviceId', '==', device_id).limit(1).stream()
        for device_doc in device_ref:
            updates.append({'device_id': device_doc.id, 'site_id': site_id})

    try:
        verkada_org_shortname = verkada_bot_user_info['org_name']
        verkada_app_init_url = f"https://vappinit.command.verkada.com/__v/{verkada_org_shortname}/app/v2/init"
        verkada_app_init_payload = {}
        response = requests_with_retry('post', verkada_app_init_url, json=verkada_app_init_payload, headers=verkada_bot_user_info['auth_headers'])
        init_data = response.json()
        sites = init_data.get('cameraGroups', {})

        updates = []
        with ThreadPoolExecutor() as executor:
            for site in sites:
                site_id = site.get('cameraGroupId')

                # Collect all device types
                device_types = [
                    ('accessControllers', site.get('accessControllers', [])),
                    ('alarmsDevice', site.get('alarmsDevice', [])),
                    ('biometricAccessController', site.get('biometricAccessController', [])),
                    ('cameras', site.get('cameras', [])),
                    ('connectBox', site.get('connectBox', [])),
                    ('deskApp', site.get('deskApp', [])),
                    ('fortress', site.get('fortress', [])),
                    ('gateway', site.get('gateway', [])),
                    ('intercom', site.get('intercom', [])),
                    ('pavaSpeaker', site.get('pavaSpeaker', [])),
                    ('speaker', site.get('speaker', [])),
                    ('vayuSensor', site.get('vayuSensor', [])),
                    ('wirelessLocks', site.get('wirelessLocks', [])),
                ]

                # Process devices concurrently
                for _, devices in device_types:
                    for device_id in devices:
                        executor.submit(process_device, device_id, site_id, updates)

        # Perform batch writes
        batch_size = 500  # Firestore batch limit
        for i in range(0, len(updates), batch_size):
            batch = db.batch()
            write_site_ids_to_firestore(batch, updates[i:i + batch_size])

    except RequestException as e:
        logger.error(f"Error fetching site data for organization {org_id}: {e}")
        return
    except ValueError as e:
        logger.error(f"Error parsing JSON response for organization {org_id}: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error for organization {org_id}: {e}")
        return
