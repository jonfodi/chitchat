import logging
import dotenv
from openai import OpenAI


from ..classes import InputState, AnalysisState
from typing import Any, Dict

dotenv.load_dotenv()
logger = logging.getLogger(__name__)    

class Validator:
    def __init__(self): 
        self.openai_client = OpenAI()

    def validate(self, state: InputState) -> Dict[str, Any]:
        can_analyze = run_validation_prompt(state)

        state["can_analyze"] = can_analyze
        return state


    def run(self, state: InputState) -> Dict[str, Any]:
        return self.validate(state)


def run_validation_prompt(state: InputState) -> bool:
    breakpoint()
    user_query = get_last_user_message(state)

    print(user_query)
    prompt = f"""
    You are a helpful assistant that validates user queries.
    You need to determine if the user query is respondable given the data. 

    The data is:


    The user query is:
    User query: {user_query}
    """
    return True
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that validates user queries. You must return a boolean value."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1000
        )
        return response.output_text
    
    except Exception as e:
        logger.error(f"Error running validation prompt: {e}")
        return False


def get_last_user_message(state: InputState) -> str:
    
    role = state["conversation"]["messages"][-1]["role"]
    if role == "user":
        return state["conversation"]["messages"][-1]["content"]
    else:
        return None # TODO: handle this case