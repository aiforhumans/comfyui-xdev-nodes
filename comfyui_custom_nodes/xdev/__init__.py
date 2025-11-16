"""ASCII-friendly access to the 🖥XDEV ComfyUI nodes.

Exposes the same NODE_CLASS_MAPPINGS / NODE_DISPLAY_NAME_MAPPINGS
structure that ComfyUI expects while allowing tests and tooling to
import modules without dealing with emoji paths.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple, Type

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


def _import_class(module_name: str, class_name: str) -> Type:
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def _load_prompt_tools() -> Tuple[Dict[str, Type], Dict[str, str]]:
    if not _ensure_path(PROMPT_TOOLS_PATH):
        return {}, {}

    definitions = [
        ("text_concatenate", "TextConcatenate", "XDEVTextConcatenate", "Text Concatenate"),
        ("multiline_prompt", "MultilinePromptBuilder", "XDEVMultilinePrompt", "Multi-line Prompt Builder"),
        ("style_injector", "StyleTagsInjector", "XDEVStyleInjector", "Style Tags Injector"),
        ("random_prompt", "RandomPromptSelector", "XDEVRandomPrompt", "Random Prompt Selector"),
        ("prompt_template", "PromptTemplateSystem", "XDEVPromptTemplate", "Prompt Template System"),
    ]

    class_map: Dict[str, Type] = {}
    display_map: Dict[str, str] = {}

    for module_name, class_name, mapping_key, display_name in definitions:
        cls = _import_class(module_name, class_name)
        _EXPORTS[class_name] = cls
        class_map[mapping_key] = cls
        display_map[mapping_key] = display_name

    return class_map, display_map


def _load_lm_studio_nodes() -> Tuple[Dict[str, Type], Dict[str, str]]:
    if not _ensure_path(LM_STUDIO_PATH):
        return {}, {}

    definitions = [
        ("lm_text_gen", "LMStudioTextGen", "XDEVLMStudioText", "LM Studio Text Generator"),
        ("lm_vision", "LMStudioVision", "XDEVLMStudioVision", "LM Studio Vision (Image Analysis)"),
        ("lm_prompt_enhancer", "LMStudioPromptEnhancer", "XDEVLMStudioEnhancer", "LM Studio Prompt Enhancer"),
        ("lm_streaming_text_gen", "LMStudioStreamingTextGen", "XDEVLMStudioStreaming", "LM Studio Streaming Text Generator"),
        ("lm_batch_processor", "LMStudioBatchProcessor", "XDEVLMStudioBatch", "LM Studio Batch Processor"),
        ("lm_model_selector", "LMStudioModelSelector", "XDEVLMStudioModelSelector", "LM Studio Model Selector"),
        ("lm_multi_model_selector", "LMStudioMultiModelSelector", "XDEVLMStudioMultiModel", "LM Studio Multi-Model Selector"),
        ("lm_model_unload_helper", "LMStudioModelUnloadHelper", "XDEVLMStudioUnloadHelper", "LM Studio Model Unload Helper"),
        ("lm_auto_unload_trigger", "LMStudioAutoUnloadTrigger", "XDEVLMStudioAutoUnload", "LM Studio Auto Unload Trigger"),
        ("lm_chat_history", "LMStudioChatHistory", "XDEVLMStudioChatHistory", "LM Studio Chat History Manager"),
        ("lm_chat_history", "LMStudioChatHistoryLoader", "XDEVLMStudioChatLoader", "LM Studio Chat History Loader"),
        ("lm_token_counter", "LMStudioTokenCounter", "XDEVLMStudioTokenCounter", "LM Studio Token Counter"),
        ("lm_context_optimizer", "LMStudioContextOptimizer", "XDEVLMStudioContextOpt", "LM Studio Context Optimizer"),
        ("lm_response_validator", "LMStudioResponseValidator", "XDEVLMStudioValidator", "LM Studio Response Validator"),
        ("lm_parameter_presets", "LMStudioParameterPresets", "XDEVLMStudioPresets", "LM Studio Parameter Presets"),
        ("lm_sdxl_prompt_builder", "LMStudioSDXLPromptBuilder", "XDEVLMStudioSDXLBuilder", "LM Studio SDXL Prompt Builder"),
        ("lm_persona_creator", "LMStudioPersonaCreator", "XDEVLMStudioPersona", "LM Studio Persona Creator"),
        ("lm_prompt_mixer", "LMStudioPromptMixer", "XDEVLMStudioPromptMixer", "LM Studio Prompt Mixer"),
        ("lm_scene_composer", "LMStudioSceneComposer", "XDEVLMStudioSceneComposer", "LM Studio Scene Composer"),
        ("lm_aspect_ratio_optimizer", "LMStudioAspectRatioOptimizer", "XDEVLMStudioAspectRatioOptimizer", "LM Studio SDXL Aspect Ratio Optimizer"),
        ("lm_refiner_prompt_generator", "LMStudioRefinerPromptGenerator", "XDEVLMStudioRefinerPromptGenerator", "LM Studio SDXL Refiner Prompt Generator"),
        ("lm_controlnet_prompter", "LMStudioControlNetPrompter", "XDEVLMStudioControlNetPrompter", "LM Studio ControlNet Prompter"),
        ("lm_regional_prompter", "LMStudioRegionalPrompterHelper", "XDEVLMStudioRegionalPrompterHelper", "LM Studio Regional Prompter Helper"),
    ]

    class_map: Dict[str, Type] = {}
    display_map: Dict[str, str] = {}

    for module_name, class_name, mapping_key, display_name in definitions:
        cls = _import_class(module_name, class_name)
        _EXPORTS[class_name] = cls
        class_map[mapping_key] = cls
        display_map[mapping_key] = display_name

    return class_map, display_map


prompt_class_map, prompt_display_map = _load_prompt_tools()
lm_class_map, lm_display_map = _load_lm_studio_nodes()

NODE_CLASS_MAPPINGS.update(prompt_class_map)
NODE_CLASS_MAPPINGS.update(lm_class_map)
NODE_DISPLAY_NAME_MAPPINGS.update(prompt_display_map)
NODE_DISPLAY_NAME_MAPPINGS.update(lm_display_map)

globals().update(_EXPORTS)

_export_names: Iterable[str] = _EXPORTS.keys()
__all__ = ("NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", *_export_names)
