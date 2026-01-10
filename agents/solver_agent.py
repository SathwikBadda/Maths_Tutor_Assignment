import time
from typing import Dict, Any, List
from anthropic import Anthropic

from orchestration.state import MathMentorState, add_agent_trace, add_error
from utils.logger import AgentLogger
from mathtools.calculator import Calculator
from mathtools.symbolic_math import SymbolicMathTool


class SolverAgent:
    """
    Solver Agent: Generates step-by-step solutions to math problems.
    Uses retrieved context and mathematical tools.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("solver", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        self.model = llm_config.get('model')
        self.temperature = llm_config.get('temperature', 0.1)
        self.max_tokens = llm_config.get('max_tokens', 4000)
        
        # Initialize tools
        self.calculator = Calculator()
        self.symbolic_math = SymbolicMathTool()
        
        # Agent config
        agent_config = config.get('agents', {}).get('solver', {})
        self.max_steps = agent_config.get('max_steps', 20)
        self.use_symbolic_math = agent_config.get('use_symbolic_math', True)
    
    def run(self, state: MathMentorState) -> MathMentorState:
        """
        Solve the mathematical problem step-by-step.
        
        Args:
            state: Current state with parsed problem and retrieved context
        
        Returns:
            Updated state with solution
        """
        start_time = time.time()
        state["current_agent"] = "solver"
        
        try:
            self.logger.log_start(
                state["state_id"],
                f"Solving problem: {state['topic']}/{state.get('subtopic', 'N/A')}"
            )
            
            # Prepare context
            problem_text = state["parsed_problem"].get("problem_text", "")
            retrieved_context = self._format_retrieved_context(state.get("retrieved_context", []))
            
            # Format prompt
            prompt = self.prompt_template.format(
                problem_text=problem_text,
                topic=state.get("topic", ""),
                retrieved_context=retrieved_context
            )
            
            # Call LLM to generate solution
            self.logger.logger.info("Generating solution with LLM")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract solution
            solution_text = response.content[0].text.strip()
            
            # Parse solution into steps
            solution_steps, final_answer = self._parse_solution(solution_text)
            
            # Update state
            state["solution_steps"] = solution_steps
            state["final_answer"] = final_answer
            state["tools_used"] = []  # Track if we used any tools
            
            # Log tools if used
            for tool_name, tool_data in []:  # Placeholder for actual tool usage tracking
                self.logger.log_tool_use(tool_name, tool_data.get("input", {}), tool_data.get("output", {}))
            
            # Add to trace
            add_agent_trace(state, "solver", "solution_generated", {
                "num_steps": len(solution_steps),
                "has_final_answer": bool(final_answer)
            })
            
            duration = time.time() - start_time
            self.logger.log_end(
                state["state_id"],
                f"Generated {len(solution_steps)} steps, answer: {final_answer[:50] if final_answer else 'N/A'}",
                duration
            )
            
            return state
        
        except Exception as e:
            self.logger.log_error(state["state_id"], e)
            add_error(state, f"Solver error: {str(e)}")
            return state
    
    def _format_retrieved_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents for the prompt."""
        if not retrieved_docs:
            return "No relevant context retrieved."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get("source", "unknown")
            content = doc.get("content", "")
            score = doc.get("similarity_score", 0.0)
            
            context_parts.append(
                f"[Context {i}] (Source: {source}, Relevance: {score:.2f})\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _parse_solution(self, solution_text: str) -> tuple[List[str], str]:
        """
        Parse solution text into steps and final answer.
        
        Args:
            solution_text: Raw solution from LLM
        
        Returns:
            Tuple of (steps, final_answer)
        """
        steps = []
        final_answer = ""
        
        # Split by common step markers
        lines = solution_text.split('\n')
        current_step = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a step header
            if line.startswith("**Step") or line.startswith("Step "):
                if current_step:
                    steps.append("\n".join(current_step))
                current_step = [line]
            elif line.startswith("**Final Answer"):
                if current_step:
                    steps.append("\n".join(current_step))
                current_step = []
                # Extract final answer
                if ":" in line:
                    final_answer = line.split(":", 1)[1].strip()
            else:
                current_step.append(line)
        
        # Add last step
        if current_step:
            if not final_answer:  # If no explicit final answer, last step might be it
                final_answer = "\n".join(current_step)
            else:
                steps.append("\n".join(current_step))
        
        return steps, final_answer