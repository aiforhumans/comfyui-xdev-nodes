"""
Test Suite for XDev LLM-Builder Nodes
Comprehensive testing with mock API responses
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Import nodes for testing
try:
    from xdev_nodes.nodes.llm_builder_core import (
        XDEV_LMStudioChatAdvanced, XDEV_LMStudioEmbeddings, XDEV_LMStudioCompletions,
        XDEV_PromptBuilderAdvanced, XDEV_TextToImagePromptBridge, XDEV_ImageCaptioningLLM
    )
    from xdev_nodes.nodes.llm_builder_memory import (
        XDEV_ConversationMemory, XDEV_PersonaSystemMessage
    )
    from xdev_nodes.nodes.llm_builder_utility import (
        XDEV_TextCleaner, XDEV_JSONExtractor, XDEV_Router
    )
    from xdev_nodes.nodes.llm_builder_advanced import (
        XDEV_MultiModal, XDEV_LLMWorkflowController
    )
    NODES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import LLM-Builder nodes: {e}")
    NODES_AVAILABLE = False


class TestLLMBuilderCoreNodes:
    """Test core LLM integration nodes"""
    
    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_lm_studio_chat_advanced_input_types(self):
        """Test LMStudioChatAdvanced input type structure"""
        input_types = XDEV_LMStudioChatAdvanced.INPUT_TYPES()
        
        assert "required" in input_types
        assert "optional" in input_types
        assert "prompt" in input_types["required"]
        assert "server_url" in input_types["required"]
        assert "temperature" in input_types["optional"]
        assert "max_tokens" in input_types["optional"]
        
        # Check parameter ranges
        temp_config = input_types["optional"]["temperature"]
        assert temp_config["min"] == 0.0
        assert temp_config["max"] == 2.0
        
        max_tokens_config = input_types["optional"]["max_tokens"]
        assert max_tokens_config["min"] == 1
        assert max_tokens_config["max"] == 4096

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_lm_studio_chat_advanced_node_attributes(self):
        """Test LMStudioChatAdvanced node attributes"""
        node = XDEV_LMStudioChatAdvanced()
        
        assert hasattr(XDEV_LMStudioChatAdvanced, 'RETURN_TYPES')
        assert hasattr(XDEV_LMStudioChatAdvanced, 'RETURN_NAMES')
        assert hasattr(XDEV_LMStudioChatAdvanced, 'FUNCTION')
        assert hasattr(XDEV_LMStudioChatAdvanced, 'CATEGORY')
        
        assert XDEV_LMStudioChatAdvanced.FUNCTION == "generate_chat"
        assert "XDev/LLM-Builder/Core" in XDEV_LMStudioChatAdvanced.CATEGORY
        assert len(XDEV_LMStudioChatAdvanced.RETURN_TYPES) == 3
        assert len(XDEV_LMStudioChatAdvanced.RETURN_NAMES) == 3

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available") 
    @patch('httpx.Client')
    def test_lm_studio_chat_mock_api_success(self, mock_httpx):
        """Test LMStudioChatAdvanced with mock successful API response"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello! This is a test response."}}],
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }
        mock_response.raise_for_status = Mock()
        
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=Mock())
        mock_context.__enter__.return_value.post = Mock(return_value=mock_response)
        mock_context.__exit__ = Mock(return_value=None)
        mock_httpx.return_value = mock_context
        
        node = XDEV_LMStudioChatAdvanced()
        result = node.generate_chat(
            prompt="Hello, how are you?",
            server_url="http://localhost:1234",
            validate_input=False  # Skip validation for testing
        )
        
        response_text, full_conversation, api_info = result
        assert "Hello! This is a test response." in response_text
        assert "Hello, how are you?" in full_conversation
        assert "test-model" in api_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_lm_studio_embeddings_input_types(self):
        """Test LMStudioEmbeddings input type structure"""
        input_types = XDEV_LMStudioEmbeddings.INPUT_TYPES()
        
        assert "required" in input_types
        assert "text" in input_types["required"]
        assert "server_url" in input_types["required"]
        assert "model" in input_types["optional"]

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    @patch('httpx.Client')
    def test_lm_studio_embeddings_mock_api(self, mock_httpx):
        """Test LMStudioEmbeddings with mock API response"""
        # Mock embeddings API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}],
            "model": "embedding-model",
            "usage": {"total_tokens": 10}
        }
        mock_response.raise_for_status = Mock()
        
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=Mock())
        mock_context.__enter__.return_value.post = Mock(return_value=mock_response)
        mock_context.__exit__ = Mock(return_value=None)
        mock_httpx.return_value = mock_context
        
        node = XDEV_LMStudioEmbeddings()
        result = node.generate_embeddings(
            text="Test embedding text",
            server_url="http://localhost:1234",
            validate_input=False
        )
        
        embeddings_json, dimensions_info, api_info = result
        embeddings_data = json.loads(embeddings_json)
        assert len(embeddings_data) == 5
        assert "5" in dimensions_info
        assert "embedding-model" in api_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_lm_studio_completions_input_types(self):
        """Test LMStudioCompletions input type structure"""
        input_types = XDEV_LMStudioCompletions.INPUT_TYPES()
        
        assert "required" in input_types
        assert "prompt" in input_types["required"]
        assert "server_url" in input_types["required"]
        assert "max_tokens" in input_types["optional"]
        assert "temperature" in input_types["optional"]
        assert "stop_sequences" in input_types["optional"]


