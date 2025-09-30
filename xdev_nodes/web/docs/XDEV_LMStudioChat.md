# LM Studio Chat (XDev) - Documentation

## Overview

The **LM Studio Chat** node provides seamless integration with local LM Studio servers for conversational AI interactions. It features **easy-to-edit conversation history** through individual input fields and supports OpenAI-compatible API endpoints with comprehensive fallback handling.

## Features

- **Easy Conversation History**: Individual input fields for each conversation turn (no complex JSON required)
- **Local LM Studio Integration**: Direct connection to LM Studio OpenAI-compatible API
- **Graceful Fallbacks**: Automatic handling of connection issues with informative error messages
- **Flexible API Configuration**: Customizable server endpoints and model selection
- **Backward Compatibility**: Supports legacy JSON message_history format for existing workflows
- **Performance Optimized**: Advanced caching and performance monitoring with TTL-based optimization
- **Professional Error Handling**: Detailed error reporting and connection diagnostics

## Input Parameters

### Required Parameters
- **prompt** (STRING): Main conversation prompt or user message
- **server_url** (STRING): LM Studio server URL (default: "http://localhost:1234")
- **model** (STRING): Model identifier (default: "local-model")

### Optional Parameters - Easy History Editing
- **history_user_1** (STRING): First user message in conversation history
- **history_assistant_1** (STRING): First assistant response in conversation history
- **history_user_2** (STRING): Second user message in conversation history
- **history_assistant_2** (STRING): Second assistant response in conversation history
- **history_user_3** (STRING): Third user message in conversation history
- **history_assistant_3** (STRING): Third assistant response in conversation history

### Optional Parameters - Configuration
- **message_history** (STRING): Legacy JSON format for complex conversation histories
- **max_tokens** (INT): Maximum tokens for response (1-4096, default: 150)
- **temperature** (FLOAT): Sampling temperature (0.0-2.0, default: 0.7)
- **validate_input** (BOOLEAN): Enable input validation (default: True)

## Output Types

1. **response** (STRING): The AI model's response text
2. **conversation_info** (STRING): Information about the conversation including message count and configuration

## Usage Examples

### Basic Chat
```
Simple conversation with current prompt only:
- prompt: "What is machine learning?"
- server_url: "http://localhost:1234"
- model: "local-model"
```

### Conversation with Easy History
```
Multi-turn conversation using individual history fields:
- history_user_1: "Hello, I'm learning about AI"
- history_assistant_1: "Great! AI is a fascinating field. What specific area interests you?"
- history_user_2: "I want to understand neural networks"
- history_assistant_2: "Neural networks are the foundation of modern AI..."
- prompt: "Can you explain backpropagation?"
```

### Legacy JSON History (Backward Compatibility)
```
Complex conversation using JSON format:
- message_history: '[{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]'
- prompt: "Continue our discussion"
```

## Conversation History Behavior

### Message Building Priority
1. **Individual Fields First**: history_user_1-3 and history_assistant_1-3 are processed in chronological order
2. **Legacy JSON Fallback**: If individual fields are empty, attempts to parse message_history JSON
3. **Current Prompt**: Always added as the final user message

### Chronological Ordering
Messages are automatically ordered chronologically:
1. history_user_1 → history_assistant_1
2. history_user_2 → history_assistant_2  
3. history_user_3 → history_assistant_3
4. Current prompt (as final user message)

### Empty Field Handling
- Empty individual history fields are automatically skipped
- Only non-empty conversation turns are included in the message list
- Maintains proper conversation flow without placeholder messages

## Server Configuration

### LM Studio Setup
1. Start LM Studio with local server enabled
2. Enable OpenAI-compatible API endpoint
3. Default URL: `http://localhost:1234`
4. Verify model is loaded and available

### Alternative Servers
Compatible with any OpenAI-compatible API server:
- **Ollama**: `http://localhost:11434`
- **Text Generation WebUI**: `http://localhost:5000`
- **Custom Servers**: Any server implementing OpenAI chat/completions endpoint

## Error Handling

### Connection Issues
- **Server Unreachable**: Returns formatted error message with connection details
- **Invalid Model**: Provides model availability information
- **API Errors**: Detailed HTTP error reporting with status codes

### Input Validation
- **URL Validation**: Checks server URL format and accessibility
- **Parameter Bounds**: Validates max_tokens, temperature within acceptable ranges
- **JSON Parsing**: Graceful handling of malformed message_history JSON

## Performance Features

### Caching System
- **TTL-Based Caching**: Responses cached for 300 seconds (5 minutes)
- **Parameter-Aware**: Cache keys include all conversation parameters
- **Memory Efficient**: Automatic cache cleanup and size management

### Monitoring
- **Performance Tracking**: All API calls monitored with detailed timing
- **Error Metrics**: Connection failure rates and error categorization
- **Usage Statistics**: Token usage and response time analytics

## Dependencies

### Required Libraries
- **httpx**: Primary HTTP client for async/sync requests (preferred)
- **requests**: Fallback HTTP client for compatibility
- **json**: Standard library for message parsing

### Graceful Degradation
- Falls back to requests library if httpx unavailable
- Provides informative errors if no HTTP client available
- Maintains functionality across different Python environments

## Technical Implementation

### API Integration
- **OpenAI-Compatible**: Uses standard chat/completions endpoint format
- **Async Support**: Leverages httpx for improved performance when available
- **Timeout Handling**: 30-second timeout with proper error messaging

### Message Format
```json
{
  "model": "local-model",
  "messages": [
    {"role": "user", "content": "history_user_1"},
    {"role": "assistant", "content": "history_assistant_1"},
    {"role": "user", "content": "current_prompt"}
  ],
  "max_tokens": 150,
  "temperature": 0.7
}
```

### Response Processing
- Extracts content from OpenAI response format
- Handles both streaming and non-streaming responses
- Provides detailed error information for debugging

## Category
**XDev/LLM/Integration**

## Version History
- **v0.6.0**: Added easy-to-edit history fields (history_user_1-3, history_assistant_1-3)
- **v0.5.0**: Initial release with JSON message_history support
- **v0.5.0**: Performance framework integration and caching system