"""Test GPU memory management functionality."""

import sys

def test_model_manager_imports():
    """Test that model manager utilities can be imported."""
    try:
        from lm_model_manager import LMModelManager, check_model_loaded
        print("✓ Model manager utilities imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import model manager: {e}")
        return False

def test_unload_helper_imports():
    """Test that unload helper node can be imported."""
    try:
        from lm_model_unload_helper import LMStudioModelUnloadHelper
        print("✓ Unload helper node imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import unload helper: {e}")
        return False

def test_model_check():
    """Test model checking functionality (no actual server needed)."""
    try:
        from lm_model_manager import check_model_loaded
        
        # This will fail to connect but shouldn't crash
        model_loaded, model_name, warning = check_model_loaded("http://localhost:9999")
        
        print(f"✓ Model check function works")
        print(f"  Model loaded: {model_loaded}")
        print(f"  Model name: {model_name}")
        return True
    except Exception as e:
        print(f"✗ Model check failed: {e}")
        return False

def test_unload_helper_node():
    """Test unload helper node instantiation."""
    try:
        from lm_model_unload_helper import LMStudioModelUnloadHelper
        
        node = LMStudioModelUnloadHelper()
        input_types = node.INPUT_TYPES()
        
        assert "required" in input_types
        assert "check_before_generation" in input_types["required"]
        
        # Test with invalid server (should not crash)
        result = node.check_model(check_before_generation=True, server_url="http://localhost:9999")
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        print("✓ Unload helper node works correctly")
        print(f"  Status: {result[0][:50]}...")
        return True
    except Exception as e:
        print(f"✗ Unload helper node test failed: {e}")
        return False

def test_updated_nodes_import():
    """Test that updated LM Studio nodes still import correctly."""
    try:
        from lm_text_gen import LMStudioTextGen
        from lm_prompt_enhancer import LMStudioPromptEnhancer
        print("✓ Text and Enhancer nodes import successfully")
        
        try:
            from lm_vision import LMStudioVision
            print("✓ Vision node imports successfully")
        except ImportError as e:
            if "numpy" in str(e) or "PIL" in str(e):
                print("⚠ Vision node requires numpy/PIL (expected in ComfyUI environment)")
            else:
                raise
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import updated nodes: {e}")
        return False

if __name__ == "__main__":
    print("Testing GPU Memory Management Functionality\n")
    print("=" * 60)
    
    tests = [
        ("Model Manager Imports", test_model_manager_imports),
        ("Unload Helper Imports", test_unload_helper_imports),
        ("Model Check Function", test_model_check),
        ("Unload Helper Node", test_unload_helper_node),
        ("Updated Nodes Import", test_updated_nodes_import),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        results.append(test_func())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All GPU memory management tests passed!")
    else:
        print("✗ Some tests failed")
        sys.exit(1)
