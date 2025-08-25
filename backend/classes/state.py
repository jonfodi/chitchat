from enum import Enum
from typing import TypedDict, NotRequired, Required, Dict, List, Any

# how should this work
# so we have an endpoint that frontend is sending data to
# we need to process it --> MavLinkProcessor
# but then i want to send a chat message to user like hey im an assistant feel free to ask me anything about the data
# that seems more complex
# i can also just process in endpoint and pass data to the graph as inputstate
# this solution would be: process_flight_data processes. stores data in a database.
# agent endpoint is chat. 
# then just need to figure out how to get the conversation working with this flow 
# maybe its a conditional edge? 

# first node = Validator 
# uses LLM to analyze user query and determine if it is a valid query
# you have access to this data. determine if you can answer the question or not
# if you can, send the data to the next node 
# if not, ask a clarifying question 
# what is the problem here. its maintaing the conversation state. but do we even wanna keep it. 
# yes we do. we need to store in DB 

class InputState(TypedDict, total=False):
    user_query: str
    conversation_id: str


class AnalysisState(InputState):
    conversation: List[Dict[str, Any]] # [{role: user, content: str}, {role: assistant, content: str}]

