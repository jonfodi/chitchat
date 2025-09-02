import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from utils.utils import create_output_dir




def write_csv(filename: str, telemetry_record  : Dict[str, Any]):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(telemetry_record.keys())
        time_length = len(telemetry_record['time_boot_ms'])
        for i in range(time_length):
            row = [telemetry_record[field][i] for field in telemetry_record.keys()]
            writer.writerow(row)

def create_csvs(time_series_data: Dict[str, Any]) -> Dict[str, Any]:    
    output_dir = create_output_dir()
    for data_type, telemetry_records in time_series_data.items():
        csv_filename = output_dir / f"timeseries_{data_type.replace('[', '_').replace(']', '')}.csv"
        write_csv(csv_filename, telemetry_records)
        print(f"Processed {data_type}: {len(telemetry_records['time_boot_ms'])} data points -> {csv_filename}")
    
    return True
