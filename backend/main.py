# main.py - FastAPI backend to receive flight data
from services.data_processor import process_flight_data
import uvicorn
import csv
from graph import Graph

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import FlightDataRequest, ChatRequest
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

from collections import defaultdict
from datetime import datetime


app = FastAPI(title="Flight Data Processor", version="1.0.0")
counter = 0
# Enable CORS for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vue app's URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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

FIELD_INFO = {
    # Time field (common across all messages)
    "time_boot_ms": {"description": "Timestamp in milliseconds since system boot", "units": "ms"},
    "TimeUS": {"description": "Time since system startup", "units": "μs"},
    
    # ATT message fields
    "Roll": {"description": "achieved vehicle roll", "units": "deg"},
    "Pitch": {"description": "achieved vehicle pitch", "units": "deg"},
    "Yaw": {"description": "achieved vehicle yaw", "units": "degheading"},
    "DesRoll": {"description": "vehicle desired roll", "units": "deg"},
    "DesPitch": {"description": "vehicle desired pitch", "units": "deg"},
    "DesYaw": {"description": "vehicle desired yaw", "units": "degheading"},
    "AEKF": {"description": "active EKF type", "units": "unitless"},
    
    # AHR2 message fields
    "Alt": {"description": "Estimated altitude", "units": "m"},
    "Lat": {"description": "Estimated latitude", "units": "deglatitude"},
    "Lng": {"description": "Estimated longitude", "units": "deglongitude"},
    "Q1": {"description": "Estimated attitude quaternion component 1", "units": "unitless"},
    "Q2": {"description": "Estimated attitude quaternion component 2", "units": "unitless"},
    "Q3": {"description": "Estimated attitude quaternion component 3", "units": "unitless"},
    "Q4": {"description": "Estimated attitude quaternion component 4", "units": "unitless"},
    
    # GPS message fields
    "Status": {"description": "GPS Fix type; 2D fix, 3D fix etc.", "units": "enum"},
    "GMS": {"description": "milliseconds since start of GPS Week", "units": "ms"},
    "GWk": {"description": "weeks since 5 Jan 1980", "units": "weeks"},
    "NSats": {"description": "number of satellites visible", "units": "satellites"},
    "HDop": {"description": "horizontal dilution of precision", "units": "unitless"},
    "VDop": {"description": "vertical dilution of precision", "units": "unitless"},
    "Spd": {"description": "ground speed", "units": "m/s"},
    "GCrs": {"description": "ground course", "units": "degheading"},
    "VZ": {"description": "vertical speed", "units": "m/s"},
    "U": {"description": "boolean value indicating whether this GPS is in use", "units": "boolean"},
    
    # POS message fields
    "RelHomeAlt": {"description": "Canonical vehicle altitude relative to home", "units": "m"},
    "RelOriginAlt": {"description": "Canonical vehicle altitude relative to navigation origin", "units": "m"},
    
    # XKQ message fields (EKF3 quaternion)
    # Q1-Q4 already defined above
    
    # XKF4 message fields (EKF3 variances)
    "C": {"description": "EKF3 core this data is for", "units": "instance"},
    "SV": {"description": "Square root of the velocity variance", "units": "unitless"},
    "SP": {"description": "Square root of the position variance", "units": "unitless"},
    "SH": {"description": "Square root of the height variance", "units": "unitless"},
    "SM": {"description": "Magnetic field variance", "units": "unitless"},
    "SVT": {"description": "Square root of the total airspeed variance", "units": "unitless"},
    "errRP": {"description": "Filtered error in roll/pitch estimate", "units": "unitless"},
    "OFN": {"description": "Most recent position reset (North component)", "units": "m"},
    "OFE": {"description": "Most recent position reset (East component)", "units": "m"},
    "FS": {"description": "Filter fault status", "units": "unitless"},
    "TS": {"description": "Filter timeout status bitmask", "units": "bitmask"},
    "SS": {"description": "Filter solution status", "units": "bitmask"},
    "GPS": {"description": "Filter GPS status", "units": "unitless"},
    "PI": {"description": "Primary core index", "units": "unitless"},
    
    # Common fields that might appear in various messages
    "I": {"description": "instance number", "units": "instance"},
    "Instance": {"description": "instance number", "units": "instance"},
}

conversations = defaultdict(lambda: {
    "messages": [],
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
})

data = defaultdict(lambda: {
    "timestamp": [],
    "data": {}
})

def get_or_create_conversation(conversation_id: str):
    # Safe fetch - returns None if doesn't exist
    conversation = conversations.get(conversation_id)
    if conversation is None:
        # Create new conversation explicitly
        conversation = conversations[conversation_id]  
    return conversation

def add_message_to_conversation(conversation: Dict[str, Any], user_query: str, role: str):

        # Add user message
    conversation["messages"].append({
        "role": role, 
        "content": user_query
    })
    
    conversation["updated_at"] = datetime.now().isoformat()
    return conversation

@app.post("/api/chat")
async def chat(request: ChatRequest):

    # retriever conversation ID from request 
    conversation_id = request.conversation_id
    # retrieve user query from request 
    user_query = request.user_query

    # retrieve conversation from DB 
    conversation = get_or_create_conversation(conversation_id)
    
    # add user message to conversation
    conversation = add_message_to_conversation(conversation, user_query, "user")

    data = get_or_cre

    
    # rename to something more in line with use case
    graph = Graph(
        conversation = conversation,
        data = {}
    )

    # run agent
    final_state = await graph.run()
    breakpoint()
    return final_state

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

def export_metadata_to_json(processed_data: Dict[str, Any]) -> str:
    """Export metadata (without timeseries) to JSON file."""
    output_dir = Path("flight_data_exports")
    filename = output_dir / f"flight_metadata_{processed_data['generated_timestamp']}.json"
    
    with open(filename, 'w') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    return str(filename)

def has_gps_fields(msg_data: Dict[str, Any]) -> bool:
    """Check if message has GPS performance fields."""
    gps_fields = ["SV", "HDop", "VDop"]
    return any(field in msg_data for field in gps_fields)

def get_numeric_fields(msg_data: Dict[str, Any]) -> List[str]:
    """Get all fields that are numeric arrays with same length as time data."""
    time_length = len(msg_data['time_boot_ms'])
    return [
        field_name for field_name, field_data in msg_data.items()
        if (isinstance(field_data, list) and 
            len(field_data) == time_length and
            all(isinstance(x, (int, float)) and x is not None for x in field_data))
    ]

def get_message_description(msg_type: str) -> str:
    """Get description for a message type."""
    return MESSAGE_DESCRIPTIONS.get(msg_type, f"MAVLink message type {msg_type} telemetry data")

def get_field_info(field_name: str) -> Dict[str, str]:
    """Get description and units for a field."""
    return FIELD_INFO.get(field_name, {
        "description": f"Data field {field_name}",
        "units": "unknown"
    })


@app.post("/api/process-flight-data")
async def process_flight_data(request: FlightDataRequest):
   
    print("=" * 50)
    print("PROCESSING FLIGHT DATA")
    print("=" * 50)

    try:
        flight_data = request.messages 
        # data_structure = {
        #     "message_type": { CMD, AHR2, etc.
        #         "field_name": [values], time_boot_ms,  Yaw, Pitch, etc. 
        #     }
        # }

        breakpoint()
        # Process messages
        processed_data = process_flight_data(flight_data)
        # Export metadata to JSON
        json_filename = export_metadata_to_json(processed_data)
        return True
        
    except Exception as e:
        print(f"ERROR processing flight data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Flight data processor is running"}

@app.get("/")
async def root():
    return {"message": "Flight Data Processor API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)