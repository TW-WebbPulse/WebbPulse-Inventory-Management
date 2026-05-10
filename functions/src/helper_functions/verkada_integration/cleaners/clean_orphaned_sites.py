from src.shared import db, logger
from typing import Set, List, Optional
from concurrent.futures import ThreadPoolExecutor

from src.helper_functions.verkada_integration.utils.http_utils import requests_with_retry


def clean_orphaned_sites(org_id: str, verkada_bot_user_info: dict) -> None:
    """
    Identifies and cleans up orphaned Verkada sites that are no longer associated with any devices.
    Also cleans up orphaned classic alarm zones if a configured zone is specified.
    Zone deletions occur before site deletions since site deletions are dependent on zone deletions.
    
    Args:
        org_id (str): The organization ID
        verkada_bot_user_info (dict): Verkada bot user info for API calls
    """
    logger.info(f"Starting orphaned site cleanup for organization {org_id}")
    
    try:
        # Clean up orphaned classic alarm zones FIRST (before site deletions)
        # This is critical because site deletions are dependent on zone deletions
        logger.info("Starting classic alarm zone cleanup phase...")
        clean_orphaned_classic_alarm_zones(org_id, verkada_bot_user_info)
        logger.info("Completed classic alarm zone cleanup phase")
        
        # Get all unique site IDs currently in use by devices
        logger.info("Starting site cleanup phase...")
        active_site_ids = get_active_site_ids(org_id)
        logger.info(f"Found {len(active_site_ids)} active site IDs in use by devices")
        
        # Get all site IDs from Verkada API
        verkada_site_ids = get_verkada_site_ids(verkada_bot_user_info)
        logger.info(f"Found {len(verkada_site_ids)} total site IDs from Verkada")
        
        # Find orphaned sites (in Verkada but not used by any devices)
        orphaned_site_ids = verkada_site_ids - active_site_ids
        logger.info(f"Found {len(orphaned_site_ids)} orphaned site IDs")
        
        if orphaned_site_ids:
            logger.info(f"Cleaning up orphaned sites: {list(orphaned_site_ids)}")
            # Clean up orphaned sites AFTER zone cleanup is complete
            cleanup_orphaned_sites(orphaned_site_ids, verkada_bot_user_info)
        else:
            logger.info("No orphaned sites found")
            
    except Exception as e:
        logger.error(f"Error during orphaned site cleanup for org {org_id}: {e}")
        raise


def get_active_site_ids(org_id: str) -> Set[str]:
    """
    Get all unique site IDs that are currently being used by devices.
    
    Args:
        org_id (str): The organization ID
        
    Returns:
        Set[str]: Set of active site IDs
    """
    active_site_ids = set()
    
    try:
        # Query all devices that have a deviceVerkadaSiteId
        devices_ref = db.collection('organizations').document(org_id).collection('devices')
        devices = devices_ref.where('deviceVerkadaSiteId', '!=', None).stream()
        
        for device in devices:
            device_data = device.to_dict()
            site_id = device_data.get('deviceVerkadaSiteId')
            if site_id and site_id.strip():  # Ensure site_id is not empty
                active_site_ids.add(site_id)
                
        logger.info(f"Retrieved {len(active_site_ids)} unique active site IDs from devices")
        return active_site_ids
        
    except Exception as e:
        logger.error(f"Error retrieving active site IDs: {e}")
        raise


def get_verkada_site_ids(verkada_bot_user_info: dict) -> Set[str]:
    """
    Get all site IDs from Verkada API.
    
    Args:
        verkada_bot_user_info (dict): Verkada bot user info
        
    Returns:
        Set[str]: Set of all site IDs from Verkada
    """
    
    
    verkada_site_ids = set()
    
    try:
        verkada_org_shortname = verkada_bot_user_info['org_name']
        verkada_site_list_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_shortname}/org/site/list"
        verkada_app_init_payload = {
            "orgId": verkada_bot_user_info['org_id']
        }
        
        response = requests_with_retry('post', verkada_site_list_url, 
                                     json=verkada_app_init_payload, 
                                     headers=verkada_bot_user_info['auth_headers'])
        site_data = response.json()
        sites = site_data.get('sites', [])
        
        for site in sites:
            site_id = site.get('siteId')
            if site_id:
                verkada_site_ids.add(site_id)
                
        logger.info(f"Retrieved {len(verkada_site_ids)} site IDs from Verkada API")
        return verkada_site_ids
        
    except Exception as e:
        logger.error(f"Error retrieving Verkada site IDs: {e}")
        raise

