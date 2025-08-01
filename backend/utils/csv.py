from pathlib import Path
from typing import Dict, Any
import csv


def export_timeseries_to_csv(msg_type: str, msg_data: Dict[str, Any], output_dir: Path, timestamp: str) -> str:
    """Export timeseries data for a message type to CSV."""
    filename = output_dir / f"timeseries_{msg_type.replace('[', '_').replace(']', '')}_{timestamp}.csv"
    
    # Get all fields with same length as time data
    time_length = len(msg_data['time_boot_ms'])
    valid_fields = [
        field_name for field_name, field_data in msg_data.items()
        if isinstance(field_data, list) and len(field_data) == time_length
    ]
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(valid_fields)
        
        # Write data rows
        for i in range(time_length):
            row = [msg_data[field][i] for field in valid_fields]
            writer.writerow(row)
    
    return str(filename)