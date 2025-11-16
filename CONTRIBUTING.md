# Contributing Guide

Thanks for helping improve the ComfyUI XDEV node collection! This document explains how to work in this repository.

## 1. Branch & Commit Workflow
- `main` – release-ready, synced with ComfyUI deployments.
- `develop` – optional integration branch for bigger features.
- Use feature branches named `feature/<short-description>` or `fix/<issue-number>`.
- Keep commits focused (tests + code together) and write clear messages, e.g. `feat(prompt): add SDXL JSON output`.

## 2. Before You Start
1. Fork/clone the repo.
2. Create/activate a virtual environment.
3. Install dev requirements: `pip install -e .[dev]`.
4. Copy the project into your ComfyUI `custom_nodes` folder if you want to test inside the UI.

## 3. Coding Guidelines
- All nodes must inherit from the relevant base class in `lm_base_node.py`.
- Return tuples (`return (result,)`) and keep `RETURN_TYPES`/`FUNCTION` consistent.
- Use helpers from `lm_utils.py` for API calls, JSON parsing, info formatting, and error handling.
- Default to ASCII; only use emojis where the UX already relies on them.
- Document complex blocks with a short comment when clarity helps future maintainers.

## 4. Testing Checklist
Run the following before opening a PR:
- `pytest` (runs `tests/test_all_refactored.py` plus smoke suites).
- Manual validation using the [Testing Checklist issue](https://github.com/aiforhumans/comfyui-xdev-nodes/issues/2):
  - Load all nodes inside ComfyUI without errors.
  - Exercise GPU unload helpers if your change touches LM Studio integration.
  - Confirm JSON/text response formats for prompt nodes.

## 5. Pull Request Template
1. Summary of changes + motivation.
2. Screenshots/logs when applicable (e.g., ComfyUI console output).
3. Testing evidence (command output or checklist items checked off).
4. Mention related issues ("Closes #X").

## 6. Release Process
1. Ensure `main` is green on CI and manual checklist.
2. Deploy to ComfyUI locally (`xcopy ...`).
3. Tag `vX.Y.Z` based on semantic versioning (e.g., new nodes = minor bump).
4. Update `pyproject.toml` + `README` if necessary.
5. Draft GitHub release with highlights and testing notes.

## 7. Questions / Support
Open a GitHub issue with:
- Node name(s)
- Reproduction steps / prompt JSON snippet
- Console output or screenshots

Happy building! 🚀
