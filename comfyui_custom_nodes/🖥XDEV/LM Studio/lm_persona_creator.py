"""LM Studio Persona Creator Node

Create detailed, consistent character/persona descriptions for image generation.
"""

try:
    from .lm_base_node import LMStudioPromptBaseNode
    from .lm_utils import ErrorFormatter, JSONParser
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode
    from lm_utils import ErrorFormatter, JSONParser

from typing import Any


class LMStudioPersonaCreator(LMStudioPromptBaseNode):
    """Generate detailed character/persona descriptions with consistency."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "character_concept": ("STRING", {"default": "a cyberpunk hacker", "multiline": True}),
                "gender": (["female", "male", "non-binary", "other", "unspecified"], {"default": "female"}),
                "age_range": (["child", "teen", "young adult", "adult", "middle-aged", "elderly", "unspecified"], {"default": "young adult"}),
                "ethnicity": (["unspecified", "caucasian", "african", "asian", "hispanic", "middle eastern", "mixed", "fantasy race"], {"default": "unspecified"}),
                "body_type": (["slim", "athletic", "average", "muscular", "curvy", "plus-size", "unspecified"], {"default": "athletic"}),
            },
            "optional": {
                "specific_features": ("STRING", {"default": "", "multiline": True, "tooltip": "Hair, eyes, distinctive features"}),
                "clothing_style": ("STRING", {"default": "", "multiline": True, "tooltip": "Outfit description"}),
                "personality_traits": ("STRING", {"default": "", "multiline": True, "tooltip": "Personality that affects appearance"}),
                "occupation_role": ("STRING", {"default": "", "tooltip": "Job or role that influences look"}),
                "setting_context": ("STRING", {"default": "", "tooltip": "World/setting they belong to"}),
                "consistency_seed": ("STRING", {"default": "", "tooltip": "Unique ID for character consistency"}),
                "generate_negative": ("BOOLEAN", {"default": True}),
                **cls.get_common_optional_inputs(),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("persona_description", "negative_prompt", "consistency_reference", "info")
    FUNCTION = "create_persona"

    def create_persona(
        self,
        character_concept: str,
        gender: str,
        age_range: str,
        ethnicity: str,
        body_type: str,
        specific_features: str = "",
        clothing_style: str = "",
        personality_traits: str = "",
        occupation_role: str = "",
        setting_context: str = "",
        consistency_seed: str = "",
        generate_negative: bool = True,
        temperature: float = 0.6,
        server_url: str = "http://localhost:1234",
        model: str = ""
    ) -> tuple[str, str, str, str]:
        """Create detailed persona description."""
        
        info_parts = self._init_info("Persona Creator", "👤")
        self._add_model_info(info_parts, server_url)
        
        info_parts.append(f"👤 {gender.title()} {age_range}")
        info_parts.append(f"💪 {body_type.title()}")
        if occupation_role:
            info_parts.append(f"💼 {occupation_role}")
        
        # Build comprehensive persona instruction
        instruction = f"""Create a detailed character/persona description for AI image generation.

CORE IDENTITY:
Concept: {character_concept}
Gender: {gender}
Age: {age_range}
{f"Ethnicity: {ethnicity}" if ethnicity != "unspecified" else ""}
Body Type: {body_type}

ADDITIONAL DETAILS:
{f"Specific Features: {specific_features}" if specific_features else ""}
{f"Clothing: {clothing_style}" if clothing_style else ""}
{f"Personality: {personality_traits}" if personality_traits else ""}
{f"Occupation: {occupation_role}" if occupation_role else ""}
{f"Setting: {setting_context}" if setting_context else ""}
{f"Consistency Seed: {consistency_seed} (use this to maintain character identity)" if consistency_seed else ""}

CHARACTER DESCRIPTION STRUCTURE:
1. **Physical Appearance** (head to toe):
   - Facial Features: Face shape, skin tone, complexion
   - Eyes: Color, shape, expression
   - Hair: Color, length, style, texture
   - Body: Build, posture, distinctive features
   - Distinctive Marks: Scars, tattoos, unique features

2. **Clothing & Accessories**:
   - Main outfit with materials and colors
   - Layering and details
   - Footwear
   - Accessories (jewelry, glasses, weapons, props)
   - How clothing reflects personality/role

3. **Expression & Pose**:
   - Default facial expression
   - Body language and stance
   - Typical poses or gestures
   - Emotional range

4. **Style & Atmosphere**:
   - Overall aesthetic (realistic, anime, painterly, etc.)
   - Lighting that suits the character
   - Mood and atmosphere
   - Color palette

