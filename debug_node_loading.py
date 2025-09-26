#!/usr/bin/env python3
"""
ComfyUI XDev Nodes Debug Script

This script performs comprehensive debugging of node loading issues by testing:
1. Import paths and module structure
2. Node class validation
3. ComfyUI compatibility checks
4. Runtime instantiation tests
"""

import os
import sys
import traceback
import importlib.util
from typing import Dict, Any, List, Tuple

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result with consistent formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

class NodeLoadDebugger:
    def __init__(self, node_path: str):
        self.node_path = os.path.abspath(node_path)
        self.root_path = self.node_path
        self.xdev_nodes_path = os.path.join(self.node_path, 'xdev_nodes')
        self.results = []
        
    def debug_all(self):
        """Run all debugging tests"""
        print_section("ComfyUI XDev Nodes - Debug Analysis")
        print(f"Node Path: {self.node_path}")
        print(f"XDev Nodes Path: {self.xdev_nodes_path}")
        
        # Test 1: File structure
        self.test_file_structure()
        
        # Test 2: Root __init__.py
        self.test_root_init()
        
        # Test 3: XDev nodes package
        self.test_xdev_package()
        
        # Test 4: Individual node modules
        self.test_individual_modules()
        
        # Test 5: Node class validation
        self.test_node_classes()
        
        # Test 6: ComfyUI compatibility
        self.test_comfyui_compatibility()
        
        # Test 7: Runtime instantiation
        self.test_runtime_instantiation()
        
        # Generate summary
        self.print_summary()
        
    def test_file_structure(self):
        """Test that all required files exist"""
        print_section("File Structure Analysis")
        
        required_files = [
            '__init__.py',
            'xdev_nodes/__init__.py',
            'xdev_nodes/nodes/__init__.py',
            'xdev_nodes/nodes/basic.py',
            'xdev_nodes/nodes/image.py',
            'xdev_nodes/nodes/text.py',
            'xdev_nodes/web/__init__.py'
        ]
        
        for file_path in required_files:
            full_path = os.path.join(self.node_path, file_path)
            exists = os.path.exists(full_path)
            print_result(f"File exists: {file_path}", exists)
            if not exists:
                self.results.append(f"MISSING FILE: {file_path}")
                
        # Check web directory structure
        web_files = [
            'xdev_nodes/web/js/xdev.js',
            'xdev_nodes/web/docs/XDEV_HelloString.md'
        ]
        
        for file_path in web_files:
            full_path = os.path.join(self.node_path, file_path)
            exists = os.path.exists(full_path)
            print_result(f"Web file exists: {file_path}", exists)
            
    def test_root_init(self):
        """Test root __init__.py import"""
        print_section("Root __init__.py Analysis")
        
        # Save current directory and change to node path
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.node_path)
            
            # Test import
            try:
                import __init__ as root_module
                print_result("Root __init__.py import", True)
                
                # Check required attributes
                has_mappings = hasattr(root_module, 'NODE_CLASS_MAPPINGS')
                has_display_names = hasattr(root_module, 'NODE_DISPLAY_NAME_MAPPINGS')
                has_web_dir = hasattr(root_module, 'WEB_DIRECTORY')
                
                print_result("Has NODE_CLASS_MAPPINGS", has_mappings)
                print_result("Has NODE_DISPLAY_NAME_MAPPINGS", has_display_names)
                print_result("Has WEB_DIRECTORY", has_web_dir)
                
                if has_mappings:
                    mappings = root_module.NODE_CLASS_MAPPINGS
                    print_result(f"Node count: {len(mappings)}", len(mappings) > 0)
                    for node_id in mappings:
                        print(f"    - {node_id}")
                        
            except Exception as e:
                print_result("Root __init__.py import", False, str(e))
                self.results.append(f"ROOT IMPORT ERROR: {e}")
                traceback.print_exc()
                
        finally:
            os.chdir(orig_cwd)
            
    def test_xdev_package(self):
        """Test xdev_nodes package import"""
        print_section("XDev Package Analysis")
        
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.node_path)
            
            try:
                import xdev_nodes
                print_result("xdev_nodes package import", True)
                
                # Check attributes
                has_mappings = hasattr(xdev_nodes, 'NODE_CLASS_MAPPINGS')
                has_display_names = hasattr(xdev_nodes, 'NODE_DISPLAY_NAME_MAPPINGS')
                has_web_dir = hasattr(xdev_nodes, 'WEB_DIRECTORY')
                
                print_result("Has NODE_CLASS_MAPPINGS", has_mappings)
                print_result("Has NODE_DISPLAY_NAME_MAPPINGS", has_display_names)
                print_result("Has WEB_DIRECTORY", has_web_dir)
                
            except Exception as e:
                print_result("xdev_nodes package import", False, str(e))
                self.results.append(f"XDEV PACKAGE ERROR: {e}")
                traceback.print_exc()
                
        finally:
            os.chdir(orig_cwd)
            
    def test_individual_modules(self):
        """Test individual node module imports"""
        print_section("Individual Module Analysis")
        
        modules = [
            ('basic', ['HelloString', 'AnyPassthrough']),
            ('image', ['PickByBrightness']),
            ('text', ['AppendSuffix'])
        ]
        
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.node_path)
            
            for module_name, expected_classes in modules:
                try:
                    module = __import__(f'xdev_nodes.nodes.{module_name}', fromlist=expected_classes)
                    print_result(f"Module {module_name} import", True)
                    
                    for class_name in expected_classes:
                        has_class = hasattr(module, class_name)
                        print_result(f"  Class {class_name}", has_class)
                        if not has_class:
                            self.results.append(f"MISSING CLASS: {module_name}.{class_name}")
                            
                except Exception as e:
                    print_result(f"Module {module_name} import", False, str(e))
                    self.results.append(f"MODULE ERROR: {module_name} - {e}")
                    
        finally:
            os.chdir(orig_cwd)
            
    def test_node_classes(self):
        """Test node class structure and methods"""
        print_section("Node Class Validation")
        
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.node_path)
            import xdev_nodes
            
            for node_id, node_class in xdev_nodes.NODE_CLASS_MAPPINGS.items():
                print(f"\nTesting {node_id}:")
                
                # Check required class methods/attributes
                has_input_types = hasattr(node_class, 'INPUT_TYPES')
                has_return_types = hasattr(node_class, 'RETURN_TYPES') 
                has_function = hasattr(node_class, 'FUNCTION')
                has_category = hasattr(node_class, 'CATEGORY')
                
                print_result(f"  Has INPUT_TYPES", has_input_types)
                print_result(f"  Has RETURN_TYPES", has_return_types)
                print_result(f"  Has FUNCTION", has_function)
                print_result(f"  Has CATEGORY", has_category)
                
                # Test INPUT_TYPES method
                if has_input_types:
                    try:
                        input_types = node_class.INPUT_TYPES()
                        print_result(f"  INPUT_TYPES callable", isinstance(input_types, dict))
                        if isinstance(input_types, dict):
                            print(f"    Required inputs: {list(input_types.get('required', {}).keys())}")
                            print(f"    Optional inputs: {list(input_types.get('optional', {}).keys())}")
                    except Exception as e:
                        print_result(f"  INPUT_TYPES callable", False, str(e))
                        
                # Check function method exists
                if has_function:
                    func_name = getattr(node_class, 'FUNCTION', '')
                    has_method = hasattr(node_class, func_name)
                    print_result(f"  Method {func_name} exists", has_method)
                    
        except Exception as e:
            print_result("Node class validation", False, str(e))
            self.results.append(f"CLASS VALIDATION ERROR: {e}")
            
        finally:
            os.chdir(orig_cwd)
            
    def test_comfyui_compatibility(self):
        """Test ComfyUI-specific compatibility requirements"""
        print_section("ComfyUI Compatibility Analysis")
        
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.node_path)
            import xdev_nodes
            
            # Check mapping consistency
            class_keys = set(xdev_nodes.NODE_CLASS_MAPPINGS.keys())
            display_keys = set(xdev_nodes.NODE_DISPLAY_NAME_MAPPINGS.keys())
            
            keys_match = class_keys == display_keys
            print_result("Mapping keys match", keys_match)
            
            if not keys_match:
                missing_display = class_keys - display_keys
                extra_display = display_keys - class_keys
                if missing_display:
                    print(f"    Missing display names: {missing_display}")
                if extra_display:
                    print(f"    Extra display names: {extra_display}")
                    
            # Check web directory
            web_dir = getattr(xdev_nodes, 'WEB_DIRECTORY', '')
            web_path = os.path.join(self.node_path, 'xdev_nodes', 'web')
            web_exists = os.path.exists(web_path)
            print_result("Web directory exists", web_exists, f"Path: {web_path}")
            
            # Check for __all__ export
            has_all = hasattr(xdev_nodes, '__all__')
            print_result("Has __all__ export", has_all)
            
        except Exception as e:
            print_result("ComfyUI compatibility check", False, str(e))
            self.results.append(f"COMPATIBILITY ERROR: {e}")
            
        finally:
            os.chdir(orig_cwd)
            
    def test_runtime_instantiation(self):
        """Test runtime instantiation of nodes"""
        print_section("Runtime Instantiation Tests")
        
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.node_path)
            import xdev_nodes
            
            for node_id, node_class in xdev_nodes.NODE_CLASS_MAPPINGS.items():
                print(f"\nTesting {node_id} instantiation:")
                
                try:
                    # Create instance
                    instance = node_class()
                    print_result(f"  Instantiation", True)
                    
                    # Test INPUT_TYPES
                    try:
                        input_types = instance.INPUT_TYPES()
                        print_result(f"  INPUT_TYPES call", True)
                    except Exception as e:
                        print_result(f"  INPUT_TYPES call", False, str(e))
                        
                    # Test function method if it exists
                    func_name = getattr(node_class, 'FUNCTION', '')
                    if func_name and hasattr(instance, func_name):
                        print_result(f"  Has method {func_name}", True)
                        
                        # Try to get method signature
                        import inspect
                        method = getattr(instance, func_name)
                        try:
                            sig = inspect.signature(method)
                            print(f"    Method signature: {sig}")
                        except Exception:
                            pass
                            
                except Exception as e:
                    print_result(f"  Instantiation", False, str(e))
                    self.results.append(f"INSTANTIATION ERROR: {node_id} - {e}")
                    
        except Exception as e:
            print_result("Runtime instantiation test", False, str(e))
            self.results.append(f"RUNTIME ERROR: {e}")
            
        finally:
            os.chdir(orig_cwd)
            
    def print_summary(self):
        """Print debugging summary"""
        print_section("Debug Summary")
        
        if not self.results:
            print("✅ All tests passed! No issues found.")
            print("\nThe XDev nodes should load correctly in ComfyUI.")
            print("If you're still experiencing issues, try:")
            print("  1. Restart ComfyUI completely")
            print("  2. Check ComfyUI console for different error messages")
            print("  3. Verify ComfyUI version compatibility")
        else:
            print("❌ Issues found:")
            for i, issue in enumerate(self.results, 1):
                print(f"  {i}. {issue}")
                
            print("\nRecommendations:")
            print("  - Fix the issues listed above")
            print("  - Re-run this debug script after fixes")
            print("  - Check ComfyUI console output for additional context")

def main():
    """Main debugging function"""
    # Get the path to the ComfyUI XDev nodes
    script_dir = os.path.dirname(os.path.abspath(__file__))
    node_path = script_dir  # Assuming this script is in the node directory
    
    if not os.path.exists(os.path.join(node_path, 'xdev_nodes')):
        print("❌ Error: xdev_nodes directory not found!")
        print(f"Looking in: {node_path}")
        print("Make sure this script is run from the comfyui-xdev-nodes directory")
        return
        
    debugger = NodeLoadDebugger(node_path)
    debugger.debug_all()

if __name__ == "__main__":
    main()