"""
Validation utilities for input and data validation.
"""

import re
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger("validators")


def validate_problem_input(text: str) -> Tuple[bool, str]:
    """
    Validate problem input text.
    
    Args:
        text: Input text to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if empty
    if not text or not text.strip():
        return False, "Input cannot be empty"
    
    # Check minimum length
    if len(text.strip()) < 5:
        return False, "Input too short (minimum 5 characters)"
    
    # Check maximum length
    if len(text) > 10000:
        return False, "Input too long (maximum 10,000 characters)"
    
    # Check for suspicious patterns (basic security)
    suspicious_patterns = [
        r'<script>',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]
    
    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            return False, f"Suspicious content detected: {pattern}"
    
    return True, ""


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate JSON data against a schema.
    
    Args:
        data: Data to validate
        schema: JSON schema
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Check field types
        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get("type")
                actual_value = data[field]
                
                if expected_type == "string" and not isinstance(actual_value, str):
                    return False, f"Field '{field}' should be string, got {type(actual_value).__name__}"
                elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                    return False, f"Field '{field}' should be number, got {type(actual_value).__name__}"
                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    return False, f"Field '{field}' should be boolean, got {type(actual_value).__name__}"
                elif expected_type == "array" and not isinstance(actual_value, list):
                    return False, f"Field '{field}' should be array, got {type(actual_value).__name__}"
                elif expected_type == "object" and not isinstance(actual_value, dict):
                    return False, f"Field '{field}' should be object, got {type(actual_value).__name__}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_topic(topic: str, allowed_topics: list) -> Tuple[bool, str]:
    """
    Validate if a topic is in the allowed list.
    
    Args:
        topic: Topic to validate
        allowed_topics: List of allowed topics
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not topic:
        return False, "Topic cannot be empty"
    
    if topic not in allowed_topics:
        return False, f"Topic '{topic}' not in allowed topics: {', '.join(allowed_topics)}"
    
    return True, ""


def validate_confidence_score(score: float) -> Tuple[bool, str]:
    """
    Validate a confidence score.
    
    Args:
        score: Confidence score
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(score, (int, float)):
        return False, f"Confidence score must be a number, got {type(score).__name__}"
    
    if score < 0.0 or score > 1.0:
        return False, f"Confidence score must be between 0.0 and 1.0, got {score}"
    
    return True, ""


def sanitize_math_input(text: str) -> str:
    """
    Sanitize mathematical input text.
    Removes potentially harmful content while preserving math notation.
    
    Args:
        text: Input text
    
    Returns:
        Sanitized text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script/style content
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Preserve common math symbols
    # Don't remove: +, -, *, /, ^, =, <, >, (), [], {}, numbers, letters, whitespace
    
    return text.strip()


def validate_file_type(filename: str, allowed_extensions: list) -> Tuple[bool, str]:
    """
    Validate file type by extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['jpg', 'png'])
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"
    
    # Extract extension
    parts = filename.lower().split('.')
    if len(parts) < 2:
        return False, "File has no extension"
    
    extension = parts[-1]
    
    if extension not in [ext.lower() for ext in allowed_extensions]:
        return False, f"File type '.{extension}' not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    return True, ""


def validate_equation(equation: str) -> Tuple[bool, str]:
    """
    Basic validation for mathematical equations.
    
    Args:
        equation: Equation string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not equation or not equation.strip():
        return False, "Equation cannot be empty"
    
    # Check for balanced parentheses
    open_count = equation.count('(')
    close_count = equation.count(')')
    if open_count != close_count:
        return False, "Unbalanced parentheses"
    
    # Check for balanced brackets
    open_bracket = equation.count('[')
    close_bracket = equation.count(']')
    if open_bracket != close_bracket:
        return False, "Unbalanced brackets"
    
    # Check for balanced braces
    open_brace = equation.count('{')
    close_brace = equation.count('}')
    if open_brace != close_brace:
        return False, "Unbalanced braces"
    
    # Check for consecutive operators (basic check)
    consecutive_operators = re.search(r'[+\-*/]{3,}', equation)
    if consecutive_operators:
        return False, "Invalid consecutive operators"
    
    return True, ""