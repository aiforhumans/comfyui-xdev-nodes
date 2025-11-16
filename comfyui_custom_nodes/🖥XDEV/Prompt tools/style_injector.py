"""Style Tags Injector Node

Injects predefined style tags into prompts.
"""

from typing import Any


class StyleTagsInjector:
    """Injects style presets into prompts."""

    STYLE_PRESETS = {
        "None": "",
        "Photorealistic": "photorealistic, photo, realistic, 8k uhd, high quality",
        "Cinematic": "cinematic lighting, dramatic, film grain, depth of field, bokeh",
        "Anime": "anime style, manga, cel shading, vibrant colors",
        "Oil Painting": "oil painting, painterly, brush strokes, canvas texture",
        "Watercolor": "watercolor painting, soft colors, paper texture, delicate",
        "Digital Art": "digital art, digital painting, trending on artstation",
        "3D Render": "3d render, octane render, unreal engine, ray tracing",
        "Sketch": "pencil sketch, hand drawn, line art, charcoal",
        "Fantasy": "fantasy art, magical, ethereal, mystical atmosphere",
        "Sci-Fi": "sci-fi, futuristic, cyberpunk, neon lights, high tech",
    }

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "style_preset": (list(cls.STYLE_PRESETS.keys()), {"default": "None"}),
            },
            "optional": {
                "style_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "position": (["prefix", "suffix"], {"default": "suffix"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "inject_style"
    CATEGORY = "🖥XDEV/Prompt tools"

    def inject_style(
        self,
        prompt: str,
        style_preset: str,
        style_strength: float = 1.0,
        position: str = "suffix"
    ) -> tuple[str]:
        """Inject style tags into prompt."""
        style_tags = self.STYLE_PRESETS.get(style_preset, "")
        
        if not style_tags or style_strength == 0.0:
            return (prompt,)
        
        # Apply strength by wrapping in emphasis syntax if needed
        if style_strength != 1.0:
            # ComfyUI/SD supports (text:weight) syntax
            style_tags = f"({style_tags}:{style_strength:.1f})"
        
        if position == "prefix":
            result = f"{style_tags}, {prompt}" if prompt.strip() else style_tags
        else:  # suffix
            result = f"{prompt}, {style_tags}" if prompt.strip() else style_tags
        
        return (result,)


__all__ = ["StyleTagsInjector"]
