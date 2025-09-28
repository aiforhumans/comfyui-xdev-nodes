# ComfyUI XDev Nodes - AI Coding Agent Instructions

## Project Overview

Complete ComfyUI development toolkit with **40 professional nodes** demonstrating best practices for ComfyUI extension development. ComfyUI uses a graph-based workflow system where nodes process data through INPUT/OUTPUT connections.

**Status**: v0.5.0 - Production-ready with 10 major phases complete including Professional Face Swapping (InsightFace + InSwapper), Advanced KSampler with learning optimization, SDXL Model Mixer, LLM integrations, and comprehensive prompt tools. Advanced performance framework, validation mixins, and professional debugging infrastructure.

### Core Architecture & Critical Knowledge

- **Node Registration**: All nodes registered in `xdev_nodes/__init__.py` with debug logging and custom API endpoints (`/xdev/status`, `/xdev/nodes`)
- **Functional Grouping**: Related nodes share files in `xdev_nodes/nodes/` (basic.py, text.py, math.py, image.py, dev_nodes.py, vae_tools.py, prompt.py, llm_integration.py, model_tools.py, sampling_advanced.py) - NOT one-file-per-node
- **Performance Framework**: Advanced performance utilities in `xdev_nodes/performance.py` with decorators, profiling, memory monitoring, and TTL caching
- **Validation System**: Standardized mixins in `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes
- **Universal Testing Architecture**: Use `InputDev(TYPE) → YourNode → OutputDev` pattern for testing ANY node with ANY type
- **Development Workflow**: Use `scripts/dev-link.ps1` to symlink into ComfyUI, then `pytest tests/ -v` to validate all 40 nodes
- **LLM Integration**: Local LLM server support with OpenAI-compatible APIs (LM Studio, Ollama) and graceful HTTP fallbacks
- **Model Operations**: Advanced SDXL model mixing with PyTorch state_dict manipulation and multi-algorithm blending
- **Advanced Sampling**: Multi-variant generation with learning optimization for iterative improvement

## Essential XDev Patterns

- **Node Registration**: All nodes registered in `xdev_nodes/__init__.py` with debug logging and custom API endpoints (`/xdev/status`, `/xdev/nodes`)

- **Functional Grouping**: Related nodes share files in `xdev_nodes/nodes/` (basic.py, text.py, math.py, image.py, dev_nodes.py, vae_tools.py, prompt.py, llm_integration.py, model_tools.py) - NOT one-file-per-node### Performance Framework Integration

- **Performance Framework**: Advanced performance utilities in `xdev_nodes/performance.py` with decorators, profiling, memory monitoring, and TTL caching**Performance Decorators** (All advanced nodes use these):

- **Validation System**: Standardized mixins in `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes```python

- **Universal Testing Architecture**: Use `InputDev(TYPE) → YourNode → OutputDev` pattern for testing ANY node with ANY typefrom ..performance import performance_monitor, cached_operation

- **Development Workflow**: Use `scripts/dev-link.ps1` to symlink into ComfyUI, then `pytest tests/ -v` to validate all 38 nodesfrom ..mixins import ImageProcessingNode

- **LLM Integration**: Local LLM server support with OpenAI-compatible APIs (LM Studio, Ollama) and graceful HTTP fallbacks

- **Model Operations**: Advanced SDXL model mixing with PyTorch state_dict manipulation and multi-algorithm blendingclass YourImageNode(ImageProcessingNode):

    @performance_monitor("resize_operation")

## Essential XDev Patterns    @cached_operation(ttl=300)  # TTL-based caching, not cache_size

    def your_method(self, image, param):

### Performance Framework Integration        # Automatic profiling + caching

**Performance Decorators** (All advanced nodes use these):        return result

```python```

from ..performance import performance_monitor, cached_operation

from ..mixins import ImageProcessingNode**Base Class Pattern** (Image nodes extend ImageProcessingNode):

```python

