"""
Basic image operations and utilities
Part of the XDev Nodes modular architecture.
"""

from __future__ import annotations
from typing import Dict, Tuple, Any
from ...performance import performance_monitor, cached_operation, intern_string
from ...mixins import ImageProcessingNode
from ...categories import NodeCategories
from ...utils import get_torch


class ImageSplit(ImageProcessingNode):
    DISPLAY_NAME = "Image Split (XDev)"
    """
    Split images into multiple parts with various patterns.
    
    Features:
    - Grid splitting (2x2, 3x3, custom)
    - Horizontal and vertical splits
    - Custom split ratios
    - Batch processing support
    """
    
    _SPLIT_MODES = (
        intern_string("horizontal"),
        intern_string("vertical"),
        intern_string("grid_2x2"),
        intern_string("grid_3x3"),
        intern_string("custom_grid")
    )
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image tensor to split"
                }),
                "mode": (cls._SPLIT_MODES, {
                    "default": "horizontal",
                    "tooltip": "Split pattern: horizontal, vertical, or grid"
                })
            },
            "optional": {
                "grid_rows": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Number of rows for custom grid (custom_grid mode only)"
                }),
                "grid_cols": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Number of columns for custom grid (custom_grid mode only)"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("split_images", "count", "split_info")
    FUNCTION = "split_image"
    CATEGORY = NodeCategories.IMAGE_MANIPULATION
    DESCRIPTION = "Split images into multiple parts with various patterns"
    
    @performance_monitor("image_split")
    @cached_operation(ttl=300)
    def split_image(self, image, mode: str, grid_rows: int = 2, grid_cols: int = 2, validate_input: bool = True):
        """Split image according to specified mode"""
        
        if validate_input:
            validation = self.validate_image_input(image, "image")
            if not validation["valid"]:
                return (image, 0, f"Error: {validation['error']}")
        
        torch = get_torch()
        if torch is None:
            return (image, 0, "Error: PyTorch not available")
        
        try:
            batch_size, height, width, channels = image.shape
            
            if mode == "horizontal":
                # Split into top and bottom halves
                mid_height = height // 2
                top = image[:, :mid_height, :, :]
                bottom = image[:, mid_height:, :, :]
                result = torch.cat([top, bottom], dim=0)
                count = 2
                info = f"Split horizontally into 2 parts ({width}x{mid_height} each)"
                
            elif mode == "vertical":
                # Split into left and right halves
                mid_width = width // 2
                left = image[:, :, :mid_width, :]
                right = image[:, :, mid_width:, :]
                result = torch.cat([left, right], dim=0)
                count = 2
                info = f"Split vertically into 2 parts ({mid_width}x{height} each)"
                
            elif mode == "grid_2x2":
                # Split into 2x2 grid
                mid_height, mid_width = height // 2, width // 2
                top_left = image[:, :mid_height, :mid_width, :]
                top_right = image[:, :mid_height, mid_width:, :]
                bottom_left = image[:, mid_height:, :mid_width, :]
                bottom_right = image[:, mid_height:, mid_width:, :]
                result = torch.cat([top_left, top_right, bottom_left, bottom_right], dim=0)
                count = 4
                info = f"Split into 2x2 grid (4 parts of {mid_width}x{mid_height})"
                
            elif mode == "grid_3x3":
                # Split into 3x3 grid
                row_height, col_width = height // 3, width // 3
                parts = []
                for row in range(3):
                    for col in range(3):
                        start_h = row * row_height
                        end_h = start_h + row_height if row < 2 else height
                        start_w = col * col_width
                        end_w = start_w + col_width if col < 2 else width
                        parts.append(image[:, start_h:end_h, start_w:end_w, :])
                result = torch.cat(parts, dim=0)
                count = 9
                info = f"Split into 3x3 grid (9 parts of approximately {col_width}x{row_height})"
                
            elif mode == "custom_grid":
                # Split into custom grid
                row_height = height // max(1, grid_rows)
                col_width = width // max(1, grid_cols)
                parts = []
                for row in range(grid_rows):
                    for col in range(grid_cols):
                        start_h = row * row_height
                        end_h = start_h + row_height if row < grid_rows - 1 else height
                        start_w = col * col_width
                        end_w = start_w + col_width if col < grid_cols - 1 else width
                        parts.append(image[:, start_h:end_h, start_w:end_w, :])
                result = torch.cat(parts, dim=0)
                count = grid_rows * grid_cols
                info = f"Split into {grid_rows}x{grid_cols} grid ({count} parts of approximately {col_width}x{row_height})"
                
            else:
                result = image
                count = 1
                info = "No split applied"
            
            return (result, count, info)
            
        except Exception as e:
            error_msg = f"Split failed: {str(e)}"
            return (image, 0, error_msg)


