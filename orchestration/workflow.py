from langgraph.graph import StateGraph, END
from typing import Dict, Any
import logging

from orchestration.state import MathMentorState
from agents.parser_agent import ParserAgent
from agents.intent_router import IntentRouter
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from rag.retriever import Retriever


class MathMentorWorkflow:
    """
    LangGraph-based workflow orchestrating all agents.
    """
    
    def __init__(self, config: Dict[str, Any], prompts: Dict[str, str]):
        """
        Initialize workflow with all agents.
        
        Args:
            config: Configuration dictionary
            prompts: Prompt templates dictionary
        """
        self.config = config
        self.prompts = prompts
        self.logger = logging.getLogger("workflow")
        
        # Initialize agents
        self.logger.info("Initializing agents...")
        self.parser = ParserAgent(config, prompts.get('parser_agent', ''))
        self.router = IntentRouter(config, prompts.get('intent_router', ''))
        self.solver = SolverAgent(config, prompts.get('solver_agent', ''))
        self.verifier = VerifierAgent(config, prompts.get('verifier_agent', ''))
        
        # Initialize RAG retriever
        self.logger.info("Initializing RAG retriever...")
        self.retriever = Retriever(config.get('rag', {}))
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        self.logger.info("Workflow initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(MathMentorState)
        
        # Add nodes
        workflow.add_node("parse", self._parse_node)
        workflow.add_node("route", self._route_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("solve", self._solve_node)
        workflow.add_node("verify", self._verify_node)
        workflow.add_node("hitl_check", self._hitl_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point
        workflow.set_entry_point("parse")
        
        # Define edges
        workflow.add_edge("parse", "route")
        
        # Conditional edge after routing (check if in scope)
        workflow.add_conditional_edges(
            "route",
            self._should_continue_after_route,
            {
                "continue": "retrieve",
                "end": "finalize"
            }
        )
        
        workflow.add_edge("retrieve", "solve")
        workflow.add_edge("solve", "verify")
        
        # Conditional edge after verification (check if HITL needed)
        workflow.add_conditional_edges(
            "verify",
            self._should_trigger_hitl,
            {
                "hitl_needed": "hitl_check",
                "proceed": "finalize"
            }
        )
        
        # After HITL, go back to solve or finalize
        workflow.add_conditional_edges(
            "hitl_check",
            self._after_hitl,
            {
                "retry": "solve",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _parse_node(self, state: MathMentorState) -> MathMentorState:
        """Parser node."""
        self.logger.info(f"[{state['state_id']}] Running parser agent")
        return self.parser.run(state)
    
    def _route_node(self, state: MathMentorState) -> MathMentorState:
        """Intent router node."""
        self.logger.info(f"[{state['state_id']}] Running intent router")
        return self.router.run(state)
    
    def _retrieve_node(self, state: MathMentorState) -> MathMentorState:
        """RAG retrieval node."""
        self.logger.info(f"[{state['state_id']}] Running RAG retrieval")
        
        try:
            # Retrieve relevant context
            retrieval_result = self.retriever.retrieve_for_problem(state["parsed_problem"])
            
            # Update state
            state["retrieved_context"] = retrieval_result["retrieved_context"]
            state["retrieval_confidence"] = retrieval_result["retrieval_confidence"]
            state["retrieval_sources"] = retrieval_result["retrieval_sources"]
            state["retrieval_query"] = retrieval_result["retrieval_query"]
            
            # Check if retrieval confidence is too low
            hitl_config = self.config.get('hitl', {})
            min_confidence = hitl_config.get('retrieval_confidence_min', 0.6)
            
            if state["retrieval_confidence"] < min_confidence:
                state["requires_human"] = True
                state["hitl_reason"] = f"Retrieval confidence too low: {state['retrieval_confidence']:.2f}"
            
            self.logger.info(
                f"[{state['state_id']}] Retrieved {len(state['retrieved_context'])} documents, "
                f"confidence: {state['retrieval_confidence']:.3f}"
            )
        
        except Exception as e:
            self.logger.error(f"[{state['state_id']}] Retrieval error: {e}", exc_info=True)
            state["retrieved_context"] = []
            state["retrieval_confidence"] = 0.0
            state["requires_human"] = True
            state["hitl_reason"] = f"Retrieval failed: {str(e)}"
        
        return state
    
    def _solve_node(self, state: MathMentorState) -> MathMentorState:
        """Solver node."""
        self.logger.info(f"[{state['state_id']}] Running solver agent")
        return self.solver.run(state)
    
    def _verify_node(self, state: MathMentorState) -> MathMentorState:
        """Verifier node."""
        self.logger.info(f"[{state['state_id']}] Running verifier agent")
        return self.verifier.run(state)
    
    def _hitl_node(self, state: MathMentorState) -> MathMentorState:
        """HITL check node."""
        self.logger.info(f"[{state['state_id']}] HITL intervention required: {state.get('hitl_reason', 'N/A')}")
        
        # In a real implementation, this would pause and wait for human input
        # For now, we'll just mark it and continue
        state["workflow_status"] = "requires_hitl"
        
        # If human feedback provided (in a real system)
        if state.get("human_feedback"):
            state["hitl_resolved"] = True
            self.logger.info(f"[{state['state_id']}] HITL resolved with feedback")
        
        return state
    
    def _finalize_node(self, state: MathMentorState) -> MathMentorState:
        """Finalize node."""
        self.logger.info(f"[{state['state_id']}] Finalizing workflow")
        
        import time
        state["end_time"] = time.time()
        state["total_duration"] = state["end_time"] - state["start_time"]
        
        if state.get("workflow_status") == "in_progress":
            if state.get("requires_human") and not state.get("hitl_resolved"):
                state["workflow_status"] = "requires_hitl"
            elif state.get("errors"):
                state["workflow_status"] = "failed"
            else:
                state["workflow_status"] = "completed"
        
        self.logger.info(
            f"[{state['state_id']}] Workflow {state['workflow_status']} "
            f"in {state['total_duration']:.2f}s"
        )
        
        return state
    
    def _should_continue_after_route(self, state: MathMentorState) -> str:
        """Decide whether to continue after routing."""
        if not state.get("in_scope", True):
            return "end"
        return "continue"
    
    def _should_trigger_hitl(self, state: MathMentorState) -> str:
        """Decide whether HITL is needed after verification."""
        if state.get("requires_human", False) and not state.get("hitl_resolved", False):
            return "hitl_needed"
        return "proceed"
    
    def _after_hitl(self, state: MathMentorState) -> str:
        """Decide what to do after HITL."""
        if state.get("hitl_resolved", False):
            # Could retry solving or just finalize
            return "finalize"
        return "finalize"
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Run the complete workflow.
        
        Args:
            state: Initial state
        
        Returns:
            Final state
        """
        self.logger.info(f"Starting workflow for state: {state['state_id']}")
        
        try:
            final_state = self.workflow.invoke(state)
            return final_state
        
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}", exc_info=True)
            state["workflow_status"] = "failed"
            state["errors"].append(f"Workflow error: {str(e)}")
            return state