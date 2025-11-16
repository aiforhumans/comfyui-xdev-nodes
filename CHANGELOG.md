# Changelog

All notable changes to this project will be documented in this file. This log follows the Keep a Changelog format and uses ISO dates.

## [Unreleased]
- Nothing yet.

## [0.1.0] - 2025-11-16

### Added
- ASCII-safe registry module `comfyui_custom_nodes.xdev` that mirrors the emoji folder structure for easier imports and testing.
- Shared SDXL prompt helper module `comfyui_custom_nodes/🖥XDEV/LM Studio/prompt_templates.py` plus related documentation in `docs/guides/`.
- Repository automation assets such as `.editorconfig`, Ruff/isort settings in `pyproject.toml`, and the GitHub Actions workflow under `.github/workflows/`.
- Centralized pytest fixtures in `tests/conftest.py` to wire up the alias package inside the test environment.
- Prompt style catalog + workflow smoke tests (`tests/test_workflow_sdxl.py`) ensuring prompt tools and LM Studio nodes stay in sync.
- `.github/agents/*` definitions describing Copilot agent responsibilities for this repo.

### Changed
- Root `comfyui_custom_nodes/__init__.py` now re-exports node mappings from the ASCII alias to keep ComfyUI discovery intact and the alias loader now uses `importlib` for better editor support.
- LM Studio prompt enhancer/text generation nodes refactored to consume the new prompt templates and share helpers; SDXL prompt builder now surfaces descriptive lighting/composition hints.
- Documentation reorganized so SDXL, GPU memory, UX, and other guides live under `docs/guides/` with updated `README.md` links plus new CLI diagnostic examples.
- Expanded test coverage across `tests/test_*.py` to match the refactored node interfaces and optional parameters, including JSON response-mode assertions.

### Fixed
- Ensured `LMStudioTextGen` exposes `temperature` as an optional input while keeping backward-compatible defaults.
- Updated LM Studio tests to match the new INPUT_TYPES contract and prevent false negatives when JSON mode is disabled.
- Added skips for the sample node tests when `example_node.py` is not present, avoiding unnecessary failures in downstream forks.
- Eliminated Pylance missing-import warnings by dynamically importing modules inside the ASCII alias loader.
