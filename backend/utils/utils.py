from pathlib import Path
from datetime import datetime

def create_output_dir():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("flight_data_exports")
    output_dir.mkdir(exist_ok=True)
    return output_dir