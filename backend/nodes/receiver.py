
import logging
import dotenv
from ..classes import AnalysisState
from typing import Any, Dict


dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self) -> None:
        pass

    def receive(self, state: AnalysisState) -> Dict[str, Any]:
        return state

    def run(self, state: AnalysisState) -> Dict[str, Any]:
        return self.receive(state)