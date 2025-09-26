# ComfyUI XDev Nodes — Professional Starter Kit

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/aiforhumans/comfyui-xdev-nodes)](https://github.com/aiforhumans/comfyui-xdev-nodes/releases)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/aiforhumans/comfyui-xdev-nodes/ci.yml)](https://github.com/aiforhumans/comfyui-xdev-nodes/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-1.0%2B-green)](https://github.com/comfyanonymous/ComfyUI)

A **production-ready starter kit** for building and publishing **ComfyUI custom nodes** with professional-grade patterns, comprehensive validation, rich documentation, and complete GitHub standards.

> 🚀 **NEW**: Complete development toolkit with 8 professional nodes including VAE tools, universal type testing, and comprehensive debugging infrastructure.

> 🔧 **ENHANCED**: Advanced input validation, rich tooltips, error handling, and professional development patterns inspired by enterprise-grade ComfyUI frameworks.

---

## ✨ Key Features

### Professional Development Patterns
- 🔍 **Comprehensive Input Validation** - Detailed type checking with informative error messages
- 📚 **Rich Tooltip Documentation** - Professional-grade help text for all inputs
- 🛡️ **Robust Error Handling** - Graceful degradation and fallback implementations
- 🎯 **Multiple Output Formats** - Enhanced return types with metadata and processing info
- ⚡ **Smart Caching** - Proper ComfyUI cache management with `IS_CHANGED`

### Enhanced Node Examples
- **HelloString** - Basic node patterns with validation
- **AnyPassthrough** - Type-safe passthrough with comprehensive checks
- **AppendSuffix** - Text processing with multiline support and validation
- **PickByBrightness** - Advanced image processing with multiple algorithms (torch/numpy/python fallbacks)
- **OutputDev** - Universal debugging output accepting all 18 ComfyUI types
- **InputDev** - Test data generator for 12 core ComfyUI types
- **VAERoundTrip** - Complete VAE encode/decode cycle testing
- **VAEPreview** - Quick latent visualization and analysis

### Complete Development Toolkit
- 🎯 **Universal Type Testing** - InputDev generates, OutputDev analyzes all 18 ComfyUI types
- 🔄 **VAE Operations** - Complete encode/decode cycle testing and quick preview tools
- 🔍 **Advanced Debugging** - Multi-input comparison, memory analysis, file export
- 📊 **Professional Validation** - Type checking, error handling, processing statistics
- ⚡ **Performance Monitoring** - Memory usage, processing time, efficiency metrics

### Professional Infrastructure
- 🏗️ **GitHub Standards** - Complete CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- 🔒 **Security Guidelines** - ComfyUI-specific security best practices
- 📊 **Comprehensive Testing** - Unit tests with validation scenarios
- 🚀 **CI/CD Pipeline** - Automated testing, linting, and quality gates
- 📖 **Rich Documentation** - Web-based help system with markdown docs

---

## Quick Start

```bash
# Developer install
git clone https://github.com/aiforhumans/comfyui-xdev-nodes
cd comfyui-xdev-nodes
pip install -e .
```
Place this folder (or a symlink) in:
```
<your-ComfyUI-root>/custom_nodes/comfyui-xdev-nodes
```
Start ComfyUI. Nodes appear under:
- `XDev/Basic`
- `XDev/Text`
- `XDev/Image`
- `XDev/Development`
- `XDev/VAE Tools`

Open an example workflow from `workflows/` to test.

---

## Node Reference (this pack)

### 1) 👋 HelloString (XDev)
**Category**: `XDev/Basic` | **Enhanced with validation patterns**

- **Purpose**: Demonstrates basic node structure with comprehensive validation
- **Inputs**: None (shows minimal input pattern)
- **Outputs**: `STRING` - Static greeting message
- **Features**: Input validation framework, rich tooltips, professional error handling
- **Use Case**: Learning foundation patterns for ComfyUI node development

### 2) 🔄 AnyPassthrough (XDev) 
**Category**: `XDev/Basic` | **Type-safe passthrough**

- **Purpose**: Pass any value through unchanged with type validation
- **Inputs**: `value` (ANY) - Any input type with comprehensive validation
- **Outputs**: `*` - Original value unchanged, with processing metadata
- **Features**: Type checking, null/undefined handling, processing statistics
- **Use Case**: Debugging workflows, type conversion, data flow analysis

### 3) ✏️ AppendSuffix (XDev)
**Category**: `XDev/Text` | **Professional text processing**

- **Purpose**: Advanced text manipulation with multiline support
- **Inputs**: 
  - `text` (STRING) - Main text content (multiline supported)
  - `suffix` (STRING) - Suffix to append
  - `validate_input` (BOOLEAN) - Enable comprehensive validation
- **Outputs**: 
  - `processed_text` (STRING) - Text with suffix appended
  - `character_count` (INT) - Total character count
  - `processing_info` (STRING) - Processing metadata
- **Features**: Multiline text handling, input validation, processing statistics

### 4) 🖼️ PickByBrightness (XDev)
**Category**: `XDev/Image` | **Advanced image processing**

- **Purpose**: Intelligent image selection with multiple algorithms
- **Inputs**:
  - `images` (IMAGE) - Image batch to process
  - `algorithm` - Selection algorithm: `["average", "luminance", "perceived", "channel_max"]`
  - `mode` - Selection mode: `["brightest", "darkest"]`
- **Outputs**:
  - `selected_image` (IMAGE) - Chosen image
  - `brightness_score` (FLOAT) - Calculated brightness value
  - `algorithm_info` (STRING) - Processing details
- **Features**: 
  - **Robust Fallbacks**: torch → numpy → pure Python implementations
  - **Multiple Algorithms**: Average, luminance, perceived brightness, channel max
  - **Professional Validation**: Comprehensive input checking and error handling

### 5) 🔍 OutputDev (XDev) 
**Category**: `XDev/Development` | **Universal debugging output**

- **Purpose**: Universal debugging and analysis node for any ComfyUI data type
- **Inputs**:
  - `input_1` (ANY) - Primary input accepting any ComfyUI data type
  - `input_2` (ANY, optional) - Secondary input for comparison
  - `input_3` (ANY, optional) - Tertiary input for comparison
  - `display_level` - Analysis detail: `["summary", "detailed", "full"]`
  - `save_to_file` (BOOLEAN) - Export analysis to timestamped file
  - `compare_inputs` (BOOLEAN) - Compare multiple inputs when connected
- **Outputs**: None (OUTPUT_NODE - terminates workflow)
- **Features**:
  - **Enhanced Type Compatibility**: Explicitly supports LATENT, MODEL, CONDITIONING, MASK, and all ComfyUI types
  - **Multi-Input Comparison**: Compare up to 3 different data streams simultaneously
  - **Memory Analysis**: Display tensor memory usage and statistics for all tensor types
  - **Content Preview**: Safe preview of actual data values with statistics
  - **File Export**: Save detailed analysis to timestamped text files

### 6) 🎯 InputDev (XDev)
**Category**: `XDev/Development` | **Universal test data generator**

- **Purpose**: Generate test data of any ComfyUI type for testing and debugging
- **Inputs**:
  - `output_type` - Data type: `["STRING", "INT", "FLOAT", "BOOLEAN", "IMAGE", "LATENT", "MASK", "MODEL", "CONDITIONING", "LIST", "DICT", "MOCK_TENSOR"]`
  - `output_mode` - Generation mode: `["simple", "realistic", "stress_test"]`
  - `custom_value` (STRING, optional) - Custom value to convert to target type
  - `size_parameter` (INT) - Size for images, lists, tensor dimensions
  - `seed` (INT) - Random seed for reproducible generation
  - `include_metadata` (BOOLEAN) - Include descriptive metadata output
- **Outputs**:
  - `generated_data` (ANY) - Generated data of specified type
  - `metadata` (STRING) - Description of generated data
- **Features**:
  - **12 Data Types**: Generate all core ComfyUI types including LATENT, MODEL, CONDITIONING, MASK
  - **3 Generation Modes**: Simple (minimal), Realistic (typical), Stress Test (edge cases)
  - **Reproducible**: Seed-based generation for consistent test results
  - **Custom Values**: Convert custom input to any target type
  - **ComfyUI Compatible**: Proper tensor formats, LATENT dicts, MODEL objects, CONDITIONING arrays

### 7) 🔄 VAE Round-Trip (XDev)
**Category**: `XDev/VAE Tools` | **Complete VAE encode/decode cycle**

- **Purpose**: Perform complete VAE round-trip: LATENT → DECODE → ENCODE → LATENT
- **Inputs**:
  - `latent` (LATENT) - Input latent to decode and re-encode
  - `vae` (VAE) - VAE model for decoding/encoding operations
  - `show_stats` (BOOLEAN) - Display processing statistics
  - `quality_check` (BOOLEAN) - Compare input vs output latent quality
  - `decode_only` (BOOLEAN) - Only decode without re-encoding
- **Outputs**:
  - `decoded_image` (IMAGE) - Visual representation of latent
  - `reencoded_latent` (LATENT) - Re-encoded latent for comparison
  - `process_info` (STRING) - Detailed processing statistics
- **Features**:
  - **Complete VAE Testing**: Full encode/decode cycle validation
  - **Quality Analysis**: Compare original vs round-trip latents
  - **Memory Monitoring**: Track memory usage during processing
  - **Visual Inspection**: See what your latents actually represent
  - **Performance Metrics**: Processing time and efficiency statistics

### 8) 👁️ VAE Preview (XDev)  
**Category**: `XDev/VAE Tools` | **Quick latent preview**

- **Purpose**: Fast LATENT → IMAGE decoding for visual inspection and debugging
- **Inputs**:
  - `latent` (LATENT) - Input latent to decode and preview
  - `vae` (VAE) - VAE model for decoding operations
  - `add_info_text` (BOOLEAN) - Add informational overlay
  - `preview_mode` - Processing level: `["full", "fast", "minimal"]`
- **Outputs**:
  - `preview_image` (IMAGE) - Decoded preview image
  - `latent_info` (STRING) - Analysis of latent properties
- **Features**:
  - **Lightweight Preview**: Quick visualization without full processing
  - **Multiple Modes**: Full analysis, fast preview, or minimal decode
  - **Latent Analysis**: Shape, memory usage, and value range validation
  - **Debug Information**: Comprehensive latent property reporting
  - **ComfyUI Compatible**: Proper IMAGE output format (0-1 range validation)

---

## How ComfyUI discovers your nodes

`xdev_nodes/__init__.py` exposes:
- `NODE_CLASS_MAPPINGS`: `"XDEV_NodeId" → PythonClass`
- `NODE_DISPLAY_NAME_MAPPINGS`: `"XDEV_NodeId" → "Pretty Name"`
- Optional: `WEB_DIRECTORY` for serving `web/` assets

ComfyUI imports the package, reads those mappings, and renders nodes in the UI.

---

## Create Your Own Node (recipe)

1. **Copy** one of the example classes (e.g., `AppendSuffix`).
2. Change:
   - `INPUT_TYPES` (widget types + options)
   - `RETURN_TYPES` (output sockets)
   - `FUNCTION` (method name)
   - Method signature (params match inputs)
3. **Register** the class in `xdev_nodes/__init__.py`:
   - Add to `NODE_CLASS_MAPPINGS`
   - Add to `NODE_DISPLAY_NAME_MAPPINGS`
4. Restart ComfyUI → test in a workflow.

---

## Project Layout

```
pyproject.toml
README.md
LICENSE
xdev_nodes/
  __init__.py                   # NODE_CLASS_MAPPINGS, display names, WEB_DIRECTORY
  nodes/
    __init__.py
    basic.py                    # HelloString, AnyPassthrough
    image.py                    # PickByBrightness (torch/NumPy/Python fallback)
    text.py                     # AppendSuffix
    dev_nodes.py                # OutputDev, InputDev (universal debugging/testing)
    vae_tools.py                # VAERoundTrip, VAEPreview (VAE operations)
  web/
    __init__.py                 # optional frontend assets
workflows/
  hello_string_save.json
  pick_by_brightness_preview.json
tests/
  test_imports.py
  test_basic_nodes.py
.github/
  workflows/ci.yml
  ISSUE_TEMPLATE/
    bug_report.md
    feature_request.md
  pull_request_template.md
docs/
  how_to_pick_types.png
```

---

## ComfyUI Datatypes — Quick Reference

> Use in nodes:  
> `INPUT_TYPES = lambda: {"required": {"arg": (<TYPE>, {opts})}}`  
> `RETURN_TYPES = ("<TYPE>", ... )`

### Core types
| Datatype | Input Spec (examples) | Python / Shape | Notes |
|---|---|---|---|
| INT | `("INT", {"default": 0, "min": 0, "max": 100})` | `int` | Bounds, step |
| FLOAT | `("FLOAT", {"default": 0.5, "step": 0.01})` | `float` | Bounds, step |
| STRING | `("STRING", {"default": ""})` | `str` | `multiline`, `placeholder` |
| BOOLEAN | `("BOOLEAN", {"default": False})` | `bool` | Toggle labels |
| IMAGE | `("IMAGE", {})` | `Tensor [B,H,W,C]` | RGB 0..1 or 0..255 |
| LATENT | `("LATENT", {})` | `dict["samples": Tensor [B,C,H,W]]` | + extras |
| MASK | `("MASK", {})` | `Tensor [H,W]` or `[B,1,H,W]` | Binary/float |
| AUDIO | `("AUDIO", {})` | `dict["waveform": Tensor [B,C,T]]` | + rate |
| * (ANY) | `("*", {})` | passthrough | any |

### Dropdown (COMBO)
| Pattern | Example | Returns |
|---|---|---|
| Fixed list | `(["brightest","darkest"], {"default":"brightest"})` | `str` |
| File list | `(folder_paths.get_filename_list("checkpoints"), {})` | `str` |

### Pipeline
| Datatype | Input Spec | Python | Notes |
|---|---|---|---|
| NOISE | `("NOISE", {})` | object | `.generate_noise` |
| SAMPLER | `("SAMPLER", {})` | object | `.sample(...)` |
| SIGMAS | `("SIGMAS", {})` | 1-D tensor | steps+1 |
| GUIDER | `("GUIDER", {})` | callable | predict noise |
| MODEL/CLIP/VAE/CONDITIONING | `("MODEL", {})`, etc. | objects | SD parts |

### Useful input options
| Key | Meaning | Example |
|---|---|---|
| `default` | initial value | `{"default": 0.5}` |
| `min/max/step` | numeric bounds | `{"min":0,"max":1,"step":0.01}` |
| `multiline` | multi-line | `{"multiline": true}` |
| `placeholder` | hint | `{"placeholder":"Enter prompt"}` |
| `defaultInput` | socket default | `{"defaultInput": true}` |
| `forceInput` | require link | `{"forceInput": true}` |
| `lazy` | defer compute | `{"lazy": true}` |
| `rawLink` | pass raw | `{"rawLink": true}` |

---

## How to Pick Types (flowchart)

See the visual guide at:
```
docs/how_to_pick_types.png
```

---

## Example Workflows

### Basic Node Testing
- `workflows/hello_string_save.json`
  - Chain: `XDEV_HelloString → SaveText`
- `workflows/pick_by_brightness_preview.json`
  - Chain: `LoadImage(s) → XDEV_PickByBrightness → PreviewImage`

### Advanced Development Workflows  
- **Universal Type Testing**: `XDEV_InputDev → XDEV_OutputDev`
  - Test any ComfyUI data type generation and analysis
- **VAE Complete Cycle**: `VAELoader → XDEV_InputDev(LATENT) → XDEV_VAERoundTrip → XDEV_OutputDev`
  - Full VAE encode/decode testing with analysis
- **Quick VAE Preview**: `XDEV_InputDev(LATENT) → XDEV_VAEPreview`
  - Fast latent visualization for debugging

### Recommended Testing Chain
```
VAELoader → XDEV_InputDev → XDEV_VAERoundTrip → XDEV_OutputDev
    ↓              ↓              ↓              ↓
   VAE          LATENT      IMAGE+LATENT     Analysis
```

These are **illustrative**; tweak to your ComfyUI version/plugins.

---

## 🎯 Development Use Cases

### Universal Type Testing
Use **InputDev** and **OutputDev** for comprehensive type compatibility testing:
- Generate any ComfyUI type with realistic or stress-test data
- Analyze output from any node with detailed statistics
- Compare multiple data streams with side-by-side analysis
- Export detailed analysis to timestamped files

### VAE Development & Debugging
Use **VAE tools** for encode/decode workflow validation:
- **VAEPreview**: Quick latent visualization during development
- **VAERoundTrip**: Complete cycle testing with quality analysis
- Test VAE compatibility, memory usage, and processing efficiency
- Validate proper IMAGE format output (0-1 range checking)

### Node Development Patterns
Learn from our **professional node examples**:
- **Comprehensive Validation**: See `AppendSuffix` for input validation patterns
- **Fallback Systems**: Study `PickByBrightness` for torch/numpy/python fallbacks  
- **Error Handling**: All nodes demonstrate graceful error recovery
- **Rich Documentation**: Every input has detailed tooltips and help text

### Testing & Debugging Workflows
- **Type Chain Testing**: `InputDev(TYPE) → YourNode → OutputDev`
- **VAE Workflow Testing**: `VAELoader → InputDev(LATENT) → YourVAENode → VAERoundTrip`
- **Multi-Input Analysis**: Connect multiple outputs to `OutputDev` for comparison
- **Performance Profiling**: Use processing statistics and memory analysis

---

## 🛠️ Development

### Setup
```bash
# Development installation
git clone https://github.com/aiforhumans/comfyui-xdev-nodes
cd comfyui-xdev-nodes
pip install -e .

# Create development symlink
scripts/dev-link.ps1  # Windows
scripts/dev-link.sh   # Unix/Linux
```

### Testing & Quality
```bash
# Run comprehensive tests
pytest -q

# Lint with ruff
ruff .

# Test specific validation scenarios
python -m pytest tests/test_basic_nodes.py::test_validation_patterns -v
```

### Professional Development Tips
- 📝 **Rich Documentation**: Every input needs comprehensive tooltips
- ✅ **Input Validation**: Implement `_validate_inputs()` method with detailed error messages
- 🎯 **Multiple Outputs**: Return processing metadata alongside main results
- 🔄 **Fallback Patterns**: Gracefully handle missing dependencies (see `image.py`)
- 🏷️ **Clear Naming**: Use prefixed IDs (e.g., `XDEV_`) and descriptive categories
- 📊 **Processing Info**: Include algorithm details and performance metrics in outputs

### Code Quality Standards
- **Type Hints**: Use comprehensive type annotations
- **Error Handling**: Never crash workflows - return error messages as outputs
- **Resource Management**: Implement proper memory and time limits for processing
- **Security**: Validate file paths and sanitize all user inputs
- **Performance**: Cache expensive computations with `IS_CHANGED`

---

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs:
- Install + `pytest`
- `ruff` lint

Trigger: push / PR to `main` or `master`.

---

## Registry Metadata (pyproject.toml)

- `[project]`: `name`, `version`, `description`, `license`, `urls`, `requires-python`
- `[tool.comfy]`:
  - `PublisherId`: your ID (often GitHub username)
  - `DisplayName`: friendly name
  - `Icon` / `Banner`: raw URLs (square icon; 21:9 banner)
  - `requires-comfyui`: version range (e.g., `>=1.0.0`)
  - `includes`: extra folders (e.g., `'dist'`)

**SemVer**: bump `MAJOR.MINOR.PATCH` for changes.

---

## Publish Checklist

- `pyproject.toml` complete
- Nodes load; no errors
- Example workflows run
- README + screenshots updated
- CI green
- Tag release (e.g., `v0.1.1`)

---

## Troubleshooting

- **Nodes don’t show**
  - Folder in `custom_nodes/`?
  - Package imports without errors?
  - Registered in `NODE_CLASS_MAPPINGS`?

- **Missing torch**
  - Install `torch` (GPU/CPU) or rely on fallbacks in `image.py`.

- **Version mismatch**
  - Check `requires-comfyui`; update ComfyUI if needed.

- **Weird datatypes**
  - Use the Quick Reference and flowchart; prefer simple types first.

---

## 🤝 Contributing

We welcome contributions! This project follows professional GitHub standards:

### Getting Started
- 📋 **[Contributing Guidelines](CONTRIBUTING.md)** - Comprehensive development setup and patterns
- 🤝 **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards and educational focus
- 🔒 **[Security Policy](SECURITY.md)** - Vulnerability reporting and ComfyUI security best practices

### Development Process
- Open issues using templates in `.github/ISSUE_TEMPLATE/`
- Follow the PR checklist in `pull_request_template.md`
- Include validation test cases for new features
- Add comprehensive documentation with examples
- Ensure all nodes follow XDev professional patterns

### Code Review Focus
- ✅ Input validation and error handling
- 📚 Rich tooltip documentation
- 🛡️ Security considerations for ComfyUI environments
- 🧪 Test coverage including edge cases
- 📖 Clear documentation with working examples

---

## License

MIT — see `LICENSE`.

---

## Kort in het Nederlands (samenvatting)

Dit is een **complete ontwikkeltoolkit** voor ComfyUI-nodes met 8 professionele nodes.  
Zet de map in `ComfyUI/custom_nodes/`, herstart ComfyUI, en je ziet alle nodes in de UI.  
Inclusief VAE-tools, universele type-testing, debugging, voorbeelden, workflows, tests en CI.  
Nieuwe node? Kopieer een voorbeeld, pas `INPUT_TYPES`/`RETURN_TYPES`/`FUNCTION` aan, registreer in `__init__.py`, klaar.
