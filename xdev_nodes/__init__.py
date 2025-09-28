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

# Auto-registration system
from .registry import registry
from .categories import NodeCategories

# Discover and register all nodes
current_dir = Path(__file__).parent
nodes_dir = current_dir / "nodes"
registry.discover_nodes(nodes_dir)

# Export for ComfyUI
NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = registry.get_mappings()

# Web directory for JS extensions
WEB_DIRECTORY = "./web"

# Export symbols
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

debug_print(f"✅ XDev Nodes (Refactored) complete! {len(NODE_CLASS_MAPPINGS)} nodes registered")
