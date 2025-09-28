"""
XDev Nodes - ComfyUI Development Toolkit (Refactored)
Modern auto-registration system for 42 professional nodes.
"""

import sys
from pathlib import Path

def debug_print(message):
    """Print debug messages during loading"""
    print(f"[XDev Debug] {message}")
    sys.stdout.flush()

debug_print("Starting XDev Nodes (Refactored) initialization...")

# Setup model paths
try:
    import folder_paths
    import os
    
    insightface_models_dir = os.path.join(folder_paths.models_dir, "insightface")
    folder_paths.add_model_folder_path("insightface", insightface_models_dir)
    
    faceswap_models_dir = os.path.join(folder_paths.models_dir, "faceswap")
    folder_paths.add_model_folder_path("faceswap", faceswap_models_dir)
    
    debug_print(f"✅ Model paths registered")
except Exception as e:
    debug_print(f"⚠️ Model path setup failed: {e}")

# Ensure this package is available for imports
current_dir = Path(__file__).parent
package_name = "xdev_nodes"

# Register this package in sys.modules if it's not already there
if package_name not in sys.modules:
    import types
    xdev_module = types.ModuleType(package_name)
    xdev_module.__file__ = str(current_dir / "__init__.py")
    xdev_module.__path__ = [str(current_dir)]
    sys.modules[package_name] = xdev_module
    
    # Also register the nodes subpackage
    nodes_package = f"{package_name}.nodes"
    if nodes_package not in sys.modules:
        nodes_module = types.ModuleType(nodes_package)
        nodes_module.__file__ = str(current_dir / "nodes" / "__init__.py")
        nodes_module.__path__ = [str(current_dir / "nodes")]
        sys.modules[nodes_package] = nodes_module

# Auto-registration system
from .registry import registry
from .categories import NodeCategories

# Discover and register all nodes
nodes_dir = current_dir / "nodes"
registry.discover_nodes(nodes_dir)

# Export for ComfyUI
NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = registry.get_mappings()

# Web directory for JS extensions
WEB_DIRECTORY = "./web"

# Export symbols
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

debug_print(f"✅ XDev Nodes (Refactored) complete! {len(NODE_CLASS_MAPPINGS)} nodes registered")
