from typing import Literal
import torch

def _avg_brightness(img: torch.Tensor) -> torch.Tensor:
    # img: [B,H,W,C], C=3
    x = img
    if x.dtype.is_floating_point:
        x = x.clamp(0.0, 1.0)
    else:
        x = x.float() / 255.0
    return x.mean(dim=(1,2,3))

class PickByBrightness:
    """
    Selects the brightest or darkest image from a batch.

    Inputs:
      - images: IMAGE tensor with shape [B,H,W,C]
      - mode: 'brightest' | 'darkest'
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {}),
                "mode": (["brightest", "darkest"], {"default": "brightest"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "pick"
    CATEGORY = "XDev/Image"

    def pick(self, images, mode: Literal["brightest","darkest"]="brightest"):
        if not isinstance(images, torch.Tensor):
            raise TypeError("Expected IMAGE torch.Tensor [B,H,W,C]")
        if images.ndim != 4 or images.shape[-1] != 3:
            raise ValueError("IMAGE must have shape [B,H,W,C] with C=3")
        scores = _avg_brightness(images)
        index = int(torch.argmax(scores)) if mode == "brightest" else int(torch.argmin(scores))
        chosen = images[index:index+1]
        return (chosen,)
