import json
import time
from typing import Dict, Any
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error, add_warning
from utils.logger import AgentLogger


class GuardrailAgent:
    """
    Guardrail Agent: Ensures quality, safety, and scope compliance.
    Checks for hallucinations, citation validity, and appropriate content.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("guardrail", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        self.model = llm_config.get('model')
        self.temperature = llm_config.get('temperature', 0.1)
        self.max_tokens = llm_config.get('max_tokens', 4000)
        
        # Load scope configuration
        self.allowed_topics = config.get('scope', {}).get('allowed_topics', [])
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Run guardrail checks on the complete interaction.
        
        Args:
            state: Current state with solution and explanation
        
        Returns:
            Updated state with guardrail results
        """
        start_time = time.time()
        state["current_agent"] = "guardrail"
        
        try:
            self.logger.log_start(
                state["state_id"],
                "Running guardrail checks"
            )
            
            # Perform checks
            scope_check = self._check_scope(state)
            citation_check = self._check_citations(state)
            hallucination_check = self._check_hallucination(state)
            safety_check = self._check_safety(state)
            
            # Aggregate results
            all_checks_pass = all([
                scope_check == "in_scope",
                citation_check == "all_citations_valid",
                hallucination_check == "no_hallucination",
                safety_check == "safe"
            ])
            
            # Collect issues
            issues = []
            if scope_check == "out_of_scope":
                issues.append("Problem is out of scope")
            if citation_check == "invalid_citations_found":
                issues.append("Invalid citations detected")
            if hallucination_check == "potential_hallucination":
                issues.append("Potential hallucination detected")
            if safety_check == "unsafe":
                issues.append("Safety concerns detected")
            
            # Update state
            state["passes_guardrails"] = all_checks_pass
            state["guardrail_issues"] = issues
            state["citation_check"] = citation_check
            state["hallucination_check"] = hallucination_check
            
            # Log warnings if issues found
            if issues:
                for issue in issues:
                    add_warning(state, issue)
                    self.logger.logger.warning(f"Guardrail issue: {issue}")
            
            # Add to trace
            add_agent_trace(state, "guardrail", "checks_complete", {
                "passes_all": all_checks_pass,
                "num_issues": len(issues),
                "scope_check": scope_check,
                "citation_check": citation_check,
                "hallucination_check": hallucination_check,
                "safety_check": safety_check
            })
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Guardrails: {'PASS' if all_checks_pass else 'FAIL'} ({len(issues)} issues)",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Guardrail error: {str(e)}")
            state["passes_guardrails"] = False
            state["guardrail_issues"] = [f"Guardrail check failed: {str(e)}"]
            return state
    
    def _check_scope(self, state: MathMentorState) -> str:
        """Check if problem is within allowed scope."""
        topic = state.get("topic", "")
        in_scope = state.get("in_scope", True)
        
        if not in_scope or topic not in self.allowed_topics:
            self.logger.logger.warning(f"Scope check failed: topic={topic}, in_scope={in_scope}")
            return "out_of_scope"
        
        return "in_scope"
    
    def _check_citations(self, state: MathMentorState) -> str:
        """Check if all citations in the solution are valid."""
        # Get solution text
        solution_steps = state.get("solution_steps", [])
        solution_text = "\n".join(solution_steps)
        
        # Get retrieved sources
        retrieved_sources = set(state.get("retrieval_sources", []))
        
        # Simple citation check - look for [Source: ...] patterns
        import re
        citations = re.findall(r'\[Source:\s*([^\]]+)\]', solution_text)
        
        if not citations:
            # No citations found - this is okay
            return "all_citations_valid"
        
        # Check if all citations exist in retrieved sources
        for citation in citations:
            citation = citation.strip()
            if citation not in retrieved_sources:
                self.logger.logger.warning(f"Invalid citation: {citation}")
                return "invalid_citations_found"
        
        return "all_citations_valid"
    
    def _check_hallucination(self, state: MathMentorState) -> str:
        """
        Check for potential hallucinations in the solution.
        Looks for invented formulas or theorems not in retrieved context.
        """
        # Get solution and context
        solution_text = "\n".join(state.get("solution_steps", []))
        retrieved_context = state.get("retrieved_context", [])
        
        # Simple heuristic checks
        # 1. If solution references formulas, check if they appear in context
        # 2. Look for common hallucination patterns
        
        # For now, a basic check based on verification confidence
        verification_confidence = state.get("verification_confidence", 0.0)
        
        if verification_confidence < 0.7:
            self.logger.logger.warning("Low verification confidence - potential hallucination")
            return "potential_hallucination"
        
        # Check if solution is much longer than typical
        if len(solution_text) > 5000 and not retrieved_context:
            self.logger.logger.warning("Long solution without context - potential hallucination")
            return "potential_hallucination"
        
        return "no_hallucination"
    
    def _check_safety(self, state: MathMentorState) -> str:
        """
        Check for safety concerns in content.
        For math problems, this is mostly about appropriate difficulty level.
        """
        # Basic safety checks for educational content
        
        # Check if content is appropriate for students
        problem_text = state.get("raw_input", "").lower()
        solution_text = "\n".join(state.get("solution_steps", [])).lower()
        
        # List of inappropriate keywords (very basic)
        inappropriate_keywords = ["hack", "cheat", "steal", "illegal"]
        
        combined_text = problem_text + " " + solution_text
        
        for keyword in inappropriate_keywords:
            if keyword in combined_text:
                self.logger.logger.warning(f"Safety concern: found keyword '{keyword}'")
                return "unsafe"
        
        return "safe"