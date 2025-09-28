"""
XDev Base Classes - Common patterns for node development
Extracted common functionality to reduce code duplication.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, List
from ..performance import performance_monitor, cached_operation
from ..mixins import ValidationMixin

class TextProcessingNode(ValidationMixin):
    """Base class for text processing nodes"""
    
    @performance_monitor("text_processing")
    def process_text(self, text: str, **kwargs) -> str:
        """Common text processing workflow"""
        if not text:
            return ""
        
        # Validation
        if hasattr(self, 'validate_input') and kwargs.get('validate_input', True):
            validation = self.validate_text_input(text)
            if not validation.get('valid', False):
                return f"Error: {validation.get('error', 'Unknown validation error')}"
        
        return self._process_text_impl(text, **kwargs)
    
    @abstractmethod
    def _process_text_impl(self, text: str, **kwargs) -> str:
        """Implement specific text processing logic"""
        pass

class PromptProcessingNode(TextProcessingNode):
    """Base class for prompt processing nodes"""
    
    # Common prompt processing utilities
    @staticmethod
    def clean_prompt(prompt: str) -> str:
        """Common prompt cleaning logic"""
        if not prompt:
            return ""
        
        # Remove extra whitespace
        prompt = ' '.join(prompt.split())
        
        # Remove duplicate commas
        prompt = re.sub(r',\s*,', ',', prompt)
        
        # Clean trailing commas
        prompt = prompt.rstrip(', ')
        
        return prompt
    
    @staticmethod
    def split_prompt(prompt: str, delimiter: str = ',') -> List[str]:
        """Split prompt into components"""
        if not prompt:
            return []
        
        return [part.strip() for part in prompt.split(delimiter) if part.strip()]

class ModelProcessingNode(ValidationMixin):
    """Base class for model processing nodes"""
    
    @performance_monitor("model_processing")
    @cached_operation(ttl=300)
    def process_model(self, model, **kwargs):
        """Common model processing workflow"""
        try:
            return self._process_model_impl(model, **kwargs)
        except Exception as e:
            return None, f"Model processing error: {str(e)}"
    
    @abstractmethod
    def _process_model_impl(self, model, **kwargs):
        """Implement specific model processing logic"""
        pass
