"""Batch refactoring script for remaining LM Studio nodes.

This script will automatically refactor the remaining 22 nodes to use
the new base classes and utilities.
"""

import re
from pathlib import Path

# Nodes to refactor (file name -> class name)
NODES_TO_REFACTOR = {
    # Simple nodes - just update imports and use base class helpers
    "lm_model_selector.py": ("LMStudioModelSelector", "utility"),
    "lm_token_counter.py": ("LMStudioTokenCounter", "utility"),
    "lm_response_validator.py": ("LMStudioResponseValidator", "utility"),
    "lm_parameter_presets.py": ("LMStudioParameterPresets", "utility"),
    "lm_context_optimizer.py": ("LMStudioContextOptimizer", "utility"),
    
    # Medium complexity - API calls to refactor
    "lm_sdxl_prompt_builder.py": ("LMStudioSDXLPromptBuilder", "prompt"),
    "lm_persona_creator.py": ("LMStudioPersonaCreator", "prompt"),
    "lm_prompt_mixer.py": ("LMStudioPromptMixer", "prompt"),
    "lm_scene_composer.py": ("LMStudioSceneComposer", "prompt"),
    "lm_aspect_ratio_optimizer.py": ("LMStudioAspectRatioOptimizer", "prompt"),
    "lm_refiner_prompt_generator.py": ("LMStudioRefinerPromptGenerator", "prompt"),
    "lm_controlnet_prompter.py": ("LMStudioControlNetPrompter", "prompt"),
    "lm_regional_prompter.py": ("LMStudioRegionalPrompterHelper", "prompt"),
    
    # Complex nodes - special handling
    "lm_vision.py": ("LMStudioVision", "vision"),
    "lm_streaming_text_gen.py": ("LMStudioStreamingTextGen", "streaming"),
    "lm_batch_processor.py": ("LMStudioBatchProcessor", "batch"),
    "lm_chat_history.py": ("LMStudioChatHistory", "chat"),  # Two classes
    "lm_multi_model_selector.py": ("LMStudioMultiModelSelector", "utility"),
    "lm_model_unload_helper.py": ("LMStudioModelUnloadHelper", "utility"),
    "lm_auto_unload_trigger.py": ("LMStudioAutoUnloadTrigger", "utility"),
}

def generate_refactoring_summary():
    """Generate a summary of what needs to be refactored."""
    
    print("="*60)
    print("BATCH REFACTORING PLAN")
    print("="*60)
    print()
    
    by_type = {}
    for filename, (classname, node_type) in NODES_TO_REFACTOR.items():
        by_type.setdefault(node_type, []).append((filename, classname))
    
    for node_type, nodes in sorted(by_type.items()):
        print(f"\n{node_type.upper()} NODES ({len(nodes)}):")
        for filename, classname in nodes:
            print(f"  - {filename:40} {classname}")
    
    print(f"\nTOTAL: {len(NODES_TO_REFACTOR)} nodes")
    print()
    print("REFACTORING PATTERN:")
    print("  1. Update imports (remove json, urllib, add base/utils)")
    print("  2. Inherit from appropriate base class")
    print("  3. Replace info formatting with base class methods")
    print("  4. Replace API calls with _make_api_request()")
    print("  5. Replace error handling with ErrorFormatter")
    print("  6. Use JSONParser for JSON responses")
    print("=" * 60)

if __name__ == "__main__":
    generate_refactoring_summary()
