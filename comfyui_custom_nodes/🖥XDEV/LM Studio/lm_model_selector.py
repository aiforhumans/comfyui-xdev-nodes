"""LM Studio Model Selector Node

Lists available models from LM Studio and outputs model string.
"""

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode

import json
import urllib.error
import urllib.request
from typing import Any


class LMStudioModelSelector(LMStudioUtilityBaseNode):
    """Select and output model name from LM Studio's loaded models."""
    
    # Class variable to cache models
    _cached_models: list[str] = []
    _cache_valid: bool = False

    @classmethod
    def get_models(cls, server_url: str = "http://localhost:1234") -> list[str]:
        """Fetch available models from LM Studio server."""
        try:
            url = f"{server_url}/v1/models"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            # Extract model IDs
            if "data" in result and isinstance(result["data"], list):
                models = [model.get("id", "unknown") for model in result["data"]]
                # Filter out embedding models for cleaner list
                text_models = [m for m in models if "embed" not in m.lower()]
                
                if text_models:
                    cls._cached_models = text_models
                    cls._cache_valid = True
                    return text_models
                else:
                    return models if models else ["No models loaded"]
            
            return ["No models loaded"]
            
        except Exception as e:
            print(f"Error fetching models from LM Studio: {e}")
            # Return cached models if available
            if cls._cached_models:
                return cls._cached_models
            return ["Error: LM Studio not running"]

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        # Try to fetch models for the dropdown
        models = cls.get_models()
        
        return {
            "required": {
                "model": (models, {"default": models[0] if models else ""}),
            },
            "optional": {
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "refresh": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_name",)
    FUNCTION = "select_model"

    def select_model(
        self,
        model: str,
        server_url: str = "http://localhost:1234",
        refresh: bool = False
    ) -> tuple[str]:
        """Return selected model name."""
        
        # If refresh is enabled, update the model list
        if refresh:
            self._cache_valid = False
            self.get_models(server_url)
        
        # Validate model is still available
        if model.startswith("Error:") or model == "No models loaded":
            print(f"Warning: {model}")
        
        return (model,)


__all__ = ["LMStudioModelSelector"]
