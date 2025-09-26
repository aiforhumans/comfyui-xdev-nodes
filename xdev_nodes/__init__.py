"""
XDev Nodes - ComfyUI Development Toolkit
Professional node development patterns and utilities for ComfyUI workflows.
"""

# Add debug logging for loading process
import sys
def debug_print(message):
    """Print debug messages during loading"""
    print(f"[XDev Debug] {message}")
    sys.stdout.flush()

debug_print("Starting XDev Nodes initialization...")
debug_print("Loading performance utilities...")
try:
    from . import utils
    debug_print("✅ Performance utilities loaded")
except Exception as e:
    debug_print(f"⚠️ Performance utilities failed to load: {e}")

# Optimized imports grouped by functionality
debug_print("Loading basic nodes...")
from .nodes.basic import HelloString, AnyPassthrough
debug_print("✅ Basic nodes loaded")

debug_print("Loading image processing...")
from .nodes.image import PickByBrightness
debug_print("✅ Image processing loaded")

debug_print("Loading text processing...")
from .nodes.text import AppendSuffix, TextCase
debug_print("✅ Text processing loaded")

debug_print("Loading math operations...")
from .nodes.math import MathBasic
debug_print("✅ Math operations loaded")

debug_print("Loading development tools...")
from .nodes.dev_nodes import OutputDev, InputDev
debug_print("✅ Development tools loaded")

debug_print("Loading VAE tools...")
from .nodes.vae_tools import VAERoundTrip, VAEPreview
debug_print("✅ VAE tools loaded")

# If you add frontend assets, keep this path relative to this package root.
WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "XDEV_HelloString": HelloString,
    "XDEV_AnyPassthrough": AnyPassthrough,
    "XDEV_PickByBrightness": PickByBrightness,
    "XDEV_AppendSuffix": AppendSuffix,
    "XDEV_OutputDev": OutputDev,
    "XDEV_InputDev": InputDev,
    "XDEV_VAERoundTrip": VAERoundTrip,
    "XDEV_VAEPreview": VAEPreview,
    # Phase 1 Foundation Nodes
    "XDEV_TextCase": TextCase,
    "XDEV_MathBasic": MathBasic,
}

debug_print("Registering node mappings...")

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_HelloString": "Hello String (XDev)",
    "XDEV_AnyPassthrough": "Any Passthrough (XDev)",
    "XDEV_PickByBrightness": "Pick Image by Brightness (XDev)",
    "XDEV_AppendSuffix": "Append Suffix (XDev)",
    "XDEV_OutputDev": "Output Dev (XDev)",
    "XDEV_InputDev": "Input Dev (XDev)",
    "XDEV_VAERoundTrip": "VAE Round-Trip (XDev)",
    "XDEV_VAEPreview": "VAE Preview (XDev)",
    # Phase 1 Foundation Nodes
    "XDEV_TextCase": "Text Case Converter (XDev)",
    "XDEV_MathBasic": "Math Basic Operations (XDev)",
}

debug_print(f"✅ XDev Nodes initialization complete! Registered {len(NODE_CLASS_MAPPINGS)} nodes:")
for node_id, display_name in NODE_DISPLAY_NAME_MAPPINGS.items():
    debug_print(f"  • {node_id} → {display_name}")

# Add custom API routes for debugging
try:
    from aiohttp import web
    from server import PromptServer
    
    @PromptServer.instance.routes.get("/xdev/status")
    async def get_xdev_status(request):
        """Get XDev nodes status and performance info"""
        return web.json_response({
            "status": "active",
            "nodes_registered": len(NODE_CLASS_MAPPINGS),
            "nodes": list(NODE_DISPLAY_NAME_MAPPINGS.keys()),
            "version": "v0.2.0",
            "features": ["lazy_evaluation", "advanced_inputs", "performance_optimized"],
            "debug_enabled": True
        })
    
    @PromptServer.instance.routes.get("/xdev/nodes")
    async def get_xdev_nodes(request):
        """Get detailed information about all XDev nodes"""
        node_info = {}
        for node_id, node_class in NODE_CLASS_MAPPINGS.items():
            node_info[node_id] = {
                "display_name": NODE_DISPLAY_NAME_MAPPINGS[node_id],
                "category": getattr(node_class, 'CATEGORY', 'Unknown'),
                "description": getattr(node_class, 'DESCRIPTION', ''),
                "function": getattr(node_class, 'FUNCTION', ''),
                "return_types": getattr(node_class, 'RETURN_TYPES', ()),
                "output_node": getattr(node_class, 'OUTPUT_NODE', False)
            }
        return web.json_response(node_info)
    
    debug_print("✅ Custom API endpoints registered: /xdev/status, /xdev/nodes")
except Exception as e:
    debug_print(f"⚠️ Could not register API endpoints: {e}")

debug_print("XDev Nodes ready for ComfyUI! 🎉")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]