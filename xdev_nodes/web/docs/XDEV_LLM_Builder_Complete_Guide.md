# LLM-Builder Node Group Documentation

## Overview

The **LLM-Builder** node group provides comprehensive LM Studio integration for ComfyUI, enabling advanced conversational AI workflows directly within ComfyUI's node-based interface. This complete suite includes **11 professional nodes** covering all aspects of LLM integration.

## 🧩 Core LM Studio Nodes

### XDEV_LMStudioChatAdvanced
**Category**: `XDev/LLM-Builder/Core`

Advanced LM Studio chat integration with full OpenAI API compatibility.

**Key Features**:
- Full OpenAI parameter support (temperature, top_p, frequency_penalty, presence_penalty)
- Model selection from `/v1/models` endpoint
- Streaming support (experimental)
- Conversation history management
- System message integration
- Performance monitoring and caching

**Inputs**:
- **prompt** (STRING): Main user message or conversation prompt
- **server_url** (STRING): LM Studio server URL (default: http://localhost:1234)
- **system_message** (STRING, optional): System instructions for AI model
- **model** (STRING, optional): Model identifier
- **temperature** (FLOAT, 0.0-2.0): Sampling temperature
- **max_tokens** (INT, 1-4096): Maximum response tokens
- **top_p, frequency_penalty, presence_penalty**: Advanced sampling parameters
- **streaming** (BOOLEAN): Enable streaming responses
- **message_history** (STRING): JSON conversation history

**Outputs**:
- **response** (STRING): AI model's response
- **full_conversation** (STRING): Complete conversation formatted
- **api_info** (STRING): API call information and statistics

---

### XDEV_LMStudioEmbeddings  
**Category**: `XDev/LLM-Builder/Core`

Generate text embeddings using LM Studio embedding models.

**Key Features**:
- Vector embedding generation
- Compatible with any OpenAI-compatible embedding API
- Automatic dimension detection
- TTL-based caching for performance

**Inputs**:
- **text** (STRING): Text to convert to embeddings
- **server_url** (STRING): LM Studio server URL
- **model** (STRING, optional): Embedding model identifier

**Outputs**:
- **embeddings_json** (STRING): JSON array of embedding vectors
- **dimensions_info** (STRING): Vector dimension information
- **api_info** (STRING): API call details

---

### XDEV_LMStudioCompletions
**Category**: `XDev/LLM-Builder/Core`

Simple text completion without chat formatting.

**Key Features**:
- Direct text completion (no role/message structure)
- Stop sequence support
- Configurable sampling parameters
- Fallback HTTP client support

**Inputs**:
- **prompt** (STRING): Text prompt for completion
- **server_url** (STRING): LM Studio server URL
- **max_tokens, temperature, top_p**: Sampling parameters
- **stop_sequences** (STRING): JSON array of stop sequences

**Outputs**:
- **completion** (STRING): Generated text completion
- **api_info** (STRING): API call information

## 🔗 Workflow Integration Nodes

### XDEV_PromptBuilderAdvanced
**Category**: `XDev/LLM-Builder/Workflow`

Advanced prompt builder with variable substitution and JSON output.

**Key Features**:
- Template-based prompt building with {variable} placeholders
- Support for additional JSON variables
- Multiple output formats (string, JSON)
- Built-in validation and error handling

**Template Example**:
```
"Create an image of {subject} in {style} with {details}"
```

**Inputs**:
- **template** (STRING): Template with {variable} placeholders
- **subject, style, details, environment, quality** (STRING): Standard variables
- **additional_vars** (STRING): JSON object with custom variables
- **output_format**: "string" or "json"

**Outputs**:
- **built_prompt** (STRING): Final constructed prompt
- **variables_info** (STRING): Variable usage information

---

### XDEV_TextToImagePromptBridge
**Category**: `XDev/LLM-Builder/Workflow`

Convert LLM responses to SDXL-compatible image prompts.

**Key Features**:
- Multiple extraction modes (direct, extract_description, extract_json, clean_and_format)
- Automatic conversational element removal
- Style suffix integration
- Length limiting with smart truncation

**Extraction Modes**:
- **direct**: Use response as-is
- **extract_description**: Remove conversational fluff, keep descriptive content
- **extract_json**: Parse JSON and extract prompt fields
- **clean_and_format**: Comprehensive cleaning for image generation

**Inputs**:
- **llm_response** (STRING): Response from LM Studio or other LLM
- **extraction_mode**: Processing method
- **style_suffix** (STRING): Quality/style terms to append
- **negative_terms** (STRING): Terms for negative prompt
- **max_length** (INT): Maximum prompt length

**Outputs**:
- **sdxl_prompt** (STRING): Processed image generation prompt
- **negative_prompt** (STRING): Negative prompt terms
- **processing_info** (STRING): Processing details

---

### XDEV_ImageCaptioningLLM
**Category**: `XDev/LLM-Builder/Workflow`

Enhance image captions using LM Studio for better prompts.

**Enhancement Styles**:
- **expand_details**: Add specific visual details, colors, lighting
- **artistic_description**: Artistic and evocative style with mood
- **technical_analysis**: Photography details and composition
- **story_context**: Narrative elements and emotional depth
- **prompt_optimization**: AI image generation keyword optimization

**Inputs**:
- **base_caption** (STRING): Base caption from CLIP interrogator
- **server_url** (STRING): LM Studio server URL
- **enhancement_style**: Type of caption enhancement
- **model, max_tokens, temperature**: LLM parameters

**Outputs**:
- **enhanced_caption** (STRING): Improved caption
- **original_caption** (STRING): Original caption preserved
- **enhancement_info** (STRING): Enhancement processing details

## 🧠 Memory & Control Nodes

### XDEV_ConversationMemory
**Category**: `XDev/LLM-Builder/Memory`

Advanced conversation history management with intelligent truncation.

**Key Features**:
- Message count and token-based truncation
- Multiple truncation strategies (oldest_first, newest_first, summarize_old)
- Automatic conversation summarization
- Memory reset functionality
- Timestamp tracking

**Truncation Strategies**:
- **oldest_first**: Remove oldest messages when limit exceeded
- **newest_first**: Remove newest messages when limit exceeded
- **summarize_old**: Summarize old messages, keep recent ones

**Inputs**:
- **current_message** (STRING): Message to add to conversation
- **role**: "user", "assistant", or "system"
- **existing_history** (STRING): Current conversation history as JSON
- **max_messages** (INT, 1-50): Maximum number of messages
- **max_tokens** (INT, 100-16000): Maximum total tokens (estimated)
- **truncation_strategy**: How to handle overflow
- **reset_memory** (BOOLEAN): Clear all history

**Outputs**:
- **updated_history** (STRING): Updated conversation history JSON
- **conversation_summary** (STRING): Human-readable summary
- **memory_info** (STRING): Memory statistics and strategy info

---

### XDEV_PersonaSystemMessage
**Category**: `XDev/LLM-Builder/Memory`

Dynamic AI persona and system message builder with templates.

**Predefined Personas**:
- **creative_assistant**: Highly creative and imaginative AI
- **technical_expert**: Precise technical expert with deep knowledge
- **friendly_helper**: Warm, friendly, and helpful assistant
- **professional_advisor**: Professional business and strategic advisor
- **artistic_mentor**: Experienced artistic mentor and guide
- **custom**: Define your own persona

**Inputs**:
- **persona_type**: Select predefined persona or "custom"
- **custom_system_message** (STRING): Custom instructions when using "custom"
- **task_context** (STRING): Specific task context to include
- **personality_traits** (STRING): Additional traits (comma-separated)
- **domain_expertise** (STRING): Domain expertise to emphasize
- **response_style**: "conversational", "formal", "creative", "technical", "friendly"
- **output_format**: "system_message" or "full_persona_json"

**Outputs**:
- **system_message** (STRING): Complete system message for LLM
- **persona_info** (STRING): Summary of persona configuration
- **persona_data** (STRING): Complete persona data as JSON

## 📊 Utility Nodes

### XDEV_TextCleaner
**Category**: `XDev/LLM-Builder/Utility`

Comprehensive text cleaning and formatting with multiple processing options.

**Cleaning Options**:
- **Remove emojis**: Strip emoji characters
- **Remove URLs**: Remove web addresses
- **Remove email/phone**: Strip contact information
- **Remove special characters**: Keep only alphanumeric and spaces
- **Normalize whitespace**: Convert multiple spaces/newlines to single spaces
- **Remove stopwords**: Filter common English stopwords
- **Case conversion**: none, lower, upper, title, sentence
- **Custom replacements**: JSON find/replace pairs

**Inputs**:
- **input_text** (STRING): Text to clean and process
- **remove_emojis, remove_urls, remove_email, remove_phone** (BOOLEAN): Cleaning flags
- **normalize_whitespace, remove_stopwords** (BOOLEAN): Formatting options
- **case_conversion**: Text case transformation
- **max_length** (INT): Maximum output length (0 = no limit)
- **custom_replacements** (STRING): JSON object with find/replace pairs

**Outputs**:
- **cleaned_text** (STRING): Processed and cleaned text
- **cleaning_report** (STRING): Report of applied cleaning steps
- **original_text** (STRING): Original text preserved

---

### XDEV_JSONExtractor
**Category**: `XDev/LLM-Builder/Utility`

Extract and manipulate JSON data from LLM responses or text.

**Extraction Modes**:
- **auto_detect**: Try multiple extraction methods automatically
- **extract_first**: Find first JSON object or array
- **extract_all**: Find all JSON structures (return as array)
- **parse_direct**: Parse entire input as JSON

**Output Formats**:
- **json_string**: Compact JSON string
- **pretty_json**: Formatted JSON with indentation
- **key_value_pairs**: Human-readable key: value format
- **extracted_value**: Direct value as string

**Inputs**:
- **input_text** (STRING): Text containing JSON data
- **extraction_mode**: How to find and extract JSON
- **target_key** (STRING): Specific JSON key to extract
- **array_index** (INT): Array index to extract
- **output_format**: Format for output
- **fallback_behavior**: What to do if extraction fails

**Outputs**:
- **extracted_data** (STRING): Extracted and formatted data
- **extraction_info** (STRING): Extraction process information
- **raw_json** (STRING): Raw JSON that was extracted

---

### XDEV_Router
**Category**: `XDev/LLM-Builder/Utility`

Conditional workflow routing based on text content analysis.

**Routing Modes**:
- **keyword_match**: Route based on keyword groups
- **json_field**: Route based on JSON field values  
- **text_length**: Route based on text length thresholds
- **pattern_match**: Route based on regex patterns
- **sentiment_basic**: Route based on simple sentiment analysis

**Inputs**:
- **input_text** (STRING): Text to analyze for routing
- **routing_mode**: Method for determining route
- **route_keywords** (STRING): Pipe-separated keyword groups
- **json_field, json_values**: JSON-based routing parameters
- **length_thresholds, regex_patterns**: Length/pattern routing
- **default_route** (STRING): Fallback route when no conditions match

**Outputs**:
- **selected_route** (STRING): Chosen route (route_1, route_2, etc.)
- **route_info** (STRING): Routing decision summary
- **analysis_details** (STRING): Detailed analysis information
- **input_passthrough** (STRING): Original input preserved

## 🖥️ Advanced Integration Nodes

### XDEV_MultiModal
**Category**: `XDev/LLM-Builder/Advanced`

Multi-modal analysis combining text and image data (vision model ready).

**Analysis Types**:
- **describe_scene**: Comprehensive scene description
- **generate_caption**: Detailed caption creation
- **analyze_content**: Detailed content analysis
- **create_prompt**: AI image generation prompt optimization
- **compare_elements**: Analyze text/visual relationships

**Inputs**:
- **text_input** (STRING): Text content for analysis
- **image_description** (STRING): Description of image content
- **image_metadata** (STRING): Image metadata as JSON
- **analysis_type**: Type of multi-modal analysis
- **server_url, model**: LM Studio parameters
- **max_tokens, temperature**: Generation parameters
- **include_technical_details** (BOOLEAN): Include technical analysis

**Outputs**:
- **analysis_result** (STRING): LLM analysis result
- **multimodal_prompt** (STRING): Combined prompt for LLM
- **technical_details** (STRING): Technical analysis information
- **combined_data** (STRING): Complete multi-modal data as JSON

---

### XDEV_LLMWorkflowController
**Category**: `XDev/LLM-Builder/Advanced`

**⚠️ EXPERIMENTAL**: LLM-driven ComfyUI workflow control and modification.

**Control Modes**:
- **suggest_changes**: Analyze description and suggest workflow modifications
- **generate_workflow**: Create complete workflow plan from description
- **modify_existing**: Analyze existing workflow and suggest modifications
- **analyze_description**: Break down requirements into technical components

**Inputs**:
- **workflow_description** (STRING): Natural language workflow description
- **current_workflow** (STRING): Existing workflow JSON (optional)
- **available_nodes** (STRING): Available node types (comma-separated)
- **control_mode**: How to process the description
- **server_url, model**: LM Studio parameters
- **include_connections** (BOOLEAN): Include node connection suggestions

**Outputs**:
- **workflow_suggestions** (STRING): LLM-generated workflow suggestions
- **structured_plan** (STRING): Organized workflow plan
- **node_analysis** (STRING): Required nodes analysis
- **implementation_notes** (STRING): Implementation warnings and tips

## 🔧 Installation & Setup

### Requirements
- **LM Studio**: Local LLM server with OpenAI-compatible API
- **Python Libraries**: `httpx` (preferred) or `requests` for HTTP calls
- **ComfyUI**: Compatible with existing XDev node framework

### LM Studio Configuration
1. Start LM Studio with local server enabled
2. Enable OpenAI-compatible API endpoint  
3. Load desired model (chat, completion, or embedding)
4. Default URL: `http://localhost:1234`

### Alternative Servers
Compatible with any OpenAI-compatible API:
- **Ollama**: `http://localhost:11434`
- **Text Generation WebUI**: `http://localhost:5000`
- **Custom servers**: Any OpenAI chat/completions implementation

## 💡 Usage Patterns

### Complete Text-to-Image Workflow
```
1. PersonaSystemMessage (creative_assistant) → system_message
2. LMStudioChatAdvanced (system_message + user_prompt) → response
3. TextToImagePromptBridge (response) → sdxl_prompt
4. KSampler (sdxl_prompt) → generated_image
```

### Conversation with Memory
```
1. ConversationMemory (current_message) → updated_history
2. LMStudioChatAdvanced (message_history=updated_history) → response
3. ConversationMemory (response, role=assistant) → updated_history
```

### Intelligent Content Processing
```
1. Router (input_text) → selected_route
2. If route_1: TextCleaner → JSONExtractor → structured_data
3. If route_2: LMStudioChatAdvanced → conversational_response  
4. If route_3: MultiModal → enhanced_analysis
```

### Dynamic Prompt Building
```
1. PromptBuilderAdvanced (template + variables) → base_prompt
2. ImageCaptioningLLM (base_prompt, enhancement=prompt_optimization) → enhanced_prompt
3. TextToImagePromptBridge (enhanced_prompt) → final_sdxl_prompt
```

## 🚀 Advanced Features

### Performance Optimization
- **TTL-based caching**: Responses cached for 5-10 minutes
- **Performance monitoring**: All nodes tracked with @performance_monitor
- **Graceful fallbacks**: httpx → requests → error handling
- **Input validation**: Comprehensive validation with detailed error messages

### Error Handling
- **Connection failures**: Detailed error messages with troubleshooting info
- **API errors**: HTTP status codes and response analysis
- **Invalid inputs**: Validation with helpful correction suggestions
- **Timeout handling**: 30-45 second timeouts with proper cleanup

### Integration Features
- **Universal Testing**: Compatible with InputDev → Node → OutputDev pattern
- **Category Organization**: Logical grouping under XDev/LLM-Builder hierarchy
- **Documentation**: Comprehensive tooltips and usage examples
- **Backward Compatibility**: Graceful handling of missing dependencies

## ⚠️ Important Notes

### Experimental Features
- **LLMWorkflowController**: Experimental workflow modification (use with caution)
- **MultiModal**: Prepared for future vision model integration
- **Streaming**: LMStudioChatAdvanced streaming support is experimental

### Performance Considerations
- **API Latency**: LLM calls can take 1-30 seconds depending on model and prompt
- **Token Limits**: Respect model token limits (typically 2K-32K tokens)
- **Rate Limiting**: Some LM Studio setups may have rate limits
- **Memory Usage**: Conversation history can accumulate quickly

### Best Practices
1. **Start Simple**: Begin with basic LMStudioChatAdvanced before advanced features
2. **Monitor Performance**: Use performance monitoring to identify bottlenecks
3. **Cache Effectively**: Enable caching for repeated operations
4. **Validate Inputs**: Keep validation enabled during development
5. **Error Handling**: Always check error outputs and implement fallbacks

This complete LLM-Builder suite transforms ComfyUI into a powerful conversational AI platform while maintaining the familiar node-based workflow approach.