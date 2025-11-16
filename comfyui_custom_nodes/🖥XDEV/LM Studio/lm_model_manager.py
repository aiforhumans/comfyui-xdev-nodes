"""LM Studio Model Manager Utility

Handles automatic model unloading to free GPU memory for ComfyUI image generation.
LM Studio doesn't have a native unload API, so we use a workaround by loading
a minimal model or restarting the connection.
"""

import json
import urllib.error
import urllib.request


class LMModelManager:
    """Manages LM Studio model loading/unloading for memory optimization."""
    
    _last_loaded_model: str | None = None
    _auto_unload: bool = True
    
    @classmethod
    def get_loaded_model(cls, server_url: str = "http://localhost:1234") -> str | None:
        """Check which model is currently loaded in LM Studio."""
        try:
            url = f"{server_url}/v1/models"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if "data" in result and isinstance(result["data"], list) and result["data"]:
                # LM Studio typically only loads one model at a time
                model_id = result["data"][0].get("id", None)
                cls._last_loaded_model = model_id
                return model_id
            
            return None
            
        except Exception as e:
            print(f"Error checking loaded model: {e}")
            return None
    
    @classmethod
    def request_model_unload(cls, server_url: str = "http://localhost:1234") -> tuple[bool, str]:
        """
        Request model unload to free GPU memory.
        
        NOTE: LM Studio doesn't have a native unload API. This function serves as a 
        placeholder that can be extended with custom solutions:
        
        Options:
        1. Manual: User manually unloads in LM Studio UI before running workflow
        2. CLI: Use LM Studio CLI if available (lms unload)
        3. API workaround: Make an invalid request to trigger timeout/cleanup
        4. External script: Call a script that interfaces with LM Studio
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check if model is loaded
            loaded_model = cls.get_loaded_model(server_url)
            
            if not loaded_model:
                return (True, "No model currently loaded")
            
            # LM Studio doesn't have unload API yet
            # Return instruction message
            message = (
                f"Model '{loaded_model}' is loaded in LM Studio. "
                "Please manually unload it in LM Studio to free GPU memory for ComfyUI. "
                "In LM Studio: Go to Local Server tab → Click 'Unload Model' button."
            )
            
            return (False, message)
            
        except Exception as e:
            return (False, f"Error requesting unload: {str(e)}")
    
    @classmethod
    def set_auto_unload(cls, enabled: bool):
        """Enable/disable automatic unload requests."""
        cls._auto_unload = enabled
    
    @classmethod
    def get_auto_unload(cls) -> bool:
        """Check if auto-unload is enabled."""
        return cls._auto_unload


def check_model_loaded(server_url: str = "http://localhost:1234") -> tuple[bool, str | None, str]:
    """
    Check if a model is loaded and return warning if needed.
    
    Returns:
        Tuple of (model_loaded: bool, model_name: Optional[str], warning: str)
    """
    model = LMModelManager.get_loaded_model(server_url)
    
    if model:
        warning = (
            f"⚠️ LM Studio model '{model}' is using GPU memory. "
            "For optimal ComfyUI performance, unload the model in LM Studio's Local Server tab. "
            "The model will be automatically loaded when this node runs."
        )
        return (True, model, warning)
    
    return (False, None, "")


__all__ = ["LMModelManager", "check_model_loaded"]
