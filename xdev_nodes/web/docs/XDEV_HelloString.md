# 🔥 Hello String (XDev) - Enhanced Documentation

## Overview

The **Hello String** node is an enhanced greeting generator demonstrating XDev's comprehensive validation and documentation patterns. This node showcases best practices for ComfyUI custom node development including rich tooltips, input validation, and flexible output generation.

## Features

- ✨ **Customizable Greetings**: Multiple format styles (simple, formal, casual, technical)
- 🕒 **Optional Timestamps**: Include current time for debugging and workflow tracking
- 📝 **Custom Messages**: Add personalized text to greetings
- 🛡️ **Error Handling**: Comprehensive error recovery and reporting
- 📊 **Metadata Output**: Additional information about generated content

## Parameters

### Optional Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `custom_message` | STRING | "" | Optional custom text appended to greeting. Leave empty for default message. |
| `include_timestamp` | BOOLEAN | false | Include current timestamp in output. Useful for debugging workflows. |
| `format_style` | COMBO | "simple" | Greeting format: simple, formal, casual, or technical |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `greeting` | STRING | Generated greeting message with optional customizations |
| `metadata` | STRING | Processing information including format style and timestamp |

## Usage Examples

### Basic Usage
```
XDEV_HelloString → PreviewText
```
**Output**: "Hello ComfyUI!"

### Custom Greeting with Timestamp
```
Settings:
- custom_message: "Welcome to the workflow!"
- include_timestamp: true
- format_style: "formal"

Output: "Greetings from ComfyUI! Welcome to the workflow! (Generated: 2025-09-26 15:30:45)"
```

### Technical Style
```
Settings:
- format_style: "technical"

Output: "ComfyUI Node System: Status Active"
```

## Advanced Features

### Format Styles

- **Simple**: Basic "Hello ComfyUI!" message
- **Formal**: Professional "Greetings from ComfyUI!" tone
- **Casual**: Friendly "Hey there from ComfyUI! 👋" with emoji
- **Technical**: System-style "ComfyUI Node System: Status Active" format

### Caching Behavior

The node implements smart caching:
- **Static content**: Cached for performance
- **Dynamic timestamps**: Always refreshed when timestamp is enabled
- **Custom messages**: Cache invalidated when content changes

## Error Handling

The node includes comprehensive error handling:
- Graceful fallback to error messages on exceptions
- Detailed error reporting in metadata output
- Non-breaking operation under all conditions

## Integration Tips

1. **Debugging Workflows**: Use with timestamp enabled to track execution times
2. **User Feedback**: Combine with conditional nodes for dynamic messaging
3. **Documentation**: Use technical format for system status reporting
4. **Testing**: Simple format provides consistent output for validation

## Tooltip Reference

Hover over the `?` badges in ComfyUI to see rich documentation for each parameter, including:
- Detailed parameter descriptions
- Usage examples and recommendations
- Expected input formats and constraints
