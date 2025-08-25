from pydantic import BaseModel, field_validator
from typing import Dict, Any, List
from enum import Enum


class AllowedMessagTypes(str, Enum):
    AHR2 = "AHR2"
    GPS = "GPS"
    POS = "POS"
    ATT = "ATT"


# Pydantic models for request validation
class FlightDataRequest(BaseModel):
    messages: Dict[str, Any]


    @field_validator('messages')
    def validate_messages(cls, v):
        if not isinstance(v, dict):
            raise ValueError("messages must be a dictionary")
        return v
    
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
    conversation_id: str
    