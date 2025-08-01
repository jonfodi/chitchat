# main.py - FastAPI backend to receive flight data
from backend.services.data_processor import export_metadata_to_json, process_messages
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import json
import csv
from datetime import datetime
from pathlib import Path
from models import FlightDataRequest

app = FastAPI(title="Flight Data Processor", version="1.0.0")

# Enable CORS for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vue app's URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Constants
ALLOWED_MESSAGE_TYPES = {
    'ATT', 'AHR2', 'GPS[0]', 'POS', 
    'XKQ[0]', 'XKQ[1]', 'XKQ[2]', 
    'XKF4[0]', 'XKF4[1]', 'XKF4[2]'
}

FALLBACK_FIELD_INFO = {
    "time_boot_ms": {"description": "Timestamp in milliseconds since system boot", "units": "ms"},
    "Roll": {"description": "Roll angle in radians", "units": "rad"},
    "Pitch": {"description": "Pitch angle in radians", "units": "rad"},
    "Yaw": {"description": "Yaw angle in radians", "units": "rad"},
    "DesRoll": {"description": "Desired roll angle in radians", "units": "rad"},
    "DesPitch": {"description": "Desired pitch angle in radians", "units": "rad"},
    "DesYaw": {"description": "Desired yaw angle in radians", "units": "rad"},
    "Alt": {"description": "Altitude relative to home position", "units": "m"},
    "Lat": {"description": "Latitude coordinate", "units": "deg"},
    "Lng": {"description": "Longitude coordinate", "units": "deg"},
    "Q1": {"description": "Quaternion component 1 (w)", "units": "unitless"},
    "Q2": {"description": "Quaternion component 2 (x)", "units": "unitless"},
    "Q3": {"description": "Quaternion component 3 (y)", "units": "unitless"},
    "Q4": {"description": "Quaternion component 4 (z)", "units": "unitless"},
    "SV": {"description": "Number of satellites visible", "units": "count"},
    "HDop": {"description": "Horizontal dilution of precision", "units": "unitless"},
    "VDop": {"description": "Vertical dilution of precision", "units": "unitless"}
}

MESSAGE_DESCRIPTIONS = {
    "AHR2": "Attitude and heading reference data containing roll, pitch, yaw angles, altitude, position coordinates, and quaternion values for aircraft orientation",
    "ATT": "Attitude data containing roll, pitch, and yaw angles",
    "GPS[0]": "Global positioning system data including latitude, longitude, altitude, and accuracy metrics from GPS sensor 0",
    "POS": "Position data containing coordinates and altitude",
    "XKQ[0]": "Extended Kalman Filter quaternion data from instance 0",
    "XKQ[1]": "Extended Kalman Filter quaternion data from instance 1",
    "XKQ[2]": "Extended Kalman Filter quaternion data from instance 2",
    "XKF4[0]": "Extended Kalman Filter state data from instance 0",
    "XKF4[1]": "Extended Kalman Filter state data from instance 1",
    "XKF4[2]": "Extended Kalman Filter state data from instance 2"
}


def get_message_description(msg_type: str) -> str:
    """Get description for a message type."""
    return MESSAGE_DESCRIPTIONS.get(msg_type, f"MAVLink message type {msg_type} telemetry data")


@app.post("/api/process-flight-data")
async def process_flight_data(data: FlightDataRequest):
    """Receive flight data from Vue frontend and export to CSV and JSON."""
    try:
        print("=" * 50)
        print("PROCESSING FLIGHT DATA")
        print("=" * 50)
        
        messages = data.messages
        print(f"Received {len(messages)} message types: {list(messages.keys())}")
        
        # Process messages
        processed_data = process_messages(messages)
        
        # Export metadata to JSON
        json_filename = export_metadata_to_json(processed_data)
        
        # Log results
        valid_types = list(processed_data["message_types"].keys())
        print(f"✅ Successfully processed {len(valid_types)} message types: {valid_types}")
        print(f"📄 Metadata exported to: {json_filename}")
        print(f"📊 CSV files created: {len(processed_data['csv_files'])}")
        
        return {
            "status": "success",
            "message": "Flight data processed successfully",
            "flight_id": processed_data["flight_id"],
            "message_types_processed": valid_types,
            "total_message_types": len(valid_types),
            "csv_files": processed_data["csv_files"],
            "metadata_file": json_filename
        }
        
    except Exception as e:
        print(f"❌ ERROR processing flight data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Flight data processor is running"}

@app.get("/")
async def root():
    return {"message": "Flight Data Processor API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)