class YourImageNode(ImageProcessingNode):class ImageResize(ImageProcessingNode):

    @performance_monitor("resize_operation")    # Inherits validation, performance monitoring, error handling

    @cached_operation(ttl=300)  # TTL-based caching, not cache_size    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}

    def your_method(self, image, param):```

        # Automatic profiling + caching

        return result**Precomputed Constants** (TextCase, MathBasic, SDXLModelMixer examples):

``````python

# TextCase: 9 case methods with O(1) lookup

**Base Class Pattern** (Image nodes extend ImageProcessingNode):_CASE_METHODS = {

```python    "lower": lambda text: text.lower(),

class ImageResize(ImageProcessingNode):    "camel": lambda text: text[0].lower() + text.title().replace(" ", "")[1:] if text else "",

    # Inherits validation, performance monitoring, error handling    # ... 7 more

    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}}

```

# SDXLModelMixer: 5 algorithms + 4 weighting strategies

**Precomputed Constants** (TextCase, MathBasic, SDXLModelMixer examples):_MIXING_ALGORITHMS = {"linear": "Linear interpolation (LERP)", "spherical": "Spherical LERP", ...}

```python_WEIGHTING_STRATEGIES = {"uniform": "Equal weights", "adaptive": "Smart adaptation", ...}

# TextCase: 9 case methods with O(1) lookup```

_CASE_METHODS = {

    "lower": lambda text: text.lower(),**Graceful Fallbacks** (All nodes follow this pattern):

    "camel": lambda text: text[0].lower() + text.title().replace(" ", "")[1:] if text else "",```python

    # ... 7 more# Always handle missing dependencies gracefully

}try: import torch; HAS_TORCH = True

except: torch = None; HAS_TORCH = False

# SDXLModelMixer: 5 algorithms + 4 weighting strategies

_MIXING_ALGORITHMS = {"linear": "Linear interpolation (LERP)", "spherical": "Spherical LERP", ...}try: import httpx; HAS_HTTPX = True  # For LLM integration

_WEIGHTING_STRATEGIES = {"uniform": "Equal weights", "adaptive": "Smart adaptation", ...}except: httpx = None; HAS_HTTPX = False

``````



**Graceful Fallbacks** (All nodes follow this pattern):### Node Implementation Standard

```python

# Always handle missing dependencies gracefully**XDev Enhanced Pattern** (ImageResize/ImageCrop examples):

try: import torch; HAS_TORCH = True```python

except: torch = None; HAS_TORCH = Falsefrom ..performance import performance_monitor, cached_operation

from ..mixins import ImageProcessingNode

try: import httpx; HAS_HTTPX = True  # For LLM integration

except: httpx = None; HAS_HTTPX = Falseclass ImageResize(ImageProcessingNode):

```    # Precompute algorithms/constants at class level

    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}

### Node Implementation Standard    

    @classmethod

**XDev Enhanced Pattern** (ImageResize/ImageCrop examples):    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:

