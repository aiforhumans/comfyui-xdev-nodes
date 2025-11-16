"""LM Studio Prompt Enhancer Node

Takes a simple prompt and expands it into a detailed image generation prompt.
"""

from typing import Any, Dict, Tuple

try:
    from .lm_base_node import LMStudioPromptBaseNode
    from .lm_utils import (
        LMStudioConnectionError,
        LMStudioAPIError,
        ErrorFormatter,
        JSONParser,
    )
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode
    from lm_utils import (
        LMStudioConnectionError,
        LMStudioAPIError,
        ErrorFormatter,
        JSONParser,
    )


class LMStudioPromptEnhancer(LMStudioPromptBaseNode):
    """Enhance simple prompts into detailed image generation prompts."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "simple_prompt": ("STRING", {"default": "a cat", "multiline": True}),
                "style": (["realistic", "artistic", "fantasy", "sci-fi", "anime", "cinematic", "none"], {"default": "none"}),
                "detail_level": (["minimal", "moderate", "detailed", "very detailed"], {"default": "detailed"}),
                "temperature": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "additional_details": ("STRING", {"default": "", "multiline": True}),
                "negative_prompt": ("BOOLEAN", {"default": False}),
                "response_format": (["text", "json"], {"default": "text"}),
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "model": ("STRING", {"default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "info")
    FUNCTION = "enhance_prompt"

    def enhance_prompt(
        self,
        simple_prompt: str,
        style: str = "none",
        detail_level: str = "detailed",
        temperature: float = 0.8,
        additional_details: str = "",
        negative_prompt: bool = False,
        response_format: str = "text",
        server_url: str = "http://localhost:1234",
        model: str = ""
    ) -> Tuple[str, str, str]:
        """Enhance a simple prompt using LM Studio with detailed feedback."""
        
        # Initialize info output using base class
        info_parts = self._init_info("SDXL Prompt Enhancer", "✨")
        info_parts.append(f"📝 Input: '{simple_prompt[:50]}{'...' if len(simple_prompt) > 50 else ''}''")
        
        # Add model info using base class
        self._add_model_info(info_parts, server_url)
        
        # Add enhancement parameters using base class
        params = {
            "detail_level": detail_level,
            "temperature": temperature,
            "format": response_format,
        }
        if style != "none":
            params["style"] = style
        if additional_details:
            params["additional_details"] = "provided"
        self._add_params_info(info_parts, **params)
        
        # Build enhancement instruction
        style_instruction = f" in {style} style" if style != "none" else ""
        detail_instruction = {
            "minimal": "Keep it concise with only essential details.",
            "moderate": "Add moderate details about composition and lighting.",
            "detailed": "Include detailed descriptions of composition, lighting, mood, and visual elements.",
            "very detailed": "Create an extremely detailed prompt with comprehensive descriptions of every visual aspect."
        }[detail_level]
        
        # Build instruction based on format
        if response_format == "json":
            instruction = f"""Transform this simple concept into a professional SDXL image generation prompt{style_instruction}.