CONSISTENCY GUIDELINES:
- Be VERY specific about unchanging features (exact eye color, hair style, distinctive marks)
- Include measurements/proportions where relevant
- Mention specific colors using descriptive names (e.g., "deep emerald green" not just "green")
- Reference consistent clothing items if character has signature look
- Note any props or accessories that are always present

OUTPUT FORMAT:
Return JSON with:
{{
  "full_description": "Complete natural language description suitable for image generation",
  "key_features": "Comma-separated essential identifying features",
  "clothing": "Detailed clothing description",
  "expression_pose": "Default expression and pose",
  "negative_prompt": "Things to avoid that would break character consistency",
  "consistency_tokens": "Unique descriptors for this character (for use across multiple generations)"
}}

EXAMPLE OUTPUT:
{{
  "full_description": "A confident young woman in her mid-20s with an athletic build, standing 5'7\" tall. She has a heart-shaped face with high cheekbones, smooth olive-toned skin, and striking almond-shaped emerald green eyes with long dark lashes. Her hair is long, wavy, dark auburn with subtle copper highlights, usually worn half-up with loose strands framing her face. She wears a fitted black leather jacket over a charcoal grey turtleneck, dark blue fitted jeans with strategic rips at the knees, and black combat boots with silver buckles. Around her neck is a thin silver chain with a small compass pendant. She typically stands with confident posture, one hand in jacket pocket, slight smirk on her lips, exuding quiet determination.",
  "key_features": "heart-shaped face, olive skin, emerald green almond eyes, long wavy dark auburn hair with copper highlights, athletic build, 5'7\"",
  "clothing": "black leather jacket, charcoal grey turtleneck, dark blue ripped jeans, black combat boots with silver buckles, silver compass necklace",
  "expression_pose": "confident stance, hand in pocket, slight smirk, determined expression, direct eye contact",
  "negative_prompt": "different eye color, blonde hair, different clothing, shy expression, poor posture, overweight, masculine features",
  "consistency_tokens": "auburn_emerald_compass_bearer, athletic_leather_jacket_woman, confident_compass_wearer"
}}

Generate the detailed persona description now."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert character designer and AI prompt engineer. You create detailed, consistent character descriptions perfect for AI image generation. Focus on specific, visual details that can be consistently reproduced. IMPORTANT: Always respond with valid JSON format as specified in the user instructions."
            },
            {
                "role": "user",
                "content": instruction
            }
        ]
        
        try:
            info_parts.append("⏳ Creating persona...")
            
            # Use base class API request method
            result = self._make_api_request(server_url, messages, temperature, 800, model)
            generated = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not generated:
                error_msg = "❌ Error: No response from LM Studio"
                info_parts.append(error_msg)
                return (error_msg, "", "", self._format_info(info_parts))
            
            # Parse JSON using utility
            parsed = JSONParser.parse_response(generated)
            
            if parsed:
                full_desc = parsed.get("full_description", "").strip()
                key_features = parsed.get("key_features", "").strip()
                clothing = parsed.get("clothing", "").strip()
                expression = parsed.get("expression_pose", "").strip()
                negative = parsed.get("negative_prompt", "").strip() if generate_negative else ""
                consistency_tokens = parsed.get("consistency_tokens", "").strip()
                
                # Build complete description
                persona_desc = full_desc
                
                # Build consistency reference
                consistency_ref = "PERSONA IDENTITY:\n"
                consistency_ref += f"Seed: {consistency_seed if consistency_seed else 'none'}\n"
                consistency_ref += f"Tokens: {consistency_tokens}\n\n"
                consistency_ref += f"KEY FEATURES:\n{key_features}\n\n"
                consistency_ref += f"CLOTHING:\n{clothing}\n\n"
                consistency_ref += f"EXPRESSION/POSE:\n{expression}"
            else:
                # Fallback to raw text
                persona_desc = generated.strip()
                negative = ""
                consistency_ref = f"Concept: {character_concept}"
                info_parts.append("⚠️ JSON parse fallback")
            
            # Success info
            word_count = len(persona_desc.split())
            info_parts.append("✅ Persona created!")
            info_parts.append(f"📊 Description: {word_count} words")
            if negative:
                info_parts.append(f"🚫 Negative: {len(negative.split(','))} elements")
            if consistency_seed:
                info_parts.append(f"🔑 Seed: {consistency_seed}")
            
            return (persona_desc, negative, consistency_ref, self._format_info(info_parts))
            
        except Exception as e:
            error_info = ErrorFormatter.format_api_error(e, "create persona")
            info_parts.append("❌ Failed")
            return (error_info, "", "", self._format_info(info_parts))


__all__ = ["LMStudioPersonaCreator"]
