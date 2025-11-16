"""Multi-line Prompt Builder Node

Builds complex prompts with subject, style, quality, and negative sections.
"""

from typing import Any, Dict, Tuple


class MultilinePromptBuilder:
    """Builds structured prompts with multiple sections."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "subject": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "style": ("STRING", {"default": "", "multiline": True}),
                "composition": ("STRING", {"default": "", "multiline": True}),
                "lighting": ("STRING", {"default": "", "multiline": True}),
                "quality": ("STRING", {"default": "masterpiece, best quality, high resolution", "multiline": True}),
                "negative": ("STRING", {"default": "low quality, blurry, distorted", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "build_prompt"
    CATEGORY = "🖥XDEV/Prompt tools"

    def build_prompt(
        self,
        subject: str,
        style: str = "",
        composition: str = "",
        lighting: str = "",
        quality: str = "",
        negative: str = ""
    ) -> Tuple[str, str]:
        """Build positive and negative prompts."""
        positive_parts = []
        
        if subject.strip():
            positive_parts.append(subject.strip())
        if style.strip():
            positive_parts.append(style.strip())
        if composition.strip():
            positive_parts.append(composition.strip())
        if lighting.strip():
            positive_parts.append(lighting.strip())
        if quality.strip():
            positive_parts.append(quality.strip())
        
        positive = ", ".join(positive_parts)
        negative_result = negative.strip() if negative.strip() else ""
        
        return (positive, negative_result)


__all__ = ["MultilinePromptBuilder"]
