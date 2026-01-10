import logging
import logging.handlers
import os
from pathlib import Path
import colorlog


def setup_logger(name: str, config: dict) -> logging.Logger:
    """
    Setup a logger with file and console handlers.
    
    Args:
        name: Logger name
        config: Logging configuration from config.yaml
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.get('level', 'INFO')))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    log_file = config.get('log_file', './logs/math_mentor.log')
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.get('max_bytes', 10485760),  # 10MB
        backupCount=config.get('backup_count', 5),
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


class AgentLogger:
    """
    Specialized logger for agent operations with structured logging.
    """
    
    def __init__(self, agent_name: str, config: dict):
        self.agent_name = agent_name
        self.logger = setup_logger(f"agent.{agent_name}", config)
    
    def log_start(self, state_id: str, input_summary: str):
        """Log agent start."""
        self.logger.info(f"[{self.agent_name}] START | State: {state_id} | Input: {input_summary}")
    
    def log_end(self, state_id: str, output_summary: str, duration: float):
        """Log agent completion."""
        self.logger.info(
            f"[{self.agent_name}] END | State: {state_id} | "
            f"Output: {output_summary} | Duration: {duration:.2f}s"
        )
    
    def log_error(self, state_id: str, error: Exception):
        """Log agent error."""
        self.logger.error(
            f"[{self.agent_name}] ERROR | State: {state_id} | "
            f"Error: {type(error).__name__}: {str(error)}",
            exc_info=True
        )
    
    def log_tool_use(self, tool_name: str, input_data: dict, output_data: dict):
        """Log tool usage."""
        self.logger.debug(
            f"[{self.agent_name}] TOOL | Tool: {tool_name} | "
            f"Input: {str(input_data)[:100]} | Output: {str(output_data)[:100]}"
        )
    
    def log_decision(self, decision_point: str, decision: str, confidence: float):
        """Log agent decision."""
        self.logger.info(
            f"[{self.agent_name}] DECISION | Point: {decision_point} | "
            f"Decision: {decision} | Confidence: {confidence:.3f}"
        )
    
    def log_hitl_trigger(self, reason: str, context: dict):
        """Log HITL trigger."""
        self.logger.warning(
            f"[{self.agent_name}] HITL_TRIGGER | Reason: {reason} | "
            f"Context: {str(context)[:200]}"
        )


def log_state_transition(logger: logging.Logger, from_agent: str, to_agent: str, state_id: str):
    """Log workflow state transition."""
    logger.info(f"WORKFLOW | Transition: {from_agent} -> {to_agent} | State: {state_id}")


def log_retrieval(logger: logging.Logger, query: str, num_results: int, top_score: float):
    """Log RAG retrieval."""
    logger.info(
        f"RAG | Query: {query[:50]}... | Results: {num_results} | "
        f"Top Score: {top_score:.3f}"
    )


def log_memory_operation(logger: logging.Logger, operation: str, session_id: str, details: str):
    """Log memory operations."""
    logger.info(f"MEMORY | Operation: {operation} | Session: {session_id} | {details}")