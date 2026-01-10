from typing import TypedDict, List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid


class MathMentorState(TypedDict, total=False):
    """
    Complete state schema for the Math Mentor workflow.
    """
    
    # Unique identifiers
    state_id: str
    session_id: str
    interaction_id: str
    timestamp: str
    
    # Input stage
    raw_input: str
    input_type: Literal["text", "image", "audio"]
    input_metadata: Dict[str, Any]
    
    # Parser stage
    parsed_problem: Dict[str, Any]
    parsing_confidence: float
    parsing_errors: List[str]
    
    # Intent routing stage
    topic: str
    subtopic: str
    complexity_score: float
    estimated_steps: int
    required_tools: List[str]
    in_scope: bool
    out_of_scope_reason: str
    
    # RAG retrieval stage
    retrieval_query: str
    retrieved_context: List[Dict[str, Any]]
    retrieval_confidence: float
    retrieval_sources: List[str]
    
    # Solver stage
    solution_steps: List[str]
    final_answer: str
    tools_used: List[Dict[str, Any]]
    
    # Verification stage
    is_verified: bool
    verification_confidence: float
    verification_method: str
    verification_details: Dict[str, Any]
    verification_issues: List[str]
    
    # HITL stage
    requires_human: bool
    hitl_reason: str
    hitl_context: Dict[str, Any]
    human_feedback: Optional[str]
    hitl_resolved: bool
    
    # Explanation stage
    explanation: str
    key_concepts: List[str]
    common_pitfalls: List[str]
    related_topics: List[str]
    
    # Guardrail stage
    passes_guardrails: bool
    guardrail_issues: List[str]
    citation_check: str
    hallucination_check: str
    
    # Evaluation stage
    overall_quality_score: float
    user_feedback_rating: Optional[int]
    user_feedback_text: Optional[str]
    areas_for_improvement: List[str]
    
    # Workflow metadata
    agent_trace: List[Dict[str, Any]]
    current_agent: str
    workflow_status: Literal["in_progress", "completed", "failed", "requires_hitl"]
    errors: List[str]
    warnings: List[str]
    
    # Timing information
    start_time: float
    end_time: Optional[float]
    total_duration: Optional[float]


def create_initial_state(
    raw_input: str,
    input_type: Literal["text", "image", "audio"],
    session_id: Optional[str] = None
) -> MathMentorState:
    """
    Create an initial state object for a new interaction.
    
    Args:
        raw_input: The raw input from the user
        input_type: Type of input (text, image, or audio)
        session_id: Optional session ID for continuity
    
    Returns:
        Initialized MathMentorState
    """
    import time
    
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    state = MathMentorState(
        state_id=str(uuid.uuid4()),
        session_id=session_id,
        interaction_id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        
        raw_input=raw_input,
        input_type=input_type,
        input_metadata={},
        
        parsed_problem={},
        parsing_confidence=0.0,
        parsing_errors=[],
        
        topic="",
        subtopic="",
        complexity_score=0.0,
        estimated_steps=0,
        required_tools=[],
        in_scope=True,
        out_of_scope_reason="",
        
        retrieval_query="",
        retrieved_context=[],
        retrieval_confidence=0.0,
        retrieval_sources=[],
        
        solution_steps=[],
        final_answer="",
        tools_used=[],
        
        is_verified=False,
        verification_confidence=0.0,
        verification_method="",
        verification_details={},
        verification_issues=[],
        
        requires_human=False,
        hitl_reason="",
        hitl_context={},
        human_feedback=None,
        hitl_resolved=False,
        
        explanation="",
        key_concepts=[],
        common_pitfalls=[],
        related_topics=[],
        
        passes_guardrails=True,
        guardrail_issues=[],
        citation_check="",
        hallucination_check="",
        
        overall_quality_score=0.0,
        user_feedback_rating=None,
        user_feedback_text=None,
        areas_for_improvement=[],
        
        agent_trace=[],
        current_agent="",
        workflow_status="in_progress",
        errors=[],
        warnings=[],
        
        start_time=time.time(),
        end_time=None,
        total_duration=None
    )
    
    return state


def add_agent_trace(state: MathMentorState, agent_name: str, action: str, details: Dict[str, Any]):
    """
    Add an entry to the agent trace.
    
    Args:
        state: Current state
        agent_name: Name of the agent
        action: Action performed
        details: Additional details
    """
    trace_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "action": action,
        "details": details
    }
    
    if "agent_trace" not in state:
        state["agent_trace"] = []
    
    state["agent_trace"].append(trace_entry)


def add_error(state: MathMentorState, error_msg: str):
    """Add an error message to the state."""
    if "errors" not in state:
        state["errors"] = []
    state["errors"].append(error_msg)


def add_warning(state: MathMentorState, warning_msg: str):
    """Add a warning message to the state."""
    if "warnings" not in state:
        state["warnings"] = []
    state["warnings"].append(warning_msg)