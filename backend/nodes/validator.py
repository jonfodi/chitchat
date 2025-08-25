import logging
from tavily import TavilyClient
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
        return state

    def run(self, state: AnalysisState) -> Dict[str, Any]:
        return self.validate(state)

