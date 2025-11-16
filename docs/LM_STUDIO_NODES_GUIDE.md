# LM Studio Nodes Complete Guide

**16 Nodes for Complete LLM Integration with ComfyUI**

## 📋 Table of Contents

1. [Core Generation Nodes](#core-generation-nodes)
2. [Advanced Generation Nodes](#advanced-generation-nodes)
3. [Utility Nodes](#utility-nodes)
4. [Context Management Nodes](#context-management-nodes)
5. [Validation & Control Nodes](#validation--control-nodes)
6. [Workflow Examples](#workflow-examples)
7. [Best Practices](#best-practices)

---

## Core Generation Nodes

### 🎯 LM Studio Text Generator
**Purpose**: Generate text using local LLM models

**Inputs**:
- `prompt`: Base instruction text
- `user_input`: Content to process
- `temperature`: Randomness (0.0-2.0)
- `max_tokens`: Maximum output length
- `system_prompt`: Model behavior instructions
- `response_format`: "text" or "json"
- `model`: Model identifier (from selector)
- `seed`: Reproducibility seed

**Outputs**:
- `generated_text`: Clean text output
- `info`: Generation statistics

**Use Cases**:
- Creative writing
- Text transformation
- Question answering
- Code generation

---

### 👁️ LM Studio Vision (Image Analysis)
**Purpose**: Analyze images with vision models (Qwen3-VL, LLaVA)

**Inputs**:
- `image`: ComfyUI IMAGE tensor
- `prompt`: Analysis instructions
- `temperature`: Response creativity
- `max_tokens`: Output length
- `response_format`: "text" or "json"
- `detail_level`: "low", "high", "auto"

**Outputs**:
- `description`: Full analysis with headers
- `prompt_ready`: Clean description for SDXL
- `info`: Processing statistics

**Key Features**:
- Automatic tensor → base64 conversion
- Extended 120s timeout for vision processing
- JSON output via prompt instructions (not API parameter)

**Use Cases**:
- Image-to-prompt generation
- Style analysis
- Content description for SDXL

---

### ✨ LM Studio Prompt Enhancer
**Purpose**: Transform simple ideas into optimized SDXL prompts

**Inputs**:
- `simple_prompt`: Basic concept
- `style`: "realistic", "artistic", "fantasy", etc.
- `detail_level`: Complexity of output
- `additional_details`: Extra requirements
- `negative_prompt`: Generate negative prompt
- `response_format`: "text" or "json"

**Outputs**:
- `positive_prompt`: Enhanced SDXL prompt
- `negative_prompt`: Things to avoid
- `info`: Enhancement statistics

**SDXL Optimizations**:
- Natural language support (full sentences work!)
- Keyword weights limited to 1.0-1.4 (SDXL is sensitive)
- Minimal negative prompts (SDXL needs less)
- Artist references and quality tags
- Both keyword and natural language styles

---

## Advanced Generation Nodes

### 🌊 LM Studio Streaming Text Generator
**Purpose**: Real-time text generation with progress updates

**Key Features**:
- Server-Sent Events (SSE) streaming
- Live progress updates via ComfyUI progress API
- Token-by-token accumulation
- Speed statistics (tokens/second)

**Outputs**:
- `generated_text`: Complete streamed output
- `token_count`: Total tokens generated
- `info`: Timing and speed stats

**Use Cases**:
- Long-form content generation
- Real-time feedback workflows
- Interactive applications

**Technical Notes**:
- Uses `Accept: text/event-stream` header
- Parses SSE `data:` format
- Progress updates every 0.5 seconds
- 120s timeout for long generations

---

### 📦 LM Studio Batch Processor
**Purpose**: Process multiple prompts efficiently

**Inputs**:
- `prompts`: One prompt per line
- `batch_delay`: Delay between requests (rate limiting)
- Standard generation parameters

**Outputs**:
- `results_json`: Structured results with status
- `results_text`: Formatted summary
- `info`: Success/failure statistics

**Features**:
- Progress tracking per prompt
- Individual error handling (continues on failure)
- Configurable inter-request delay
- Success/failure counts

**Use Cases**:
- Dataset generation
- Prompt testing/comparison
- Bulk processing workflows

---

## Utility Nodes

### 🎯 LM Studio Model Selector
**Purpose**: Manual model selection input

**Simple pass-through node for model ID strings**

---

### 🎯 LM Studio Multi-Model Selector
**Purpose**: Automatic model discovery and selection

**Inputs**:
- `auto_refresh`: Query API on each execution
- `model_filter`: "all", "text", "vision", "embedding"
- `fallback_model`: Use if API fails

**Outputs**:
- `selected_model`: Primary model ID
- `available_models`: JSON list of all models
- `info`: Discovery statistics

**Features**:
- Dynamic model discovery via `/v1/models` API
- Intelligent filtering (heuristic-based)
- Automatic fallback on connection failure
- Always-execute for latest model list

**Use Cases**:
- Dynamic workflows
- Model availability checking
- Automatic model selection

---

### 🔄 LM Studio Model Unload Helper
**Purpose**: Check model status and provide guidance

**Use Case**: Memory management awareness

---

### 🚦 LM Studio Auto Unload Trigger
**Purpose**: Automatically unload models before image generation

**Modes**:
- `warning_only`: Print warning (non-blocking)
- `lms_cli`: Execute `lms unload --all` command
- `force_error`: Stop workflow until manual unload

**Use Case**: Prevent GPU memory conflicts

---

## Context Management Nodes

### 💬 LM Studio Chat History Manager
**Purpose**: Maintain stateful conversations

**Inputs**:
- `session_id`: Unique conversation identifier
- `role`: "user", "assistant", "system"
- `message`: Content to add
- `reset_history`: Clear and start fresh
- `max_messages`: Conversation length limit

**Outputs**:
- `messages_json`: OpenAI-compatible message array
- `formatted_history`: Human-readable conversation
- `info`: Message counts and statistics

**Key Features**:
- Global session storage (persists across executions)
- Automatic truncation (preserves system messages)
- `IS_CHANGED` always returns new timestamp (stateful)
- Thread-safe for single workflow

**Use Cases**:
- Multi-turn conversations
- Context-aware generation
- Chatbot workflows

---

### 💬 LM Studio Chat History Loader
**Purpose**: Retrieve existing chat history

**Simple loader for connecting history to generation nodes**

---

### 🔢 LM Studio Token Counter
**Purpose**: Estimate token usage before API calls

**Inputs**:
- `text`: Content to analyze
- `estimation_method`: "rough" (4 chars/token), "whitespace" (1.3 tokens/word), "chars_per_token" (custom)
- `context_limit`: Model's max context window
- `max_completion`: Planned generation tokens

**Outputs**:
- `estimated_tokens`: Input token estimate
- `available_tokens`: Remaining capacity
- `within_limit`: Boolean check
- `warning`: Overflow guidance if exceeded
- `info`: Detailed breakdown

**Features**:
- Multiple estimation methods
- Context overflow detection
- Actionable warnings
- Budget planning

**Use Cases**:
- Pre-flight token validation
- Cost estimation
- Prompt optimization feedback

---

### ✂️ LM Studio Context Optimizer
**Purpose**: Smart truncation to fit token limits

**Inputs**:
- `text`: Content to optimize
- `max_tokens`: Target token count
- `strategy`: Truncation method
  - `end`: Keep beginning
  - `middle`: Remove middle, keep start/end
  - `smart`: Preserve specified amounts from both ends
  - `summarize`: Keep first/last sentences of paragraphs
- `preserve_start`/`preserve_end`: Token amounts to keep (smart mode)

**Outputs**:
- `optimized_text`: Truncated content
- `original_tokens`: Before optimization
- `optimized_tokens`: After optimization
- `info`: Reduction statistics

**Use Cases**:
- Fit prompts into context windows
- Conversation history management
- Document summarization

---

## Validation & Control Nodes

### ✓ LM Studio Response Validator
**Purpose**: Validate LLM outputs with automatic retry logic

**Validation Types**:
- `json`: Validate JSON format + optional schema
- `length`: Min/max character checks
- `contains`: Required text presence
- `regex`: Pattern matching
- `none`: Pass-through (no validation)

**Inputs**:
- `response`: Text to validate (force input)
- `validation_type`: Method selection
- Type-specific parameters (schema, length bounds, patterns)
- `strict_mode`: Fail workflow on error (vs. warning)

**Outputs**:
- `validated_response`: Original or error message
- `is_valid`: Boolean result
- `validation_errors`: Detailed error list
- `info`: Validation summary

**Features**:
- Custom `VALIDATE_INPUTS` method
- Schema validation for JSON (type, required fields)
- Strict mode for workflow control
- Actionable error messages

**Use Cases**:
- Ensure JSON structure for parsing
- Quality control gates
- Retry workflows on validation failure
- Data integrity checks

---

### 🎛️ LM Studio Parameter Presets
**Purpose**: Quick parameter configurations

**Presets**:
- `creative`: High randomness (temp 0.9, penalties 0.5)
- `balanced`: General purpose (temp 0.7, no penalties)
- `precise`: Focused outputs (temp 0.3)
- `factual`: Very deterministic (temp 0.1)
- `diverse`: Maximum variety (temp 0.8, penalties 1.0)
- `conversational`: Natural chat style (temp 0.7, penalties 0.3)
- `analytical`: Structured responses (temp 0.4, presence 0.2)
- `storytelling`: Engaging narratives (temp 0.85, penalties 0.4/0.6)
- `custom`: Use manual inputs

**Outputs**:
- `temperature`: Selected value
- `top_p`: Nucleus sampling
- `frequency_penalty`: Reduce repetition
- `presence_penalty`: Topic diversity
- `info`: Preset description + tips

**Features**:
- Per-parameter overrides (set to -1 or -999 to use preset)
- Usage tips based on values
- Quick switching between modes

**Use Cases**:
- Rapid experimentation
- Consistent generation styles
- Educational (understand parameter effects)

---

## Workflow Examples

### Example 1: Image Analysis → SDXL Generation
```
[Load Image] 
    ↓
[LM Studio Vision] (prompt_ready output)
    ↓
[LM Studio Prompt Enhancer] (optional: add style)
    ↓
[SDXL Checkpoint Loader] + [CLIP Text Encode]
    ↓
[K Sampler]
```

### Example 2: Conversational Workflow
```
[LM Studio Chat History] (add user message)
    ↓ (messages_json)
[LM Studio Chat History Loader] (retrieve full history)
    ↓
[LM Studio Text Generator] (context-aware response)
    ↓
[LM Studio Chat History] (add assistant response)
```

### Example 3: Safe Prompt Generation with Validation
```
[Simple Prompt Input]
    ↓
[LM Studio Token Counter] (check length)
    ↓
[LM Studio Context Optimizer] (if needed)
    ↓
[LM Studio Prompt Enhancer] (response_format="json")
    ↓
[LM Studio Response Validator] (validate JSON structure)
    ↓ (if valid)
[JSON Parser] → [SDXL]
```

### Example 4: Batch Processing with Progress
```
[Text Input: Multiple Prompts]
    ↓
[LM Studio Batch Processor]
    ↓ (results_json)
[Parse Results] → [Individual Workflows]
```

### Example 5: Parameter Experimentation
```
[LM Studio Parameter Presets] (select: "creative")
    ↓ (temperature, top_p, etc.)
[LM Studio Text Generator] (use preset values)
    ↓
[Compare with "precise" preset]
```

---

## Best Practices

### Memory Management
1. Use **Auto Unload Trigger** between prompt generation and image generation
2. Monitor model status with **Model Unload Helper**
3. Vision models need more VRAM - unload before Flux/SDXL

### Token Optimization
1. **Token Counter** before generation to predict costs
2. **Context Optimizer** to fit large prompts into limits
3. Smart truncation strategies:
   - `end`: General use (keep instructions at start)
   - `smart`: Preserve key sections
   - `summarize`: For long documents

### Quality Control
1. **Response Validator** with `strict_mode=False` for warnings
2. Enable `strict_mode=True` to halt workflow on bad outputs
3. JSON validation with schema for structured outputs
4. Use `contains` validation for required elements

### Streaming vs. Standard
- **Standard Text Gen**: Faster for short outputs, cleaner results
- **Streaming Text Gen**: Better for long outputs, live feedback, user interaction

### Parameter Selection
1. Start with **Parameter Presets** for common scenarios
2. Override individual parameters for fine-tuning
3. Use `creative` for prompts, `precise` for data extraction
4. Use `diverse` to avoid repetitive outputs in batch processing

### Chat History Management
1. Set `max_messages` based on model context limit
2. System messages are always preserved during truncation
3. Use unique `session_id` for different conversation threads
4. Reset history when starting new topics

### Model Selection
1. **Manual Selector**: When you know exact model ID
2. **Multi-Model Selector**: For dynamic workflows and availability checks
3. Set `fallback_model` for robustness
4. Use `model_filter` to auto-select appropriate type

### Vision Model Usage
1. Use `detail_level="high"` for detailed analysis
2. Use `detail_level="low"` for quick descriptions (faster)
3. JSON output requires prompt instructions (not API parameter)
4. Vision models need 120s+ timeout for complex images

### Batch Processing
1. Set `batch_delay` > 0 to avoid overwhelming server
2. Monitor `results_json` for individual failures
3. Use progress updates for long batches
4. Consider streaming for real-time feedback on single items

---

## Research-Backed Optimizations

### Based on LM Studio API (lmstudio-ai/lms)
- ✅ Streaming support via SSE
- ✅ Model management via `/v1/models` endpoint
- ✅ GPU offloading strategies
- ✅ TTL for automatic model unloading
- ✅ CLI integration for programmatic control

### Based on OpenAI Python SDK Patterns
- ✅ Structured outputs (JSON mode)
- ✅ Error handling with specific exception types
- ✅ Retry strategies (manual implementation needed)
- ✅ Token estimation and optimization
- ✅ Context management best practices

### Based on ComfyUI Node Development
- ✅ Custom `VALIDATE_INPUTS` for input validation
- ✅ `IS_CHANGED` for stateful behavior
- ✅ Progress callbacks via `set_progress()`
- ✅ `INPUT_IS_LIST`/`OUTPUT_IS_LIST` for batch processing
- ✅ Multiple outputs with clear naming
- ✅ Info panels for user feedback

---

## Troubleshooting

### "No response from LM Studio"
- Check LM Studio is running
- Verify Local Server is started (green indicator)
- Test `http://localhost:1234/v1/models` in browser
- Ensure model is loaded

### "HTTP Error 400: Bad Request"
- Vision models: Don't use `response_format` parameter (use prompt instructions)
- Check JSON payload structure
- Verify model supports requested features

### "Token limit exceeded"
- Use **Token Counter** to check before generation
- Apply **Context Optimizer** to reduce length
- Reduce `max_tokens` parameter
- Use model with larger context window

### "Streaming timeout"
- Increase timeout (default 120s for vision, 60s for text)
- Check model is actually loaded (not just downloaded)
- Verify sufficient VRAM available
- Try non-streaming mode first

### "Validation failed"
- Check validation type matches response format
- Review error message for specific issues
- Use `strict_mode=False` during development
- Verify JSON schema if using JSON validation

---

## Node Count Summary

**Total: 16 Nodes**

- **Core Generation**: 3 nodes (text, vision, prompt enhancer)
- **Advanced Generation**: 2 nodes (streaming, batch)
- **Utility**: 4 nodes (selectors, unload helpers)
- **Context Management**: 4 nodes (chat history, token counter, optimizer)
- **Validation & Control**: 2 nodes (validator, presets)
- **Plus**: 1 loader node (chat history loader)

---

## Version History

**v2.0** (November 2025)
- ✨ Added 8 new advanced nodes
- 🔧 Research-backed optimizations from LM Studio, OpenAI SDK, and ComfyUI patterns
- 📊 Token management and context optimization
- ✅ Response validation with schema support
- 🌊 Streaming support with progress updates
- 💬 Chat history management for stateful conversations
- 🎛️ Parameter presets for quick experimentation
- 📦 Batch processing capabilities

**v1.0** (Previous)
- Basic text generation
- Vision model support
- SDXL prompt enhancement
- Model selection and memory management
