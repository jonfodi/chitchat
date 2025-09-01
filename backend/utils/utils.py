from pathlib import Path
from datetime import datetime
from typing import Any


ALLOWED_MESSAGE_TYPES = ["AHR2", "ATT", "GPS", "POS"]

def create_output_dir():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("flight_data_exports")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def is_message_type_to_process(msg_type: str) -> bool:
    """Check if message type is valid."""
    return msg_type in ALLOWED_MESSAGE_TYPES

def is_data_time_series(msg_data: Any) -> bool:
    """Check if message data is valid."""
    return (
        isinstance(msg_data, dict) and 
        'time_boot_ms' in msg_data and 
        isinstance(msg_data['time_boot_ms'], list) and 
        len(msg_data['time_boot_ms']) > 0
    )