"""ComfyUI Custom Node Package

This package contains custom nodes for ComfyUI.
Place this entire folder into ComfyUI/custom_nodes/
"""

# Import from Prompt tools and LM Studio
import sys
from pathlib import Path

# Add current directory to path for proper imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Import from the prompt tools package
prompt_tools_path = current_dir / "🖥XDEV" / "Prompt tools"
if prompt_tools_path.exists():
    sys.path.insert(0, str(prompt_tools_path))
    from text_concatenate import TextConcatenate
    from multiline_prompt import MultilinePromptBuilder
    from style_injector import StyleTagsInjector
    from random_prompt import RandomPromptSelector
    from prompt_template import PromptTemplateSystem
    
    NODE_CLASS_MAPPINGS.update({
        "XDEVTextConcatenate": TextConcatenate,
        "XDEVMultilinePrompt": MultilinePromptBuilder,
        "XDEVStyleInjector": StyleTagsInjector,
        "XDEVRandomPrompt": RandomPromptSelector,
        "XDEVPromptTemplate": PromptTemplateSystem,
    })
    
    NODE_DISPLAY_NAME_MAPPINGS.update({
        "XDEVTextConcatenate": "Text Concatenate",
        "XDEVMultilinePrompt": "Multi-line Prompt Builder",
        "XDEVStyleInjector": "Style Tags Injector",
        "XDEVRandomPrompt": "Random Prompt Selector",
        "XDEVPromptTemplate": "Prompt Template System",
    })

# Import from LM Studio package
lm_studio_path = current_dir / "🖥XDEV" / "LM Studio"
if lm_studio_path.exists():
    sys.path.insert(0, str(lm_studio_path))
    
    # Import all nodes from LM Studio package
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
    
    # New creative generation nodes
    from lm_prompt_mixer import LMStudioPromptMixer
    from lm_scene_composer import LMStudioSceneComposer
    
    # New SDXL-specific nodes
    from lm_aspect_ratio_optimizer import LMStudioAspectRatioOptimizer
    from lm_refiner_prompt_generator import LMStudioRefinerPromptGenerator
    
    # New technical integration nodes
    from lm_controlnet_prompter import LMStudioControlNetPrompter
    from lm_regional_prompter import LMStudioRegionalPrompterHelper
    
    NODE_CLASS_MAPPINGS.update({
        # Core generation
        "XDEVLMStudioText": LMStudioTextGen,
        "XDEVLMStudioVision": LMStudioVision,
        "XDEVLMStudioEnhancer": LMStudioPromptEnhancer,
        
        # Advanced generation
        "XDEVLMStudioStreaming": LMStudioStreamingTextGen,
        "XDEVLMStudioBatch": LMStudioBatchProcessor,
        
        # Utility
        "XDEVLMStudioModelSelector": LMStudioModelSelector,
        "XDEVLMStudioMultiModel": LMStudioMultiModelSelector,
        "XDEVLMStudioUnloadHelper": LMStudioModelUnloadHelper,
        "XDEVLMStudioAutoUnload": LMStudioAutoUnloadTrigger,
        
        # Context management
        "XDEVLMStudioChatHistory": LMStudioChatHistory,
        "XDEVLMStudioChatLoader": LMStudioChatHistoryLoader,
        "XDEVLMStudioTokenCounter": LMStudioTokenCounter,
        "XDEVLMStudioContextOpt": LMStudioContextOptimizer,
        
        # Validation and control
        "XDEVLMStudioValidator": LMStudioResponseValidator,
        "XDEVLMStudioPresets": LMStudioParameterPresets,
        
        # SDXL and persona
        "XDEVLMStudioSDXLBuilder": LMStudioSDXLPromptBuilder,
        "XDEVLMStudioPersona": LMStudioPersonaCreator,
        
        # Creative generation
        "XDEVLMStudioPromptMixer": LMStudioPromptMixer,
        "XDEVLMStudioSceneComposer": LMStudioSceneComposer,
        
        # SDXL-specific
        "XDEVLMStudioAspectRatioOptimizer": LMStudioAspectRatioOptimizer,
        "XDEVLMStudioRefinerPromptGenerator": LMStudioRefinerPromptGenerator,
        
        # Technical integration
        "XDEVLMStudioControlNetPrompter": LMStudioControlNetPrompter,
        "XDEVLMStudioRegionalPrompterHelper": LMStudioRegionalPrompterHelper,
    })
    
    NODE_DISPLAY_NAME_MAPPINGS.update({
        # Core generation
        "XDEVLMStudioText": "LM Studio Text Generator",
        "XDEVLMStudioVision": "LM Studio Vision (Image Analysis)",
        "XDEVLMStudioEnhancer": "LM Studio Prompt Enhancer",
        
        # Advanced generation
        "XDEVLMStudioStreaming": "LM Studio Streaming Text Generator",
        "XDEVLMStudioBatch": "LM Studio Batch Processor",
        
        # Utility
        "XDEVLMStudioModelSelector": "LM Studio Model Selector",
        "XDEVLMStudioMultiModel": "LM Studio Multi-Model Selector",
        "XDEVLMStudioUnloadHelper": "LM Studio Model Unload Helper",
        "XDEVLMStudioAutoUnload": "LM Studio Auto Unload Trigger",
        
        # Context management
        "XDEVLMStudioChatHistory": "LM Studio Chat History Manager",
        "XDEVLMStudioChatLoader": "LM Studio Chat History Loader",
        "XDEVLMStudioTokenCounter": "LM Studio Token Counter",
        "XDEVLMStudioContextOpt": "LM Studio Context Optimizer",
        
        # Validation and control
        "XDEVLMStudioValidator": "LM Studio Response Validator",
        "XDEVLMStudioPresets": "LM Studio Parameter Presets",
        
        # SDXL and persona
        "XDEVLMStudioSDXLBuilder": "LM Studio SDXL Prompt Builder",
        "XDEVLMStudioPersona": "LM Studio Persona Creator",
        
        # Creative generation
        "XDEVLMStudioPromptMixer": "LM Studio Prompt Mixer",
        "XDEVLMStudioSceneComposer": "LM Studio Scene Composer",
        
        # SDXL-specific
        "XDEVLMStudioAspectRatioOptimizer": "LM Studio SDXL Aspect Ratio Optimizer",
        "XDEVLMStudioRefinerPromptGenerator": "LM Studio SDXL Refiner Prompt Generator",
        
        # Technical integration
        "XDEVLMStudioControlNetPrompter": "LM Studio ControlNet Prompter",
        "XDEVLMStudioRegionalPrompterHelper": "LM Studio Regional Prompter Helper",
    })

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
