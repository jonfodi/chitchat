import json
from google import genai
from google.genai import types
import pandas as pd
from openai import OpenAI
import dotenv

dotenv.load_dotenv()
openai_client = OpenAI()


# Initialize client
client = genai.Client()

# Simple in-memory storage (replace with database later)
# should resemble a relational schema 
# conversation is table
# columns will be system instruction, messages, intent
conversations = {}

def call_llm(conversation: dict, user_message: str):
    # Get system instruction from conversation data structure
    messages = conversation["messages"]
    # Create contents from messages
    contents = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    contents = contents + [{"role": "user", "content": user_message}]
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=conversation["system_instruction"]
        ),
        contents=contents
    )
    
    return response.text

def get_csv_content(csv_path: str):
    df = pd.read_csv(csv_path)
    return df.to_string()

def create_conversation(chat_id: str):
    
    system_instruction = """You are an expert flight engineer specializing in telemetry data analysis.
    
    You have access to the following telemetry data that you should use to answer questions:

    """

    # Initialize conversation with enhanced system instruction
    conversations[chat_id] = {
        "messages": [],
        "system_instruction": system_instruction
    }

def get_or_create_conversation(chat_id: str):
    if chat_id not in conversations:
        create_conversation(chat_id)
    return conversations[chat_id]

def add_message_to_conversation(conversation, message: str, role: str) -> dict:
    return {
        **conversation,
        "messages": conversation["messages"] + [{
            "role": role,
            "content": message
        }]
    }

def classify_intent(conversation: dict) -> json:
    # call openAI with system instruction and user message
    print(conversation["messages"][-1]["content"])

    instructions = """
    You are an expert technical evaluator. Your responses MUST be in JSON format.
    You will be given a user question and you need to classify the intent of the question into one of the following formats.
    - direct: question that can be answered with the following data
        - Yaw, pitch, roll, altitude, speed
        - min, max, average for each of these values 
    - investigative: question that requires time series data to answer

    Example of a direct question:
    - What was the maximum altitude reached in this flight?
    - What was the average speed of the flight?
    

    Example of an investigative question:
    - were there any anomalies in the flight data?
    - investigate the GPS failure for the flight
    - describe how well the control system performed
    - describe the flight path 

    Example output:
    {"intent": "direct"}
    """

    response = openai_client.responses.create(
    model="gpt-4.1",
    instructions=instructions,
    input=conversation["messages"][-1]["content"]
    )

    print(response.output_text)
    breakpoint()
    return response.output_text

def create_json_string(json_data_filepath: str) -> str:
    with open(json_data_filepath, "r") as f:
        data = json.load(f)
    json_data = json.dumps(data)
    return json_data

# system instructions should be something high level like 
# you are analyzing flight data. you should answer concisely and enofrce accuracy. 
# then for each query whether its direct or investigative i should add this shit 

def create_direct_question_query(conversation: dict) -> str:
    # create the query that will be used for direct questions 
    # return the query
    json_data = create_json_string("../flight_data_exports/flight_metadata_20250801_155049.json")

    query = f"""
    You are an expert flight engineer. 
    You are given a direct question that can be answered with the following data:

    {json_data}

    Provide a direct and accuracte response. Give the response using the same units provided in the json data.

    Example question: What is the maximum altitude reached in this flight?
    Example response: The maximum altitude reached in this flight was 1000 meters.

    User question: {conversation["messages"][-1]["content"]}

    """
    return query

def create_investigative_question_query(conversation: dict) -> str:
    # create the query that will be used for investigative questions
    # return the query
    csv_content = get_csv_content('../flight_data_exports/timeseries_AHR2_20250801_155049.csv')

    query = f"""
    You are an expert flight engineer. 
    You are given a investigative question that requires time series data to answer. You have the following time series data

    {csv_content}

    Provide a response that is accurate and reflective of the data.

    User question: {conversation["messages"][-1]["content"]}
    """

    return query

def make_llm_call(conversation: dict) -> str:

    response = openai_client.responses.create(
    model="gpt-4.1",
    instruction = conversation["system_instruction"],
    input=conversation["messages"][-1]["query"]
    )

    return response.output_text

# CANT DO THIS YET -  conversation can have many intents - so it needs to be on a message 
def add_intent_to_conversation(conversation: dict, intent: str) -> dict:
    return {
        **conversation,
        "intent": intent
    }

def create_query(conversation: dict, intent: json) -> str:
    # create the query based on the intent
    # return the query
    # parse intent dict {"intent": "direct"}
    intent_type = intent.get("intent")
     
    if intent_type == "direct":
        return create_direct_question_query(conversation)
    elif intent_type == "investigative":
        return create_investigative_question_query(conversation)
    else:
        raise ValueError(f"Invalid intent type: {intent_type}")
# POST ENDPOINT FUNCTION

def add_user_message_to_conversation(conversation: dict, user_message: str) -> dict:
    return {
        **conversation,
        "messages": conversation["messages"] + [{
            "role": "user",
            "user_message": user_message
        }]
    }

def add_query_to_conversation(conversation: dict, query: str) -> dict:
    return {
        **conversation,
        "messages": conversation["messages"] + [{
            "query": query
        }]
    }

def chat_with_llm(chat_id: str, user_message: str):
    try:
        # Create new conversation if it doesn't exist
        conversation = get_or_create_conversation(chat_id)
        # Add user message to conversation
        # add before the LLM call, easier to track if there are errors, re-run inference if fails
        # this can also be await async 
        conversation = add_message_to_conversation(conversation=conversation, message=user_message, role="user")
        breakpoint()
        intent = classify_intent(conversation)
        print(intent)
        query = create_query(intent, conversation)
        conversation = add_query_to_conversation(conversation = conversation, query = query)
        
        response = make_llm_call(conversation)
        # Make LLM call with full conversation history
        # Add assistant response to conversation history
        conversation = add_message_to_conversation(conversation = conversation, message = response, role = "assistant")
        return response 
    except Exception as e:
        print(f"Error in chat: {e}")
        return "Sorry, something went wrong."

if __name__ == "__main__":
    
    chat_id = "flight_analysis_001"
    response = chat_with_llm(chat_id, "What was the maximum altitude reached in this flight?")
    print(response)
    

    # chat_with_llm(chat_id, "Any anomalies with the flight data?")
    # print(conversations[chat_id]["messages"])
    # classify_intent()

