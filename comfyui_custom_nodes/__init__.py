"""ComfyUI Custom Node Package.

The ASCII-friendly registry lives in :mod:`comfyui_custom_nodes.xdev`. This
module simply re-exports the mapping objects so ComfyUI discovers the nodes
normally when this folder is copied into ``custom_nodes``.
"""

from .xdev import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
