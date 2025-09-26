# Configuration and Testing Infrastructure

## Overview

This document covers the configuration system, path management, file validation, and testing infrastructure for the XDev Nodes toolkit.

## Configuration System

### Environment Configuration

```python
# config/settings.py
import os
from pathlib import Path

class XDevConfig:
    """Central configuration management for XDev nodes"""
    
    # Base paths
    COMFYUI_BASE = os.environ.get('COMFYUI_PATH', Path.cwd())
    XDEV_BASE = Path(__file__).parent.parent
    
    # Performance settings
    CACHE_SIZE = int(os.environ.get('XDEV_CACHE_SIZE', 1000))
    PERFORMANCE_MONITORING = os.environ.get('XDEV_PERF_MONITOR', 'True').lower() == 'true'
    
    # Validation settings
    STRICT_VALIDATION = os.environ.get('XDEV_STRICT_VALIDATION', 'True').lower() == 'true'
    MAX_IMAGE_SIZE = int(os.environ.get('XDEV_MAX_IMAGE_SIZE', 8192))
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('XDEV_LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('XDEV_LOG_FILE', None)
```

### Path Management

```python
# utils/paths.py
from pathlib import Path
import platform
from typing import Union, List

class PathManager:
    """Cross-platform path management for XDev nodes"""
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize path for current platform"""
        path = Path(path)
        if platform.system() == "Windows":
            # Handle Windows-specific path issues
            return path.resolve()
        return path.expanduser().resolve()
    
    @staticmethod
    def validate_path(path: Union[str, Path], must_exist: bool = True) -> bool:
        """Validate path existence and accessibility"""
        try:
            path = PathManager.normalize_path(path)
            if must_exist and not path.exists():
                return False
            if path.exists() and not os.access(path, os.R_OK):
                return False
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def safe_mkdir(path: Union[str, Path]) -> bool:
        """Safely create directory with proper error handling"""
        try:
            path = PathManager.normalize_path(path)
            path.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False
```

## File Type Validation

### Supported File Types

```python
# utils/file_types.py
from typing import Dict, List, Set
from pathlib import Path

class FileTypeValidator:
    """Validate file types for XDev nodes"""
    
    SUPPORTED_IMAGES = {
        '.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tga'
    }
    
    SUPPORTED_VIDEOS = {
        '.mp4', '.avi', '.mov', '.mkv', '.webm'
    }
    
    SUPPORTED_AUDIO = {
        '.wav', '.mp3', '.ogg', '.flac', '.m4a'
    }
    
    SUPPORTED_DATA = {
        '.json', '.yaml', '.yml', '.toml', '.txt', '.csv'
    }
    
    @classmethod
    def is_supported_image(cls, path: Union[str, Path]) -> bool:
        """Check if file is a supported image format"""
        return Path(path).suffix.lower() in cls.SUPPORTED_IMAGES
    
    @classmethod
    def get_file_category(cls, path: Union[str, Path]) -> str:
        """Get category of file based on extension"""
        suffix = Path(path).suffix.lower()
        
        if suffix in cls.SUPPORTED_IMAGES:
            return "image"
        elif suffix in cls.SUPPORTED_VIDEOS:
            return "video"
        elif suffix in cls.SUPPORTED_AUDIO:
            return "audio"
        elif suffix in cls.SUPPORTED_DATA:
            return "data"
        else:
            return "unknown"
    
    @classmethod
    def validate_file_for_node(cls, path: Union[str, Path], node_type: str) -> Dict[str, Any]:
        """Validate if file is suitable for specific node type"""
        path = Path(path)
        
        if not path.exists():
            return {"valid": False, "error": f"File does not exist: {path}"}
        
        category = cls.get_file_category(path)
        
        # Node-specific validation rules
        validation_rules = {
            "image": cls.SUPPORTED_IMAGES,
            "video": cls.SUPPORTED_VIDEOS,
            "audio": cls.SUPPORTED_AUDIO,
            "data": cls.SUPPORTED_DATA
        }
        
        if node_type in validation_rules:
            if path.suffix.lower() in validation_rules[node_type]:
                return {"valid": True, "category": category}
            else:
                return {"valid": False, "error": f"Unsupported file type for {node_type}: {path.suffix}"}
        
        return {"valid": True, "category": category}
```

