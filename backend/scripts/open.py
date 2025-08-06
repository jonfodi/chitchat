from openai import OpenAI
import pandas as pd
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv('../flight_data_exports/timeseries_AHR2_20250801_155049.csv')
csv_content = df.to_string()

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": f"Describe what is in this file:\n{csv_content}"
        }
    ])

print(response.output_text)