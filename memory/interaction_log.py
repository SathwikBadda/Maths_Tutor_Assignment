import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging


class InteractionLogger:
    """
    Logs individual interactions with detailed information.
    Separate from session storage for analytics purposes.
    """
    
    def __init__(self, log_path: str = "./memory/storage/interactions"):
        """
        Initialize interaction logger.
        
        Args:
            log_path: Path to store interaction logs
        """
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("interaction_logger")
        
        self.logger.info(f"Interaction logger initialized: {self.log_path}")
    
    def log_interaction(
        self,
        interaction_id: str,
        data: Dict[str, Any]
    ):
        """
        Log a single interaction.
        
        Args:
            interaction_id: Unique interaction identifier
            data: Interaction data
        """
        try:
            # Create daily log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = self.log_path / f"interactions_{date_str}.jsonl"
            
            # Prepare log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                **data
            }
            
            # Append to file (JSONL format)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            self.logger.debug(f"Logged interaction: {interaction_id}")
        
        except Exception as e:
            self.logger.error(f"Failed to log interaction: {e}", exc_info=True)
    
    def get_interactions_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Get all interactions for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
        
        Returns:
            List of interactions
        """
        log_file = self.log_path / f"interactions_{date_str}.jsonl"
        
        if not log_file.exists():
            return []
        
        interactions = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        interactions.append(json.loads(line))
        except Exception as e:
            self.logger.error(f"Failed to read interactions: {e}")
        
        return interactions
    
    def get_recent_interactions(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get N most recent interactions.
        
        Args:
            n: Number of interactions to retrieve
        
        Returns:
            List of recent interactions
        """
        # Get all log files sorted by date (newest first)
        log_files = sorted(
            self.log_path.glob("interactions_*.jsonl"),
            reverse=True
        )
        
        interactions = []
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Read from end of file
                    for line in reversed(lines):
                        if line.strip():
                            interactions.append(json.loads(line))
                            if len(interactions) >= n:
                                return interactions
            except Exception as e:
                self.logger.error(f"Failed to read {log_file}: {e}")
        
        return interactions
    
    def get_statistics(self, date_str: str = None) -> Dict[str, Any]:
        """
        Get statistics for interactions.
        
        Args:
            date_str: Optional date filter (YYYY-MM-DD)
        
        Returns:
            Statistics dictionary
        """
        if date_str:
            interactions = self.get_interactions_by_date(date_str)
        else:
            # Get all interactions from recent files
            interactions = self.get_recent_interactions(1000)
        
        if not interactions:
            return {
                "total_interactions": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "topics": {}
            }
        
        # Calculate statistics
        total = len(interactions)
        successful = sum(1 for i in interactions if i.get("workflow_status") == "completed")
        
        durations = [i.get("total_duration", 0) for i in interactions if i.get("total_duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Topic distribution
        topics = {}
        for i in interactions:
            topic = i.get("topic", "unknown")
            topics[topic] = topics.get(topic, 0) + 1
        
        return {
            "total_interactions": total,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration": avg_duration,
            "topics": topics,
            "date": date_str or "all"
        }