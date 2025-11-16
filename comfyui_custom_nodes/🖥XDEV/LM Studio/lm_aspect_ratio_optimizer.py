"""
LM Studio SDXL Aspect Ratio Optimizer Node

Optimizes prompts based on target aspect ratio and composition requirements.
Adjusts framing, perspective, and composition keywords based on portrait vs landscape.
Based on research: SDXL dimension handling, composition best practices
"""

import json
import re
import urllib.error
import urllib.request

try:
    from .lm_base_node import LMStudioPromptBaseNode
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode


class LMStudioAspectRatioOptimizer(LMStudioPromptBaseNode):
    """
    Optimizes prompts for specific aspect ratios and SDXL dimensions.
    Adjusts composition, framing, and spatial descriptors accordingly.
    """
    
    # SDXL base ratios from research
    ASPECT_RATIOS = {
        "1:1 (1024x1024)": (1024, 1024),
        "16:9 (1344x768)": (1344, 768),
        "9:16 (768x1344)": (768, 1344),
        "21:9 (1536x640)": (1536, 640),
        "9:21 (640x1536)": (640, 1536),
        "4:3 (1152x896)": (1152, 896),
        "3:4 (896x1152)": (896, 1152),
        "3:2 (1216x832)": (1216, 832),
        "2:3 (832x1216)": (832, 1216),
        "19:13 (1216x832)": (1216, 832),
        "13:19 (832x1216)": (832, 1216),
    }
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": ""}),
                "aspect_ratio": (list(cls.ASPECT_RATIOS.keys()), {"default": "1:1 (1024x1024)"}),
                "optimization_focus": (["composition", "framing", "subject_placement", "all"], {"default": "all"}),
            },
            "optional": {
                **cls.get_common_optional_inputs(),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("optimized_prompt", "composition_guide", "width", "height", "info")
    FUNCTION = "optimize_prompt"
    
    def optimize_prompt(self, base_prompt: str, aspect_ratio: str, optimization_focus: str,
                       temperature: float = 0.5, server_url: str = "http://localhost:1234", model: str = "") -> tuple:
        """Optimize prompt for specific aspect ratio."""
        
        if not base_prompt.strip():
            return ("", "", 1024, 1024, "⚠️ Error: Base prompt is required")
        
        # Get dimensions
        width, height = self.ASPECT_RATIOS[aspect_ratio]
        
        # Determine orientation
        if width > height:
            orientation = "landscape"
            ratio_desc = "wide, horizontal"
        elif height > width:
            orientation = "portrait"
            ratio_desc = "tall, vertical"
        else:
            orientation = "square"
            ratio_desc = "balanced, square"
        
        # Build optimization instructions
        focus_instructions = {
            "composition": "Focus on composition keywords: adjust framing, perspective, camera angle",
            "framing": "Focus on framing: modify shot type (close-up, wide shot, etc.)",
            "subject_placement": "Focus on subject placement: adjust positioning and spatial relationships",
            "all": "Optimize all aspects: composition, framing, subject placement, and spatial keywords"
        }
        
        focus_instruction = focus_instructions[optimization_focus]
        
        # Build system prompt with research findings
        system_prompt = f"""You are an SDXL prompt optimization expert specializing in aspect ratio composition.

TARGET ASPECT RATIO: {aspect_ratio}
Dimensions: {width}x{height}
Orientation: {orientation} ({ratio_desc})

OPTIMIZATION RULES FOR {orientation.upper()}:

{"FOR LANDSCAPE (Wide):" if orientation == "landscape" else ""}
{"- Use: wide shot, panoramic, expansive, sweeping vista" if orientation == "landscape" else ""}
{"- Emphasize: horizontal elements, width, breadth" if orientation == "landscape" else ""}
{"- Composition: rule of thirds horizontally, leading lines" if orientation == "landscape" else ""}
{"- Avoid: vertical emphasis, tall subjects dominating" if orientation == "landscape" else ""}
{"- Camera: wide angle lens, establishing shot" if orientation == "landscape" else ""}

{"FOR PORTRAIT (Tall):" if orientation == "portrait" else ""}
{"- Use: portrait shot, full body, vertical composition" if orientation == "portrait" else ""}
{"- Emphasize: height, vertical elements, standing poses" if orientation == "portrait" else ""}
{"- Composition: centered or rule of thirds vertically" if orientation == "portrait" else ""}
{"- Avoid: wide landscapes, horizontal emphasis" if orientation == "portrait" else ""}
{"- Camera: portrait lens, medium to close-up" if orientation == "portrait" else ""}

{"FOR SQUARE:" if orientation == "square" else ""}
{"- Use: centered composition, symmetrical, balanced" if orientation == "square" else ""}
{"- Emphasize: focal point, radial composition" if orientation == "square" else ""}
{"- Composition: centered, symmetrical, no bias" if orientation == "square" else ""}
{"- Works well: faces, objects, architectural details" if orientation == "square" else ""}

TASK: {focus_instruction}

SDXL CROP PARAMETERS:
- orig_width, orig_height: {width}, {height}
- target_width, target_height: {width}, {height}
- crop_coords_top_left: 0, 0 (no cropping)

IMPORTANT: Always respond with valid JSON format.

Respond with JSON:
{{
  "optimized_prompt": "the aspect-ratio optimized prompt",
  "composition_guide": "specific composition recommendations for this ratio",
  "added_keywords": ["keyword1", "keyword2"],
  "removed_keywords": ["keyword1", "keyword2"],
  "reasoning": "brief explanation of optimizations"
}}"""
        
        user_prompt = f"""Optimize this prompt for {aspect_ratio}:

{base_prompt}

Apply {orientation} orientation optimizations."""
        
        # Build API payload
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "stream": False
        }
        
        if model.strip():
            payload["model"] = model.strip()
        
        lm_studio_url = f"{server_url}/v1/chat/completions"

        try:
            # Make API request
            req = urllib.request.Request(
                lm_studio_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result['choices'][0]['message']['content']
            
            # Parse JSON response
            json_match = re.search(r'\{[^{}]*"optimized_prompt"[^{}]*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    
                    optimized_prompt = parsed.get("optimized_prompt", base_prompt)
                    composition_guide = parsed.get("composition_guide", "")
                    added_keywords = parsed.get("added_keywords", [])
                    removed_keywords = parsed.get("removed_keywords", [])
                    reasoning = parsed.get("reasoning", "")
                    
                    # Build comprehensive composition guide
                    guide = f"""Composition Recommendations:
{composition_guide}

Added Keywords:
{', '.join(added_keywords) if added_keywords else 'None'}

Removed Keywords:
{', '.join(removed_keywords) if removed_keywords else 'None'}

Reasoning:
{reasoning}"""
                    
                    # Build info string
                    info = f"""Aspect Ratio: {aspect_ratio}
Dimensions: {width}x{height}
Orientation: {orientation}
Focus: {optimization_focus}
Temperature: {temperature}
Keywords Added: {len(added_keywords)}
Keywords Removed: {len(removed_keywords)}"""
                    
                    return (optimized_prompt, guide, width, height, info)
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            optimized_prompt = response_text.strip()
            guide = f"Orientation: {orientation}\nOptimize for {ratio_desc} composition"
            info = f"Aspect Ratio: {aspect_ratio}\nDimensions: {width}x{height}\n⚠️ JSON parsing failed"
            
            return (optimized_prompt, guide, width, height, info)
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No details"
            error_msg = f"❌ HTTP Error {e.code}: {e.reason}\n{error_body}"
            print(f"[LM Studio Aspect Ratio Optimizer] {error_msg}")
            return (base_prompt, "", width, height, error_msg)
        
        except urllib.error.URLError as e:
            error_msg = f"❌ Connection Error: {e.reason}\nIs LM Studio running at {lm_studio_url}?"
            print(f"[LM Studio Aspect Ratio Optimizer] {error_msg}")
            return (base_prompt, "", width, height, error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"[LM Studio Aspect Ratio Optimizer] {error_msg}")
            return (base_prompt, "", width, height, error_msg)


NODE_CLASS_MAPPINGS = {
    "XDEVLMStudioAspectRatioOptimizer": LMStudioAspectRatioOptimizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVLMStudioAspectRatioOptimizer": "LM Studio SDXL Aspect Ratio Optimizer",
}
