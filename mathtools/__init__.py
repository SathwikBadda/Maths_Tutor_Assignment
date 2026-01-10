"""
MCP-style tools for mathematical operations.
"""

# Use relative imports to avoid circular dependency issues
from mathtools import calculator
from mathtools import symbolic_math
from mathtools import ocr_processor
from mathtools import speech_to_text
from mathtools import tool_registry

# Export main classes and functions
Calculator = calculator.Calculator
SymbolicMathTool = symbolic_math.SymbolicMathTool
OCRProcessor = ocr_processor.OCRProcessor
SpeechToTextProcessor = speech_to_text.SpeechToTextProcessor
TOOL_REGISTRY = tool_registry.TOOL_REGISTRY
get_tool = tool_registry.get_tool
register_tool = tool_registry.register_tool

__all__ = [
    'Calculator',
    'SymbolicMathTool',
    'OCRProcessor',
    'SpeechToTextProcessor',
    'TOOL_REGISTRY',
    'get_tool',
    'register_tool',
]