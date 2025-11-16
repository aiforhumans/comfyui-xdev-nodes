"""Base Node Class for LM Studio Nodes

Provides common functionality and patterns for all LM Studio nodes.
"""

from typing import Any, Dict, Tuple, Optional
from abc import ABC, abstractmethod

try:
    from .lm_utils import (
        LMStudioAPIClient,
        InfoFormatter,
        OutputFormatter,
        build_messages,
        build_payload,
        extract_response_text,
    )
    from .lm_model_manager import check_model_loaded
except ImportError:
    from lm_utils import (
        LMStudioAPIClient,
        InfoFormatter,
        OutputFormatter,
        build_messages,
        build_payload,
        extract_response_text,
    )
    from lm_model_manager import check_model_loaded


class LMStudioBaseNode(ABC):
    """Base class for LM Studio nodes with common functionality."""
    
    # Common attributes that all nodes share
    CATEGORY = "🖥XDEV/LM Studio"
    OUTPUT_NODE = False
    
    # Default API settings
    DEFAULT_SERVER_URL = "http://localhost:1234"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 200
    DEFAULT_TIMEOUT = 60
    
    @classmethod
    def get_common_required_inputs(cls) -> Dict[str, Tuple]:
        """Get common required input parameters.
        
        Returns:
            Dictionary of common required inputs
        """
        return {
            "prompt": ("STRING", {"default": "Write a creative prompt:", "multiline": True}),
            "temperature": ("FLOAT", {"default": cls.DEFAULT_TEMPERATURE, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": cls.DEFAULT_MAX_TOKENS, "min": -1, "max": 4096, "step": 1}),
        }
    
    @classmethod
    def get_common_optional_inputs(cls) -> Dict[str, Tuple]:
        """Get common optional input parameters.
        
        Returns:
            Dictionary of common optional inputs
        """
        return {
            "system_prompt": ("STRING", {"default": "", "multiline": True}),
            "response_format": (["text", "json"], {"default": "text"}),
            "server_url": ("STRING", {"default": cls.DEFAULT_SERVER_URL}),
            "model": ("STRING", {"default": "", "forceInput": True}),
            "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
        }
    
    @classmethod
    @abstractmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters for the node.
        
        Must be implemented by subclass.
        """
        pass
    
    def _init_info(self, title: str, emoji: str = "📝") -> list:
        """Initialize info output with header.
        
        Args:
            title: Node title
            emoji: Emoji prefix
            
        Returns:
            List of info lines
        """
        return InfoFormatter.create_header(title, emoji)
    
    def _add_model_info(self, info_parts: list, server_url: str) -> None:
        """Add model loading information to info output.
        
        Args:
            info_parts: List of info lines to append to
            server_url: Server URL to check
        """
        model_loaded, loaded_model, warning = check_model_loaded(server_url)
        InfoFormatter.add_model_info(info_parts, loaded_model if model_loaded else None, warning)
    
    def _add_params_info(self, info_parts: list, **params) -> None:
        """Add parameter information to info output.
        
        Args:
            info_parts: List of info lines to append to
            **params: Parameter key-value pairs
        """
        InfoFormatter.add_parameters(info_parts, params)
    
    def _add_completion_info(self, info_parts: list, output_text: str, success: bool = True) -> None:
        """Add completion status to info output.
        
        Args:
            info_parts: List of info lines to append to
            output_text: Generated output text
            success: Whether generation succeeded
        """
        InfoFormatter.add_completion(info_parts, output_text, success)
    
    def _format_info(self, info_parts: list) -> str:
        """Format info parts into final string.
        
        Args:
            info_parts: List of info lines
            
        Returns:
            Formatted info string
        """
        return InfoFormatter.format(info_parts)
    
    def _wrap_output(self, text: str, title: str = "GENERATED TEXT", emoji: str = "🎯") -> str:
        """Wrap output text with header and footer.
        
        Args:
            text: Output text
            title: Header title
            emoji: Emoji prefix
            
        Returns:
            Formatted output string
        """
        return OutputFormatter.wrap_output(text, title, emoji)
    
    def _make_api_request(
        self,
        server_url: str,
        messages: list,
        temperature: float,
        max_tokens: int,
        response_format: str = "text",
        model: Optional[str] = None,
        seed: int = -1,
        timeout: int = None
    ) -> str:
        """Make API request to LM Studio.
        
        Args:
            server_url: Server URL
            messages: Messages array
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            response_format: "text" or "json"
            model: Model name (optional)
            seed: Random seed
            timeout: Request timeout (uses default if None)
            
        Returns:
            Generated text from API
            
        Raises:
            LMStudioConnectionError: Connection failed
            LMStudioAPIError: API error
        """
        payload = build_payload(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            model=model,
            seed=seed,
            stream=False
        )
        
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        
        result = LMStudioAPIClient.make_request(
            server_url=server_url,
            endpoint="/v1/chat/completions",
            payload=payload,
            timeout=timeout
        )
        
        return extract_response_text(result)
    
    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: str = "text",
        user_input: Optional[str] = None
    ) -> list:
        """Build messages array for API request.
        
        Args:
            prompt: Main prompt
            system_prompt: System prompt
            response_format: "text" or "json"
            user_input: Additional user input
            
        Returns:
            Messages array
        """
        return build_messages(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            user_input=user_input
        )


class LMStudioTextBaseNode(LMStudioBaseNode):
    """Base class for text generation nodes."""
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("generated_text", "info")
    # Don't set FUNCTION here - let subclass define it
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Default INPUT_TYPES for text nodes."""
        return {
            "required": {
                "prompt": ("STRING", {"default": "Write a creative prompt:", "multiline": True}),
                "user_input": ("STRING", {"default": "", "multiline": True}),
                **cls.get_common_required_inputs(),
            },
            "optional": cls.get_common_optional_inputs()
        }


class LMStudioPromptBaseNode(LMStudioBaseNode):
    """Base class for prompt generation/manipulation nodes."""
    
    # Many prompt nodes return multiple strings
    DEFAULT_TIMEOUT = 90  # Prompt nodes often need more time
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for SDXL prompt generation.
        
        Returns:
            Default system prompt
        """
        return (
            "You are an expert at creating SDXL image generation prompts. "
            "SDXL understands natural language well - you can use full sentences "
            "or comma-separated keywords. Focus on specific visual details, "
            "composition, lighting, mood, and style. Keep negative prompts minimal "
            "- only include specific things to avoid."
        )


class LMStudioUtilityBaseNode(LMStudioBaseNode):
    """Base class for utility nodes (model management, validation, etc)."""
    
    # Utility nodes typically don't make API calls
    pass


__all__ = [
    "LMStudioBaseNode",
    "LMStudioTextBaseNode",
    "LMStudioPromptBaseNode",
    "LMStudioUtilityBaseNode",
]
