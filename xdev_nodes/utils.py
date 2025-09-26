"""
Optimized utility functions for XDev nodes.
Contains performance-optimized common operations to reduce code duplication.
"""

from typing import Any, Dict, Optional, Union
import sys
from functools import lru_cache

# Cache for commonly used validation results
@lru_cache(maxsize=128)
def cached_type_check(obj_type: str, expected_type: str) -> bool:
    """Cached type checking for common validations"""
    return obj_type == expected_type

def fast_string_validation(text: str, max_length: int = 100000) -> bool:
    """Optimized string validation with early returns"""
    return isinstance(text, str) and len(text) <= max_length

def get_object_size(obj: Any) -> int:
    """Get approximate object size in bytes using sys.getsizeof"""
    try:
        return sys.getsizeof(obj)
    except (TypeError, AttributeError):
        return 0

def safe_json_serialize(obj: Any, max_length: int = 1000) -> str:
    """Safely serialize objects to JSON with length limits"""
    try:
        if hasattr(obj, 'tolist'):  # Handle numpy/torch arrays
            obj = obj.tolist()
        
        result = str(obj)
        if len(result) > max_length:
            result = result[:max_length] + "..."
        return result
    except Exception:
        return f"<{type(obj).__name__}>"

def efficient_data_analysis(data: Any, level: str = "basic") -> Dict[str, str]:
    """Optimized data analysis with minimal overhead"""
    obj_type = type(data).__name__
    
    # Basic level - minimal information
    if level == "basic":
        return {
            "type": obj_type,
            "size": str(get_object_size(data))
        }
    
    # Detailed level - add shape/device info if available  
    analysis = {"type": obj_type}
    
    if hasattr(data, 'shape'):
        analysis["shape"] = str(data.shape)
    elif hasattr(data, '__len__'):
        try:
            analysis["length"] = str(len(data))
        except (TypeError, AttributeError):
            pass
    
    if hasattr(data, 'device'):
        analysis["device"] = str(data.device)
    
    if hasattr(data, 'dtype'):
        analysis["dtype"] = str(data.dtype)
    
    # Full level - add content preview
    if level == "full":
        analysis["preview"] = safe_json_serialize(data, 200)
    
    return analysis

# Pre-compiled validation patterns for better performance
COMMON_VALIDATION_PATTERNS = {
    "mode_brightness": frozenset(["brightest", "darkest"]),
    "analysis_level": frozenset(["basic", "detailed", "full"]), 
    "format_style": frozenset(["simple", "formal", "casual", "technical"]),
    "algorithm": frozenset(["average", "weighted", "luminance"])
}

def validate_choice(value: str, pattern_name: str) -> bool:
    """Fast choice validation using pre-compiled patterns"""
    return value in COMMON_VALIDATION_PATTERNS.get(pattern_name, frozenset())

# Lazy import utilities
_torch_cache = None
_numpy_cache = None

def get_torch():
    """Lazy import torch with caching"""
    global _torch_cache
    if _torch_cache is None:
        try:
            import torch
            _torch_cache = torch
        except ImportError:
            _torch_cache = False
    return _torch_cache if _torch_cache is not False else None

def get_numpy():
    """Lazy import numpy with caching"""
    global _numpy_cache
    if _numpy_cache is None:
        try:
            import numpy as np
            _numpy_cache = np
        except ImportError:
            _numpy_cache = False
    return _numpy_cache if _numpy_cache is not False else None