class ImageTile(ImageProcessingNode):
    DISPLAY_NAME = "Image Tile (XDev)"
    """
    Create tiled patterns from input images.
    
    Features:
    - Multiple tiling patterns (repeat, mirror, mirror_repeat)
    - Custom tile counts for horizontal and vertical
    - Seamless edge handling
    - Performance optimized
    """
    
    _TILE_MODES = (
        intern_string("repeat"),
        intern_string("mirror"),
        intern_string("mirror_repeat")
    )
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image to tile"
                }),
                "tiles_x": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Number of horizontal tiles"
                }),
                "tiles_y": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Number of vertical tiles"
                }),
                "mode": (cls._TILE_MODES, {
                    "default": "repeat",
                    "tooltip": "Tiling mode: repeat, mirror, or mirror_repeat"
                })
            },
            "optional": {
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("tiled_image", "final_width", "final_height", "tile_info")
    FUNCTION = "tile_image"
    CATEGORY = NodeCategories.IMAGE_MANIPULATION
    DESCRIPTION = "Create tiled patterns from input images with various modes"
    
    @performance_monitor("image_tile")
    @cached_operation(ttl=300)
    def tile_image(self, image, tiles_x: int, tiles_y: int, mode: str, validate_input: bool = True):
        """Create tiled pattern from input image"""
        
        if validate_input:
            validation = self.validate_image_input(image, "image")
            if not validation["valid"]:
                return (image, 0, 0, f"Error: {validation['error']}")
        
        torch = get_torch()
        if torch is None:
            return (image, 0, 0, "Error: PyTorch not available")
        
        try:
            batch_size, height, width, channels = image.shape
            
            # Create horizontal tiles
            if mode == "repeat":
                horizontal_tiles = [image for _ in range(tiles_x)]
            elif mode == "mirror":
                horizontal_tiles = []
                for i in range(tiles_x):
                    if i % 2 == 0:
                        horizontal_tiles.append(image)
                    else:
                        horizontal_tiles.append(image.flip(2))  # Flip horizontally
            elif mode == "mirror_repeat":
                base_pattern = [image, image.flip(2)]  # Original + horizontal mirror
                horizontal_tiles = []
                for i in range(tiles_x):
                    horizontal_tiles.append(base_pattern[i % 2])
            else:
                horizontal_tiles = [image for _ in range(tiles_x)]
            
            # Concatenate horizontally
            horizontal_result = torch.cat(horizontal_tiles, dim=2)
            
            # Create vertical tiles
            if mode == "repeat":
                vertical_tiles = [horizontal_result for _ in range(tiles_y)]
            elif mode == "mirror":
                vertical_tiles = []
                for i in range(tiles_y):
                    if i % 2 == 0:
                        vertical_tiles.append(horizontal_result)
                    else:
                        vertical_tiles.append(horizontal_result.flip(1))  # Flip vertically
            elif mode == "mirror_repeat":
                base_pattern = [horizontal_result, horizontal_result.flip(1)]  # Original + vertical mirror
                vertical_tiles = []
                for i in range(tiles_y):
                    vertical_tiles.append(base_pattern[i % 2])
            else:
                vertical_tiles = [horizontal_result for _ in range(tiles_y)]
            
            # Concatenate vertically
            result = torch.cat(vertical_tiles, dim=1)
            
            final_height, final_width = result.shape[1], result.shape[2]
            info = f"Tiled {tiles_x}x{tiles_y} using {mode} mode ({final_width}x{final_height})"
            
            return (result, final_width, final_height, info)
            
        except Exception as e:
            error_msg = f"Tiling failed: {str(e)}"
            return (image, width, height, error_msg)