class TestLLMBuilderWorkflowNodes:
    """Test workflow integration nodes"""
    
    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_prompt_builder_advanced_basic_functionality(self):
        """Test PromptBuilderAdvanced basic functionality"""
        node = XDEV_PromptBuilderAdvanced()
        
        result = node.build_prompt(
            template="Create an image of {subject} in {style} with {details}",
            subject="a cat",
            style="anime style",
            details="bright colors",
            validate_input=False
        )
        
        built_prompt, variables_info = result
        assert "a cat" in built_prompt
        assert "anime style" in built_prompt
        assert "bright colors" in built_prompt
        assert "Variables used: 3" in variables_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_prompt_builder_json_variables(self):
        """Test PromptBuilderAdvanced with JSON additional variables"""
        node = XDEV_PromptBuilderAdvanced()
        
        additional_vars = json.dumps({"mood": "happy", "lighting": "golden hour"})
        
        result = node.build_prompt(
            template="A {subject} in {mood} {lighting}",
            subject="person",
            additional_vars=additional_vars,
            output_format="json",
            validate_input=False
        )
        
        built_prompt, variables_info = result
        prompt_data = json.loads(built_prompt)
        assert "person" in prompt_data["prompt"]
        assert "happy" in prompt_data["prompt"]
        assert "golden hour" in prompt_data["prompt"]
        assert "mood" in prompt_data["variables"]

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_text_to_image_prompt_bridge(self):
        """Test TextToImagePromptBridge functionality"""
        node = XDEV_TextToImagePromptBridge()
        
        llm_response = "I'll create a beautiful landscape image with mountains, trees, and a lake in the background."
        
        result = node.convert_to_image_prompt(
            llm_response=llm_response,
            extraction_mode="clean_and_format",
            style_suffix="highly detailed, 8k",
            validate_input=False
        )
        
        sdxl_prompt, negative_prompt, processing_info = result
        assert "mountains" in sdxl_prompt
        assert "trees" in sdxl_prompt
        assert "highly detailed, 8k" in sdxl_prompt
        assert "clean_and_format" in processing_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_text_to_image_bridge_json_extraction(self):
        """Test TextToImagePromptBridge JSON extraction"""
        node = XDEV_TextToImagePromptBridge()
        
        llm_response = json.dumps({
            "prompt": "A cyberpunk cityscape with neon lights",
            "style": "futuristic",
            "mood": "dark"
        })
        
        result = node.convert_to_image_prompt(
            llm_response=llm_response,
            extraction_mode="extract_json",
            validate_input=False
        )
        
        sdxl_prompt, negative_prompt, processing_info = result
        assert "cyberpunk cityscape" in sdxl_prompt
        assert "neon lights" in sdxl_prompt

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_image_captioning_llm_input_types(self):
        """Test ImageCaptioningLLM input types"""
        input_types = XDEV_ImageCaptioningLLM.INPUT_TYPES()
        
        assert "required" in input_types
        assert "base_caption" in input_types["required"]
        assert "server_url" in input_types["required"]
        assert "enhancement_style" in input_types["optional"]
        
        # Check enhancement style options
        style_options = input_types["optional"]["enhancement_style"][0]
        assert "expand_details" in style_options
        assert "artistic_description" in style_options
        assert "prompt_optimization" in style_options


