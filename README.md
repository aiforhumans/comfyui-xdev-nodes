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