# main.py - FastAPI backend to receive flight data
import csv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import FlightDataRequest
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

app = FastAPI(title="Flight Data Processor", version="1.0.0")

# Enable CORS for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vue app's URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
ALLOWED_MESSAGE_TYPES = {
    'ATT', 'AHR2', 'GPS[0]', 'POS', 
    'XKQ[0]', 'XKQ[1]', 'XKQ[2]', 
    'XKF4[0]', 'XKF4[1]', 'XKF4[2]'
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

ALLOWED_MESSAGE_TYPES = {
    'ATT', 'AHR2', 'GPS[0]', 'POS', 
    'XKQ[0]', 'XKQ[1]', 'XKQ[2]', 
    'XKF4[0]', 'XKF4[1]', 'XKF4[2]'
}

def has_control_pairs(msg_data: Dict[str, Any]) -> bool:
    """Check if message has desired/actual control pairs."""
    control_pairs = [
        ("Roll", "DesRoll"),
        ("Pitch", "DesPitch"), 
        ("Yaw", "DesYaw")
    ]
    
    return any(
        actual in msg_data and desired in msg_data
        for actual, desired in control_pairs
    )

def assess_control_quality(avg_rms: float, avg_correlation: float) -> str:
    """Assess overall control quality based on RMS error and correlation."""
    if avg_rms < 0.01 and avg_correlation > 0.95:
        return "EXCELLENT"
    elif avg_rms < 0.05 and avg_correlation > 0.85:
        return "GOOD"
    elif avg_rms < 0.1 and avg_correlation > 0.7:
        return "FAIR"
    else:
        return "POOR"

def calculate_rate_of_change_stats(values: List[float], time_ms: List[float]) -> Dict[str, float]:
    """Calculate rate of change statistics for stability assessment."""
    if len(values) < 2 or len(time_ms) < 2 or len(values) != len(time_ms):
        return {}
    
    # Calculate rates of change
    rates = []
    for i in range(1, len(values)):
        dt = (time_ms[i] - time_ms[i-1]) / 1000.0  # Convert ms to seconds
        if dt > 0:
            rate = (values[i] - values[i-1]) / dt
            rates.append(rate)
    
    if not rates:
        return {}
    
    # Calculate standard deviation of rates
    mean_rate = sum(rates) / len(rates)
    variance = sum((rate - mean_rate) ** 2 for rate in rates) / len(rates)
    std_dev_rate = variance ** 0.5
    
    return {
        "std_dev_rate": round(std_dev_rate, 6)
    }

def calculate_control_error_stats(desired_values: List[float], actual_values: List[float]) -> Dict[str, float]:
    """Calculate control error RMS and correlation coefficient."""
    if not desired_values or not actual_values or len(desired_values) != len(actual_values):
        return {}
    
    # Calculate errors
    errors = [actual - desired for actual, desired in zip(actual_values, desired_values)]
    
    # RMS Error
    squared_errors = [error ** 2 for error in errors]
    rms_error = (sum(squared_errors) / len(squared_errors)) ** 0.5
    
    # Correlation coefficient
    n = len(desired_values)
    mean_desired = sum(desired_values) / n
    mean_actual = sum(actual_values) / n
    
    numerator = sum((d - mean_desired) * (a - mean_actual) 
                   for d, a in zip(desired_values, actual_values))
    
    sum_sq_desired = sum((d - mean_desired) ** 2 for d in desired_values)
    sum_sq_actual = sum((a - mean_actual) ** 2 for a in actual_values)
    
    denominator = (sum_sq_desired * sum_sq_actual) ** 0.5
    correlation = numerator / denominator if denominator != 0 else 0.0
    
    return {
        "rms_error": round(rms_error, 6),
        "correlation": round(correlation, 6)
    }

def analyze_gps_performance(msg_data: Dict[str, Any], time_data: List[float]) -> Dict[str, Any]:
    """Analyze GPS performance metrics."""
    if not has_gps_fields(msg_data):
        return {}
    
    performance = {}
    
    # Satellite performance
    if "SV" in msg_data:
        sv_data = [float(x) for x in msg_data["SV"] if isinstance(x, (int, float))]
        if sv_data:
            good_fix_count = sum(1 for sv in sv_data if sv >= 4)
            good_fix_ratio = good_fix_count / len(sv_data)
            
            performance["satellite_performance"] = {
                "good_fix_ratio": round(good_fix_ratio, 6),
                "avg_satellites": round(sum(sv_data) / len(sv_data), 6)
            }
    
    # Accuracy performance
    if "HDop" in msg_data:
        hdop_data = [float(x) for x in msg_data["HDop"] if isinstance(x, (int, float))]
        if hdop_data:
            good_accuracy_count = sum(1 for hdop in hdop_data if hdop <= 5.0)
            good_accuracy_ratio = good_accuracy_count / len(hdop_data)
            
            performance["accuracy_performance"] = {
                "good_accuracy_ratio": round(good_accuracy_ratio, 6),
                "avg_hdop": round(sum(hdop_data) / len(hdop_data), 6)
            }
    
    return performance

def analyze_control_performance(msg_data: Dict[str, Any], time_data: List[float]) -> Dict[str, Any]:
    """Analyze control performance for messages with control pairs."""
    if not has_control_pairs(msg_data):
        return {}
    
    control_pairs = [
        ("Roll", "DesRoll"),
        ("Pitch", "DesPitch"),
        ("Yaw", "DesYaw")
    ]
    
    control_analysis = {}
    rms_values = []
    correlation_values = []
    
    for actual_field, desired_field in control_pairs:
        if actual_field in msg_data and desired_field in msg_data:
            actual_values = [float(x) for x in msg_data[actual_field]]
            desired_values = [float(x) for x in msg_data[desired_field]]
            
            # Control error analysis
            error_stats = calculate_control_error_stats(desired_values, actual_values)
            
            # Rate of change analysis
            rate_stats = calculate_rate_of_change_stats(actual_values, time_data)
            
            # Actual value stability
            actual_stats = calculate_field_stats(actual_values)
            
            control_analysis[actual_field.lower()] = {
                "control_errors": error_stats,
                "rate_statistics": rate_stats,
                "stability": {
                    "actual_std_dev": actual_stats.get("std_dev", 0.0)
                }
            }
            
            # Collect for overall assessment
            if error_stats:
                rms_values.append(error_stats["rms_error"])
                correlation_values.append(error_stats["correlation"])
    
    # Overall assessment
    if rms_values and correlation_values:
        avg_rms = sum(rms_values) / len(rms_values)
        avg_correlation = sum(correlation_values) / len(correlation_values)
        control_quality = assess_control_quality(avg_rms, avg_correlation)
        
        control_analysis["overall_assessment"] = {
            "control_quality": control_quality,
            "avg_rms_error": round(avg_rms, 6),
            "avg_correlation": round(avg_correlation, 6)
        }
    
    return control_analysis

def calculate_field_stats(data: List[float]) -> Dict[str, float]:
    """Calculate statistics for a numeric field."""
    if not data:
        return {}
    
    min_val = min(data)
    max_val = max(data)
    mean_val = sum(data) / len(data)
    variance = sum((x - mean_val) ** 2 for x in data) / len(data)
    std_dev = variance ** 0.5
    
    return {
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "mean": round(mean_val, 6),
        "std_dev": round(std_dev, 6)
    }

def is_valid_message(msg_type: str, msg_data: Any) -> bool:
    """Check if message type and data are valid for processing."""
    return (
        msg_type in ALLOWED_MESSAGE_TYPES and
        isinstance(msg_data, dict) and
        'time_boot_ms' in msg_data and
        isinstance(msg_data['time_boot_ms'], list) and
        len(msg_data['time_boot_ms']) > 0
    )

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
    
    # Add control performance analysis for ATT messages
    if msg_type == "ATT":
        control_performance = analyze_control_performance(msg_data, time_data)
        if control_performance:
            metadata["control_performance"] = control_performance
    
    # Add GPS performance analysis for GPS messages
    if msg_type == "GPS[0]":
        gps_performance = analyze_gps_performance(msg_data, time_data)
        if gps_performance:
            metadata["gps_performance"] = gps_performance
    
    return metadata


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

def classify_question_intent(user_question: str):
    prompt = f"""
    You are a helpful assistant that classifies the intent of a user's question.
    The user's question is: {user_question}
    The intent is:
    """
    response = claude.generate_response(prompt)
    return response

def ask_investiative_question(user_question: str, csv_file_path: str):
    prompt = f"""
    You are a helpful assistant that asks an investigative question to the user.
    The user's question is: {user_question}
    The question is:
    """
    response = claude.generate_response(prompt)
    return response

def ask_specific_question(user_question: str, json_file_path: str):
    prompt = f"""
    You are a helpful assistant that asks a specific question to the user.
    The user's question is: {user_question}
    The question is:

    """
    response = claude.generate_response(prompt)
    return response

def generate_response(user_question: str):
    pass
@app.get("/api/chat")
async def chat(user_question: str):
    #initial LLM call to classify the question
    try:
        reponse_message = generate_response(user_question)
        return {"message": user_question, "response": reponse_message}
    except Exception as e:
        return {"message": user_question, "error": f"Error: {e}"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Flight data processor is running"}

@app.get("/")
async def root():
    return {"message": "Flight Data Processor API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)