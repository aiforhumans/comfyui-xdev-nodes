# ComfyUI XDev Nodes — Expanded

A clean, CI-ready **starter kit** for building and publishing **ComfyUI custom nodes**.  
It shows the minimal patterns you need (inputs, returns, registration), includes sample nodes, example workflows, tests, and a ready-to-use CI pipeline.

---

## Highlights

- Minimal examples: **HelloString**, **AnyPassthrough**, **AppendSuffix**, **PickByBrightness**
- Clean structure for **backend nodes** (+ optional `web/` assets)
- **Registry-ready**: `pyproject.toml` with `[tool.comfy]`
- **Workflows** for instant validation
- **Tests + GitHub Actions** for quality gates
- Docs & quick **datatype** reference

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

Open an example workflow from `workflows/` to test.

---

## Node Reference (this pack)

### 1) HelloString
- `INPUT_TYPES` → `{ "required": {} }`
- `RETURN_TYPES` → `("STRING",)`
- `FUNCTION` → `"hello"`
- Purpose: return a static greeting.

### 2) AnyPassthrough
- `INPUT_TYPES` → `{ "required": { "value": ("*", {}) } }`
- `RETURN_TYPES` → `("*",)`
- `FUNCTION` → `"do_it"`
- Purpose: pass any value through unchanged.

### 3) AppendSuffix
- `INPUT_TYPES` → `{ "required": { "text": ("STRING", {"default": ""}), "suffix": ("STRING", {"default": " - xdev"}) } }`
- `RETURN_TYPES` → `("STRING",)`
- `FUNCTION` → `"run"`
- Purpose: append a suffix to a string.

### 4) PickByBrightness
- `INPUT_TYPES` → `{ "required": { "images": ("IMAGE", {}), "mode": (["brightest","darkest"], {"default":"brightest"}) } }`
- `RETURN_TYPES` → `("IMAGE",)`
- `FUNCTION` → `"pick"`
- Purpose: pick brightest or darkest image in a batch.  
- Note: uses **torch** if present; falls back to **NumPy** or pure Python.

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

- `workflows/hello_string_save.json`
  - Chain: `XDEV_HelloString → SaveText`
- `workflows/pick_by_brightness_preview.json`
  - Chain: `LoadImage(s) → XDEV_PickByBrightness → PreviewImage`

These are **illustrative**; tweak to your ComfyUI version/plugins.

---

## Development

```bash
# dev install
pip install -e .
# run tests
pytest -q
# lint (ruff)
ruff .
```

Tips:
- Keep node classes small and focused.
- Name IDs with a clear prefix (e.g., `XDEV_`).
- Avoid heavy logs in hot paths.

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

## Contributing

- Open issues with templates in `.github/ISSUE_TEMPLATE/`
- PRs: follow the checklist in `pull_request_template.md`
- Keep examples minimal and well-commented

---

## License

MIT — see `LICENSE`.

---

## Kort in het Nederlands (samenvatting)

Dit is een **startpakket** voor ComfyUI-nodes.  
Zet de map in `ComfyUI/custom_nodes/`, herstart ComfyUI, en je ziet de nodes in de UI.  
Voorbeelden, workflows, tests en CI zijn inbegrepen.  
Nieuwe node? Kopieer een voorbeeld, pas `INPUT_TYPES`/`RETURN_TYPES`/`FUNCTION` aan, registreer in `__init__.py`, klaar.
