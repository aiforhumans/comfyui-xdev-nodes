# Phase 5: LM Studio Local API Integration

## Overview
Phase 5 introduces professional-grade integration with LM Studio and other local Language Model servers. This integration provides seamless connectivity to local LLMs running on your machine, enabling private, high-performance AI chat completions within ComfyUI workflows.

## New Node (Phase 5)

### XDEV_LMStudioChat (XDev)
**Purpose**: Connect to LM Studio local API for chat completions with advanced configuration
**Category**: `XDev/LLM/Integration`

**Key Features**:
- **OpenAI-Compatible API**: Full support for OpenAI chat completions format
- **Automatic Server Discovery**: Scans common ports (1234, 8000, 8080, 11434) for running servers
- **Configuration Presets**: 5 presets (creative, balanced, focused, precise, custom) for different use cases
- **Message History Management**: Supports conversation context and system prompts
- **Streaming Support**: Both streaming and non-streaming responses (experimental)
- **Robust Error Handling**: Graceful fallbacks and comprehensive error messages
- **Performance Monitoring**: Built-in performance tracking and caching
- **HTTP Client Fallbacks**: Supports both httpx and requests with automatic fallback

## Technical Implementation

### Supported Local LLM Servers
- **LM Studio**: Primary target with default port 1234
- **Ollama**: Port 11434 support with health checks
- **vLLM**: Port 8000 compatibility
- **Any OpenAI-compatible API**: Custom URLs supported

### Configuration Presets
```python
"creative": {"temperature": 0.9, "top_p": 0.9, "max_tokens": 2048}
"balanced": {"temperature": 0.7, "top_p": 0.8, "max_tokens": 1024}
"focused":  {"temperature": 0.3, "top_p": 0.7, "max_tokens": 512}
"precise":  {"temperature": 0.1, "top_p": 0.5, "max_tokens": 256}
"custom":   {"temperature": custom, "top_p": custom, "max_tokens": custom}
```

### Input Parameters

