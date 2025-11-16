"""Test GPU memory management functionality."""

import sys


def test_model_manager_imports():
    """Test that model manager utilities can be imported."""
    from lm_model_manager import LMModelManager, check_model_loaded  # noqa: F401

    print("✓ Model manager utilities imported successfully")


def test_unload_helper_imports():
    """Test that unload helper node can be imported."""
    from lm_model_unload_helper import LMStudioModelUnloadHelper  # noqa: F401

    print("✓ Unload helper node imported successfully")


def test_model_check():
    """Test model checking functionality (no actual server needed)."""
    from lm_model_manager import check_model_loaded

    # This will fail to connect but shouldn't crash
    model_loaded, model_name, warning = check_model_loaded("http://localhost:9999")

    assert isinstance(model_loaded, bool)
    assert isinstance(model_name, (str, type(None)))
    assert isinstance(warning, (str, type(None)))

    print("✓ Model check function works without server")


def test_unload_helper_node():
    """Test unload helper node instantiation."""
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


def test_updated_nodes_import():
    """Test that updated LM Studio nodes still import correctly."""
    from lm_prompt_enhancer import LMStudioPromptEnhancer  # noqa: F401
    from lm_text_gen import LMStudioTextGen  # noqa: F401

    print("✓ Text and enhancer nodes import successfully")

    try:
        from lm_vision import LMStudioVision  # noqa: F401
        print("✓ Vision node imports successfully")
    except ImportError as e:  # pragma: no cover - environment specific
        if "numpy" in str(e) or "PIL" in str(e):
            print("⚠ Vision node requires numpy/PIL (expected warning)")
        else:
            raise

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

    passed = 0
    failed = 0
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            test_func()
            passed += 1
        except AssertionError as exc:
            failed += 1
            print(f"❌ Assertion failed: {exc}")
        except Exception as exc:  # pragma: no cover - manual execution helper
            failed += 1
            print(f"❌ Unexpected error: {exc}")

    print("\n" + "=" * 60)
    print(f"\nResults: {passed}/{len(tests)} tests passed")

    if failed:
        sys.exit(1)
    print("✓ All GPU memory management tests passed!")