```python        return {

from ..performance import performance_monitor, cached_operation            "required": {

from ..mixins import ImageProcessingNode                "image": ("IMAGE", {"tooltip": "Input image tensor [B,H,W,C] in 0-1 range"}),

                "width": ("INT", {"default": 512, "min": 1, "max": 8192, "tooltip": "Target width"}),

class ImageResize(ImageProcessingNode):                "height": ("INT", {"default": 512, "min": 1, "max": 8192, "tooltip": "Target height"}),

    # Precompute algorithms/constants at class level                "algorithm": (list(cls._RESIZE_ALGORITHMS.keys()), {"default": "lanczos", "tooltip": "Resize algorithm"})

    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}            },

                "optional": {

    @classmethod                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})

    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:            }

        return {        }

            "required": {    

                "image": ("IMAGE", {"tooltip": "Input image tensor [B,H,W,C] in 0-1 range"}),    RETURN_TYPES = ("IMAGE", "STRING")

                "width": ("INT", {"default": 512, "min": 1, "max": 8192, "tooltip": "Target width"}),    RETURN_NAMES = ("resized_image", "resize_info") 

                "height": ("INT", {"default": 512, "min": 1, "max": 8192, "tooltip": "Target height"}),    FUNCTION = "resize_image"

                "algorithm": (list(cls._RESIZE_ALGORITHMS.keys()), {"default": "lanczos", "tooltip": "Resize algorithm"})    CATEGORY = "XDev/Image/Manipulation"

            },    DESCRIPTION = "Resize images with multiple algorithms and performance monitoring"

            "optional": {    

                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})    @performance_monitor("image_resize")

            }    @cached_operation(ttl=300)

        }    def resize_image(self, image, width, height, algorithm, validate_input=True):

            if validate_input:

    RETURN_TYPES = ("IMAGE", "STRING")            validation = self.validate_image_input(image, "image")

    RETURN_NAMES = ("resized_image", "resize_info")             if not validation["valid"]: 

    FUNCTION = "resize_image"                return (image, f"Error: {validation['error']}")

    CATEGORY = "XDev/Image/Manipulation"        

    DESCRIPTION = "Resize images with multiple algorithms and performance monitoring"        # Implementation with algorithm lookup

            resize_func = self._RESIZE_ALGORITHMS[algorithm]

    @performance_monitor("image_resize")        result = resize_func(image, width, height)

    @cached_operation(ttl=300)        

    def resize_image(self, image, width, height, algorithm, validate_input=True):        return (result, f"Resized to {width}x{height} using {algorithm}")

        if validate_input:```

            validation = self.validate_image_input(image, "image")

            if not validation["valid"]: **Critical XDev Patterns**:

                return (image, f"Error: {validation['error']}")- Use `from ..performance import` for performance decorators

        - Use `from ..mixins import` for base classes (ImageProcessingNode, ValidationMixin)

        # Implementation with algorithm lookup- All tooltips required - this is educational toolkit

        resize_func = self._RESIZE_ALGORITHMS[algorithm]- Graceful fallbacks: torch → numpy → pure Python (see image.py)

        result = resize_func(image, width, height)- Performance-first: precompute constants, cache validations, use @performance_monitor

        

        return (result, f"Resized to {width}x{height} using {algorithm}")### Critical ComfyUI Datatypes & XDev Testing

```

- **IMAGE**: `torch.Tensor [B,H,W,C]` in 0-1 range (RGB)

**Critical XDev Patterns**:- **LATENT**: `dict["samples": Tensor [B,C,H,W]]` - compressed image representation  

- Use `from ..performance import` for performance decorators- **VAE**: Model object for encode/decode operations

- Use `from ..mixins import` for base classes (ImageProcessingNode, ValidationMixin)- **STRING**: Standard Python string

- All tooltips required - this is educational toolkit- **"*"**: ANY type for passthrough nodes (used in InputDev/OutputDev)

- Graceful fallbacks: torch → numpy → pure Python (see image.py)- **Dropdown**: `(["option1","option2"], {"default":"option1"})`

- Performance-first: precompute constants, cache validations, use @performance_monitor

**XDev Universal Testing Pattern**: Use `InputDev(TYPE) → YourNode → OutputDev` for testing any node with any data type. InputDev generates 12 ComfyUI types, OutputDev analyzes everything.e performance decorators: `@performance_monitor("operation_name")`, `@cached_operation(ttl=N)` demonstrating best practices for ComfyUI extension development. ComfyUI uses a graph-based workflow system where nodes process data through INPUT/OUTPUT connections.

### Critical ComfyUI Datatypes & XDev Testing

**Status**: v0.4.0 - Production-ready with 7 major phases complete including SDXL Model Mixer, LLM integrations, and comprehensive prompt tools. Advanced performance framework, validation mixins, and professional debugging infrastructure.

- **IMAGE**: `torch.Tensor [B,H,W,C]` in 0-1 range (RGB)

- **LATENT**: `dict["samples": Tensor [B,C,H,W]]` - compressed image representation  ### Core Architecture & Critical Knowledge

- **VAE**: Model object for encode/decode operations

- **STRING**: Standard Python string- **Node Registration**: All nodes registered in `xdev_nodes/__init__.py` with debug logging and custom API endpoints (`/xdev/status`, `/xdev/nodes`)

- **"*"**: ANY type for passthrough nodes (used in InputDev/OutputDev)- **Functional Grouping**: Related nodes share files in `xdev_nodes/nodes/` (basic.py, text.py, math.py, image.py, dev_nodes.py, vae_tools.py, prompt.py, llm_integration.py, model_tools.py) - NOT one-file-per-node

- **Dropdown**: `(["option1","option2"], {"default":"option1"})`- **Performance Framework**: Advanced performance utilities in `xdev_nodes/performance.py` with decorators, profiling, memory monitoring, and TTL caching

- **Validation System**: Standardized mixins in `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes

