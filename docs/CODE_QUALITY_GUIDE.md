# XDev Nodes Code Quality & Performance Guide

## Overview
This document outlines the code quality standards, performance optimizations, and best practices implemented in XDev ComfyUI Nodes v0.6.0.

## Code Quality Standards

### Type Safety
- **Strict type hints**: All functions use comprehensive type annotations
- **Named return types**: Use dataclasses instead of plain tuples for clarity
- **Runtime type checking**: Validation mixins ensure type safety at runtime

```python
from xdev_nodes.result_types import MathResult

def calculate(a: float, b: float, operation: str) -> MathResult:
    """Type-safe calculation with structured return"""
    result = a + b
    return MathResult(
        result=result,
        formula=f"{a} + {b} = {result}",
        metadata="Addition operation completed"
    )
```

### Error Handling
- **Custom exceptions**: Structured error hierarchy with context
- **Graceful degradation**: Fallback behaviors for missing dependencies
- **Detailed error messages**: Include parameter names, values, and suggestions

```python
from xdev_nodes.exceptions import ValidationError, handle_node_errors

@handle_node_errors("MathBasic")
def process_input(value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise ValidationError(
            "Expected numeric value",
            parameter="input_value",
            value=value,
            node_name="MathBasic"
        )
    return float(value)
```

### Category Consistency
All nodes must use centralized category definitions:

```python
from xdev_nodes.categories import NodeCategories

class MyNode:
    CATEGORY = NodeCategories.MATH  # ✅ Correct
    # CATEGORY = "XDev/Math"        # ❌ Avoid hardcoded strings
```

## Performance Optimization

### Caching Strategy
- **Operation-specific caches**: Different cache sizes based on usage patterns
- **TTL-based expiration**: Automatic cache cleanup to prevent memory leaks
- **Hit rate monitoring**: Track cache effectiveness for optimization

```python
from xdev_nodes.performance import cached_operation, performance_monitor

@performance_monitor("expensive_operation")
@cached_operation(ttl=300)  # 5-minute cache
def expensive_calculation(data: Any) -> Any:
    # Expensive computation here
    return result
```

### Memory Optimization
- **Lazy imports**: Load heavy dependencies only when needed
- **String interning**: Reduce memory for repeated strings
- **Slot-based classes**: Minimize memory overhead for frequently instantiated classes

```python
from xdev_nodes.utils import get_torch, get_numpy

# Lazy loading - only imports when actually used
def process_tensor(data):
    torch = get_torch()  # Only loads torch if needed
    if torch:
        return torch.tensor(data)
    else:
        numpy = get_numpy()  # Fallback to numpy
        return numpy.array(data)
```

### Micro-optimizations
- **Pre-computed lookups**: Store operation mappings at class level
- **Batch processing**: Process multiple items efficiently
- **Early returns**: Fail fast for invalid inputs

```python
class OptimizedNode:
    # Pre-compute at class level for O(1) lookup
    _OPERATIONS = {
        "add": operator.add,
        "multiply": operator.mul,
        # ... other operations
    }
    
    def calculate(self, a, b, op):
        # Early validation
        if op not in self._OPERATIONS:
            raise ValueError(f"Invalid operation: {op}")
        
        # O(1) lookup instead of if/elif chain
        operation_func = self._OPERATIONS[op]
        return operation_func(a, b)
```

## Testing Standards

### Comprehensive Coverage
- **Unit tests**: Test individual node functionality
- **Integration tests**: Test node interactions with framework
- **Performance tests**: Verify optimization effectiveness
- **Edge case tests**: Handle boundary conditions and errors

### Test Organization
```python
class TestMathBasic:
    """Organized test structure"""
    
    # Basic functionality
    def test_basic_operations(self):
        pass
    
    # Edge cases
    def test_division_by_zero(self):
        pass
    
    # Performance
    def test_caching_effectiveness(self):
        pass
    
    # Integration
    def test_validation_integration(self):
        pass
```

