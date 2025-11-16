"""Reusable prompt templates and instructions for LM Studio nodes."""

from __future__ import annotations

from typing import Dict, Literal

DetailLevel = Literal["minimal", "moderate", "detailed", "very detailed"]

# Centralized SDXL keyword catalogs so nodes, docs, and tests stay in sync.
LIGHTING_KEYWORDS: Dict[str, str] = {
    "natural": "available light, golden daylight, realistic shadows",
    "studio": "key/fill/rim setup with controlled highlights",
    "golden hour": "warm low-angle sun with long shadows",
    "dramatic": "high contrast chiaroscuro, deep shadows",
    "soft": "diffused light, gentle falloff, dreamy feel",
    "volumetric": "god rays with particles visible",
    "rim light": "back edge highlight that outlines the subject",
    "neon": "bold colored glows and reflections",
    "candlelight": "warm flickering illumination",
    "moonlit": "cool blue tones with silhouettes",
    "custom": "user-provided lighting setup"
}

MOOD_KEYWORDS: Dict[str, str] = {
    "dramatic": "intense, high-stakes energy",
    "peaceful": "calm, tranquil atmosphere",
    "mysterious": "enigmatic, shadow-filled scene",
    "energetic": "dynamic, action-focused",
    "romantic": "soft, intimate feel",
    "melancholic": "quiet, reflective mood",
    "whimsical": "playful, imaginative tone"
}

CAMERA_FRAMING: Dict[str, str] = {
    "portrait": "shoulders-up framing focused on the subject",
    "full body": "head-to-toe framing",
    "mid shot": "waist-up composition",
    "close-up": "face filling most of the frame",
    "wide shot": "environment-forward view",
    "dynamic angle": "Dutch tilt or motion-heavy framing",
    "low angle": "camera below eye level",
    "high angle": "camera above eye level",
    "bird's eye": "top-down perspective",
    "macro": "extreme close detail",
    "custom": "user-provided framing"
}

QUALITY_TAGS: Dict[str, str] = {
    "highly detailed": "micro-detail emphasis",
    "8k resolution": "ultra high fidelity",
    "award winning": "prestige photography vibe",
    "professional": "studio-grade production",
    "sharp focus": "crisp clarity",
    "film grain": "cinematic texture",
    "bokeh": "shallow depth of field",
    "dramatic lighting": "spotlit high contrast",
    "sweeping composition": "epic scene layout"
}

SDXL_SYSTEM_PROMPT = (
    "You are an expert at writing SDXL prompts. SDXL understands natural language "
    "better than SD 1.5 - you can describe images in detail with full sentences OR "
    "use comma-separated keywords. Both work well. When using keyword weights like "
    "(keyword:1.2), keep weights between 1.0-1.4 as SDXL is very sensitive. Focus "
    "on vivid, specific visual details. For negative prompts, keep them minimal - "
    "only include what you actively want to avoid (like 'cartoon' for photos, or "
    "'blurry, low quality')."
)

_DETAIL_INSTRUCTIONS = {
    "minimal": "Keep it concise with only essential details.",
    "moderate": "Add moderate details about composition and lighting.",
    "detailed": "Include detailed descriptions of composition, lighting, mood, and visual elements.",
    "very detailed": "Create an extremely detailed prompt with comprehensive descriptions of every visual aspect.",
}


def get_detail_instruction(level: DetailLevel) -> str:
    """Return the guidance text that maps to the requested SDXL detail level."""
    return _DETAIL_INSTRUCTIONS[level]


