def check_verkada_device_type(device_serial_number: str) -> str:
    """
    Check the type of a Verkada device based on its serial number.

    Args:
        device_serial_number (str): The serial number of the device.

    Returns:
        str: The type of the device.
    """
    # Check if the serial number is long enough
    if len(device_serial_number) < 3:
        return 'Unknown'

    camera_prefixes = [
        "ALP", "EGW", "A3P", "QF6", "DFL", "KT7", "DAL", "4KL", "KDT", "TQL", "RK7", "6F7", "GJ7", "YC3", "CQQ", "TTR",
        "TAC", "LXD", "49K", "3PJ", "PD7", "DRH", "GAK", "AHM", "W9P", "MTF", "QJT", "6JN", "NMC", "HFJ", "KXR", "PJF",
        "9YK", "PEG", "4HA", "7JE", "E9W", "KL9", "37T", "H9K", "D7L", "DXE", "HWH", "PDG", "YKC", "KWF", "3TE", "EXP",
        "D7M", "CPH", "3CF", "9PA", "7GN", "73C", "FTW", "CAM", "FCX", "DGA", "AC7", "TEP", "RNT", "HKA", "CRJ", "RLP",
        "9CR", "Y9P", "N46", "QK4", "3EW", "LAQ", "JM4", "KEQ", "7J4", "DE7", "NH9", "KC7", "GFR", "HDE", "N9D", "4XN",
        "D4C", "G37", "GEX", "JEH", "TEH", "XPD", "6LH", "GTY", "KDY", "QN4", "CG9", "9DT", "CPE", "HTR", "WH3", "3NY",
        "YMG", "7GE", "6T4", "D7X", "P76", "EJD", "H6T", "CKK", "XYA", "LQW", "T4Q", "FXG", "RND", "JR3", "LR9", "RFD",
        "W9K", "HEF", "J97", "PMF", "FJH", "PK4"
    ]
    access_controller_prefixes = ["R7M","M7R","MPH","NEX","DAM","DXM"]
    input_output_board_prefixes = ["6GA"]
    envirmental_sensor_prefixes = ["6CC","PJE","NR6","T7L","NCG","9JX","JQ9","CHQ"]
    intercom_prefixes = ["CHA","DDD","CRY","MKE","LKE","KEN","YDA","DKC","KYL"]
    gateway_prefixes = ["PR4","LPT","NAR"]
    command_connector_prefixes = ["WEY","A9G","MYW","7WP","7CG","EWL","CFA","CFC","CFD"]
    viewing_station_prefixes = ["DRJ"]
    deskstation_prefixes = ["DEK"]
    speaker_prefixes = ["ANN"]
    hub_prefixes = ["DQ6"]
    panel_prefixes = ["DQ4"]
    keypad_prefixes = ["KP4", "KP9", "KP7", "KP6"]
    door_contact_prefixes = ["DC3"]
    glass_break_prefixes = ["DG3"]
    motion_sensor_prefixes = ["DM3"]
    panic_button_prefixes = ["DP3"]
    water_sensor_prefixes = ["DW3"]
    wireless_relay_prefixes = ["DR3"]
    siren_strobe_prefixes = ["FDT"]
    new_panel_prefixes = ["XC4"]
    alarm_expander_prefixes = ["39Q"]


    prefix = device_serial_number[:3]

    if prefix in camera_prefixes:
        return 'Camera'
    elif prefix in access_controller_prefixes:
        return 'Access Controller'
    elif prefix in input_output_board_prefixes:
        return 'Input Output Board'
    elif prefix in envirmental_sensor_prefixes:
        return 'Environmental Sensor'
    elif prefix in intercom_prefixes:
        return 'Intercom'
    elif prefix in gateway_prefixes:
        return 'Gateway'
    elif prefix in command_connector_prefixes:
        return 'Command Connector'
    elif prefix in viewing_station_prefixes:
        return 'Viewing Station'
    elif prefix in deskstation_prefixes:
        return 'Desk Station'
    elif prefix in speaker_prefixes:
        return 'Speaker'
    elif prefix in hub_prefixes or prefix in panel_prefixes:
        return 'Classic Alarm Hub Device'
    elif prefix in keypad_prefixes:
        return 'Classic Alarm Keypad'
    elif prefix in door_contact_prefixes:
        return 'Classic Alarm Door Contact Sensor'
    elif prefix in glass_break_prefixes:
        return 'Classic Alarm Glass Break Sensor'
    elif prefix in motion_sensor_prefixes:
        return 'Classic Alarm Motion Sensor'
    elif prefix in panic_button_prefixes:
        return 'Classic Alarm Panic Button'
    elif prefix in water_sensor_prefixes:
        return 'Classic Alarm Water Sensor'
    elif prefix in wireless_relay_prefixes:
        return 'Classic Alarm Wireless Relay'
    elif prefix in siren_strobe_prefixes:
        return 'Siren Strobe'
    elif prefix in new_panel_prefixes:
        return 'BP52 Panel'
    elif prefix in alarm_expander_prefixes:
        return 'Alarm Expander'
    else:
        return 'Unknown'