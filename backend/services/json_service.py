from typing import Dict, Any
from utils.utils import get_numeric_fields, get_field_info, get_message_description, calculate_field_stats

def create_message_metadata(msg_type: str, msg_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create metadata for a message type without timeseries data."""
    time_data = msg_data['time_boot_ms']
    data_length = len(time_data)
    numeric_fields = get_numeric_fields(msg_data)
    
    # Calculate field statistics
    fields_info = {}
    for field_name in numeric_fields:
        if field_name != 'time_boot_ms':  # Skip time field for stats
            field_info = get_field_info(field_name)
            stats = calculate_field_stats([float(x) for x in msg_data[field_name]])
            
            fields_info[field_name] = {
                "description": field_info["description"],
                "units": field_info["units"],
                **stats
            }
    
    # Base metadata structure
    metadata = {
        "message_type": msg_type,
        "description": get_message_description(msg_type),
        "data_points": data_length,
        "time_range": {
            "start_ms": float(time_data[0]),
            "end_ms": float(time_data[-1]),
            "duration_ms": float(time_data[-1] - time_data[0])
        },
        "fields": fields_info
    }
    
    return metadata