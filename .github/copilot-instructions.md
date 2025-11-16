# ComfyUI Custom Nodes Development Guide

## Architecture Overview

This is a **ComfyUI custom nodes package** organized under the `🖥XDEV` namespace with two main categories:
- **Prompt tools**: Text manipulation and prompt generation utilities (5 nodes)
- **LM Studio**: Local LLM integration via LM Studio's OpenAI-compatible API (6 nodes)

### Critical Package Structure
ComfyUI requires **dual `__init__.py` pattern**:
1. Root `__init__.py` imports from `comfyui_custom_nodes/__init__.py`
2. `comfyui_custom_nodes/__init__.py` dynamically discovers and registers nodes from subdirectories
3. Each category folder (e.g., `🖥XDEV/Prompt tools/`) has its own `__init__.py` exporting `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`

**Why**: ComfyUI loads the root folder as a Python package, expecting `NODE_CLASS_MAPPINGS` dict at the top level.

## Copilot & Agent Guidance

### Coding Style for AI Pairing
- Prefer small, composable helpers in each node so Copilot can reason about IO contracts.
- Keep docstrings explicit about tensor shapes, expected tuple order, and side effects (CLI calls, network requests).
- Reuse utilities from `lm_base_node.py` and `lm_utils.py`; do not duplicate retry logic or parsing helpers.
- When adding inputs/outputs, update both `INPUT_TYPES` and `RETURN_TYPES` in the same hunk so Copilot keeps them in sync.
- Stick to ASCII and explicit imports; avoid wildcard imports so completion engines see symbol origins.

### Agent Playbook
1. **Assess**: Read this file plus `README.md` to understand dual `__init__.py` structure and node categories before changing code.
2. **Plan**: Draft a short todo list when touching multiple files (new node + tests + docs) so Copilot agents can track progress.
3. **Modify**: Edit nodes via helpers (`_build_messages`, `_make_api_request`, `check_model_loaded`). Keep new logic behind clearly named functions for reuse.
4. **Validate**: Run targeted tests in `tests/` (e.g., `pytest tests/test_prompt_tools.py`) and, when LM Studio is unavailable, mock responses per existing fixtures.
5. **Document**: Update this guide and `docs/` summaries whenever behavior or public inputs change, so future agents inherit accurate context.

### Prompting Patterns
- *“Add a new SDXL utility node that mirrors lm_prompt_enhancer structure, with INPUT_TYPES matching { ... } and tests in tests/test_prompt_tools.py.”*
- *“Refactor lm_auto_unload_trigger to share CLI invocation helper from lm_utils.run_lms_cli.”*
- *“When response_format='json', ensure JSONParser handles fallback text by adding regression tests.”*
- Remind Copilot to keep return tuples aligned with `RETURN_TYPES`, and to respect GPU safety checks before invoking LM Studio models.

## Repo-Specific Task Templates

### Add a New Prompt Tool Node
1. Copy `comfyui_custom_nodes/🖥XDEV/Prompt tools/text_concatenate.py` as a starting point.
2. Update `INPUT_TYPES`, `RETURN_TYPES`, and `CATEGORY` together; keep docstring explicit about IO semantics.
3. Register the node in `comfyui_custom_nodes/🖥XDEV/Prompt tools/__init__.py` and ensure the top-level `comfyui_custom_nodes/__init__.py` picks it up.
4. Add or extend tests in `tests/test_prompt_tools.py` (import via dynamic path setup) and run `pytest tests/test_prompt_tools.py`.
5. Document any new parameters in `README.md` and `docs/docs/comfyui_prompt_mastering_guide.md` if they affect workflows.

### Enhance or Fix an LM Studio Node
1. Identify shared helpers in `lm_base_node.py` / `lm_utils.py`; extend them instead of duplicating logic.
2. For network changes, update `_make_api_request` usage and ensure `JSONParser` handles new fields (add regression tests under `tests/test_lm_studio.py`).
3. Respect GPU safety: call `check_model_loaded()` when models are involved and surface warnings through `info` output.
4. When touching CLI interactions, reuse `run_lms_cli` helper and adjust `tests/test_auto_unload.py` to mock subprocess behavior.
5. Update docs (`GPU_MEMORY_IMPLEMENTATION.md`, `SDXL_OPTIMIZATION.md`) if behavior visible to users changes.

### Documentation or Release Prep
1. Sync high-level changes into `README.md`, `docs/README.md`, and any affected deep-dive doc in `docs/docs/`.
2. Run `python -m pytest` (or targeted suites) and capture results in the PR description.
3. Bump metadata (version in `pyproject.toml`, changelog entry if applicable) before tagging a release.
4. Use `xcopy` command from Deployment section to mirror into a local ComfyUI install for smoke testing.
5. Open a draft PR summarizing key changes plus testing evidence; mention GPU memory implications explicitly.

## ComfyUI Node Conventions

