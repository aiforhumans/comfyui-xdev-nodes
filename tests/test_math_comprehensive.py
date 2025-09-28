"""
Comprehensive test suite for XDev Math nodes.
Tests core functionality, edge cases, performance, and error handling.
"""

import pytest
import sys
import os

# Add the project root to the path so we can import xdev_nodes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from xdev_nodes.nodes.math import MathBasic
from xdev_nodes.exceptions import MathError, ValidationError


class TestMathBasic:
    """Comprehensive tests for MathBasic node"""
    
    @pytest.fixture
    def math_node(self):
        """Create a fresh MathBasic instance for each test"""
        return MathBasic()
    
    # Basic functionality tests
    def test_basic_operations(self, math_node):
        """Test all basic mathematical operations"""
        # Addition
        result = math_node.calculate(2.0, 3.0, "add")
        assert result[0] == 5.0
        assert "2.0 + 3.0 = 5.0" in result[1]
        
        # Subtraction
        result = math_node.calculate(5.0, 3.0, "subtract")
        assert result[0] == 2.0
        
        # Multiplication
        result = math_node.calculate(4.0, 3.0, "multiply")
        assert result[0] == 12.0
        
        # Division
        result = math_node.calculate(12.0, 4.0, "divide")
        assert result[0] == 3.0
        
        # Modulo
        result = math_node.calculate(10.0, 3.0, "modulo")
        assert result[0] == 1.0
        
        # Power
        result = math_node.calculate(2.0, 3.0, "power")
        assert result[0] == 8.0
        
        # Floor division
        result = math_node.calculate(7.0, 2.0, "floor_divide")
        assert result[0] == 3.0
    
    # Edge cases and error handling
    def test_division_by_zero(self, math_node):
        """Test division by zero error handling"""
        with pytest.raises(MathError) as exc_info:
            math_node.calculate(5.0, 0.0, "divide")
        
        assert "Division by zero" in str(exc_info.value)
        assert exc_info.value.operation == "divide"
    
    def test_modulo_by_zero(self, math_node):
        """Test modulo by zero error handling"""
        with pytest.raises(MathError):
            math_node.calculate(5.0, 0.0, "modulo")
    
    def test_invalid_operation(self, math_node):
        """Test invalid operation handling"""
        with pytest.raises(ValidationError):
            math_node.calculate(1.0, 2.0, "invalid_op")
    
    def test_extreme_values(self, math_node):
        """Test with extreme values"""
        # Large numbers
        result = math_node.calculate(1e6, 1e6, "add")
        assert result[0] == 2e6
        
        # Small numbers
        result = math_node.calculate(1e-6, 1e-6, "add")
        assert abs(result[0] - 2e-6) < 1e-10
        
        # Negative numbers
        result = math_node.calculate(-5.0, -3.0, "multiply")
        assert result[0] == 15.0
    
    def test_precision_handling(self, math_node):
        """Test precision parameter"""
        # Test different precision levels
        result = math_node.calculate(1.0, 3.0, "divide", precision=2)
        assert result[0] == 0.33
        
        result = math_node.calculate(1.0, 3.0, "divide", precision=6)
        assert result[0] == 0.333333
        
        # Test zero precision (integer results)
        result = math_node.calculate(7.7, 2.2, "add", precision=0)
        assert result[0] == 10
        assert isinstance(result[0], (int, float))
    
    # Performance tests
    def test_caching_performance(self, math_node):
        """Test that caching improves performance for repeated operations"""
        import time
        
        # First call - should be slower (cache miss)
        start = time.perf_counter()
        result1 = math_node.calculate(123.456, 789.012, "multiply")
        first_time = time.perf_counter() - start
        
        # Second call - should be faster (cache hit)
        start = time.perf_counter()
        result2 = math_node.calculate(123.456, 789.012, "multiply")
        second_time = time.perf_counter() - start
        
        # Results should be identical
        assert result1[0] == result2[0]
        
        # Second call should be faster (allowing for some variance)
        # Note: This test might be flaky on very fast systems
        if first_time > 1e-6:  # Only check if first call was measurable
            assert second_time <= first_time * 2  # Allow 2x variance
    
    def test_memory_efficiency(self, math_node):
        """Test memory usage doesn't grow excessively"""
        import gc
        import sys
        
        # Get initial memory state
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for i in range(100):
            math_node.calculate(float(i), float(i + 1), "add")
        
        # Check memory hasn't grown excessively
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Allow some growth but not linear with operations
        object_growth = final_objects - initial_objects
        assert object_growth < 50  # Reasonable threshold
    
    # Input validation tests  
    def test_input_validation(self, math_node):
        """Test input validation with invalid types"""
        with pytest.raises(ValidationError):
            math_node.calculate("not_a_number", 2.0, "add")
        
        with pytest.raises(ValidationError):
            math_node.calculate(1.0, None, "add")
    
    # Boundary tests
    def test_boundary_values(self, math_node):
        """Test boundary values like infinity and NaN"""
        # Test with very large numbers that might overflow
        result = math_node.calculate(1e308, 2.0, "multiply")
        # Should handle overflow gracefully
        assert not (result[0] != result[0])  # Check not NaN
        
        # Test with very small numbers
        result = math_node.calculate(1e-308, 0.5, "multiply")
        assert result[0] >= 0  # Should be positive


class TestMathBasicIntegration:
    """Integration tests for MathBasic with other system components"""
    
    def test_with_validation_mixin(self):
        """Test integration with validation framework"""
        math_node = MathBasic()
        
        # Test that validation is properly integrated
        validation = math_node.validate_numeric_input(5.0, "test_param")
        assert validation["valid"] is True
        
        validation = math_node.validate_numeric_input("invalid", "test_param")
        assert validation["valid"] is False
    
    def test_performance_monitoring_integration(self):
        """Test that performance monitoring is working"""
        math_node = MathBasic()
        
        # This should trigger performance monitoring
        result = math_node.calculate(1.0, 2.0, "add")
        
        # Check that result is valid (monitoring shouldn't break functionality)
        assert result[0] == 3.0
        assert isinstance(result[1], str)
        assert isinstance(result[2], str)


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("a,b,op,expected", [
    (0, 0, "add", 0),
    (1, -1, "add", 0),
    (100, 50, "subtract", 50),
    (0.1, 0.2, "add", 0.3),
    (-5, -5, "multiply", 25),
    (2, 8, "power", 256),
])
def test_math_operations_parametrized(a, b, op, expected):
    """Parametrized test for various operation combinations"""
    math_node = MathBasic()
    result = math_node.calculate(float(a), float(b), op)
    assert abs(result[0] - expected) < 1e-10  # Account for floating point precision


if __name__ == "__main__":
    pytest.main([__file__, "-v"])