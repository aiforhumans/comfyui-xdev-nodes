# Input Dev Node (XDev)

## Overview

The **Input Dev** node is a universal test data generator that can create and output **any type** of ComfyUI data for testing, debugging, and workflow development. It's the perfect companion to Output Dev, allowing you to generate test data without needing actual source files or complex setups.

## Features

### Universal Data Generation
- **8 Data Types**: STRING, INT, FLOAT, IMAGE, LATENT, LIST, DICT, MOCK_TENSOR
- **3 Generation Modes**: Simple, Realistic, Stress Test
- **Custom Values**: Use your own data instead of generated values
- **Reproducible**: Seed-based generation for consistent results

### Advanced Generation Options
- **Size Control**: Configurable dimensions for images, lists, and tensors
- **Stress Testing**: Generate edge cases and extreme values
- **Metadata Output**: Detailed information about generated data
- **Memory Efficient**: Smart sizing to prevent memory overflow

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **output_type** | Choice | "STRING" | Type of data to generate |
| **output_mode** | Choice | "realistic" | Generation complexity level |
| **custom_value** | String | "" | Custom value to use (will be converted to target type) |
| **size_parameter** | Int | 512 | Size for images, lists, tensor dimensions |
| **seed** | Int | 0 | Random seed for reproducible generation |
| **include_metadata** | Boolean | True | Include descriptive metadata output |

## Output Types

| Type | Returns | Description |
|------|---------|-------------|
| **Generated Data** | `*` (Any) | The generated data of the specified type |
| **Metadata** | `STRING` | Description of the generated data |

## Data Type Details

### STRING Generation
- **Simple**: Basic test string ("test_string")
- **Realistic**: Descriptive string with specified character count
- **Stress Test**: Unicode characters, special symbols, extreme lengths

### INT Generation
- **Simple**: Fixed value (42)
- **Realistic**: Random integers in practical range (-1000 to 1000)
- **Stress Test**: Extreme values (max/min int32, zero, ±1)

### FLOAT Generation
- **Simple**: Mathematical constant (3.14159)
- **Realistic**: Random floats in practical range (-100.0 to 100.0)
- **Stress Test**: Infinity, negative infinity, very small/large values

### IMAGE Generation
Creates ComfyUI-compatible IMAGE tensors in **[Batch, Height, Width, Channels]** format:
- **Simple**: 1x1x1x3 single pixel (black)
- **Realistic**: Square images with random RGB values (0-1 range)
- **Stress Test**: Large images up to specified size limit

### LATENT Generation
Creates ComfyUI-compatible LATENT dictionaries:
- **Format**: `{"samples": tensor}` with 4-channel latent space
- **Size**: Automatically scaled (image_size ÷ 8 for typical VAE)
- **Values**: Gaussian distributed for realistic latent representation

### LIST Generation
- **Simple**: [1, 2, 3]
- **Realistic**: Random integers, configurable length
- **Stress Test**: Mixed types, edge cases, nested structures

### DICT Generation
- **Simple**: {"key": "value", "number": 42}
- **Realistic**: Multiple key-value pairs with varied data types
- **Stress Test**: Unicode keys, extreme values, deep nesting

### MOCK_TENSOR Generation
Creates tensor-like objects when torch is unavailable:
- **Simulated Properties**: shape, dtype, device, requires_grad
- **Safe Methods**: numel(), element_size(), is_contiguous()
- **Debugging**: Useful for testing without torch dependencies

## Generation Modes Explained

### Simple Mode
- **Purpose**: Minimal, predictable data
- **Use Case**: Basic connection testing
- **Characteristics**: Small, consistent values
- **Performance**: Very fast generation

### Realistic Mode (Default)
- **Purpose**: Practical, representative data
- **Use Case**: Typical workflow testing
- **Characteristics**: Random but reasonable values
- **Performance**: Balanced speed and realism

### Stress Test Mode
- **Purpose**: Edge cases and extreme scenarios
- **Use Case**: Robustness testing and debugging
- **Characteristics**: Large values, special cases, boundary conditions
- **Performance**: May be slower for large data

