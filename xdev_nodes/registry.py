"""
XDev Node Registry - Auto-registration system for ComfyUI nodes
Automatically discovers and registers nodes from module files.
"""

import inspect
import importlib
from pathlib import Path
from typing import Dict, Any, Type
import sys

def debug_print(message):
    """Print debug messages during loading"""
    print(f"[XDev Registry] {message}")
    sys.stdout.flush()

class NodeRegistry:
    """Automatic node discovery and registration system"""
    
    def __init__(self):
        self.node_classes: Dict[str, Type] = {}
        self.display_names: Dict[str, str] = {}
        
    def discover_nodes(self, nodes_dir: Path) -> None:
        """Auto-discover all nodes from .py files in nodes directory and subdirectories"""
        debug_print(f"Discovering nodes from: {nodes_dir}")
        
        # First, scan direct .py files in the nodes directory (legacy support)
        for python_file in nodes_dir.glob("*.py"):
            if python_file.name.startswith("_"):  # Skip __init__.py and private files
                continue
                
            module_name = f"xdev_nodes.nodes.{python_file.stem}"
            try:
                debug_print(f"Loading module: {module_name}")
                module = importlib.import_module(module_name)
                self._extract_nodes_from_module(module, python_file.stem)
            except Exception as e:
                debug_print(f"⚠️ Failed to load {module_name}: {e}")
        
        # Then, recursively scan subdirectories (Phase 2 support)
        for subdir in nodes_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("_"):
                self._discover_nodes_in_subdirectory(subdir, f"xdev_nodes.nodes.{subdir.name}")
    
    def _discover_nodes_in_subdirectory(self, subdir: Path, module_prefix: str) -> None:
        """Recursively discover nodes in subdirectories"""
        debug_print(f"Scanning subdirectory: {subdir}")
        
        for python_file in subdir.glob("*.py"):
            if python_file.name.startswith("_"):  # Skip __init__.py and private files
                continue
                
            module_name = f"{module_prefix}.{python_file.stem}"
            try:
                debug_print(f"Loading module: {module_name}")
                module = importlib.import_module(module_name)
                self._extract_nodes_from_module(module, python_file.stem)
            except Exception as e:
                debug_print(f"⚠️ Failed to load {module_name}: {e}")
    
    def _extract_nodes_from_module(self, module: Any, module_name: str) -> None:
        """Extract node classes from a module using reflection"""
        nodes_found = 0
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip if not defined in this module
            if obj.__module__ != module.__name__:
                continue
                
            # Check if it's a ComfyUI node (has required attributes)
            if self._is_comfyui_node(obj):
                node_id = f"XDEV_{name}"
                display_name = getattr(obj, 'DISPLAY_NAME', f"{name} (XDev)")
                
                self.node_classes[node_id] = obj
                self.display_names[node_id] = display_name
                nodes_found += 1
                debug_print(f"  ✅ Registered: {node_id} → {display_name}")
        
        debug_print(f"Found {nodes_found} nodes in {module_name}")
    
    def _is_comfyui_node(self, cls: Type) -> bool:
        """Check if a class is a valid ComfyUI node"""
        required_attributes = ['INPUT_TYPES', 'RETURN_TYPES', 'FUNCTION', 'CATEGORY']
        
        # Must have INPUT_TYPES as classmethod
        if not hasattr(cls, 'INPUT_TYPES') or not isinstance(inspect.getattr_static(cls, 'INPUT_TYPES'), classmethod):
            return False
            
        # Must have other required attributes
        for attr in ['RETURN_TYPES', 'FUNCTION', 'CATEGORY']:
            if not hasattr(cls, attr):
                return False
                
        # Must have the main function defined
        function_name = getattr(cls, 'FUNCTION', None)
        if function_name and not hasattr(cls, function_name):
            return False
            
        return True
    
    def get_mappings(self) -> tuple[Dict[str, Type], Dict[str, str]]:
        """Get the class and display name mappings for ComfyUI"""
        return self.node_classes.copy(), self.display_names.copy()

# Global registry instance
registry = NodeRegistry()