## Testing Infrastructure

### Test Configuration

```python
# tests/conftest.py
import pytest
from pathlib import Path
import torch
import numpy as np

@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return {
        "cache_size": 100,
        "performance_monitoring": False,
        "strict_validation": True,
        "max_image_size": 1024
    }

@pytest.fixture
def sample_image():
    """Generate sample image tensor for testing"""
    # Create a 64x64 RGB image
    return torch.rand(1, 64, 64, 3)

@pytest.fixture
def sample_latent():
    """Generate sample latent tensor for testing"""
    # Create a typical latent representation
    return {
        "samples": torch.rand(1, 4, 8, 8)
    }

@pytest.fixture
def temp_directory(tmp_path):
    """Create temporary directory for file tests"""
    return tmp_path
```

### Performance Testing

```python
# tests/test_performance.py
import pytest
import time
from xdev_nodes.utils.performance import PerformanceMonitor

class TestPerformance:
    
    def test_performance_monitoring(self, test_config):
        """Test performance monitoring functionality"""
        monitor = PerformanceMonitor(enabled=True)
        
        with monitor.measure("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        stats = monitor.get_stats()
        assert "test_operation" in stats
        assert stats["test_operation"]["count"] == 1
        assert stats["test_operation"]["avg_time"] >= 0.1
    
    def test_caching_performance(self, sample_image):
        """Test caching system performance"""
        from xdev_nodes.utils.cache import cached_operation
        
        call_count = 0
        
        @cached_operation(cache_size=10)
        def expensive_operation(data):
            nonlocal call_count
            call_count += 1
            return data * 2
        
        # First call should execute
        result1 = expensive_operation(sample_image)
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_operation(sample_image)
        assert call_count == 1
        assert torch.equal(result1, result2)
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from xdev_nodes.nodes.image import (
    ImageResize, ImageCrop, ImageRotate, 
    ImageBlend, ImageSplit, ImageTile
)

class TestImageNodeIntegration:
    
    def test_resize_crop_pipeline(self, sample_image):
        """Test resize followed by crop"""
        # Resize image
        resizer = ImageResize()
        resized, _ = resizer.resize_image(
            sample_image, 128, 128, "lanczos"
        )
        
        # Crop resized image
        cropper = ImageCrop()
        cropped, _ = cropper.crop_image(
            resized, 64, 64, "center"
        )
        
        assert cropped.shape == (1, 64, 64, 3)
    
    def test_split_tile_roundtrip(self, sample_image):
        """Test splitting and tiling roundtrip"""
        # Split image into tiles
        splitter = ImageSplit()
        tiles, metadata = splitter.split_image(
            sample_image, 2, 2, "grid"
        )
        
        # Reconstruct from tiles
        tiler = ImageTile()
        reconstructed, _ = tiler.tile_image(
            tiles, 2, 2, 0  # No overlap for exact reconstruction
        )
        
        # Should be approximately equal (minor floating point differences)
        assert torch.allclose(sample_image, reconstructed, atol=1e-6)
```

### Error Handling Testing

```python
# tests/test_error_handling.py
import pytest
import torch
from xdev_nodes.nodes.image import ImageResize

class TestErrorHandling:
    
    def test_invalid_input_types(self):
        """Test handling of invalid input types"""
        resizer = ImageResize()
        
        # Test with invalid image type
        result, metadata = resizer.resize_image(
            "not an image", 64, 64, "lanczos"
        )
        
        assert "Error" in result or "Error" in metadata
    
    def test_invalid_dimensions(self, sample_image):
        """Test handling of invalid dimensions"""
        resizer = ImageResize()
        
        # Test with negative dimensions
        result, metadata = resizer.resize_image(
            sample_image, -64, 64, "lanczos"
        )
        
        assert "Error" in result or "Error" in metadata
    
    def test_memory_limits(self):
        """Test handling of memory-intensive operations"""
        resizer = ImageResize()
        
        # Create very large image
        large_image = torch.rand(1, 4096, 4096, 3)
        
        # Should handle gracefully
        result, metadata = resizer.resize_image(
            large_image, 8192, 8192, "lanczos"
        )
        
        # Should either succeed or fail gracefully
        assert result is not None
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Test XDev Nodes

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=xdev_nodes --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Local Testing Scripts

```powershell
# scripts/test-all.ps1
# Comprehensive local testing script

