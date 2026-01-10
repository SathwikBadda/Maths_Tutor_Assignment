import time
from typing import Dict, Any
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error
from utils.logger import AgentLogger


class ExplainerAgent:
    """
    Explainer Agent: Creates pedagogical explanations of solutions.
    Adapts to student's level and provides conceptual insights.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("explainer", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        self.model = llm_config.get('model')
        self.temperature = llm_config.get('temperature', 0.3)  # Slightly higher for explanations
        self.max_tokens = llm_config.get('max_tokens', 4000)
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Generate pedagogical explanation for the solution.
        
        Args:
            state: Current state with verified solution
        
        Returns:
            Updated state with explanation
        """
        start_time = time.time()
        state["current_agent"] = "explainer"
        
        try:
            self.logger.log_start(
                state["state_id"],
                f"Explaining solution for {state['topic']} problem"
            )
            
            # Prepare inputs
            problem_text = state["parsed_problem"].get("problem_text", "")
            solution = "\n".join(state.get("solution_steps", []))
            solution += f"\n\nFinal Answer: {state.get('final_answer', '')}"
            
            # Get student context (if available)
            student_context = self._get_student_context(state)
            
            # Format prompt
            prompt = self.prompt_template.format(
                problem_text=problem_text,
                solution=solution,
                student_context=student_context
            )
            
            # Call LLM for explanation
            self.logger.logger.info("Generating pedagogical explanation")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract explanation
            explanation = response.content[0].text.strip()
            
            # Parse explanation components
            key_concepts, common_pitfalls, related_topics = self._parse_explanation(explanation)
            
            # Update state
            state["explanation"] = explanation
            state["key_concepts"] = key_concepts
            state["common_pitfalls"] = common_pitfalls
            state["related_topics"] = related_topics
            
            # Add to trace
            add_agent_trace(state, "explainer", "explanation_generated", {
                "num_key_concepts": len(key_concepts),
                "num_pitfalls": len(common_pitfalls)
            })
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Explanation generated with {len(key_concepts)} concepts",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Explainer error: {str(e)}")
            # Provide basic explanation as fallback
            state["explanation"] = "Solution provided above."
            state["key_concepts"] = []
            state["common_pitfalls"] = []
            state["related_topics"] = []
            return state
    
    def _get_student_context(self, state: MathMentorState) -> str:
        """Get student context from memory if available."""
        # This would integrate with memory system
        # For now, provide basic context
        return f"Topic: {state.get('topic', 'N/A')}, Complexity: {state.get('complexity_score', 0.5)}"
    
    def _parse_explanation(self, explanation: str) -> tuple:
        """
        Parse explanation to extract structured components.
        
        Returns:
            Tuple of (key_concepts, common_pitfalls, related_topics)
        """
        key_concepts = []
        common_pitfalls = []
        related_topics = []
        
        lines = explanation.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if '**Key Concepts**' in line or 'Key Concepts:' in line:
                current_section = 'concepts'
            elif '**Common Pitfalls**' in line or 'Common Pitfalls:' in line:
                current_section = 'pitfalls'
            elif '**Related Topics**' in line or 'Related Topics:' in line:
                current_section = 'topics'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section == 'concepts':
                    key_concepts.append(item)
                elif current_section == 'pitfalls':
                    common_pitfalls.append(item)
                elif current_section == 'topics':
                    related_topics.append(item)
        
        return key_concepts, common_pitfalls, related_topics