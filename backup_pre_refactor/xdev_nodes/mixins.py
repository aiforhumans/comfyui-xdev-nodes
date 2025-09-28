"""
Validation mixins and base classes for XDev nodes.
Provides standardized validation patterns and reduces code duplication.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union, Type
from .performance import PrecompiledPatterns, fast_type_check, intern_string, CompactDict, performance_monitor

class ValidationMixin:
    """Base validation mixin providing common validation methods"""
    
    @staticmethod
    def validate_string_input(value: Any, param_name: str, max_length: int = 100000, allow_empty: bool = True) -> Dict[str, Any]:
        """Standardized string validation with detailed error reporting"""
        if not isinstance(value, str):
            return {
                "valid": False,
                "error": f"{param_name} must be a string, got {type(value).__name__}"
            }
        
        if not allow_empty and not value.strip():
            return {
                "valid": False,
                "error": f"{param_name} cannot be empty"
            }
            
        if len(value) > max_length:
            return {
                "valid": False,
                "error": f"{param_name} too long ({len(value)} chars), maximum is {max_length}"
            }
            
        return {"valid": True, "error": None}
    
    @staticmethod  
    def validate_numeric_input(value: Any, param_name: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Dict[str, Any]:
        """Standardized numeric validation"""
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            return {
                "valid": False,
                "error": f"{param_name} must be a number, got {type(value).__name__}"
            }
            
        if min_val is not None and num_value < min_val:
            return {
                "valid": False,
                "error": f"{param_name} must be >= {min_val}, got {num_value}"
            }
            
        if max_val is not None and num_value > max_val:
            return {
                "valid": False,
                "error": f"{param_name} must be <= {max_val}, got {num_value}"
            }
            
        return {"valid": True, "error": None}
    
    @staticmethod
    def validate_choice(value: str, param_name: str, valid_choices: Union[List[str], str]) -> Dict[str, Any]:
        """Validate choice against predefined options"""
        if isinstance(valid_choices, str):
            # Use precompiled pattern
            if not PrecompiledPatterns.validate_pattern(value, valid_choices):
                pattern_choices = PrecompiledPatterns.VALIDATION_PATTERNS.get(valid_choices, set())
                return {
                    "valid": False,
                    "error": f"{param_name} must be one of: {', '.join(sorted(pattern_choices))}"
                }
        else:
            # Use provided list
            if value not in valid_choices:
                return {
                    "valid": False,
                    "error": f"{param_name} must be one of: {', '.join(valid_choices)}"
                }
                
        return {"valid": True, "error": None}

class CachingMixin:
    """Mixin providing caching capabilities for node operations"""
    
    def __init__(self):
        self._cache = CompactDict()
        self._cache_keys = set()
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return intern_string(f"{self.__class__.__name__}:{'|'.join(key_parts)}")
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get result from cache if available"""
        return self._cache.get(cache_key)
    
    def _set_cached_result(self, cache_key: str, result: Any, max_cache_size: int = 100) -> None:
        """Cache result with size management"""
        if len(self._cache) >= max_cache_size:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self._cache_keys), None)
            if oldest_key:
                self._cache.pop(oldest_key, None)
                self._cache_keys.discard(oldest_key)
        
        self._cache[cache_key] = result
        self._cache_keys.add(cache_key)

class ErrorHandlingMixin:
    """Mixin providing standardized error handling patterns"""
    
    def _handle_validation_error(self, validation_result: Dict[str, Any], default_return: Tuple) -> Optional[Tuple]:
        """Handle validation errors with consistent error format"""
        if not validation_result["valid"]:
            error_msg = f"Validation Error: {validation_result['error']}"
            # Return error in same format as successful result
            if len(default_return) == 2:
                return (error_msg, "validation_failed")
            elif len(default_return) == 3:
                return (error_msg, "validation_failed", "error")
            else:
                return (error_msg,) + ("error",) * (len(default_return) - 1)
        return None
    
    def _safe_execute(self, operation_func, *args, error_prefix: str = "Operation failed", **kwargs) -> Tuple[bool, Any]:
        """Safely execute operation with error handling"""
        try:
            result = operation_func(*args, **kwargs)
            return True, result
        except Exception as e:
            error_msg = f"{error_prefix}: {str(e)}"
            return False, error_msg