**XDev Universal Testing Pattern**: Use `InputDev(TYPE) → YourNode → OutputDev` for testing any node with any data type. InputDev generates 12 ComfyUI types, OutputDev analyzes everything.- **Universal Testing Architecture**: Use `InputDev(TYPE) → YourNode → OutputDev` pattern for testing ANY node with ANY type

- **Development Workflow**: Use `scripts/dev-link.ps1` to symlink into ComfyUI, then `pytest tests/ -v` to validate all 38 nodes

## Development Workflows- **LLM Integration**: Local LLM server support with OpenAI-compatible APIs (LM Studio, Ollama) and graceful HTTP fallbacks

- **Model Operations**: Advanced SDXL model mixing with PyTorch state_dict manipulation and multi-algorithm blending

### Local Development Setup

Use symlink for live development: `scripts/dev-link.ps1 $ComfyUI_Path`## Essential XDev Patterns



### Testing Strategy  ### Performance Framework Integration

- `pytest tests/ -v` - runs all tests (no ComfyUI runtime needed)**Performance Decorators** (All advanced nodes use these):

- Universal testing: `InputDev(TYPE) → YourNode → OutputDev````python

- Tests validate imports + basic functionality for all 38 nodesfrom ..performance import performance_monitor, cached_operation

- Performance tests included for @performance_monitor decorated methodsfrom ..mixins import ImageProcessingNode



### Adding New Nodesclass YourImageNode(ImageProcessingNode):

1. Add to appropriate file in `xdev_nodes/nodes/` (functional grouping)    @performance_monitor("resize_operation")

2. Extend appropriate base class (`ImageProcessingNode` for image ops, `ValidationMixin` for basic validation)    @cached_operation(ttl=300)  # TTL-based caching, not cache_size

3. Use performance decorators: `@performance_monitor("operation_name")`, `@cached_operation(ttl=N)`    def your_method(self, image, param):

4. Register in `NODE_CLASS_MAPPINGS` + `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`        # Automatic profiling + caching

5. Use `XDEV_` prefix, `(XDev)` suffix, `XDev/Category/Subcategory` pattern        return result

6. Create test workflow in `workflows/````



## Current Architecture (38 Nodes)**Base Class Pattern** (Image nodes extend ImageProcessingNode):

```python

**Phase 7 Complete**: SDXLModelMixer (5 algorithms, 4 weighting strategies, 3-level validation, selective layer blending)class ImageResize(ImageProcessingNode):

**Phase 6 Complete**: LLM-Enhanced Prompt Tools (7 nodes) - LLMPromptAssistant, LLMContextualBuilder, LLMSDXLPhotoEnhancer, LLMSDXLExpertWriter, LLMDevFramework, LLMPersonBuilder, LLMStyleBuilder    # Inherits validation, performance monitoring, error handling

**Phase 5 Complete**: LLM Integration (1 node) - LMStudioChat with OpenAI-compatible API support    _RESIZE_ALGORITHMS = {"lanczos": ..., "nearest": ..., "bilinear": ..., "bicubic": ...}

**Phase 4 Complete**: Advanced Prompt Tools (3 nodes) - PromptAttention, PromptChainOfThought, PromptFewShot```

