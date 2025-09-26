from __future__ import annotations
from typing import Dict, Tuple, Any, Literal

# Try to import torch; fall back if unavailable.
try:
    import torch  # type: ignore
except Exception:
    torch = None  # type: ignore

def _avg_brightness_torch(img):
    # img: [B,H,W,C], C=3
    x = img
    if x.dtype.is_floating_point:
        x = x.clamp(0.0, 1.0)
    else:
        x = x.float() / 255.0
    return x.mean(dim=(1,2,3))

def _avg_brightness_list(img):
    # img is a Python list or nested lists
    def mean(nums):
        return sum(nums) / len(nums) if nums else 0.0
    scores = []
    for b in img:
        flat = []
        for row in b:
            for pix in row:
                flat.extend(pix)
        maxv = max(flat) if flat else 1.0
        scale = 255.0 if maxv > 1.0 else 1.0
        flat = [v/scale for v in flat]
        scores.append(mean(flat))
    return scores

class PickByBrightness:
    """
    Enhanced image brightness selector with comprehensive validation and rich documentation.
    
    This node demonstrates:
    - Robust fallback implementations (torch → numpy → pure Python)
    - Comprehensive input validation with detailed error messages
    - Rich tooltip documentation for all parameters
    - Advanced brightness calculation with multiple algorithms
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "Batch of input images to analyze. Supports ComfyUI IMAGE tensors in [B,H,W,C] format. Minimum batch size: 2 images."
                }),
                "mode": (["brightest", "darkest"], {
                    "default": "brightest",
                    "tooltip": "Selection criteria: 'brightest' picks the image with highest average brightness, 'darkest' picks the image with lowest average brightness."
                }),
            },
            "optional": {
                "algorithm": (["average", "weighted", "luminance"], {
                    "default": "average",
                    "tooltip": "Brightness calculation method: 'average' uses simple RGB mean, 'weighted' applies perceptual weights, 'luminance' uses standard luminance formula."
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable comprehensive input validation with detailed error messages. Recommended for production workflows."
                }),
                "return_metadata": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Return additional metadata including brightness scores and processing method used."
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "FLOAT", "STRING")
    RETURN_NAMES = ("selected_image", "brightness_score", "processing_info")
    FUNCTION = "pick"
    CATEGORY = "XDev/Image"
    DESCRIPTION = "Select brightest or darkest image from batch with comprehensive validation and multiple algorithms"

    def pick(self, images, mode: Literal["brightest","darkest"]="brightest", 
             algorithm: str = "average", validate_input: bool = True, 
             return_metadata: bool = False) -> Tuple[Any, float, str]:
        """
        Select brightest or darkest image from batch with comprehensive validation.
        
        Args:
            images: Input batch of images
            mode: Selection criteria (brightest/darkest)
            algorithm: Brightness calculation method
            validate_input: Enable input validation
            return_metadata: Include processing metadata
            
        Returns:
            Tuple of (selected_image, brightness_score, processing_info)
        """
        try:
            # Comprehensive input validation
            if validate_input:
                validation_result = self._validate_inputs(images, mode, algorithm)
                if not validation_result["valid"]:
                    error_msg = f"Input validation failed: {validation_result['error']}"
                    # Return error as image info, dummy values for other outputs
                    return (images if hasattr(images, '__len__') and len(images) > 0 else None, 0.0, error_msg)
            
            processing_method = "unknown"
            selected_image = None
            brightness_score = 0.0
            
            # Torch path (preferred)
            if torch is not None and isinstance(images, torch.Tensor):
                processing_method = "torch"
                scores = self._calculate_brightness_scores(images, algorithm, "torch")
                idx = int(torch.argmax(scores).item() if mode == "brightest" else torch.argmin(scores).item())
                selected_image = images[idx:idx+1]
                brightness_score = float(scores[idx].item())
            
            # NumPy path (fallback)
            elif processing_method == "unknown":
                try:
                    import numpy as np
                    processing_method = "numpy"
                    arr = np.asarray(images, dtype=float)
                    if arr.max() > 1.0:
                        arr = arr / 255.0
                    scores = self._calculate_brightness_scores(arr, algorithm, "numpy")
                    idx = int(np.argmax(scores) if mode == "brightest" else np.argmin(scores))
                    selected_image = arr[idx:idx+1]
                    brightness_score = float(scores[idx])
                except Exception:
                    processing_method = "python_fallback"
            
            # Pure Python fallback
            if processing_method == "python_fallback" or selected_image is None:
                processing_method = "python_fallback"
                scores = _avg_brightness_list(images)
                if mode == "brightest":
                    idx = max(range(len(scores)), key=lambda i: scores[i])
                else:
                    idx = min(range(len(scores)), key=lambda i: scores[i])
                selected_image = [images[idx]]
                brightness_score = scores[idx]
            
            # Compile processing info
            if return_metadata:
                info = f"Method: {processing_method} | Algorithm: {algorithm} | Selected: {mode} | Score: {brightness_score:.4f}"
            else:
                info = f"Selected {mode} image using {processing_method}"
            
            return (selected_image, brightness_score, info)
            
        except Exception as e:
            error_msg = f"Error processing images: {str(e)}"
            return (images if hasattr(images, '__len__') and len(images) > 0 else None, 0.0, error_msg)
    
    def _validate_inputs(self, images, mode: str, algorithm: str) -> Dict[str, Any]:
        """
        Comprehensive input validation with detailed error messages.
        
        Returns:
            Dict with 'valid' boolean and 'error' message if invalid
        """
        # Validate images input
        if images is None:
            return {
                "valid": False,
                "error": "Images input is None. Please provide a valid image batch."
            }
        
        # Check if images is a proper batch
        try:
            if hasattr(images, '__len__'):
                batch_size = len(images)
                if batch_size < 2:
                    return {
                        "valid": False,
                        "error": f"Batch size too small ({batch_size}). Need at least 2 images to compare brightness."
                    }
                if batch_size > 100:
                    return {
                        "valid": False,
                        "error": f"Batch size too large ({batch_size}). Maximum supported batch size is 100 images."
                    }
            else:
                return {
                    "valid": False,
                    "error": "Images input is not a proper batch. Expected tensor or array with multiple images."
                }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error checking batch size: {str(e)}"
            }
        
        # Validate mode parameter
        if mode not in ["brightest", "darkest"]:
            return {
                "valid": False,
                "error": f"Invalid mode '{mode}'. Must be 'brightest' or 'darkest'."
            }
        
        # Validate algorithm parameter
        if algorithm not in ["average", "weighted", "luminance"]:
            return {
                "valid": False,
                "error": f"Invalid algorithm '{algorithm}'. Must be 'average', 'weighted', or 'luminance'."
            }
        
        # All validations passed
        return {"valid": True, "error": None}
    
    def _calculate_brightness_scores(self, images, algorithm: str, method: str):
        """Calculate brightness scores using specified algorithm and method."""
        if method == "torch" and torch is not None:
            if algorithm == "luminance":
                # Standard luminance formula: 0.299*R + 0.587*G + 0.114*B
                weights = torch.tensor([0.299, 0.587, 0.114]).to(images.device)
                return torch.sum(images * weights, dim=-1).mean(dim=(1,2))
            elif algorithm == "weighted":
                # Perceptual weighting
                weights = torch.tensor([0.3, 0.59, 0.11]).to(images.device)
                return torch.sum(images * weights, dim=-1).mean(dim=(1,2))
            else:  # average
                return _avg_brightness_torch(images)
        else:
            # NumPy implementation
            import numpy as np
            if algorithm == "luminance":
                weights = np.array([0.299, 0.587, 0.114])
                return np.sum(images * weights, axis=-1).mean(axis=(1,2))
            elif algorithm == "weighted":
                weights = np.array([0.3, 0.59, 0.11])
                return np.sum(images * weights, axis=-1).mean(axis=(1,2))
            else:  # average
                return images.mean(axis=(1,2,3))
    
    @classmethod
    def IS_CHANGED(cls, images, mode="brightest", algorithm="average", validate_input=True, return_metadata=False):
        """ComfyUI caching mechanism."""
        try:
            # Create cache key from inputs and image properties
            cache_key = f"{mode}_{algorithm}_{validate_input}_{return_metadata}"
            if hasattr(images, 'shape'):
                cache_key += f"_{images.shape}"
            return cache_key
        except:
            return f"{mode}_{algorithm}_{validate_input}_{return_metadata}"