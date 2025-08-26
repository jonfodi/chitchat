import logging
import dotenv
from openai import OpenAI


from ..classes import AnalysisState
from typing import Any, Dict

dotenv.load_dotenv()
logger = logging.getLogger(__name__)    

class ResponseHandler:
    def __init__(self): 
        self.openai_client = OpenAI()
    
    def run(self, state: AnalysisState) -> Dict[str, Any]:
        return state