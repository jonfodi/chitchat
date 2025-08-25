import logging
from typing import Any, Dict, List

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph

from .classes.state import InputState, AnalysisState
from .nodes.receiver import Receiver
from .nodes.validator import Validator

logger = logging.getLogger(__name__)

class Graph:
    def __init__(self, conversation: List[Dict[str, Any]]):
        
        # Initialize InputState
        self.input_state = InputState(
            conversation = conversation,
            messages=[
                SystemMessage(content="Expert flight data analyst")
            ]
        )

        # Initialize nodes
        self._init_nodes()
        self._build_workflow()

    def _init_nodes(self):
        """Initialize all workflow nodes"""
        self.receive = Receiver()
        self.validate = Validator()
 
    def _build_workflow(self):
        """Configure the state graph workflow"""
        self.workflow = StateGraph(AnalysisState)
        
        # Add nodes with their respective processing functions
        self.workflow.add_node("crawler", self.crawler.run)
        self.workflow.add_node("extractor", self.extract.run)
        self.workflow.add_node("processor", self.process.run)

        # Configure workflow edges
        self.workflow.set_entry_point("crawler")
        self.workflow.set_finish_point("processor")
        

        # Connect remaining nodes
        self.workflow.add_edge("crawler", "extractor")
        self.workflow.add_edge("extractor", "processor")

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