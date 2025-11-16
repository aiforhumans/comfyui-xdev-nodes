"""Prompt Tools for ComfyUI

A collection of utility nodes for working with text prompts.
"""

from .multiline_prompt import MultilinePromptBuilder
from .prompt_template import PromptTemplateSystem
from .random_prompt import RandomPromptSelector
from .style_injector import StyleTagsInjector
from .text_concatenate import TextConcatenate

NODE_CLASS_MAPPINGS = {
    "XDEVTextConcatenate": TextConcatenate,
    "XDEVMultilinePrompt": MultilinePromptBuilder,
    "XDEVStyleInjector": StyleTagsInjector,
    "XDEVRandomPrompt": RandomPromptSelector,
    "XDEVPromptTemplate": PromptTemplateSystem,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVTextConcatenate": "Text Concatenate",
    "XDEVMultilinePrompt": "Multi-line Prompt Builder",
    "XDEVStyleInjector": "Style Tags Injector",
    "XDEVRandomPrompt": "Random Prompt Selector",
    "XDEVPromptTemplate": "Prompt Template System",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
