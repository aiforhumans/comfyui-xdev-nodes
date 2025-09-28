"""
Performance optimization improvements for XDev nodes.
Micro-optimizations and enhanced caching strategies.
"""

from typing import Dict, Any, Optional, Tuple, Union
from functools import lru_cache
import operator
from ..performance import performance_monitor, cached_operation
from ..result_types import MathResult


class OptimizedMathBasic:
    """
    Performance-optimized version of MathBasic with enhanced caching and micro-optimizations.
    
    Optimizations implemented:
    1. Slot-based class to reduce memory overhead
    2. Pre-computed operation lookup with interned strings
    3. Enhanced caching with operation-specific strategies
    4. Micro-optimizations for hot paths
    5. Batch operation support for multiple calculations
    """
    
    __slots__ = ('_cache', '_stats')
    
    # Class-level constants for maximum performance
    _OPS = {
        'add': operator.add,
        'sub': operator.sub, 
        'mul': operator.mul,
        'div': operator.truediv,
        'mod': operator.mod,
        'pow': operator.pow,
        'fdiv': operator.floordiv
    }
    
    # Pre-computed symbols for formula generation
    _SYMBOLS = {
        'add': '+', 'sub': '-', 'mul': '*', 
        'div': '/', 'mod': '%', 'pow': '^', 'fdiv': '//'
    }
    
    # Cache sizes optimized for different operation patterns
    _CACHE_SIZES = {
        'add': 1000,    # Most common operations
        'sub': 1000,
        'mul': 500,     # Medium usage
        'div': 200,     # Less common but expensive
        'mod': 100,
        'pow': 50,      # Least common
        'fdiv': 100
    }
    
    def __init__(self):
        # Per-instance statistics for cache optimization
        self._stats = {'hits': 0, 'misses': 0, 'operations': {}}
        # Pre-allocate cache dictionaries
        self._cache = {op: {} for op in self._OPS}
    
    @performance_monitor("optimized_math_calculate")
    def calculate(self, a: float, b: float, operation: str, 
                 precision: int = 6) -> MathResult:
        """
        Optimized calculation with enhanced caching and micro-optimizations.
        """
        # Fast path validation - check common cases first
        if operation not in self._OPS:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Generate cache key - optimized for speed
        cache_key = (a, b, precision) if precision != 6 else (a, b)
        
        # Check cache first
        op_cache = self._cache[operation]
        if cache_key in op_cache:
            self._stats['hits'] += 1
            return op_cache[cache_key]
        
        # Cache miss - perform calculation
        self._stats['misses'] += 1
        
        # Handle division by zero early
        if b == 0.0 and operation in ('div', 'mod', 'fdiv'):
            raise ZeroDivisionError(f"Cannot {operation} by zero")
        
        # Perform operation using pre-computed function
        op_func = self._OPS[operation]
        raw_result = op_func(a, b)
        
        # Apply precision efficiently
        if precision == 0:
            result = float(int(raw_result))
        elif precision == 6:  # Default case
            result = raw_result  # Skip rounding for default precision
        else:
            result = round(raw_result, precision)
        
        # Generate formula string efficiently
        symbol = self._SYMBOLS[operation]
        formula = f"{a} {symbol} {b} = {result}"
        
        # Generate metadata
        self._stats['operations'][operation] = self._stats['operations'].get(operation, 0) + 1
        metadata = f"Operation: {operation}, Cache: {self._stats['hits']}/{self._stats['hits'] + self._stats['misses']}"
        
        # Create result object
        result_obj = MathResult(result, formula, metadata)
        
        # Cache result with size management
        max_size = self._CACHE_SIZES[operation]
        if len(op_cache) >= max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(op_cache))
            del op_cache[oldest_key]
        
        op_cache[cache_key] = result_obj
        return result_obj
    
    @lru_cache(maxsize=128)
    def _format_number(self, num: float, precision: int) -> str:
        """Cached number formatting for common values"""
        if precision == 0:
            return str(int(num))
        return f"{num:.{precision}f}"
    
    def batch_calculate(self, operations: list[Tuple[float, float, str]]) -> list[MathResult]:
        """
        Batch processing for multiple operations - more efficient than individual calls.
        
        Args:
            operations: List of (a, b, operation) tuples
            
        Returns:
            List of MathResult objects
        """
        results = []
        
        # Group operations by type for better cache locality
        grouped_ops = {}
        for i, (a, b, op) in enumerate(operations):
            if op not in grouped_ops:
                grouped_ops[op] = []
            grouped_ops[op].append((i, a, b))
        
        # Pre-allocate results list
        results = [None] * len(operations)
        
        # Process each operation type in batch
        for op_type, op_list in grouped_ops.items():
            for i, a, b in op_list:
                results[i] = self.calculate(a, b, op_type)
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get detailed cache statistics for optimization analysis"""
        total_ops = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_ops * 100) if total_ops > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_operations': total_ops,
            'cache_hits': self._stats['hits'],
            'cache_misses': self._stats['misses'],
            'operations_breakdown': self._stats['operations'].copy(),
            'cache_sizes': {op: len(cache) for op, cache in self._cache.items()}
        }
    
    def optimize_cache_sizes(self):
        """Dynamically adjust cache sizes based on usage patterns"""
        ops_count = self._stats['operations']
        if not ops_count:
            return
        
        total_ops = sum(ops_count.values())
        
        # Redistribute cache sizes based on actual usage
        for op, count in ops_count.items():
            usage_ratio = count / total_ops
            # Adjust cache size (minimum 50, maximum 2000)
            new_size = max(50, min(2000, int(1000 * usage_ratio * 2)))
            self._CACHE_SIZES[op] = new_size
            
            # Trim cache if it's now too large
            op_cache = self._cache[op]
            if len(op_cache) > new_size:
                # Keep most recent entries
                items = list(op_cache.items())[-new_size:]
                self._cache[op] = dict(items)


# Performance testing utilities
class PerformanceTester:
    """Utility class for benchmarking math operations"""
    
    @staticmethod
    def benchmark_operations(node_instance, num_operations: int = 10000):
        """Benchmark math operations performance"""
        import time
        import random
        
        operations = ['add', 'sub', 'mul', 'div']
        results = {}
        
        for op in operations:
            start_time = time.perf_counter()
            
            for _ in range(num_operations):
                a = random.uniform(-1000, 1000)
                b = random.uniform(0.1, 1000) if op == 'div' else random.uniform(-1000, 1000)
                try:
                    node_instance.calculate(a, b, op)
                except ZeroDivisionError:
                    continue  # Skip division by zero cases
            
            end_time = time.perf_counter()
            results[op] = {
                'total_time': end_time - start_time,
                'ops_per_second': num_operations / (end_time - start_time),
                'avg_time_per_op': (end_time - start_time) / num_operations
            }
        
        return results
    
    @staticmethod
    def compare_implementations(original_node, optimized_node, num_tests: int = 1000):
        """Compare performance between original and optimized implementations"""
        import time
        import random
        
        test_cases = []
        for _ in range(num_tests):
            a = random.uniform(-100, 100)
            b = random.uniform(-100, 100)
            op = random.choice(['add', 'sub', 'mul'])
            test_cases.append((a, b, op))
        
        # Test original implementation
        start = time.perf_counter()
        for a, b, op in test_cases:
            original_node.calculate(a, b, op)
        original_time = time.perf_counter() - start
        
        # Test optimized implementation  
        start = time.perf_counter()
        for a, b, op in test_cases:
            optimized_node.calculate(a, b, op)
        optimized_time = time.perf_counter() - start
        
        speedup = original_time / optimized_time if optimized_time > 0 else float('inf')
        
        return {
            'original_time': original_time,
            'optimized_time': optimized_time,
            'speedup_factor': speedup,
            'performance_improvement': f"{(speedup - 1) * 100:.1f}%"
        }