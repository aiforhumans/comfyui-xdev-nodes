# 🔥 Pick Image by Brightness (XDev) - Enhanced Documentation

## Overview

The **Pick by Brightness** node is an advanced image selector demonstrating XDev's robust fallback implementations and comprehensive validation patterns. This node analyzes image brightness using multiple algorithms and automatically selects the optimal processing method (torch → numpy → pure Python).

## Features

- 🖼️ **Multi-Format Support**: Works with ComfyUI IMAGE tensors, numpy arrays, and pure Python lists
- ⚡ **Smart Fallbacks**: Automatic torch → numpy → Python processing chain
- 🧮 **Multiple Algorithms**: Average, weighted, and luminance brightness calculations
- 🛡️ **Comprehensive Validation**: Detailed error checking with informative messages
- 📊 **Rich Metadata**: Processing method and brightness score reporting
- 🚀 **Performance Optimized**: Uses fastest available method (GPU when possible)

## Parameters

### Required Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `images` | IMAGE | - | Batch of input images in [B,H,W,C] format. Minimum 2 images required for comparison. |
| `mode` | COMBO | "brightest" | Selection criteria: "brightest" or "darkest" |

### Optional Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `algorithm` | COMBO | "average" | Brightness calculation: "average", "weighted", or "luminance" |
| `validate_input` | BOOLEAN | true | Enable comprehensive input validation with detailed error messages |
| `return_metadata` | BOOLEAN | false | Return detailed processing information and brightness scores |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `selected_image` | IMAGE | The brightest or darkest image from the batch |
| `brightness_score` | FLOAT | Numerical brightness score of selected image (0.0-1.0) |
| `processing_info` | STRING | Processing method used and additional metadata |

## Brightness Algorithms

### Average (Default)
```
Simple RGB mean: (R + G + B) / 3
```
- **Use Case**: General purpose brightness comparison
- **Performance**: Fastest calculation
- **Accuracy**: Good for most images

### Weighted
```
Perceptual weighting: 0.3*R + 0.59*G + 0.11*B
```
- **Use Case**: Human-perceived brightness
- **Performance**: Fast with better accuracy
- **Accuracy**: Better matches human vision

### Luminance
```
Standard luminance: 0.299*R + 0.587*G + 0.114*B
```
- **Use Case**: Professional color analysis
- **Performance**: Slightly slower but most accurate
- **Accuracy**: Industry standard luminance calculation

## Processing Methods

### 1. Torch Processing (Preferred)
- **Availability**: When PyTorch is installed and input is tensor
- **Performance**: GPU acceleration available
- **Accuracy**: Full precision floating point
- **Features**: All algorithms supported

### 2. NumPy Processing (Fallback)
- **Availability**: When torch unavailable but numpy present
- **Performance**: CPU optimized operations
- **Accuracy**: High precision
- **Features**: All algorithms supported

### 3. Pure Python (Ultimate Fallback)
- **Availability**: Always available
- **Performance**: Slowest but most compatible
- **Accuracy**: Basic precision
- **Features**: Simple average algorithm only

## Usage Examples

### Basic Brightness Selection
```
LoadImage (batch) → XDEV_PickByBrightness → PreviewImage

Settings:
- mode: "brightest"
- algorithm: "average"

Output: Brightest image from batch with score and method info
```

### Professional Luminance Analysis
```
ImageBatch → XDEV_PickByBrightness → [Analysis Chain]

Settings:
- mode: "darkest"
- algorithm: "luminance"
- return_metadata: true

Output: Most accurate darkest image with detailed processing info
```

### Validation-Disabled Fast Processing
```
Settings:
- validate_input: false  # Skip validation for speed
- algorithm: "average"   # Fastest algorithm

Use Case: High-performance batch processing where inputs are guaranteed valid
```

## Validation Features

### Comprehensive Input Validation

When `validate_input` is enabled (recommended):

#### Batch Size Validation
- **Minimum**: 2 images required for comparison
- **Maximum**: 100 images supported (performance limit)
- **Error**: Detailed batch size information

#### Data Type Validation
- **Input Checking**: Validates proper image tensor/array format
- **Null Checking**: Prevents processing of None/empty inputs
- **Format Validation**: Ensures compatible data structures

#### Parameter Validation
- **Mode Validation**: Ensures "brightest" or "darkest" only
- **Algorithm Validation**: Checks supported algorithm names
- **Range Checking**: Validates reasonable input ranges

### Error Messages

Detailed error reporting includes:
- Specific validation failure reasons
- Current vs. expected input formats
- Suggested corrections for common issues
- Processing method attempted when errors occur

## Performance Characteristics

### Processing Speed (Relative)
1. **Torch + GPU**: ~100x (fastest)
2. **Torch + CPU**: ~10x
3. **NumPy**: ~3x
4. **Pure Python**: 1x (baseline)

### Memory Usage
- **Torch**: GPU memory when available, efficient tensor operations
- **NumPy**: System RAM, optimized array operations
- **Python**: Minimal memory, basic list operations

### Accuracy Comparison
| Algorithm | Speed | Accuracy | Use Case |
|-----------|-------|----------|----------|
| Average | Fastest | Good | General purpose |
| Weighted | Fast | Better | Perceptual matching |
| Luminance | Slower | Best | Professional analysis |

## Advanced Features

### Smart Caching

The node implements intelligent caching:
- **Input-Dependent**: Cache keys include image properties
- **Method-Aware**: Different cache entries for different processing methods  
- **Parameter-Sensitive**: Invalidated when any setting changes

### Error Recovery

Graceful fallback chain:
1. Try torch processing with error catching
2. Fall back to numpy with exception handling
3. Ultimate fallback to pure Python
4. Return error information if all methods fail

## Integration Patterns

### Image Quality Analysis
```
LoadImage → XDEV_PickByBrightness → QualityAnalyzer → Report
```

### Batch Processing Workflow
```
ImageBatcher → XDEV_PickByBrightness → [Process Best] → Output
```

### Conditional Processing
```
XDEV_PickByBrightness → ConditionalNode → [Bright/Dark Processing]
```

## Troubleshooting

### Common Issues

1. **"Batch size too small" Error**
   - **Cause**: Single image or empty batch
   - **Solution**: Ensure at least 2 images in batch

2. **"Processing method: python_fallback" Warning**
   - **Cause**: PyTorch/NumPy unavailable
   - **Solution**: Install torch for better performance

3. **Low brightness scores**
   - **Cause**: Dark images or incorrect algorithm
   - **Solution**: Try different algorithm or check image brightness

### Performance Tips

1. **Use GPU**: Install CUDA-enabled PyTorch for best performance
2. **Batch Size**: Optimal range 2-20 images for speed vs. choice
3. **Algorithm Choice**: Use "average" for speed, "luminance" for accuracy
4. **Disable Validation**: For trusted inputs in production pipelines

## Tooltip Reference

Rich tooltip documentation covers:
- **Parameter Descriptions**: Detailed explanation of each input
- **Algorithm Details**: How each brightness calculation works
- **Performance Implications**: Speed vs. accuracy tradeoffs
- **Use Case Examples**: When to use each setting
- **Troubleshooting**: Common issues and solutions
