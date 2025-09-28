# Image Resize (XDev) - Professional Image Resizing

## Overview
The **Image Resize** node provides professional-quality image resizing with multiple algorithms and aspect ratio control. Built with performance optimization and ComfyUI best practices.

## Features
- **Multiple Resize Algorithms**: lanczos, bilinear, bicubic, nearest neighbor
- **Aspect Ratio Preservation**: Automatic scaling to fit within target dimensions
- **Performance Optimized**: @performance_monitor and @cached_operation decorators
- **Batch Processing**: Handles multiple images efficiently
- **Quality Control**: Uses appropriate algorithm based on scaling direction

## Inputs

### Required
- **image** (IMAGE): Input image tensor in ComfyUI format [B,H,W,C] with values 0-1
- **width** (INT): Target width in pixels (1-8192). Use 0 for auto-calculation from height
- **height** (INT): Target height in pixels (1-8192). Use 0 for auto-calculation from width  
- **method** (STRING): Resize algorithm
  - `lanczos`: Best quality, uses area/bilinear approximation
  - `bilinear`: Balanced quality and speed
  - `bicubic`: Smooth results, good for upscaling
  - `nearest`: Pixelated/blocky, fastest for pixel art

### Optional
- **keep_aspect_ratio** (BOOLEAN): Preserve original aspect ratio (default: True)
- **validate_input** (BOOLEAN): Enable input validation (default: True)

## Outputs
- **image** (IMAGE): Resized image tensor
- **width** (INT): Actual output width
- **height** (INT): Actual output height  
- **resize_info** (STRING): Detailed resize information

## Algorithm Details

### Aspect Ratio Preservation
When `keep_aspect_ratio` is True and both width/height are specified:
- Calculates which dimension needs more scaling
- Fits image within the target box while preserving proportions
- Results in image that fits completely within width×height bounds

### Quality Optimization
- **Downscaling**: Uses area interpolation for lanczos to reduce aliasing
- **Upscaling**: Uses bilinear/bicubic for smooth results
- **Automatic Clamping**: Ensures output values remain in [0,1] range

## Performance Features
- **Intelligent Caching**: Results cached based on input parameters and image properties
- **Memory Efficient**: In-place operations where possible
- **Batch Optimized**: Processes multiple images simultaneously
- **Performance Monitoring**: Automatic timing and statistics

## Usage Examples

### Basic Resize
```
ImageResize:
  width: 1024
  height: 768
  method: "lanczos"
  keep_aspect_ratio: True
```

### Custom Aspect Ratio
```  
ImageResize:
  width: 512
  height: 512
  method: "bicubic"
  keep_aspect_ratio: False  # Forces exact dimensions
```

### Performance Mode
```
ImageResize:
  width: 256
  height: 256
  method: "bilinear" 
  validate_input: False  # Maximum performance
```

## Technical Notes
- Uses PyTorch's interpolation functions for high performance
- Converts between ComfyUI [B,H,W,C] and PyTorch [B,C,H,W] formats automatically
- Handles edge cases like zero dimensions gracefully
- Provides detailed error messages for troubleshooting

## Category
**XDev/Image** - Professional image manipulation tools