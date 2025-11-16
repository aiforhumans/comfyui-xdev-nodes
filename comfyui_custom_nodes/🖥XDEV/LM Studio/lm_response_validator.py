"""LM Studio Response Validator Node

Validates LLM outputs against schemas and retries on failure.
"""

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode

import json
import re
from typing import Any


class LMStudioResponseValidator(LMStudioUtilityBaseNode):
    """Validate LLM responses with automatic retry suggestions."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "response": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                "validation_type": (["json", "length", "contains", "regex", "none"], {"default": "none"}),
            },
            "optional": {
                "json_schema": ("STRING", {"default": '{"type": "object", "required": ["key"]}', "multiline": True, "tooltip": "JSON schema for validation"}),
                "min_length": ("INT", {"default": 10, "min": 0, "max": 10000}),
                "max_length": ("INT", {"default": 1000, "min": 0, "max": 10000}),
                "must_contain": ("STRING", {"default": "", "tooltip": "Text that must be present"}),
                "regex_pattern": ("STRING", {"default": "", "tooltip": "Regex pattern to match"}),
                "strict_mode": ("BOOLEAN", {"default": False, "tooltip": "Fail on validation error"}),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("validated_response", "is_valid", "validation_errors", "info")
    FUNCTION = "validate_response"

    @classmethod
    def VALIDATE_INPUTS(cls, response: str, validation_type: str, **kwargs) -> bool:
        """Custom input validation."""
        if not response and validation_type != "none":
            return "Response is required for validation"
        return True

    def validate_response(
        self,
        response: str,
        validation_type: str,
        json_schema: str = "",
        min_length: int = 10,
        max_length: int = 1000,
        must_contain: str = "",
        regex_pattern: str = "",
        strict_mode: bool = False
    ) -> tuple[str, bool, str, str]:
        """Validate response against specified criteria."""
        
        info_parts = self._init_info("Response Validator", "✓")
        info_parts.append(f"🔍 Type: {validation_type}")
        info_parts.append(f"⚠️ Strict Mode: {'ON' if strict_mode else 'OFF'}")
        
        errors = []
        is_valid = True
        
        # No validation requested
        if validation_type == "none":
            info_parts.append("✅ No validation (pass-through)")
            return (response, True, "", self._format_info(info_parts))
        
        # JSON validation
        if validation_type == "json":
            try:
                parsed = json.loads(response)
                info_parts.append("✅ Valid JSON")
                
                # Optional schema validation
                if json_schema.strip():
                    try:
                        schema = json.loads(json_schema)
                        # Basic schema validation (type and required fields)
                        if "type" in schema and schema["type"] == "object":
                            if "required" in schema:
                                missing = [k for k in schema["required"] if k not in parsed]
                                if missing:
                                    errors.append(f"Missing required fields: {', '.join(missing)}")
                                    is_valid = False
                                else:
                                    info_parts.append("✅ All required fields present")
                    except json.JSONDecodeError:
                        errors.append("Invalid JSON schema provided")
                        is_valid = False
                        
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON: {str(e)}")
                is_valid = False
        
        # Length validation
        elif validation_type == "length":
            length = len(response)
            info_parts.append(f"📊 Length: {length} chars")
            
            if length < min_length:
                errors.append(f"Too short: {length} < {min_length}")
                is_valid = False
            elif length > max_length:
                errors.append(f"Too long: {length} > {max_length}")
                is_valid = False
            else:
                info_parts.append(f"✅ Length OK ({min_length}-{max_length})")
        
        # Contains validation
        elif validation_type == "contains":
            if must_contain:
                if must_contain in response:
                    info_parts.append(f"✅ Contains: '{must_contain[:30]}...'")
                else:
                    errors.append(f"Missing required text: '{must_contain}'")
                    is_valid = False
            else:
                errors.append("No 'must_contain' text specified")
                is_valid = False
        
        # Regex validation
        elif validation_type == "regex":
            if regex_pattern:
                try:
                    if re.search(regex_pattern, response):
                        info_parts.append("✅ Regex match")
                    else:
                        errors.append(f"No regex match: '{regex_pattern}'")
                        is_valid = False
                except re.error as e:
                    errors.append(f"Invalid regex: {str(e)}")
                    is_valid = False
            else:
                errors.append("No regex pattern specified")
                is_valid = False
        
        # Build error message
        error_msg = "\n".join(errors) if errors else ""
        
        # Update info
        if is_valid:
            info_parts.append("✅ Validation passed")
        else:
            info_parts.append(f"❌ Validation failed ({len(errors)} error(s))")
            if strict_mode:
                info_parts.append("⚠️ Strict mode: Workflow may halt")
        
        # In strict mode, return error as response
        if not is_valid and strict_mode:
            return (error_msg, False, error_msg, self._format_info(info_parts))
        
        return (response, is_valid, error_msg, self._format_info(info_parts))


__all__ = ["LMStudioResponseValidator"]