Simple concept: {simple_prompt}
{f"Additional requirements: {additional_details}" if additional_details else ""}

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
  "negative_prompt": "{"minimal list of specific things to avoid" if negative_prompt else ""}"
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
        else:
            instruction = f"""Transform this simple concept into a professional SDXL image generation prompt{style_instruction}.

Simple concept: {simple_prompt}
{f"Additional requirements: {additional_details}" if additional_details else ""}

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

            if negative_prompt:
                instruction += "\n\nAlso provide a negative prompt with common issues to avoid (same comma-separated format)."
        
        # Build request
        messages = [
            {
                "role": "system",
                "content": "You are an expert at writing SDXL prompts. SDXL understands natural language better than SD 1.5 - you can describe images in detail with full sentences OR use comma-separated keywords. Both work well. When using keyword weights like (keyword:1.2), keep weights between 1.0-1.4 as SDXL is very sensitive. Focus on vivid, specific visual details. For negative prompts, keep them minimal - only include what you actively want to avoid (like 'cartoon' for photos, or 'blurry, low quality')."
            },
            {
                "role": "user",
                "content": instruction
            }
        ]
        
        try:
            info_parts.append("⏳ Enhancing prompt...")
            
            # Build messages using base class helper
            sys_prompt = "You are an expert at writing SDXL prompts. SDXL understands natural language better than SD 1.5 - you can describe images in detail with full sentences OR use comma-separated keywords. Both work well. When using keyword weights like (keyword:1.2), keep weights between 1.0-1.4 as SDXL is very sensitive. Focus on vivid, specific visual details. For negative prompts, keep them minimal - only include what you actively want to avoid (like 'cartoon' for photos, or 'blurry, low quality')."
            
            messages = self._build_messages(
                prompt=instruction,
                system_prompt=sys_prompt,
                response_format="text"  # Don't use response_format param, use instruction-based JSON
            )
            
            # Make API request using base class helper
            generated = self._make_api_request(
                server_url=server_url,
                messages=messages,
                temperature=temperature,
                max_tokens=400,
                response_format="text",  # Don't use response_format param
                model=model,
                timeout=60
            )
            
            # Parse response based on format
            neg_prompt = ""
            
            if response_format == "json":
                # Use JSONParser utility for robust parsing
                parsed = JSONParser.parse_response(generated, expected_keys=["positive_prompt", "negative_prompt"])
                enhanced = JSONParser.extract_field(parsed, "positive_prompt", generated.strip())
                neg_prompt = JSONParser.extract_field(parsed, "negative_prompt", "")
            else:
                # Text format - try to split positive and negative if requested
                if negative_prompt:
                    # Look for negative prompt section
                    lines = generated.strip().split('\n')
                    enhanced_lines = []
                    neg_lines = []
                    in_negative = False
                    
                    for line in lines:
                        line_lower = line.lower()
                        if any(marker in line_lower for marker in ['negative prompt:', 'negative:', 'avoid:']):
                            in_negative = True
                            continue
                        
                        if in_negative:
                            neg_lines.append(line.strip())
                        else:
                            enhanced_lines.append(line.strip())
                    
                    enhanced = ', '.join([l for l in enhanced_lines if l])
                    neg_prompt = ', '.join([l for l in neg_lines if l])
                    
                    # Clean up any remaining labels
                    enhanced = enhanced.replace('Positive prompt:', '').replace('Positive:', '').strip()
                    neg_prompt = neg_prompt.replace('Negative prompt:', '').replace('Negative:', '').replace('Avoid:', '').strip()
                else:
                    enhanced = generated.strip()
            
            # Clean up the prompts - remove quotes, extra commas
            enhanced = enhanced.strip('"\' ').replace(',,', ',').strip(', ')
            neg_prompt = neg_prompt.strip('"\' ').replace(',,', ',').strip(', ')
            
            # Success info using base class
            info_parts.append("✅ Enhancement complete!")
            pos_words = len(enhanced.split(','))
            info_parts.append(f"📊 Positive: {pos_words} elements, {len(enhanced)} chars")
            if neg_prompt:
                neg_words = len(neg_prompt.split(','))
                info_parts.append(f"🚫 Negative: {neg_words} elements, {len(neg_prompt)} chars")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return (enhanced, neg_prompt, self._format_info(info_parts))
            
        except LMStudioConnectionError as e:
            error_msg = ErrorFormatter.format_connection_error(server_url, str(e))
            info_parts.append("❌ Connection failed")
            return (error_msg, "", self._format_info(info_parts))
            
        except LMStudioAPIError as e:
            error_msg = ErrorFormatter.format_api_error(str(e))
            info_parts.append("❌ API error")
            return (error_msg, "", self._format_info(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return (error_msg, "", self._format_info(info_parts))