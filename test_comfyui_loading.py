#!/usr/bin/env python3
"""
ComfyUI Loading Simulation Test

This script simulates exactly how ComfyUI loads custom node packages
to identify any environment-specific issues.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path

def simulate_comfyui_loading():
    """Simulate ComfyUI's exact loading process"""
    print("🔍 Simulating ComfyUI Custom Node Loading Process")
    print("=" * 60)
    
    # Get the current directory (should be the node package directory)
    current_dir = Path(__file__).parent.absolute()
    print(f"Node directory: {current_dir}")
    
    # Check if we're in the right place
    if not (current_dir / "xdev_nodes").exists():
        print("❌ Error: Not in the correct directory!")
        print("This script should be run from the comfyui-xdev-nodes directory")
        return False
    
    # Simulate ComfyUI's loading steps
    print("\n1. 📁 Checking for __init__.py...")
    init_file = current_dir / "__init__.py"
    if not init_file.exists():
        print(f"❌ Missing __init__.py at {init_file}")
        return False
    print(f"✅ Found __init__.py at {init_file}")
    
    print("\n2. 🐍 Simulating ComfyUI import process...")
    
    # Save original state
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    
    try:
        # ComfyUI changes to the node directory
        os.chdir(current_dir)
        print(f"Changed working directory to: {os.getcwd()}")
        
        # ComfyUI adds the directory to sys.path
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
            print(f"Added to sys.path: {current_dir}")
        
        # Try to import the module like ComfyUI does
        print("\n3. 📦 Attempting module import...")
        
        # Method 1: Direct __init__ import (how ComfyUI does it)
        try:
            # Clear any cached imports
            module_name = "__init__"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            import __init__ as node_module
            print("✅ Successfully imported via direct __init__ import")
            
            # Verify required attributes
            required_attrs = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
            for attr in required_attrs:
                if hasattr(node_module, attr):
                    value = getattr(node_module, attr)
                    print(f"✅ {attr}: {len(value) if hasattr(value, '__len__') else 'Available'}")
                else:
                    print(f"❌ Missing {attr}")
                    return False
            
            # Test each node class
            print("\n4. 🔧 Testing node classes...")
            mappings = node_module.NODE_CLASS_MAPPINGS
            
            for node_id, node_class in mappings.items():
                try:
                    # Test instantiation
                    instance = node_class()
                    
                    # Test INPUT_TYPES
                    input_types = instance.INPUT_TYPES()
                    
                    # Test that it has a callable function
                    func_name = getattr(node_class, 'FUNCTION', None)
                    if func_name and hasattr(instance, func_name):
                        method = getattr(instance, func_name)
                        if callable(method):
                            print(f"✅ {node_id}: All tests passed")
                        else:
                            print(f"❌ {node_id}: Method {func_name} not callable")
                            return False
                    else:
                        print(f"❌ {node_id}: Missing or invalid FUNCTION attribute")
                        return False
                        
                except Exception as e:
                    print(f"❌ {node_id}: Error during testing - {e}")
                    return False
            
            print("\n🎉 All ComfyUI loading simulation tests passed!")
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("This suggests a module dependency issue")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error during import: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    finally:
        # Restore original state
        os.chdir(original_cwd)
        sys.path[:] = original_path
        print(f"\nRestored working directory to: {os.getcwd()}")
    
def check_python_environment():
    """Check Python environment compatibility"""
    print("\n🐍 Python Environment Check")
    print("=" * 30)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Executable: {sys.executable}")
    
    # Check for potential issues
    issues = []
    
    # Check Python version
    version_info = sys.version_info
    if version_info < (3, 8):
        issues.append("Python version too old (< 3.8)")
    elif version_info >= (3, 12):
        print("⚠️  Note: Python 3.12+ may have compatibility issues with some ComfyUI setups")
    
    # Check for __future__ import support (test by trying to compile)
    try:
        compile("from __future__ import annotations", "<test>", "exec")
        print("✅ __future__ annotations supported")
    except SyntaxError:
        issues.append("__future__ annotations not supported")
    
    # Check typing support
    try:
        from typing import Dict, Tuple, Any, List
        print("✅ typing module working")
    except ImportError:
        issues.append("typing module issues")
    
    if issues:
        print("\n❌ Environment issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Python environment looks good")
        return True

def main():
    """Main function"""
    print("ComfyUI XDev Nodes - Loading Simulation Test")
    print("=" * 50)
    
    # Check environment first
    env_ok = check_python_environment()
    
    if not env_ok:
        print("\n🚫 Environment issues detected. Fix these first.")
        return
    
    # Run loading simulation
    loading_ok = simulate_comfyui_loading()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL DIAGNOSIS")
    print("=" * 60)
    
    if loading_ok:
        print("✅ SUCCESS: Nodes should load correctly in ComfyUI")
        print("\nIf you're still seeing import errors:")
        print("1. 🔄 Restart ComfyUI completely (close terminal/process)")
        print("2. 🔍 Check ComfyUI console for different error messages")
        print("3. 🐛 Enable ComfyUI debug logging if available")
        print("4. 📋 Check if there are any Windows-specific permission issues")
        print("5. 🔧 Try running ComfyUI as administrator (temporarily)")
        
        print("\nIf issues persist, the problem may be:")
        print("- ComfyUI version incompatibility")
        print("- Python environment differences between testing and ComfyUI")
        print("- File permission issues")
        print("- Antivirus software blocking imports")
    else:
        print("❌ FAILED: Issues found that prevent proper loading")
        print("\nRecommended actions:")
        print("1. Fix the specific errors shown above")
        print("2. Re-run this simulation test")
        print("3. Restart ComfyUI after fixes")

if __name__ == "__main__":
    main()