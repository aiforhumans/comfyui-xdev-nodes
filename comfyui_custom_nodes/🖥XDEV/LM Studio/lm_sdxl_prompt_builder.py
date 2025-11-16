"""LM Studio SDXL Prompt Builder Node

Generates complete SDXL-optimized prompts with proper structure and conditioning parameters.
"""

try:
    from .lm_base_node import LMStudioPromptBaseNode
    from .lm_utils import JSONParser, ErrorFormatter
    from .lm_model_manager import check_model_loaded
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode
    from lm_utils import JSONParser, ErrorFormatter
    from lm_model_manager import check_model_loaded

from typing import Any, Dict, Tuple


class LMStudioSDXLPromptBuilder(LMStudioPromptBaseNode):
    """Build complete SDXL prompts with LLM assistance and proper conditioning structure."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "concept": ("STRING", {"default": "a fantasy warrior", "multiline": True, "tooltip": "Simple concept or description"}),
                "style": (["photorealistic", "digital art", "anime", "fantasy art", "cinematic", "oil painting", "watercolor", "concept art", "3d render", "custom"], {"default": "photorealistic"}),
                "composition": (["portrait", "full body", "mid shot", "close-up", "wide shot", "dynamic angle", "low angle", "high angle"], {"default": "portrait"}),
                "lighting": (["natural", "studio", "golden hour", "dramatic", "soft", "volumetric", "rim light", "neon", "custom"], {"default": "natural"}),
                "detail_level": (["moderate", "high", "very high", "ultra detailed"], {"default": "high"}),
            },
            "optional": {
                "custom_details": ("STRING", {"default": "", "multiline": True, "tooltip": "Additional specific requirements"}),
                "artist_references": ("STRING", {"default": "", "tooltip": "Comma-separated artist names"}),
                "negative_prompt": ("BOOLEAN", {"default": True}),
                "include_conditioning_params": ("BOOLEAN", {"default": True, "tooltip": "Add width/height/aesthetic_score"}),
                "target_width": ("INT", {"default": 1024, "min": 512, "max": 2048, "step": 64}),
                "target_height": ("INT", {"default": 1024, "min": 512, "max": 2048, "step": 64}),
                "aesthetic_score": ("FLOAT", {"default": 6.5, "min": 1.0, "max": 10.0, "step": 0.5}),
                **cls.get_common_optional_inputs(),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "conditioning_params", "info")
    FUNCTION = "build_sdxl_prompt"

    def build_sdxl_prompt(
        self,
        concept: str,
        style: str,
        composition: str,
        lighting: str,
        detail_level: str,
        custom_details: str = "",
        artist_references: str = "",
        negative_prompt: bool = True,
        include_conditioning_params: bool = True,
        target_width: int = 1024,
        target_height: int = 1024,
        aesthetic_score: float = 6.5,
        temperature: float = 0.75,
        server_url: str = "http://localhost:1234",
        model: str = ""
    ) -> Tuple[str, str, str, str]:
        """Build SDXL-optimized prompt with proper structure."""
        
        info_parts = self._init_info("SDXL Prompt Builder", "🎨")
        self._add_model_info(info_parts, server_url)
        
        info_parts.append(f"🎭 Style: {style}")
        info_parts.append(f"📐 Composition: {composition}")
        info_parts.append(f"💡 Lighting: {lighting}")
        info_parts.append(f"🔍 Detail: {detail_level}")
        
        # Build comprehensive instruction
        instruction = f"""Create an optimized SDXL image generation prompt based on this concept: "{concept}"

REQUIREMENTS:
Style: {style}
Composition: {composition}
Lighting: {lighting}
Detail Level: {detail_level}
{f"Additional Requirements: {custom_details}" if custom_details else ""}
{f"Artist References: {artist_references}" if artist_references else ""}

SDXL BEST PRACTICES TO FOLLOW:
1. SDXL understands natural language - write detailed descriptions like explaining to a person
2. Can also use comma-separated keywords - both approaches work
3. Start with main subject and key descriptors
4. Include specific composition and framing details ({composition})
5. Specify lighting ({lighting}) and atmosphere
6. Add mood and emotional tone
7. Reference artists or styles if provided
8. Use quality tags: "highly detailed", "8k resolution", "professional", "award winning"
9. Keep keyword weights between (1.0-1.4) - SDXL is very sensitive
10. Negative prompts should be MINIMAL - only what you actively want to avoid

STRUCTURE YOUR OUTPUT:
- Subject first with vivid details (colors, materials, textures, features)
- Composition and perspective ({composition})
- Lighting specifics ({lighting})
- Mood and atmosphere
- Style or artist references
- Quality boosters at end

