"""
Prompt Module - Auto-import all prompt-related nodes
Contains 4 focused modules for prompt engineering and manipulation.
"""

# Auto-import all prompt modules when they're created
# This maintains backward compatibility while enabling modular organization

try:
    from .prompt_core import *
    from .prompt_builders import *
    from .prompt_advanced import *  
    from .prompt_llm import *
except ImportError:
    # During transition, some modules may not exist yet
    pass

__all__ = [
    # Will be populated as modules are split
]