"""Text Concatenate Node

Combines multiple text inputs with optional separator.
"""

from typing import Any, Dict, Tuple


class TextConcatenate:
    """Concatenates up to 5 text inputs with a separator."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "text1": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "text2": ("STRING", {"default": "", "multiline": True}),
                "text3": ("STRING", {"default": "", "multiline": True}),
                "text4": ("STRING", {"default": "", "multiline": True}),
                "text5": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": ", "}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "concatenate"
    CATEGORY = "🖥XDEV/Prompt tools"

    def concatenate(
        self, 
        text1: str,
        text2: str = "",
        text3: str = "",
        text4: str = "",
        text5: str = "",
        separator: str = ", "
    ) -> Tuple[str]:
        """Concatenate text inputs with separator."""
        texts = [t.strip() for t in [text1, text2, text3, text4, text5] if t.strip()]
        result = separator.join(texts)
        return (result,)


__all__ = ["TextConcatenate"]