### Parametrized Testing
Use pytest parameters for comprehensive coverage:

```python
@pytest.mark.parametrize("a,b,op,expected", [
    (1, 2, "add", 3),
    (5, 3, "subtract", 2),
    (4, 3, "multiply", 12),
])
def test_operations(a, b, op, expected):
    node = MathBasic()
    result = node.calculate(a, b, op)
    assert result.result == expected
```

## Performance Monitoring

### Built-in Metrics
All performance-critical operations include monitoring:

```python
# Automatic timing and memory tracking
@performance_monitor("image_processing")
def process_image(image):
    # Processing code here
    return processed_image
```

### Cache Analytics
Monitor cache effectiveness:

```python
# Get detailed cache statistics
stats = node.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1f}%")
print(f"Total operations: {stats['total_operations']}")
```

### Benchmarking Tools
Use built-in performance testing:

```python
from xdev_nodes.optimizations import PerformanceTester

# Benchmark node performance
results = PerformanceTester.benchmark_operations(math_node, 10000)
for op, metrics in results.items():
    print(f"{op}: {metrics['ops_per_second']:.0f} ops/sec")
```

## Dependency Management

### Lazy Loading Pattern
```python
# Heavy dependencies loaded only when needed
try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

def process_with_torch(data):
    if not HAS_TORCH:
        raise ImportError("PyTorch is required for this operation")
    return torch.tensor(data)
```

### Graceful Fallbacks
```python
def resize_image(image, size):
    # Try optimized path first
    if HAS_TORCH:
        return torch_resize(image, size)
    elif HAS_PILLOW:
        return pillow_resize(image, size)
    else:
        # Pure Python fallback
        return basic_resize(image, size)
```

## Code Organization Best Practices

### Module Structure
- **Functional grouping**: Related nodes in same file
- **Clear imports**: Explicit dependency management  
- **Consistent naming**: Follow XDEV_ prefix convention
- **Documentation**: Comprehensive docstrings and tooltips

### Category Organization
```
XDev/
├── Basic/           # Core utilities
├── Math/            # Mathematical operations
├── Text/            # Text processing
├── Image/           # Image operations
│   ├── Basic/       # Simple operations
│   ├── Manipulation/ # Complex transformations
│   └── Analysis/    # Analysis tools
├── Prompts/         # Prompt engineering
├── LLM/            # AI integration
├── Sampling/       # Advanced sampling
└── Development/    # Debug tools
```

## Migration Guide

### Updating Existing Nodes
1. **Add type hints**: Use proper type annotations
2. **Use NodeCategories**: Replace hardcoded category strings
3. **Implement proper exceptions**: Use XDev exception hierarchy
4. **Add performance monitoring**: Use decorators for critical operations
5. **Update tests**: Ensure comprehensive coverage

### Example Migration
```python
# Before
class OldNode:
    CATEGORY = "XDev/Math"  # Hardcoded string
    
    def calculate(self, a, b):  # No type hints
        return (a + b, "done")  # Tuple return

# After  
from xdev_nodes.categories import NodeCategories
from xdev_nodes.result_types import MathResult
from xdev_nodes.performance import performance_monitor

class NewNode:
    CATEGORY = NodeCategories.MATH  # Centralized constant
    
    @performance_monitor("addition")
    def calculate(self, a: float, b: float) -> MathResult:  # Type hints
        result = a + b
        return MathResult(  # Structured return
            result=result,
            formula=f"{a} + {b} = {result}",
            metadata="Addition completed successfully"
        )
```

## Future Improvements

### Planned Enhancements
- **AI-powered optimization**: Automatic cache size tuning
- **Advanced profiling**: Memory leak detection
- **Performance regression testing**: Automated performance monitoring in CI
- **Interactive documentation**: Live examples and tutorials
- **Community plugins**: Extension framework for custom nodes

### Contributing
See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines and code standards.