"""
Advanced performance utilities for XDev nodes.
Provides memory profiling, execution timing, caching strategies, and performance monitoring.
"""

from typing import Any, Dict, Optional, Union, Callable, TypeVar, Generic
import sys
import time
import gc
from functools import lru_cache, wraps
from contextlib import contextmanager
from collections import defaultdict
import threading

# Type definitions for performance utilities
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Global performance tracking
_performance_stats = defaultdict(list)
_memory_stats = defaultdict(list)
_cache_stats = defaultdict(int)

class PerformanceProfiler:
    """Advanced performance profiler for node operations"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.start_memory = None
        
    def __enter__(self):
        gc.collect()  # Clean garbage before measurement
        self.start_memory = self._get_memory_usage()
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        gc.collect()
        end_memory = self._get_memory_usage()
        
        execution_time = end_time - self.start_time
        memory_delta = end_memory - self.start_memory
        
        # Store performance statistics
        _performance_stats[self.name].append({
            'execution_time': execution_time,
            'memory_delta': memory_delta,
            'timestamp': time.time()
        })
        
    @staticmethod
    def _get_memory_usage() -> int:
        """Get current memory usage in bytes"""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except ImportError:
            # Fallback to basic measurement
            return sys.getsizeof(gc.get_objects())

class AdvancedCache:
    """Thread-safe advanced caching with size limits and TTL"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._timestamps = {}
        self._access_order = []
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
                
            # Check TTL
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                self._remove_key(key)
                return None
                
            # Update access order for LRU
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            _cache_stats['hits'] += 1
            return self._cache[key]
            
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            # Evict if at capacity
            while len(self._cache) >= self.max_size and self._access_order:
                oldest_key = self._access_order.pop(0)
                self._remove_key(oldest_key)
                
            self._cache[key] = value
            self._timestamps[key] = time.time()
            if key not in self._access_order:
                self._access_order.append(key)
                
            _cache_stats['sets'] += 1
            
    def _remove_key(self, key: str) -> None:
        """Remove key from all internal structures"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)

# Global advanced cache instance
_advanced_cache = AdvancedCache(max_size=500, ttl_seconds=600)

def performance_monitor(func_name: Optional[str] = None):
    """Decorator for automatic performance monitoring"""
    def decorator(func: F) -> F:
        monitor_name = func_name or f"{func.__module__}.{func.__qualname__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceProfiler(monitor_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def cached_operation(cache_key_func: Optional[Callable] = None, ttl: int = 300):
    """Advanced caching decorator with custom key generation"""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
            # Try to get from cache
            cached_result = _advanced_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Execute and cache result
            result = func(*args, **kwargs)
            _advanced_cache.set(cache_key, result)
            return result
        return wrapper
    return decorator

# String interning for memory optimization
_interned_strings = {}

def intern_string(s: str) -> str:
    """Intern strings for memory optimization"""
    if s not in _interned_strings:
        _interned_strings[s] = sys.intern(s)  # Use Python's built-in string interning
    return _interned_strings[s]

# Pre-compiled patterns for maximum performance
class PrecompiledPatterns:
    """Container for pre-compiled patterns and constants"""
    
    # ComfyUI type validation
    COMFYUI_TYPES = frozenset([
        "STRING", "INT", "FLOAT", "BOOLEAN", "IMAGE", "LATENT", 
        "VAE", "MODEL", "CONDITIONING", "CLIP", "MASK", "SAMPLER"
    ])
    
    # Common validation sets
    VALIDATION_PATTERNS = {
        "brightness_modes": frozenset(["brightest", "darkest"]),
        "analysis_levels": frozenset(["basic", "detailed", "full"]),
        "format_styles": frozenset(["simple", "formal", "casual", "technical"]),
        "case_types": frozenset([
            "lower", "upper", "title", "capitalize", 
            "camel", "pascal", "snake", "kebab", "constant"
        ]),
        "math_operations": frozenset([
            "add", "subtract", "multiply", "divide", 
            "modulo", "power", "floor_divide"
        ])
    }
    
    @classmethod
    @lru_cache(maxsize=128)
    def validate_pattern(cls, value: str, pattern_name: str) -> bool:
        """Cached pattern validation"""
        return value in cls.VALIDATION_PATTERNS.get(pattern_name, frozenset())

# Memory-efficient data structures
class CompactDict(dict):
    """Memory-optimized dictionary for small datasets"""
    __slots__ = ()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Intern string keys for memory efficiency
        for key in list(self.keys()):
            if isinstance(key, str):
                interned_key = intern_string(key)
                if interned_key != key:
                    self[interned_key] = self.pop(key)

# Utility functions for performance optimization
@lru_cache(maxsize=256)
def fast_type_check(obj_type: str, expected_types: tuple) -> bool:
    """Ultra-fast type checking with caching"""
    return obj_type in expected_types

@cached_operation(ttl=3600)  # Cache for 1 hour
def analyze_object_structure(obj: Any) -> Dict[str, Any]:
    """Cached object structure analysis"""
    obj_type = type(obj).__name__
    
    structure = CompactDict({
        "type": intern_string(obj_type),
        "module": intern_string(obj.__class__.__module__)
    })
    
    # Add type-specific information
    if hasattr(obj, 'shape'):
        structure["shape"] = str(obj.shape)
    elif hasattr(obj, '__len__'):
        try:
            structure["length"] = len(obj)
        except (TypeError, AttributeError):
            pass
            
    if hasattr(obj, 'device'):
        structure["device"] = intern_string(str(obj.device))
        
    if hasattr(obj, 'dtype'):
        structure["dtype"] = intern_string(str(obj.dtype))
        
    return structure

def get_performance_stats(node_name: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics for monitoring"""
    if node_name:
        return {
            "executions": len(_performance_stats.get(node_name, [])),
            "avg_time": sum(s['execution_time'] for s in _performance_stats.get(node_name, [])) / max(1, len(_performance_stats.get(node_name, []))),
            "total_memory_delta": sum(s['memory_delta'] for s in _performance_stats.get(node_name, []))
        }
    
    return {
        "total_cache_hits": _cache_stats['hits'],
        "total_cache_sets": _cache_stats['sets'],
        "cache_hit_rate": _cache_stats['hits'] / max(1, _cache_stats['hits'] + _cache_stats['sets']),
        "monitored_functions": list(_performance_stats.keys())
    }

def clear_performance_cache():
    """Clear all performance caches and statistics"""
    global _performance_stats, _memory_stats, _cache_stats
    _performance_stats.clear()
    _memory_stats.clear() 
    _cache_stats.clear()
    _advanced_cache._cache.clear()
    _advanced_cache._timestamps.clear()
    _advanced_cache._access_order.clear()