### Mandatory Node Structure
```python
class YourNode:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {"param": ("TYPE", {"default": value})},
            "optional": {"opt": ("TYPE", {})}
        }
    
    RETURN_TYPES = ("STRING",)  # Tuple of type names
    RETURN_NAMES = ("output",)  # Optional, tuple matching RETURN_TYPES
    FUNCTION = "process"         # Method name to call
    CATEGORY = "🖥XDEV/Subcategory"
    
    def process(self, param: str, opt: str = "") -> Tuple[str]:
        return (result,)  # MUST return tuple, not list!
```

### ComfyUI Type System
- **Native types**: `STRING`, `INT`, `FLOAT`, `BOOLEAN`, `IMAGE`
- **Type configs**: `{"multiline": True}`, `{"min": 0, "max": 100, "step": 0.1}`, `{"forceInput": True}` (hides widget, requires connection)
- **Enums**: `(["option1", "option2"], {"default": "option1"})`
- **IMAGE type**: Tensor in format `[batch, height, width, channels]` with float values 0-1

### Return Value Rules
❌ **WRONG**: `return [result]` or `return result`  
✅ **CORRECT**: `return (result,)` or `return (output1, output2)`

ComfyUI expects tuples matching `RETURN_TYPES` length. Single returns need trailing comma.

## Node Registration Pattern

Each category's `__init__.py` must export:
```python
NODE_CLASS_MAPPINGS = {
    "XDEVNodeID": NodeClass,  # Unique ID for ComfyUI
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVNodeID": "Display Name",  # User-visible name
}
```

Main `comfyui_custom_nodes/__init__.py` aggregates these via dynamic imports with path manipulation:
```python
category_path = current_dir / "🖥XDEV" / "Category Name"
sys.path.insert(0, str(category_path))  # Critical for relative imports
from module import NodeClass
NODE_CLASS_MAPPINGS.update({"ID": NodeClass})
```

## Development Workflow

### Local Testing (Before ComfyUI Deployment)
```powershell
# Activate venv
.venv\Scripts\activate

# Run tests with proper Python path
cd tests
python test_prompt_tools.py  # Smoke tests
python test_lm_studio.py      # LM Studio tests
python test_auto_unload.py    # GPU memory tests
pytest                        # Full test suite
```

Tests share a `tests/conftest.py` helper that wires up ASCII-safe imports (see `comfyui_custom_nodes.xdev`). Prefer importing nodes via `from comfyui_custom_nodes.xdev import ...` inside tests.

### Deploy to ComfyUI
```powershell
xcopy c:\NOOODE "C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\NOOODE" /E /I /Y /Q
```

**Must restart ComfyUI** after any Python file changes. No hot reload.

## LM Studio Integration Specifics

### GPU Memory Management
**Critical**: LM Studio models and ComfyUI both use GPU memory. When running workflows with both:
1. LM Studio nodes automatically detect loaded models and print warnings
2. Users should manually unload models in LM Studio UI before image generation
3. Use `LMStudioModelUnloadHelper` node to check status and provide guidance
4. Use `LMStudioAutoUnloadTrigger` node to automatically handle unload workflow
5. All generation nodes use `check_model_loaded()` to warn about memory conflicts

**Auto Unload Trigger**: Node placed between prompt generation and image generation. When triggered:
- `warning_only`: Prints prominent warning to console (non-blocking)
- `lms_cli`: Uses LM Studio CLI (`lms unload --all`) to programmatically unload model (default)
- `force_error`: Returns error status to stop workflow until manually unloaded
- Has passthrough input/output to chain in workflows without disrupting data flow
- Requires lms CLI setup: `cmd /c %USERPROFILE%/.lmstudio/bin/lms.exe bootstrap` in PowerShell

### API Communication Pattern
All LM Studio nodes use `urllib.request` (not `requests`) to avoid dependencies:
```python
payload = {"messages": [...], "temperature": 0.7, "stream": False}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                             headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=60) as response:
    result = json.loads(response.read().decode('utf-8'))
```

### Vision Model Image Handling
ComfyUI image tensors → base64 PNG for LM Studio API:
```python
img_array = (np.array(image_tensor)[0] * 255).astype(np.uint8)  # First batch, scale to 0-255
img = Image.fromarray(img_array)
buffer = BytesIO()
img.save(buffer, format="PNG")
base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
image_url = f"data:image/png;base64,{base64_str}"
```

### SDXL Prompt Format
Prompt Enhancer generates optimized prompts for SDXL models:
- **Natural Language Support**: SDXL understands full sentences better than SD 1.5 - can use detailed descriptions OR comma-separated keywords
- **Keyword Weight Sensitivity**: Use (keyword:1.1) to (keyword:1.4) maximum - SDXL is very sensitive to emphasis, don't go higher
- **Structure Options**: 
  - Natural language: "A professional photograph of X with Y, Z lighting, highly detailed"
  - Keyword style: "subject, descriptors, composition, lighting, mood, style, quality tags"
