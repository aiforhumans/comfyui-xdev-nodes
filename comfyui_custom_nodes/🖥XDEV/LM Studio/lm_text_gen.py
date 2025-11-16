"""LM Studio Text Generation Node

Generates text prompts using LM Studio local server.
"""

from typing import Any, Dict, Tuple

try:
    from .lm_base_node import LMStudioTextBaseNode
    from .lm_utils import (
        LMStudioConnectionError,
        LMStudioAPIError,
        ErrorFormatter,
    )
except ImportError:
    from lm_base_node import LMStudioTextBaseNode
    from lm_utils import (
        LMStudioConnectionError,
        LMStudioAPIError,
        ErrorFormatter,
    )


class LMStudioTextGen(LMStudioTextBaseNode):
    """Generate text using LM Studio API."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "prompt": ("STRING", {"default": "Write a creative image prompt for:", "multiline": True}),
                "user_input": ("STRING", {"default": "a fantasy landscape", "multiline": True}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 200, "min": -1, "max": 4096, "step": 1}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "You are a creative AI assistant that generates detailed SDXL image prompts. SDXL understands natural language well - describe images vividly with specific details about subject, composition, lighting, mood, and style. You can use full sentences or comma-separated keywords. Keep negative prompts minimal.", "multiline": True}),
                "response_format": (["text", "json"], {"default": "text"}),
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "model": ("STRING", {"default": "", "forceInput": True}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }
    
    FUNCTION = "generate_text"

    def generate_text(
        self,
        prompt: str,
        user_input: str,
        temperature: float = 0.7,
        max_tokens: int = 200,
        system_prompt: str = "",
        response_format: str = "text",
        server_url: str = "http://localhost:1234",
        model: str = "",
        seed: int = -1
    ) -> Tuple[str, str]:
        """Generate text using LM Studio API with enhanced output formatting."""
        
        # Initialize info output using base class
        info_parts = self._init_info("LM Studio Text Generator", "📝")
        
        # Add model info
        self._add_model_info(info_parts, server_url)
        
        # Add generation parameters
        params = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "format": response_format,
        }
        if seed >= 0:
            params["seed"] = seed
        self._add_params_info(info_parts, **params)
        
        try:
            info_parts.append("⏳ Generating...")
            
            # Build messages using base class helper
            messages = self._build_messages(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format,
                user_input=user_input
            )
            
            # Make API request using base class helper
            generated = self._make_api_request(
                server_url=server_url,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                model=model,
                seed=seed,
                timeout=60
            )
            
            # Add completion info
            self._add_completion_info(info_parts, generated)
            
            # Format output using base class helper
            output = self._wrap_output(generated, "GENERATED TEXT", "🎯")
            
            return (output, self._format_info(info_parts))
            
        except LMStudioConnectionError as e:
            error_msg = ErrorFormatter.format_connection_error(server_url, str(e))
            info_parts.append("❌ Connection failed")
            info_parts.append("See main output for troubleshooting")
            return (error_msg, self._format_info(info_parts))
            
        except LMStudioAPIError as e:
            error_msg = ErrorFormatter.format_api_error(str(e))
            info_parts.append("❌ API error")
            return (error_msg, self._format_info(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return (error_msg, self._format_info(info_parts))


__all__ = ["LMStudioTextGen"]
