from typing import Dict, Any, Optional
import logging

from orchestration.state import MathMentorState


class HITLManager:
    """
    Human-in-the-Loop Manager.
    Handles decision points where human intervention is needed.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize HITL manager.
        
        Args:
            config: HITL configuration
        """
        self.config = config
        self.logger = logging.getLogger("hitl_manager")
        
        # Load thresholds
        self.ocr_confidence_min = config.get('ocr_confidence_min', 0.7)
        self.parsing_confidence_min = config.get('parsing_confidence_min', 0.8)
        self.verification_confidence_min = config.get('verification_confidence_min', 0.85)
        self.retrieval_confidence_min = config.get('retrieval_confidence_min', 0.6)
        
        self.logger.info(f"HITL Manager initialized with thresholds: OCR={self.ocr_confidence_min}, "
                        f"Parsing={self.parsing_confidence_min}, Verification={self.verification_confidence_min}")
    
    def should_trigger_hitl(self, state: MathMentorState) -> bool:
        """
        Determine if HITL should be triggered based on state.
        
        Args:
            state: Current workflow state
        
        Returns:
            True if HITL should be triggered
        """
        # Check if already triggered
        if state.get("requires_human", False) and not state.get("hitl_resolved", False):
            return True
        
        # Check OCR confidence (if image input)
        if state.get("input_type") == "image":
            ocr_confidence = state.get("input_metadata", {}).get("ocr_confidence", 1.0)
            if ocr_confidence < self.ocr_confidence_min:
                state["requires_human"] = True
                state["hitl_reason"] = f"OCR confidence too low: {ocr_confidence:.2f}"
                self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
                return True
        
        # Check parsing confidence
        parsing_confidence = state.get("parsing_confidence", 1.0)
        if parsing_confidence < self.parsing_confidence_min:
            state["requires_human"] = True
            state["hitl_reason"] = f"Parsing confidence too low: {parsing_confidence:.2f}"
            self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
            return True
        
        # Check if parser needs clarification
        if state.get("parsed_problem", {}).get("needs_clarification", False):
            state["requires_human"] = True
            state["hitl_reason"] = "Parser needs clarification"
            self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
            return True
        
        # Check retrieval confidence
        retrieval_confidence = state.get("retrieval_confidence", 1.0)
        if retrieval_confidence < self.retrieval_confidence_min:
            state["requires_human"] = True
            state["hitl_reason"] = f"Retrieval confidence too low: {retrieval_confidence:.2f}"
            self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
            return True
        
        # Check verification confidence
        verification_confidence = state.get("verification_confidence", 1.0)
        if verification_confidence < self.verification_confidence_min:
            state["requires_human"] = True
            state["hitl_reason"] = f"Verification confidence too low: {verification_confidence:.2f}"
            self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
            return True
        
        # Check if verification failed
        if not state.get("is_verified", True):
            state["requires_human"] = True
            state["hitl_reason"] = "Solution verification failed"
            self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
            return True
        
        # Check for errors
        if state.get("errors", []):
            state["requires_human"] = True
            state["hitl_reason"] = f"Errors occurred: {len(state['errors'])} error(s)"
            self.logger.warning(f"HITL triggered: {state['hitl_reason']}")
            return True
        
        return False
    
    def get_hitl_context(self, state: MathMentorState) -> Dict[str, Any]:
        """
        Get context information for HITL decision.
        
        Args:
            state: Current state
        
        Returns:
            HITL context dictionary
        """
        return {
            "reason": state.get("hitl_reason", "Unknown"),
            "problem": state.get("raw_input", "")[:200],
            "topic": state.get("topic", ""),
            "parsing_confidence": state.get("parsing_confidence", 0.0),
            "retrieval_confidence": state.get("retrieval_confidence", 0.0),
            "verification_confidence": state.get("verification_confidence", 0.0),
            "errors": state.get("errors", []),
            "current_solution": state.get("final_answer", "")[:200]
        }
    
    def resolve_hitl(
        self,
        state: MathMentorState,
        human_input: Optional[str] = None,
        action: str = "accept"
    ) -> MathMentorState:
        """
        Resolve HITL with human input.
        
        Args:
            state: Current state
            human_input: Optional feedback/correction from human
            action: Action to take (accept, reject, retry)
        
        Returns:
            Updated state
        """
        self.logger.info(f"Resolving HITL with action: {action}")
        
        state["hitl_resolved"] = True
        state["human_feedback"] = human_input
        
        if action == "accept":
            # Human accepts current state
            state["requires_human"] = False
            self.logger.info("HITL resolved: accepted")
        elif action == "reject":
            # Human rejects - mark as failed
            state["workflow_status"] = "failed"
            state["requires_human"] = False
            self.logger.info("HITL resolved: rejected")
        elif action == "retry":
            # Retry with human feedback
            if human_input:
                # Update the raw input with corrected version
                state["raw_input"] = human_input
                state["requires_human"] = False
                self.logger.info("HITL resolved: retrying with corrections")
        
        return state
    
    def format_hitl_message(self, state: MathMentorState) -> str:
        """
        Format a user-friendly HITL message.
        
        Args:
            state: Current state
        
        Returns:
            Formatted message for user
        """
        reason = state.get("hitl_reason", "Unknown reason")
        context = self.get_hitl_context(state)
        
        message = f"🔍 **Human Review Needed**\n\n"
        message += f"**Reason**: {reason}\n\n"
        
        if "confidence" in reason.lower():
            message += "The system has low confidence in this step. "
            message += "Please review the following:\n\n"
        
        if context.get("parsing_confidence", 1.0) < self.parsing_confidence_min:
            message += f"- Problem parsing confidence: {context['parsing_confidence']:.1%}\n"
        
        if context.get("retrieval_confidence", 1.0) < self.retrieval_confidence_min:
            message += f"- Context retrieval confidence: {context['retrieval_confidence']:.1%}\n"
        
        if context.get("verification_confidence", 1.0) < self.verification_confidence_min:
            message += f"- Solution verification confidence: {context['verification_confidence']:.1%}\n"
        
        if context.get("errors"):
            message += f"\n**Errors encountered**: {len(context['errors'])}\n"
            for error in context['errors'][:3]:  # Show first 3 errors
                message += f"- {error}\n"
        
        message += "\nPlease review the solution and provide feedback."
        
        return message