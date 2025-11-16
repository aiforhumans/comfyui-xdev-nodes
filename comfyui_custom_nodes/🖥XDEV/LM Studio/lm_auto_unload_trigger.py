"""LM Studio Auto Unload Trigger Node

Automatically triggers model unload in LM Studio when signal is received.
Useful for automated workflows that need to free GPU memory before image generation.

Uses LM Studio CLI (lms) for programmatic model unloading.
"""

from typing import Any

try:
    from .lm_base_node import LMStudioUtilityBaseNode
    from .lm_model_manager import check_model_loaded
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode
    from lm_model_manager import check_model_loaded


class LMStudioAutoUnloadTrigger(LMStudioUtilityBaseNode):
    """Automatically unload LM Studio model when triggered."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "trigger": ("BOOLEAN", {"default": True}),
                "unload_method": (["warning_only", "lms_cli", "force_error"], {"default": "lms_cli"}),
            },
            "optional": {
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "passthrough": ("STRING", {"default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("status", "unloaded", "passthrough")
    FUNCTION = "trigger_unload"

    def trigger_unload(
        self,
        trigger: bool = True,
        unload_method: str = "warning_only",
        server_url: str = "http://localhost:1234",
        passthrough: str = ""
    ) -> tuple[str, bool, str]:
        """Trigger model unload when signal received."""
        
        if not trigger:
            return ("Trigger disabled - no action taken", False, passthrough)
        
        # Check if model is loaded
        model_loaded, model_name, warning = check_model_loaded(server_url)
        
        if not model_loaded:
            status = "✓ No LM Studio model loaded - GPU memory available"
            print(status)
            return (status, True, passthrough)
        
        # Model is loaded - take action based on method
        if unload_method == "warning_only":
            status = (
                f"⚠️ WARNING: LM Studio model '{model_name}' is still loaded!\n"
                f"GPU Memory Conflict Detected!\n\n"
                f"MANUAL ACTION REQUIRED:\n"
                f"1. Open LM Studio\n"
                f"2. Go to 'Local Server' tab\n"
                f"3. Click 'Unload Model' button\n\n"
                f"Workflow will continue, but image generation may fail due to GPU memory limits."
            )
            print(f"\n{'='*60}")
            print(status)
            print(f"{'='*60}\n")
            return (status, False, passthrough)
        
        elif unload_method == "lms_cli":
            # Attempt to unload via LM Studio CLI (lms)
            try:
                import subprocess
                
                # Try to run lms unload --all
                try:
                    result = subprocess.run(
                        ["lms", "unload", "--all"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        status = f"✓ Successfully unloaded model '{model_name}' via lms CLI"
                        print(status)
                        return (status, True, passthrough)
                    else:
                        # lms command failed
                        error_output = result.stderr or result.stdout
                        raise Exception(f"lms command failed: {error_output}")
                        
                except FileNotFoundError as err:
                    # lms not found in PATH
                    raise Exception("lms CLI not found in PATH. Please run: lms bootstrap") from err
                except subprocess.TimeoutExpired as err:
                    raise Exception("lms command timed out") from err
                
            except Exception as e:
                status = (
                    f"⚠️ LM Studio model '{model_name}' is loaded\n"
                    f"CLI unload failed: {str(e)}\n\n"
                    f"FALLBACK OPTIONS:\n"
                    f"1. Install lms CLI: Run 'lms bootstrap' in PowerShell\n"
                    f"   Location: %USERPROFILE%/.lmstudio/bin/lms.exe bootstrap\n"
                    f"2. Manual unload: Open LM Studio → Local Server tab → Click 'Unload Model'\n"
                    f"3. Use command: lms unload --all"
                )
                print(f"\n{'='*60}")
                print(status)
                print(f"{'='*60}\n")
                return (status, False, passthrough)
        
        elif unload_method == "force_error":
            # Force workflow to stop with error message
            error_msg = (
                f"WORKFLOW STOPPED: LM Studio model '{model_name}' is using GPU memory!\n\n"
                f"To continue:\n"
                f"1. Open LM Studio\n"
                f"2. Go to Local Server tab\n"
                f"3. Click 'Unload Model'\n"
                f"4. Restart this workflow\n\n"
                f"This prevents GPU out-of-memory errors during image generation."
            )
            print(f"\n{'='*60}")
            print(f"ERROR: {error_msg}")
            print(f"{'='*60}\n")
            # Return error in status but don't actually raise exception (ComfyUI might not handle well)
            return (f"❌ ERROR: {error_msg}", False, passthrough)
        
        return ("Unknown unload method", False, passthrough)


__all__ = ["LMStudioAutoUnloadTrigger"]