OUTPUT FORMAT:
Return a JSON object with:
{{
  "positive_prompt": "detailed natural language description OR comma-separated keywords with rich visual details",
  "negative_prompt": "{"minimal list of specific things to avoid" if negative_prompt else ""}",
  "clip_g": "core description focusing on overall concept and composition",
  "clip_l": "detailed description with specific visual attributes and style"
}}

EXAMPLE (natural language):
{{
  "positive_prompt": "A professional photograph of an elven warrior woman with flowing silver hair, piercing blue eyes, wearing ornate leather armor with silver filigree, standing confidently in an ancient forest clearing, dramatic sunlight filtering through ancient trees, cinematic lighting, highly detailed, award winning photography",
  "negative_prompt": "blurry, low quality, deformed",
  "clip_g": "elven warrior woman in ancient forest, cinematic lighting",
  "clip_l": "flowing silver hair, piercing blue eyes, ornate leather armor with silver filigree, dramatic sunlight, highly detailed photography"
}}

EXAMPLE (keyword style):
{{
  "positive_prompt": "beautiful woman warrior, (elven features:1.2), silver flowing hair, blue eyes, ornate leather armor, silver filigree details, ancient forest background, (dramatic lighting:1.1), sunlight through trees, highly detailed, 8k, professional photography, sharp focus, award winning",
  "negative_prompt": "ugly, deformed, low quality",
  "clip_g": "elven warrior, ancient forest, dramatic composition",
  "clip_l": "detailed armor, leather texture, silver decorations, forest environment, professional quality"
}}

Generate the prompt now using {detail_level} detail level and {style} style."""

        # Build messages
        messages = [
            {
                "role": "system",
                "content": "You are an expert at creating SDXL prompts. You understand ComfyUI's dual CLIP encoder system (CLIP-G for global composition, CLIP-L for local details). IMPORTANT: Always return valid JSON with positive_prompt, negative_prompt, clip_g, and clip_l fields as specified in the instructions."
            },
            {
                "role": "user",
                "content": instruction
            }
        ]
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 600,
            "stream": False
        }
        
        if model:
            payload["model"] = model
        
        try:
            info_parts.append("⏳ Generating prompt...")
            
            url = f"{server_url}/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            generated = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not generated:
                error_msg = "❌ Error: No response from LM Studio"
                info_parts.append(error_msg)
                return (error_msg, "", "", "\n".join(info_parts))
            
            # Parse JSON response
            try:
                import re
                json_match = re.search(r'\{.*\}', generated, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    positive = parsed.get("positive_prompt", "").strip()
                    negative = parsed.get("negative_prompt", "").strip() if negative_prompt else ""
                    clip_g = parsed.get("clip_g", positive).strip()
                    clip_l = parsed.get("clip_l", positive).strip()
                else:
                    # Fallback
                    positive = generated.strip()
                    negative = ""
                    clip_g = positive
                    clip_l = positive
            except (json.JSONDecodeError, Exception) as e:
                # Fallback to text
                positive = generated.strip()
                negative = ""
                clip_g = positive
                clip_l = positive
                info_parts.append(f"⚠️ JSON parse fallback: {str(e)}")
            
            # Build conditioning parameters JSON
            conditioning_params = ""
            if include_conditioning_params:
                params = {
                    "width": target_width,
                    "height": target_height,
                    "target_width": target_width,
                    "target_height": target_height,
                    "crop_w": 0,
                    "crop_h": 0,
                    "aesthetic_score": aesthetic_score,
                    "clip_g": clip_g,
                    "clip_l": clip_l
                }
                conditioning_params = json.dumps(params, indent=2)
            
            # Success info
            pos_words = len(positive.split())
            info_parts.append("✅ Prompt generated!")
            info_parts.append(f"📊 Positive: {pos_words} words")
            if negative:
                neg_words = len(negative.split(','))
                info_parts.append(f"🚫 Negative: {neg_words} elements")
            if include_conditioning_params:
                info_parts.append(f"📐 Size: {target_width}×{target_height}")
                info_parts.append(f"⭐ Aesthetic: {aesthetic_score}")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return (positive, negative, conditioning_params, "\n".join(info_parts))
            
        except (urllib.error.URLError, ConnectionRefusedError, OSError) as e:
            error_msg = f"❌ Connection Error\n\n{str(e)}"
            info_parts.append("❌ Connection failed")
            return (error_msg, "", "", "\n".join(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return (error_msg, "", "", "\n".join(info_parts))


__all__ = ["LMStudioSDXLPromptBuilder"]
