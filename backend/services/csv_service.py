import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from utils.utils import create_output_dir




def write_csv(filename: str, msg_data: Dict[str, Any]):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
    
        writer.writerow(msg_data.keys())
    
        time_length = len(msg_data['time_boot_ms'])
        for i in range(time_length):
            row = [msg_data[field][i] for field in msg_data.keys()]
            writer.writerow(row)

def create_csvs(messages: Dict[str, Any]) -> Dict[str, Any]:
    """Process all valid messages and return metadata with CSV file paths."""
    
    output_dir = create_output_dir()

    for msg_type, msg_data in messages.items():
        
        csv_filename = output_dir / f"timeseries_{msg_type.replace('[', '_').replace(']', '')}.csv"

        write_csv(csv_filename, msg_data)

        print(f"Processed {msg_type}: {len(msg_data['time_boot_ms'])} data points -> {csv_filename}")
    
    return True
