"""
ComfyUI XDev Nodes - Custom Node Package

This package provides a starter kit for ComfyUI custom nodes with examples
demonstrating best practices for node development.
"""

import os
import sys

# Add the current directory to the Python path so we can import xdev_nodes
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the node mappings from the xdev_nodes subpackage
try:
    from xdev_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, WEB_DIRECTORY
except ImportError:
    # Fallback: try importing with explicit path manipulation
    import importlib.util
    xdev_nodes_path = os.path.join(current_dir, 'xdev_nodes', '__init__.py')
    spec = importlib.util.spec_from_file_location("xdev_nodes", xdev_nodes_path)
    xdev_nodes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xdev_nodes)
    
    NODE_CLASS_MAPPINGS = xdev_nodes.NODE_CLASS_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS = xdev_nodes.NODE_DISPLAY_NAME_MAPPINGS
    WEB_DIRECTORY = xdev_nodes.WEB_DIRECTORY

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]