**Phase 3 Complete**: Core Prompt Tools (5 nodes) - PromptCombiner, PromptWeighter, PromptCleaner, PromptAnalyzer, PromptRandomizer

**Phase 2 Complete**: Enhanced Prompt Builders (5 nodes) - PersonBuilder, StyleBuilder, PromptMatrix, PromptInterpolator, PromptScheduler**Precomputed Constants** (TextCase, MathBasic, SDXLModelMixer examples):

**Phase 1 Complete**: Image Processing (6 nodes) - ImageResize, ImageCrop, ImageRotate, ImageBlend, ImageSplit, ImageTile```python

**Foundation**: Core Toolkit - HelloString, AnyPassthrough, AppendSuffix, PickByBrightness, InputDev/OutputDev, VAERoundTrip/VAEPreview, TextCase, MathBasic# TextCase: 9 case methods with O(1) lookup

_CASE_METHODS = {

### Advanced Architecture Components    "lower": lambda text: text.lower(),

- **Performance Framework**: `xdev_nodes/performance.py` - decorators, profiling, memory monitoring, TTL caching    "camel": lambda text: text[0].lower() + text.title().replace(" ", "")[1:] if text else "",

- **Validation System**: `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes    # ... 7 more

- **Optimized Utils**: `xdev_nodes/utils.py` - lazy imports, cached operations, efficient data analysis}

- **LLM Integration**: `xdev_nodes/nodes/llm_integration.py` - Local LLM server support (LM Studio, Ollama)

- **Model Tools**: `xdev_nodes/nodes/model_tools.py` - Advanced SDXL model mixing with PyTorch state_dict manipulation# SDXLModelMixer: 5 algorithms + 4 weighting strategies

- **Prompt Tools**: `xdev_nodes/nodes/prompt.py` - Comprehensive prompt engineering toolkit (17 nodes)_MIXING_ALGORITHMS = {"linear": "Linear interpolation (LERP)", "spherical": "Spherical LERP", ...}

- **Custom API Endpoints**: `/xdev/status` and `/xdev/nodes` for debugging and monitoring_WEIGHTING_STRATEGIES = {"uniform": "Equal weights", "adaptive": "Smart adaptation", ...}
```

**Graceful Fallbacks** (All nodes follow this pattern):
```python
# Always handle missing dependencies gracefully
try: import torch; HAS_TORCH = True
except: torch = None; HAS_TORCH = False

try: import httpx; HAS_HTTPX = True  # For LLM integration
except: httpx = None; HAS_HTTPX = False
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
    @cached_operation(ttl=300)
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
- Tests validate imports + basic functionality for all 38 nodes
- Performance tests included for @performance_monitor decorated methods

### Adding New Nodes
1. Add to appropriate file in `xdev_nodes/nodes/` (functional grouping)
2. Extend appropriate base class (`ImageProcessingNode` for image ops, `ValidationMixin` for basic validation)
3. Use performance decorators: `@performance_monitor("operation_name")`, `@cached_operation(cache_size=N)`
4. Register in `NODE_CLASS_MAPPINGS` + `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`
5. Use `XDEV_` prefix, `(XDev)` suffix, `XDev/Category/Subcategory` pattern
6. Create test workflow in `workflows/`

## Current Architecture (42 Nodes)

