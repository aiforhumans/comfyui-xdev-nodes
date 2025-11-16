"""Test configuration and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "comfyui_custom_nodes"
PROMPT_TOOLS = PACKAGE_ROOT / "🖥XDEV" / "Prompt tools"
LM_STUDIO = PACKAGE_ROOT / "🖥XDEV" / "LM Studio"

for path in (ROOT, PACKAGE_ROOT, PROMPT_TOOLS, LM_STUDIO):
    resolved = str(path)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)

__all__ = ["ROOT", "PACKAGE_ROOT", "PROMPT_TOOLS", "LM_STUDIO"]