# Any Passthrough (XDev) - Rebuilt

**Universal data passthrough node with comprehensive analysis and debugging capabilities.**

## 🎯 Purpose
Pass any ComfyUI data type unchanged while providing detailed analysis and debugging information. Perfect for workflow debugging, data inspection, and understanding data flow.

## 📊 Inputs

### Required
- **`input`** (ANY): Any data type supported by ComfyUI
  - IMAGE tensors, text strings, numbers, latents, models, conditioning, etc.

### Optional  
- **`analysis_level`** (basic/detailed/debug): Level of data analysis
  - **basic**: Type and size information
  - **detailed**: Adds shape, device, memory usage  
  - **debug**: Includes object IDs, gradients, performance data

- **`show_content_preview`** (boolean): Include actual data preview
  - Shows first few values for tensors/arrays
  - Truncated text preview for strings

- **`track_performance`** (boolean): Monitor processing time and memory

## 📤 Outputs

### 1. **`output`** (ANY)
- The original input data, completely unchanged
- Connect to any node that accepts the input data type

### 2. **`data_report`** (STRING)  
- Comprehensive analysis of the input data
- Example: `"Type: Tensor | Shape: (1, 512, 512, 3) | Elements: 786,432 | DType: float32 | Device: cpu | Memory: 3.0MB"`

### 3. **`performance_info`** (STRING)
- Processing time and memory usage (if tracking enabled)
- Example: `"Processing time: 0.02ms | Memory: 245.3MB"`

## 🔗 Connection Examples

### Basic Data Inspection
```
LoadImage → Any Passthrough → PreviewImage
                         ↓
                   [data_report] → PreviewText
```

### Workflow Debugging
```
Model → Any Passthrough (debug mode) → KSampler
                    ↓
            [data_report] → Console Print
                    ↓  
        [performance_info] → SaveText
```

### Conditional Processing Based on Data Analysis  
```
Latent → Any Passthrough → [data_report] → String Contains → Conditional Node
                      ↓                                            ↓
                 [output] → ────────────────────────────────→ Process A/B
```

## 🛠️ Technical Features

### JSON Serialization Safety
- Fixed ComfyUI JSON serialization errors with tensors
- Safe caching mechanism that doesn't break ComfyUI's internal systems

### Comprehensive Analysis
- **Basic**: Data type, size/length, element count
- **Detailed**: Module info, dtype, device, memory usage
- **Debug**: Object IDs, gradient status, contiguity, performance metrics

### Error Handling
- Graceful fallback when analysis fails  
- Never breaks the data passthrough functionality
- Detailed error reporting for debugging

### Performance Optimized
- Minimal overhead on data passthrough
- Optional performance tracking
- Efficient caching system

## 💡 Pro Tips

1. **Use for debugging**: Set to "debug" mode to understand data flow issues
2. **Performance monitoring**: Enable tracking to identify bottlenecks
3. **Data validation**: Use detailed analysis to verify tensor shapes/types
4. **Workflow documentation**: Save data reports for workflow documentation

## 🚨 Fixes Applied (v2.0)

- ✅ Fixed JSON serialization errors with ComfyUI tensors
- ✅ Improved caching mechanism for better performance
- ✅ Enhanced error handling and fallback mechanisms  
- ✅ Added comprehensive data analysis capabilities
- ✅ Safe content preview without breaking workflows

This rebuilt version resolves all previous issues and provides enhanced debugging capabilities!
