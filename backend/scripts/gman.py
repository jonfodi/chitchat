from google import genai
import pandas as pd

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="")
df = pd.read_csv('../flight_data_exports/timeseries_AHR2_20250801_155049.csv')
csv_content = df.to_string()

prompt = """You are an expert flight engineer. Analyze the attached CSV telemetry data and categorize the type of flight.

**Determine:**
* **Flight Type**: Manned aircraft, drone/UAV, helicopter, experimental vehicle, or other
* **Vehicle Category**: Commercial, military, consumer, research, etc.
* **Mission Type**: Transportation, surveillance, recreation, testing, etc.

Here is the telemetry data:
"""

response = client.models.generate_content(
    model="gemini-2.5-flash", contents=f"{prompt}\n\n{csv_content}"
)
print(response.text)