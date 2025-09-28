# Image Split (XDev) - Professional Image Grid Splitting

## Overview
The **Image Split** node provides professional image splitting into regular grids using efficient PyTorch tensor operations. Based on research from PyTorch and TorchVision's WindowPartition techniques for optimal performance.

## Features
- **Multiple Split Modes**: Grid (NxM), fixed tiles, horizontal/vertical strips
- **Efficient Tensor Operations**: Uses PyTorch's optimized tensor reshaping and view operations
- **Configurable Overlap**: Seamless processing with tile overlap support
- **Batch Processing**: Handles multiple images simultaneously
- **Flexible Output**: Individual tiles, batched, or reassembled grid formats

## Inputs

### Required
- **image** (IMAGE): Input image tensor in ComfyUI format [B,H,W,C]
- **mode** (STRING): Split mode
  - `grid`: Split into NxM regular grid based on rows/cols
  - `tiles`: Split into fixed-size tiles with optional overlap
  - `strips_horizontal`: Split into horizontal strips
  - `strips_vertical`: Split into vertical strips
- **rows** (INT): Number of rows for grid mode (1-32)
- **cols** (INT): Number of columns for grid mode (1-32)

### Optional  
- **tile_width** (INT): Fixed tile width for tiles mode (1-2048, default: 256)
- **tile_height** (INT): Fixed tile height for tiles mode (1-2048, default: 256)
- **overlap** (INT): Overlap between tiles in pixels (0-256, default: 0)
- **output_mode** (STRING): Output format
  - `separate`: Individual tiles as separate batch items
  - `batch`: All tiles stacked in batch dimension
  - `grid_image`: Reassemble into single grid visualization
- **validate_input** (BOOLEAN): Enable input validation (default: True)

## Outputs
- **tiles** (IMAGE): Split image tiles tensor
- **tile_count** (INT): Total number of tiles created
- **tiles_per_row** (INT): Number of tiles per row (for grid reconstruction)
- **split_info** (STRING): Detailed split information and parameters

## Split Algorithms

### Grid Mode
Uses efficient tensor reshaping based on PyTorch's optimized operations:
1. **Dimension Calculation**: `tile_h = height // rows`, `tile_w = width // cols`
2. **Tensor Reshape**: `[B,H,W,C] → [B,rows,tile_h,cols,tile_w,C]`
3. **Reorder Dimensions**: `[B,rows,cols,tile_h,tile_w,C]`
4. **Flatten to Tiles**: `[B*rows*cols,tile_h,tile_w,C]`

### Tiles Mode with Overlap
Implements sliding window with configurable overlap:
- **Step Calculation**: `step = max(1, tile_size - overlap)`
- **Sliding Window**: Iterates with efficient tensor slicing
- **Memory Efficient**: Uses tensor views where possible

### Strip Modes
- **Horizontal**: Splits image into horizontal bands
- **Vertical**: Splits image into vertical columns
- **Optimal Performance**: Direct tensor slicing without copying

## Advanced Features

### Overlap Processing
Perfect for seamless tile processing in computer vision:
```
ImageSplit:
  mode: "tiles"
  tile_width: 512
  tile_height: 512
  overlap: 64  # 64px overlap for seamless reconstruction
```

### Batch Processing
Efficiently handles multiple images:
- Maintains batch dimension consistency
- Memory-optimized tensor operations
- Parallel processing support

### Grid Reconstruction
The `grid_image` output mode reassembles tiles for visualization:
- Uses inverse tensor operations
- Maintains perfect reconstruction
- Useful for debugging and preview

## Usage Examples

### Basic 2x2 Grid
```
ImageSplit:
  mode: "grid"
  rows: 2
  cols: 2
  output_mode: "batch"
```

### Fixed Tile Size with Overlap
```  
ImageSplit:
  mode: "tiles"
  tile_width: 256
  tile_height: 256
  overlap: 32
  output_mode: "separate"
```

### Horizontal Strips
```
ImageSplit:
  mode: "strips_horizontal"  
  rows: 4  # 4 horizontal strips
  output_mode: "batch"
```

### Large Image Processing
```
ImageSplit:
  mode: "tiles"
  tile_width: 1024
  tile_height: 1024
  overlap: 128  # For AI upscaling workflows
  output_mode: "separate"
```

## Performance Features
- **@performance_monitor**: Automatic timing and statistics
- **@cached_operation**: Intelligent result caching
- **Zero-Copy Operations**: Uses tensor views where possible
- **Memory Efficient**: Minimizes temporary tensor allocation
- **Batch Optimized**: Vectorized operations across batches

## Technical Implementation
Based on research from PyTorch's WindowPartition system:
- **Efficient Reshaping**: Uses `view()` and `permute()` for zero-copy operations
- **Contiguous Memory**: Ensures optimal memory layout with `.contiguous()`
- **Dimension Management**: Maintains ComfyUI tensor format throughout
- **Error Recovery**: Graceful handling of non-divisible dimensions

## Use Cases
- **AI Model Processing**: Split large images for model inference
- **Tile-Based Processing**: Computer vision algorithms requiring tiles
- **Memory Management**: Process large images in smaller chunks
- **Parallel Processing**: Distribute tiles across multiple workers
- **Seamless Reconstruction**: Overlap support for artifact-free reassembly

## Category  
**XDev/Image** - Professional image manipulation tools