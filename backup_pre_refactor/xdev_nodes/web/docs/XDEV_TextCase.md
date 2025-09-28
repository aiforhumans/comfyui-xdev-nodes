# XDEV_TextCase Node Documentation

## Overview
The **Text Case Converter (XDev)** node provides comprehensive text case conversion capabilities with 9 different case formats. This Phase 1 foundation node demonstrates XDev patterns for simple, focused functionality with rich documentation and validation.

## Features
- **9 Case Formats**: lower, upper, title, capitalize, camel, pascal, snake, kebab, constant
- **Precomputed Operations**: Efficient conversion using precomputed method mapping
- **Rich Metadata**: Returns original case analysis and conversion information
- **Input Validation**: Optional validation with detailed error reporting
- **Multiline Support**: Handles multiline text while preserving newlines

## Inputs

### Required
- **text** (STRING): The text content to convert case for
  - Default: "Hello World"  
  - Supports multiline input
  - Preserves newlines during conversion
  
- **case_type** (DROPDOWN): Case conversion method
  - **lower**: "hello world"
  - **upper**: "HELLO WORLD"
  - **title**: "Hello World" 
  - **capitalize**: "Hello world"
  - **camel**: "helloWorld"
  - **pascal**: "HelloWorld"
  - **snake**: "hello_world"
  - **kebab**: "hello-world"
  - **constant**: "HELLO_WORLD"

### Optional  
- **validate_input** (BOOLEAN): Enable input validation
  - Default: True
  - Disable for performance in trusted workflows

## Outputs
1. **converted_text** (STRING): Text converted to specified case
2. **original_case** (STRING): Analysis of original text case characteristics
3. **conversion_info** (STRING): Detailed conversion metadata and statistics

## Usage Examples

### Basic Case Conversion
```
Input: "Hello World", case_type: "snake"
Output: "hello_world"
```

### Programming Identifier Conversion
```
Input: "user name field", case_type: "camel"  
Output: "userNameField"
```

### Constant Generation
```
Input: "api base url", case_type: "constant"
Output: "API_BASE_URL"
```

## Technical Details

### Performance Optimizations
- **Precomputed Methods**: All case conversion functions are precomputed for O(1) lookup
- **Lazy Validation**: Optional input validation can be disabled for performance
- **Efficient Algorithms**: Uses optimized string operations with minimal allocations

### Error Handling
- Comprehensive input validation with detailed error messages
- Graceful degradation on conversion errors
- Preserves original text on failure with error information

### Integration Patterns
- **Universal Testing**: Use `InputDev(STRING) → TextCase → OutputDev` 
- **Text Processing Chains**: Combine with other text nodes for complex operations
- **Workflow Integration**: Outputs work seamlessly with ComfyUI string inputs

## Algorithm Details

### Case Conversion Methods
| Method | Algorithm | Example |
|--------|-----------|---------|
| lower | `text.lower()` | "hello world" |
| upper | `text.upper()` | "HELLO WORLD" |
| title | `text.title()` | "Hello World" |
| capitalize | `text.capitalize()` | "Hello world" |
| camel | Custom algorithm with first char lowercase | "helloWorld" |
| pascal | `text.title().replace(" ", "")` | "HelloWorld" |
| snake | `text.lower().replace(" ", "_")` | "hello_world" |
| kebab | `text.lower().replace(" ", "-")` | "hello-world" |
| constant | `text.upper().replace(" ", "_")` | "HELLO_WORLD" |

### Validation Logic
1. **Type Check**: Ensures input is string type
2. **Method Validation**: Verifies case_type is supported
3. **Error Recovery**: Returns detailed error information on failure

## Best Practices
- **Performance**: Disable validation in trusted, high-performance workflows
- **Chaining**: Use with other text processing nodes for complex transformations
- **Testing**: Always test with InputDev/OutputDev for comprehensive validation
- **Documentation**: Use conversion_info output for workflow documentation

## Troubleshooting

### Common Issues
1. **Input Type Error**: Ensure input is STRING type, not other data types
2. **Invalid Case Type**: Use only supported case conversion methods
3. **Empty Results**: Check that input text is not empty or whitespace-only

### Performance Tips
- Disable validation for repeated operations on trusted data
- Use precomputed case types instead of dynamic string building
- Consider caching results for identical inputs in loops

## Related Nodes
- **AppendSuffix**: Text modification and decoration
- **InputDev**: Universal data generation for testing
- **OutputDev**: Comprehensive output analysis and validation