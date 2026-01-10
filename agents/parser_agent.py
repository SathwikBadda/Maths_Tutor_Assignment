import json
import time
from typing import Dict, Any
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error
from utils.logger import AgentLogger


class ParserAgent:
    """
    Parser Agent: Extracts structured information from raw input.
    Handles text, OCR output, and ASR transcripts.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("parser", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        self.model = llm_config.get('model', 'claude-sonnet-4-20250514')
        self.temperature = llm_config.get('temperature', 0.1)
        self.max_tokens = llm_config.get('max_tokens', 4000)
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Parse raw input into structured format.
        
        Args:
            state: Current state
        
        Returns:
            Updated state with parsed problem
        """
        start_time = time.time()
        state["current_agent"] = "parser"
        
        try:
            self.logger.log_start(
                state["state_id"],
                f"Input type: {state['input_type']}, length: {len(state['raw_input'])}"
            )
            
            # Prepare input text
            input_text = state["raw_input"]
            
            # Format prompt
            prompt = self.prompt_template.format(input_text=input_text)
            
            # Call LLM
            self.logger.logger.info(f"Calling LLM for parsing with model: {self.model}")
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
            self.logger.logger.debug(f"LLM response: {response_text[:200]}...")
            
            # Parse JSON response
            parsed_problem = self._extract_json(response_text)
            
            if not parsed_problem:
                raise ValueError("Failed to extract valid JSON from LLM response")
            
            # Update state
            state["parsed_problem"] = parsed_problem
            state["parsing_confidence"] = parsed_problem.get("confidence", 0.0)
            
            # Check if clarification needed
            if parsed_problem.get("needs_clarification", False):
                state["requires_human"] = True
                state["hitl_reason"] = f"Parser needs clarification: {parsed_problem.get('clarification_reason', 'Ambiguous problem')}"
                self.logger.log_hitl_trigger(
                    state["hitl_reason"],
                    {"confidence": state["parsing_confidence"]}
                )
            
            # Add to trace
            add_agent_trace(state, "parser", "parse_complete", {
                "topic": parsed_problem.get("topic", "unknown"),
                "confidence": state["parsing_confidence"],
                "needs_clarification": parsed_problem.get("needs_clarification", False)
            })
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Topic: {parsed_problem.get('topic', 'unknown')}, confidence: {state['parsing_confidence']:.3f}",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Parser error: {str(e)}")
            state["parsing_confidence"] = 0.0
            state["requires_human"] = True
            state["hitl_reason"] = f"Parser failed: {str(e)}"
            return state
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response.
        Handles cases where JSON is wrapped in markdown code blocks.
        """
        try:
            # Try direct parsing first
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract from code block
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
                # Try to find JSON object in text
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = text[start:end]
                    return json.loads(json_str)
        
        return {}
    
    def should_trigger_hitl(self, state: MathMentorState) -> bool:
        """Check if HITL should be triggered."""
        hitl_config = self.config.get('hitl', {})
        min_confidence = hitl_config.get('parsing_confidence_min', 0.8)
        
        return (
            state.get("parsing_confidence", 0.0) < min_confidence
            or state.get("parsed_problem", {}).get("needs_clarification", False)
        )