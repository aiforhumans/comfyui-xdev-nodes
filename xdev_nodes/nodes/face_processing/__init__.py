"""
Face Processing Module - Auto-import all face processing nodes
Contains core face swap functionality, batch processing, and analysis tools.
"""

try:
    from .face_swap_core import *
    from .face_swap_batch import *
    from .face_swap_analysis import *
except ImportError:
    # During transition, some modules may not exist yet
    pass

__all__ = [
    # Will be populated as modules are split
]