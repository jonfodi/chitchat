from pydantic import BaseModel
from typing import Dict, Any

# Pydantic models for request validation
class FlightDataRequest(BaseModel):
    messages: Dict[str, Any]