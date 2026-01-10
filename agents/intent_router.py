import json
import time
from typing import Dict, Any
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error, add_warning
from utils.logger import AgentLogger


class IntentRouter:
    """
    Intent Router Agent: Classifies problem topic, complexity, and scope.
    Determines which specialized components to use.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("intent_router", config.get('logging', {}))
        
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
        Route the problem to appropriate topic and assess complexity.
        
        Args:
            state: Current state with parsed problem
        
        Returns:
            Updated state with routing information
        """
        start_time = time.time()
        state["current_agent"] = "intent_router"
        
        try:
            self.logger.log_start(
                state["state_id"],
                f"Routing problem: {state['parsed_problem'].get('topic', 'unknown')}"
            )
            
            # Format prompt
            prompt = self.prompt_template.format(
                parsed_problem=json.dumps(state["parsed_problem"], indent=2)
            )
            
            # Call LLM
            self.logger.logger.info("Calling LLM for intent classification")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response
            response_text = response.content[0].text.strip()
            routing_result = self._extract_json(response_text)
            
            if not routing_result:
                raise ValueError("Failed to extract valid routing information")
            
            # Update state
            state["topic"] = routing_result.get("topic", "unknown")
            state["subtopic"] = routing_result.get("subtopic", "")
            state["complexity_score"] = routing_result.get("complexity_score", 0.5)
            state["estimated_steps"] = routing_result.get("estimated_steps", 5)
            state["required_tools"] = routing_result.get("required_tools", [])
            state["in_scope"] = routing_result.get("in_scope", True)
            state["out_of_scope_reason"] = routing_result.get("out_of_scope_reason", "")
            
            # Check scope
            if not state["in_scope"] or state["topic"] not in self.allowed_topics:
                state["workflow_status"] = "failed"
                add_error(state, f"Problem out of scope: {state['out_of_scope_reason']}")
                self.logger.logger.warning(
                    f"Problem rejected - out of scope: {state['topic']}, "
                    f"reason: {state['out_of_scope_reason']}"
                )
            
            # Log decision
            self.logger.log_decision(
                "topic_classification",
                f"{state['topic']}/{state['subtopic']}",
                state["complexity_score"]
            )
            
            # Add to trace
            add_agent_trace(state, "intent_router", "routing_complete", {
                "topic": state["topic"],
                "subtopic": state["subtopic"],
                "complexity": state["complexity_score"],
                "in_scope": state["in_scope"]
            })
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Topic: {state['topic']}, complexity: {state['complexity_score']:.2f}",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Intent routing error: {str(e)}")
            state["in_scope"] = False
            state["workflow_status"] = "failed"
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