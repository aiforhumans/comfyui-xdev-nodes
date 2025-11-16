"""LM Studio Model Unload Helper Node

Provides a workflow node to check and remind about model unloading.
"""

from typing import Any, Dict, Tuple

try:
    from .lm_base_node import LMStudioUtilityBaseNode
    from .lm_model_manager import LMModelManager, check_model_loaded
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode
    from lm_model_manager import LMModelManager, check_model_loaded


class LMStudioModelUnloadHelper(LMStudioUtilityBaseNode):
    """Check if LM Studio model is loaded and provide unload guidance."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "check_before_generation": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "passthrough": ("STRING", {"default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("status_message", "passthrough")
    FUNCTION = "check_model"

    def check_model(
        self,
        check_before_generation: bool = True,
        server_url: str = "http://localhost:1234",
        passthrough: str = ""
    ) -> Tuple[str, str]:
        """Check model status and return guidance message."""
        
        if not check_before_generation:
            return ("Model check disabled", passthrough)
        
        try:
            model_loaded, model_name, warning = check_model_loaded(server_url)
            
            if model_loaded:
                message = (
                    f"⚠️ MODEL LOADED: '{model_name}'\n\n"
                    "For optimal ComfyUI image generation:\n"
                    "1. Open LM Studio\n"
                    "2. Go to 'Local Server' tab\n"
                    "3. Click 'Unload Model' button\n\n"
                    "This frees GPU memory for Stable Diffusion.\n"
                    "The model will be automatically loaded when needed by LM Studio nodes."
                )
                print(warning)
                return (message, passthrough)
            else:
                message = "✓ No LM Studio model loaded - GPU memory available for ComfyUI"
                return (message, passthrough)
                
        except Exception as e:
            error_msg = f"Error checking model status: {str(e)}"
            print(error_msg)
            return (error_msg, passthrough)


__all__ = ["LMStudioModelUnloadHelper"]
