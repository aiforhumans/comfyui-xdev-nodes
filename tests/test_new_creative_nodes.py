"""
Test suite for new LM Studio creative/SDXL/technical nodes

Tests the 6 new nodes:
- Prompt Mixer
- Scene Composer
- Aspect Ratio Optimizer
- Refiner Prompt Generator
- ControlNet Prompter
- Regional Prompter Helper
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "comfyui_custom_nodes" / "🖥XDEV" / "LM Studio"))

# Import nodes
from lm_prompt_mixer import LMStudioPromptMixer
from lm_scene_composer import LMStudioSceneComposer
from lm_aspect_ratio_optimizer import LMStudioAspectRatioOptimizer
from lm_refiner_prompt_generator import LMStudioRefinerPromptGenerator
from lm_controlnet_prompter import LMStudioControlNetPrompter
from lm_regional_prompter import LMStudioRegionalPrompterHelper


def test_imports():
    """Test that all nodes can be imported."""
    print("✅ All nodes imported successfully")


def test_prompt_mixer_structure():
    """Test Prompt Mixer node structure."""
    node = LMStudioPromptMixer()
    
    # Test INPUT_TYPES
    input_types = node.INPUT_TYPES()
    assert "required" in input_types
    assert "prompt_a" in input_types["required"]
    assert "prompt_b" in input_types["required"]
    assert "blend_ratio" in input_types["required"]
    assert "blend_mode" in input_types["required"]
    
    # Test return types
    assert LMStudioPromptMixer.RETURN_TYPES == ("STRING", "STRING", "STRING")
    assert LMStudioPromptMixer.RETURN_NAMES == ("mixed_prompt", "element_breakdown", "info")
    assert LMStudioPromptMixer.FUNCTION == "mix_prompts"
    assert LMStudioPromptMixer.CATEGORY == "🖥XDEV/LM Studio"
    
    print("✅ Prompt Mixer structure validated")


def test_scene_composer_structure():
    """Test Scene Composer node structure."""
    node = LMStudioSceneComposer()
    
    # Test INPUT_TYPES
    input_types = node.INPUT_TYPES()
    assert "required" in input_types
    assert "subject" in input_types["required"]
    assert "environment_type" in input_types["required"]
    assert "time_of_day" in input_types["required"]
    
    # Test return types (7 outputs)
    assert LMStudioSceneComposer.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    assert LMStudioSceneComposer.RETURN_NAMES == ("full_scene", "foreground", "midground", "background", "lighting", "atmosphere", "info")
    assert LMStudioSceneComposer.FUNCTION == "compose_scene"
    
    print("✅ Scene Composer structure validated")


def test_aspect_ratio_optimizer_structure():
    """Test Aspect Ratio Optimizer node structure."""
    node = LMStudioAspectRatioOptimizer()
    
    # Test INPUT_TYPES
    input_types = node.INPUT_TYPES()
    assert "required" in input_types
    assert "base_prompt" in input_types["required"]
    assert "aspect_ratio" in input_types["required"]
    
    # Test SDXL aspect ratios are defined
    assert hasattr(LMStudioAspectRatioOptimizer, "ASPECT_RATIOS")
    assert len(LMStudioAspectRatioOptimizer.ASPECT_RATIOS) > 0
    assert "1:1 (1024x1024)" in LMStudioAspectRatioOptimizer.ASPECT_RATIOS
    
    # Test return types (includes width and height)
    assert LMStudioAspectRatioOptimizer.RETURN_TYPES == ("STRING", "STRING", "INT", "INT", "STRING")
    assert LMStudioAspectRatioOptimizer.RETURN_NAMES == ("optimized_prompt", "composition_guide", "width", "height", "info")
    
    print("✅ Aspect Ratio Optimizer structure validated")


def test_refiner_prompt_generator_structure():
    """Test Refiner Prompt Generator node structure."""
    node = LMStudioRefinerPromptGenerator()
    
    # Test INPUT_TYPES
    input_types = node.INPUT_TYPES()
    assert "required" in input_types
    assert "base_prompt" in input_types["required"]
    assert "refiner_focus" in input_types["required"]
    assert "refiner_strength" in input_types["required"]
    
    # Test return types (includes refiner_params)
    assert LMStudioRefinerPromptGenerator.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING")
    assert LMStudioRefinerPromptGenerator.RETURN_NAMES == ("refiner_prompt", "emphasis_tags", "refiner_params", "info")
    assert LMStudioRefinerPromptGenerator.FUNCTION == "generate_refiner_prompt"
    
    print("✅ Refiner Prompt Generator structure validated")


def test_controlnet_prompter_structure():
    """Test ControlNet Prompter node structure."""
    node = LMStudioControlNetPrompter()
    
    # Test INPUT_TYPES
    input_types = node.INPUT_TYPES()
    assert "required" in input_types
    assert "base_prompt" in input_types["required"]
    assert "control_type" in input_types["required"]
    assert "control_strength" in input_types["required"]
    
    # Verify control types list
    control_types = input_types["required"]["control_type"][0]
    assert "pose" in control_types
    assert "canny_edge" in control_types
    assert "depth" in control_types
    
    # Test return types (includes negative_prompt)
    assert LMStudioControlNetPrompter.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING")
    assert LMStudioControlNetPrompter.RETURN_NAMES == ("controlnet_prompt", "guidance_notes", "negative_prompt", "info")
    
    print("✅ ControlNet Prompter structure validated")


def test_regional_prompter_structure():
    """Test Regional Prompter Helper node structure."""
    node = LMStudioRegionalPrompterHelper()
    
    # Test INPUT_TYPES
    input_types = node.INPUT_TYPES()
    assert "required" in input_types
    assert "optional" in input_types
    assert "composition_concept" in input_types["required"]
    assert "region_count" in input_types["required"]
    assert "region_layout" in input_types["required"]
    
    # Test return types (6 outputs for up to 4 regions)
    assert LMStudioRegionalPrompterHelper.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    assert LMStudioRegionalPrompterHelper.RETURN_NAMES == ("region_1_prompt", "region_2_prompt", "region_3_prompt", "region_4_prompt", "composition_guide", "info")
    assert LMStudioRegionalPrompterHelper.FUNCTION == "generate_regional_prompts"
    
    print("✅ Regional Prompter Helper structure validated")


def test_node_class_mappings():
    """Test that nodes are properly registered."""
    from lm_prompt_mixer import NODE_CLASS_MAPPINGS as mixer_mappings
    from lm_scene_composer import NODE_CLASS_MAPPINGS as scene_mappings
    from lm_aspect_ratio_optimizer import NODE_CLASS_MAPPINGS as aspect_mappings
    from lm_refiner_prompt_generator import NODE_CLASS_MAPPINGS as refiner_mappings
    from lm_controlnet_prompter import NODE_CLASS_MAPPINGS as controlnet_mappings
    from lm_regional_prompter import NODE_CLASS_MAPPINGS as regional_mappings
    
    assert "XDEVLMStudioPromptMixer" in mixer_mappings
    assert "XDEVLMStudioSceneComposer" in scene_mappings
    assert "XDEVLMStudioAspectRatioOptimizer" in aspect_mappings
    assert "XDEVLMStudioRefinerPromptGenerator" in refiner_mappings
    assert "XDEVLMStudioControlNetPrompter" in controlnet_mappings
    assert "XDEVLMStudioRegionalPrompterHelper" in regional_mappings
    
    print("✅ Node class mappings validated")


def run_all_tests():
    """Run all tests."""
    print("\n🧪 Testing New LM Studio Nodes\n")
    print("=" * 60)
    
    try:
        test_imports()
        test_prompt_mixer_structure()
        test_scene_composer_structure()
        test_aspect_ratio_optimizer_structure()
        test_refiner_prompt_generator_structure()
        test_controlnet_prompter_structure()
        test_regional_prompter_structure()
        test_node_class_mappings()
        
        print("=" * 60)
        print("\n✅ ALL TESTS PASSED!")
        print("\nNew Nodes Summary:")
        print("  1. ✅ Prompt Mixer - Blend two prompts intelligently")
        print("  2. ✅ Scene Composer - Multi-layer scene descriptions")
        print("  3. ✅ Aspect Ratio Optimizer - SDXL ratio-specific prompts")
        print("  4. ✅ Refiner Prompt Generator - SDXL refiner optimization")
        print("  5. ✅ ControlNet Prompter - Control-type aware prompts")
        print("  6. ✅ Regional Prompter Helper - Multi-region compositions")
        print("\n📝 Total: 6 new nodes, 24 total nodes in package")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