## Common Use Cases

### 1. Basic Node Testing
Generate simple data to test node connections:
```
InputDev (STRING, simple) → YourTextNode → OutputDev
```

### 2. Image Processing Workflows
Create test images without loading files:
```
InputDev (IMAGE, realistic, 512px) → ImageProcessor → OutputDev
```

### 3. Stress Testing Nodes
Test node robustness with extreme values:
```
InputDev (IMAGE, stress_test, 2048px) → YourNode → OutputDev
```

### 4. Reproducible Testing
Use fixed seeds for consistent test results:
```
InputDev (seed=123) → ProcessingNode → OutputDev
```

### 5. Custom Data Injection
Use custom_value to inject specific test data:
```
InputDev (STRING, custom_value="Special Test Case") → Node → OutputDev
```

## Example Configurations

### Testing Image Processing
```
Output Type: IMAGE
Mode: realistic  
Size Parameter: 512
Seed: 42
Result: 1×512×512×3 tensor with random RGB values
```

### Testing String Processing
```
Output Type: STRING
Mode: stress_test
Size Parameter: 1000
Custom Value: ""
Result: 1000-character string with Unicode and special characters
```

### Testing Latent Processing
```
Output Type: LATENT
Mode: realistic
Size Parameter: 512
Result: {"samples": 1×4×64×64 tensor} (512÷8=64)
```

### Custom Value Conversion
```
Output Type: INT
Custom Value: "42.7"
Result: 42 (converted from string to integer)
```

## Metadata Output Examples

When `include_metadata` is enabled, the second output provides detailed information:

```
"Type: IMAGE | Mode: realistic | Size Parameter: 512 | Seed: 42 | Shape: (1, 512, 512, 3)"
```

```
"Type: STRING | Mode: stress_test | Size Parameter: 100 | Seed: 0 | String Length: 100"
```

## Integration Patterns

### With Output Dev
Perfect testing pair for complete data analysis:
```
InputDev → ProcessingNode → OutputDev
```

### Comparison Testing
Generate different data types for comparison:
```
InputDev (IMAGE, simple) → OutputDev (input_1)
InputDev (IMAGE, realistic) → OutputDev (input_2)
```

### Workflow Development
Use as temporary data source while building workflows:
```
InputDev → Node1 → Node2 → Node3 → OutputDev
```
Replace with real data sources when ready.

## Performance Considerations

### Memory Usage
- **Large Images**: Size parameter capped at reasonable limits
- **Tensors**: Memory usage scales with size³ for 3D data
- **Lists**: Generation time scales linearly with length

### Generation Speed
- **Simple Mode**: Near-instantaneous
- **Realistic Mode**: Fast for most sizes
- **Stress Test**: May take longer for large/complex data

### Torch Dependencies
- **With Torch**: Real tensor generation for maximum compatibility
- **Without Torch**: Mock objects that behave like tensors
- **Fallback**: Always functional regardless of environment

## Technical Details

### Reproducible Generation
- Uses Python's `random` module with configurable seed
- Same seed + parameters = identical output
- Useful for consistent testing across sessions

### ComfyUI Compatibility
- **IMAGE Format**: Follows ComfyUI [B,H,W,C] convention
- **LATENT Format**: Proper `{"samples": tensor}` structure
- **Type System**: Outputs work with all ComfyUI nodes

### Caching Behavior
The `IS_CHANGED` method ensures proper caching:
- Different parameters = different cache key
- Same parameters = reuses cached result
- Efficient for repeated generations

## Troubleshooting

### Import Errors
- Node works without torch installation
- Mock tensors created when torch unavailable
- All basic types work in any environment

### Large Data Generation
- Adjust size_parameter if memory issues occur
- Use "simple" mode for basic testing
- Monitor system resources with large tensors

### Custom Value Conversion
- Strings converted to target types when possible
- Invalid conversions fall back to default values
- Check metadata output for conversion details

### Seed Consistency
- Use same seed for reproducible results
- Different seeds = different random patterns
- Seed affects all random generation in the node