def get_configured_classic_alarm_zone(org_id: str) -> Optional[str]:
    """
    Get the configured classic alarm zone for an organization.
    
    Args:
        org_id (str): The organization ID
        
    Returns:
        Optional[str]: The configured classic alarm zone ID, or None if not configured
    """
    try:
        org_ref = db.collection('organizations').document(org_id).get()
        if not org_ref.exists:
            raise Exception("Organization document not found in Firestore.")
        org_data = org_ref.to_dict()
        if org_data is None:
            raise Exception("Organization document is empty or corrupted.")
        product_designations = org_data.get('orgVerkadaProductSiteDesignations')
        if product_designations is None:
            raise Exception(f"Product designations not found in Firestore for org {org_id}.")
        return product_designations.get('Classic Alarm Zone')
    except Exception as e:
        logger.error(f"Error getting configured classic alarm zone for org {org_id}: {e}")
        raise

def get_classic_alarm_zones(verkada_bot_user_info: dict) -> Set[str]:
    """
    Get all classic alarm zones from Verkada.
    
    Args:
        verkada_bot_user_info (dict): Verkada bot user info
        
    Returns:
        Set[str]: Set of all classic alarm zone IDs from Verkada
    """
    
    verkada_zone_ids = set()
    
    try:
        verkada_org_shortname = verkada_bot_user_info['org_name']
        verkada_zone_list_url = f"https://alarms.command.verkada.com/__v/{verkada_org_shortname}/zone/list"
        verkada_zone_list_payload = {
            "organizationId": verkada_bot_user_info['org_id'],
            "includeLastEvent": False
        }
        
        
        
        response = requests_with_retry('post', verkada_zone_list_url, 
                                     json=verkada_zone_list_payload, 
                                     headers=verkada_bot_user_info['auth_headers'])
        
        zone_data = response.json()
        
        
        zones = zone_data.get('zone', [])
        logger.info(f"Found {len(zones)} zones in response")
        
        for i, zone in enumerate(zones):
            zone_id = zone.get('zoneId')
            if zone_id:
                verkada_zone_ids.add(zone_id)
                
            else:
                logger.warning(f"Zone {i} has no zoneId: {zone}")
                
        logger.info(f"Retrieved {len(verkada_zone_ids)} classic alarm zone IDs from Verkada API")
        logger.info(f"Zone IDs: {list(verkada_zone_ids)}")
        return verkada_zone_ids
        
    except Exception as e:
        logger.error(f"Error retrieving Verkada classic alarm zone IDs: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise

def delete_classic_alarm_zone(zone_id: str, verkada_bot_user_info: dict) -> bool:
    """
    Delete a classic alarm zone from Verkada.
    
    Args:
        zone_id (str): The zone ID of the classic alarm zone to delete
        verkada_bot_user_info (dict): Verkada bot user info
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    
    try:
        verkada_org_shortname = verkada_bot_user_info['org_name']
        delete_url = f"https://alarms.command.verkada.com/__v/{verkada_org_shortname}/zone/delete"
        payload = {
            "zoneId": zone_id
        }
        
        response = requests_with_retry('post', delete_url, 
                                     json=payload, 
                                     headers=verkada_bot_user_info['auth_headers'])
        response.raise_for_status()
        
        logger.info(f"Successfully deleted classic alarm zone: {zone_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete classic alarm zone {zone_id}: {e}")
        return False

def clean_orphaned_classic_alarm_zones(org_id: str, verkada_bot_user_info: dict) -> None:
    """
    Identifies and cleans up orphaned classic alarm zones that are not the configured zone.
    
    Args:
        org_id (str): The organization ID
        verkada_bot_user_info (dict): Verkada bot user info for API calls
    """
    logger.info(f"Starting orphaned classic alarm zone cleanup for organization {org_id}")
    
    try:
        # Get the configured classic alarm zone
        logger.info(f"Getting configured classic alarm zone for org {org_id}")
        configured_zone_id = get_configured_classic_alarm_zone(org_id)
        logger.info(f"Retrieved configured zone ID: {configured_zone_id}")
        
        # If no zone is configured, skip the cleanup
        if not configured_zone_id:
            logger.info("No classic alarm zone configured for this organization, skipping zone cleanup")
            return
        
        logger.info(f"Configured classic alarm zone: {configured_zone_id}")
        
        # Get all classic alarm zones from Verkada
        logger.info("Retrieving all classic alarm zones from Verkada...")
        verkada_zone_ids = get_classic_alarm_zones(verkada_bot_user_info)
        logger.info(f"Found {len(verkada_zone_ids)} total classic alarm zones from Verkada")
        logger.info(f"All zone IDs: {list(verkada_zone_ids)}")
        
        # Find orphaned zones (in Verkada but not the configured zone)
        orphaned_zone_ids = verkada_zone_ids - {configured_zone_id}
        logger.info(f"Found {len(orphaned_zone_ids)} orphaned classic alarm zone IDs")
        logger.info(f"Orphaned zone IDs: {list(orphaned_zone_ids)}")
        
        if orphaned_zone_ids:
            # Clean up orphaned zones
            cleanup_orphaned_classic_alarm_zones(orphaned_zone_ids, verkada_bot_user_info)
        else:
            logger.info("No orphaned classic alarm zones found")
            
    except Exception as e:
        logger.error(f"Error during orphaned classic alarm zone cleanup for org {org_id}: {e}")
        raise

def cleanup_orphaned_classic_alarm_zones(orphaned_zone_ids: Set[str], verkada_bot_user_info: dict) -> None:
    """
    Clean up orphaned classic alarm zones by removing them from Verkada.
    If a zone deletion fails, the process continues with the next zone.
    
    Args:
        orphaned_zone_ids (Set[str]): Set of orphaned zone IDs to clean up
        verkada_bot_user_info (dict): Verkada bot user info
    """
    def delete_zone(zone_id: str) -> tuple[str, bool]:
        """Delete a single classic alarm zone from Verkada. Returns (zone_id, success)."""
        success = delete_classic_alarm_zone(zone_id, verkada_bot_user_info)
        return (zone_id, success)
    
    # Process deletions in parallel for better performance
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(delete_zone, orphaned_zone_ids))
    
    # Track successful and failed deletions
    successful_zones = []
    failed_zones = []
    
    for zone_id, success in results:
        if success:
            successful_zones.append(zone_id)
        else:
            failed_zones.append(zone_id)
    
    successful_deletions = len(successful_zones)
    failed_deletions = len(failed_zones)
    
    logger.info(f"Classic alarm zone cleanup completed: {successful_deletions} successful, {failed_deletions} failed")
    
    if successful_zones:
        logger.info(f"Successfully deleted zones: {', '.join(successful_zones)}")
    
    if failed_zones:
        logger.warning(f"Failed to delete zones (process continued): {', '.join(failed_zones)}")


def cleanup_orphaned_sites(orphaned_site_ids: Set[str], verkada_bot_user_info: dict) -> None:
    """
    Clean up orphaned sites by removing them from Verkada.
    
    Args:
        orphaned_site_ids (Set[str]): Set of orphaned site IDs to clean up
        verkada_bot_user_info (dict): Verkada bot user info
    """
    
    verkada_org_shortname = verkada_bot_user_info['org_name']
    auth_headers = verkada_bot_user_info['auth_headers']
    
    def delete_site(site_id: str) -> bool:
        """Delete a single site from Verkada."""
        try:
            # Use the correct API endpoint for site deletion
            # Based on the pattern used in other Verkada API calls in the codebase
            delete_url = f"https://vprovision.command.verkada.com/__v/{verkada_org_shortname}/org/camera_group/delete"
            payload = {
                "cameraGroupId": site_id
            }
            response = requests_with_retry('post', delete_url, headers=auth_headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"Successfully deleted orphaned site: {site_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete orphaned site {site_id}: {e}")
            return False
    
    # Process deletions in parallel for better performance
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(delete_site, orphaned_site_ids))
    
    successful_deletions = sum(results)
    logger.info(f"Successfully deleted {successful_deletions}/{len(orphaned_site_ids)} orphaned sites")


def get_site_usage_stats(org_id: str) -> dict:
    """
    Get statistics about site usage for monitoring purposes.
    
    Args:
        org_id (str): The organization ID
        
    Returns:
        dict: Statistics about site usage
    """
    try:
        devices_ref = db.collection('organizations').document(org_id).collection('devices')
        
        # Get devices with site IDs
        devices_with_sites = devices_ref.where('deviceVerkadaSiteId', '!=', None).stream()
        
        # Count devices per site
        site_device_counts = {}
        total_devices_with_sites = 0
        
        for device in devices_with_sites:
            device_data = device.to_dict()
            site_id = device_data.get('deviceVerkadaSiteId')
            if site_id:
                site_device_counts[site_id] = site_device_counts.get(site_id, 0) + 1
                total_devices_with_sites += 1
        
        # Get total devices
        total_devices = len(list(devices_ref.stream()))
        
        stats = {
            'total_devices': total_devices,
            'devices_with_sites': total_devices_with_sites,
            'devices_without_sites': total_devices - total_devices_with_sites,
            'unique_sites_in_use': len(site_device_counts),
            'site_device_distribution': site_device_counts
        }
        
        logger.info(f"Site usage stats for org {org_id}: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting site usage stats for org {org_id}: {e}")
        raise 