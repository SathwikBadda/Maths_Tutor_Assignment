import json
import time
from typing import Dict, Any
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error
from utils.logger import AgentLogger


class EvaluatorAgent:
    """
    Evaluator Agent: Assesses interaction quality and generates learning signals.
    Identifies areas for improvement and knowledge gaps.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("evaluator", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        self.model = llm_config.get('model')
        self.temperature = llm_config.get('temperature', 0.2)
        self.max_tokens = llm_config.get('max_tokens', 4000)
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Evaluate the quality of the complete interaction.
        
        Args:
            state: Current state with complete interaction
        
        Returns:
            Updated state with evaluation results
        """
        start_time = time.time()
        state["current_agent"] = "evaluator"
        
        try:
            self.logger.log_start(
                state["state_id"],
                "Evaluating interaction quality"
            )
            
            # Prepare interaction summary
            interaction_summary = self._create_interaction_summary(state)
            user_feedback = self._get_user_feedback(state)
            
            # Format prompt
            prompt = self.prompt_template.format(
                interaction_history=json.dumps(interaction_summary, indent=2),
                user_feedback=user_feedback
            )
            
            # Call LLM for evaluation
            self.logger.logger.info("Generating quality evaluation")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract evaluation
            evaluation_text = response.content[0].text.strip()
            evaluation_result = self._extract_json(evaluation_text)
            
            if not evaluation_result:
                raise ValueError("Failed to extract evaluation result")
            
            # Update state with evaluation metrics
            state["overall_quality_score"] = evaluation_result.get("overall_quality_score", 0.0)
            state["areas_for_improvement"] = evaluation_result.get("areas_for_improvement", [])
            
            # Add to trace
            add_agent_trace(state, "evaluator", "evaluation_complete", {
                "quality_score": state["overall_quality_score"],
                "num_improvements": len(state["areas_for_improvement"])
            })
            
            # Log evaluation results
            self.logger.logger.info(
                f"Quality evaluation: score={state['overall_quality_score']:.2f}, "
                f"improvements={len(state['areas_for_improvement'])}"
            )
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Quality score: {state['overall_quality_score']:.2f}",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Evaluator error: {str(e)}")
            state["overall_quality_score"] = 0.5  # Default neutral score
            state["areas_for_improvement"] = ["Evaluation failed"]
            return state
    
    def _create_interaction_summary(self, state: MathMentorState) -> Dict[str, Any]:
        """Create a summary of the interaction for evaluation."""
        return {
            "input": {
                "type": state.get("input_type", "text"),
                "problem": state.get("raw_input", "")[:200]
            },
            "parsing": {
                "topic": state.get("topic", ""),
                "complexity": state.get("complexity_score", 0.0),
                "confidence": state.get("parsing_confidence", 0.0)
            },
            "retrieval": {
                "num_docs": len(state.get("retrieved_context", [])),
                "confidence": state.get("retrieval_confidence", 0.0)
            },
            "solution": {
                "num_steps": len(state.get("solution_steps", [])),
                "has_answer": bool(state.get("final_answer", ""))
            },
            "verification": {
                "is_verified": state.get("is_verified", False),
                "confidence": state.get("verification_confidence", 0.0),
                "method": state.get("verification_method", "")
            },
            "workflow": {
                "status": state.get("workflow_status", ""),
                "duration": state.get("total_duration", 0.0),
                "errors": state.get("errors", []),
                "hitl_triggered": state.get("requires_human", False)
            }
        }
    
    def _get_user_feedback(self, state: MathMentorState) -> str:
        """Get user feedback if available."""
        rating = state.get("user_feedback_rating")
        text = state.get("user_feedback_text")
        
        if rating is not None:
            feedback = f"Rating: {rating}/5"
            if text:
                feedback += f"\nComments: {text}"
            return feedback
        
        return "No user feedback provided"
    
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