- **Artist References**: Include specific artists (Greg Rutkowski, Artgerm, Tom Bagshaw, Alphonse Mucha, Elke Vogelsang, etc.)
- **Minimal Negative Prompts**: SDXL needs far less negative prompting than SD 1.5 - only include specific things to avoid
- **Quality Tags**: Use specific quality descriptors (award winning photography, highly detailed, 8k resolution, sharp focus, professional)
- **Composition Details**: Specify framing (portrait, close-up, wide shot), perspective, camera settings
- Example natural language: `"A professional photograph of a rhino dressed in a tailored suit and tie, sitting at a polished wooden bar table with elegant bar stools in the background, award winning photography in the style of Elke Vogelsang, dramatic lighting, shallow depth of field, highly detailed"`
- Example keyword style: `"beautiful woman, hand-dyed cotton clothes, beaded feather fringe, colorful pigtails, subtropical flowers, symmetrical face, intricate, elegant, highly detailed, 8k, digital painting, trending on pinterest, concept art, sharp focus, art by Tom Bagshaw and Alphonse Mucha"`

### JSON Response Format
All LM Studio nodes support structured JSON output:
- **Text Generator**: Set `response_format="json"` for JSON objects
- **Prompt Enhancer**: JSON mode returns `{"positive_prompt": "...", "negative_prompt": "..."}`
- **Vision Model**: JSON format for structured image descriptions
- **Automatic Handling**: System prompt auto-updated with JSON instructions
- **API Parameter**: Uses OpenAI-compatible `response_format` parameter
- **Parsing**: Regex extraction with fallback to text parsing for robustness

### Import Pattern for Test Compatibility
Use conditional imports to work in both ComfyUI and test environments:
```python
try:
    from .lm_model_manager import check_model_loaded
except ImportError:
    from lm_model_manager import check_model_loaded
```

## Common Pitfalls

1. **Forgetting `__init__.py` at root**: ComfyUI won't discover nodes
2. **Not updating main `__init__.py`**: New nodes in subdirectories won't register without updating `comfyui_custom_nodes/__init__.py`
3. **Using `forceInput: True` without model selector**: Model param becomes required input connection
4. **Not handling ComfyUI's IMAGE tensor format**: Must check for batch dimension and scale 0-1 float to 0-255 uint8
5. **Windows path issues with emoji folder names**: Import via `comfyui_custom_nodes.xdev` to avoid raw emoji paths.
6. **subprocess in nodes**: Use `subprocess.run()` for CLI calls (e.g., lms CLI), set timeout to prevent hangs

## Testing Strategy

- **Smoke tests** (`test_*.py`): Import nodes, call methods, assert return types
- **LM Studio tests**: Structural only (no live API calls unless server detected)
- **GPU memory tests**: Test model detection and CLI unload functionality
- Run tests before deployment to catch import errors early
- Use `sys.path.insert(0, str(path))` in tests to simulate ComfyUI import structure

## Key Files for New Node Development

- `comfyui_custom_nodes/🖥XDEV/Prompt tools/text_concatenate.py` - Simplest prompt tool example
- `comfyui_custom_nodes/🖥XDEV/LM Studio/lm_vision.py` - Complex example with image handling and API calls
- `comfyui_custom_nodes/🖥XDEV/LM Studio/lm_model_manager.py` - GPU memory management utilities
- `comfyui_custom_nodes/🖥XDEV/LM Studio/lm_model_unload_helper.py` - User-facing model status checker
- `comfyui_custom_nodes/🖥XDEV/LM Studio/lm_auto_unload_trigger.py` - Automated model unloading with CLI
- `comfyui_custom_nodes/🖥XDEV/LM Studio/lm_prompt_enhancer.py` - SDXL prompt optimization with JSON support
- `tests/test_prompt_tools.py` - Test patterns for prompt tools
- `tests/test_auto_unload.py` - GPU memory management testing patterns
- `docs/docs/comfyui_node_developments_research.md` - Comprehensive ComfyUI node development reference

## Recent Optimizations (Nov 2025)

### JSON Response Format Support
All three main LM Studio nodes (text gen, prompt enhancer, vision) now support `response_format` parameter:
- Add to `INPUT_TYPES` optional section: `"response_format": (["text", "json"], {"default": "text"})`
- If JSON: append to system prompt "Always respond with valid JSON format"
- If JSON: add to payload `"response_format": {"type": "json_object"}`
- Parse with regex `r'\{[^{}]*"key"[^{}]*\}'` with text fallback

### SDXL Prompt Enhancement
Updated prompt enhancer with SDXL research-based best practices:
1. Natural language support - SDXL understands detailed descriptions, not just keywords
2. Keyword weight limits - Keep (keyword:weight) between 1.0-1.4, SDXL is very sensitive
3. Minimal negative prompts - Only include specific things to avoid (e.g., "cartoon" for photos)
4. Artist references - Use specific artist names for style guidance
5. Quality descriptors - Use detailed quality tags (award winning, highly detailed, 8k)
6. Flexible format - Supports both natural language AND comma-separated keywords
7. Composition details - Include framing, perspective, camera settings
8. Research sources - Based on Stability-AI/generative-models and community best practices

### LMS CLI Integration
`lm_auto_unload_trigger.py` uses subprocess to call LM Studio CLI:
```python
result = subprocess.run(["lms", "unload", "--all"], 
                       capture_output=True, text=True, timeout=10)
```
Requires one-time setup: `cmd /c %USERPROFILE%/.lmstudio/bin/lms.exe bootstrap`
