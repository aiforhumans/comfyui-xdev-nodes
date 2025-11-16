"""Test auto unload trigger functionality."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add LM Studio folder to path
lm_studio_path = project_root / "comfyui_custom_nodes" / "🖥XDEV" / "LM Studio"
sys.path.insert(0, str(lm_studio_path))

def test_auto_unload_trigger_import():
    """Test that auto unload trigger can be imported."""
    try:
        from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger
        print("✓ Auto unload trigger imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import auto unload trigger: {e}")
        return False

def test_auto_unload_trigger_structure():
    """Test auto unload trigger node structure."""
    try:
        from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger
        
        node = LMStudioAutoUnloadTrigger()
        input_types = node.INPUT_TYPES()
        
        assert "required" in input_types
        assert "trigger" in input_types["required"]
        assert "unload_method" in input_types["required"]
        
        # Check unload methods
        methods = input_types["required"]["unload_method"][0]
        assert "warning_only" in methods
        assert "lms_cli" in methods
        assert "force_error" in methods
        
        print("✓ Auto unload trigger structure is correct")
        print(f"  Unload methods: {methods}")
        return True
    except Exception as e:
        print(f"✗ Auto unload trigger structure test failed: {e}")
        return False

def test_auto_unload_trigger_disabled():
    """Test trigger when disabled."""
    try:
        from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger
        
        node = LMStudioAutoUnloadTrigger()
        status, unloaded, passthrough = node.trigger_unload(
            trigger=False,
            unload_method="warning_only"
        )
        
        assert "disabled" in status.lower()
        assert unloaded == False
        
        print("✓ Disabled trigger works correctly")
        print(f"  Status: {status}")
        return True
    except Exception as e:
        print(f"✗ Disabled trigger test failed: {e}")
        return False

def test_auto_unload_trigger_warning():
    """Test warning_only method."""
    try:
        from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger
        
        node = LMStudioAutoUnloadTrigger()
        # This will try to connect to LM Studio (will fail if not running)
        status, unloaded, passthrough = node.trigger_unload(
            trigger=True,
            unload_method="warning_only",
            server_url="http://localhost:9999",  # Invalid port
            passthrough="test_data"
        )
        
        assert isinstance(status, str)
        assert isinstance(unloaded, bool)
        assert passthrough == "test_data"
        
        print("✓ Warning method works correctly")
        print(f"  Unloaded: {unloaded}")
        return True
    except Exception as e:
        print(f"✗ Warning method test failed: {e}")
        return False

def test_auto_unload_trigger_passthrough():
    """Test passthrough functionality."""
    try:
        from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger
        
        node = LMStudioAutoUnloadTrigger()
        test_data = "prompt_output_data"
        
        status, unloaded, passthrough = node.trigger_unload(
            trigger=True,
            unload_method="warning_only",
            passthrough=test_data
        )
        
        assert passthrough == test_data
        
        print("✓ Passthrough works correctly")
        print(f"  Passthrough data preserved: {passthrough}")
        return True
    except Exception as e:
        print(f"✗ Passthrough test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Auto Unload Trigger Functionality\n")
    print("=" * 60)
    
    tests = [
        ("Auto Unload Trigger Import", test_auto_unload_trigger_import),
        ("Auto Unload Trigger Structure", test_auto_unload_trigger_structure),
        ("Disabled Trigger", test_auto_unload_trigger_disabled),
        ("Warning Method", test_auto_unload_trigger_warning),
        ("Passthrough Data", test_auto_unload_trigger_passthrough),
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
        print("✓ All auto unload trigger tests passed!")
    else:
        print("✗ Some tests failed")
        sys.exit(1)
