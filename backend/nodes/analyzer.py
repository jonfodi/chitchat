
import logging
import dotenv
from ..classes import InputState, AnalysisState
from typing import Any, Dict

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self) -> None:
        pass

    def analyze(self, state: AnalysisState) -> Dict[str, Any]:
        print("analyzing")
        return state

    def run(self, state: InputState) -> Dict[str, Any]:
        return self.analyze(state)