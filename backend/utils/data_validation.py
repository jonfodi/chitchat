def has_gps_fields(msg_data: Dict[str, Any]) -> bool:
    """Check if message has GPS performance fields."""
    gps_fields = ["SV", "HDop", "VDop"]
    return any(field in msg_data for field in gps_fields)

def is_valid_message(msg_type: str, msg_data: Any) -> bool:
    """Check if message type and data are valid for processing."""
    return (
        msg_type in ALLOWED_MESSAGE_TYPES and
        isinstance(msg_data, dict) and
        'time_boot_ms' in msg_data and
        isinstance(msg_data['time_boot_ms'], list) and
        len(msg_data['time_boot_ms']) > 0
    )