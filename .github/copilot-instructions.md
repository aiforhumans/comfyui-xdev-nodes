# ComfyUI XDev Nodes - AI Coding Agent Instructions

## Project Overview

Complete ComfyUI development toolkit with **21 professional nodes** demonstrating best practices for ComfyUI extension development. ComfyUI uses a graph-based workflow system where nodes process data through INPUT/OUTPUT connections.

**Status**: v0.2.0 + Phase 3 complete (5 prompt tool nodes). Production-ready with advanced performance framework, validation mixins, and comprehensive debugging infrastructure.

### Core Architecture & Critical Knowledge

- **Node Registration**: All nodes registered in `xdev_nodes/__init__.py` with debug logging and custom API endpoints (`/xdev/status`, `/xdev/nodes`)
- **Functional Grouping**: Related nodes share files in `xdev_nodes/nodes/` (basic.py, text.py, math.py, image.py, dev_nodes.py, vae_tools.py) - NOT one-file-per-node
- **Performance Framework**: Advanced performance utilities in `xdev_nodes/performance.py` with decorators, profiling, and memory monitoring
- **Validation System**: Standardized mixins in `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes
- **Universal Testing Architecture**: Use `InputDev(TYPE) → YourNode → OutputDev` pattern for testing ANY node with ANY type
- **Development Workflow**: Use `scripts/dev-link.ps1` to symlink into ComfyUI, then `pytest tests/ -v` to validate all 21 nodes

## Essential XDev Patterns

### Performance Framework Integration
**Performance Decorators** (All Phase 2 nodes use these):
```python
from ..performance import performance_monitor, cached_operation
from ..mixins import ImageProcessingNode

class YourImageNode(ImageProcessingNode):
    @performance_monitor("resize_operation")
    @cached_operation(cache_size=100)
    def your_method(self, image, param):
        # Automatic profiling + caching
        return result
```

**Base Class Pattern** (Image nodes extend ImageProcessingNode):
```python
class ImageResize(ImageProcessingNode):
    # Inherits validation, performance monitoring, error handling
    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}
```

**Precomputed Constants** (TextCase, MathBasic examples):
```python
# TextCase: 9 case methods with O(1) lookup
_CASE_METHODS = {
    "lower": lambda text: text.lower(),
    "camel": lambda text: text[0].lower() + text.title().replace(" ", "")[1:] if text else "",
    # ... 7 more
}

# ImageBlend: 8 blend modes with torch/numpy/python fallbacks  
_BLEND_MODES = {"normal": ..., "multiply": ..., "screen": ..., "overlay": ...}
```

**Graceful Fallbacks** (All image nodes follow this pattern):
```python
# Always handle missing torch gracefully - numpy/pure Python fallbacks
try: import torch; HAS_TORCH = True
except: torch = None; HAS_TORCH = False
```

### Node Implementation Standard

**XDev Enhanced Pattern** (ImageResize/ImageCrop examples):
```python
from ..performance import performance_monitor, cached_operation
from ..mixins import ImageProcessingNode

class ImageResize(ImageProcessingNode):
    # Precompute algorithms/constants at class level
    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image tensor [B,H,W,C] in 0-1 range"}),
                "width": ("INT", {"default": 512, "min": 1, "max": 8192, "tooltip": "Target width"}),
                "height": ("INT", {"default": 512, "min": 1, "max": 8192, "tooltip": "Target height"}),
                "algorithm": (list(cls._RESIZE_ALGORITHMS.keys()), {"default": "lanczos", "tooltip": "Resize algorithm"})
            },
            "optional": {
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("resized_image", "resize_info") 
    FUNCTION = "resize_image"
    CATEGORY = "XDev/Image/Manipulation"
    DESCRIPTION = "Resize images with multiple algorithms and performance monitoring"
    
    @performance_monitor("image_resize")
    @cached_operation(cache_size=50)
    def resize_image(self, image, width, height, algorithm, validate_input=True):
        if validate_input:
            validation = self.validate_image_input(image, "image")
            if not validation["valid"]: 
                return (image, f"Error: {validation['error']}")
        
        # Implementation with algorithm lookup
        resize_func = self._RESIZE_ALGORITHMS[algorithm]
        result = resize_func(image, width, height)
        
        return (result, f"Resized to {width}x{height} using {algorithm}")
```

**Critical XDev Patterns**:
- Use `from ..performance import` for performance decorators
- Use `from ..mixins import` for base classes (ImageProcessingNode, ValidationMixin)
- All tooltips required - this is educational toolkit
- Graceful fallbacks: torch → numpy → pure Python (see image.py)
- Performance-first: precompute constants, cache validations, use @performance_monitor

### Critical ComfyUI Datatypes & XDev Testing

- **IMAGE**: `torch.Tensor [B,H,W,C]` in 0-1 range (RGB)
- **LATENT**: `dict["samples": Tensor [B,C,H,W]]` - compressed image representation  
- **VAE**: Model object for encode/decode operations
- **STRING**: Standard Python string
- **"*"**: ANY type for passthrough nodes (used in InputDev/OutputDev)
- **Dropdown**: `(["option1","option2"], {"default":"option1"})`

**XDev Universal Testing Pattern**: Use `InputDev(TYPE) → YourNode → OutputDev` for testing any node with any data type. InputDev generates 12 ComfyUI types, OutputDev analyzes everything.

## Development Workflows

### Local Development Setup
Use symlink for live development: `scripts/dev-link.ps1 $ComfyUI_Path`

### Testing Strategy  
- `pytest tests/ -v` - runs all tests (no ComfyUI runtime needed)
- Universal testing: `InputDev(TYPE) → YourNode → OutputDev`
- Tests validate imports + basic functionality for all 21 nodes
- Performance tests included for @performance_monitor decorated methods

### Adding New Nodes
1. Add to appropriate file in `xdev_nodes/nodes/` (functional grouping)
2. Extend appropriate base class (`ImageProcessingNode` for image ops, `ValidationMixin` for basic validation)
3. Use performance decorators: `@performance_monitor("operation_name")`, `@cached_operation(cache_size=N)`
4. Register in `NODE_CLASS_MAPPINGS` + `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`
5. Use `XDEV_` prefix, `(XDev)` suffix, `XDev/Category/Subcategory` pattern
6. Create test workflow in `workflows/`

## Current Architecture (21 Nodes)

**Phase 3 Complete**: PromptCombiner (4 modes + weighting), PromptWeighter (5 operations), PromptCleaner (comprehensive cleanup), PromptAnalyzer (detailed analysis), PromptRandomizer (5 randomization modes)
**Phase 2 Complete**: ImageResize (4 algorithms), ImageCrop (7 modes), ImageRotate (lossless + arbitrary angles), ImageBlend (8 blend modes), ImageSplit (grid/strip/smart), ImageTile (seamless tiling)
**Phase 1 Complete**: TextCase (9 case formats), MathBasic (7 operations)  
**Original Toolkit**: HelloString, AnyPassthrough, AppendSuffix, PickByBrightness, InputDev/OutputDev, VAERoundTrip/VAEPreview

### Advanced Architecture Components
- **Performance Framework**: `xdev_nodes/performance.py` - decorators, profiling, memory monitoring, caching
- **Validation System**: `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes
- **Optimized Utils**: `xdev_nodes/utils.py` - lazy imports, cached operations, efficient data analysis
- **Custom API Endpoints**: `/xdev/status` and `/xdev/nodes` for debugging and monitoring