Write-Host "Running XDev Nodes Test Suite" -ForegroundColor Green

# Set environment variables for testing
$env:XDEV_PERF_MONITOR = "false"
$env:XDEV_STRICT_VALIDATION = "true"
$env:XDEV_LOG_LEVEL = "DEBUG"

# Run basic tests
Write-Host "Running basic tests..." -ForegroundColor Yellow
pytest tests/test_basic_nodes.py -v

# Run performance tests
Write-Host "Running performance tests..." -ForegroundColor Yellow
pytest tests/test_performance.py -v

# Run integration tests
Write-Host "Running integration tests..." -ForegroundColor Yellow
pytest tests/test_integration.py -v

# Run error handling tests
Write-Host "Running error handling tests..." -ForegroundColor Yellow
pytest tests/test_error_handling.py -v

# Generate coverage report
Write-Host "Generating coverage report..." -ForegroundColor Yellow
pytest tests/ --cov=xdev_nodes --cov-report=html

Write-Host "Test suite completed! Check htmlcov/index.html for coverage report." -ForegroundColor Green
```

## Logging and Monitoring

### Logging Configuration

```python
# utils/logging.py
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging for XDev nodes"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    logger = logging.getLogger('xdev_nodes')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

### Performance Monitoring

```python
# utils/monitoring.py
from functools import wraps
import time
import psutil
import torch
from typing import Dict, Any

class SystemMonitor:
    """Monitor system resources during node execution"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
    
    @staticmethod
    def get_gpu_memory() -> Dict[str, float]:
        """Get GPU memory usage if available"""
        if not torch.cuda.is_available():
            return {"allocated_mb": 0, "cached_mb": 0}
        
        return {
            "allocated_mb": torch.cuda.memory_allocated() / 1024 / 1024,
            "cached_mb": torch.cuda.memory_reserved() / 1024 / 1024
        }

def monitor_resources(func):
    """Decorator to monitor resource usage of functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = SystemMonitor()
        
        # Before execution
        start_memory = monitor.get_memory_usage()
        start_gpu = monitor.get_gpu_memory()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # After execution
            end_time = time.time()
            end_memory = monitor.get_memory_usage()
            end_gpu = monitor.get_gpu_memory()
            
            # Log resource usage
            logger = logging.getLogger('xdev_nodes.monitoring')
            logger.debug(f"{func.__name__} - Execution time: {end_time - start_time:.3f}s")
            logger.debug(f"{func.__name__} - Memory delta: {end_memory['rss_mb'] - start_memory['rss_mb']:.2f}MB")
            
            if torch.cuda.is_available():
                logger.debug(f"{func.__name__} - GPU memory delta: {end_gpu['allocated_mb'] - start_gpu['allocated_mb']:.2f}MB")
            
            return result
            
        except Exception as e:
            logger = logging.getLogger('xdev_nodes.monitoring')
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    
    return wrapper
```

## Best Practices

### Configuration Management
- Use environment variables for runtime configuration
- Provide sensible defaults for all settings
- Validate configuration values at startup
- Support both development and production configurations

### Path Handling
- Always use pathlib.Path for cross-platform compatibility
- Normalize paths before use
- Validate path existence and permissions
- Handle path-related errors gracefully

### Testing Strategy
- Write unit tests for individual node functions
- Create integration tests for node combinations
- Include performance benchmarks for critical operations
- Test error conditions and edge cases
- Maintain high test coverage (>80%)

### Monitoring and Logging
- Log important operations and errors
- Monitor resource usage for performance optimization
- Provide detailed error messages for debugging
- Use structured logging for better analysis

This infrastructure provides a solid foundation for reliable, maintainable, and well-tested ComfyUI extensions.