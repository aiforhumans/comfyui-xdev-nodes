# ComfyUI XDev Nodes - AI Coding Agent Instructions

## Project Overview

Complete ComfyUI development toolkit with **10 professional nodes** demonstrating best practices for ComfyUI extension development. ComfyUI uses a graph-based workflow system where nodes process data through INPUT/OUTPUT connections.

**Status**: v0.2.0 + Phase 1 foundation nodes (TextCase, MathBasic). Production-ready with performance optimizations and comprehensive debugging infrastructure.

### Core Architecture & Critical Knowledge

- **Node Registration**: All nodes registered in `xdev_nodes/__init__.py` with debug logging and API endpoints
- **Functional Grouping**: Related nodes share files in `xdev_nodes/nodes/` (basic.py, text.py, math.py, image.py, dev_nodes.py, vae_tools.py) - NOT one-file-per-node
- **Performance Layer**: Centralized utilities in `xdev_nodes/utils.py` with lazy imports, caching, and optimized operations
- **Universal Testing Architecture**: Use `InputDev(TYPE) → YourNode → OutputDev` pattern for testing ANY node with ANY type
- **Development Workflow**: Use `scripts/dev-link.ps1` to symlink into ComfyUI, then `pytest tests/ -q` to validate

## Essential XDev Patterns

### Performance & Error Patterns
**Precomputed Constants** (TextCase, MathBasic examples):
```python
# TextCase: 9 case methods with O(1) lookup
_CASE_METHODS = {
    "lower": lambda text: text.lower(),
    "camel": lambda text: text[0].lower() + text.title().replace(" ", "")[1:] if text else "",
    # ... 7 more
}

# MathBasic: operator mapping prevents runtime lookups
_OPERATIONS = {"add": operator.add, "multiply": operator.mul, ...}
```

**Graceful Fallbacks** (image.py pattern):
```python
# Always handle missing torch gracefully - numpy/pure Python fallbacks
try: import torch; HAS_TORCH = True
except: torch = None; HAS_TORCH = False
```

### Node Implementation Standard

**XDev Enhanced Pattern** (TextCase/MathBasic examples):
```python
class NodeName:
    # Precompute operations/constants at class level
    _CONSTANTS = {"key": "value"}
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {"param": ("TYPE", {"tooltip": "Descriptive tooltip"})},
            "optional": {
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable validation"})
            }
        }
    
    RETURN_TYPES = ("TYPE", "STRING")
    RETURN_NAMES = ("result", "metadata") 
    FUNCTION = "method_name"
    CATEGORY = "XDev/Subcategory"
    DESCRIPTION = "One-line description for API endpoints"
    
    def _validate_inputs(self, param) -> Dict[str, Any]:
        """Required validation pattern with detailed errors"""
        if not isinstance(param, expected_type):
            return {"valid": False, "error": f"Expected {expected_type}, got {type(param).__name__}"}
        return {"valid": True, "error": None}
    
    def method_name(self, param, validate_input=True):
        if validate_input:
            validation = self._validate_inputs(param)
            if not validation["valid"]: 
                return (f"Error: {validation['error']}", "validation_failed")
        # Always return tuple matching RETURN_TYPES
        return (result, metadata_string)
```

**Critical XDev Patterns**:
- Use `from ..utils import` for shared functionality (lazy imports, validation)
- All tooltips required - this is educational toolkit
- Graceful fallbacks: torch → numpy → pure Python (see image.py)
- Performance-first: precompute constants, cache validations

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
- `pytest tests/ -q` - runs all tests (no ComfyUI runtime needed)
- Universal testing: `InputDev(TYPE) → YourNode → OutputDev`
- Tests validate imports + basic functionality only

### Adding New Nodes
1. Add to appropriate file in `xdev_nodes/nodes/` (functional grouping)
2. Register in `NODE_CLASS_MAPPINGS` + `NODE_DISPLAY_NAME_MAPPINGS` in `__init__.py`
3. Use `XDEV_` prefix, `(XDev)` suffix, `XDev/Category` pattern
4. Create test workflow in `workflows/`

## Current Architecture (10 Nodes)

**Phase 1 Complete**: TextCase (9 case formats), MathBasic (7 operations)
**Original Toolkit**: HelloString, AnyPassthrough, AppendSuffix, PickByBrightness, InputDev/OutputDev, VAERoundTrip/VAEPreview