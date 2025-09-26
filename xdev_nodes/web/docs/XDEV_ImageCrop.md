# Image Crop (XDev) - Smart Image Cropping

## Overview
The **Image Crop** node provides intelligent image cropping with multiple positioning modes and automatic padding. Features smart content-aware cropping and professional edge handling.

## Features
- **Smart Cropping**: Content-aware positioning based on brightness analysis
- **Multiple Crop Modes**: Center, smart, custom coordinates, corner positions
- **Automatic Padding**: Handles out-of-bounds crops with configurable padding color
- **Performance Optimized**: Cached operations and efficient batch processing
- **Flexible Positioning**: Supports negative coordinates for advanced layouts

## Inputs

### Required
- **image** (IMAGE): Input image tensor in ComfyUI format [B,H,W,C]
- **width** (INT): Crop width in pixels (1-8192)
- **height** (INT): Crop height in pixels (1-8192)
- **mode** (STRING): Crop positioning mode
  - `center`: Center the crop region
  - `smart`: AI-guided cropping based on content brightness
  - `custom`: Use x_offset/y_offset coordinates
  - `top_left`: Crop from top-left corner
  - `top_right`: Crop from top-right corner
  - `bottom_left`: Crop from bottom-left corner
  - `bottom_right`: Crop from bottom-right corner

### Optional
- **x_offset** (INT): X coordinate offset for custom mode (-8192 to 8192)
- **y_offset** (INT): Y coordinate offset for custom mode (-8192 to 8192)
- **pad_color** (FLOAT): Padding color for out-of-bounds areas (0.0=black, 1.0=white)
- **validate_input** (BOOLEAN): Enable input validation (default: True)

## Outputs
- **image** (IMAGE): Cropped image tensor
- **crop_x** (INT): Actual crop X coordinate used
- **crop_y** (INT): Actual crop Y coordinate used
- **crop_info** (STRING): Detailed crop information and padding status

## Smart Cropping Algorithm
The `smart` mode uses advanced content analysis:
1. **Brightness Analysis**: Calculates brightness map for entire image
2. **Sliding Window**: Tests multiple crop positions with adaptive step size
3. **Content Scoring**: Finds region with highest average brightness/detail
4. **Optimal Positioning**: Selects best crop position automatically

### Performance Optimization
- **Adaptive Step Size**: Larger images use larger steps for efficiency
- **Early Termination**: Stops when optimal region found
- **Memory Efficient**: Uses in-place operations where possible

## Padding System
When crop region extends beyond image boundaries:
- **Automatic Detection**: Identifies out-of-bounds areas
- **Configurable Color**: Set padding color (0.0-1.0 range)
- **Seamless Integration**: Pads only necessary regions
- **Status Reporting**: Info string indicates when padding applied

## Advanced Features

### Negative Coordinates
Custom mode supports negative offsets for advanced positioning:
- Negative X: Crops from left edge with left padding
- Negative Y: Crops from top edge with top padding
- Useful for creating borders or extending canvas

### Batch Processing
- Handles multiple images simultaneously
- Consistent crop regions across batch
- Efficient memory usage

## Usage Examples

### Center Crop
```
ImageCrop:
  width: 512
  height: 512
  mode: "center"
```

### Smart Content-Aware Crop  
```
ImageCrop:
  width: 768
  height: 768
  mode: "smart"
  # Automatically finds most interesting region
```

### Custom Positioned Crop
```
ImageCrop:
  width: 256
  height: 256
  mode: "custom"
  x_offset: 100
  y_offset: 50
```

### Crop with Padding
```
ImageCrop:
  width: 1024
  height: 1024
  mode: "custom"
  x_offset: -50  # Negative = padding on left
  y_offset: -25  # Negative = padding on top
  pad_color: 0.5  # Gray padding
```

### Corner Positioning
```
ImageCrop:
  width: 400
  height: 300
  mode: "bottom_right"
  # Crops from bottom-right corner
```

## Performance Features
- **@performance_monitor**: Automatic timing and call tracking
- **@cached_operation**: Intelligent result caching with TTL
- **Memory Efficient**: Direct tensor operations without copying
- **Error Recovery**: Graceful handling of invalid parameters

## Technical Notes
- Uses PyTorch tensor operations for maximum performance
- Supports images larger than crop dimensions (downsampling)
- Handles edge cases like zero-sized crops gracefully
- Maintains ComfyUI tensor format throughout processing

## Category
**XDev/Image** - Professional image manipulation tools