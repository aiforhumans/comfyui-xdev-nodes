from __future__ import annotations
from typing import Dict, Tuple, Any, Union, Optional
import operator
from functools import lru_cache
from ..utils import efficient_data_analysis
from ..performance import performance_monitor, cached_operation, intern_string, PrecompiledPatterns
from ..mixins import MathProcessingNode, ValidationMixin
from ..categories import NodeCategories

class MathBasic(MathProcessingNode):
    DISPLAY_NAME = "Math Basic (XDev)"
    """
    Optimized Phase 1 Foundation Node: High-performance mathematical operations.
    
    Enhanced with:
    - Advanced caching for repeated calculations
    - Performance monitoring and profiling
    - Memory-efficient string interning
    - Modular validation mixins
    """

    # Precomputed operation mapping with interned keys for memory efficiency
    _OPERATIONS = {
        intern_string("add"): operator.add,
        intern_string("subtract"): operator.sub,
        intern_string("multiply"): operator.mul,
        intern_string("divide"): operator.truediv,
        intern_string("modulo"): operator.mod,
        intern_string("power"): operator.pow,
        intern_string("floor_divide"): operator.floordiv
    }
    
    _OPERATION_SYMBOLS = {
        intern_string("add"): intern_string("+"),
        intern_string("subtract"): intern_string("-"), 
        intern_string("multiply"): intern_string("*"),
        intern_string("divide"): intern_string("/"),
        intern_string("modulo"): intern_string("%"),
        intern_string("power"): intern_string("^"),
        intern_string("floor_divide"): intern_string("//")
    }
    
    # Pre-interned operation names for performance
    _OPERATION_NAMES = tuple(intern_string(key) for key in _OPERATIONS.keys())

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "a": ("FLOAT", {
                    "default": 0.0,
                    "min": -999999.0,
                    "max": 999999.0,
                    "step": 0.01,
                    "display": "number",
                    "tooltip": "First number for the mathematical operation. Accepts both integers and decimal values."
                }),
                "b": ("FLOAT", {
                    "default": 1.0,
                    "min": -999999.0,
                    "max": 999999.0,
                    "step": 0.01,
                    "display": "number", 
                    "tooltip": "Second number for the mathematical operation. For division/modulo, cannot be zero."
                }),
                "operation": (cls._OPERATION_NAMES, {
                    "default": "add",
                    "tooltip": "Mathematical operation: add, subtract, multiply, divide, modulo, power, floor_divide"
                })
            },
            "optional": {
                "precision": ("INT", {
                    "default": 6,
                    "min": 0,
                    "max": 15,
                    "step": 1,
                    "tooltip": "Number of decimal places to round the result to. 0 for integer results."
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation including division by zero checks. Disable for performance in trusted workflows."
                })
            }
        }

    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("result", "result_int", "calculation_info")
    FUNCTION = "calculate"
    CATEGORY = NodeCategories.MATH
    DESCRIPTION = "Perform basic mathematical operations with precision control"

    def _validate_inputs(self, a: float, b: float, operation: str) -> Dict[str, Any]:
        """
        Comprehensive input validation for mathematical operations.
        """
        # Check if inputs are valid numbers
        try:
            float(a)
            float(b)
        except (TypeError, ValueError) as e:
            return {
                "valid": False,
                "error": f"Invalid number inputs: {str(e)}"
            }
        
        # Check operation validity
        if operation not in self._OPERATIONS:
            return {
                "valid": False,
                "error": f"Invalid operation '{operation}'. Must be one of: {', '.join(self._OPERATIONS.keys())}"
            }
        
        # Check for division by zero
        if operation in ["divide", "modulo", "floor_divide"] and b == 0:
            return {
                "valid": False,
                "error": f"Cannot {operation} by zero"
            }
        
        # Check for invalid power operations
        if operation == "power":
            if a == 0 and b < 0:
                return {
                    "valid": False,
                    "error": "Cannot raise zero to negative power"
                }
            if a < 0 and not float(b).is_integer():
                return {
                    "valid": False,
                    "error": "Cannot raise negative number to non-integer power"
                }
        
        return {"valid": True, "error": None}

    @performance_monitor("MathBasic.calculate")
    @cached_operation(ttl=600)  # Cache mathematical results for 10 minutes
    def calculate(self, a: float, b: float, operation: str, precision: int = 6, validate_input: bool = True) -> Tuple[float, int, str]:
        """
        High-performance mathematical calculation with caching and monitoring.
        
        Features:
        - Automatic performance monitoring and profiling
        - Result caching for repeated calculations
        - Optimized error handling with pre-interned strings
        - Memory-efficient operations
        """
        # Fast path validation using mixins
        if validate_input:
            validation = self.validate_numeric_inputs(a=a, b=b)
            if not validation["valid"]:
                error_result = self._handle_validation_error(validation, (0.0, 0, ""))
                return error_result or (0.0, 0, f"Validation Error: {validation['error']}")
            
            # Validate operation choice using precompiled patterns
            op_validation = self.validate_choice(operation, "operation", "math_operations")
            if not op_validation["valid"]:
                error_result = self._handle_validation_error(op_validation, (0.0, 0, ""))
                return error_result or (0.0, 0, f"Operation Error: {op_validation['error']}")
        
        # Check for mathematical edge cases efficiently
        error_check = self._check_mathematical_validity(a, b, operation)
        if error_check:
            return error_check
        
        # Perform calculation using precomputed operation - O(1) lookup
        interned_op = intern_string(operation)
        result = self._OPERATIONS[interned_op](a, b)
        
        # Handle precision efficiently
        if 0 <= precision < 15:
            result = round(result, precision)
        
        # Generate optimized calculation info
        info = self._generate_calculation_info(a, b, interned_op, result, precision)
        
        # Convert to int (truncated) 
        result_int = int(result)
        
        return (result, result_int, info)
    
    @lru_cache(maxsize=64)
    def _check_mathematical_validity(self, a: float, b: float, operation: str) -> Optional[Tuple[float, int, str]]:
        """Cached mathematical validity checking"""
        interned_op = intern_string(operation)
        
        # Division by zero check
        if interned_op in ("divide", "modulo", "floor_divide") and b == 0:
            symbol = self._OPERATION_SYMBOLS[interned_op]
            return (0.0, 0, intern_string(f"Error: Division by zero ({a} {symbol} {b})"))
        
        # Invalid power operations
        if interned_op == "power":
            if a == 0 and b < 0:
                return (0.0, 0, intern_string("Error: Cannot raise zero to negative power"))
            if a < 0 and not float(b).is_integer():
                return (0.0, 0, intern_string("Error: Cannot raise negative number to non-integer power"))
        
        return None
    
    @lru_cache(maxsize=128) 
    def _generate_calculation_info(self, a: float, b: float, operation: str, result: float, precision: int) -> str:
        """Cached calculation info generation"""
        symbol = self._OPERATION_SYMBOLS[operation]
        base_info = f"{a} {symbol} {b} = {result}"
        
        if 0 <= precision < 6:
            base_info += f" (rounded to {precision} decimals)"
        
        return intern_string(base_info)

    @classmethod
    def IS_CHANGED(cls, a, b, operation, precision=6, validate_input=True):
        """
        ComfyUI caching mechanism for mathematical operations.
        """
        return f"{a}_{b}_{operation}_{precision}_{validate_input}"