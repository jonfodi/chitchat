import pandas as pd
import anthropic

client = anthropic.Anthropic(api_key="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")
print("initialized client")

df = pd.read_csv('../flight_data_exports/timeseries_AHR2_20250801_155049.csv')
csv_content = df.to_string()
print("read csv")
# Send as plain text in the message
response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Here's the CSV data:\n\n{csv_content}\n\nPlease analyze this data."
                }
            ]
        }
    ]
)

print(response.content[0].text)