class TestLLMBuilderMemoryNodes:
    """Test memory and control nodes"""
    
    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_conversation_memory_basic_functionality(self):
        """Test ConversationMemory basic functionality"""
        node = XDEV_ConversationMemory()
        
        result = node.manage_memory(
            current_message="Hello, how are you?",
            role="user",
            existing_history="[]",
            validate_input=False
        )
        
        updated_history, conversation_summary, memory_info = result
        history_data = json.loads(updated_history)
        assert len(history_data) == 1
        assert history_data[0]["role"] == "user"
        assert history_data[0]["content"] == "Hello, how are you?"
        assert "Messages: 1" in memory_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_conversation_memory_truncation(self):
        """Test ConversationMemory truncation functionality"""
        node = XDEV_ConversationMemory()
        
        # Create existing history with multiple messages
        existing_history = json.dumps([
            {"role": "user", "content": "Message 1", "timestamp": "2024-01-01T00:00:00"},
            {"role": "assistant", "content": "Response 1", "timestamp": "2024-01-01T00:01:00"},
            {"role": "user", "content": "Message 2", "timestamp": "2024-01-01T00:02:00"},
            {"role": "assistant", "content": "Response 2", "timestamp": "2024-01-01T00:03:00"}
        ])
        
        result = node.manage_memory(
            current_message="New message",
            role="user",
            existing_history=existing_history,
            max_messages=3,  # Should truncate to 3 messages
            validate_input=False
        )
        
        updated_history, conversation_summary, memory_info = result
        history_data = json.loads(updated_history)
        assert len(history_data) == 3  # Truncated to max_messages
        assert history_data[-1]["content"] == "New message"  # Latest message preserved

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_conversation_memory_reset(self):
        """Test ConversationMemory reset functionality"""
        node = XDEV_ConversationMemory()
        
        existing_history = json.dumps([
            {"role": "user", "content": "Old message 1"},
            {"role": "assistant", "content": "Old response 1"}
        ])
        
        result = node.manage_memory(
            current_message="Fresh start",
            role="user",
            existing_history=existing_history,
            reset_memory=True,
            validate_input=False
        )
        
        updated_history, conversation_summary, memory_info = result
        history_data = json.loads(updated_history)
        assert len(history_data) == 1
        assert history_data[0]["content"] == "Fresh start"
        assert "Memory reset" in conversation_summary

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_persona_system_message_basic(self):
        """Test PersonaSystemMessage basic functionality"""
        node = XDEV_PersonaSystemMessage()
        
        result = node.build_persona(
            persona_type="creative_assistant",
            task_context="Generate artistic image descriptions",
            validate_input=False
        )
        
        system_message, persona_info, persona_data = result
        assert "creative" in system_message.lower()
        assert "artistic" in system_message.lower()
        assert "Creative Assistant" in persona_info
        
        # Check JSON data structure
        persona_dict = json.loads(persona_data)
        assert "persona_name" in persona_dict
        assert "system_message" in persona_dict
        assert "traits" in persona_dict

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_persona_system_message_custom(self):
        """Test PersonaSystemMessage custom persona"""
        node = XDEV_PersonaSystemMessage()
        
        custom_message = "You are a specialized photography expert focused on landscape photography."
        
        result = node.build_persona(
            persona_type="custom",
            custom_system_message=custom_message,
            domain_expertise="landscape photography",
            personality_traits="patient, detail-oriented",
            validate_input=False
        )
        
        system_message, persona_info, persona_data = result
        assert "photography expert" in system_message
        assert "landscape photography" in system_message
        assert "patient" in system_message
        assert "detail-oriented" in system_message


