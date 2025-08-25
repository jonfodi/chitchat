import logging
import dotenv

from backend.classes.state import Gender, InputState

from ..classes import AnalysisState
from typing import Any, Dict

dotenv.load_dotenv()
logger = logging.getLogger(__name__)    

class Validator:
    def __init__(self): 
        pass

    def validate(self, state: AnalysisState) -> Dict[str, Any]:
        can_analyze = run_validation_prompt(state)

        state["can_analyze"] = can_analyze
        return state


    def run(self, state: AnalysisState) -> Dict[str, Any]:
        return self.validate(state)


def run_validation_prompt(state: AnalysisState) -> bool:
    user_query = state["messages"][-1]["content"]
    prompt = f"""
    You are a helpful assistant that validates user queries.
    You need to determine if the user query is respondable given the data. 

    The data is:


    The user query is:
    User query: {user_query}
    """
    
