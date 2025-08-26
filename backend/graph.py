import logging
from typing import Any, Dict, List

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph

from .classes.state import InputState, AnalysisState
from .nodes import Validator
from .nodes.analyzer import Analyzer


logger = logging.getLogger(__name__)

class Graph:
    def __init__(self, conversation: List[Dict[str, Any]], data: Dict[str, Any]):
        
        # Initialize InputState
        self.input_state = InputState(
            conversation = conversation,
            data = data,
            messages=[
                SystemMessage(content="Expert flight data analyst")
            ]
        )

        # Initialize nodes
        self._init_nodes()
        self._build_workflow()

    def _init_nodes(self):
        """Initialize all workflow nodes"""
        self.validator = Validator()
        self.analyzer = Analyzer()
 
    def _build_workflow(self):
        """Configure the state graph workflow"""
        self.workflow = StateGraph(AnalysisState)
        
        # Add nodes with their respective processing functions
        self.workflow.add_node("validator", self.validator.run)
        self.workflow.add_node("analyzer", self.analyzer.run)
        # Set entry point
        self.workflow.set_entry_point("validator")

        # Add conditional edge from validator
        self.workflow.add_conditional_edges(
            "validator",  # source node
            self.route_after_validation,  # router function
            {
                "analyzer": "analyzer",
                "response_handler": "response_handler"
            }
        )

        # Both nodes can be terminal, so set multiple finish points
        self.workflow.set_finish_point("analyzer")
        # self.workflow.set_finish_point("response_handler")

 

    def run(self) -> Dict[str, Any]:
        """Execute the workflow synchronously"""
        print("compiling graph")
        compiled_graph = self.workflow.compile()
        print("graph compiled")
        
        # Use invoke() for synchronous execution instead of astream()
        print("invoking graph")
        final_state = compiled_graph.invoke(
            self.input_state,
        )
        print("graph invoked")
        return final_state

    def compile(self):
        graph = self.workflow.compile()
        return graph