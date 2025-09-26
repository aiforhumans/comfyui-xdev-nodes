# Development Nodes Usage Guide

## Overview

The **Input Dev** and **Output Dev** nodes are powerful tools for testing, debugging, and developing ComfyUI workflows. Together, they provide a complete testing environment for any ComfyUI data type.

## Quick Start

### Basic Connection Testing
The simplest use case is testing if two nodes can connect:

```
InputDev (STRING) → YourNode → OutputDev
```

This workflow:
1. **InputDev** generates a test string
2. **YourNode** processes it  
3. **OutputDev** displays the result with full analysis

### Multi-Type Testing
Test your node with different data types:

```
InputDev (STRING) → YourNode → OutputDev (input_1)
InputDev (INT) → YourNode → OutputDev (input_2) 
InputDev (IMAGE) → YourNode → OutputDev (input_3)
```

Enable "compare_inputs" on OutputDev to see how your node handles different types.

## Data Type Examples

### STRING Testing
```javascript
// InputDev Settings:
output_type: "STRING"
output_mode: "realistic" 
size_parameter: 100
custom_value: "My custom test text"

// Generates:
- Simple: "test_string"
- Realistic: "Generated test string with 100 characters: AAAA..."
- Stress Test: Unicode, special chars, extreme lengths
- Custom: "My custom test text"
```

### IMAGE Testing
```javascript
// InputDev Settings:
output_type: "IMAGE"
output_mode: "realistic"
size_parameter: 512

// Generates ComfyUI-compatible tensors:
- Shape: [1, 512, 512, 3] (Batch, Height, Width, Channels)
- Values: Random RGB in 0-1 range
- Memory: ~3MB for 512x512 image
```

### LATENT Testing  
```javascript
// InputDev Settings:
output_type: "LATENT"
output_mode: "realistic"
size_parameter: 512

// Generates:
- Format: {"samples": tensor}
- Shape: [1, 4, 64, 64] (512÷8=64 for typical VAE)
- Values: Gaussian distributed latent representation
```

### Custom Data Injection
```javascript
// InputDev Settings:
output_type: "INT"
custom_value: "42"

// Result: 42 (converted from string)
// Use for specific test cases
```

## OutputDev Analysis Modes

### Summary Mode
Basic information for quick checks:
```
Type: Tensor
Shape: (1, 512, 512, 3)
Memory Usage: 3.00 MB
```

### Detailed Mode (Default)
Adds technical details:
```
Type: Tensor
Module: torch
Shape: (1, 512, 512, 3) 
Total Elements: 786,432
Memory Usage: 3.00 MB
Data Type: torch.float32
Device: cpu
Requires Gradient: False
Is Contiguous: True
```

### Full Mode
Includes content preview and statistics:
```
[Previous details plus...]

📋 CONTENT PREVIEW:
Values: [0.2341, 0.7892, 0.1234, 0.9876, 0.4567, ... (786,427 more)]
Range: 0.0000 to 1.0000
Mean: 0.4987
```

## Advanced Workflows

### Stress Testing Pipeline
Test your nodes with extreme data:

```
InputDev (stress_test, 2048px) → YourImageNode → OutputDev (full mode)
```

This generates large images with edge cases to test memory handling and performance.

### Reproducible Testing
Use seeds for consistent test results:

```
InputDev (seed=123, STRING) → ProcessNode → OutputDev
InputDev (seed=123, STRING) → ProcessNode → OutputDev
```

Both workflows will generate identical input data for consistent testing.

### Multi-Path Comparison
Compare different processing approaches:

```
InputDev → Method1 → OutputDev (input_1)
       → Method2 → OutputDev (input_2)
       → Method3 → OutputDev (input_3)
```

Enable "compare_inputs" to see differences between methods.

### Memory Analysis
Monitor memory usage with large tensors:

```
InputDev (IMAGE, 1024px) → YourNode → OutputDev (full, save_to_file=true)
```

This creates detailed memory reports saved to timestamped files.

## Common Patterns

### Node Development Workflow
1. **Start Simple**: Use InputDev with simple mode
2. **Test Realistic**: Switch to realistic mode with typical data
3. **Stress Test**: Use stress_test mode to find edge cases
4. **Compare Results**: Use multiple inputs to verify consistency

### Debugging Workflow Issues
1. **Insert OutputDev** at problem points in your workflow
2. **Analyze Data Flow**: Check data types and shapes between nodes
3. **Compare Expected vs Actual**: Use multiple OutputDev nodes to compare
4. **Save Analysis**: Enable file export for detailed debugging sessions

### Performance Testing
1. **Generate Large Data**: Use InputDev with large size_parameter
2. **Monitor Memory**: Use OutputDev full mode to track memory usage
3. **Time Operations**: Use OutputDev to verify processing completed
4. **Document Results**: Save analysis files for performance records

## Integration with Existing Nodes

### With Image Processing Nodes
```
InputDev (IMAGE, 512px) → LoadImageBatch → YourImageProcessor → OutputDev
```

### With Text Processing Nodes  
```
InputDev (STRING, custom="Test sentence") → TextEncoder → YourTextNode → OutputDev
```

### With Model Nodes
```
InputDev (LATENT, 512px) → YourModel → OutputDev (detailed)
```

## File Export Features

When OutputDev has "save_to_file" enabled:

### File Format
```
Output Dev Node Analysis - 2025-09-26 15:30:45
============================================================

INPUT_1 Analysis:
------------------------------
Type: Tensor
Module: torch
Shape: (1, 512, 512, 3)
Total Elements: 786432
Memory Usage: 3.00 MB
...
```

### File Naming
Files are saved as: `output_dev_analysis_YYYYMMDD_HHMMSS.txt`

### Use Cases
- Document test results
- Track memory usage over time  
- Share debugging information
- Create test reports

## Troubleshooting

### OutputDev Not Showing Results
- Check ComfyUI console/terminal window
- Ensure OutputDev is connected in workflow
- Verify workflow execution completed

### InputDev Generate Errors  
- Check custom_value format for target type
- Reduce size_parameter if memory issues
- Try "simple" mode for basic testing

### Connection Issues
- Verify node IDs match in workflow JSON
- Check that ComfyUI recognizes the nodes (restart if needed)
- Use "*" (ANY) type connections for maximum compatibility

## Best Practices

### Systematic Testing
1. Start with simple data
2. Progress to realistic scenarios  
3. Test edge cases with stress mode
4. Document findings with file export

### Memory Management
- Use appropriate size_parameter values
- Monitor memory usage with full analysis mode
- Test with various image sizes progressively

### Reproducible Results
- Use consistent seeds for repeatable tests
- Document test configurations
- Save analysis files for later comparison

### Workflow Development
- Use InputDev as temporary data source during development
- Replace with real data sources when workflow is stable
- Keep OutputDev nodes for ongoing debugging