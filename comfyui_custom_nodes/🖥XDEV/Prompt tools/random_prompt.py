"""Random Prompt Selector Node

Randomly selects from a list of prompts.
"""

import random
from typing import Any


class RandomPromptSelector:
    """Randomly selects one prompt from a list."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "prompts": ("STRING", {"default": "prompt 1\nprompt 2\nprompt 3", "multiline": True}),
                "delimiter": (["newline", "comma", "semicolon"], {"default": "newline"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "enable_random": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("selected_prompt", "index")
    FUNCTION = "select_random"
    CATEGORY = "🖥XDEV/Prompt tools"

    def select_random(
        self,
        prompts: str,
        delimiter: str = "newline",
        seed: int = 0,
        enable_random: bool = True
    ) -> tuple[str, int]:
        """Randomly select a prompt from the list."""
        # Parse prompts based on delimiter
        if delimiter == "newline":
            prompt_list = [p.strip() for p in prompts.split('\n') if p.strip()]
        elif delimiter == "comma":
            prompt_list = [p.strip() for p in prompts.split(',') if p.strip()]
        else:  # semicolon
            prompt_list = [p.strip() for p in prompts.split(';') if p.strip()]
        
        if not prompt_list:
            return ("", 0)
        
        if enable_random:
            random.seed(seed)
            index = random.randint(0, len(prompt_list) - 1)
        else:
            index = 0
        
        selected = prompt_list[index]
        return (selected, index)


__all__ = ["RandomPromptSelector"]
