import time
from typing import Dict, Any
from anthropic import Anthropic
from utils.logger import AgentLogger

class MathNormalizerAgent:
    """
    Math Normalizer Agent: Converts natural language math descriptions to standard notation.
    """
    
    def __init__(self, config: Dict[str, Any], prompt_template: str):
        self.config = config
        self.prompt_template = prompt_template
        self.logger = AgentLogger("math_normalizer", config.get('logging', {}))
        
        # Initialize Anthropic client
        llm_config = config.get('llm', {})
        self.client = Anthropic(api_key=llm_config.get('api_key'))
        # Use a faster/cheaper model for normalization if possible, or default to config
        self.model = llm_config.get('model', 'claude-3-haiku-20240307')
        self.temperature = 0.0 # Deterministic output preferred
        self.max_tokens = 1000
    
    def normalize(self, text: str) -> str:
        """
        Normalize the input text.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Normalized mathematical text
        """
        start_time = time.time()
        
        try:
            self.logger.logger.info(f"Normalizing text: {text}")
            
            # Format prompt
            prompt = self.prompt_template.format(input_text=text)
            
            # Call LLM
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response
            normalized_text = response.content[0].text.strip()
            
            duration = time.time() - start_time
            self.logger.logger.info(f"Normalization complete. Output: {normalized_text} (Time: {duration:.2f}s)")
            
            return normalized_text
            
        except Exception as e:
            self.logger.log_error("normalization_error", e)
            # Fallback to original text on error
            return text