class BaseXDevNode(ValidationMixin, CachingMixin, ErrorHandlingMixin, ABC):
    """Abstract base class for XDev nodes with common patterns"""
    
    @abstractmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        """Define input types - must be implemented by subclasses"""
        pass
    
    # ComfyUI expects these as class attributes, not properties
    RETURN_TYPES = ("STRING",)  # Default, should be overridden
    RETURN_NAMES = ("output",)  # Default, should be overridden  
    FUNCTION = "execute"        # Default, should be overridden
    CATEGORY = "XDev/Base"      # Default category
    DESCRIPTION = "XDev base node"  # Default description
    
    def validate_all_inputs(self, **kwargs) -> Dict[str, Any]:
        """Validate all inputs using defined validation rules"""
        # Override in subclasses to define specific validation
        return {"valid": True, "error": None}
    
    def get_processing_info(self, **kwargs) -> str:
        """Generate processing information metadata"""
        info_parts = [f"Node: {self.__class__.__name__}"]
        for key, value in kwargs.items():
            if isinstance(value, (str, int, float, bool)):
                info_parts.append(f"{key}={value}")
        return intern_string(", ".join(info_parts))

class TextProcessingNode(BaseXDevNode):
    """Base class for text processing nodes"""
    
    CATEGORY = "XDev/Text"
    
    def validate_text_inputs(self, text: str, **kwargs) -> Dict[str, Any]:
        """Common text validation"""
        validation = self.validate_string_input(text, "text", allow_empty=kwargs.get('allow_empty', True))
        if not validation["valid"]:
            return validation
        return self.validate_all_inputs(**kwargs)

class MathProcessingNode(BaseXDevNode):
    """Base class for mathematical operation nodes"""
    
    CATEGORY = "XDev/Math"
    
    def validate_numeric_inputs(self, **kwargs) -> Dict[str, Any]:
        """Common numeric validation"""
        for key, value in kwargs.items():
            if key.startswith(('a', 'b', 'x', 'y', 'value', 'number')):
                validation = self.validate_numeric_input(value, key)
                if not validation["valid"]:
                    return validation
        return self.validate_all_inputs(**kwargs)

class ImageProcessingNode(BaseXDevNode):
    """Base class for image processing nodes"""
    
    CATEGORY = "XDev/Image"
    
    def validate_image_inputs(self, image: Any, **kwargs) -> Dict[str, Any]:
        """Common image validation"""
        # Check if it's a tensor-like object
        if not hasattr(image, 'shape'):
            return {
                "valid": False,
                "error": "Image input must be a tensor with shape attribute"
            }
        
        # Validate image tensor shape [B,H,W,C]
        if len(image.shape) != 4:
            return {
                "valid": False,
                "error": f"Image must have 4 dimensions [B,H,W,C], got {len(image.shape)}"
            }
            
        return self.validate_all_inputs(**kwargs)

# Factory function for creating optimized node classes
def create_optimized_node(base_class: Type[BaseXDevNode], **class_attributes) -> Type[BaseXDevNode]:
    """Factory to create optimized node classes with performance monitoring"""
    
    class OptimizedNode(base_class):
        pass
    
    # Add class attributes
    for attr_name, attr_value in class_attributes.items():
        setattr(OptimizedNode, attr_name, attr_value)
    
    # Wrap main function with performance monitoring
    if hasattr(OptimizedNode, 'FUNCTION'):
        func_name = OptimizedNode.FUNCTION
        if hasattr(OptimizedNode, func_name):
            original_func = getattr(OptimizedNode, func_name)
            monitored_func = performance_monitor(f"{OptimizedNode.__name__}.{func_name}")(original_func)
            setattr(OptimizedNode, func_name, monitored_func)
    
    return OptimizedNode