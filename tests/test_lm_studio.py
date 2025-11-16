"""Tests for LM Studio Integration Nodes

Note: These tests require LM Studio to be running at http://localhost:1234
with a model loaded. Tests will be skipped if connection fails.
"""

import json

import pytest
from comfyui_custom_nodes.xdev import LMStudioPromptEnhancer, LMStudioTextGen

# Note: Vision tests require an actual image tensor, so we'll do basic structural tests


class TestLMStudioTextGen:
    """Tests for LMStudioTextGen node."""
    
    def test_input_types_structure(self):
        """Test INPUT_TYPES structure."""
        input_types = LMStudioTextGen.INPUT_TYPES()
        assert "required" in input_types
        assert "optional" in input_types
        assert "prompt" in input_types["required"]
        assert "temperature" in input_types["optional"]
        assert "server_url" in input_types["optional"]
    
    def test_node_attributes(self):
        """Test node has required attributes."""
        assert hasattr(LMStudioTextGen, "RETURN_TYPES")
        assert hasattr(LMStudioTextGen, "FUNCTION")
        assert hasattr(LMStudioTextGen, "CATEGORY")
        assert LMStudioTextGen.RETURN_TYPES == ("STRING", "STRING")  # generated_text, info
        assert LMStudioTextGen.CATEGORY == "🖥XDEV/LM Studio"
    
    def test_error_handling_no_server(self):
        """Test error handling when server is not available."""
        node = LMStudioTextGen()
        result = node.generate_text(
            prompt="test",
            user_input="test",
            server_url="http://localhost:9999"  # Non-existent server
        )
        assert isinstance(result, tuple)
        assert len(result) == 2  # generated_text, info
        assert "Error" in result[0] or "error" in result[0].lower()


class TestLMStudioPromptEnhancer:
    """Tests for LMStudioPromptEnhancer node."""
    
    def test_input_types_structure(self):
        """Test INPUT_TYPES structure."""
        input_types = LMStudioPromptEnhancer.INPUT_TYPES()
        assert "required" in input_types
        assert "simple_prompt" in input_types["required"]
        assert "style" in input_types["required"]
        assert "detail_level" in input_types["required"]
    
    def test_node_attributes(self):
        """Test node has required attributes."""
        assert hasattr(LMStudioPromptEnhancer, "RETURN_TYPES")
        assert LMStudioPromptEnhancer.RETURN_TYPES == ("STRING", "STRING", "STRING")  # positive, negative, info
        assert len(LMStudioPromptEnhancer.RETURN_NAMES) == 3
    
    def test_style_options(self):
        """Test style options are available."""
        input_types = LMStudioPromptEnhancer.INPUT_TYPES()
        styles = input_types["required"]["style"][0]
        assert "realistic" in styles
        assert "artistic" in styles
        assert "fantasy" in styles
        assert "none" in styles
    
    def test_error_handling(self):
        """Test error handling."""
        node = LMStudioPromptEnhancer()
        result = node.enhance_prompt(
            simple_prompt="test",
            server_url="http://localhost:9999"
        )
        assert isinstance(result, tuple)
        assert len(result) == 3  # positive, negative, info


class TestLMStudioVision:
    """Basic structural tests for LMStudioVision."""
    
    def test_node_structure(self):
        """Test node structure without actual image."""
        from comfyui_custom_nodes.xdev import LMStudioVision
        
        assert hasattr(LMStudioVision, "INPUT_TYPES")
        assert hasattr(LMStudioVision, "RETURN_TYPES")
        assert LMStudioVision.RETURN_TYPES == ("STRING", "STRING", "STRING")  # description, prompt_ready, info
        assert LMStudioVision.CATEGORY == "🖥XDEV/LM Studio"
    
    def test_input_types(self):
        """Test INPUT_TYPES includes image input."""
        from comfyui_custom_nodes.xdev import LMStudioVision
        
        input_types = LMStudioVision.INPUT_TYPES()
        assert "required" in input_types
        assert "image" in input_types["required"]
        assert "prompt" in input_types["required"]


# Integration test (requires LM Studio running)
def test_lm_studio_connection():
    """Test if LM Studio is accessible (optional integration test)."""
    import urllib.request
    import urllib.error
    
    try:
        url = "http://localhost:1234/v1/models"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"\n✓ LM Studio is running")
            if "data" in data and len(data["data"]) > 0:
                print(f"  Loaded models: {[m.get('id', 'unknown') for m in data['data']]}")
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError):
        pytest.skip("LM Studio server not running on localhost:1234")
    except Exception as e:  # pragma: no cover - informational only
        pytest.skip(f"Skipped LM Studio connection test due to unexpected error: {e}")


# Smoke tests for manual execution
if __name__ == "__main__":
    print("Running LM Studio nodes smoke tests...\n")
    
    # Test LMStudioTextGen
    print("Testing LMStudioTextGen...")
    tg = TestLMStudioTextGen()
    tg.test_input_types_structure()
    tg.test_node_attributes()
    tg.test_error_handling_no_server()
    print("✓ LMStudioTextGen structure tests passed\n")
    
    # Test LMStudioPromptEnhancer
    print("Testing LMStudioPromptEnhancer...")
    pe = TestLMStudioPromptEnhancer()
    pe.test_input_types_structure()
    pe.test_node_attributes()
    pe.test_style_options()
    pe.test_error_handling()
    print("✓ LMStudioPromptEnhancer structure tests passed\n")
    
    # Test LMStudioVision
    print("Testing LMStudioVision...")
    tv = TestLMStudioVision()
    tv.test_node_structure()
    tv.test_input_types()
    print("✓ LMStudioVision structure tests passed\n")
    
    # Check LM Studio connection
    print("Checking LM Studio connection...")
    test_lm_studio_connection()
    
    print("\n✅ All LM Studio node structure tests passed!")
    print("\nNote: Full integration tests require LM Studio running with a model loaded.")
