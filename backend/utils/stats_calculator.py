from typing import Dict, Any, List



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
