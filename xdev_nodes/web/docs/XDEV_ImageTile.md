# Image Tile (XDev) - Professional Pattern Tiling

## Overview  
The **Image Tile** node creates sophisticated tiled patterns from images using efficient PyTorch tensor operations. Features advanced tiling algorithms and seamless edge blending for professional texture creation.

## Features
- **8 Tiling Patterns**: Repeat, mirror, flip, rotate, and checkerboard modes
- **Seamless Edge Blending**: Reduces seam visibility with gradient blending
- **Efficient Broadcasting**: Uses PyTorch's optimized tensor operations
- **Texture Creation**: Perfect for creating seamless textures and patterns
- **Performance Optimized**: Cached operations and memory-efficient processing

## Inputs

### Required
- **image** (IMAGE): Input image tensor to tile [B,H,W,C]
- **tiles_x** (INT): Number of horizontal tile repetitions (1-16)
- **tiles_y** (INT): Number of vertical tile repetitions (1-16)  
- **mode** (STRING): Tiling pattern mode
  - `repeat`: Simple repetition using torch.tile
  - `mirror_x`: Mirror horizontally on alternating columns
  - `mirror_y`: Mirror vertically on alternating rows
  - `mirror_both`: Mirror both directions creating 4-way symmetry
  - `flip_x`: Flip horizontally on alternating tiles
  - `flip_y`: Flip vertically on alternating tiles
  - `rotate_90`: Rotate tiles by 90° increments in sequence
  - `checkerboard`: Alternating original and double-flipped tiles

### Optional
- **seamless** (BOOLEAN): Apply edge blending for seamless tiling (default: False)
- **blend_width** (INT): Width of blend region in pixels (1-64, default: 8)
- **validate_input** (BOOLEAN): Enable input validation (default: True)

## Outputs
- **tiled_image** (IMAGE): Resulting tiled pattern
- **output_width** (INT): Final image width
- **output_height** (INT): Final image height
- **tile_info** (STRING): Detailed tiling information and parameters

## Tiling Algorithms

### Repeat Mode
Simple efficient repetition using PyTorch's native operations:
```python
tiled = image.repeat(1, tiles_y, tiles_x, 1)
```

### Mirror Modes
Creates seamless patterns with reflective symmetry:
- **Mirror X**: `flip(2)` on alternating columns for horizontal mirror
- **Mirror Y**: `flip(1)` on alternating rows for vertical mirror  
- **Mirror Both**: Combines both for 4-way symmetrical patterns

### Rotation Mode
Sequential 90° rotations using efficient tensor operations:
- **Transpose + Flip**: `tensor.transpose(1, 2).flip(1)` for 90° clockwise
- **Progressive Rotation**: Each tile rotated by `(x + y) % 4 * 90°`
- **Seamless Transitions**: Creates flowing rotational patterns

### Checkerboard Mode
Alternating pattern with dual transformations:
- **Even Positions**: Original image
- **Odd Positions**: Double-flipped (`flip(1).flip(2)`)
- **Mathematical Pattern**: `(x + y) % 2` determines tile variant

## Seamless Blending System

### Edge Detection
Automatically identifies tile boundaries:
- **Horizontal Seams**: At `y * tile_height` positions
- **Vertical Seams**: At `x * tile_width` positions
- **Blend Region**: Configurable width around each seam

### Gradient Blending
Creates smooth transitions using linear interpolation:
```python
weights = torch.linspace(1.0, 0.0, blend_width)
blended = region1 * weights + region2 * (1 - weights)
```

### Multi-Seam Handling
- **Independent Processing**: Horizontal and vertical seams handled separately
- **Overlap Management**: Handles corner intersections gracefully
- **Memory Efficient**: In-place blending where possible

## Advanced Features

### Texture Creation Workflow
Perfect for creating seamless textures:
1. **Base Pattern**: Start with small texture sample
2. **Mirror Mode**: Use `mirror_both` for seamless edges
3. **Seamless Blending**: Enable with appropriate blend width
4. **Large Output**: Generate high-resolution seamless textures

### Performance Optimization
- **Efficient Concatenation**: Uses `torch.cat()` for optimal memory usage
- **Batch Processing**: Maintains batch dimensions throughout
- **Zero-Copy Operations**: Uses tensor views where possible
- **Conditional Blending**: Only applies seamless processing when needed

## Usage Examples

### Basic Texture Tiling
```
ImageTile:
  tiles_x: 4
  tiles_y: 4  
  mode: "repeat"
```

### Seamless Mirrored Pattern
```
ImageTile:
  tiles_x: 3
  tiles_y: 3
  mode: "mirror_both"
  seamless: true
  blend_width: 16
```

### Rotational Kaleidoscope
```
ImageTile:
  tiles_x: 6
  tiles_y: 6
  mode: "rotate_90" 
  # Creates flowing rotational pattern
```

### Checkerboard Texture
```
ImageTile:
  tiles_x: 8
  tiles_y: 8
  mode: "checkerboard"
  seamless: true
  blend_width: 4
```

### Large Seamless Texture
```
ImageTile:
  tiles_x: 16
  tiles_y: 16
  mode: "mirror_x"
  seamless: true
  blend_width: 32  # Wider blending for large patterns
```

## Mathematical Foundations

### Tensor Operations
Uses advanced PyTorch operations for efficiency:
- **Broadcasting**: Efficient repetition with minimal memory
- **Dimension Permutation**: Optimal tensor layout for processing
- **In-Place Operations**: Reduces memory allocation overhead

### Pattern Mathematics  
- **Modular Arithmetic**: `(x + y) % pattern` for regular patterns
- **Bit Operations**: Efficient checkerboard calculation
- **Symmetry Groups**: Mathematical foundation for mirror operations

## Performance Features
- **@performance_monitor**: Automatic timing and call tracking
- **@cached_operation**: Intelligent caching with parameter-based keys
- **Memory Efficient**: Minimal tensor copying and optimal layouts
- **Error Recovery**: Graceful fallback for blending failures

## Technical Notes
- **Device Awareness**: Maintains tensor device consistency
- **Gradient Computation**: Compatible with autograd for training workflows
- **Memory Management**: Automatic cleanup of temporary tensors
- **Edge Case Handling**: Robust handling of single-tile and edge cases

## Use Cases
- **Texture Synthesis**: Creating seamless textures from small samples
- **Pattern Generation**: Artistic and geometric pattern creation
- **Background Creation**: Large seamless backgrounds for design
- **Tile Testing**: Previewing how textures tile before final use
- **Kaleidoscope Effects**: Creating symmetrical artistic patterns

## Category
**XDev/Image** - Professional image manipulation tools