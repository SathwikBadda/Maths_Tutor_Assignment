"""
Agent trace visualization for Streamlit.
"""

import streamlit as st
from typing import Dict, Any, List
import json


def display_agent_trace(agent_trace: List[Dict[str, Any]]):
    """
    Display the agent execution trace with timeline view.
    
    Args:
        agent_trace: List of agent trace entries
    """
    if not agent_trace:
        st.info("No agent trace available")
        return
    
    st.subheader(f"🔍 Agent Trace ({len(agent_trace)} actions)")
    
    # Timeline view
    for i, trace_entry in enumerate(agent_trace, 1):
        agent_name = trace_entry.get('agent', 'Unknown')
        action = trace_entry.get('action', 'unknown')
        timestamp = trace_entry.get('timestamp', 'N/A')
        details = trace_entry.get('details', {})
        
        # Create visual timeline
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Agent icon
                agent_icons = {
                    'parser': '📝',
                    'intent_router': '🎯',
                    'rag_retrieval': '📚',
                    'solver': '🧮',
                    'verifier': '✓',
                    'explainer': '💡',
                    'guardrail': '🛡️',
                    'evaluator': '📊'
                }
                icon = agent_icons.get(agent_name, '🤖')
                
                st.markdown(f"### {icon}")
                st.caption(timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp)
            
            with col2:
                st.markdown(f"**{agent_name.replace('_', ' ').title()}**")
                st.markdown(f"*{action.replace('_', ' ').title()}*")
                
                # Display details in expandable section
                if details:
                    with st.expander("Details"):
                        st.json(details)
            
            # Add separator except for last item
            if i < len(agent_trace):
                st.markdown("---")


def display_compact_trace(agent_trace: List[Dict[str, Any]]):
    """
    Display a compact version of agent trace.
    
    Args:
        agent_trace: List of agent trace entries
    """
    if not agent_trace:
        return
    
    trace_summary = " → ".join([
        entry.get('agent', 'unknown').replace('_', ' ').title()
        for entry in agent_trace
    ])
    
    st.caption(f"Execution flow: {trace_summary}")


def display_trace_statistics(agent_trace: List[Dict[str, Any]]):
    """
    Display statistics about the agent trace.
    
    Args:
        agent_trace: List of agent trace entries
    """
    if not agent_trace:
        return
    
    # Count actions per agent
    agent_counts = {}
    for entry in agent_trace:
        agent = entry.get('agent', 'unknown')
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    st.subheader("📈 Trace Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Actions", len(agent_trace))
    
    with col2:
        st.metric("Unique Agents", len(agent_counts))
    
    with col3:
        most_active = max(agent_counts.items(), key=lambda x: x[1])
        st.metric("Most Active Agent", most_active[0].title())
    
    # Show breakdown
    with st.expander("Agent Breakdown"):
        for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"**{agent.replace('_', ' ').title()}**: {count} action(s)")


def create_trace_visualization(agent_trace: List[Dict[str, Any]]) -> str:
    """
    Create a Mermaid diagram of the agent trace.
    
    Args:
        agent_trace: List of agent trace entries
    
    Returns:
        Mermaid diagram string
    """
    if not agent_trace:
        return ""
    
    diagram_lines = ["graph LR"]
    
    for i, entry in enumerate(agent_trace):
        agent = entry.get('agent', 'unknown')
        action = entry.get('action', 'unknown')
        
        node_id = f"A{i}"
        label = f"{agent}<br/>{action}"
        
        diagram_lines.append(f"    {node_id}[\"{label}\"]")
        
        if i > 0:
            prev_node = f"A{i-1}"
            diagram_lines.append(f"    {prev_node} --> {node_id}")
    
    return "\n".join(diagram_lines)


def export_trace_to_json(agent_trace: List[Dict[str, Any]]) -> str:
    """
    Export agent trace to JSON string.
    
    Args:
        agent_trace: List of agent trace entries
    
    Returns:
        JSON string
    """
    return json.dumps(agent_trace, indent=2, ensure_ascii=False)


def display_trace_with_download(agent_trace: List[Dict[str, Any]]):
    """
    Display agent trace with download option.
    
    Args:
        agent_trace: List of agent trace entries
    """
    display_agent_trace(agent_trace)
    
    if agent_trace:
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download as JSON
            trace_json = export_trace_to_json(agent_trace)
            st.download_button(
                label="📥 Download Trace (JSON)",
                data=trace_json,
                file_name="agent_trace.json",
                mime="application/json"
            )
        
        with col2:
            # Show statistics
            if st.button("📊 Show Statistics"):
                display_trace_statistics(agent_trace)