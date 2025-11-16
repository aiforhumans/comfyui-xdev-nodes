# ComfyUI XDEV Nodes

High-performance LM Studio + prompt engineering toolkit for ComfyUI. This repository contains 24 production-ready custom nodes organized under the 🖥XDEV namespace, a unified testing strategy, and complete documentation for deployment inside ComfyUI or reuse in other projects.

## Highlights
- ✅ 24 nodes covering text generation, prompt automation, GPU-memory safety, batch workflows, and regional prompting.
- ✅ Common base classes (`lm_base_node.py`) and utilities (`lm_utils.py`) keep logic DRY and make future maintenance simple.
- ✅ GPU-friendly LM Studio integration with automatic model detection, warnings, and CLI-based unloading.
- ✅ Comprehensive documentation (`docs/`) plus a structured GitHub testing checklist ([Issue #2](https://github.com/aiforhumans/comfyui-xdev-nodes/issues/2)).
- ✅ Ready-to-ship `pyproject.toml`, tests, and deployment scripts for GitHub CI/CD.

## Requirements
- Python 3.10–3.13 verified locally
- ComfyUI (portable Windows build or standard install)
- LM Studio (for LM nodes)
- Optional: VS Code + Copilot, `pytest`

## Quick Start
1. **Clone + set up environment**
	```powershell
	git clone https://github.com/aiforhumans/comfyui-xdev-nodes
	cd comfyui-xdev-nodes
	python -m venv .venv
	.venv\Scripts\activate
	pip install -r requirements.txt
	pip install -r requirements-dev.txt  # linting + Ruff + pytest
	```
2. **Run the test suite**
	```powershell
	python -m pytest
	```
3. **Lint (optional but recommended)**
	```powershell
	python -m ruff check
	```
4. **Copy into ComfyUI** using the deployment command in the section below.

## Installation

### Option A – Deploy inside ComfyUI
```powershell
git clone https://github.com/aiforhumans/comfyui-xdev-nodes NOOODE
xcopy NOOODE C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\NOOODE /E /I /Y /Q
```
Restart ComfyUI and look under **🖥XDEV/** for all nodes.

### Option B – Local development
```powershell
git clone https://github.com/aiforhumans/comfyui-xdev-nodes
cd comfyui-xdev-nodes
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
pytest
```

## Node Catalog

### Prompt tools (🖥XDEV/Prompt tools)
- `text_concatenate.py` – Merge up to five strings with separators.
- `multiline_prompt.py` – Subject/style/composition prompt builder.
- `style_injector.py` – 10 style banks with adjustable strength.
- `random_prompt.py` – Weighted random prompt selection.
- `prompt_template.py` – Template + variable substitution system.

### LM Studio Core (🖥XDEV/LM Studio)
- `lm_text_gen.py` – General text generation with local LLMs.
- `lm_prompt_enhancer.py` – SDXL-ready prompt enhancer with JSON option.
- `lm_vision.py` – Image understanding with tensor→base64 conversion.
- `lm_streaming_text_gen.py` – SSE streaming outputs for realtime UX.
- `lm_batch_processor.py` – Queue multiple prompts with throttling.

### Prompt engineering suite
- `lm_persona_creator.py`
- `lm_prompt_mixer.py`
- `lm_scene_composer.py`
- `lm_sdxl_prompt_builder.py`
- `lm_aspect_ratio_optimizer.py`
- `lm_refiner_prompt_generator.py`
- `lm_controlnet_prompter.py`
- `lm_regional_prompter.py`

### Utility + safety nodes
- `lm_token_counter.py`, `lm_response_validator.py`, `lm_context_optimizer.py`
- `lm_parameter_presets.py`, `lm_model_selector.py`, `lm_multi_model_selector.py`
- `lm_model_unload_helper.py`, `lm_auto_unload_trigger.py`
- `lm_chat_history.py`, `lm_model_manager.py`, `lm_utils.py`, `lm_base_node.py`

Every node inherits from the LM Studio base classes to ensure consistent inputs (server URL, model, temperature, response format) and info outputs.

## Architecture Overview

```
comfyui_custom_nodes/
├── __init__.py
└── 🖥XDEV/
		├── Prompt tools/
		└── LM Studio/
				├── lm_base_node.py        # Base classes
				├── lm_utils.py            # API client, JSON parsing, info helpers
				├── lm_model_manager.py    # GPU memory + LM Studio state checks
				└── <24 node modules>
```

Supporting docs live in `docs/` (see [docs/README.md](docs/README.md) for a curated index). Tests are under `tests/` with `test_all_refactored.py` covering imports, inheritance, helper utilities, and backward compatibility.

## Development Workflow
1. Edit nodes in `comfyui_custom_nodes/🖥XDEV/...`.
2. Run local tests: `pytest tests` or targeted scripts inside `tests/`.
3. Deploy via `xcopy` helper command to your ComfyUI install.
4. Follow the [testing checklist](https://github.com/aiforhumans/comfyui-xdev-nodes/issues/2) before pushing.

## Testing
- `tests/test_all_refactored.py` – Imports, inheritance, helper validation.
- `tests/test_prompt_tools.py`, `tests/test_lm_studio.py`, `tests/test_auto_unload.py` – Smoke + regression coverage.
- Use GitHub Issue #2 to track manual QA flows (Vision, Batch, Chat History, GPU unload, error handling, etc.).

## Deployment to ComfyUI
```powershell
xcopy c:\NOOODE C:\ComfyUI_windows_portable\ComfyUI\custom_nodes\NOOODE /E /I /Y /Q
```
Always restart ComfyUI; the loader caches Python modules.

## Documentation
- `docs/README.md` – Entry point with links to SDXL research, troubleshooting, workflow templates, etc.
- Deep dives include:
	- `docs/docs/comfyui_node_developments_research.md`
	- `docs/docs/comfyui_prompt_mastering_guide.md`
	- `docs/docs/comfyui_troubleshooting_guide.md`
	- `docs/REFACTORING_SUMMARY.md` (history of the 24-node rewrite)
- Focused guides now live under `docs/guides/`:
	- `gpu_memory.md` – LM Studio unload workflow + warnings
	- `sdxl_prompting.md` – Research notes powering prompt enhancer
	- `ux_improvements.md` – Info panel + Copilot UX guidelines

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for a dated list of repository updates, refactors, and fixes.

## Contributing & License
- See [CONTRIBUTING.md](CONTRIBUTING.md) for branch conventions, testing requirements, and release steps.
- Licensed under [MIT](LICENSE).

---

**Maintained by [AI for Humans](https://github.com/aiforhumans)** – contributions, bug reports, and workflow ideas are always welcome!
