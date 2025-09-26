# Output Dev Node (XDev)

## Overview

The **Output Dev** node is a universal debugging and testing output node that can receive and analyze **any type** of ComfyUI data. It's designed to be the ultimate debugging tool for workflow development, providing comprehensive analysis of data flowing through your ComfyUI workflows.

## Features

### Universal Input Acceptance
- **Primary Input**: Accepts any ComfyUI data type via `*` (universal) type
- **Secondary & Tertiary Inputs**: Optional additional inputs for comparison
- **Zero Conversion**: Displays data as-is without modification or conversion

### Comprehensive Analysis Modes
- **Summary**: Basic type and size information
- **Detailed**: Adds shape, device, and memory information
- **Full**: Includes content preview and statistical analysis

### Advanced Debugging Features
- **Multi-Input Comparison**: Compare up to 3 different data streams
- **File Export**: Save analysis results to timestamped text files
- **Memory Analysis**: Display memory usage for tensor objects
- **Content Preview**: Safe preview of actual data values

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **input_1** | `*` (Any) | Required | Primary input - accepts any ComfyUI data type |
| **input_2** | `*` (Any) | Optional | Secondary input for comparison |
| **input_3** | `*` (Any) | Optional | Tertiary input for comparison |
| **display_level** | Choice | "detailed" | Analysis detail level: summary/detailed/full |
| **save_to_file** | Boolean | False | Save analysis to timestamped text file |
| **compare_inputs** | Boolean | False | Compare multiple inputs when connected |

## Output Behavior

This is an **OUTPUT_NODE** - it terminates workflow execution and displays results in the console/terminal. It does not return any data to other nodes.

## Analysis Information Displayed

### For All Data Types
- Python type name and module
- Memory usage (for tensor objects)
- Basic size/length information

### For Tensors (IMAGE, LATENT, etc.)
- Shape and total element count
- Data type (dtype) and device (CPU/GPU)
- Gradient tracking status
- Memory contiguity status
- Value range (min/max/mean) when available

### For Strings
- Character and word count
- Content preview (first 100 characters)

### For Lists/Dictionaries
- Length and structure information
- Preview of first few items/keys

## Common Use Cases

### 1. Debugging Node Connections
Connect any node output to verify the data type and structure:
```
YourNode → OutputDev
```

### 2. Comparing Multiple Outputs
Compare outputs from different nodes or processing paths:
```
NodeA → OutputDev (input_1)
NodeB → OutputDev (input_2)
```
Enable "compare_inputs" to see differences.

### 3. Memory Usage Analysis
Set display_level to "full" to analyze memory usage of large tensors:
- IMAGE tensors: See dimensions and memory consumption
- LATENT data: Analyze latent space dimensions
- MODEL outputs: Check tensor sizes and device placement

### 4. Workflow Documentation
Enable "save_to_file" to create permanent records of data analysis for documentation or debugging later.

## Example Outputs

### Simple String Analysis
```
📊 INPUT_1 ANALYSIS:
------------------------------
Type: str
Module: builtins
Characters: 12
Words: 2
```

### Image Tensor Analysis
```
📊 INPUT_1 ANALYSIS:
------------------------------
Type: Tensor
Module: torch
Shape: (1, 512, 512, 3)
Total Elements: 786,432
Memory Usage: 3.00 MB
Data Type: torch.float32
Device: cpu
Requires Gradient: False
Is Contiguous: True

📋 CONTENT PREVIEW:
Values: [0.2341, 0.7892, 0.1234, 0.9876, 0.4567, ... (786,427 more)]
Range: 0.0000 to 1.0000
Mean: 0.4987
```

### Multi-Input Comparison
```
🔄 INPUT COMPARISON (2 inputs):
----------------------------------------
Types: INPUT_1: Tensor, INPUT_2: Tensor
✅ All inputs have the same type
Shapes: INPUT_1: (1, 512, 512, 3), INPUT_2: (1, 256, 256, 3)
⚠️ Different shapes detected
```

## Integration Tips

### With Image Processing
```
LoadImage → ImageProcessingNode → OutputDev
                                   ↑
                              Set to "full" mode to see
                              pixel value ranges and statistics
```

### With Model Outputs
```
ModelNode → OutputDev (input_1)
          → AnotherModel → OutputDev (input_2)
```
Use comparison mode to analyze different model outputs.

### Performance Monitoring
Enable "save_to_file" when processing large batches to track memory usage patterns over time.

## Technical Notes

### Output Node Behavior
- This node has `OUTPUT_NODE = True`, meaning it forces execution and terminates the workflow branch
- Results are displayed in the ComfyUI console/terminal, not in the web interface
- Does not return data to subsequent nodes

### Memory Safety
- Uses safe tensor access methods to prevent crashes
- Handles missing torch gracefully with fallback analysis
- Limits content preview size to prevent console overflow

### File Export Format
When "save_to_file" is enabled, creates files named:
`output_dev_analysis_YYYYMMDD_HHMMSS.txt`

## Troubleshooting

### No Output Visible
- Check ComfyUI console/terminal window
- Ensure node is connected and workflow is executed
- Verify input connections are properly linked

### Torch-Related Errors
- Node works without torch installation
- Some advanced analysis requires torch for tensor objects
- Basic analysis available for all data types

### Large Data Analysis
- Use "summary" mode for very large tensors to avoid performance issues
- "full" mode may take longer with huge datasets
- Consider using file export for detailed analysis of large data