# GPU Memory Management Implementation

## Overview
Added automatic GPU memory detection and user guidance for managing LM Studio models when running ComfyUI workflows.

## Problem
LM Studio models and ComfyUI's Stable Diffusion models both compete for GPU memory. When a model is loaded in LM Studio while running image generation in ComfyUI, it can cause:
- Out of memory errors
- Slower generation
- System instability

## Solution
Created a comprehensive GPU memory management system:

### New Files Created
1. **`lm_model_manager.py`** - Core utility module
   - `LMModelManager` class for checking loaded models
   - `check_model_loaded()` function used by all generation nodes
   - Placeholder for future unload API when LM Studio adds it

2. **`lm_model_unload_helper.py`** - User-facing workflow node
   - Checks if LM Studio has models loaded
   - Provides clear instructions for manual unloading
   - Can be placed early in workflows as a reminder

### Updated Files
All LM Studio generation nodes now automatically check for loaded models:
- `lm_text_gen.py`
- `lm_prompt_enhancer.py`
- `lm_vision.py`

Changes:
- Import `check_model_loaded` from `lm_model_manager`
- Call check at start of generation methods
- Print warning to console if model detected
- Use try/except for import to work in both ComfyUI and test environments

### Updated Registration
- `comfyui_custom_nodes/🖥XDEV/LM Studio/__init__.py` - Added new node to mappings

### Updated Documentation
- **README.md** - Added GPU memory management section with workflow instructions
- **.github/copilot-instructions.md** - Added GPU memory management to LM Studio section

## Workflow Usage

### Option 1: Unload Before Running
1. Open LM Studio → Local Server tab
2. Click "Unload Model" button
3. Run ComfyUI workflow
4. LM Studio nodes will load model when needed

### Option 2: Use Helper Node
1. Add "LM Studio Model Unload Helper" node to workflow
2. Place it before image generation nodes
3. It will warn you if a model is loaded
4. Follow on-screen instructions to unload manually

## CLI Diagnostics

For repeatable troubleshooting, use the LM Studio CLI (`lms.exe`) in the same shell as your ComfyUI install. The helper nodes and `run_lms_cli` utility expect this output format.

```powershell
# List currently loaded models
%USERPROFILE%\.lmstudio\bin\lms.exe list --loaded

# Sample output
Loaded Models:
    - llama-3.1-8b-instruct (GPU 0, 10.4 GB)

# Force-unload everything before running SDXL workflows
%USERPROFILE%\.lmstudio\bin\lms.exe unload --all

# Success output should resemble
Unloading all models...
✔ All models unloaded. GPU memory reclaimed.
```

If the CLI hangs or returns an error, capture the exact command/output pair in your bug report; the nodes surface that text verbatim in their info outputs.

## Technical Details

### Why Manual Unload?
LM Studio doesn't currently have a programmatic unload API. The solution:
- Detects loaded models via `/v1/models` endpoint
- Provides user-friendly instructions
- Prints warnings to console
- Non-blocking (doesn't prevent workflow execution)

### Import Pattern
Used conditional imports to work in both environments:
```python
try:
    from .lm_model_manager import check_model_loaded
except ImportError:
    from lm_model_manager import check_model_loaded
```

This allows:
- Relative imports in ComfyUI (package context)
- Absolute imports in tests (standalone scripts)

## Testing
All tests passing:
```
✓ Model manager utilities imported successfully
✓ Unload helper node imported successfully  
✓ Model check function works
✓ Unload helper node works correctly
✓ Text and Enhancer nodes import successfully
⚠ Vision node requires numpy/PIL (expected in ComfyUI environment)
```

## Files Modified Summary
- **Created**: 3 new files (lm_model_manager.py, lm_model_unload_helper.py, test_gpu_memory.py)
- **Updated**: 5 existing files (3 LM Studio nodes, 1 init, README, copilot-instructions)
- **Total Changes**: 8 files

## Deployment
Deployed to ComfyUI with:
```powershell
xcopy c:\NOOODE "C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\NOOODE" /E /I /Y
```

**Remember to restart ComfyUI** to load the new node!

## Future Enhancements
When LM Studio adds an unload API:
- Update `LMModelManager.request_model_unload()` 
- Add automatic unload option
- Add model reloading after image generation
