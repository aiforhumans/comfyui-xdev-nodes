"""
LM Studio SDXL Refiner Prompt Generator Node

Generates optimized prompts for SDXL refiner stage.
Focuses on detail enhancement, quality improvement, and aesthetic refinement.
Based on research: SDXL refiner best practices, stage2strength, aesthetic scores
"""

import json
import re
import urllib.error
import urllib.request

try:
    from .lm_base_node import LMStudioPromptBaseNode
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode


class LMStudioRefinerPromptGenerator(LMStudioPromptBaseNode):
    """
    Generates SDXL refiner-optimized prompts for the second stage of generation.
    Emphasizes details, quality, and aesthetic refinement.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": ""}),
                "refiner_focus": (["detail_enhancement", "quality_boost", "style_consistency", "fix_artifacts", "balanced"], {"default": "balanced"}),
                "aesthetic_target": (["commercial", "artistic", "photorealistic", "cinematic", "painterly", "editorial"], {"default": "commercial"}),
                "refiner_strength": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 1.0, "step": 0.05}),
            },
            "optional": {
                **cls.get_common_optional_inputs(),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("refiner_prompt", "emphasis_tags", "refiner_params", "info")
    FUNCTION = "generate_refiner_prompt"
    
    def generate_refiner_prompt(self, base_prompt: str, refiner_focus: str, aesthetic_target: str,
                               refiner_strength: float, temperature: float = 0.4, 
                               server_url: str = "http://localhost:1234", model: str = "") -> tuple:
        """Generate refiner-optimized prompt."""
        
        if not base_prompt.strip():
            return ("", "", "", "⚠️ Error: Base prompt is required")
        
        # Map refiner focus to instructions
        focus_instructions = {
            "detail_enhancement": """PRIORITY: Add fine details, textures, and micro-features
- Enhance surface details (skin pores, fabric weave, wood grain)
- Add texture descriptors (rough, smooth, glossy, matte)
- Include material properties (metallic sheen, translucency)
- Emphasize intricate details (fine hair strands, small ornaments)""",
            
            "quality_boost": """PRIORITY: Maximize output quality and technical excellence
- Add quality tags: sharp focus, highly detailed, 8k resolution
- Include technical terms: professional, award-winning, masterpiece
- Emphasize clarity: crystal clear, pristine, flawless
- Professional photography terms when applicable""",
            
            "style_consistency": """PRIORITY: Maintain and refine the artistic style
- Reinforce core style elements from base prompt
- Add style-specific descriptors
- Enhance artistic technique descriptors
- Maintain color palette and mood consistency""",
            
            "fix_artifacts": """PRIORITY: Correct common generation issues
- Add descriptors to fix anatomy (correct proportions, proper hands)
- Clarity and coherence (well-defined, clear features)
- Avoid deformations (smooth, natural, anatomically correct)
- Proper lighting and exposure""",
            
            "balanced": """PRIORITY: Balanced refinement across all aspects
- Moderate detail enhancement
- Quality improvements
- Style consistency
- Subtle artifact correction"""
        }
        
        # Map aesthetic target to score and descriptors
        aesthetic_map = {
            "commercial": (6.5, "polished, professional, appealing, market-ready"),
            "artistic": (7.0, "artistic, creative, expressive, gallery-quality"),
            "photorealistic": (6.0, "realistic, authentic, lifelike, true-to-life"),
            "cinematic": (7.5, "cinematic, dramatic, epic, film-quality"),
            "painterly": (7.0, "painterly, artistic, brushwork, fine art"),
            "editorial": (6.5, "editorial, sophisticated, refined, magazine-quality")
        }
        
        aesthetic_score, aesthetic_descriptors = aesthetic_map[aesthetic_target]
        
        focus_instruction = focus_instructions[refiner_focus]
        
        # Build system prompt based on research
        system_prompt = f"""You are an SDXL refiner prompt specialist. The refiner is a second-stage model that enhances details and quality.

REFINER CHARACTERISTICS (from research):
- Operates as image-to-image on base model latents
- Specializes in denoising small noise levels
- Focuses on high-quality data refinement
- Uses aesthetic score guidance
- Typical strength: 0.15 (current: {refiner_strength})

