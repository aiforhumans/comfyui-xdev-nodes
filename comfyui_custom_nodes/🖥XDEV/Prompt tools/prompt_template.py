"""Prompt Template System Node

Template-based prompt generation with variable substitution.
"""

from typing import Any, Dict, Tuple
import re


class PromptTemplateSystem:
    """Template system with variable substitution."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "template": ("STRING", {
                    "default": "A {adjective} {subject} in {location}, {style}",
                    "multiline": True
                }),
            },
            "optional": {
                "var_1": ("STRING", {"default": ""}),
                "var_2": ("STRING", {"default": ""}),
                "var_3": ("STRING", {"default": ""}),
                "var_4": ("STRING", {"default": ""}),
                "var_5": ("STRING", {"default": ""}),
                "var_6": ("STRING", {"default": ""}),
                "var_7": ("STRING", {"default": ""}),
                "var_8": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "apply_template"
    CATEGORY = "🖥XDEV/Prompt tools"

    def apply_template(
        self,
        template: str,
        var_1: str = "",
        var_2: str = "",
        var_3: str = "",
        var_4: str = "",
        var_5: str = "",
        var_6: str = "",
        var_7: str = "",
        var_8: str = ""
    ) -> Tuple[str]:
        """Apply template with variable substitution."""
        result = template
        
        # Find all {variable} patterns in template
        variables = re.findall(r'\{(\w+)\}', template)
        
        # Build variable mapping
        var_map = {
            f"var_{i+1}": var for i, var in enumerate([
                var_1, var_2, var_3, var_4, var_5, var_6, var_7, var_8
            ])
        }
        
        # Auto-assign vars to template variables in order
        for i, var_name in enumerate(variables):
            if i < len([var_1, var_2, var_3, var_4, var_5, var_6, var_7, var_8]):
                var_value = [var_1, var_2, var_3, var_4, var_5, var_6, var_7, var_8][i]
                if var_value:
                    result = result.replace(f"{{{var_name}}}", var_value)
        
        # Also support direct {var_1} style replacement
        for key, value in var_map.items():
            if value:
                result = result.replace(f"{{{key}}}", value)
        
        # Clean up any unreplaced variables
        result = re.sub(r'\{[^}]+\}', '', result)
        
        # Clean up extra spaces and commas
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r',\s*,', ',', result)
        result = result.strip(' ,')
        
        return (result,)


__all__ = ["PromptTemplateSystem"]
