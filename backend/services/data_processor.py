from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from models import ALLOWED_MESSAGE_TYPES, is_valid_message, export_timeseries_to_csv, create_message_metadata
import json


def process_messages(messages: Dict[str, Any]) -> Dict[str, Any]:
    """Process all valid messages and return metadata with CSV file paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("flight_data_exports")
    output_dir.mkdir(exist_ok=True)
    
    processed_data = {
        "flight_id": f"flight_{timestamp}",
        "generated_timestamp": timestamp,
        "message_types": {},
        "csv_files": []
    }
    
    for msg_type, msg_data in messages.items():
        if not is_valid_message(msg_type, msg_data):
            if msg_type in ALLOWED_MESSAGE_TYPES:
                print(f"⚠️  Skipping message type '{msg_type}' - invalid structure")
            continue
        
        # Export timeseries to CSV
        csv_filename = export_timeseries_to_csv(msg_type, msg_data, output_dir, timestamp)
        processed_data["csv_files"].append(csv_filename)
        
        # Create metadata (without timeseries)
        processed_data["message_types"][msg_type] = create_message_metadata(msg_type, msg_data)
        
        print(f"✅ Processed {msg_type}: {len(msg_data['time_boot_ms'])} data points -> {csv_filename}")
    
    return processed_data

def export_metadata_to_json(processed_data: Dict[str, Any]) -> str:
    """Export metadata (without timeseries) to JSON file."""
    output_dir = Path("flight_data_exports")
    filename = output_dir / f"flight_metadata_{processed_data['generated_timestamp']}.json"
    
    with open(filename, 'w') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    return str(filename)