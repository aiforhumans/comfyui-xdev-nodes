"""
Type definitions for XDev node return values.
Provides structured, typed return values instead of plain tuples.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import torch

@dataclass(frozen=True)
class MathResult:
    """Result from mathematical operations"""
    result: float
    formula: str
    metadata: str
    
    def __iter__(self):
        """Allow tuple unpacking for backward compatibility"""
        return iter((self.result, self.formula, self.metadata))

@dataclass(frozen=True) 
class StringResult:
    """Result from string processing operations"""
    processed_text: str
    length: int
    metadata: str = ""
    
    def __iter__(self):
        """Allow tuple unpacking for backward compatibility"""
        return iter((self.processed_text, self.length, self.metadata))

@dataclass(frozen=True)
class ImageAnalysisResult:
    """Result from image analysis operations"""
    analysis_text: str
    statistics: Dict[str, Any]
    recommendations: List[str]
    
    def __iter__(self):
        """Allow tuple unpacking for backward compatibility"""
        return iter((self.analysis_text, self.statistics, self.recommendations))

@dataclass(frozen=True)
class VAERoundTripResult:
    """Result from VAE round-trip operations"""
    decoded_image: torch.Tensor
    reencoded_latent: Dict[str, torch.Tensor]
    process_info: str
    quality_metrics: Optional[Dict[str, float]] = None
    
    def __iter__(self):
        """Allow tuple unpacking for backward compatibility"""
        return iter((self.decoded_image, self.reencoded_latent, self.process_info))

@dataclass(frozen=True)
class ValidationResult:
    """Standardized validation result"""
    valid: bool
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            object.__setattr__(self, 'warnings', [])

@dataclass(frozen=True)
class PerformanceMetrics:
    """Performance measurement results"""
    execution_time: float
    memory_delta: int
    cache_hits: int
    cache_misses: int
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

# Type aliases for commonly used types
NodeInputTypes = Dict[str, Dict[str, Any]]
NodeReturnValue = Union[MathResult, StringResult, ImageAnalysisResult, VAERoundTripResult]