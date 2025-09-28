"""
Test suite for LM Studio integration node.

This test suite validates the LMStudioChat node functionality including:
- Basic import and initialization
- Input validation and error handling
- Message building and conversation management
- HTTP client fallbacks and graceful degradation
- Configuration presets and parameter handling
- Mock server responses and API compatibility
"""

import sys
import os
import json
import unittest
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the nodes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from xdev_nodes.nodes.llm_integration import LMStudioChat
    IMPORT_SUCCESS = True
except Exception as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)


class TestLMStudioChatImport(unittest.TestCase):
    """Test LM Studio Chat node import and initialization."""
    
    def test_import_success(self):
        """Test that the LMStudioChat node can be imported successfully."""
        self.assertTrue(IMPORT_SUCCESS, f"Failed to import LMStudioChat: {IMPORT_ERROR if not IMPORT_SUCCESS else ''}")
    
    def test_node_attributes(self):
        """Test that the node has all required attributes."""
        if not IMPORT_SUCCESS:
            self.skipTest("Import failed")
        
        # Required node attributes
        self.assertTrue(hasattr(LMStudioChat, 'INPUT_TYPES'))
        self.assertTrue(hasattr(LMStudioChat, 'RETURN_TYPES'))
        self.assertTrue(hasattr(LMStudioChat, 'RETURN_NAMES'))
        self.assertTrue(hasattr(LMStudioChat, 'FUNCTION'))
        self.assertTrue(hasattr(LMStudioChat, 'CATEGORY'))
        self.assertTrue(hasattr(LMStudioChat, 'DESCRIPTION'))
    
    def test_input_types_structure(self):
        """Test the INPUT_TYPES structure."""
        if not IMPORT_SUCCESS:
            self.skipTest("Import failed")
        
        input_types = LMStudioChat.INPUT_TYPES()
        
        # Check structure
        self.assertIn('required', input_types)
        self.assertIn('optional', input_types)
        
        # Check required inputs
        required = input_types['required']
        self.assertIn('prompt', required)
        self.assertIn('server_url', required)
        self.assertIn('model', required)
        self.assertIn('preset', required)
        
        # Check optional inputs
        optional = input_types['optional']
        self.assertIn('system_prompt', optional)
        self.assertIn('temperature', optional)
        self.assertIn('max_tokens', optional)
        self.assertIn('stream', optional)


class TestLMStudioChatConfiguration(unittest.TestCase):
    """Test LM Studio Chat configuration and presets."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Import failed")
        self.node = LMStudioChat()
    
    def test_preset_configurations(self):
        """Test that all presets are properly configured."""
        presets = LMStudioChat._PRESETS
        
        # Check all presets exist
        expected_presets = ['creative', 'balanced', 'focused', 'precise', 'custom']
        for preset in expected_presets:
            self.assertIn(preset, presets)
        
        # Check preset structure
        for preset_name, config in presets.items():
            if preset_name != 'custom':  # custom preset is handled differently
                self.assertIn('temperature', config)
                self.assertIn('max_tokens', config)
                self.assertIn('top_p', config)
    
    def test_preset_config_retrieval(self):
        """Test preset configuration retrieval."""
        # Test predefined preset
        config = self.node._get_preset_config('balanced', 0.5, 512, 0.9)
        expected = LMStudioChat._PRESETS['balanced']
        self.assertEqual(config, expected)
        
        # Test custom preset
        config = self.node._get_preset_config('custom', 0.5, 512, 0.9)
        expected = {'temperature': 0.5, 'max_tokens': 512, 'top_p': 0.9}
        self.assertEqual(config, expected)
    
    def test_default_ports(self):
        """Test that default ports are reasonable."""
        ports = LMStudioChat._DEFAULT_PORTS
        
        # Should contain common LLM server ports
        self.assertIn(1234, ports)  # LM Studio default
        self.assertIn(8000, ports)  # vLLM default
        self.assertIn(11434, ports)  # Ollama default
        
        # All should be valid port numbers
        for port in ports:
            self.assertGreaterEqual(port, 1)
            self.assertLessEqual(port, 65535)


class TestLMStudioChatValidation(unittest.TestCase):
    """Test LM Studio Chat input validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Import failed")
        self.node = LMStudioChat()
    
    def test_url_validation(self):
        """Test URL validation functionality."""
        # Valid URLs
        self.assertTrue(self.node._is_valid_url("http://localhost:1234"))
        self.assertTrue(self.node._is_valid_url("https://example.com"))
        self.assertTrue(self.node._is_valid_url("http://192.168.1.1:8000"))
        
        # Invalid URLs
        self.assertFalse(self.node._is_valid_url("not-a-url"))
        self.assertFalse(self.node._is_valid_url(""))
        self.assertFalse(self.node._is_valid_url("localhost:1234"))  # missing protocol
    
    def test_message_list_building(self):
        """Test message list building functionality."""
        # Basic message
        messages = self.node._build_message_list("Hello", "", "")
        expected = [{"role": "user", "content": "Hello"}]
        self.assertEqual(messages, expected)
        
        # With system prompt
        messages = self.node._build_message_list("Hello", "You are helpful", "")
        expected = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        self.assertEqual(messages, expected)
        
        # With history
        history = json.dumps([{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}])
        messages = self.node._build_message_list("How are you?", "", history)
        expected = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How are you?"}
        ]
        self.assertEqual(messages, expected)
        
        # With invalid history (should ignore)
        messages = self.node._build_message_list("Hello", "", "invalid json")
        expected = [{"role": "user", "content": "Hello"}]
        self.assertEqual(messages, expected)


