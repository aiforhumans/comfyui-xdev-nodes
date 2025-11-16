"""ASCII-friendly access to the 🖥XDEV ComfyUI nodes.

Exposes the same NODE_CLASS_MAPPINGS / NODE_DISPLAY_NAME_MAPPINGS
structure that ComfyUI expects while allowing tests and tooling to
import modules without dealing with emoji paths.
"""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Iterable
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "🖥XDEV"
PROMPT_TOOLS_PATH = BASE_DIR / "Prompt tools"
LM_STUDIO_PATH = BASE_DIR / "LM Studio"

NODE_CLASS_MAPPINGS: dict[str, type] = {}
NODE_DISPLAY_NAME_MAPPINGS: dict[str, str] = {}

# Keep track of direct symbol exports for IDE/Copilot friendliness
_EXPORTS: dict[str, type] = {}


def _load_category(alias: str, path: Path) -> tuple[dict[str, type], dict[str, str]]:
    """Load NODE_*_MAPPINGS from a category package."""
    init_file = path / "__init__.py"
    if not init_file.exists():
        return {}, {}

    spec = importlib.util.spec_from_file_location(
        f"comfyui_custom_nodes.xdev.{alias}",
        init_file,
        submodule_search_locations=[str(path)],
    )
    if spec is None or spec.loader is None:
        return {}, {}

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    class_map = getattr(module, "NODE_CLASS_MAPPINGS", {})
    display_map = getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {})

    for cls in class_map.values():
        _EXPORTS[cls.__name__] = cls

    return class_map, display_map


prompt_class_map, prompt_display_map = _load_category("prompt_tools", PROMPT_TOOLS_PATH)
lm_class_map, lm_display_map = _load_category("lm_studio", LM_STUDIO_PATH)

NODE_CLASS_MAPPINGS.update(prompt_class_map)
NODE_CLASS_MAPPINGS.update(lm_class_map)
NODE_DISPLAY_NAME_MAPPINGS.update(prompt_display_map)
NODE_DISPLAY_NAME_MAPPINGS.update(lm_display_map)

globals().update(_EXPORTS)

_export_names: Iterable[str] = _EXPORTS.keys()
__all__ = ("NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", *_export_names)
