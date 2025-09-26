# ComfyUI XDev Nodes - AI Coding Agent Instructions

## Project Overview

This is a **ComfyUI custom nodes package** that serves as a starter kit for building ComfyUI extensions. ComfyUI uses a graph-based workflow system where nodes process data through INPUT/OUTPUT connections.

### Core Architecture

- **Node Registration**: All nodes must be registered in `xdev_nodes/__init__.py` via `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`
- **Package Structure**: Nodes go in `xdev_nodes/nodes/`, web assets in `xdev_nodes/web/`
- **ComfyUI Integration**: Uses `pyproject.toml` with `[tool.comfy]` section for registry metadata

### Node Implementation Patterns

ComfyUI supports two patterns for node development:

#### V1 Pattern (Traditional - Used in this project)
```python
class NodeName:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {"required": {"param": ("TYPE", {"default": value})}}
    
    RETURN_TYPES = ("TYPE",)
    FUNCTION = "method_name"
    CATEGORY = "XDev/Subcategory"
    
    def method_name(self, param):
        return (result,)  # Always return tuple
```

#### V3 Pattern (Modern ComfyExtension)
```python
from comfy_api.latest.io import ComfyExtension, ComfyNode, Schema, Input, Output

class ModernNode(ComfyNode):
    def define_schema(self) -> Schema:
        return Schema(
            node_id="MODERN_Node",
            display_name="Modern Node",
            category="Category",
            inputs=[Input("param", "TYPE", default=value)],
            outputs=[Output("result", "TYPE")]
        )
    
    async def execute(self, param):
        return (result,)

async def comfy_entrypoint() -> ComfyExtension:
    return ComfyExtension([ModernNode])
```

### Critical ComfyUI Datatypes

- **IMAGE**: `torch.Tensor [B,H,W,C]` in 0-1 range (RGB)
- **STRING**: Standard Python string
- **"*"**: ANY type for passthrough nodes
- **Dropdown**: `(["option1","option2"], {"default":"option1"})`

## Development Workflows

### Local Development Setup
```bash
# Use dev-link scripts for symlinked development
scripts/dev-link.ps1  # Windows
scripts/dev-link.sh   # Unix
# Creates symlink in ComfyUI/custom_nodes/
```

### Testing
- `pytest -q` runs all tests
- Tests are minimal: import validation (`test_imports.py`) + basic functionality (`test_basic_nodes.py`)
- No ComfyUI runtime required for tests

### Registry Publishing
- Bump version in `pyproject.toml`
- Update `[tool.comfy]` metadata (PublisherId, DisplayName, requires-comfyui)
- CI runs on push/PR to main/master

### Advanced pyproject.toml Configuration
Beyond basic metadata, ComfyUI extensions support:
```toml
[tool.comfy]
PublisherId = "your-publisher-id"
DisplayName = "Extension Display Name"
Icon = "https://raw.githubusercontent.com/.../icon.png"
Banner = "https://raw.githubusercontent.com/.../banner.png"
requires-comfyui = ">=1.0.0"
web = "web"  # Web directory for frontend assets
includes = ["models", "docs"]  # Additional directories to include

# Model dependencies (auto-downloaded by ComfyUI Manager)
[[tool.comfy.models]]
location = "checkpoints"
model_url = "https://huggingface.co/model/download"

# Frontend package compatibility
comfyui-frontend-package = ">=1.0.0"
```

## Project-Specific Patterns

### Robust Fallbacks
See `xdev_nodes/nodes/image.py` - implements torch → numpy → pure Python fallbacks:
```python
# Always handle missing torch gracefully
try:
    import torch
except Exception:
    torch = None
```

### Node ID Conventions
- All node IDs use `XDEV_` prefix (prevents conflicts)
- Display names include `(XDev)` suffix
- Categories use `XDev/Subcategory` pattern

### Web Extensions
- `xdev_nodes/web/js/xdev.js` adds right-click menu items
- Individual node docs in `xdev_nodes/web/docs/XDEV_NodeName.md`
- `WEB_DIRECTORY = "./web"` in `__init__.py` enables web assets

### Type Annotations
- Use `from __future__ import annotations` for forward references
- Type hint method parameters but ComfyUI ignores them at runtime
- `RETURN_TYPES` and `INPUT_TYPES` are the authoritative type definitions

## Key Integration Points

### ComfyUI Discovery
ComfyUI scans `custom_nodes/` folders and imports packages, looking for:
- `NODE_CLASS_MAPPINGS`: `{"INTERNAL_ID": PythonClass}`
- `NODE_DISPLAY_NAME_MAPPINGS`: `{"INTERNAL_ID": "UI Display Name"}`
- Optional `WEB_DIRECTORY` for frontend assets

### Workflow Files
- `.json` files in `workflows/` are ComfyUI workflow examples
- Reference nodes by their `INTERNAL_ID` from mappings
- Test workflows by loading in ComfyUI UI

### Error Handling
- ComfyUI expects nodes to return tuples matching `RETURN_TYPES`
- Exceptions crash the workflow - handle gracefully
- Use fallback implementations when dependencies missing

## Common Tasks

### Adding New Node
1. Create class in appropriate `xdev_nodes/nodes/*.py` file
2. Add to both mappings in `xdev_nodes/__init__.py`
3. Add workflow test in `workflows/`
4. Restart ComfyUI to see changes

