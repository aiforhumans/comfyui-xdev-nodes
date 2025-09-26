from __future__ import annotations
from typing import Dict, Tuple, Any

class AppendSuffix:
    """Append a suffix to the input text."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": " - xdev"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "XDev/Text"

    def run(self, text: str, suffix: str) -> Tuple[str]:
        return (f"{text}{suffix}",)