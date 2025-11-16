"""Test suite for refactored LM Studio nodes.

Tests the new base classes and utilities with refactored nodes.
"""

import sys

def test_utils_import():
    """Test that utilities module imports correctly."""
    print("Testing utils import...")
    from lm_utils import (
        LMStudioAPIClient,
        InfoFormatter,
        OutputFormatter,
        JSONParser,
        ErrorFormatter,
        build_messages,
        build_payload,
    )
    print("✅ All utilities imported successfully")
    
    # Test InfoFormatter
    lines = InfoFormatter.create_header("Test Node", "🔧")
    assert len(lines) == 3
    assert "Test Node" in lines[1]
    print("✅ InfoFormatter works")
    
    # Test OutputFormatter
    output = OutputFormatter.wrap_output("test content", "TEST", "🎯")
    assert "TEST" in output
    assert "test content" in output
    print("✅ OutputFormatter works")
    
    # Test JSONParser
    json_text = '{"key": "value", "number": 42}'
    parsed = JSONParser.parse_response(json_text)
    assert parsed["key"] == "value"
    assert parsed["number"] == 42
    print("✅ JSONParser works")
    
    # Test JSON extraction with regex
    messy_response = 'Here is the result: {"positive_prompt": "a beautiful scene", "negative_prompt": "ugly"} Hope that helps!'
    parsed = JSONParser.parse_response(messy_response, expected_keys=["positive_prompt", "negative_prompt"])
    assert "positive_prompt" in parsed
    print("✅ JSONParser regex extraction works")
    
    # Test build_messages
    messages = build_messages("test prompt", system_prompt="system", response_format="json")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "JSON" in messages[0]["content"]
    print("✅ build_messages works")
    
    # Test build_payload
    payload = build_payload(messages, temperature=0.7, max_tokens=200, response_format="json", seed=42)
    assert payload["temperature"] == 0.7
    assert payload["max_tokens"] == 200
    assert payload["seed"] == 42
    assert "response_format" in payload
    print("✅ build_payload works")


def test_base_node_import():
    """Test that base node classes import correctly."""
    print("\nTesting base node import...")
    from lm_base_node import (
        LMStudioBaseNode,
        LMStudioTextBaseNode,
        LMStudioPromptBaseNode,
    )
    print("✅ All base classes imported successfully")
    
    # Test base class attributes
    assert LMStudioBaseNode.CATEGORY == "🖥XDEV/LM Studio"
    assert LMStudioBaseNode.DEFAULT_SERVER_URL == "http://localhost:1234"
    print("✅ Base class attributes correct")
    
    # Test common inputs
    required = LMStudioBaseNode.get_common_required_inputs()
    assert "prompt" in required
    assert "temperature" in required
    print("✅ Common inputs available")
    
    optional = LMStudioBaseNode.get_common_optional_inputs()
    assert "system_prompt" in optional
    assert "response_format" in optional
    print("✅ Common optional inputs available")


def test_refactored_text_gen():
    """Test refactored text generation node."""
    print("\nTesting refactored LM Studio Text Gen...")
    from lm_text_gen import LMStudioTextGen
    
    # Test class attributes
    assert LMStudioTextGen.FUNCTION == "generate_text"
    assert LMStudioTextGen.CATEGORY == "🖥XDEV/LM Studio"
    assert len(LMStudioTextGen.RETURN_TYPES) == 2
    print("✅ LMStudioTextGen attributes correct")
    
    # Test INPUT_TYPES
    inputs = LMStudioTextGen.INPUT_TYPES()
    assert "required" in inputs
    assert "optional" in inputs
    assert "prompt" in inputs["required"]
    assert "user_input" in inputs["required"]
    print("✅ LMStudioTextGen INPUT_TYPES correct")
    
    # Test instance can be created
    node = LMStudioTextGen()
    assert hasattr(node, "generate_text")
    assert hasattr(node, "_init_info")
    assert hasattr(node, "_add_model_info")
    print("✅ LMStudioTextGen instance created with base class methods")


