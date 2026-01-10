import yaml
from pathlib import Path
from typing import Dict, Any
import os


class ConfigLoader:
    """
    Loads and manages configuration from YAML files.
    """
    
    def __init__(self, config_path: str = "config.yaml", prompts_path: str = "prompts.yaml"):
        self.config_path = Path(config_path)
        self.prompts_path = Path(prompts_path)
        self._config = None
        self._prompts = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.yaml."""
        if self._config is None:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        return self._config
    
    def load_prompts(self) -> Dict[str, str]:
        """Load prompts from prompts.yaml."""
        if self._prompts is None:
            with open(self.prompts_path, 'r', encoding='utf-8') as f:
                self._prompts = yaml.safe_load(f)
        return self._prompts
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Example: config.get('llm.temperature') returns config['llm']['temperature']
        """
        config = self.load_config()
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_prompt(self, agent_name: str) -> str:
        """Get prompt template for a specific agent."""
        prompts = self.load_prompts()
        return prompts.get(agent_name, "")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        config = self.load_config()
        llm_config = config.get('llm', {})
        
        # Load API key from environment
        api_key_env = llm_config.get('api_key_env', 'ANTHROPIC_API_KEY')
        llm_config['api_key'] = os.getenv(api_key_env)
        
        return llm_config
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG configuration."""
        return self.load_config().get('rag', {})
    
    def get_hitl_config(self) -> Dict[str, Any]:
        """Get HITL configuration."""
        return self.load_config().get('hitl', {})
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        config = self.load_config()
        return config.get('agents', {}).get(agent_name, {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.load_config().get('logging', {})
    
    def is_topic_in_scope(self, topic: str) -> bool:
        """Check if a topic is within allowed scope."""
        config = self.load_config()
        allowed_topics = config.get('scope', {}).get('allowed_topics', [])
        return topic in allowed_topics
    
    def get_allowed_subtopics(self, topic: str) -> list:
        """Get allowed subtopics for a given topic."""
        config = self.load_config()
        subtopics = config.get('scope', {}).get('allowed_subtopics', {})
        return subtopics.get(topic, [])


# Global instance
_config_loader = None


def get_config_loader(config_path: str = "config.yaml", prompts_path: str = "prompts.yaml") -> ConfigLoader:
    """Get or create global config loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path, prompts_path)
    return _config_loader