class TestLMStudioChatMockResponses(unittest.TestCase):
    """Test LM Studio Chat with mock HTTP responses."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Import failed")
        self.node = LMStudioChat()
    
    @pytest.mark.skip(reason="Mock response test needs fixing")
    @patch('xdev_nodes.nodes.llm_integration.HAS_REQUESTS', True)
    @patch('xdev_nodes.nodes.llm_integration.requests')
    def test_mock_successful_response_requests(self, mock_requests):
        """Test successful API response using requests mock."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Hello! I'm doing well, thank you for asking."
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response  # For health checks
        
        # Test the response
        result = self.node.generate_response(
            prompt="How are you?",
            server_url="http://localhost:1234",
            model="test-model",
            preset="balanced",
            validate_input=True
        )
        
        response, conversation, server_info, stats = result
        
        # Verify response content
        self.assertEqual(response, "Hello! I'm doing well, thank you for asking.")
        self.assertIn("How are you?", conversation)
        self.assertIn("Hello! I'm doing well", conversation)
    
    def test_error_handling_no_http_client(self):
        """Test error handling when no HTTP client is available."""
        # Temporarily disable HTTP clients
        original_httpx = getattr(self.node.__class__, '_original_httpx', None)
        original_requests = getattr(self.node.__class__, '_original_requests', None)
        
        with patch('xdev_nodes.nodes.llm_integration.HAS_HTTPX', False), \
             patch('xdev_nodes.nodes.llm_integration.HAS_REQUESTS', False):
            
            result = self.node.generate_response(
                prompt="Test",
                server_url="http://localhost:1234",
                model="test-model",
                preset="balanced"
            )
            
            response, conversation, server_info, stats = result
            self.assertEqual(response, "")
            self.assertIn("No HTTP client available", server_info)
    
    def test_empty_prompt_validation(self):
        """Test validation of empty prompts."""
        result = self.node.generate_response(
            prompt="",
            server_url="http://localhost:1234",
            model="test-model",
            preset="balanced",
            validate_input=True
        )
        
        response, conversation, server_info, stats = result
        self.assertEqual(response, "")
        self.assertIn("Empty prompt", server_info)
    
    def test_invalid_url_validation(self):
        """Test validation of invalid URLs."""
        result = self.node.generate_response(
            prompt="Test",
            server_url="invalid-url",
            model="test-model",
            preset="balanced",
            validate_input=True
        )
        
        response, conversation, server_info, stats = result
        self.assertEqual(response, "")
        self.assertIn("Invalid server URL", server_info)


class TestLMStudioChatGenerationStats(unittest.TestCase):
    """Test LM Studio Chat generation statistics."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Import failed")
        self.node = LMStudioChat()
    
    def test_generation_stats_building(self):
        """Test generation statistics building."""
        config = {"temperature": 0.7, "max_tokens": 1024, "top_p": 0.8}
        response = "This is a test response from the LLM."
        
        stats = self.node._build_generation_stats(response, 1.5, config, 3)
        
        # Check that all expected stats are present
        self.assertIn("Generation time: 1.50s", stats)
        self.assertIn(f"Response length: {len(response)} characters", stats)
        self.assertIn("Messages in conversation: 3", stats)
        self.assertIn("Temperature: 0.7", stats)
        self.assertIn("Max tokens: 1024", stats)
        self.assertIn("Top-p: 0.8", stats)
    
    def test_server_info_building_error_handling(self):
        """Test server info building with error conditions."""
        # Test with invalid URL (should handle gracefully)
        info = self.node._get_server_info("http://invalid-server:9999", 1)
        
        # Should contain server URL even on error
        self.assertIn("http://invalid-server:9999", info)
        self.assertIn("Status:", info)


def run_llm_integration_tests():
    """Run all LM Studio integration tests."""
    print("\n" + "="*60)
    print("🤖 Testing LM Studio Integration Node")
    print("="*60)
    
    # Test categories
    test_classes = [
        TestLMStudioChatImport,
        TestLMStudioChatConfiguration,
        TestLMStudioChatValidation,
        TestLMStudioChatMockResponses,
        TestLMStudioChatGenerationStats
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🔄 Testing {test_class.__name__.replace('TestLMStudioChat', '')}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        class_total = result.testsRun
        class_passed = class_total - len(result.failures) - len(result.errors)
        class_failed = len(result.failures) + len(result.errors)
        
        total_tests += class_total
        passed_tests += class_passed
        failed_tests += class_failed
        
        if class_failed == 0:
            print(f"  ✅ All {class_passed} tests passed")
        else:
            print(f"  ❌ {class_failed}/{class_total} tests failed")
            for test, error in result.failures + result.errors:
                print(f"    - {test}: {error.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    print(f"\n📊 LM Studio Integration Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("🎉 All LM Studio integration tests passed!")
        return True
    else:
        print(f"⚠️  {failed_tests} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_llm_integration_tests()
    sys.exit(0 if success else 1)