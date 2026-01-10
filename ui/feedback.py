"""
Feedback collection UI components.
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime


class FeedbackCollector:
    """
    Manages feedback collection from users.
    """
    
    def __init__(self):
        self.feedback_key = "user_feedback"
    
    def collect_rating(self, interaction_id: str) -> Optional[int]:
        """
        Collect a rating from the user.
        
        Args:
            interaction_id: Unique interaction identifier
        
        Returns:
            Rating (1-5) or None
        """
        col1, col2, col3, col4, col5 = st.columns(5)
        
        rating = None
        
        with col1:
            if st.button("⭐", key=f"rating_1_{interaction_id}"):
                rating = 1
        
        with col2:
            if st.button("⭐⭐", key=f"rating_2_{interaction_id}"):
                rating = 2
        
        with col3:
            if st.button("⭐⭐⭐", key=f"rating_3_{interaction_id}"):
                rating = 3
        
        with col4:
            if st.button("⭐⭐⭐⭐", key=f"rating_4_{interaction_id}"):
                rating = 4
        
        with col5:
            if st.button("⭐⭐⭐⭐⭐", key=f"rating_5_{interaction_id}"):
                rating = 5
        
        return rating
    
    def collect_feedback_form(self, interaction_id: str) -> Dict[str, Any]:
        """
        Display a comprehensive feedback form.
        
        Args:
            interaction_id: Unique interaction identifier
        
        Returns:
            Feedback dictionary
        """
        st.subheader("📝 Provide Feedback")
        
        with st.form(key=f"feedback_form_{interaction_id}"):
            # Rating
            rating = st.slider(
                "How helpful was this solution?",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Not helpful, 5 = Very helpful"
            )
            
            # Categories
            st.write("What aspects were helpful? (Select all that apply)")
            col1, col2 = st.columns(2)
            
            with col1:
                clarity = st.checkbox("Clear explanation")
                accuracy = st.checkbox("Accurate solution")
                completeness = st.checkbox("Complete steps")
            
            with col2:
                examples = st.checkbox("Good examples")
                concepts = st.checkbox("Concept explanation")
                presentation = st.checkbox("Well presented")
            
            # Issues
            st.write("Did you encounter any issues?")
            col1, col2 = st.columns(2)
            
            with col1:
                wrong_answer = st.checkbox("Incorrect answer")
                confusing = st.checkbox("Confusing explanation")
                incomplete = st.checkbox("Missing steps")
            
            with col2:
                slow = st.checkbox("Too slow")
                technical_error = st.checkbox("Technical error")
                other_issue = st.checkbox("Other issue")
            
            # Free text
            comments = st.text_area(
                "Additional comments (optional)",
                placeholder="Any other feedback or suggestions..."
            )
            
            # Submit
            submitted = st.form_submit_button("Submit Feedback")
            
            if submitted:
                feedback = {
                    "timestamp": datetime.now().isoformat(),
                    "interaction_id": interaction_id,
                    "rating": rating,
                    "helpful_aspects": {
                        "clarity": clarity,
                        "accuracy": accuracy,
                        "completeness": completeness,
                        "examples": examples,
                        "concepts": concepts,
                        "presentation": presentation
                    },
                    "issues": {
                        "wrong_answer": wrong_answer,
                        "confusing": confusing,
                        "incomplete": incomplete,
                        "slow": slow,
                        "technical_error": technical_error,
                        "other": other_issue
                    },
                    "comments": comments
                }
                
                st.success("✅ Thank you for your feedback!")
                return feedback
        
        return {}
    
    def display_quick_feedback(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Display quick thumbs up/down feedback.
        
        Args:
            interaction_id: Unique interaction identifier
        
        Returns:
            Feedback dictionary or None
        """
        st.markdown("### Was this helpful?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 Helpful", key=f"thumbs_up_{interaction_id}"):
                return {
                    "timestamp": datetime.now().isoformat(),
                    "interaction_id": interaction_id,
                    "rating": 5,
                    "type": "quick_positive"
                }
        
        with col2:
            if st.button("👎 Not Helpful", key=f"thumbs_down_{interaction_id}"):
                return {
                    "timestamp": datetime.now().isoformat(),
                    "interaction_id": interaction_id,
                    "rating": 1,
                    "type": "quick_negative"
                }
        
        return None


def collect_feedback(interaction_id: str, style: str = "quick") -> Optional[Dict[str, Any]]:
    """
    Collect user feedback.
    
    Args:
        interaction_id: Unique interaction identifier
        style: Feedback style ("quick", "detailed", "rating")
    
    Returns:
        Feedback dictionary or None
    """
    collector = FeedbackCollector()
    
    if style == "quick":
        return collector.display_quick_feedback(interaction_id)
    elif style == "detailed":
        return collector.collect_feedback_form(interaction_id)
    elif style == "rating":
        rating = collector.collect_rating(interaction_id)
        if rating:
            return {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                "rating": rating,
                "type": "rating_only"
            }
    
    return None


def display_feedback_summary(feedback_data: list):
    """
    Display a summary of collected feedback.
    
    Args:
        feedback_data: List of feedback dictionaries
    """
    if not feedback_data:
        st.info("No feedback collected yet")
        return
    
    st.subheader("📊 Feedback Summary")
    
    # Calculate metrics
    total_feedback = len(feedback_data)
    ratings = [f.get('rating', 0) for f in feedback_data if f.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Feedback", total_feedback)
    
    with col2:
        st.metric("Average Rating", f"{avg_rating:.1f}/5")
    
    with col3:
        positive = sum(1 for r in ratings if r >= 4)
        positive_pct = (positive / len(ratings) * 100) if ratings else 0
        st.metric("Positive Feedback", f"{positive_pct:.0f}%")
    
    # Rating distribution
    if ratings:
        st.write("**Rating Distribution:**")
        rating_counts = {i: ratings.count(i) for i in range(1, 6)}
        
        for rating, count in sorted(rating_counts.items(), reverse=True):
            stars = "⭐" * rating
            bar_length = int((count / max(rating_counts.values())) * 20)
            bar = "█" * bar_length
            st.write(f"{stars} ({rating}): {bar} {count}")


def get_feedback_insights(feedback_data: list) -> Dict[str, Any]:
    """
    Generate insights from feedback data.
    
    Args:
        feedback_data: List of feedback dictionaries
    
    Returns:
        Insights dictionary
    """
    if not feedback_data:
        return {}
    
    # Common issues
    issues = []
    for feedback in feedback_data:
        if 'issues' in feedback:
            for issue, has_issue in feedback['issues'].items():
                if has_issue:
                    issues.append(issue)
    
    # Most common issue
    issue_counts = {issue: issues.count(issue) for issue in set(issues)}
    
    return {
        "total_feedback": len(feedback_data),
        "avg_rating": sum(f.get('rating', 0) for f in feedback_data) / len(feedback_data),
        "common_issues": issue_counts,
        "has_comments": sum(1 for f in feedback_data if f.get('comments'))
    }