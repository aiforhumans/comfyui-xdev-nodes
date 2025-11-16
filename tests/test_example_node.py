"""Tests for example_node.py"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from comfyui_custom_nodes.example_node import ExampleNode


def test_example_node_add_positive():
    """Test basic addition with positive numbers."""
    node = ExampleNode()
    result = node.add(2.0, 3.0)
    assert result == (5.0,), f"Expected (5.0,), got {result}"
    assert isinstance(result, tuple), "Must return tuple, not list"


def test_example_node_add_negative():
    """Test addition with negative numbers."""
    node = ExampleNode()
    result = node.add(-5.0, 3.0)
    assert result == (-2.0,), f"Expected (-2.0,), got {result}"


def test_example_node_add_zero():
    """Test addition with zero."""
    node = ExampleNode()
    result = node.add(0.0, 0.0)
    assert result == (0.0,), f"Expected (0.0,), got {result}"


def test_example_node_add_decimals():
    """Test addition with decimal numbers."""
    node = ExampleNode()
    result = node.add(1.5, 2.3)
    assert abs(result[0] - 3.8) < 0.0001, f"Expected ~3.8, got {result[0]}"


def test_example_node_input_types():
    """Test INPUT_TYPES structure."""
    input_types = ExampleNode.INPUT_TYPES()
    assert "required" in input_types, "INPUT_TYPES must have 'required' key"
    assert "a" in input_types["required"], "INPUT_TYPES must define 'a' parameter"
    assert "b" in input_types["required"], "INPUT_TYPES must define 'b' parameter"
    
    # Check parameter types
    assert input_types["required"]["a"][0] == "FLOAT", "Parameter 'a' must be FLOAT type"
    assert input_types["required"]["b"][0] == "FLOAT", "Parameter 'b' must be FLOAT type"
    
    # Check defaults exist
    assert "default" in input_types["required"]["a"][1], "Parameter 'a' must have default"
    assert "default" in input_types["required"]["b"][1], "Parameter 'b' must have default"


def test_example_node_attributes():
    """Test that node has required ComfyUI attributes."""
    assert hasattr(ExampleNode, "RETURN_TYPES"), "Node must have RETURN_TYPES"
    assert hasattr(ExampleNode, "FUNCTION"), "Node must have FUNCTION"
    assert hasattr(ExampleNode, "CATEGORY"), "Node must have CATEGORY"
    
    assert ExampleNode.RETURN_TYPES == ("FLOAT",), "RETURN_TYPES must be ('FLOAT',)"
    assert ExampleNode.FUNCTION == "add", "FUNCTION must be 'add'"
    assert ExampleNode.CATEGORY == "Custom/Examples", "CATEGORY must be 'Custom/Examples'"


def test_example_node_return_type_is_tuple():
    """Critical test: ensure return type is tuple, not list."""
    node = ExampleNode()
    result = node.add(1.0, 1.0)
    assert type(result) is tuple, f"Return type must be tuple, got {type(result).__name__}"


def test_node_mappings_exist():
    """Test that NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS exist."""
    from comfyui_custom_nodes.example_node import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )
    
    assert "ExampleNode" in NODE_CLASS_MAPPINGS, "ExampleNode must be in NODE_CLASS_MAPPINGS"
    assert "ExampleNode" in NODE_DISPLAY_NAME_MAPPINGS, "ExampleNode must be in NODE_DISPLAY_NAME_MAPPINGS"
    assert NODE_CLASS_MAPPINGS["ExampleNode"] is ExampleNode, "Mapping must point to ExampleNode class"


if __name__ == "__main__":
    # Run tests without pytest
    print("Running smoke tests...")
    
    test_example_node_add_positive()
    print("✓ Positive addition test passed")
    
    test_example_node_add_negative()
    print("✓ Negative addition test passed")
    
    test_example_node_return_type_is_tuple()
    print("✓ Return type is tuple (CRITICAL)")
    
    test_example_node_input_types()
    print("✓ INPUT_TYPES structure valid")
    
    test_example_node_attributes()
    print("✓ Required attributes present")
    
    test_node_mappings_exist()
    print("✓ Node mappings registered")
    
    print("\n✅ All smoke tests passed!")
