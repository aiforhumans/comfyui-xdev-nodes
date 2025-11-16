"""Test auto unload trigger functionality."""

import sys


def test_auto_unload_trigger_import():
    """Test that auto unload trigger can be imported."""
    from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger  # noqa: F401

    print("✓ Auto unload trigger imported successfully")


def test_auto_unload_trigger_structure():
    """Test auto unload trigger node structure."""
    from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger

    node = LMStudioAutoUnloadTrigger()
    input_types = node.INPUT_TYPES()

    assert "required" in input_types
    assert "trigger" in input_types["required"]
    assert "unload_method" in input_types["required"]

    # Check unload methods
    methods = input_types["required"]["unload_method"][0]
    assert set(methods) == {"warning_only", "lms_cli", "force_error"}

    tooltip = input_types["required"]["unload_method"][1].get("tooltip")
    assert "workflow" in tooltip.lower()

    print("✓ Auto unload trigger structure is correct")


def test_auto_unload_trigger_disabled():
    """Test trigger when disabled."""
    from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger

    node = LMStudioAutoUnloadTrigger()
    status, unloaded, passthrough = node.trigger_unload(
        trigger=False,
        unload_method="warning_only"
    )

    assert "disabled" in status.lower()
    assert unloaded is False
    assert passthrough == ""

    print("✓ Disabled trigger works correctly")


def test_auto_unload_trigger_warning():
    """Test warning_only method."""
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


def test_auto_unload_trigger_passthrough():
    """Test passthrough functionality."""
    from lm_auto_unload_trigger import LMStudioAutoUnloadTrigger

    node = LMStudioAutoUnloadTrigger()
    test_data = "prompt_output_data"

    _, _, passthrough = node.trigger_unload(
        trigger=True,
        unload_method="warning_only",
        passthrough=test_data
    )

    assert passthrough == test_data

    print("✓ Passthrough works correctly")

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
        except Exception as exc:  # pragma: no cover - manual usage helper
            failed += 1
            print(f"❌ Unexpected error: {exc}")
    
    print("\n" + "=" * 60)
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if failed:
        sys.exit(1)
    print("✓ All auto unload trigger tests passed!")
