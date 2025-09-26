from __future__ import annotations
from typing import Dict, Tuple, Any

class AppendSuffix:
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
                    "tooltip": "Optional separator character(s) to insert between text and suffix. Leave empty for direct concatenation."
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable comprehensive input validation with detailed error messages. Recommended for production workflows."
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("processed_text", "total_length")
    FUNCTION = "run"
    CATEGORY = "XDev/Text"
    DESCRIPTION = "Append suffix to text with comprehensive validation and rich documentation"

    def run(self, text: str, suffix: str, separator: str = "", validate_input: bool = True) -> Tuple[str, int]:
        """
        Process text by appending suffix with optional validation and separator.
        
        Args:
            text: Input text content
            suffix: Suffix to append
            separator: Optional separator between text and suffix
            validate_input: Enable input validation
            
        Returns:
            Tuple of (processed_text, total_length)
        """
        try:
            # Comprehensive input validation
            if validate_input:
                validation_result = self._validate_inputs(text, suffix, separator)
                if not validation_result["valid"]:
                    error_msg = f"Input validation failed: {validation_result['error']}"
                    return (error_msg, len(error_msg))
            
            # Process the text
            if separator:
                result = f"{text}{separator}{suffix}"
            else:
                result = f"{text}{suffix}"
            
            return (result, len(result))
            
        except Exception as e:
            error_msg = f"Error processing text: {str(e)}"
            return (error_msg, len(error_msg))
    
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