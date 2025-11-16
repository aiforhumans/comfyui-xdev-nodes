"""ASCII-friendly access to the 🖥XDEV ComfyUI nodes.

Exposes the same NODE_CLASS_MAPPINGS / NODE_DISPLAY_NAME_MAPPINGS
structure that ComfyUI expects while allowing tests and tooling to
import modules without dealing with emoji paths.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Tuple, Type

BASE_DIR = Path(__file__).resolve().parent.parent / "🖥XDEV"
PROMPT_TOOLS_PATH = BASE_DIR / "Prompt tools"
LM_STUDIO_PATH = BASE_DIR / "LM Studio"

NODE_CLASS_MAPPINGS: Dict[str, Type] = {}
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {}

# Keep track of direct symbol exports for IDE/Copilot friendliness
_EXPORTS: Dict[str, Type] = {}


def _ensure_path(path: Path) -> bool:
    if not path.exists():
        return False
    resolved = str(path)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)
    return True


def _load_prompt_tools() -> Tuple[Dict[str, Type], Dict[str, str]]:
    if not _ensure_path(PROMPT_TOOLS_PATH):
        return {}, {}

    from text_concatenate import TextConcatenate
    from multiline_prompt import MultilinePromptBuilder
    from style_injector import StyleTagsInjector
    from random_prompt import RandomPromptSelector
    from prompt_template import PromptTemplateSystem

    _EXPORTS.update({
        "TextConcatenate": TextConcatenate,
        "MultilinePromptBuilder": MultilinePromptBuilder,
        "StyleTagsInjector": StyleTagsInjector,
        "RandomPromptSelector": RandomPromptSelector,
        "PromptTemplateSystem": PromptTemplateSystem,
    })

    class_map = {
        "XDEVTextConcatenate": TextConcatenate,
        "XDEVMultilinePrompt": MultilinePromptBuilder,
        "XDEVStyleInjector": StyleTagsInjector,
        "XDEVRandomPrompt": RandomPromptSelector,
        "XDEVPromptTemplate": PromptTemplateSystem,
    }

    display_map = {
        "XDEVTextConcatenate": "Text Concatenate",
        "XDEVMultilinePrompt": "Multi-line Prompt Builder",
        "XDEVStyleInjector": "Style Tags Injector",
        "XDEVRandomPrompt": "Random Prompt Selector",
        "XDEVPromptTemplate": "Prompt Template System",
    }

    return class_map, display_map


def _load_lm_studio_nodes() -> Tuple[Dict[str, Type], Dict[str, str]]:
    if not _ensure_path(LM_STUDIO_PATH):
        return {}, {}

    from lm_text_gen import LMStudioTextGen
    from lm_vision import LMStudioVision
    from lm_prompt_enhancer import LMStudioPromptEnhancer
    from lm_streaming_text_gen import LMStudioStreamingTextGen
    from lm_batch_processor import LMStudioBatchProcessor
    from lm_model_selector import LMStudioModelSelector
    from lm_multi_model_selector import LMStudioMultiModelSelector
    from lm_model_unload_helper import LMStudioModelUnloadHelper
    from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger
    from lm_chat_history import LMStudioChatHistory, LMStudioChatHistoryLoader
    from lm_token_counter import LMStudioTokenCounter
    from lm_context_optimizer import LMStudioContextOptimizer
    from lm_response_validator import LMStudioResponseValidator
    from lm_parameter_presets import LMStudioParameterPresets
    from lm_sdxl_prompt_builder import LMStudioSDXLPromptBuilder
    from lm_persona_creator import LMStudioPersonaCreator
    from lm_prompt_mixer import LMStudioPromptMixer
    from lm_scene_composer import LMStudioSceneComposer
    from lm_aspect_ratio_optimizer import LMStudioAspectRatioOptimizer
    from lm_refiner_prompt_generator import LMStudioRefinerPromptGenerator
    from lm_controlnet_prompter import LMStudioControlNetPrompter
    from lm_regional_prompter import LMStudioRegionalPrompterHelper

    _EXPORTS.update({
        "LMStudioTextGen": LMStudioTextGen,
        "LMStudioVision": LMStudioVision,
        "LMStudioPromptEnhancer": LMStudioPromptEnhancer,
        "LMStudioStreamingTextGen": LMStudioStreamingTextGen,
        "LMStudioBatchProcessor": LMStudioBatchProcessor,
        "LMStudioModelSelector": LMStudioModelSelector,
        "LMStudioMultiModelSelector": LMStudioMultiModelSelector,
        "LMStudioModelUnloadHelper": LMStudioModelUnloadHelper,
        "LMStudioAutoUnloadTrigger": LMStudioAutoUnloadTrigger,
        "LMStudioChatHistory": LMStudioChatHistory,
        "LMStudioChatHistoryLoader": LMStudioChatHistoryLoader,
        "LMStudioTokenCounter": LMStudioTokenCounter,
        "LMStudioContextOptimizer": LMStudioContextOptimizer,
        "LMStudioResponseValidator": LMStudioResponseValidator,
        "LMStudioParameterPresets": LMStudioParameterPresets,
        "LMStudioSDXLPromptBuilder": LMStudioSDXLPromptBuilder,
        "LMStudioPersonaCreator": LMStudioPersonaCreator,
        "LMStudioPromptMixer": LMStudioPromptMixer,
        "LMStudioSceneComposer": LMStudioSceneComposer,
        "LMStudioAspectRatioOptimizer": LMStudioAspectRatioOptimizer,
        "LMStudioRefinerPromptGenerator": LMStudioRefinerPromptGenerator,
        "LMStudioControlNetPrompter": LMStudioControlNetPrompter,
        "LMStudioRegionalPrompterHelper": LMStudioRegionalPrompterHelper,
    })

    class_map = {
        "XDEVLMStudioText": LMStudioTextGen,
        "XDEVLMStudioVision": LMStudioVision,
        "XDEVLMStudioEnhancer": LMStudioPromptEnhancer,
        "XDEVLMStudioStreaming": LMStudioStreamingTextGen,
        "XDEVLMStudioBatch": LMStudioBatchProcessor,
        "XDEVLMStudioModelSelector": LMStudioModelSelector,
        "XDEVLMStudioMultiModel": LMStudioMultiModelSelector,
        "XDEVLMStudioUnloadHelper": LMStudioModelUnloadHelper,
        "XDEVLMStudioAutoUnload": LMStudioAutoUnloadTrigger,
        "XDEVLMStudioChatHistory": LMStudioChatHistory,
        "XDEVLMStudioChatLoader": LMStudioChatHistoryLoader,
        "XDEVLMStudioTokenCounter": LMStudioTokenCounter,
        "XDEVLMStudioContextOpt": LMStudioContextOptimizer,
        "XDEVLMStudioValidator": LMStudioResponseValidator,
        "XDEVLMStudioPresets": LMStudioParameterPresets,
        "XDEVLMStudioSDXLBuilder": LMStudioSDXLPromptBuilder,
        "XDEVLMStudioPersona": LMStudioPersonaCreator,
        "XDEVLMStudioPromptMixer": LMStudioPromptMixer,
        "XDEVLMStudioSceneComposer": LMStudioSceneComposer,
        "XDEVLMStudioAspectRatioOptimizer": LMStudioAspectRatioOptimizer,
        "XDEVLMStudioRefinerPromptGenerator": LMStudioRefinerPromptGenerator,
        "XDEVLMStudioControlNetPrompter": LMStudioControlNetPrompter,
        "XDEVLMStudioRegionalPrompterHelper": LMStudioRegionalPrompterHelper,
    }

    display_map = {
        "XDEVLMStudioText": "LM Studio Text Generator",
        "XDEVLMStudioVision": "LM Studio Vision (Image Analysis)",
        "XDEVLMStudioEnhancer": "LM Studio Prompt Enhancer",
        "XDEVLMStudioStreaming": "LM Studio Streaming Text Generator",
        "XDEVLMStudioBatch": "LM Studio Batch Processor",
        "XDEVLMStudioModelSelector": "LM Studio Model Selector",
        "XDEVLMStudioMultiModel": "LM Studio Multi-Model Selector",
        "XDEVLMStudioUnloadHelper": "LM Studio Model Unload Helper",
        "XDEVLMStudioAutoUnload": "LM Studio Auto Unload Trigger",
        "XDEVLMStudioChatHistory": "LM Studio Chat History Manager",
        "XDEVLMStudioChatLoader": "LM Studio Chat History Loader",
        "XDEVLMStudioTokenCounter": "LM Studio Token Counter",
        "XDEVLMStudioContextOpt": "LM Studio Context Optimizer",
        "XDEVLMStudioValidator": "LM Studio Response Validator",
        "XDEVLMStudioPresets": "LM Studio Parameter Presets",
        "XDEVLMStudioSDXLBuilder": "LM Studio SDXL Prompt Builder",
        "XDEVLMStudioPersona": "LM Studio Persona Creator",
        "XDEVLMStudioPromptMixer": "LM Studio Prompt Mixer",
        "XDEVLMStudioSceneComposer": "LM Studio Scene Composer",
        "XDEVLMStudioAspectRatioOptimizer": "LM Studio SDXL Aspect Ratio Optimizer",
        "XDEVLMStudioRefinerPromptGenerator": "LM Studio SDXL Refiner Prompt Generator",
        "XDEVLMStudioControlNetPrompter": "LM Studio ControlNet Prompter",
        "XDEVLMStudioRegionalPrompterHelper": "LM Studio Regional Prompter Helper",
    }

    return class_map, display_map


prompt_class_map, prompt_display_map = _load_prompt_tools()
lm_class_map, lm_display_map = _load_lm_studio_nodes()

NODE_CLASS_MAPPINGS.update(prompt_class_map)
NODE_CLASS_MAPPINGS.update(lm_class_map)
NODE_DISPLAY_NAME_MAPPINGS.update(prompt_display_map)
NODE_DISPLAY_NAME_MAPPINGS.update(lm_display_map)

globals().update(_EXPORTS)

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    *_EXPORTS.keys(),
]