**Phase 10 Complete**: Professional Face Swapping (2 nodes) - FaceExtractEmbed and FaceSwapApply with InsightFace + InSwapper integration, CUDA optimization, graceful fallbacks
**Phase 9 Complete**: Advanced KSampler (2 nodes) - AdvancedKSampler with 3-variant generation and VariantSelector with learning optimization
**Phase 8 Complete**: SDXLModelMixer (5 algorithms, 4 weighting strategies, 3-level validation, selective layer blending)
**Phase 7 Complete**: LLM-Enhanced Prompt Tools (7 nodes) - LLMPromptAssistant, LLMContextualBuilder, LLMSDXLPhotoEnhancer, LLMSDXLExpertWriter, LLMDevFramework, LLMPersonBuilder, LLMStyleBuilder
**Phase 6 Complete**: LLM Integration (1 node) - LMStudioChat with OpenAI-compatible API support
**Phase 5 Complete**: Advanced Prompt Tools (3 nodes) - PromptAttention, PromptChainOfThought, PromptFewShot
**Phase 4 Complete**: Core Prompt Tools (5 nodes) - PromptCombiner, PromptWeighter, PromptCleaner, PromptAnalyzer, PromptRandomizer
**Phase 3 Complete**: Enhanced Prompt Builders (5 nodes) - PersonBuilder, StyleBuilder, PromptMatrix, PromptInterpolator, PromptScheduler
**Phase 2 Complete**: Image Processing (6 nodes) - ImageResize, ImageCrop, ImageRotate, ImageBlend, ImageSplit, ImageTile
**Phase 1 Complete**: Core Toolkit - HelloString, AnyPassthrough, AppendSuffix, PickByBrightness, InputDev/OutputDev, VAERoundTrip/VAEPreview, TextCase, MathBasic

### Advanced Architecture Components
- **Performance Framework**: `xdev_nodes/performance.py` - decorators, profiling, memory monitoring, TTL caching
- **Validation System**: `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes
- **Optimized Utils**: `xdev_nodes/utils.py` - lazy imports, cached operations, efficient data analysis
- **Face Swapping**: `xdev_nodes/nodes/faceswap_professional.py` - Professional InsightFace + InSwapper integration with CUDA optimization
- **LLM Integration**: `xdev_nodes/nodes/llm_integration.py` - Local LLM server support (LM Studio, Ollama)
- **Model Tools**: `xdev_nodes/nodes/model_tools.py` - Advanced SDXL model mixing with PyTorch state_dict manipulation
- **Sampling Advanced**: `xdev_nodes/nodes/sampling_advanced.py` - Multi-variant sampling with learning optimization
- **Prompt Tools**: `xdev_nodes/nodes/prompt.py` - Comprehensive prompt engineering toolkit (17 nodes)
- **Custom API Endpoints**: `/xdev/status` and `/xdev/nodes` for debugging and monitoring

## Advanced KSampler - Native ComfyUI Integration (DeepWiki Enhanced)

### XDEV_AdvancedKSampler - Professional Multi-Variant Generation

**Category**: `XDev/Sampling/Advanced`

**Core Architecture**: Native ComfyUI integration based on DeepWiki research
- Uses ComfyUI's common_ksampler function (same as KSampler node)
- CFGGuider integration with strategy-specific model_options hooks
- Dynamic sampler selection from KSAMPLER_NAMES
- Native scheduler optimization (karras, exponential, sgm_uniform, etc.)

**Strategy Implementation**:
- **Quality Variant**: Precision samplers (dpmpp_2m, heun, uni_pc) + enhanced CFG (1.05x boost)
- **Speed Variant**: Fast samplers (euler, lcm, dpm_fast) + optimized CFG (capped at 12.0)
- **Creative Variant**: Ancestral/SDE samplers + experimental CFG (dynamic scaling)

**Advanced Learning**: Optimizes native ComfyUI parameters
- Sampler/scheduler preference learning based on selection frequency
- CFG strategy adaptation per sampling approach
- Confidence-based parameter shifts with professional bounds
- Native ComfyUI parameter validation (steps: 1-200, CFG: 0.1-30.0)

**Enhanced Features**:
- CFG enhancement via model_options hooks (enhanced/optimized/experimental)
- Strategy-specific sampler selection from ComfyUI's KSAMPLER_NAMES
- Learning adapts native parameters (samplers, schedulers, CFG patterns)
- Comprehensive fallback system (native → direct API → enhanced mock)

**Usage Pattern** (DeepWiki Optimized):
```
1. Native Generation: Uses common_ksampler with strategy-enhanced models
2. CFG Analysis: Strategy-specific guidance via model_options hooks  
3. Parameter Learning: Adapts ComfyUI native samplers/schedulers based on selections
4. Professional Results: Production-quality sampling with educational architecture
```

### XDEV_VariantSelector - Learning Feedback

**Category**: `XDev/Sampling/Advanced`

**Core Function**: Processes user selection and ratings to provide feedback for learning system

**Rating System**: 1-10 scale for each variant (quality, speed, creative)
**Selection Notes**: Optional text feedback for context
**Output**: Formatted feedback string for learning integration

### Advanced Sampling Strategies

**Quality Strategy Implementation**:
- Steps: `int(base_steps * 1.5)` (capped at 200)
- CFG: `base_cfg + 0.5` (refined guidance)
- Priority: Maximum detail and precision
- Best For: Final renders, professional output

**Speed Strategy Implementation**:
- Steps: `max(5, int(base_steps * 0.6))` (minimum viable)
- CFG: `max(1.0, base_cfg - 1.0)` (efficiency focus)
- Scheduler: Prefers fast schedulers (euler, dpmpp_2m)
- Best For: Concept iteration, rapid prototyping

**Creative Strategy Implementation**:
- Steps: `base_steps ± random(0.2 * base_steps)`
- CFG: `base_cfg ± random(1.0)`
- Experimental: Random scheduler/sampler variations
- Best For: Artistic exploration, unexpected results

### Learning Algorithm Details

**Parameter Adjustment Logic**:
```python
# Learning strength controls adaptation rate (0.0-1.0)
# Higher values = faster learning, lower values = gradual adaptation

