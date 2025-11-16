"""LM Studio Multi-Model Selector Node

Dynamically discover and select from available models.
"""

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode

import json
from typing import Any, Dict, List, Tuple
import urllib.request
import urllib.error


class LMStudioMultiModelSelector(LMStudioUtilityBaseNode):
    """Dynamically discover and select from loaded models."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "auto_refresh": ("BOOLEAN", {"default": True, "tooltip": "Auto-discover models from server"}),
            },
            "optional": {
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "model_filter": (["all", "text", "vision", "embedding"], {"default": "all"}),
                "fallback_model": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("selected_model", "available_models", "info")
    FUNCTION = "select_model"

    @classmethod
    def IS_CHANGED(cls, auto_refresh: bool, **kwargs) -> float:
        """Refresh model list on each execution if auto_refresh enabled."""
        if auto_refresh:
            import time
            return time.time()
        return False

    def get_loaded_models(self, server_url: str) -> Tuple[List[Dict[str, Any]], str]:
        """Query LM Studio API for loaded models."""
        try:
            url = f"{server_url}/v1/models"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
                models = result.get("data", [])
                return models, ""
                
        except (urllib.error.URLError, ConnectionRefusedError, OSError) as e:
            return [], f"Connection failed: {str(e)}"
        except Exception as e:
            return [], f"Error: {str(e)}"

    def select_model(
        self,
        auto_refresh: bool = True,
        server_url: str = "http://localhost:1234",
        model_filter: str = "all",
        fallback_model: str = ""
    ) -> Tuple[str, str, str]:
        """Select model from available options."""
        
        info_parts = self._init_info("Multi-Model Selector", "🎯")
        info_parts.append(f"🔄 Auto-refresh: {'ON' if auto_refresh else 'OFF'}")
        info_parts.append(f"🔍 Filter: {model_filter}")
        
        # Get models from API
        models, error = self.get_loaded_models(server_url)
        
        if error:
            info_parts.append(f"❌ {error}")
            if fallback_model:
                info_parts.append(f"🔄 Using fallback: {fallback_model}")
                return (fallback_model, "[]", self._format_info(info_parts))
            else:
                info_parts.append("⚠️ No fallback model configured")
                return ("", "[]", self._format_info(info_parts))
        
        if not models:
            info_parts.append("⚠️ No models loaded in LM Studio")
            if fallback_model:
                info_parts.append(f"🔄 Using fallback: {fallback_model}")
                return (fallback_model, "[]", self._format_info(info_parts))
            else:
                info_parts.append("💡 Load a model in LM Studio first")
                return ("", "[]", self._format_info(info_parts))
        
        # Filter models
        filtered_models = []
        for model in models:
            model_id = model.get("id", "")
            
            if model_filter == "all":
                filtered_models.append(model)
            elif model_filter == "text":
                # Heuristic: exclude vision models (contain "vision", "vl", "visual")
                if not any(k in model_id.lower() for k in ["vision", "-vl", "visual", "llava"]):
                    filtered_models.append(model)
            elif model_filter == "vision":
                # Heuristic: include vision models
                if any(k in model_id.lower() for k in ["vision", "-vl", "visual", "llava", "qwen3-vl"]):
                    filtered_models.append(model)
            elif model_filter == "embedding":
                # Heuristic: include embedding models
                if any(k in model_id.lower() for k in ["embed", "embedding"]):
                    filtered_models.append(model)
        
        # Select primary model (first in list)
        if filtered_models:
            selected = filtered_models[0].get("id", "")
            info_parts.append(f"✅ Selected: {selected}")
            info_parts.append(f"📊 Available: {len(filtered_models)} model(s)")
        else:
            selected = ""
            info_parts.append("⚠️ No models match filter")
            if fallback_model:
                selected = fallback_model
                info_parts.append(f"🔄 Using fallback: {fallback_model}")
        
        # List all available
        available_list = []
        for i, model in enumerate(filtered_models, 1):
            model_id = model.get("id", "unknown")
            available_list.append({
                "id": model_id,
                "owned_by": model.get("owned_by", ""),
                "created": model.get("created", 0)
            })
            if i <= 3:  # Show first 3 in info
                info_parts.append(f"  {i}. {model_id}")
        
        if len(filtered_models) > 3:
            info_parts.append(f"  ... and {len(filtered_models) - 3} more")
        
        available_json = json.dumps(available_list, indent=2)
        
        return (selected, available_json, self._format_info(info_parts))


__all__ = ["LMStudioMultiModelSelector"]
