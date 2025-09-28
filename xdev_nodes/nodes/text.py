from __future__ import annotations
from typing import Dict, Tuple, Any
from functools import lru_cache
from ..utils import fast_string_validation, efficient_data_analysis
from ..performance import performance_monitor, cached_operation, intern_string, PrecompiledPatterns
from ..mixins import TextProcessingNode, ValidationMixin
from ..categories import NodeCategories

class AppendSuffix:
    DISPLAY_NAME = "Append Suffix (XDev)"
    """
    Advanced text suffix appender with comprehensive validation and rich documentation.
    
    This node demonstrates XDev best practices including:
    - Rich tooltip documentation for all inputs
    - Comprehensive input validation with detailed error messages
    - Proper error handling and graceful degradation
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "The original text content to which the suffix will be appended. Supports multiline input for complex text operations. Leave empty to append suffix only."
                }),
                "suffix": ("STRING", {
                    "default": " - xdev",
                    "multiline": False,
                    "tooltip": "The suffix text to append to the original content. Common uses: timestamps, signatures, version tags, or decorative elements."
                }),
            },
            "optional": {
                "separator": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Optional separator character(s) to insert between text and suffix. Leave empty for direct concatenation.",
                    "lazy": True
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable comprehensive input validation with detailed error messages. Recommended for production workflows."
                }),
                "max_length": ("INT", {
                    "default": 1000,
                    "min": 10,
                    "max": 100000,
                    "step": 10,
                    "display": "slider",
                    "tooltip": "Maximum allowed length for the final processed text",
                    "lazy": True
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("processed_text", "total_length")
    FUNCTION = "run"
    CATEGORY = NodeCategories.TEXT
    DESCRIPTION = "Append suffix to text with comprehensive validation and rich documentation"
    
    # Example of experimental features - advanced text processing
    EXPERIMENTAL = True  # Mark as experimental to show this feature

    def run(self, text: str, suffix: str, separator: str = "", validate_input: bool = True, max_length: int = 1000) -> Tuple[str, int]:
        """
        Optimized text processing with efficient string operations and optional validation.
        """
        try:
            # Fast path validation when enabled
            if validate_input and not self._fast_validate(text, suffix, separator):
                validation_result = self._validate_inputs(text, suffix, separator)
                if not validation_result["valid"]:
                    error_msg = f"Input validation failed: {validation_result['error']}"
                    return (error_msg, len(error_msg))
            
            # Optimized string building - single operation when possible
            if separator:
                result = text + separator + suffix
            else:
                result = text + suffix
            
            # Check max length constraint
            if len(result) > max_length:
                result = result[:max_length]
                print(f"[XDev Warning] Text truncated to {max_length} characters")
            
            return (result, len(result))
            
        except Exception as e:
            error_msg = f"Error processing text: {str(e)}"
            return (error_msg, len(error_msg))
    
    def _fast_validate(self, text: str, suffix: str, separator: str) -> bool:
        """Fast validation for common cases - returns True if inputs are likely valid."""
        return (fast_string_validation(text, max_length=100000) and 
                fast_string_validation(suffix, max_length=10000) and 
                fast_string_validation(separator, max_length=100))
    
    def _validate_inputs(self, text: str, suffix: str, separator: str) -> Dict[str, Any]:
        """
        Comprehensive input validation with detailed error messages.
        
        Returns:
            Dict with 'valid' boolean and 'error' message if invalid
        """
        # Validate text input
        if not isinstance(text, str):
            return {
                "valid": False,
                "error": f"Text must be a string, got {type(text).__name__}. Convert input to string format."
            }
        
        # Validate suffix input
        if not isinstance(suffix, str):
            return {
                "valid": False,
                "error": f"Suffix must be a string, got {type(suffix).__name__}. Check suffix input type."
            }
        
        # Validate separator input
        if not isinstance(separator, str):
            return {
                "valid": False,
                "error": f"Separator must be a string, got {type(separator).__name__}. Use empty string for no separator."
            }
        
        # Check for reasonable length limits
        if len(text) > 100000:
            return {
                "valid": False,
                "error": f"Text too long ({len(text)} characters). Maximum supported length is 100,000 characters."
            }
        
        if len(suffix) > 10000:
            return {
                "valid": False,
                "error": f"Suffix too long ({len(suffix)} characters). Maximum supported length is 10,000 characters."
            }
        
        # All validations passed
        return {"valid": True, "error": None}
    
    @classmethod
    def IS_CHANGED(cls, text, suffix, separator="", validate_input=True):
        """
        ComfyUI caching mechanism - return a value that changes when inputs change.
        This helps ComfyUI determine when to re-execute the node.
        """
        return f"{text}_{suffix}_{separator}_{validate_input}"


class TextCase(TextProcessingNode):
    DISPLAY_NAME = "Text Case (XDev)"
    """
    Optimized Phase 1 Foundation Node: High-performance text case conversion.
    
    Enhanced with:
    - Advanced caching and performance monitoring
    - Modular validation mixins
    - String interning for memory efficiency
    - Precompiled pattern validation
    """

    # Precomputed case conversion methods for maximum performance
    _CASE_METHODS = {
        intern_string("lower"): lambda text: text.lower(),
        intern_string("upper"): lambda text: text.upper(), 
        intern_string("title"): lambda text: text.title(),
        intern_string("capitalize"): lambda text: text.capitalize(),
        intern_string("camel"): lambda text: text[0].lower() + text.title().replace(" ", "")[1:] if text else "",
        intern_string("pascal"): lambda text: text.title().replace(" ", ""),
        intern_string("snake"): lambda text: text.lower().replace(" ", "_"),
        intern_string("kebab"): lambda text: text.lower().replace(" ", "-"),
        intern_string("constant"): lambda text: text.upper().replace(" ", "_")
    }
    
    # Pre-interned strings for memory efficiency
    _CASE_TYPES = tuple(intern_string(key) for key in _CASE_METHODS.keys())
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {
                    "default": "Hello World",
                    "multiline": True,
                    "tooltip": "Text content to convert case for. Supports multiline text and preserves newlines."
                }),
                "case_type": (cls._CASE_TYPES, {
                    "default": "lower", 
                    "tooltip": "Case conversion method: lower, upper, title, capitalize, camel, pascal, snake, kebab, constant"
                }),
            },
            "optional": {
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable validation for safety. Disable for maximum performance in trusted workflows."
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("converted_text", "original_case", "conversion_info")
    FUNCTION = "convert_case"
    DESCRIPTION = "High-performance text case conversion with 9 case formats"

    def validate_all_inputs(self, text: str, case_type: str, **kwargs) -> Dict[str, Any]:
        """Optimized validation using precompiled patterns and mixins"""
        # Use mixin validation for string input
        text_validation = self.validate_string_input(text, "text", max_length=100000)
        if not text_validation["valid"]:
            return text_validation
        
        # Use precompiled pattern validation for case type
        case_validation = self.validate_choice(case_type, "case_type", "case_types")
        if not case_validation["valid"]:
            return case_validation
            
        return {"valid": True, "error": None}

    @performance_monitor("TextCase.convert_case")
    @cached_operation(ttl=300)  # Cache results for 5 minutes
    def convert_case(self, text: str, case_type: str, validate_input: bool = True) -> Tuple[str, str, str]:
        """
        High-performance text case conversion with caching and monitoring.
        
        Features:
        - Automatic performance monitoring
        - Result caching for repeated operations
        - Optimized string operations
        - Memory-efficient interning
        """
        # Fast path validation
        if validate_input:
            validation = self.validate_all_inputs(text, case_type)
            error_result = self._handle_validation_error(validation, ("", "", ""))
            if error_result:
                return error_result
        
        # Optimized original text analysis
        text_len = len(text)
        original_info = self._analyze_original_case(text, text_len)
        
        # Apply case conversion using precomputed method - O(1) lookup
        converted_text = self._CASE_METHODS[intern_string(case_type)](text)
        
        # Generate conversion metadata efficiently
        conversion_info = intern_string(f"Converted to {case_type}: {len(converted_text)} chars " +
                                      ("(changed)" if text != converted_text else "(unchanged)"))
        
        return (converted_text, original_info, conversion_info)
    
    @lru_cache(maxsize=128)
    def _analyze_original_case(self, text: str, text_len: int) -> str:
        """Cached original text case analysis"""
        if text.isupper():
            return intern_string(f"Original: {text_len} chars, all uppercase")
        elif text.islower():
            return intern_string(f"Original: {text_len} chars, all lowercase") 
        elif text.istitle():
            return intern_string(f"Original: {text_len} chars, title case")
        else:
            return intern_string(f"Original: {text_len} chars, mixed case")

    @classmethod 
    def IS_CHANGED(cls, text, case_type, validate_input=True):
        """
        ComfyUI caching mechanism for case conversion.
        """
        return f"{text}_{case_type}_{validate_input}"