class TestLLMBuilderUtilityNodes:
    """Test utility nodes"""
    
    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_text_cleaner_basic_functionality(self):
        """Test TextCleaner basic functionality"""
        node = XDEV_TextCleaner()
        
        input_text = "Hello!!! 😀😀😀   This is    a test   message!!!   "
        
        result = node.clean_text(
            input_text=input_text,
            remove_emojis=True,
            normalize_whitespace=True,
            validate_input=False
        )
        
        cleaned_text, cleaning_report, original_text = result
        assert "😀" not in cleaned_text  # Emojis removed
        assert "This is a test message" in cleaned_text  # Whitespace normalized
        assert original_text == input_text  # Original preserved
        assert "Removed emojis" in cleaning_report

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_text_cleaner_custom_replacements(self):
        """Test TextCleaner custom replacements"""
        node = XDEV_TextCleaner()
        
        custom_replacements = json.dumps({"old_word": "new_word", "test": "example"})
        
        result = node.clean_text(
            input_text="This is a test with old_word in it",
            custom_replacements=custom_replacements,
            validate_input=False
        )
        
        cleaned_text, cleaning_report, original_text = result
        assert "new_word" in cleaned_text
        assert "example" in cleaned_text
        assert "old_word" not in cleaned_text
        assert "test" not in cleaned_text

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_json_extractor_parse_direct(self):
        """Test JSONExtractor direct parsing"""
        node = XDEV_JSONExtractor()
        
        json_input = json.dumps({"name": "test", "value": 42, "active": True})
        
        result = node.extract_json(
            input_text=json_input,
            extraction_mode="parse_direct",
            output_format="pretty_json",
            validate_input=False
        )
        
        extracted_data, extraction_info, raw_json = result
        parsed_data = json.loads(extracted_data)
        assert parsed_data["name"] == "test"
        assert parsed_data["value"] == 42
        assert parsed_data["active"] is True
        assert "parse_direct" in extraction_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_json_extractor_target_key(self):
        """Test JSONExtractor target key extraction"""
        node = XDEV_JSONExtractor()
        
        json_input = json.dumps({"config": {"setting": "value"}, "data": [1, 2, 3]})
        
        result = node.extract_json(
            input_text=json_input,
            extraction_mode="parse_direct",
            target_key="data",
            validate_input=False
        )
        
        extracted_data, extraction_info, raw_json = result
        parsed_data = json.loads(extracted_data)
        assert parsed_data == [1, 2, 3]
        assert "data" in extraction_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_router_keyword_match(self):
        """Test Router keyword matching"""
        node = XDEV_Router()
        
        result = node.route_text(
            input_text="I want to generate an image of a beautiful landscape",
            routing_mode="keyword_match",
            route_keywords="image,visual,picture|chat,talk,conversation|data,analyze,process",
            validate_input=False
        )
        
        selected_route, route_info, analysis_details, input_passthrough = result
        assert selected_route == "route_1"  # Should match first group (image)
        assert "image" in analysis_details
        assert "keyword_match" in route_info

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_router_text_length(self):
        """Test Router text length routing"""
        node = XDEV_Router()
        
        short_text = "Short"
        long_text = "This is a much longer text that should exceed the first threshold and route to a different path based on length analysis."
        
        # Test short text
        result = node.route_text(
            input_text=short_text,
            routing_mode="text_length",
            length_thresholds="10|50|200",
            validate_input=False
        )
        
        selected_route, route_info, analysis_details, input_passthrough = result
        assert selected_route == "route_1"  # Should be under first threshold
        
        # Test long text
        result = node.route_text(
            input_text=long_text,
            routing_mode="text_length",
            length_thresholds="10|50|200",
            validate_input=False
        )
        
        selected_route, route_info, analysis_details, input_passthrough = result
        assert selected_route == "route_3"  # Should be over second threshold