if selected_variant == "quality":
    base_steps += learning_strength * 2.0
    base_cfg += learning_strength * 0.3
elif selected_variant == "speed":
    base_steps -= learning_strength * 1.5
    base_cfg -= learning_strength * 0.2
elif selected_variant == "creative":
    # Maintains current parameters but increases experimentation range
    creative_variance += learning_strength * 0.1
```

**Boundary Management**:
- Steps: Always kept within 5-200 range
- CFG: Always kept within 1.0-30.0 range
- Denoise: Always kept within 0.1-1.0 range
- Learning accumulates gradually to prevent parameter drift

### Integration Patterns

**Complete Workflow Example**:
```
InputDev(MODEL/CONDITIONING/LATENT) → AdvancedKSampler → [3 OutputDev nodes for analysis]
                                                      ↓
                                     VariantSelector → [Results Analysis]
                                         ↓
                                [Feed selection back to next generation]
```

**Performance Optimization**:
- All operations use `@performance_monitor` decorators
- TTL-based caching for repeated parameter combinations
- Graceful fallbacks for missing dependencies
- Memory-efficient latent handling

## SDXL Model Mixer - Complete Mode Reference

### Mixing Algorithms (5 modes)
- **LINEAR**: Linear interpolation (LERP) - Standard weighted average blending (✅ Fully implemented)
- **SPHERICAL**: Spherical linear interpolation (SLERP) - Smooth geometric blending for better feature preservation (🔄 SLERP implementation in development)
- **ADDITIVE**: Additive blending - Combines model weights additively with normalization (✅ Fully implemented)
- **WEIGHTED_AVERAGE**: Intelligent weighted averaging with automatic scaling (✅ Fully implemented)
- **GEOMETRIC_MEAN**: Geometric mean blending - Preserves multiplicative relationships between weights (🚧 Implementation in development)

### Weighting Strategies (4 modes)
- **UNIFORM**: Equal weights for all models (automatic distribution)
- **MANUAL**: User-specified weights via weight_1, weight_2, weight_3, weight_4 parameters
- **PRIORITY**: Priority-based weighting favoring primary model with blend_ratio control
- **ADAPTIVE**: Intelligent adaptive weighting based on model compatibility and blend_ratio

### Layer Selection Options
- **ALL**: Blend entire model (default, most comprehensive)
- **ENCODER**: Blend only encoder layers (style/content processing)
- **DECODER**: Blend only decoder layers (image generation)
- **ATTENTION**: Blend only attention mechanisms (feature focus)
- **CUSTOM**: Comma-separated layer names for precise control

### Validation Levels (3 modes)
- **BASIC**: Essential compatibility checks (parameter counts, device placement)
- **DETAILED**: Extended validation (architecture analysis, memory estimation)
- **COMPREHENSIVE**: Full analysis (layer-by-layer compatibility, optimization suggestions)

### Advanced Architecture Components
- **Performance Framework**: `xdev_nodes/performance.py` - decorators, profiling, memory monitoring, TTL caching
- **Validation System**: `xdev_nodes/mixins.py` - ValidationMixin, ImageProcessingNode base classes
- **Optimized Utils**: `xdev_nodes/utils.py` - lazy imports, cached operations, efficient data analysis
- **LLM Integration**: `xdev_nodes/nodes/llm_integration.py` - Local LLM server support (LM Studio, Ollama)
- **Model Tools**: `xdev_nodes/nodes/model_tools.py` - Advanced SDXL model mixing with PyTorch state_dict manipulation
- **Prompt Tools**: `xdev_nodes/nodes/prompt.py` - Comprehensive prompt engineering toolkit (17 nodes)
- **Custom API Endpoints**: `/xdev/status` and `/xdev/nodes` for debugging and monitoring

## SDXL Model Mixer Usage Patterns

### Common Mixing Scenarios
```python
# Artistic Style Fusion: Photorealistic + Artistic
# Algorithm: SPHERICAL (preserves style characteristics)
# Strategy: PRIORITY (favor base model structure)
# Layers: ALL (comprehensive blending)

