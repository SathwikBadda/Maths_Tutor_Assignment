"""
MCP-style tool registry for managing and discovering tools.
"""

from typing import Dict, Any, Optional, Callable
import logging


# Global tool registry
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger("tool_registry")


def register_tool(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    output_schema: Dict[str, Any],
    execute_fn: Callable
):
    """
    Register a new tool in the registry.
    
    Args:
        name: Tool name
        description: Tool description
        input_schema: JSON schema for input
        output_schema: JSON schema for output
        execute_fn: Function to execute the tool
    """
    TOOL_REGISTRY[name] = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "execute": execute_fn
    }
    logger.info(f"Registered tool: {name}")


def get_tool(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a tool from the registry.
    
    Args:
        name: Tool name
    
    Returns:
        Tool definition or None
    """
    ensure_tools_registered()
    return TOOL_REGISTRY.get(name)


def list_tools() -> list:
    """
    List all registered tools.
    
    Returns:
        List of tool names
    """
    ensure_tools_registered()
    return list(TOOL_REGISTRY.keys())


def get_tool_schema(name: str) -> Optional[Dict[str, Any]]:
    """
    Get the schema for a tool.
    
    Args:
        name: Tool name
    
    Returns:
        Tool schema or None
    """
    ensure_tools_registered()
    tool = TOOL_REGISTRY.get(name)
    if tool:
        return {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_schema"],
            "output_schema": tool["output_schema"]
        }
    return None


def execute_tool(name: str, **kwargs) -> Any:
    """
    Execute a tool with given parameters.
    
    Args:
        name: Tool name
        **kwargs: Tool parameters
    
    Returns:
        Tool output
    """
    ensure_tools_registered()
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        raise ValueError(f"Tool not found: {name}")
    
    logger.debug(f"Executing tool: {name} with params: {kwargs}")
    return tool["execute"](**kwargs)


# Pre-register standard tools
def _register_standard_tools():
    """Register standard mathematical tools."""
    
    # Calculator tool
    from .calculator import Calculator
    calc = Calculator()
    
    register_tool(
        name="calculator",
        description="Performs basic arithmetic operations and evaluates mathematical expressions",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate"
                },
                "operation": {
                    "type": "string",
                    "enum": ["evaluate", "simplify"],
                    "default": "evaluate"
                }
            },
            "required": ["expression"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": "number"},
                "expression": {"type": "string"},
                "error": {"type": "string"}
            }
        },
        execute_fn=lambda expression, operation="evaluate": calc.execute(expression, operation)
    )
    
    # Symbolic math tool
    from .symbolic_math import SymbolicMathTool
    sym_math = SymbolicMathTool()
    
    register_tool(
        name="symbolic_solver",
        description="Solves equations symbolically, performs algebraic manipulation, calculus operations",
        input_schema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["solve", "simplify", "expand", "factor", "differentiate", "integrate", "limit"]
                },
                "expression": {"type": "string"},
                "variable": {
                    "type": "string",
                    "default": "x"
                },
                "domain": {
                    "type": "string",
                    "enum": ["real", "complex"],
                    "default": "real"
                }
            },
            "required": ["operation", "expression"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "result": {"type": ["string", "array"]},
                "latex": {"type": "string"},
                "verification": {"type": "boolean"},
                "error": {"type": "string"}
            }
        },
        execute_fn=lambda operation, expression, variable="x", domain="real": 
            sym_math.execute(operation, expression, variable, domain)
    )
    
    logger.info("Standard tools registered")


# Lazy registration - called only when needed to avoid circular imports
# Tools will be registered on first use
_tools_registered = False

def ensure_tools_registered():
    """Ensure standard tools are registered."""
    global _tools_registered
    if not _tools_registered:
        _register_standard_tools()
        _tools_registered = True