class TestLLMBuilderAdvancedNodes:
    """Test advanced integration nodes"""
    
    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_multimodal_input_types(self):
        """Test MultiModal input types"""
        input_types = XDEV_MultiModal.INPUT_TYPES()
        
        assert "required" in input_types
        assert "text_input" in input_types["required"]
        assert "image_description" in input_types["optional"]
        assert "analysis_type" in input_types["optional"]
        
        # Check analysis type options
        analysis_options = input_types["optional"]["analysis_type"][0]
        assert "describe_scene" in analysis_options
        assert "generate_caption" in analysis_options
        assert "create_prompt" in analysis_options

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_multimodal_basic_functionality(self):
        """Test MultiModal basic functionality"""
        node = XDEV_MultiModal()
        
        result = node.analyze_multimodal(
            text_input="A beautiful sunset over the ocean",
            image_description="Golden sunset with orange and pink clouds reflected in calm water",
            analysis_type="describe_scene",
            validate_input=False
        )
        
        analysis_result, multimodal_prompt, technical_details, combined_data = result
        
        assert "sunset" in multimodal_prompt.lower()
        assert "ocean" in multimodal_prompt.lower()
        assert "describe_scene" in technical_details
        
        # Check combined data structure
        combined_dict = json.loads(combined_data)
        assert "text_input" in combined_dict
        assert "image_description" in combined_dict
        assert "analysis_type" in combined_dict

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_llm_workflow_controller_input_types(self):
        """Test LLMWorkflowController input types"""
        input_types = XDEV_LLMWorkflowController.INPUT_TYPES()
        
        assert "required" in input_types
        assert "workflow_description" in input_types["required"]
        assert "control_mode" in input_types["optional"]
        assert "available_nodes" in input_types["optional"]
        
        # Check control mode options
        control_options = input_types["optional"]["control_mode"][0]
        assert "suggest_changes" in control_options
        assert "generate_workflow" in control_options
        assert "modify_existing" in control_options

    @pytest.mark.skipif(not NODES_AVAILABLE, reason="LLM-Builder nodes not available")
    def test_llm_workflow_controller_basic(self):
        """Test LLMWorkflowController basic functionality"""
        node = XDEV_LLMWorkflowController()
        
        result = node.control_workflow(
            workflow_description="Create a text-to-image generation workflow with SDXL model",
            control_mode="suggest_changes",
            available_nodes="KSampler,CLIPTextEncode,VAEDecode,CheckpointLoaderSimple",
            validate_input=False
        )
        
        workflow_suggestions, structured_plan, node_analysis, implementation_notes = result
        
        assert "KSampler" in node_analysis or "KSampler" in workflow_suggestions
        assert "text-to-image" in structured_plan.lower()
        assert "suggest_changes" in structured_plan
        assert "experimental" in implementation_notes.lower()


if __name__ == "__main__":
    # Run specific test categories
    import subprocess
    
    print("🧪 Running LLM-Builder Node Tests...")
    
    # Run tests with pytest
    test_files = [
        "tests/test_llm_builder_nodes.py::TestLLMBuilderCoreNodes",
        "tests/test_llm_builder_nodes.py::TestLLMBuilderWorkflowNodes", 
        "tests/test_llm_builder_nodes.py::TestLLMBuilderMemoryNodes",
        "tests/test_llm_builder_nodes.py::TestLLMBuilderUtilityNodes",
        "tests/test_llm_builder_nodes.py::TestLLMBuilderAdvancedNodes"
    ]
    
    for test_file in test_files:
        print(f"\n📋 Running {test_file}...")
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_file, "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ PASSED")
            else:
                print("❌ FAILED")
                print(result.stdout)
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT")
        except Exception as e:
            print(f"💥 ERROR: {e}")