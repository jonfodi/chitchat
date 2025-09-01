import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from utils.utils import create_output_dir


def write_csv(filename: str, msg_data: Dict[str, Any]):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
    
        writer.writerow(msg_data.keys())
    
        for i in range(time_length):
            row = [msg_data[field][i] for field in msg_data.keys()]
            writer.writerow(row)

def create_csv_for_message_type(msg_type: str, msg_data: Dict[str, Any], output_dir: Path, timestamp: str) -> str:
    """Export timeseries data for a message type to CSV."""
    filename = output_dir / f"timeseries_{msg_type.replace('[', '_').replace(']', '')}_{timestamp}.csv"
    
    # Get all fields with same length as time data
    time_length = len(msg_data['time_boot_ms'])
    valid_fields = [
        field_name for field_name, field_data in msg_data.items()
        if isinstance(field_data, list) and len(field_data) == time_length
    ]

    write_csv(filename, msg_data)
    

    
    return str(filename)

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


def process_flight_data(messages: Dict[str, Any]) -> Dict[str, Any]:
    """Process all valid messages and return metadata with CSV file paths."""
    
    output_dir = create_output_dir()

    
    for msg_type, msg_data in messages.items():
        breakpoint()
        if not is_valid_message_type(msg_type) or not is_valid_message_data(msg_data):
            print(f"Skipping message type '{msg_type}")
            continue
        
        # Export timeseries to CSV
        csv_filename = create_csv_for_message_type(msg_type, msg_data, output_dir, timestamp)

        # Create metadata (without timeseries)
        processed_data["message_types"][msg_type] = create_message_metadata(msg_type, msg_data)
        
        print(f"Processed {msg_type}: {len(msg_data['time_boot_ms'])} data points -> {csv_filename}")
    
    return processed_data