def test_refactored_prompt_enhancer():
    """Test refactored prompt enhancer node."""
    print("\nTesting refactored LM Studio Prompt Enhancer...")
    from lm_prompt_enhancer import LMStudioPromptEnhancer
    
    # Test class attributes
    assert LMStudioPromptEnhancer.FUNCTION == "enhance_prompt"
    assert LMStudioPromptEnhancer.CATEGORY == "🖥XDEV/LM Studio"
    assert len(LMStudioPromptEnhancer.RETURN_TYPES) == 3
    print("✅ LMStudioPromptEnhancer attributes correct")
    
    # Test INPUT_TYPES
    inputs = LMStudioPromptEnhancer.INPUT_TYPES()
    assert "required" in inputs
    assert "optional" in inputs
    assert "simple_prompt" in inputs["required"]
    assert "style" in inputs["required"]
    print("✅ LMStudioPromptEnhancer INPUT_TYPES correct")
    
    # Test instance can be created
    node = LMStudioPromptEnhancer()
    assert hasattr(node, "enhance_prompt")
    assert hasattr(node, "_init_info")
    assert hasattr(node, "_get_default_system_prompt")
    print("✅ LMStudioPromptEnhancer instance created with base class methods")


def test_error_handling():
    """Test error handling utilities."""
    print("\nTesting error handling...")
    from lm_utils import ErrorFormatter, LMStudioConnectionError, LMStudioAPIError
    
    # Test connection error formatting
    conn_error = ErrorFormatter.format_connection_error("http://localhost:1234", "Connection refused")
    assert "Connection Error" in conn_error
    assert "localhost:1234" in conn_error
    assert "Troubleshooting" in conn_error
    print("✅ Connection error formatting works")
    
    # Test API error formatting
    api_error = ErrorFormatter.format_api_error("Model not found", 404)
    assert "API Error 404" in api_error
    assert "Model not found" in api_error
    print("✅ API error formatting works")
    
    # Test exception classes
    try:
        raise LMStudioConnectionError("Test connection error")
    except LMStudioConnectionError as e:
        assert str(e) == "Test connection error"
        print("✅ LMStudioConnectionError works")
    
    try:
        raise LMStudioAPIError("Test API error")
    except LMStudioAPIError as e:
        assert str(e) == "Test API error"
        print("✅ LMStudioAPIError works")


def test_backwards_compatibility():
    """Test that refactored nodes maintain backward compatibility."""
    print("\nTesting backwards compatibility...")
    from lm_text_gen import LMStudioTextGen
    from lm_prompt_enhancer import LMStudioPromptEnhancer
    
    # Check that old interface still works
    text_gen = LMStudioTextGen()
    inputs = LMStudioTextGen.INPUT_TYPES()
    
    # Simulate node execution signature
    import inspect
    sig = inspect.signature(text_gen.generate_text)
    params = list(sig.parameters.keys())
    
    # Check all expected parameters exist
    expected = ["prompt", "user_input", "temperature", "max_tokens", "system_prompt", 
                "response_format", "server_url", "model", "seed"]
    for param in expected:
        assert param in params, f"Missing parameter: {param}"
    
    print("✅ LMStudioTextGen maintains backward compatibility")
    
    # Check prompt enhancer
    enhancer = LMStudioPromptEnhancer()
    sig = inspect.signature(enhancer.enhance_prompt)
    params = list(sig.parameters.keys())
    
    expected = ["simple_prompt", "style", "detail_level", "temperature", 
                "additional_details", "negative_prompt", "response_format", "server_url", "model"]
    for param in expected:
        assert param in params, f"Missing parameter: {param}"
    
    print("✅ LMStudioPromptEnhancer maintains backward compatibility")


def main():
    """Run all tests."""
    print("="*60)
    print("REFACTORED NODES TEST SUITE")
    print("="*60)
    
    try:
        test_utils_import()
        test_base_node_import()
        test_refactored_text_gen()
        test_refactored_prompt_enhancer()
        test_error_handling()
        test_backwards_compatibility()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📊 Summary:")
        print("  - Utilities module: ✅ Working")
        print("  - Base node classes: ✅ Working")
        print("  - Refactored nodes: ✅ Working")
        print("  - Error handling: ✅ Working")
        print("  - Backward compatibility: ✅ Maintained")
        print("\n🎉 Refactoring successful! Ready for deployment.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
