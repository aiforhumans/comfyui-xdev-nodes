from __future__ import annotations
from typing import Dict, Tuple, Any
import datetime

class HelloString:
    """
    Enhanced greeting node demonstrating XDev best practices.
    
    This node showcases:
    - Rich tooltip documentation
    - Optional customization parameters
    - Comprehensive error handling
    - Dynamic content generation
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {},
            "optional": {
                "custom_message": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Optional custom message to append to the greeting. Leave empty to use default ComfyUI greeting."
                }),
                "include_timestamp": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Include current timestamp in the greeting message. Useful for debugging and workflow tracking."
                }),
                "format_style": (["simple", "formal", "casual", "technical"], {
                    "default": "simple",
                    "tooltip": "Choose greeting format style. Simple: basic message, Formal: professional tone, Casual: friendly tone, Technical: includes system info."
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("greeting", "metadata")
    FUNCTION = "hello"
    CATEGORY = "XDev/Basic"
    DESCRIPTION = "Enhanced greeting generator with customizable formatting and optional timestamp"

    def hello(self, custom_message: str = "", include_timestamp: bool = False, format_style: str = "simple") -> Tuple[str, str]:
        """
        Generate customized greeting message with optional enhancements.
        
        Args:
            custom_message: Optional custom text to append
            include_timestamp: Whether to include current timestamp
            format_style: Formatting style for the greeting
            
        Returns:
            Tuple of (greeting_message, metadata_info)
        """
        try:
            # Base greeting based on style
            if format_style == "formal":
                base_greeting = "Greetings from ComfyUI!"
            elif format_style == "casual":
                base_greeting = "Hey there from ComfyUI! 👋"
            elif format_style == "technical":
                base_greeting = "ComfyUI Node System: Status Active"
            else:  # simple
                base_greeting = "Hello ComfyUI!"
            
            # Add custom message if provided
            if custom_message.strip():
                greeting = f"{base_greeting} {custom_message.strip()}"
            else:
                greeting = base_greeting
            
            # Add timestamp if requested
            metadata = f"Format: {format_style}"
            if include_timestamp:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                greeting = f"{greeting} (Generated: {timestamp})"
                metadata += f", Timestamp: {timestamp}"
            
            return (greeting, metadata)
            
        except Exception as e:
            error_msg = f"Error generating greeting: {str(e)}"
            return (error_msg, f"Error: {str(e)}")
    
    @classmethod
    def IS_CHANGED(cls, custom_message="", include_timestamp=False, format_style="simple"):
        # Include timestamp in cache key when timestamp is enabled to ensure refresh
        if include_timestamp:
            return datetime.datetime.now().isoformat()
        return f"{custom_message}_{format_style}"


class AnyPassthrough:
    """
    Enhanced passthrough node demonstrating the ANY datatype with comprehensive validation.
    
    This node showcases:
    - ANY type handling with validation
    - Rich documentation and tooltips
    - Optional data transformation
    - Comprehensive error reporting
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "value": ("*", {
                    "tooltip": "Input value of any type to pass through unchanged. Supports all ComfyUI data types including IMAGE, STRING, INT, FLOAT, LATENT, etc."
                })
            },
            "optional": {
                "validate_data": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable data type validation and reporting. Provides detailed information about the passed data structure."
                }),
                "add_metadata": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Generate additional metadata about the passed data including type information and basic statistics."
                }),
            }
        }

    RETURN_TYPES = ("*", "STRING")
    RETURN_NAMES = ("passthrough_value", "data_info")
    FUNCTION = "do_it"
    CATEGORY = "XDev/Basic"
    DESCRIPTION = "Pass any data type unchanged with optional validation and metadata generation"

    def do_it(self, value, validate_data: bool = True, add_metadata: bool = False):
        """
        Pass through any value with optional validation and metadata.
        
        Args:
            value: Input value of any type
            validate_data: Enable validation reporting
            add_metadata: Generate detailed metadata
            
        Returns:
            Tuple of (original_value, data_information)
        """
        try:
            info_parts = []
            
            if validate_data:
                # Basic type information
                value_type = type(value).__name__
                info_parts.append(f"Type: {value_type}")
                
                # Type-specific information
                if hasattr(value, 'shape'):  # Tensor-like objects
                    info_parts.append(f"Shape: {value.shape}")
                elif hasattr(value, '__len__') and not isinstance(value, str):
                    info_parts.append(f"Length: {len(value)}")
                elif isinstance(value, (int, float)):
                    info_parts.append(f"Value: {value}")
                elif isinstance(value, str):
                    info_parts.append(f"Length: {len(value)} characters")
            
            if add_metadata:
                # Additional metadata
                info_parts.append(f"Module: {type(value).__module__}")
                if hasattr(value, 'dtype'):
                    info_parts.append(f"DType: {value.dtype}")
                if hasattr(value, 'device'):
                    info_parts.append(f"Device: {value.device}")
            
            # Compile information
            if info_parts:
                data_info = " | ".join(info_parts)
            else:
                data_info = "Passthrough: No validation requested"
            
            return (value, data_info)
            
        except Exception as e:
            error_info = f"Error during passthrough: {str(e)}"
            return (value, error_info)
    
    @classmethod
    def IS_CHANGED(cls, value, validate_data=True, add_metadata=False):
        # For caching, we need to be careful with the value
        # Use id() for object identity and basic properties
        try:
            cache_key = f"{id(value)}_{type(value).__name__}_{validate_data}_{add_metadata}"
            if hasattr(value, 'shape'):
                cache_key += f"_{value.shape}"
            return cache_key
        except:
            return f"unknown_{validate_data}_{add_metadata}"