def build_sdxl_instruction(
    *,
    simple_prompt: str,
    additional_details: str,
    style: str,
    detail_instruction: str,
    response_format: Literal["text", "json"],
    include_negative_prompt: bool,
) -> str:
    """Create the long-form instruction payload for SDXL prompt enhancement."""

    style_instruction = f" in {style} style" if style != "none" else ""
    extras = f"Additional requirements: {additional_details}" if additional_details else ""

    if response_format == "json":
        neg_placeholder = ("minimal list of specific things to avoid" if include_negative_prompt else "")
        return f"""Transform this simple concept into a professional SDXL image generation prompt{style_instruction}.

Simple concept: {simple_prompt}
{extras}

IMPORTANT SDXL BEST PRACTICES:
1. SDXL understands natural language - you can describe in detail OR use comma-separated keywords
2. Subject first with vivid descriptors (colors, materials, textures)
3. Composition and framing details (portrait, wide shot, close-up, perspective)
4. Lighting specifics (golden hour, studio lighting, rim light, dramatic shadows)
5. Mood and atmosphere (dramatic, peaceful, energetic, mysterious)
6. Style references - use artist names (Greg Rutkowski, Artgerm, etc.) or art styles
7. Quality boosters at end (highly detailed, 8k resolution, award winning photography)
8. For keyword weights use (keyword:weight) between 1.0-1.4 only - SDXL is very sensitive
9. NEGATIVE PROMPTS: Keep minimal! Only include what you actively want to avoid

{detail_instruction}

Return a JSON object with this structure:
{{
  "positive_prompt": "detailed natural language description OR comma-separated keywords with rich visual details",
  "negative_prompt": "{neg_placeholder}"
}}

EXAMPLE (keyword style):
{{
  "positive_prompt": "beautiful woman wearing fantastic hand-dyed cotton clothes, embellished beaded feather decorative fringe knots, colorful pigtails, subtropical flowers and plants, symmetrical face, intricate, elegant, highly detailed, 8k, digital painting, trending on pinterest, concept art, sharp focus, illustration, art by Tom Bagshaw and Alphonse Mucha",
  "negative_prompt": "ugly, deformed"
}}

EXAMPLE (natural language style):
{{
  "positive_prompt": "A professional photograph of a rhino dressed in a tailored suit and tie, sitting at a polished wooden bar table with elegant bar stools in the background, award winning photography in the style of Elke Vogelsang, dramatic lighting, shallow depth of field, highly detailed",
  "negative_prompt": "cartoon, illustration, animation"
}}"""

    instruction = f"""Transform this simple concept into a professional SDXL image generation prompt{style_instruction}.

Simple concept: {simple_prompt}
{extras}

IMPORTANT SDXL BEST PRACTICES:
1. SDXL understands natural language well - describe images in detail like you're explaining to a person
2. You can ALSO use comma-separated keywords - both approaches work
3. Subject first with vivid details (materials, colors, textures, lighting)
4. Include composition (portrait, wide angle, close-up) and perspective
5. Specify lighting (golden hour, studio lighting, dramatic shadows, rim light)
6. Add mood and atmosphere keywords (dramatic, peaceful, mysterious)
7. Reference artists or styles (Greg Rutkowski, Artgerm, photorealistic, digital art)
8. Add quality tags at end (highly detailed, 8k resolution, award winning)
9. For weights use (keyword:1.1) to (keyword:1.4) max - SDXL is sensitive to emphasis
10. Keep negative prompts minimal - only what you want to avoid

{detail_instruction}

EXAMPLE (keyword style):
"a woman in a futuristic suit holding a gun, looking at camera, neon lighting, rain-soaked street, cyberpunk art by Krenz Cushart, neo-figurative, highly detailed anime style, dramatic composition, vibrant colors, 8k resolution"

EXAMPLE (natural language):
"A stunning photograph of a man in a subway station, beautiful detailed eyes, professional award winning portrait photography, shot with Zeiss 150mm f/2.8 lens, highly detailed glossy eyes and skin pores visible, dramatic lighting from overhead fluorescents, black and white photography"

Return ONLY the formatted prompt, no explanations."""

    if include_negative_prompt:
        instruction += "\n\nAlso provide a negative prompt with common issues to avoid (same comma-separated format)."

    return instruction


PROMPT_STYLE_LIBRARY = {
    "lighting": LIGHTING_KEYWORDS,
    "mood": MOOD_KEYWORDS,
    "composition": CAMERA_FRAMING,
    "quality": QUALITY_TAGS,
}

__all__ = [
    "SDXL_SYSTEM_PROMPT",
    "get_detail_instruction",
    "build_sdxl_instruction",
    "LIGHTING_KEYWORDS",
    "MOOD_KEYWORDS",
    "CAMERA_FRAMING",
    "QUALITY_TAGS",
    "PROMPT_STYLE_LIBRARY",
]
