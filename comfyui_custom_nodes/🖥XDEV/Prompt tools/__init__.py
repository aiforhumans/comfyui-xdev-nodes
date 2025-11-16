"""Prompt Tools for ComfyUI

A collection of utility nodes for working with text prompts.
"""

from .text_concatenate import TextConcatenate
from .multiline_prompt import MultilinePromptBuilder
from .style_injector import StyleTagsInjector
from .random_prompt import RandomPromptSelector
from .prompt_template import PromptTemplateSystem

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
