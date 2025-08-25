from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,    
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