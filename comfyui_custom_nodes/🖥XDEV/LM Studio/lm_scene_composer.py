"""LM Studio Scene Composer Node

Builds complex multi-layer scene descriptions with proper spatial relationships.
Generates foreground, midground, background, lighting, and atmosphere.
Based on research: A1111 prompt weighting, composable diffusion, spatial descriptors
"""

import re
import urllib.error
import urllib.request

try:
    from .lm_base_node import LMStudioPromptBaseNode
    from .lm_utils import JSONParser
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode
    from lm_utils import JSONParser


class LMStudioSceneComposer(LMStudioPromptBaseNode):
    """
    Composes complex scenes with layered elements using LM Studio AI.
    Generates separate descriptions for foreground, midground, background, lighting, and atmosphere.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "subject": ("STRING", {"multiline": True, "default": ""}),
                "environment_type": (["outdoor", "indoor", "fantasy", "sci-fi", "abstract", "natural", "urban", "rural"], {"default": "outdoor"}),
                "time_of_day": (["morning", "midday", "afternoon", "sunset", "dusk", "night", "dawn", "any"], {"default": "any"}),
                "weather_atmosphere": (["clear", "cloudy", "foggy", "rainy", "stormy", "snowy", "misty", "dramatic", "any"], {"default": "any"}),
                "mood": (["peaceful", "dramatic", "mysterious", "energetic", "melancholic", "epic", "intimate", "tense", "joyful", "any"], {"default": "any"}),
                "composition_style": (["centered", "rule_of_thirds", "dynamic", "symmetrical", "asymmetrical", "leading_lines", "framing", "any"], {"default": "any"}),
                "detail_level": (["minimal", "moderate", "high", "very_high"], {"default": "high"}),
            },
            "optional": {
                **cls.get_common_optional_inputs(),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("full_scene", "foreground", "midground", "background", "lighting", "atmosphere", "info")
    FUNCTION = "compose_scene"
    
    def compose_scene(self, subject: str, environment_type: str, time_of_day: str, 
                     weather_atmosphere: str, mood: str, composition_style: str,
                     detail_level: str, temperature: float = 0.7, server_url: str = "http://localhost:1234", 
                     model: str = "") -> tuple:
        """Compose a multi-layered scene description."""
        
        if not subject.strip():
            return ("", "", "", "", "", "", "⚠️ Error: Subject is required")
        
        # Map detail level to description
        detail_map = {
            "minimal": "basic descriptions, focus on essential elements only",
            "moderate": "balanced detail, include key visual elements",
            "high": "detailed descriptions with specific visual characteristics",
            "very_high": "highly detailed descriptions with textures, materials, and fine elements"
        }
        
        detail_instruction = detail_map[detail_level]
        
        # Build system prompt with research-backed techniques
        system_prompt = f"""You are an expert scene composition specialist for AI image generation. Create a detailed, layered scene description optimized for stable diffusion models.

RESEARCH-BACKED TECHNIQUES:
1. SPATIAL LAYERING: Clearly separate foreground, midground, and background elements
2. PROMPT WEIGHTING: Use emphasis for important elements - (element:1.1) to (element:1.3)
3. SPATIAL DESCRIPTORS: Use "in the foreground", "in the background", "behind", "in front of"
4. COMPOSABLE DIFFUSION: Structure elements so they can be combined with AND operator
5. LIGHTING & ATMOSPHERE: Define separately for better control

SCENE PARAMETERS:
- Environment: {environment_type}
- Time of Day: {time_of_day}
- Weather/Atmosphere: {weather_atmosphere}
- Mood: {mood}
- Composition: {composition_style}
- Detail Level: {detail_instruction}

INSTRUCTIONS:
- Create vivid, specific descriptions for each layer
- Maintain spatial coherence (what's in front vs behind)
- Ensure lighting matches time of day and weather
- Atmosphere should support the mood
- Use professional photography/art terminology
- Include quality tags appropriate for detail level

IMPORTANT: Always respond with valid JSON format.

Respond with JSON:
{{
  "foreground": "detailed foreground description with emphasis tags",
  "midground": "detailed midground description",
  "background": "detailed background description",
  "lighting": "lighting setup and quality",
  "atmosphere": "atmospheric effects and mood elements",
  "full_scene": "complete unified scene description combining all layers",
  "composition_notes": "brief notes on spatial relationships"
}}"""
        
        user_prompt = f"""Create a scene composition for:

SUBJECT: {subject}

Requirements:
- Environment: {environment_type}
- Time: {time_of_day}
- Weather: {weather_atmosphere}
- Mood: {mood}
- Composition Style: {composition_style}

Generate the layered scene description with proper spatial relationships and emphasis."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Use base class API request
            result = self._make_api_request(server_url, messages, temperature, 1500, model)
            response_text = result['choices'][0]['message']['content']
            
            # Parse JSON using utility
            parsed = JSONParser.parse_response(response_text)
            
            if parsed:
                foreground = parsed.get("foreground", "")
                midground = parsed.get("midground", "")
                background = parsed.get("background", "")
                lighting = parsed.get("lighting", "")
                atmosphere = parsed.get("atmosphere", "")
                full_scene = parsed.get("full_scene", "")
                composition_notes = parsed.get("composition_notes", "")
                
                # Build info string
                info = f"""Environment: {environment_type}
Time: {time_of_day}
Weather: {weather_atmosphere}
Mood: {mood}
Composition: {composition_style}
Detail Level: {detail_level}
Temperature: {temperature}

Composition Notes:
{composition_notes}"""
                
                return (full_scene, foreground, midground, background, lighting, atmosphere, info)
            
            # Fallback: try to extract sections from text
            full_scene = response_text.strip()
            
            # Simple extraction attempts
            foreground = self._extract_section(response_text, ["foreground", "front", "closest"])
            midground = self._extract_section(response_text, ["midground", "middle", "center"])
            background = self._extract_section(response_text, ["background", "behind", "distant"])
            lighting = self._extract_section(response_text, ["lighting", "light", "illumination"])
            atmosphere = self._extract_section(response_text, ["atmosphere", "mood", "ambiance"])
            
            info = f"""Environment: {environment_type}
Time: {time_of_day}
Weather: {weather_atmosphere}
Mood: {mood}
Composition: {composition_style}
Detail Level: {detail_level}
⚠️ JSON parsing failed, using text extraction"""
            
            return (full_scene, foreground, midground, background, lighting, atmosphere, info)
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No details"
            error_msg = f"❌ HTTP Error {e.code}: {e.reason}\n{error_body}"
            print(f"[LM Studio Scene Composer] {error_msg}")
            return ("", "", "", "", "", "", error_msg)
        
        except urllib.error.URLError as e:
            error_msg = f"❌ Connection Error: {e.reason}\nIs LM Studio running at {server_url}?"
            print(f"[LM Studio Scene Composer] {error_msg}")
            return ("", "", "", "", "", "", error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"[LM Studio Scene Composer] {error_msg}")
            return ("", "", "", "", "", "", error_msg)
    
    def _extract_section(self, text: str, keywords: list) -> str:
        """Extract a section from text based on keywords."""
        text_lower = text.lower()
        
        for keyword in keywords:
            # Look for patterns like "Foreground: description"
            pattern = rf'{keyword}[:\s]+([^\n]+(?:\n(?![A-Z][a-z]+:)[^\n]+)*)'
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""


NODE_CLASS_MAPPINGS = {
    "XDEVLMStudioSceneComposer": LMStudioSceneComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVLMStudioSceneComposer": "LM Studio Scene Composer",
}
