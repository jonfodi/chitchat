from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="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", 
    
)

print("*" * 50)
csv_agent = create_csv_agent(llm, 
    "../flight_data_exports/timeseries_AHR2_20250801_155049.csv",
    verbose=True, 
    allow_dangerous_code=True, 
    handle_parsing_errors=True)


print("%" *50)
response = csv_agent.invoke("Summarize this flight data. Format your response with 'Final Answer:' followed by the data.", handle_parsing_errors=True)
print("=" * 50)
print(response)