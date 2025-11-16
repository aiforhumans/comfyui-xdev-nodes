"""Tests for new LM Studio nodes

Run with: pytest test_new_lm_nodes.py
"""

from comfyui_custom_nodes.xdev import (
    LMStudioBatchProcessor,
    LMStudioChatHistory,
    LMStudioChatHistoryLoader,
    LMStudioContextOptimizer,
    LMStudioMultiModelSelector,
    LMStudioParameterPresets,
    LMStudioResponseValidator,
    LMStudioStreamingTextGen,
    LMStudioTokenCounter,
)


def test_streaming_text_gen_import():
    """Test streaming text generator imports."""
    assert hasattr(LMStudioStreamingTextGen, 'INPUT_TYPES')
    assert hasattr(LMStudioStreamingTextGen, 'stream_generate')
    assert LMStudioStreamingTextGen.RETURN_TYPES == ("STRING", "STRING", "STRING")
    print("✓ Streaming Text Gen imports successfully")


def test_chat_history_import():
    """Test chat history manager imports."""
    assert hasattr(LMStudioChatHistory, 'INPUT_TYPES')
    assert hasattr(LMStudioChatHistory, 'manage_history')
    assert hasattr(LMStudioChatHistoryLoader, 'load_history')
    print("✓ Chat History nodes import successfully")


def test_batch_processor_import():
    """Test batch processor imports."""
    assert hasattr(LMStudioBatchProcessor, 'INPUT_TYPES')
    assert hasattr(LMStudioBatchProcessor, 'process_batch')
    assert LMStudioBatchProcessor.RETURN_TYPES == ("STRING", "STRING", "STRING")
    print("✓ Batch Processor imports successfully")


def test_response_validator_import():
    """Test response validator imports."""
    assert hasattr(LMStudioResponseValidator, 'INPUT_TYPES')
    assert hasattr(LMStudioResponseValidator, 'validate_response')
    assert hasattr(LMStudioResponseValidator, 'VALIDATE_INPUTS')
    print("✓ Response Validator imports successfully")


def test_token_counter_import():
    """Test token counter imports."""
    assert hasattr(LMStudioTokenCounter, 'INPUT_TYPES')
    assert hasattr(LMStudioTokenCounter, 'count_tokens')
    assert LMStudioTokenCounter.RETURN_TYPES == ("INT", "INT", "BOOLEAN", "STRING", "STRING")
    print("✓ Token Counter imports successfully")


def test_context_optimizer_import():
    """Test context optimizer imports."""
    assert hasattr(LMStudioContextOptimizer, 'INPUT_TYPES')
    assert hasattr(LMStudioContextOptimizer, 'optimize_context')
    print("✓ Context Optimizer imports successfully")


def test_parameter_presets_import():
    """Test parameter presets imports."""
    assert hasattr(LMStudioParameterPresets, 'INPUT_TYPES')
    assert hasattr(LMStudioParameterPresets, 'apply_preset')
    assert hasattr(LMStudioParameterPresets, 'PRESETS')
    assert "creative" in LMStudioParameterPresets.PRESETS
    print("✓ Parameter Presets imports successfully")


def test_multi_model_selector_import():
    """Test multi-model selector imports."""
    assert hasattr(LMStudioMultiModelSelector, 'INPUT_TYPES')
    assert hasattr(LMStudioMultiModelSelector, 'select_model')
    assert hasattr(LMStudioMultiModelSelector, 'IS_CHANGED')
    print("✓ Multi-Model Selector imports successfully")


def test_token_counter_logic():
    """Test token counter logic."""
    node = LMStudioTokenCounter()
    text = "This is a test prompt with multiple words."
    
    result = node.count_tokens(
        text=text,
        estimation_method="rough",
        chars_per_token=4.0,
        context_limit=4096,
        max_completion=500
    )
    
    estimated_tokens, available_tokens, within_limit, warning, info = result
    
    assert isinstance(estimated_tokens, int)
    assert estimated_tokens > 0
    assert available_tokens > 0
    assert isinstance(within_limit, bool)
    assert within_limit is True  # Should be within 4096 limit
    print(f"✓ Token Counter: {estimated_tokens} tokens estimated")


def test_response_validator_logic():
    """Test response validator logic."""
    node = LMStudioResponseValidator()
    
    # Test JSON validation
    json_response = '{"key": "value", "number": 42}'
    result = node.validate_response(
        response=json_response,
        validation_type="json",
        strict_mode=False
    )
    
    validated, is_valid, errors, info = result
    assert is_valid is True
    print("✓ Response Validator: JSON validation passed")
    
    # Test length validation
    text = "Short text"
    result = node.validate_response(
        response=text,
        validation_type="length",
        min_length=5,
        max_length=100,
        strict_mode=False
    )
    
    validated, is_valid, errors, info = result
    assert is_valid is True
    print("✓ Response Validator: Length validation passed")


def test_context_optimizer_logic():
    """Test context optimizer logic."""
    node = LMStudioContextOptimizer()
    long_text = "This is a very long text. " * 100  # 2600 chars
    
    result = node.optimize_context(
        text=long_text,
        max_tokens=100,
        strategy="end",
        chars_per_token=4.0
    )
    
    optimized, original_tokens, optimized_tokens, info = result
    
    assert len(optimized) < len(long_text)
    assert optimized_tokens < original_tokens
    print(f"✓ Context Optimizer: {original_tokens} → {optimized_tokens} tokens")


def test_parameter_presets_logic():
    """Test parameter presets logic."""
    node = LMStudioParameterPresets()
    
    # Test creative preset
    result = node.apply_preset(preset="creative")
    temp, top_p, freq_pen, pres_pen, info = result
    
    assert temp == 0.9
    assert top_p == 0.95
    assert freq_pen == 0.5
    assert pres_pen == 0.5
    print("✓ Parameter Presets: Creative preset applied")
    
    # Test with override
    result = node.apply_preset(
        preset="creative",
        temperature_override=0.5
    )
    temp, top_p, freq_pen, pres_pen, info = result
    
    assert temp == 0.5  # Override applied
    assert top_p == 0.95  # Original preset
    print("✓ Parameter Presets: Override applied")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing New LM Studio Nodes")
    print("="*50 + "\n")
    
    # Import tests
    test_streaming_text_gen_import()
    test_chat_history_import()
    test_batch_processor_import()
    test_response_validator_import()
    test_token_counter_import()
    test_context_optimizer_import()
    test_parameter_presets_import()
    test_multi_model_selector_import()
    
    print("\n" + "-"*50)
    print("Logic Tests")
    print("-"*50 + "\n")
    
    # Logic tests
    test_token_counter_logic()
    test_response_validator_logic()
    test_context_optimizer_logic()
    test_parameter_presets_logic()
    
    print("\n" + "="*50)
    print("✅ All Tests Passed!")
    print("="*50 + "\n")
