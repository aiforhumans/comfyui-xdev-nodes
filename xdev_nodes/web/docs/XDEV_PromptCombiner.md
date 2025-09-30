# Prompt Combiner (XDev) - Documentation

## Overview

The **Prompt Combiner** node provides advanced prompt combination capabilities with multiple merging strategies, intelligent formatting options, and **chat message formatting**. It supports combining up to 4 regular prompts plus dedicated system, user, and assistant message blocks for conversational AI workflows.

## Features

- **Multiple Combination Modes**: Concatenation, weighted merging, alternating, priority-based merging, **chat format**, and **instruct format**
- **Chat Message Support**: Dedicated blocks for system, user, and assistant messages
- **Flexible Separators**: Comma, space, newline, pipe, semicolon, or custom separators  
- **Weighted Merging**: Apply individual weights to each prompt in weighted_merge mode
- **Conversational Formatting**: Professional chat and instruction templates
- **Performance Optimized**: Uses advanced caching and performance monitoring
- **Comprehensive Validation**: Input validation with detailed error reporting

## Input Parameters

### Required Parameters
- **prompt_1** (STRING): First prompt to combine
- **prompt_2** (STRING): Second prompt to combine  
- **mode** (DROPDOWN): Combination strategy
  - `concatenate`: Simple joining with separator
  - `weighted_merge`: Combine with weight syntax (prompt:weight)
  - `alternating`: Alternate between prompts
  - `priority_merge`: Sort by length, longest first
  - `chat_format`: Format as conversational messages (Role: Content)
  - `instruct_format`: Format as instruction blocks (### Role\\nContent)
- **separator** (DROPDOWN): Separator between prompts
  - `comma`: ", " (default)
  - `space`: " "
  - `newline`: "\\n"
  - `pipe`: " | "
  - `semicolon`: "; "
  - `custom`: Use custom_separator value

### Optional Parameters
- **prompt_3** (STRING): Optional third prompt
- **prompt_4** (STRING): Optional fourth prompt
- **system_message** (STRING): System message for chat/instruct formats
- **user_message** (STRING): User message for chat/instruct formats  
- **assistant_message** (STRING): Assistant message for chat/instruct formats
- **weight_1-4** (FLOAT): Individual weights for weighted_merge mode (0.1-5.0)
- **custom_separator** (STRING): Custom separator when separator="custom"
- **validate_input** (BOOLEAN): Enable input validation

## Output Types

1. **combined_prompt** (STRING): The resulting combined prompt or formatted conversation
2. **combination_info** (STRING): Information about the combination process and message types
3. **total_items** (INT): Number of non-empty prompts/messages processed

## Usage Examples

### Chat Message Formatting
```
Inputs:
- mode: "chat_format"
- system_message: "You are a creative AI assistant specialized in image generation."
- user_message: "Create a beautiful mountain landscape at sunset."
- assistant_message: "I'll create a stunning mountain landscape with warm sunset colors."

Output:
System: You are a creative AI assistant specialized in image generation.

User: Create a beautiful mountain landscape at sunset.

### Priority Merging
```
Inputs:
- prompt_1: "art"
- prompt_2: "highly detailed masterpiece"
- prompt_3: "beautiful"
- mode: "priority_merge"

Output: "highly detailed masterpiece, beautiful, art"
```

## Advanced Features

### Performance Optimization
- **Caching**: Results are cached for 10 minutes (600 seconds)
- **Performance Monitoring**: Execution time and memory usage tracked
- **Lazy Evaluation**: Only processes non-empty prompts

### Error Handling
- Graceful fallback when combination fails
- Detailed validation error messages
- Returns original prompt_1 if combination fails

### Custom Separators
```
Inputs:
- separator: "custom"
- custom_separator: " | "

Creates: "prompt1 | prompt2 | prompt3"
```

## Integration Patterns

### With Other XDev Nodes
```
XDEV_PromptCombiner → XDEV_PromptWeighter → XDEV_PromptCleaner
```

### For Prompt Engineering
```
Multiple PromptCombiners → PromptAnalyzer → PromptRandomizer
```

### Quality Control Pipeline
```
PromptCombiner → PromptCleaner → PromptAnalyzer → OutputDev
```

## Performance Notes

- **Memory Efficient**: Minimal memory overhead for prompt processing
- **Fast Processing**: Precomputed combination strategies for O(1) lookup
- **Scalable**: Handles prompts up to 100,000 characters (configurable)

## Best Practices

1. **Use Validation**: Keep `validate_input=True` for development
2. **Weighted Merging**: Use weights between 0.8-1.5 for subtle effects  
3. **Empty Prompts**: Empty prompts are automatically filtered out
4. **Performance**: Use caching effectively by reusing similar combinations
5. **Readability**: Use descriptive separators for complex prompt chains

## Common Use Cases

- **Style Transfer**: Combine content + style prompts
- **Quality Enhancement**: Add quality terms to base prompts
- **Multi-aspect Prompts**: Combine subject + environment + style
- **A/B Testing**: Create prompt variations for comparison
- **Batch Processing**: Standardize prompt formatting across workflows

## Troubleshooting

**Issue**: Empty output
- **Solution**: Check that at least one prompt has content

**Issue**: Unexpected format
- **Solution**: Verify separator choice and mode selection

**Issue**: Performance slow
- **Solution**: Enable caching and avoid extremely long prompts

This node is part of the XDev toolkit's comprehensive prompt engineering suite, designed for professional ComfyUI workflows.