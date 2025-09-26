from __future__ import annotations
from typing import Dict, Tuple, Any, Literal

# Try to import torch; fall back if unavailable.
try:
    import torch  # type: ignore
except Exception:
    torch = None  # type: ignore

def _avg_brightness_torch(img: "torch.Tensor"):
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
    """Selects the brightest or darkest image from a batch."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "images": ("IMAGE", {}),
                "mode": (["brightest","darkest"], {"default":"brightest"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "pick"
    CATEGORY = "XDev/Image"

    def pick(self, images, mode: Literal["brightest","darkest"]="brightest") -> Tuple[Any]:
        # Torch path
        if torch is not None and isinstance(images, torch.Tensor):
            scores = _avg_brightness_torch(images)
            idx = int(torch.argmax(scores).item() if mode == "brightest" else torch.argmin(scores).item())
            return (images[idx:idx+1],)

        # NumPy path
        try:
            import numpy as np
            arr = np.asarray(images, dtype=float)
            if arr.max() > 1.0:
                arr = arr / 255.0
            scores = arr.mean(axis=(1,2,3))
            idx = int(np.argmax(scores) if mode == "brightest" else np.argmin(scores))
            return (arr[idx:idx+1],)
        except Exception:
            pass

        # Pure Python fallback
        scores = _avg_brightness_list(images)
        if mode == "brightest":
            idx = max(range(len(scores)), key=lambda i: scores[i])
        else:
            idx = min(range(len(scores)), key=lambda i: scores[i])
        return ([images[idx]],)