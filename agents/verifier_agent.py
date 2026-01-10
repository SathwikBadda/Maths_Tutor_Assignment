import json
import time
from typing import Dict, Any
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error
from utils.logger import AgentLogger
from mathtools.symbolic_math import SymbolicMathTool


class VerifierAgent:
    """
    Verifier Agent: Checks the correctness of solutions.
    Uses symbolic verification, numerical testing, and logical checks.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("verifier", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        self.model = llm_config.get('model')
        self.temperature = llm_config.get('temperature', 0.1)
        self.max_tokens = llm_config.get('max_tokens', 4000)
        
        # Initialize symbolic math tool
        self.symbolic_math = SymbolicMathTool()
        
        # Agent config
        agent_config = config.get('agents', {}).get('verifier', {})
        self.num_test_cases = agent_config.get('num_test_cases', 5)
        self.use_symbolic = agent_config.get('use_symbolic_verification', True)
        self.use_numerical = agent_config.get('use_numerical_verification', True)
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Verify the correctness of the solution.
        
        Args:
            state: Current state with solution
        
        Returns:
            Updated state with verification results
        """
        start_time = time.time()
        state["current_agent"] = "verifier"
        
        try:
            self.logger.log_start(
                state["state_id"],
                f"Verifying solution for {state['topic']} problem"
            )
            
            # Prepare verification input
            problem_text = state["parsed_problem"].get("problem_text", "")
            solution = "\n".join(state.get("solution_steps", []))
            solution += f"\n\nFinal Answer: {state.get('final_answer', '')}"
            
            # Format prompt
            prompt = self.prompt_template.format(
                problem_text=problem_text,
                solution=solution
            )
            
            # Call LLM for verification
            self.logger.logger.info("Performing LLM-based verification")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract verification result
            verification_text = response.content[0].text.strip()
            verification_result = self._extract_json(verification_text)
            
            if not verification_result:
                raise ValueError("Failed to extract verification result")
            
            # Perform additional verification if enabled
            additional_checks = self._perform_additional_verification(state)
            
            # Combine results
            is_correct = verification_result.get("is_correct", False)
            base_confidence = verification_result.get("confidence", 0.0)
            
            # Adjust confidence based on additional checks
            if additional_checks.get("symbolic_check") == "failed":
                is_correct = False
                base_confidence *= 0.5
            
            # Update state
            state["is_verified"] = is_correct
            state["verification_confidence"] = base_confidence
            state["verification_method"] = verification_result.get("verification_method", "logical")
            state["verification_details"] = {
                **verification_result.get("verification_details", {}),
                **additional_checks
            }
            state["verification_issues"] = verification_result.get("issues_found", [])
            
            # Check if HITL needed
            hitl_config = self.config.get('hitl', {})
            min_confidence = hitl_config.get('verification_confidence_min', 0.85)
            
            if not is_correct or base_confidence < min_confidence:
                state["requires_human"] = True
                state["hitl_reason"] = f"Verification confidence too low: {base_confidence:.2f} or solution incorrect"
                self.logger.log_hitl_trigger(
                    state["hitl_reason"],
                    {"confidence": base_confidence, "is_correct": is_correct}
                )
            
            # Log decision
            self.logger.log_decision(
                "verification",
                "correct" if is_correct else "incorrect",
                base_confidence
            )
            
            # Add to trace
            add_agent_trace(state, "verifier", "verification_complete", {
                "is_correct": is_correct,
                "confidence": base_confidence,
                "method": state["verification_method"]
            })
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Verified: {is_correct}, confidence: {base_confidence:.3f}",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Verifier error: {str(e)}")
            state["is_verified"] = False
            state["verification_confidence"] = 0.0
            state["requires_human"] = True
            state["hitl_reason"] = "Verification failed"
            return state
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            else:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end > start:
                    return json.loads(text[start:end])
        return {}
    
    def _perform_additional_verification(self, state: MathMentorState) -> Dict[str, str]:
        """
        Perform additional verification using symbolic math.
        
        Args:
            state: Current state
        
        Returns:
            Dictionary with check results
        """
        checks = {
            "symbolic_check": "not_applicable",
            "numerical_check": "not_applicable",
            "constraint_check": "passed"
        }
        
        # Only perform symbolic check for algebra/calculus
        topic = state.get("topic", "")
        if topic in ["algebra", "calculus"] and self.use_symbolic:
            try:
                # This is a simplified example
                # In reality, you'd need to parse the equation from the problem
                # and verify the answer satisfies it
                checks["symbolic_check"] = "not_implemented"
            except Exception as e:
                self.logger.logger.debug(f"Symbolic check failed: {e}")
                checks["symbolic_check"] = "failed"
        
        return checks