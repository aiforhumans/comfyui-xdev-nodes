"""
Custom exceptions for XDev nodes.
Provides structured error handling with consistent messaging.
"""

from typing import Any, Optional


class XDevError(Exception):
    """Base exception for all XDev node errors"""
    
    def __init__(self, message: str, node_name: str = "", parameter: str = ""):
        self.message = message
        self.node_name = node_name
        self.parameter = parameter
        super().__init__(self.formatted_message)
    
    @property
    def formatted_message(self) -> str:
        """Format error message with context"""
        parts = []
        if self.node_name:
            parts.append(f"[{self.node_name}]")
        if self.parameter:
            parts.append(f"Parameter '{self.parameter}':")
        parts.append(self.message)
        return " ".join(parts)


class ValidationError(XDevError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, parameter: str, value: Any = None, node_name: str = ""):
        self.value = value
        if value is not None:
            message = f"{message} (got: {type(value).__name__} = {repr(value)})"
        super().__init__(message, node_name, parameter)


class MathError(XDevError):
    """Raised for mathematical operation errors"""
    
    def __init__(self, operation: str, message: str, a: float = None, b: float = None):
        self.operation = operation
        self.a = a
        self.b = b
        if a is not None and b is not None:
            message = f"Cannot {operation} {a} and {b}: {message}"
        super().__init__(message, "MathBasic", operation)


class ImageProcessingError(XDevError):
    """Raised for image processing errors"""
    
    def __init__(self, message: str, image_shape: Optional[tuple] = None, node_name: str = ""):
        if image_shape:
            message = f"{message} (image shape: {image_shape})"
        super().__init__(message, node_name)


class FaceSwapError(XDevError):
    """Raised for face processing errors"""
    
    def __init__(self, message: str, num_faces_found: int = 0, node_name: str = ""):
        if num_faces_found >= 0:
            message = f"{message} (found {num_faces_found} faces)"
        super().__init__(message, node_name)


class ModelLoadError(XDevError):
    """Raised when model loading fails"""
    
    def __init__(self, model_type: str, message: str, path: str = ""):
        if path:
            message = f"Failed to load {model_type} from '{path}': {message}"
        else:
            message = f"Failed to load {model_type}: {message}"
        super().__init__(message, "ModelLoader")


class CacheError(XDevError):
    """Raised for caching-related errors"""
    pass


class PerformanceError(XDevError):
    """Raised for performance monitoring errors"""
    pass


# Error handler decorator
def handle_node_errors(node_name: str = ""):
    """Decorator to handle node exceptions gracefully"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except XDevError:
                raise  # Re-raise XDev errors as-is
            except ZeroDivisionError as e:
                raise MathError("divide", "Division by zero") from e
            except ValueError as e:
                raise ValidationError(str(e), "input", node_name=node_name) from e
            except TypeError as e:
                raise ValidationError(str(e), "input", node_name=node_name) from e
            except Exception as e:
                raise XDevError(f"Unexpected error: {str(e)}", node_name) from e
        return wrapper
    return decorator