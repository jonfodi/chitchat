from openai import OpenAI
import pandas as pd
client = OpenAI(api_key="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")

file = client.files.create(
    file=open("../flight_data_exports/timeseries_AHR2_20250801_155049.csv", "rb"),
    purpose="assistants"
)

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