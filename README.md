# ComfyUI — Xtremedev Nodes

Production‑ready custom nodes for ComfyUI with clean templates, tests, and CI.

## Quick Start
1. **Clone:**
   ```bash
   git clone https://github.com/yourname/comfyui-xdev-nodes.git
   cd comfyui-xdev-nodes
   ```
2. **Link into ComfyUI:** (Windows PowerShell)
   ```powershell
   ./scripts/dev-link.ps1 -ComfyPath "C:\comfy\ComfyUI"
   ```
   Linux/Mac:
   ```bash
   ./scripts/dev-link.sh /path/to/ComfyUI
   ```
3. **Run ComfyUI**, search for category **Xtremedev/** and try the sample nodes.

## Layout
```
comfyui-xdev-nodes/
├─ src/xdev_nodes/               # your node pack (Python package)
│  ├─ __init__.py                # registers nodes
│  └─ basic_nodes.py             # example nodes (AddConstant, BlendImages, LatentNoise)
├─ tests/                        # pytest tests
├─ scripts/                      # dev helper scripts
├─ .github/workflows/ci.yml      # lint & tests
├─ pyproject.toml                # ruff + pytest config
├─ requirements.txt              # optional runtime deps
├─ .gitignore
├─ LICENSE (MIT)
└─ README.md
```

## Develop
- Add new nodes in `src/xdev_nodes/*.py`, then expose them in `src/xdev_nodes/__init__.py`.
- Use the included tests as a template: `pytest -q`.
- Keep tensors on GPU, batch‑safe, and wrap math with `torch.no_grad()`.

## Install (manual copy)
Copy the `src/xdev_nodes/` folder into `ComfyUI/custom_nodes/Xtremedev-Nodes/`.

## License
MIT — see `LICENSE`.