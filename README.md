# ComfyUI XDev Nodes — Expanded

A clean, CI‑ready starter kit for **ComfyUI custom node development**. Includes:

- Minimal Python nodes with clear INPUT/RETURN metadata
- Image/text utilities
- Optional frontend `web/` folder (served by ComfyUI)
- Packaging metadata compatible with the ComfyUI Registry
- Tests you can adapt for your CI

## Install (local dev)

```bash
git clone https://github.com/aiforhumans/comfyui-xdev-nodes
cd comfyui-xdev-nodes
# Developer install
pip install -e .
```
Then link/copy this folder into your `ComfyUI/custom_nodes/` directory (or use ComfyUI Manager).

## Nodes
- **HelloString** — returns a constant greeting.
- **AnyPassthrough** — demonstrates the `ANY` datatype; returns input unchanged.
- **PickByBrightness** — picks brightest/darkest image from batch.
- **AppendSuffix** — appends a suffix to text.

## Notes
- `image.py` gracefully degrades if `torch` is not available (falls back to NumPy / pure Python).

---

## Next steps (recommended)

### 1) Fill in registry metadata
Edit `pyproject.toml`:
- Set `[tool.comfy]` → `PublisherId` (usually your GitHub username), `DisplayName`, and add `Icon` and `Banner` URLs (raw GitHub links to images in this repo).
- Keep `requires-comfyui` aligned with the versions you test.

### 2) Add a Help Page for ComfyUI Manager
Create a short help page in `docs/` and link it from the README. Include:
- What each node does (with screenshots)
- Example workflows (`.json`) and expected outputs
- Known limitations / GPU/CPU notes

### 3) Provide example workflows
Add a `workflows/` folder with small demo `.json` workflows that use your nodes. This helps users validate install quickly.

### 4) Set up tests & lint
- Add/extend `tests/` and run locally:
  ```bash
  pip install -r requirements-dev.txt  # if you add one
  pytest -q
  ```
- (Optional) Add linting:
  ```toml
  # example ruff config in pyproject.toml
  [tool.ruff]
  line-length = 100
  select = ["E","F","I","UP"]
  ```
- (Optional) Pre-commit hooks:
  ```bash
  pip install pre-commit
  pre-commit install
  ```

### 5) Add CI (GitHub Actions)
Create `.github/workflows/ci.yml` to run `pytest` and `ruff` on push/PR. Example job:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -e . pytest ruff
      - run: ruff .
      - run: pytest -q
```

### 6) Version & releases
- Use SemVer in `pyproject.toml` (`1.0.0`, `1.1.0`, `1.1.1`).
- Tag releases in Git for distribution and easier rollback:
  ```bash
  git tag v0.1.1 -m "XDev Nodes initial release"
  git push --tags
  ```

### 7) Publish checklist (manual install or registry)
- ✅ `pyproject.toml` is complete and valid
- ✅ Folder name equals the package/repo name
- ✅ Nodes load cleanly in ComfyUI (no stdout/stderr spam)
- ✅ Example workflows run end‑to‑end
- ✅ README + screenshots + help page are up-to-date

### 8) UX polish (optional but nice)
- Add icons/banners and per-node thumbnails
- Provide tooltips for parameters in docstrings
- Add categories/subcategories that match your ecosystem

### 9) Backwards compatibility & deprecation
- If you rename node IDs, add shims or a migration note
- Avoid breaking inputs/outputs without a major version bump

### 10) Issue templates
Add `.github/ISSUE_TEMPLATE/` with bug/feature templates to streamline user reports.

---

## Project layout
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
  web/
    __init__.py                 # optional frontend assets
tests/
  test_imports.py
  test_basic_nodes.py
workflows/                      # (recommended) example .json workflows
docs/                           # (recommended) help page for ComfyUI Manager
```