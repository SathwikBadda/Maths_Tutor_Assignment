import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from orchestration.state import MathMentorState


class SessionManager:
    """
    Manages session memory and interaction history.
    Stores interactions as JSON files.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize session manager.
        
        Args:
            config: Memory configuration
        """
        self.config = config
        self.logger = logging.getLogger("session_manager")
        
        self.storage_path = Path(config.get('storage_path', './memory/storage/sessions'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.max_session_length = config.get('max_session_length', 50)
        self.retention_days = config.get('retention_days', 90)
        
        self.logger.info(f"Session manager initialized with storage: {self.storage_path}")
    
    def save_interaction(self, state: MathMentorState):
        """
        Save an interaction to persistent storage.
        
        Args:
            state: Completed interaction state
        """
        try:
            session_id = state.get("session_id", "unknown")
            interaction_id = state.get("interaction_id", "unknown")
            
            # Load existing session or create new
            session = self._load_session(session_id) or {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "interactions": []
            }
            
            # Add interaction
            interaction = {
                "interaction_id": interaction_id,
                "timestamp": state.get("timestamp", datetime.now().isoformat()),
                "input": {
                    "raw_input": state.get("raw_input", ""),
                    "input_type": state.get("input_type", "text")
                },
                "parsed_problem": state.get("parsed_problem", {}),
                "topic": state.get("topic", ""),
                "subtopic": state.get("subtopic", ""),
                "solution": {
                    "steps": state.get("solution_steps", []),
                    "final_answer": state.get("final_answer", "")
                },
                "verification": {
                    "is_verified": state.get("is_verified", False),
                    "confidence": state.get("verification_confidence", 0.0)
                },
                "retrieval": {
                    "num_docs": len(state.get("retrieved_context", [])),
                    "confidence": state.get("retrieval_confidence", 0.0),
                    "sources": state.get("retrieval_sources", [])
                },
                "workflow_status": state.get("workflow_status", "unknown"),
                "duration": state.get("total_duration", 0.0),
                "errors": state.get("errors", []),
                "user_feedback": {
                    "rating": state.get("user_feedback_rating"),
                    "text": state.get("user_feedback_text")
                }
            }
            
            session["interactions"].append(interaction)
            session["updated_at"] = datetime.now().isoformat()
            
            # Trim if too long
            if len(session["interactions"]) > self.max_session_length:
                session["interactions"] = session["interactions"][-self.max_session_length:]
            
            # Save session
            self._save_session(session)
            
            self.logger.info(
                f"Saved interaction {interaction_id} to session {session_id} "
                f"(total: {len(session['interactions'])} interactions)"
            )
        
        except Exception as e:
            self.logger.error(f"Failed to save interaction: {e}", exc_info=True)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data or None
        """
        return self._load_session(session_id)
    
    def get_recent_interactions(self, session_id: str, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent interactions for a session.
        
        Args:
            session_id: Session identifier
            n: Number of recent interactions
        
        Returns:
            List of recent interactions
        """
        session = self._load_session(session_id)
        if not session:
            return []
        
        return session.get("interactions", [])[-n:]
    
    def get_student_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get student context for personalization.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Student context summary
        """
        session = self._load_session(session_id)
        if not session:
            return {}
        
        interactions = session.get("interactions", [])
        
        # Analyze interactions
        topics = {}
        total_problems = len(interactions)
        verified_count = sum(1 for i in interactions if i.get("verification", {}).get("is_verified", False))
        
        for interaction in interactions:
            topic = interaction.get("topic", "unknown")
            topics[topic] = topics.get(topic, 0) + 1
        
        return {
            "total_problems_solved": total_problems,
            "success_rate": verified_count / total_problems if total_problems > 0 else 0,
            "favorite_topics": topics,
            "recent_topics": [i.get("topic") for i in interactions[-5:]]
        }
    
    def cleanup_old_sessions(self):
        """Remove sessions older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for session_file in self.storage_path.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session = json.load(f)
                    
                    created_at = datetime.fromisoformat(session.get("created_at", ""))
                    
                    if created_at < cutoff_date:
                        session_file.unlink()
                        self.logger.info(f"Deleted old session: {session_file.stem}")
                
                except Exception as e:
                    self.logger.error(f"Error processing session {session_file}: {e}")
        
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}", exc_info=True)
    
    def _load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from disk."""
        session_file = self.storage_path / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def _save_session(self, session: Dict[str, Any]):
        """Save session to disk."""
        session_id = session.get("session_id", "unknown")
        session_file = self.storage_path / f"{session_id}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save session {session_id}: {e}")
            raise