CURRENT SETTINGS:
- Focus: {refiner_focus}
- Aesthetic Target: {aesthetic_target} (score: {aesthetic_score})
- Strength: {refiner_strength}

{focus_instruction}

AESTHETIC TARGET DESCRIPTORS:
{aesthetic_descriptors}

REFINER PROMPT GUIDELINES:
1. Keep core subject/concept from base prompt
2. Add detail-oriented descriptors
3. Include quality and finish tags
4. Avoid major compositional changes
5. Emphasize refinement over transformation
6. Use aesthetic descriptors matching target
7. Add technical photography/art terms

IMPORTANT: Always respond with valid JSON format.

Respond with JSON:
{{
  "refiner_prompt": "the refiner-optimized prompt",
  "emphasis_tags": "key emphasis tags for refiner stage (comma-separated)",
  "added_elements": ["element1", "element2"],
  "refinement_strategy": "brief strategy explanation",
  "aesthetic_score": {aesthetic_score},
  "negative_aesthetic_score": 2.5
}}"""
        
        user_prompt = f"""Create a refiner prompt based on this base prompt:

{base_prompt}

Focus: {refiner_focus}
Aesthetic Target: {aesthetic_target}
Strength: {refiner_strength}

Generate the refiner-optimized prompt."""
        
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
            json_match = re.search(r'\{[^{}]*"refiner_prompt"[^{}]*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    
                    refiner_prompt = parsed.get("refiner_prompt", base_prompt)
                    emphasis_tags = parsed.get("emphasis_tags", "")
                    added_elements = parsed.get("added_elements", [])
                    refinement_strategy = parsed.get("refinement_strategy", "")
                    aesthetic_score_val = parsed.get("aesthetic_score", aesthetic_score)
                    negative_aesthetic_score = parsed.get("negative_aesthetic_score", 2.5)
                    
                    # Build refiner parameters JSON
                    refiner_params = json.dumps({
                        "aesthetic_score": aesthetic_score_val,
                        "negative_aesthetic_score": negative_aesthetic_score,
                        "stage2strength": refiner_strength,
                        "orig_width": 1024,
                        "orig_height": 1024,
                        "target_width": 1024,
                        "target_height": 1024,
                        "crop_coords_top": 0,
                        "crop_coords_left": 0
                    }, indent=2)
                    
                    # Build info string
                    info = f"""Focus: {refiner_focus}
Aesthetic Target: {aesthetic_target}
Aesthetic Score: {aesthetic_score_val}
Negative Aesthetic: {negative_aesthetic_score}
Refiner Strength: {refiner_strength}
Temperature: {temperature}

Refinement Strategy:
{refinement_strategy}

Added Elements:
{', '.join(added_elements) if added_elements else 'None'}"""
                    
                    return (refiner_prompt, emphasis_tags, refiner_params, info)
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            refiner_prompt = response_text.strip()
            emphasis_tags = f"{aesthetic_target} aesthetic, refined details"
            
            refiner_params = json.dumps({
                "aesthetic_score": aesthetic_score,
                "negative_aesthetic_score": 2.5,
                "stage2strength": refiner_strength
            }, indent=2)
            
            info = f"""Focus: {refiner_focus}
Aesthetic Target: {aesthetic_target}
Refiner Strength: {refiner_strength}
⚠️ JSON parsing failed, using text response"""
            
            return (refiner_prompt, emphasis_tags, refiner_params, info)
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No details"
            error_msg = f"❌ HTTP Error {e.code}: {e.reason}\n{error_body}"
            print(f"[LM Studio Refiner Prompt Generator] {error_msg}")
            return (base_prompt, "", "{}", error_msg)
        
        except urllib.error.URLError as e:
            error_msg = f"❌ Connection Error: {e.reason}\nIs LM Studio running at {lm_studio_url}?"
            print(f"[LM Studio Refiner Prompt Generator] {error_msg}")
            return (base_prompt, "", "{}", error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"[LM Studio Refiner Prompt Generator] {error_msg}")
            return (base_prompt, "", "{}", error_msg)


NODE_CLASS_MAPPINGS = {
    "XDEVLMStudioRefinerPromptGenerator": LMStudioRefinerPromptGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVLMStudioRefinerPromptGenerator": "LM Studio SDXL Refiner Prompt Generator",
}
