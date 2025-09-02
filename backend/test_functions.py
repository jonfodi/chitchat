import sys
import os
sys.path.append(os.path.dirname(__file__))  # Add backend to path

from main import save_csvs


SAMPLE_TIME_SERIES_DATA = {
    "CMD": {
        'time_boot_ms': [5258.467],
        'CTot': [1],
        'CNum': [0],
        'CId': [16],
        'Prm1': [0],
        'Prm2': [0],
        'Prm3': [0],
        'Prm4': [0],
        'Lat': [0],
        'Lng': [0],
        'Alt': [0],
        'Frame': [0]
    },
    "ATT": {
        'time_boot_ms': [5258.467],
        'DesRoll': [0.1],
        'Roll': [0.05],
        'DesPitch': [0.2],
        'Pitch': [0.15],
        'DesYaw': [1.57],
        'Yaw': [1.55],
        'ErrRP': [0.02],
        'ErrYaw': [0.02],
        'AEKF': [1]
    }
}

def test_save_csvs():
    print("Testing save_csvs function...")
    
    try:
        result = save_csvs(SAMPLE_TIME_SERIES_DATA)
        print(f"✓ Function executed successfully")
        print(f"✓ Result type: {type(result)}")
        print(f"✓ Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"✗ Error type: {type(e)}")

if __name__ == '__main__':
    test_save_csvs()