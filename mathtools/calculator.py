import math
import re
from typing import Dict, Any, Union


class Calculator:
    """
    MCP-style calculator tool for basic arithmetic operations.
    """
    
    TOOL_SCHEMA = {
        "name": "calculator",
        "description": "Performs basic arithmetic operations and evaluates mathematical expressions",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sin(pi/2)', 'sqrt(16)')"
                },
                "operation": {
                    "type": "string",
                    "enum": ["evaluate", "simplify"],
                    "description": "Operation to perform",
                    "default": "evaluate"
                }
            },
            "required": ["expression"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "result": {"type": "number"},
                "expression": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    }
    
    # Safe mathematical functions
    SAFE_FUNCTIONS = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'sqrt': math.sqrt,
        'abs': abs,
        'ceil': math.ceil,
        'floor': math.floor,
        'pow': pow,
        'pi': math.pi,
        'e': math.e,
    }
    
    def __init__(self):
        self.last_result = None
    
    def execute(self, expression: str, operation: str = "evaluate") -> Dict[str, Any]:
        """
        Execute a calculation.
        
        Args:
            expression: Mathematical expression to evaluate
            operation: Operation type (evaluate or simplify)
        
        Returns:
            Result dictionary with result, expression, or error
        """
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Replace common symbols
            expression = expression.replace('^', '**')
            expression = expression.replace('÷', '/')
            expression = expression.replace('×', '*')
            
            # Evaluate the expression safely
            result = self._safe_eval(expression)
            
            self.last_result = result
            
            return {
                "result": result,
                "expression": expression,
                "error": None
            }
        
        except ZeroDivisionError:
            return {
                "result": None,
                "expression": expression,
                "error": "Division by zero"
            }
        except ValueError as e:
            return {
                "result": None,
                "expression": expression,
                "error": f"Invalid value: {str(e)}"
            }
        except Exception as e:
            return {
                "result": None,
                "expression": expression,
                "error": f"Calculation error: {str(e)}"
            }
    
    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: Expression to evaluate
        
        Returns:
            Numerical result
        """
        # Create a safe namespace
        safe_dict = {"__builtins__": {}}
        safe_dict.update(self.SAFE_FUNCTIONS)
        
        # Evaluate the expression
        try:
            result = eval(expression, safe_dict)
            return float(result)
        except NameError as e:
            raise ValueError(f"Unknown function or variable: {e}")
    
    def batch_evaluate(self, expressions: list) -> list:
        """
        Evaluate multiple expressions.
        
        Args:
            expressions: List of expressions
        
        Returns:
            List of results
        """
        results = []
        for expr in expressions:
            results.append(self.execute(expr))
        return results
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the MCP tool schema."""
        return cls.TOOL_SCHEMA


# Example usage
if __name__ == "__main__":
    calc = Calculator()
    
    # Test cases
    test_expressions = [
        "2 + 2",
        "sqrt(16)",
        "sin(pi/2)",
        "log(e)",
        "2^3",
        "10 / 0",  # Should handle error
    ]
    
    for expr in test_expressions:
        result = calc.execute(expr)
        print(f"{expr} = {result}")