"""
Test suite for Phase 6 LLM-Enhanced Prompt Tool Nodes
Tests all 4 new LLM-enhanced nodes with mock LLM responses and integration validation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestLLMEnhancedNodes:
    """Test suite for Phase 6 LLM-Enhanced prompt tools."""
    
    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for testing."""
        return {
            "choices": [{
                "message": {
                    "content": "Test LLM response content"
                }
            }]
        }
    
    @pytest.fixture
    def mock_framework(self):
        """Mock LLMPromptFramework for testing."""
        framework = Mock()
        framework.make_request = AsyncMock()
        framework.make_request.return_value = {
            "choices": [{
                "message": {
                    "content": "Enhanced prompt content"
                }
            }]
        }
        return framework
    
    def test_llm_prompt_assistant_import(self):
        """Test LLMPromptAssistant can be imported."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMPromptAssistant
            assert LLMPromptAssistant is not None
            assert hasattr(LLMPromptAssistant, 'INPUT_TYPES')
            assert hasattr(LLMPromptAssistant, 'enhance_prompt')
        except ImportError as e:
            pytest.fail(f"Failed to import LLMPromptAssistant: {e}")
    
    def test_llm_contextual_builder_import(self):
        """Test LLMContextualBuilder can be imported."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMContextualBuilder
            assert LLMContextualBuilder is not None
            assert hasattr(LLMContextualBuilder, 'INPUT_TYPES')
            assert hasattr(LLMContextualBuilder, 'build_contextual_prompt')
        except ImportError as e:
            pytest.fail(f"Failed to import LLMContextualBuilder: {e}")
    
    def test_llm_person_builder_import(self):
        """Test LLMPersonBuilder can be imported."""
        try:
            from xdev_nodes.nodes.prompt import LLMPersonBuilder
            assert LLMPersonBuilder is not None
            assert hasattr(LLMPersonBuilder, 'INPUT_TYPES')
            assert hasattr(LLMPersonBuilder, 'generate_character')
        except ImportError as e:
            pytest.fail(f"Failed to import LLMPersonBuilder: {e}")
    
    def test_llm_style_builder_import(self):
        """Test LLMStyleBuilder can be imported."""
        try:
            from xdev_nodes.nodes.prompt import LLMStyleBuilder
            assert LLMStyleBuilder is not None
            assert hasattr(LLMStyleBuilder, 'INPUT_TYPES')
            assert hasattr(LLMStyleBuilder, 'generate_style')
        except ImportError as e:
            pytest.fail(f"Failed to import LLMStyleBuilder: {e}")
    
    def test_llm_prompt_framework_import(self):
        """Test LLMPromptFramework can be imported."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMPromptFramework
            assert LLMPromptFramework is not None
            assert hasattr(LLMPromptFramework, 'make_request')
        except ImportError as e:
            pytest.fail(f"Failed to import LLMPromptFramework: {e}")
    
    @pytest.mark.asyncio
    async def test_llm_prompt_assistant_basic_functionality(self, mock_framework):
        """Test LLMPromptAssistant basic functionality with mocked LLM."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMPromptAssistant
            
            # Create instance
            assistant = LLMPromptAssistant()
            
            # Mock the framework
            with patch.object(assistant, 'llm_framework', mock_framework):
                # Test basic enhancement
                result = await assistant.enhance_prompt(
                    prompt="a beautiful landscape",
                    task_type="generation",
                    enhancement_level="medium",
                    custom_instructions="",
                    server_url="http://localhost:1234",
                    model="test-model",
                    enable_llm=True
                )
                
                # Verify result structure
                assert isinstance(result, tuple)
                assert len(result) == 3  # enhanced_prompt, analysis, metadata
                
                # Verify LLM was called
                mock_framework.make_request.assert_called_once()
                
        except ImportError:
            pytest.skip("LLMPromptAssistant not available")
        except Exception as e:
            pytest.fail(f"LLMPromptAssistant test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_llm_contextual_builder_functionality(self, mock_framework):
        """Test LLMContextualBuilder functionality with mocked LLM."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMContextualBuilder
            
            # Create instance
            builder = LLMContextualBuilder()
            
            # Mock the framework
            with patch.object(builder, 'llm_framework', mock_framework):
                # Test contextual building
                result = await builder.build_contextual_prompt(
                    base_prompt="a character",
                    context="fantasy setting",
                    style="detailed",
                    mood="heroic",
                    custom_context="",
                    server_url="http://localhost:1234",
                    model="test-model",
                    enable_llm=True
                )
                
                # Verify result structure
                assert isinstance(result, tuple)
                assert len(result) == 3  # contextual_prompt, context_analysis, metadata
                
                # Verify LLM was called
                mock_framework.make_request.assert_called_once()
                
        except ImportError:
            pytest.skip("LLMContextualBuilder not available")
        except Exception as e:
            pytest.fail(f"LLMContextualBuilder test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_llm_person_builder_functionality(self, mock_framework):
        """Test LLMPersonBuilder functionality with mocked LLM."""
        try:
            from xdev_nodes.nodes.prompt import LLMPersonBuilder
            
            # Create instance
            builder = LLMPersonBuilder()
            
            # Mock the framework - need to create it since it's instantiated in __init__
            with patch('xdev_nodes.nodes.prompt.LLMPromptFramework') as mock_framework_class:
                mock_framework_class.return_value = mock_framework
                
                # Re-create instance with mocked framework
                builder = LLMPersonBuilder()
                
                # Test character generation
                result = await builder.generate_character(
                    base_prompt="warrior",
                    character_type="hero",
                    personality_traits="brave, loyal",
                    background="medieval",
                    relationships="",
                    custom_traits="",
                    ai_enhancement="medium",
                    server_url="http://localhost:1234",
                    model="test-model",
                    enable_ai=True
                )
                
                # Verify result structure
                assert isinstance(result, tuple)
                assert len(result) == 4  # character_prompt, personality_analysis, traits_list, metadata
                
                # Verify LLM was called
                mock_framework.make_request.assert_called_once()
                
        except ImportError:
            pytest.skip("LLMPersonBuilder not available")
        except Exception as e:
            pytest.fail(f"LLMPersonBuilder test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_llm_style_builder_functionality(self, mock_framework):
        """Test LLMStyleBuilder functionality with mocked LLM."""
        try:
            from xdev_nodes.nodes.prompt import LLMStyleBuilder
            
            # Create instance
            builder = LLMStyleBuilder()
            
            # Mock the framework - need to create it since it's instantiated in __init__
            with patch('xdev_nodes.nodes.prompt.LLMPromptFramework') as mock_framework_class:
                mock_framework_class.return_value = mock_framework
                
                # Re-create instance with mocked framework
                builder = LLMStyleBuilder()
                
                # Test style generation
                result = await builder.generate_style(
                    base_prompt="portrait",
                    art_style="renaissance",
                    medium="oil painting",
                    mood="serene",
                    color_palette="warm",
                    lighting="soft",
                    composition="",
                    custom_elements="",
                    ai_enhancement="medium",
                    server_url="http://localhost:1234",
                    model="test-model",
                    enable_ai=True
                )
                
                # Verify result structure
                assert isinstance(result, tuple)
                assert len(result) == 4  # styled_prompt, style_analysis, elements_list, metadata
                
                # Verify LLM was called
                mock_framework.make_request.assert_called_once()
                
        except ImportError:
            pytest.skip("LLMStyleBuilder not available")
        except Exception as e:
            pytest.fail(f"LLMStyleBuilder test failed: {e}")
    
    def test_node_input_types_structure(self):
        """Test that all LLM-enhanced nodes have proper INPUT_TYPES structure."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMPromptAssistant, LLMContextualBuilder
            from xdev_nodes.nodes.prompt import LLMPersonBuilder, LLMStyleBuilder
            
            nodes = [LLMPromptAssistant, LLMContextualBuilder, LLMPersonBuilder, LLMStyleBuilder]
            
            for node_class in nodes:
                input_types = node_class.INPUT_TYPES()
                
                # Verify structure
                assert isinstance(input_types, dict)
                assert "required" in input_types
                assert isinstance(input_types["required"], dict)
                
                # Verify common LLM parameters
                required = input_types["required"]
                assert any("server_url" in key or "url" in key for key in required.keys())
                assert any("model" in key for key in required.keys())
                assert any("enable" in key for key in required.keys())
                
        except ImportError:
            pytest.skip("LLM-enhanced nodes not available")
    
    def test_node_return_types_structure(self):
        """Test that all LLM-enhanced nodes have proper RETURN_TYPES structure."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMPromptAssistant, LLMContextualBuilder
            from xdev_nodes.nodes.prompt import LLMPersonBuilder, LLMStyleBuilder
            
            nodes = [
                (LLMPromptAssistant, 3),  # enhanced_prompt, analysis, metadata
                (LLMContextualBuilder, 3),  # contextual_prompt, context_analysis, metadata
                (LLMPersonBuilder, 4),  # character_prompt, personality_analysis, traits_list, metadata
                (LLMStyleBuilder, 4),  # styled_prompt, style_analysis, elements_list, metadata
            ]
            
            for node_class, expected_count in nodes:
                # Verify RETURN_TYPES
                assert hasattr(node_class, 'RETURN_TYPES')
                assert len(node_class.RETURN_TYPES) == expected_count
                
                # Verify RETURN_NAMES
                assert hasattr(node_class, 'RETURN_NAMES')
                assert len(node_class.RETURN_NAMES) == expected_count
                
                # Verify FUNCTION
                assert hasattr(node_class, 'FUNCTION')
                assert isinstance(node_class.FUNCTION, str)
                
                # Verify CATEGORY
                assert hasattr(node_class, 'CATEGORY')
                assert "XDev" in node_class.CATEGORY
                
        except ImportError:
            pytest.skip("LLM-enhanced nodes not available")
    
    def test_error_handling_without_llm(self):
        """Test that nodes handle LLM unavailability gracefully."""
        try:
            from xdev_nodes.nodes.llm_integration import LLMPromptAssistant
            
            # Create instance
            assistant = LLMPromptAssistant()
            
            # Test with LLM disabled
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    assistant.enhance_prompt(
                        prompt="test prompt",
                        task_type="generation",
                        enhancement_level="medium",
                        custom_instructions="",
                        server_url="http://localhost:1234",
                        model="test-model",
                        enable_llm=False
                    )
                )
                
                # Should return original prompt when LLM disabled
                assert isinstance(result, tuple)
                assert len(result) == 3
                
            finally:
                loop.close()
                
        except ImportError:
            pytest.skip("LLMPromptAssistant not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])