import concurrent.futures
from src.helper_functions.verkada_integration.utils.check_verkada_device_type import check_verkada_device_type
from src.shared import db, logger



# Renamed: This function now only checks the type and returns data for batching
def _get_device_update_data(args):
    """Helper function to get data needed to update a single device's Verkada type."""
    doc_id, device_serial_number = args
    try:
        device_verkada_device_type = check_verkada_device_type(device_serial_number)
        if device_verkada_device_type is not None:
            # Return doc_id and the new type if found
            return (doc_id, device_verkada_device_type)
        else:
            # Return None if no type found or no update needed
            return None
    except Exception as e:
        logger.error(f"Error checking device type for {doc_id} ({device_serial_number}): {e}")
        return None # Indicate error or inability to process

def update_all_devices_verkada_device_type(org_id: str, max_workers: int = 10, batch_size: int = 499) -> None:
    """
    Updates the Verkada device type for all devices in an organization concurrently
    using batch writes.
    """
    org_ref = db.collection('organizations').document(org_id)
    devices_ref = org_ref.collection('devices')
    docs = devices_ref.stream()

    tasks = []
    for doc in docs:
        device_serial_number = doc.get('deviceSerialNumber')
        if device_serial_number:
            # Pass only doc_id and serial number needed for the check
            tasks.append((doc.id, device_serial_number))

    update_data_list = []
    # Use ThreadPoolExecutor for concurrent checks
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map tasks to the checking function
        results = executor.map(_get_device_update_data, tasks)
        # Filter out None results (errors or no update needed)
        update_data_list = [result for result in results if result is not None]

    # Process updates in batches
    batch = db.batch()
    batch_count = 0
    total_updated = 0
    for doc_id, device_verkada_device_type in update_data_list:
        doc_ref = devices_ref.document(doc_id)
        batch.update(doc_ref, {'deviceVerkadaDeviceType': device_verkada_device_type})
        batch_count += 1
        total_updated += 1

        if batch_count >= batch_size:
            try:
                logger.info(f"Committing batch of {batch_count} updates...")
                batch.commit()
                logger.info(f"Batch committed successfully.")
            except Exception as e:
                logger.error(f"Error committing batch: {e}")
            # Start a new batch
            batch = db.batch()
            batch_count = 0

    # Commit any remaining updates in the last batch
    if batch_count > 0:
        try:
            logger.info(f"Committing final batch of {batch_count} updates...")
            batch.commit()
            logger.info(f"Final batch committed successfully.")
        except Exception as e:
            logger.error(f"Error committing final batch: {e}")

    logger.info(f"Finished updating Verkada device types. Attempted to update {total_updated} devices.")
