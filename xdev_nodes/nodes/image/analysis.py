"""
Image analysis and selection tools
Part of the XDev Nodes modular architecture.
"""

from __future__ import annotations
from typing import Dict, Tuple, Any, Literal
from ...utils import get_torch, get_numpy, validate_choice
from ...categories import NodeCategories


def _avg_brightness_torch(img):
    """Optimized torch brightness calculation with minimal memory allocation"""
    torch = get_torch()
    if torch is None:
        raise RuntimeError("PyTorch not available")
    
    # Optimize for common case: already normalized floating point
    if img.dtype.is_floating_point:
        # Clamp in-place for memory efficiency if possible
        if img.is_contiguous():
            return img.clamp_(0.0, 1.0).mean(dim=(1, 2, 3))
        else:
            return img.clamp(0.0, 1.0).mean(dim=(1, 2, 3))
    else:
        # Efficient integer to float conversion
        return (img.float() * (1.0 / 255.0)).mean(dim=(1, 2, 3))


def _avg_brightness_list(img):
    """Optimized pure Python brightness calculation with reduced memory allocation"""
    scores = []
    for b in img:
        # Use generator expressions for memory efficiency
        flat = (pixel_val for row in b for pixel in row for pixel_val in pixel)
        pixel_values = list(flat)
        if not pixel_values:
            scores.append(0.0)
            continue
        
        # Efficient normalization
        max_val = max(pixel_values)
        if max_val > 1.0:
            # Integer values - normalize by 255
            mean_brightness = sum(v / 255.0 for v in pixel_values) / len(pixel_values)
        else:
            # Already normalized float values
            mean_brightness = sum(pixel_values) / len(pixel_values)
        
        scores.append(mean_brightness)
    return scores


class PickByBrightness:
    """
    Advanced image selection based on brightness analysis with multiple algorithms.
    
    Intelligently selects the brightest or darkest image from a batch using various
    brightness calculation methods. Features graceful fallbacks from PyTorch to NumPy
    to pure Python for maximum compatibility.
    """
    
    DISPLAY_NAME = "Pick By Brightness (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "Batch of images to analyze. Must contain at least 2 images for comparison."
                }),
                "mode": (["brightest", "darkest"], {
                    "default": "brightest",
                    "tooltip": "Selection criteria: 'brightest' selects highest brightness, 'darkest' selects lowest brightness."
                })
            },
            "optional": {
                "algorithm": (["average", "weighted", "luminance"], {
                    "default": "average",
                    "tooltip": "Brightness calculation method: 'average' (simple mean), 'weighted' (perceptual), 'luminance' (standard formula)."
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable comprehensive input validation with detailed error messages."
                }),
                "return_metadata": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Include detailed processing information in the output string."
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "FLOAT", "STRING")
    RETURN_NAMES = ("selected_image", "brightness_score", "selection_info")
    FUNCTION = "pick"
    CATEGORY = NodeCategories.IMAGE_ANALYSIS
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
            
            # Torch path (preferred) with lazy loading
            torch = get_torch()
            if torch is not None and hasattr(images, 'dtype'):  # Check for tensor-like object
                processing_method = "torch"
                scores = self._calculate_brightness_scores(images, algorithm, "torch")
                idx = int(torch.argmax(scores).item() if mode == "brightest" else torch.argmin(scores).item())
                selected_image = images[idx:idx+1]
                brightness_score = float(scores[idx].item())
            
            # NumPy path (fallback) with lazy import
            elif processing_method == "unknown":
                try:
                    np = get_numpy()
                    if np is not None:
                        processing_method = "numpy"
                        # Efficient array conversion with minimal copying
                        arr = np.asarray(images, dtype=np.float32)  # Use float32 for memory efficiency
                        if arr.max() > 1.0:
                            arr *= (1.0 / 255.0)  # In-place operation for memory efficiency
                        scores = self._calculate_brightness_scores(arr, algorithm, "numpy")
                        idx = int(np.argmax(scores) if mode == "brightest" else np.argmin(scores))
                        selected_image = arr[idx:idx+1]
                        brightness_score = float(scores[idx])
                    else:
                        processing_method = "python_fallback"
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
        Optimized input validation with early returns for performance.
        """
        # Fast null check
        if images is None:
            return {"valid": False, "error": "Images input is None. Please provide a valid image batch."}
        
        # Use optimized validation with direct checks
        if mode not in {"brightest", "darkest"}:
            return {"valid": False, "error": f"Invalid mode '{mode}'. Must be 'brightest' or 'darkest'."}
        
        if algorithm not in {"average", "weighted", "luminance"}:
            return {"valid": False, "error": f"Invalid algorithm '{algorithm}'. Must be one of: average, weighted, luminance."}
        
        # Optimized batch size validation
        try:
            batch_size = len(images) if hasattr(images, '__len__') else 0
            if batch_size < 2:
                return {"valid": False, "error": f"Batch size too small ({batch_size}). Need at least 2 images."}
            if batch_size > 100:
                return {"valid": False, "error": f"Batch size too large ({batch_size}). Maximum: 100 images."}
        except Exception as e:
            return {"valid": False, "error": f"Error checking batch size: {str(e)}"}
        
        # All validations passed
        return {"valid": True, "error": None}
    
    def _calculate_brightness_scores(self, images, algorithm: str, method: str):
        """Calculate brightness scores using specified algorithm and method."""
        torch = get_torch()
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
            # NumPy implementation with lazy loading
            np = get_numpy()
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
            return float("nan")
