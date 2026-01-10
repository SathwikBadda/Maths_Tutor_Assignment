"""
Reusable Streamlit UI components.
"""

import streamlit as st
from typing import Dict, Any, List


def display_solution(state: Dict[str, Any]):
    """
    Display the solution with steps and final answer.
    
    Args:
        state: Workflow state containing solution
    """
    st.header("📝 Solution")
    
    # Display status
    status = state.get('workflow_status', 'unknown')
    verification_confidence = state.get('verification_confidence', 0.0)
    
    if status == 'completed':
        st.success(f"✅ Solution Complete (verified with {verification_confidence:.0%} confidence)")
    elif status == 'requires_hitl':
        st.warning(f"⚠️ Human Review Needed: {state.get('hitl_reason', 'Unknown')}")
    elif status == 'failed':
        st.error("❌ Failed to solve problem")
    
    # Display solution steps
    solution_steps = state.get('solution_steps', [])
    if solution_steps:
        st.subheader("Step-by-Step Solution")
        for i, step in enumerate(solution_steps, 1):
            with st.container():
                st.markdown(f"**Step {i}**")
                st.markdown(step)
                st.markdown("")
    
    # Display final answer
    final_answer = state.get('final_answer', '')
    if final_answer:
        st.subheader("Final Answer")
        st.success(final_answer)


def display_metrics(state: Dict[str, Any]):
    """
    Display problem metrics in columns.
    
    Args:
        state: Workflow state
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Topic", state.get('topic', 'N/A'))
    
    with col2:
        complexity = state.get('complexity_score', 0.0)
        st.metric("Complexity", f"{complexity:.1f}/1.0")
    
    with col3:
        duration = state.get('total_duration', 0.0)
        st.metric("Duration", f"{duration:.1f}s")
    
    with col4:
        confidence = state.get('verification_confidence', 0.0)
        st.metric("Confidence", f"{confidence:.0%}")


def display_error(error_message: str, details: str = None):
    """
    Display an error message with optional details.
    
    Args:
        error_message: Main error message
        details: Optional detailed error information
    """
    st.error(f"❌ {error_message}")
    
    if details:
        with st.expander("Error Details"):
            st.code(details)


def display_problem_summary(state: Dict[str, Any]):
    """
    Display a summary of the parsed problem.
    
    Args:
        state: Workflow state
    """
    parsed = state.get('parsed_problem', {})
    
    with st.expander("📋 Problem Summary", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Topic:**", parsed.get('topic', 'N/A'))
            st.write("**Subtopic:**", parsed.get('subtopic', 'N/A'))
            st.write("**Question Type:**", parsed.get('question_type', 'N/A'))
        
        with col2:
            variables = parsed.get('variables', [])
            st.write("**Variables:**", ', '.join(variables) if variables else 'None')
            
            constraints = parsed.get('constraints', [])
            if constraints:
                st.write("**Constraints:**")
                for constraint in constraints:
                    st.write(f"  - {constraint}")


def display_retrieved_context(retrieved_docs: List[Dict[str, Any]]):
    """
    Display retrieved context documents.
    
    Args:
        retrieved_docs: List of retrieved documents
    """
    if not retrieved_docs:
        st.info("No context retrieved")
        return
    
    st.subheader(f"📚 Retrieved Context ({len(retrieved_docs)} documents)")
    
    for i, doc in enumerate(retrieved_docs, 1):
        with st.expander(
            f"Source {i}: {doc.get('source', 'N/A')} "
            f"(Relevance: {doc.get('similarity_score', 0):.2f})"
        ):
            st.markdown(f"**Topic:** {doc.get('topic', 'N/A')}")
            st.markdown(f"**Subtopic:** {doc.get('subtopic', 'N/A')}")
            st.markdown("**Content:**")
            content = doc.get('content', '')
            st.text(content[:500] + ('...' if len(content) > 500 else ''))


def display_key_concepts(concepts: List[str], pitfalls: List[str], related: List[str]):
    """
    Display key concepts, pitfalls, and related topics.
    
    Args:
        concepts: List of key concepts
        pitfalls: List of common pitfalls
        related: List of related topics
    """
    if concepts:
        st.subheader("💡 Key Concepts")
        for concept in concepts:
            st.markdown(f"- {concept}")
    
    if pitfalls:
        st.subheader("⚠️ Common Pitfalls")
        for pitfall in pitfalls:
            st.markdown(f"- {pitfall}")
    
    if related:
        st.subheader("🔗 Related Topics")
        for topic in related:
            st.markdown(f"- {topic}")


def display_workflow_status(state: Dict[str, Any]):
    """
    Display workflow execution status with progress indicator.
    
    Args:
        state: Workflow state
    """
    status = state.get('workflow_status', 'in_progress')
    
    status_colors = {
        'in_progress': '🔄',
        'completed': '✅',
        'failed': '❌',
        'requires_hitl': '⚠️'
    }
    
    icon = status_colors.get(status, '❓')
    st.markdown(f"### {icon} Status: {status.replace('_', ' ').title()}")
    
    # Show agent trace summary
    agent_trace = state.get('agent_trace', [])
    if agent_trace:
        st.caption(f"Executed {len(agent_trace)} agent actions")


def create_problem_card(interaction: Dict[str, Any], index: int):
    """
    Create a card display for a problem in history.
    
    Args:
        interaction: Interaction data
        index: Problem index
    """
    topic = interaction.get('topic', 'N/A')
    status = interaction.get('workflow_status', 'unknown')
    
    status_emoji = {
        'completed': '✅',
        'failed': '❌',
        'requires_hitl': '⚠️'
    }.get(status, '❓')
    
    with st.expander(f"Problem {index}: {topic} {status_emoji}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Input:**")
            st.text(interaction.get('raw_input', 'N/A')[:100] + '...')
            st.write(f"**Status:** {status}")
        
        with col2:
            st.write("**Answer:**")
            answer = interaction.get('final_answer', 'N/A')
            st.text(answer[:100] + ('...' if len(answer) > 100 else ''))
            
            duration = interaction.get('total_duration', 0)
            st.write(f"**Duration:** {duration:.1f}s")


def display_progress_bar(current_step: int, total_steps: int, step_name: str):
    """
    Display a progress bar for workflow execution.
    
    Args:
        current_step: Current step number
        total_steps: Total number of steps
        step_name: Name of current step
    """
    progress = current_step / total_steps
    st.progress(progress)
    st.caption(f"Step {current_step}/{total_steps}: {step_name}")