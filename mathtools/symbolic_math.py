import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Dict, Any, List, Union


class SymbolicMathTool:
    """
    MCP-style symbolic mathematics tool using SymPy.
    """
    
    TOOL_SCHEMA = {
        "name": "symbolic_solver",
        "description": "Solves equations symbolically, performs algebraic manipulation, calculus operations",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["solve", "simplify", "expand", "factor", "differentiate", "integrate", "limit"],
                    "description": "Mathematical operation to perform"
                },
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression or equation"
                },
                "variable": {
                    "type": "string",
                    "description": "Variable to solve for or differentiate with respect to",
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
        "output_schema": {
            "type": "object",
            "properties": {
                "result": {"type": ["string", "array"]},
                "latex": {"type": "string"},
                "verification": {"type": "boolean"},
                "error": {"type": "string"}
            }
        }
    }
    
    def __init__(self):
        self.transformations = standard_transformations + (implicit_multiplication_application,)
    
    def execute(
        self,
        operation: str,
        expression: str,
        variable: str = "x",
        domain: str = "real"
    ) -> Dict[str, Any]:
        """
        Execute a symbolic math operation.
        
        Args:
            operation: Type of operation (solve, simplify, etc.)
            expression: Mathematical expression
            variable: Variable name
            domain: Domain of the solution (real or complex)
        
        Returns:
            Result dictionary
        """
        try:
            # Parse the expression
            expr = self._parse_expression(expression)
            var = sp.Symbol(variable, real=(domain == "real"))
            
            # Execute the operation
            if operation == "solve":
                result = self._solve(expr, var, domain)
            elif operation == "simplify":
                result = sp.simplify(expr)
            elif operation == "expand":
                result = sp.expand(expr)
            elif operation == "factor":
                result = sp.factor(expr)
            elif operation == "differentiate":
                result = sp.diff(expr, var)
            elif operation == "integrate":
                result = sp.integrate(expr, var)
            elif operation == "limit":
                result = sp.limit(expr, var, 0)  # Default limit point
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Verify the result if it's a solution
            verification = self._verify_solution(expr, var, result) if operation == "solve" else True
            
            return {
                "result": self._format_result(result),
                "latex": sp.latex(result) if result is not None else "",
                "verification": verification,
                "error": None
            }
        
        except Exception as e:
            return {
                "result": None,
                "latex": "",
                "verification": False,
                "error": f"Symbolic math error: {str(e)}"
            }
    
    def _parse_expression(self, expression: str) -> sp.Expr:
        """Parse a string expression into a SymPy expression."""
        # Replace common notations
        expression = expression.replace('^', '**')
        expression = expression.replace('√', 'sqrt')
        
        try:
            return parse_expr(expression, transformations=self.transformations)
        except Exception as e:
            raise ValueError(f"Failed to parse expression: {str(e)}")
    
    def _solve(self, expr: sp.Expr, var: sp.Symbol, domain: str) -> List:
        """Solve an equation."""
        solutions = sp.solve(expr, var, domain=sp.S.Reals if domain == "real" else sp.S.Complexes)
        return solutions if isinstance(solutions, list) else [solutions]
    
    def _verify_solution(self, expr: sp.Expr, var: sp.Symbol, solutions: Any) -> bool:
        """Verify if solutions satisfy the equation."""
        if not solutions or not isinstance(solutions, list):
            return False
        
        try:
            for sol in solutions:
                if isinstance(sol, (sp.Expr, sp.Number)):
                    substituted = expr.subs(var, sol)
                    simplified = sp.simplify(substituted)
                    if simplified != 0:
                        return False
            return True
        except Exception:
            return False
    
    def _format_result(self, result: Any) -> Union[str, List[str]]:
        """Format result for output."""
        if result is None:
            return "No solution"
        elif isinstance(result, list):
            return [str(r) for r in result]
        else:
            return str(result)
    
    def solve_equation(self, equation: str, variable: str = "x") -> Dict[str, Any]:
        """Convenience method for solving equations."""
        return self.execute("solve", equation, variable)
    
    def differentiate(self, expression: str, variable: str = "x") -> Dict[str, Any]:
        """Convenience method for differentiation."""
        return self.execute("differentiate", expression, variable)
    
    def integrate(self, expression: str, variable: str = "x") -> Dict[str, Any]:
        """Convenience method for integration."""
        return self.execute("integrate", expression, variable)
    
    def simplify_expression(self, expression: str) -> Dict[str, Any]:
        """Convenience method for simplification."""
        return self.execute("simplify", expression)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the MCP tool schema."""
        return cls.TOOL_SCHEMA


# Example usage
if __name__ == "__main__":
    tool = SymbolicMathTool()
    
    # Test solve
    print("Solving x**2 - 4 = 0:")
    result = tool.solve_equation("x**2 - 4")
    print(result)
    
    # Test differentiate
    print("\nDifferentiating x**2 + 2*x:")
    result = tool.differentiate("x**2 + 2*x")
    print(result)
    
    # Test integrate
    print("\nIntegrating 2*x:")
    result = tool.integrate("2*x")
    print(result)