
import logging
import dotenv
from ..classes import AnalysisState
from typing import Any, Dict
from ..classes.state import InputState

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class ChatAgent:
    def __init__(self) -> None:
        pass

    def receive(self, state: AnalysisState) -> Dict[str, Any]:
        return state

    def run(self, state: InputState) -> Dict[str, Any]:
        return self.receive(state)