# Performance Enhancement: Base + Turbo
# Algorithm: LINEAR (simple speed optimization)
# Strategy: ADAPTIVE (intelligent speed/quality balance)
# Layers: DECODER (focus on generation speed)

# Multi-Style Blend: 3-4 different artistic models
# Algorithm: WEIGHTED_AVERAGE (balanced multi-model) - Use LINEAR as fallback until GEOMETRIC_MEAN ready
# Strategy: UNIFORM or MANUAL (equal or custom distribution)
# Layers: ENCODER (style characteristics only)

# Feature Enhancement: Base + Specialized (hands/faces)
# Algorithm: ADDITIVE (combine specialized features)
# Strategy: MANUAL (precise control over enhancement strength)
# Layers: ATTENTION (focus enhancement areas)
```

### Validation Strategy Selection
- **BASIC**: Production use, fast validation for known-compatible models
- **DETAILED**: Development/testing, balance of speed and analysis depth  
- **COMPREHENSIVE**: Research/experimentation, full compatibility analysis with optimization insights

### Performance Optimization Tips
- Use **LINEAR** for fastest mixing (simple interpolation) - Currently most reliable
- Use **WEIGHTED_AVERAGE** for balanced multi-model blending (fully stable)
- **SPHERICAL** and **GEOMETRIC_MEAN**: Advanced algorithms in development, may fall back to LINEAR
- **ENCODER-only** blending: Faster, affects style/content processing
- **DECODER-only** blending: Faster, affects final image generation
- **ALL** layers: Slowest but most comprehensive results