### Web Extension
- Modify `xdev_nodes/web/js/xdev.js` for UI interactions
- Add node docs to `xdev_nodes/web/docs/`
- Use `nodeData?.name?.startsWith?.("XDEV_")` for node filtering

## Path Management & Integration

### Official Path Patterns
```python
# ComfyUI uses folder_paths for asset management
import folder_paths

# Get custom nodes directories
custom_paths = folder_paths.get_folder_paths("custom_nodes")

# Model directories (checkpoints, loras, controlnet, etc.)
model_paths = folder_paths.folder_names_and_paths

# Web directory registration (automatic via WEB_DIRECTORY or pyproject.toml)
WEB_DIRECTORY = "./web"  # V1 pattern
# or in pyproject.toml: web = "web"  # V3 pattern
```

### Internationalization Support
```python
# Add locales/ directory for translations
# ComfyUI auto-discovers and serves via /i18n endpoint
locales/
  en/
    common.json
  es/
    common.json
```

### Workflow Template Discovery
```python
# Place example workflows in standard directories
example_workflows/  # or examples/, workflow/, workflows/
  basic_usage.json
  advanced_example.json
# Auto-served via /workflow_templates endpoint
```

### Testing Strategy
- Keep tests lightweight - no ComfyUI runtime dependency
- Test import mechanics and basic node functionality
- Use example workflows for integration testing

## Advanced Node Features

### Hidden Inputs
ComfyUI provides special hidden inputs for advanced functionality:
```python
# Available hidden inputs
"hidden": {
    "unique_id": "UNIQUE_ID",      # Node instance ID
    "prompt": "PROMPT",            # Full workflow prompt
    "extra_pnginfo": "EXTRA_PNGINFO",  # Metadata for PNG output
    "auth_token": "AUTH_TOKEN_COMFY_ORG",  # API authentication
    "api_key": "API_KEY_COMFY_ORG"  # Alternative auth method
}
```

### Lazy Evaluation
Optimize performance with lazy input evaluation:
```python
def check_lazy_status(self, **kwargs):
    # Return list of input names that need evaluation
    return ["input_name"] if condition else []

# Mark inputs as lazy in INPUT_TYPES
"input_name": ("TYPE", {"lazy": True})
```

### Output Nodes
Force execution of nodes that produce final results:
```python
OUTPUT_NODE = True  # V1 pattern
# or in V3 Schema: is_output_node=True
```

### API Node Patterns
For nodes that call external APIs:
```python
# V3 pattern with polling operations
async def execute(self, input_data, auth_token=None):
    client = ApiClient(auth_token=auth_token)
    operation = await client.start_async_task(input_data)
    return await operation.wait_for_completion()

# Mark as API node in schema
is_api_node = True
```

## Workflow Testing & CI Details

### Workflow JSON Structure
- Workflows reference nodes by `INTERNAL_ID` (e.g., "XDEV_HelloString")
- Node connections use `links` array with `[link_id, from_node, from_socket, to_node, to_socket]`
- Test with minimal chains: `LoadImage → XDEV_PickByBrightness → PreviewImage`

### CI Pipeline Specifics
- **Linting**: Uses `ruff` (no config file - uses defaults)
- **Testing**: `pytest -q` for minimal output
- **Python Version**: 3.11 in CI, >=3.10 supported
- **Dependencies**: Only `pytest ruff` beyond package deps
- Triggers on push/PR to `main` or `master`

### Backward Compatibility Rules
- **Never change node IDs** after publishing (breaks existing workflows)
- **Input/Output changes** require new node versions or careful defaults
- **Category changes** acceptable but avoid frequent moves
- Use PR template checklist for compatibility review

### Quality Gates
- All imports must work without ComfyUI runtime
- Nodes must handle missing dependencies gracefully (see torch fallbacks)
- Example workflows should be minimal and focused
- Issue templates enforce structured bug reports with workflow reproduction

## Professional Node Development Patterns

### Comprehensive Input Validation
All XDev nodes implement detailed validation with informative error messages:
```python
def _validate_inputs(self, param1, param2) -> Dict[str, Any]:
    if not isinstance(param1, str):
        return {
            "valid": False,
            "error": f"Parameter must be string, got {type(param1).__name__}. Convert input to string format."
        }
    return {"valid": True, "error": None}
```

### Rich Tooltip Documentation
Every input parameter includes comprehensive tooltips:
```python
"text": ("STRING", {
    "default": "",
    "multiline": True,
    "tooltip": "The original text content to process. Supports multiline input for complex operations. Leave empty to process suffix only."
})
```

### Enhanced Output Patterns
Nodes return multiple outputs for better workflow integration:
```python
RETURN_TYPES = ("STRING", "INT", "STRING")
RETURN_NAMES = ("processed_text", "character_count", "processing_info")
```

### Smart Caching Implementation
Proper ComfyUI cache management with `IS_CHANGED`:
```python
@classmethod
def IS_CHANGED(cls, text, suffix, validate_input=True):
    return f"{text}_{suffix}_{validate_input}"
```

### Robust Error Handling
Graceful degradation instead of exceptions:
```python
try:
    result = self.process(input_data)
    return (result, len(result), "Success")
except Exception as e:
    error_msg = f"Error processing: {str(e)}"
    return (error_msg, len(error_msg), f"Error: {str(e)}")
```

### Professional Documentation System
Rich markdown documentation for web interface:
- Comprehensive feature descriptions with examples
- Parameter tables with detailed explanations
- Usage patterns and integration examples
- Troubleshooting guides and performance tips
- Algorithm explanations and comparison tables