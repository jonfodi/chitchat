from google import genai
from google.genai import types
import pandas as pd


# Initialize client
api_key = "AIzaSyDc_YFO9MiE_e69LVkCd_zS-xmTGog-fos"
client = genai.Client(api_key=api_key)

# Simple in-memory storage (replace with database later)
conversations = {}



def call_llm(chat_id: str, messages: list):
    # Get system instruction from conversation data structure
    system_instruction = conversations[chat_id]["system_instruction"]
    
    # Create contents from messages
    contents = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        ),
        contents=contents
    )
    
    return response.text



def create_conversation(chat_id: str):
    # Load CSV data
    df = pd.read_csv('../flight_data_exports/timeseries_AHR2_20250801_155049.csv')
    csv_content = df.to_string()
    
    # Create enhanced system instruction with CSV data
    system_instruction = f"""You are an expert flight engineer specializing in telemetry data analysis.
    
    You have access to the following telemetry data that you should use to answer questions:

    {csv_content}
    """

    # Initialize conversation with enhanced system instruction
    conversations[chat_id] = {
        "messages": [],
        "system_instruction": system_instruction
    }
    


# POST ENDPOINT FUNCTION
def chat_with_llm(chat_id: str, user_message: str):
    """Main chat function"""
    try:
        # Create new conversation if it doesn't exist
        if chat_id not in conversations:
            create_conversation(chat_id)
        
        # Add user message to conversation history
        conversations[chat_id]["messages"].append({
            "role": "user",
            "content": user_message
        })
        
        # Make LLM call with full conversation history
        response = call_llm(chat_id, conversations[chat_id]["messages"])
        
        # Add assistant response to conversation history
        conversations[chat_id]["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return response
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return "Sorry, something went wrong."

if __name__ == "__main__":
    
    chat_id = "flight_analysis_001"
    chat_with_llm(chat_id, "What was the maximum altitude reached in this flight?")
    print(conversations[chat_id]["messages"])

    chat_with_llm(chat_id, "Any anomalies with the flight data?")
    print(conversations[chat_id]["messages"])
