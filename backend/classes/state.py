from enum import Enum
from typing import TypedDict, NotRequired, Required, Dict, List, Any

# Define a single shoe item
# ideally this would be data that a nike api would need to retrieve an item and process a payment
class ShoeItem(TypedDict):
    pass

# make gender enum of either male or female
class Gender(Enum):
    MALE = "men"
    WOMAN = "women"

class ShoeType(Enum):
    AIR_FORCE_ONE = "air force one"
    AIR_JORDAN = "air jordan"
    AIR_MAX = "air max"

class InputState(TypedDict, total=False):
    shoe_type: Required[str]
    size: Required[float]
    gender: Required[Gender]
    budget: NotRequired[int]
    color: NotRequired[str]

class AnalysisState(InputState):
    url: str
    shoe_data: Dict[str, Any]
    enhanced_shoe_data: Dict[str, Any]
    shoe_reccomendations: List[Dict[str, Any]]  # Ranked list of shoe recommendations
    extraction_status: NotRequired[str]  # Track extraction success/failure