#### Required Inputs
- **prompt** (STRING, multiline): The user message to send to the LLM
- **server_url** (STRING): LM Studio server URL (default: http://localhost:1234)
- **model** (STRING): Model name or ID (auto-detected if available)
- **preset** (CHOICE): Configuration preset for different use cases

#### Optional Inputs
- **system_prompt** (STRING, multiline): System message to set LLM behavior
- **message_history** (STRING, multiline): Previous conversation in JSON format
- **temperature** (FLOAT, 0.0-2.0): Response randomness (0=deterministic, 2=very random)
- **max_tokens** (INT, 1-8192): Maximum tokens to generate
- **top_p** (FLOAT, 0.0-1.0): Nucleus sampling threshold
- **stream** (BOOLEAN): Enable streaming responses (experimental)
- **auto_detect_server** (BOOLEAN): Automatically detect running servers
- **timeout** (INT, 5-300): Request timeout in seconds
- **validate_input** (BOOLEAN): Enable input validation

#### Outputs
1. **response** (STRING): The LLM's generated response
2. **full_conversation** (STRING): Complete conversation history in JSON format
3. **server_info** (STRING): Server status, available models, and connection details
4. **generation_stats** (STRING): Performance metrics and generation statistics

## Usage Patterns

### Basic Chat Completion
```
InputDev(STRING) → LMStudioChat → OutputDev
```
- Simple single-turn conversation
- Uses balanced preset for general purpose responses

### Advanced Conversation Management
```
PromptCombiner → LMStudioChat → PromptAnalyzer → OutputDev
```
- Combine multiple prompts before sending to LLM
- Analyze the response structure and quality

### Creative Workflows
```
PromptMatrix → LMStudioChat(creative) → PromptCleaner → StyleBuilder
```
- Generate multiple prompt variations
- Use creative preset for imaginative responses
- Clean and enhance the output for further processing

### System-Guided Responses
```
PersonBuilder → LMStudioChat(focused) → PromptWeighter → OutputDev
```
- Build character-specific system prompts
- Use focused preset for consistent character responses
- Weight important aspects of the response

## Server Configuration

### LM Studio Setup
1. **Install LM Studio**: Download from https://lmstudio.ai/
2. **Load a Model**: Choose and download a model (e.g., Llama, Mistral, CodeLlama)
3. **Start Local Server**: 
   - Click "Local Server" tab in LM Studio
   - Select your model
   - Click "Start Server"
   - Default URL: http://localhost:1234

### Automatic Detection
The node automatically scans these common ports:
- **1234**: LM Studio default
- **8000**: vLLM default  
- **8080**: llamafile default
- **11434**: Ollama default
- **5000, 3000**: Alternative local server ports

### Custom Server Configuration
- Set `server_url` to your custom endpoint
- Ensure the server implements OpenAI-compatible `/v1/chat/completions`
- Use `/v1/models` endpoint for model discovery
- Health checks via `/health` or `/v1/models`

## Performance Features

### Caching Strategy
- **Server Detection**: Cached for 5 minutes to avoid repeated scans
- **Server Info**: Cached for 1 minute to reduce API calls
- **Performance Monitoring**: All operations tracked with @performance_monitor

### Error Handling
- **HTTP Client Fallbacks**: httpx → requests → graceful error
- **Connection Timeouts**: Configurable with sensible defaults
- **Input Validation**: Comprehensive validation with helpful error messages
- **Server Health Checks**: Automatic detection of offline servers

### Memory Management
- **Lazy Loading**: HTTP clients loaded only when needed
- **Efficient JSON Parsing**: Minimal memory footprint for large responses
- **Resource Cleanup**: Proper connection handling and cleanup

## Integration Examples

### Example 1: Simple Chat
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "server_url": "http://localhost:1234",
  "model": "llama-3.1-8b",
  "preset": "balanced"
}
```

### Example 2: Creative Writing
```json
{
  "prompt": "Write a short story about a time-traveling cat",
  "system_prompt": "You are a creative writer specializing in whimsical fantasy stories",
  "preset": "creative",
  "temperature": 0.9,
  "max_tokens": 2048
}
```

### Example 3: Technical Analysis
```json
{
  "prompt": "Review this code for potential security issues: [code here]",
  "system_prompt": "You are a senior security engineer. Provide detailed analysis.",
  "preset": "focused",
  "temperature": 0.2,
  "max_tokens": 1024
}
```

### Example 4: Conversation Context
```json
{
  "prompt": "What do you think about that solution?",
  "message_history": "[{\"role\":\"user\",\"content\":\"How do I solve this math problem?\"},{\"role\":\"assistant\",\"content\":\"Here's the step-by-step solution...\"}]",
  "preset": "balanced"
}
```

## Dependencies and Requirements

### HTTP Client Libraries (Optional)
The node supports multiple HTTP clients with graceful fallbacks:

1. **httpx** (Recommended): `pip install httpx`
   - Modern async HTTP client
   - Better streaming support
   - More robust connection handling

2. **requests** (Fallback): `pip install requests`
   - Widely available HTTP client
   - Simpler API but less features
   - Good compatibility with older systems

3. **No HTTP Client**: Graceful error message with installation instructions

### LM Studio Compatibility
- **LM Studio 0.2.19+**: Full compatibility with all features
- **OpenAI API Format**: Standard chat completions endpoint
- **Model Support**: Any model loaded in LM Studio
- **Streaming**: Experimental support for Server-Sent Events

## Error Messages and Troubleshooting

### Common Issues

1. **"No HTTP client available"**
   - Install httpx: `pip install httpx`
   - Or install requests: `pip install requests`

2. **"Invalid server URL"**
   - Check URL format: http://localhost:1234
   - Ensure protocol (http/https) is included

3. **"Connection timeout"**
   - Check if LM Studio server is running
   - Verify the correct port number
   - Increase timeout value if needed

4. **"Unexpected response format"**
   - Ensure server implements OpenAI-compatible API
   - Check if model is properly loaded in LM Studio

### Debug Information
The node provides detailed debug information:
- **Server Info**: Connection status, available models
- **Generation Stats**: Timing, token counts, configuration
- **Performance Metrics**: Automatic performance monitoring

## Future Enhancements

Phase 5 establishes the foundation for local LLM integration. Potential future additions:

### Phase 6 Possibilities
- **Multi-Model Management**: Switch between different models dynamically
- **Embedding Generation**: Support for text embeddings via local APIs
- **Function Calling**: OpenAI-compatible function calling support
- **Advanced Streaming**: Real-time token streaming with UI updates
- **Model Performance Analysis**: Benchmarking and comparison tools
- **Custom API Adapters**: Support for non-OpenAI compatible APIs

## Security Considerations

### Local-First Approach
- **Privacy**: All data stays on your local machine
- **No Cloud Dependencies**: Works completely offline
- **Secure by Default**: No API keys or tokens sent to external services

### Network Security
- **Local Network Only**: Default configuration uses localhost
- **Configurable Timeouts**: Prevents hanging connections
- **Input Validation**: Prevents injection attacks

### Best Practices
- Keep LM Studio and models updated
- Monitor system resources during generation
- Use appropriate timeout values for your use case
- Validate all user inputs in production workflows

## Performance Benchmarks

### Typical Performance (Local Hardware)
- **Model Loading**: 5-30 seconds (depending on model size)
- **First Token Latency**: 100-500ms (varies by model)
- **Generation Speed**: 10-50 tokens/second (hardware dependent)
- **Memory Usage**: 4-16GB RAM (model size dependent)

### Optimization Tips
- **Use SSD Storage**: Faster model loading
- **Sufficient RAM**: Avoid swapping during generation
- **GPU Acceleration**: Significantly faster than CPU-only
- **Batch Processing**: Better throughput for multiple requests

This comprehensive LM Studio integration makes local LLM usage in ComfyUI workflows seamless, private, and highly configurable.