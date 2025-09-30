"""
Modular Style and Persona Management System for XDev Framework
Professional style libraries, persona profiles, and character building tools
"""

import json
import random
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin
from ...categories import NodeCategories

@dataclass
class StyleProfile:
    """Complete style profile with all attributes"""
    name: str
    category: str
    description: str
    visual_style: str
    color_palette: str
    lighting: str
    composition: str
    mood: str
    techniques: List[str] = field(default_factory=list)
    influences: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    quality_descriptors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PersonaProfile:
    """Comprehensive persona profile for character generation"""
    name: str
    age_range: str
    gender: str
    ethnicity: str
    personality: str
    occupation: str
    appearance: Dict[str, str] = field(default_factory=dict)
    clothing_style: str = ""
    expressions: List[str] = field(default_factory=list)
    poses: List[str] = field(default_factory=list)
    settings: List[str] = field(default_factory=list)
    backstory: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class XDEV_StyleLibrary(ValidationMixin):
    """
    Comprehensive style library with presets for photography, art, and rendering styles.
    Includes modular style components that can be mixed and matched.
    """
    
    DISPLAY_NAME = "Style Library Manager (XDev)"
    
    # Comprehensive style library
    _STYLE_LIBRARY = {
        "photography": {
            "portrait": StyleProfile(
                name="Portrait Photography",
                category="photography",
                description="Professional portrait photography with natural lighting",
                visual_style="realistic, professional portrait",
                color_palette="natural skin tones, soft colors",
                lighting="soft natural lighting, studio lighting",
                composition="rule of thirds, centered subject",
                mood="professional, approachable",
                techniques=["shallow depth of field", "bokeh", "professional lighting"],
                influences=["Annie Leibovitz", "Peter Hurley"],
                keywords=["portrait", "headshot", "professional", "natural"],
                quality_descriptors=["sharp focus", "professional quality", "studio lighting"]
            ),
            "landscape": StyleProfile(
                name="Landscape Photography",
                category="photography",
                description="Stunning landscape photography with dramatic lighting",
                visual_style="realistic landscape, wide angle",
                color_palette="vibrant natural colors, golden hour tones",
                lighting="golden hour, dramatic lighting, natural light",
                composition="wide angle, leading lines, rule of thirds",
                mood="serene, majestic, inspiring",
                techniques=["HDR", "long exposure", "wide angle lens"],
                influences=["Ansel Adams", "Marc Adamus"],
                keywords=["landscape", "nature", "scenic", "outdoor"],
                quality_descriptors=["breathtaking", "pristine", "award-winning"]
            ),
            "street": StyleProfile(
                name="Street Photography",
                category="photography",
                description="Candid street photography capturing authentic moments",
                visual_style="photojournalistic, candid, authentic",
                color_palette="urban colors, high contrast",
                lighting="available light, dramatic shadows",
                composition="dynamic angles, decisive moment",
                mood="authentic, urban, energetic",
                techniques=["candid capture", "fast shutter", "available light"],
                influences=["Henri Cartier-Bresson", "Vivian Maier"],
                keywords=["street", "candid", "urban", "documentary"],
                quality_descriptors=["authentic", "compelling", "decisive moment"]
            )
        },
        "art": {
            "impressionist": StyleProfile(
                name="Impressionist Painting",
                category="art",
                description="Impressionist style with loose brushstrokes and light effects",
                visual_style="impressionist painting, loose brushstrokes",
                color_palette="light pastels, vibrant colors, broken color",
                lighting="natural light, dappled sunlight",
                composition="loose composition, emphasis on light",
                mood="peaceful, atmospheric, luminous",
                techniques=["visible brushstrokes", "plein air", "color mixing"],
                influences=["Claude Monet", "Pierre-Auguste Renoir"],
                keywords=["impressionist", "painterly", "atmospheric"],
                quality_descriptors=["masterful", "luminous", "expressive"]
            ),
            "digital_art": StyleProfile(
                name="Digital Art",
                category="art",
                description="Modern digital art with clean lines and vibrant colors",
                visual_style="digital artwork, clean lines, modern",
                color_palette="vibrant digital colors, gradient effects",
                lighting="dramatic digital lighting, glow effects",
                composition="modern composition, digital effects",
                mood="futuristic, dynamic, creative",
                techniques=["digital painting", "vector graphics", "3D rendering"],
                influences=["concept art", "game art", "digital illustration"],
                keywords=["digital", "modern", "artistic", "creative"],
                quality_descriptors=["polished", "professional", "stunning"]
            ),
            "oil_painting": StyleProfile(
                name="Oil Painting",
                category="art",
                description="Classical oil painting with rich colors and textures",
                visual_style="oil painting, classical technique",
                color_palette="rich oil colors, warm earth tones",
                lighting="classical lighting, chiaroscuro",
                composition="classical composition, balanced",
                mood="timeless, elegant, sophisticated",
                techniques=["oil painting", "glazing", "impasto"],
                influences=["Renaissance masters", "baroque painters"],
                keywords=["oil painting", "classical", "traditional"],
                quality_descriptors=["masterpiece", "museum quality", "timeless"]
            )
        },
        "rendering": {
            "photorealistic": StyleProfile(
                name="Photorealistic 3D",
                category="rendering",
                description="Photorealistic 3D rendering with perfect lighting",
                visual_style="photorealistic 3D render, hyperrealistic",
                color_palette="accurate color reproduction",
                lighting="physically accurate lighting, global illumination",
                composition="professional composition, perfect framing",
                mood="clean, precise, perfect",
                techniques=["ray tracing", "global illumination", "subsurface scattering"],
                influences=["architectural visualization", "product rendering"],
                keywords=["3D render", "photorealistic", "CGI"],
                quality_descriptors=["flawless", "hyperrealistic", "technically perfect"]
            ),
            "stylized": StyleProfile(
                name="Stylized 3D",
                category="rendering",
                description="Stylized 3D rendering with artistic flair",
                visual_style="stylized 3D, artistic rendering",
                color_palette="stylized colors, artistic palette",
                lighting="artistic lighting, stylized shadows",
                composition="dynamic composition, artistic angles",
                mood="playful, artistic, creative",
                techniques=["toon shading", "stylized lighting", "artistic textures"],
                influences=["animation studios", "game art"],
                keywords=["stylized", "artistic", "animated"],
                quality_descriptors=["charming", "artistic", "well-crafted"]
            )
        }
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        # Flatten style categories for UI
        style_options = []
        for category, styles in cls._STYLE_LIBRARY.items():
            for style_name in styles.keys():
                style_options.append(f"{category}_{style_name}")
        
        return {
            "required": {
                "style_preset": (style_options + ["custom"], {"default": "photography_portrait", "tooltip": "Select style preset"}),
                "blend_mode": (["replace", "blend", "enhance"], {"default": "replace", "tooltip": "How to apply the style"}),
            },
            "optional": {
                "custom_style": ("STRING", {"default": "", "multiline": True, "tooltip": "Custom style description"}),
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Style intensity"}),
                "focus_aspect": (["all", "visual", "lighting", "composition", "mood"], {"default": "all", "tooltip": "Focus on specific aspect"}),
                "additional_keywords": ("STRING", {"default": "", "tooltip": "Additional style keywords"}),
                "quality_level": (["standard", "high", "premium", "masterpiece"], {"default": "high", "tooltip": "Quality enhancement level"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("style_prompt", "style_description", "technical_details", "metadata_json")
    FUNCTION = "apply_style"
    CATEGORY = f"{NodeCategories.PROMPTS}/Style"
    DESCRIPTION = "Comprehensive style library with presets for photography, art, and rendering"
    
    @performance_monitor("style_application")
    @cached_operation(ttl=300)
    def apply_style(self, style_preset, blend_mode, custom_style="", intensity=1.0,
                   focus_aspect="all", additional_keywords="", quality_level="high", validate_input=True):
        
        if validate_input and style_preset == "custom":
            validation = self.validate_string_input(custom_style, "custom_style")
            if not validation["valid"]:
                return ("", f"Error: {validation['error']}", "", "")
        
        try:
            # Get style profile
            if style_preset == "custom":
                # Create custom style profile
                style_profile = StyleProfile(
                    name="Custom Style",
                    category="custom",
                    description=custom_style,
                    visual_style=custom_style,
                    color_palette="",
                    lighting="",
                    composition="",
                    mood=""
                )
            else:
                category, style_name = style_preset.split("_", 1)
                style_profile = self._STYLE_LIBRARY[category][style_name]
            
            # Build style prompt based on focus and intensity
            style_prompt = self._build_style_prompt(style_profile, focus_aspect, intensity, additional_keywords, quality_level)
            
            # Generate technical details
            technical_details = self._generate_technical_details(style_profile, intensity)
            
            # Create metadata
            metadata = {
                "style_name": style_profile.name,
                "category": style_profile.category,
                "intensity": intensity,
                "focus_aspect": focus_aspect,
                "quality_level": quality_level,
                "techniques": style_profile.techniques,
                "influences": style_profile.influences
            }
            
            metadata_json = json.dumps(metadata, indent=2)
            
            return (style_prompt, style_profile.description, technical_details, metadata_json)
            
        except Exception as e:
            return ("", f"Error: {str(e)}", "", "")
    
    def _build_style_prompt(self, profile: StyleProfile, focus: str, intensity: float, 
                           additional_keywords: str, quality_level: str) -> str:
        """Build complete style prompt"""
        components = []
        
        # Base visual style
        if focus in ["all", "visual"]:
            components.append(profile.visual_style)
        
        # Color palette
        if focus in ["all", "visual"] and profile.color_palette:
            components.append(profile.color_palette)
        
        # Lighting
        if focus in ["all", "lighting"] and profile.lighting:
            components.append(profile.lighting)
        
        # Composition
        if focus in ["all", "composition"] and profile.composition:
            components.append(profile.composition)
        
        # Mood
        if focus in ["all", "mood"] and profile.mood:
            components.append(profile.mood)
        
        # Keywords
        if profile.keywords:
            keyword_count = max(1, int(len(profile.keywords) * intensity))
            components.extend(profile.keywords[:keyword_count])
        
        # Quality descriptors based on level
        quality_map = {
            "standard": profile.quality_descriptors[:1],
            "high": profile.quality_descriptors[:2],
            "premium": profile.quality_descriptors + ["award-winning"],
            "masterpiece": profile.quality_descriptors + ["masterpiece", "award-winning", "gallery worthy"]
        }
        
        if quality_level in quality_map:
            components.extend(quality_map[quality_level])
        
        # Additional keywords
        if additional_keywords.strip():
            components.append(additional_keywords.strip())
        
        # Apply intensity weighting if needed
        if intensity != 1.0 and intensity > 0.7:
            # Add emphasis to key terms
            base_prompt = ", ".join(components)
            if intensity > 1.2:
                return f"({base_prompt}:{intensity:.1f})"
            else:
                return base_prompt
        else:
            return ", ".join(components)
    
    def _generate_technical_details(self, profile: StyleProfile, intensity: float) -> str:
        """Generate technical implementation details"""
        details = f"Style: {profile.name}\\n"
        details += f"Category: {profile.category}\\n"
        details += f"Intensity: {intensity:.1f}\\n\\n"
        
        if profile.techniques:
            details += f"Techniques: {', '.join(profile.techniques)}\\n"
        
        if profile.influences:
            details += f"Influences: {', '.join(profile.influences)}\\n"
        
        # Implementation suggestions
        details += f"\\nImplementation:\\n"
        if profile.category == "photography":
            details += "• Use with photorealistic models\\n"
            details += "• Consider camera/lens specifications\\n"
        elif profile.category == "art":
            details += "• Works well with artistic models\\n"
            details += "• Consider adding medium specifications\\n"
        elif profile.category == "rendering":
            details += "• Ideal for 3D/CGI workflows\\n"
            details += "• Consider technical rendering parameters\\n"
        
        return details

class XDEV_PersonaBuilder(ValidationMixin):
    """
    Advanced character and persona builder with comprehensive personality and appearance profiles.
    Creates detailed character descriptions for consistent character generation.
    """
    
    DISPLAY_NAME = "Persona Builder (XDev)"
    
    # Character attribute libraries
    _PERSONALITY_TRAITS = {
        "positive": ["confident", "charismatic", "friendly", "optimistic", "creative", "intelligent", "compassionate"],
        "neutral": ["calm", "focused", "observant", "practical", "reserved", "analytical", "independent"],
        "complex": ["mysterious", "complex", "introspective", "passionate", "determined", "unconventional"]
    }
    
    _OCCUPATIONS = {
        "creative": ["artist", "designer", "photographer", "writer", "musician", "architect"],
        "professional": ["doctor", "lawyer", "engineer", "teacher", "scientist", "business executive"],
        "service": ["chef", "barista", "nurse", "social worker", "fitness trainer", "travel guide"],
        "technical": ["programmer", "data scientist", "researcher", "technician", "analyst"]
    }
    
    _CLOTHING_STYLES = {
        "casual": "casual clothes, jeans, t-shirt, comfortable style",
        "professional": "business attire, suit, professional clothing, formal wear",
        "creative": "artistic clothing, unique style, creative fashion, bohemian",
        "athletic": "athletic wear, sportswear, fitness clothing, active style",
        "elegant": "elegant attire, sophisticated clothing, refined style",
        "vintage": "vintage clothing, retro style, classic fashion",
        "urban": "urban fashion, street style, modern casual, trendy"
    }
    
    _EXPRESSIONS = [
        "gentle smile", "confident expression", "thoughtful look", "friendly demeanor",
        "serious expression", "warm smile", "intense gaze", "peaceful expression",
        "determined look", "creative spark in eyes", "wise expression", "joyful smile"
    ]
    
    _POSES = [
        "standing confidently", "sitting relaxed", "arms crossed", "hands on hips",
        "leaning against wall", "walking stride", "thoughtful pose", "dynamic stance",
        "casual sitting", "professional posture", "creative pose", "action pose"
    ]
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "character_name": ("STRING", {"default": "", "tooltip": "Character name or identifier"}),
                "age_category": (["child", "teenager", "young_adult", "adult", "middle_aged", "elderly"], {"default": "adult", "tooltip": "Age category"}),
                "gender": (["male", "female", "non-binary", "unspecified"], {"default": "unspecified", "tooltip": "Gender identity"}),
                "personality_type": (list(cls._PERSONALITY_TRAITS.keys()), {"default": "positive", "tooltip": "Personality category"}),
            },
            "optional": {
                "ethnicity": ("STRING", {"default": "", "tooltip": "Ethnic background (optional)"}),
                "occupation_category": (list(cls._OCCUPATIONS.keys()) + ["custom"], {"default": "professional", "tooltip": "Occupation type"}),
                "custom_occupation": ("STRING", {"default": "", "tooltip": "Custom occupation"}),
                "clothing_style": (list(cls._CLOTHING_STYLES.keys()), {"default": "casual", "tooltip": "Clothing style"}),
                "hair_color": ("STRING", {"default": "", "tooltip": "Hair color"}),
                "hair_style": ("STRING", {"default": "", "tooltip": "Hair style"}),
                "eye_color": ("STRING", {"default": "", "tooltip": "Eye color"}),
                "build": (["slim", "average", "athletic", "muscular", "curvy", "heavy", "petite"], {"default": "average", "tooltip": "Body build"}),
                "height": (["short", "average", "tall"], {"default": "average", "tooltip": "Height category"}),
                "expression_override": ("STRING", {"default": "", "tooltip": "Specific expression"}),
                "pose_override": ("STRING", {"default": "", "tooltip": "Specific pose"}),
                "backstory": ("STRING", {"default": "", "multiline": True, "tooltip": "Character backstory"}),
                "randomize_details": ("BOOLEAN", {"default": False, "tooltip": "Randomize unspecified details"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_prompt", "character_description", "appearance_details", "persona_json")
    FUNCTION = "build_persona"
    CATEGORY = f"{NodeCategories.PROMPTS}/Character"
    DESCRIPTION = "Advanced character and persona builder with comprehensive profiles"
    
    @performance_monitor("persona_building")
    @cached_operation(ttl=300)
    def build_persona(self, character_name, age_category, gender, personality_type,
                     ethnicity="", occupation_category="professional", custom_occupation="",
                     clothing_style="casual", hair_color="", hair_style="", eye_color="",
                     build="average", height="average", expression_override="", pose_override="",
                     backstory="", randomize_details=False, validate_input=True):
        
        if validate_input and not character_name.strip():
            return ("", "Error: Character name is required", "", "")
        
        try:
            # Build persona profile
            persona = self._build_persona_profile(
                character_name, age_category, gender, personality_type, ethnicity,
                occupation_category, custom_occupation, clothing_style,
                hair_color, hair_style, eye_color, build, height,
                expression_override, pose_override, backstory, randomize_details
            )
            
            # Generate prompts and descriptions
            character_prompt = self._generate_character_prompt(persona)
            character_description = self._generate_character_description(persona)
            appearance_details = self._generate_appearance_details(persona)
            
            # Create JSON profile
            persona_json = json.dumps(asdict(persona), indent=2)
            
            return (character_prompt, character_description, appearance_details, persona_json)
            
        except Exception as e:
            return ("", f"Error: {str(e)}", "", "")
    
    def _build_persona_profile(self, name, age_category, gender, personality_type, ethnicity,
                              occupation_category, custom_occupation, clothing_style,
                              hair_color, hair_style, eye_color, build, height,
                              expression_override, pose_override, backstory, randomize_details) -> PersonaProfile:
        """Build complete persona profile"""
        
        # Determine occupation
        if custom_occupation.strip():
            occupation = custom_occupation.strip()
        elif occupation_category in self._OCCUPATIONS:
            occupations = self._OCCUPATIONS[occupation_category]
            occupation = random.choice(occupations) if randomize_details else occupations[0]
        else:
            occupation = "professional"
        
        # Build appearance dictionary
        appearance = {}
        
        if hair_color or randomize_details:
            appearance["hair_color"] = hair_color or random.choice(["brown", "black", "blonde", "red", "gray"])
        
        if hair_style or randomize_details:
            appearance["hair_style"] = hair_style or random.choice(["short", "medium length", "long", "curly", "straight"])
        
        if eye_color or randomize_details:
            appearance["eye_color"] = eye_color or random.choice(["brown", "blue", "green", "hazel", "gray"])
        
        appearance["build"] = build
        appearance["height"] = height
        
        # Select personality traits
        if personality_type in self._PERSONALITY_TRAITS:
            traits = self._PERSONALITY_TRAITS[personality_type]
            if randomize_details:
                selected_traits = random.sample(traits, min(3, len(traits)))
            else:
                selected_traits = traits[:3]
            personality = ", ".join(selected_traits)
        else:
            personality = "balanced personality"
        
        # Select expression and pose
        expression = expression_override or (random.choice(self._EXPRESSIONS) if randomize_details else self._EXPRESSIONS[0])
        pose = pose_override or (random.choice(self._POSES) if randomize_details else self._POSES[0])
        
        # Create persona profile
        persona = PersonaProfile(
            name=name,
            age_range=age_category.replace("_", " "),
            gender=gender if gender != "unspecified" else "",
            ethnicity=ethnicity,
            personality=personality,
            occupation=occupation,
            appearance=appearance,
            clothing_style=self._CLOTHING_STYLES.get(clothing_style, clothing_style),
            expressions=[expression],
            poses=[pose],
            settings=[],  # Could be expanded
            backstory=backstory,
            metadata={
                "created_with": "XDev Persona Builder",
                "randomized": randomize_details,
                "personality_type": personality_type,
                "occupation_category": occupation_category
            }
        )
        
        return persona
    
    def _generate_character_prompt(self, persona: PersonaProfile) -> str:
        """Generate concise character prompt for image generation"""
        prompt_parts = []
        
        # Age and gender
        if persona.age_range and persona.gender:
            prompt_parts.append(f"{persona.age_range} {persona.gender}")
        elif persona.age_range:
            prompt_parts.append(persona.age_range)
        elif persona.gender:
            prompt_parts.append(persona.gender)
        
        # Ethnicity
        if persona.ethnicity:
            prompt_parts.append(persona.ethnicity)
        
        # Physical appearance
        appearance_parts = []
        if persona.appearance.get("hair_color") and persona.appearance.get("hair_style"):
            appearance_parts.append(f"{persona.appearance['hair_color']} {persona.appearance['hair_style']} hair")
        elif persona.appearance.get("hair_color"):
            appearance_parts.append(f"{persona.appearance['hair_color']} hair")
        elif persona.appearance.get("hair_style"):
            appearance_parts.append(f"{persona.appearance['hair_style']} hair")
        
        if persona.appearance.get("eye_color"):
            appearance_parts.append(f"{persona.appearance['eye_color']} eyes")
        
        if persona.appearance.get("build") != "average":
            appearance_parts.append(f"{persona.appearance['build']} build")
        
        if appearance_parts:
            prompt_parts.append(", ".join(appearance_parts))
        
        # Clothing
        if persona.clothing_style:
            prompt_parts.append(persona.clothing_style)
        
        # Expression
        if persona.expressions:
            prompt_parts.append(persona.expressions[0])
        
        # Pose
        if persona.poses:
            prompt_parts.append(persona.poses[0])
        
        return ", ".join(prompt_parts)
    
    def _generate_character_description(self, persona: PersonaProfile) -> str:
        """Generate detailed character description"""
        description = f"CHARACTER: {persona.name}\\n"
        description += f"{'='*40}\\n\\n"
        
        description += f"BASIC INFO:\\n"
        description += f"• Age: {persona.age_range}\\n"
        if persona.gender:
            description += f"• Gender: {persona.gender}\\n"
        if persona.ethnicity:
            description += f"• Ethnicity: {persona.ethnicity}\\n"
        description += f"• Occupation: {persona.occupation}\\n"
        description += f"• Personality: {persona.personality}\\n\\n"
        
        description += f"APPEARANCE:\\n"
        for key, value in persona.appearance.items():
            if value:
                description += f"• {key.replace('_', ' ').title()}: {value}\\n"
        
        description += f"• Clothing Style: {persona.clothing_style}\\n\\n"
        
        if persona.expressions:
            description += f"EXPRESSIONS: {', '.join(persona.expressions)}\\n"
        
        if persona.poses:
            description += f"POSES: {', '.join(persona.poses)}\\n"
        
        if persona.backstory:
            description += f"\\nBACKSTORY:\\n{persona.backstory}\\n"
        
        return description
    
    def _generate_appearance_details(self, persona: PersonaProfile) -> str:
        """Generate focused appearance details for consistent generation"""
        details = []
        
        # Physical characteristics
        if persona.appearance.get("hair_color") and persona.appearance.get("hair_style"):
            details.append(f"{persona.appearance['hair_color']} {persona.appearance['hair_style']} hair")
        
        if persona.appearance.get("eye_color"):
            details.append(f"{persona.appearance['eye_color']} eyes")
        
        if persona.appearance.get("build") and persona.appearance["build"] != "average":
            details.append(f"{persona.appearance['build']} build")
        
        if persona.appearance.get("height") and persona.appearance["height"] != "average":
            details.append(f"{persona.appearance['height']} height")
        
        # Add personality reflection in appearance
        if "confident" in persona.personality:
            details.append("confident posture")
        if "creative" in persona.personality:
            details.append("creative flair")
        if "friendly" in persona.personality:
            details.append("approachable demeanor")
        
        return ", ".join(details)


class XDEV_StyleMixer(ValidationMixin):
    """
    Advanced style mixing system that blends multiple styles with precise control.
    Allows for creative style combinations and custom style formulas.
    """
    
    DISPLAY_NAME = "Style Mixer (XDev)"
    
    # Mixing algorithms
    _MIXING_MODES = {
        "blend": "Smooth blending of styles with weighted influence",
        "layered": "Apply styles in layers with composition rules",
        "alternating": "Alternate between styles for different aspects",
        "fusion": "Deep fusion creating new hybrid style",
        "contrast": "Contrasting styles for dramatic effect",
        "evolution": "Evolve from one style to another"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        # Get available styles from StyleLibrary
        style_options = []
        for category, styles in XDEV_StyleLibrary._STYLE_LIBRARY.items():
            for style_name in styles.keys():
                style_options.append(f"{category}_{style_name}")
        
        return {
            "required": {
                "primary_style": (style_options, {"default": "photography_portrait", "tooltip": "Primary base style"}),
                "secondary_style": (style_options, {"default": "art_impressionist", "tooltip": "Secondary style to mix"}),
                "mixing_mode": (list(cls._MIXING_MODES.keys()), {"default": "blend", "tooltip": "How to combine styles"}),
                "mix_ratio": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1, "tooltip": "Balance between styles (0=primary, 1=secondary)"}),
            },
            "optional": {
                "tertiary_style": (["none"] + style_options, {"default": "none", "tooltip": "Optional third style"}),
                "tertiary_influence": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.1, "tooltip": "Influence of tertiary style"}),
                "focus_elements": (["all", "visual", "lighting", "composition", "mood", "technical"], {"default": "all", "tooltip": "Which elements to mix"}),
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Overall mixing intensity"}),
                "preserve_coherence": ("BOOLEAN", {"default": True, "tooltip": "Maintain style coherence"}),
                "experimental_mode": ("BOOLEAN", {"default": False, "tooltip": "Enable experimental combinations"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("mixed_style_prompt", "style_formula", "mixing_analysis", "style_metadata")
    FUNCTION = "mix_styles"
    CATEGORY = f"{NodeCategories.PROMPTS}/Style"
    DESCRIPTION = "Advanced style mixing system for creative style combinations"
    
    @performance_monitor("style_mixing")
    @cached_operation(ttl=300)
    def mix_styles(self, primary_style, secondary_style, mixing_mode, mix_ratio,
                  tertiary_style="none", tertiary_influence=0.2, focus_elements="all",
                  intensity=1.0, preserve_coherence=True, experimental_mode=False, validate_input=True):
        
        try:
            # Get style profiles
            primary_profile = self._get_style_profile(primary_style)
            secondary_profile = self._get_style_profile(secondary_style)
            tertiary_profile = self._get_style_profile(tertiary_style) if tertiary_style != "none" else None
            
            # Mix styles based on mode
            mixed_prompt = self._mix_style_prompts(
                primary_profile, secondary_profile, tertiary_profile,
                mixing_mode, mix_ratio, tertiary_influence, focus_elements,
                intensity, preserve_coherence, experimental_mode
            )
            
            # Generate style formula
            style_formula = self._generate_style_formula(
                primary_style, secondary_style, tertiary_style,
                mix_ratio, tertiary_influence, mixing_mode
            )
            
            # Generate mixing analysis
            mixing_analysis = self._analyze_style_mix(
                primary_profile, secondary_profile, tertiary_profile,
                mixing_mode, mix_ratio, preserve_coherence
            )
            
            # Create metadata
            metadata = {
                "primary_style": primary_style,
                "secondary_style": secondary_style,
                "tertiary_style": tertiary_style,
                "mixing_mode": mixing_mode,
                "mix_ratio": mix_ratio,
                "tertiary_influence": tertiary_influence,
                "focus_elements": focus_elements,
                "intensity": intensity,
                "experimental": experimental_mode
            }
            
            return (mixed_prompt, style_formula, mixing_analysis, json.dumps(metadata, indent=2))
            
        except Exception as e:
            return ("", f"Error: {str(e)}", "", "")
    
    def _get_style_profile(self, style_key: str) -> Optional[StyleProfile]:
        """Get style profile from library"""
        if style_key == "none":
            return None
        
        category, style_name = style_key.split("_", 1)
        return XDEV_StyleLibrary._STYLE_LIBRARY[category][style_name]
    
    def _mix_style_prompts(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile],
                          mode: str, ratio: float, tertiary_influence: float, focus: str,
                          intensity: float, preserve_coherence: bool, experimental: bool) -> str:
        """Mix style prompts based on specified mode"""
        
        if mode == "blend":
            return self._blend_styles(primary, secondary, tertiary, ratio, tertiary_influence, focus, intensity)
        elif mode == "layered":
            return self._layer_styles(primary, secondary, tertiary, ratio, focus, intensity)
        elif mode == "alternating":
            return self._alternate_styles(primary, secondary, tertiary, focus, intensity)
        elif mode == "fusion":
            return self._fuse_styles(primary, secondary, tertiary, ratio, intensity, experimental)
        elif mode == "contrast":
            return self._contrast_styles(primary, secondary, focus, intensity)
        elif mode == "evolution":
            return self._evolve_styles(primary, secondary, ratio, intensity)
        else:
            return self._blend_styles(primary, secondary, tertiary, ratio, tertiary_influence, focus, intensity)
    
    def _blend_styles(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile],
                     ratio: float, tertiary_influence: float, focus: str, intensity: float) -> str:
        """Smooth style blending"""
        components = []
        
        # Calculate weights
        primary_weight = 1.0 - ratio
        secondary_weight = ratio
        tertiary_weight = tertiary_influence if tertiary else 0.0
        
        # Normalize weights
        total_weight = primary_weight + secondary_weight + tertiary_weight
        if total_weight > 0:
            primary_weight /= total_weight
            secondary_weight /= total_weight
            tertiary_weight /= total_weight
        
        # Mix visual styles
        if focus in ["all", "visual"]:
            visual_parts = []
            if primary_weight > 0.3:
                visual_parts.append(f"({primary.visual_style}:{primary_weight:.1f})")
            if secondary_weight > 0.3:
                visual_parts.append(f"({secondary.visual_style}:{secondary_weight:.1f})")
            if tertiary and tertiary_weight > 0.2:
                visual_parts.append(f"({tertiary.visual_style}:{tertiary_weight:.1f})")
            components.extend(visual_parts)
        
        # Mix other elements
        for element in ["color_palette", "lighting", "composition", "mood"]:
            if focus in ["all", element.split("_")[0]]:
                element_parts = []
                primary_val = getattr(primary, element, "")
                secondary_val = getattr(secondary, element, "")
                
                if primary_val and primary_weight > 0.3:
                    element_parts.append(primary_val)
                if secondary_val and secondary_weight > 0.3:
                    element_parts.append(secondary_val)
                if tertiary and tertiary_weight > 0.2:
                    tertiary_val = getattr(tertiary, element, "")
                    if tertiary_val:
                        element_parts.append(tertiary_val)
                
                if element_parts:
                    components.extend(element_parts)
        
        result = ", ".join(components)
        
        # Apply intensity
        if intensity > 1.2:
            return f"({result}:{intensity:.1f})"
        elif intensity < 0.8:
            return f"({result}:{intensity:.1f})"
        else:
            return result
    
    def _layer_styles(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile],
                     ratio: float, focus: str, intensity: float) -> str:
        """Layer styles with composition rules"""
        layers = []
        
        # Base layer (primary)
        layers.append(primary.visual_style)
        
        # Secondary layer based on ratio
        if ratio > 0.3:
            if focus in ["all", "lighting"]:
                layers.append(secondary.lighting)
            if focus in ["all", "mood"]:
                layers.append(secondary.mood)
        
        if ratio > 0.6:
            layers.append(secondary.visual_style)
        
        # Tertiary accents
        if tertiary and ratio > 0.7:
            layers.append(tertiary.color_palette)
        
        return ", ".join(filter(None, layers))
    
    def _alternate_styles(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile],
                         focus: str, intensity: float) -> str:
        """Alternate styles for different aspects"""
        components = []
        
        # Alternate assignments
        components.append(primary.visual_style)  # Primary visual
        components.append(secondary.lighting)   # Secondary lighting
        components.append(primary.composition)  # Primary composition
        components.append(secondary.mood)       # Secondary mood
        
        if tertiary:
            components.append(tertiary.color_palette)  # Tertiary color
        
        return ", ".join(filter(None, components))
    
    def _fuse_styles(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile],
                    ratio: float, intensity: float, experimental: bool) -> str:
        """Deep fusion creating hybrid style"""
        fusion_components = []
        
        # Create hybrid descriptions
        if experimental:
            fusion_components.append(f"hybrid of {primary.name} and {secondary.name}")
        
        # Combine keywords creatively
        primary_keywords = primary.keywords[:3]
        secondary_keywords = secondary.keywords[:3]
        
        # Interleave keywords
        mixed_keywords = []
        for i in range(max(len(primary_keywords), len(secondary_keywords))):
            if i < len(primary_keywords):
                mixed_keywords.append(primary_keywords[i])
            if i < len(secondary_keywords):
                mixed_keywords.append(secondary_keywords[i])
        
        fusion_components.extend(mixed_keywords[:5])
        
        # Add fusion-specific terms
        fusion_components.extend([
            "creative fusion",
            "artistic blend",
            f"{primary.category}-{secondary.category} style"
        ])
        
        return ", ".join(fusion_components)
    
    def _contrast_styles(self, primary: StyleProfile, secondary: StyleProfile, focus: str, intensity: float) -> str:
        """Create contrasting style effects"""
        contrasts = []
        
        contrasts.append(f"contrast between {primary.visual_style} and {secondary.visual_style}")
        contrasts.append(f"{primary.mood} meets {secondary.mood}")
        
        if primary.lighting and secondary.lighting:
            contrasts.append(f"dramatic contrast of {primary.lighting} and {secondary.lighting}")
        
        return ", ".join(contrasts)
    
    def _evolve_styles(self, primary: StyleProfile, secondary: StyleProfile, ratio: float, intensity: float) -> str:
        """Evolve from one style to another"""
        if ratio < 0.3:
            return f"{primary.visual_style}, evolving towards {secondary.name}"
        elif ratio > 0.7:
            return f"evolved from {primary.name} to {secondary.visual_style}"
        else:
            return f"transitioning from {primary.visual_style} to {secondary.visual_style}"
    
    def _generate_style_formula(self, primary: str, secondary: str, tertiary: str,
                               ratio: float, tertiary_influence: float, mode: str) -> str:
        """Generate style mixing formula"""
        formula = f"STYLE FORMULA:\\n"
        formula += f"Mode: {mode}\\n"
        formula += f"Primary ({(1-ratio)*100:.0f}%): {primary}\\n"
        formula += f"Secondary ({ratio*100:.0f}%): {secondary}\\n"
        
        if tertiary != "none":
            formula += f"Tertiary ({tertiary_influence*100:.0f}%): {tertiary}\\n"
        
        formula += f"\\nMixing Ratio: {1-ratio:.1f}:{ratio:.1f}"
        if tertiary != "none":
            formula += f":{tertiary_influence:.1f}"
        
        return formula
    
    def _analyze_style_mix(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile],
                          mode: str, ratio: float, preserve_coherence: bool) -> str:
        """Analyze the style mixing results"""
        analysis = f"STYLE MIXING ANALYSIS:\\n"
        analysis += f"{'='*30}\\n\\n"
        
        analysis += f"Compatibility Score: {self._calculate_compatibility(primary, secondary):.2f}/1.00\\n"
        analysis += f"Coherence Level: {'High' if preserve_coherence else 'Experimental'}\\n"
        analysis += f"Mixing Complexity: {self._assess_complexity(primary, secondary, tertiary, mode)}\\n\\n"
        
        analysis += f"Primary Style Influence: {(1-ratio)*100:.0f}%\\n"
        analysis += f"Secondary Style Influence: {ratio*100:.0f}%\\n"
        
        if tertiary:
            analysis += f"Tertiary Style Influence: {20:.0f}%\\n"
        
        analysis += f"\\nExpected Result: {self._predict_result(primary, secondary, mode, ratio)}"
        
        return analysis
    
    def _calculate_compatibility(self, primary: StyleProfile, secondary: StyleProfile) -> float:
        """Calculate style compatibility score"""
        # Simple compatibility based on category and shared elements
        if primary.category == secondary.category:
            return 0.8
        elif primary.category in ["photography", "rendering"] and secondary.category in ["photography", "rendering"]:
            return 0.6
        elif primary.category == "art" or secondary.category == "art":
            return 0.7
        else:
            return 0.5
    
    def _assess_complexity(self, primary: StyleProfile, secondary: StyleProfile, tertiary: Optional[StyleProfile], mode: str) -> str:
        """Assess mixing complexity"""
        complexity_score = 1
        
        if tertiary:
            complexity_score += 1
        
        if mode in ["fusion", "contrast", "evolution"]:
            complexity_score += 1
        
        if primary.category != secondary.category:
            complexity_score += 1
        
        if complexity_score <= 2:
            return "Simple"
        elif complexity_score <= 3:
            return "Moderate"
        else:
            return "Complex"
    
    def _predict_result(self, primary: StyleProfile, secondary: StyleProfile, mode: str, ratio: float) -> str:
        """Predict mixing result"""
        if mode == "blend" and ratio < 0.3:
            return f"Predominantly {primary.name} with subtle {secondary.name} influences"
        elif mode == "blend" and ratio > 0.7:
            return f"Predominantly {secondary.name} with {primary.name} undertones"
        elif mode == "blend":
            return f"Balanced fusion of {primary.name} and {secondary.name}"
        elif mode == "contrast":
            return f"Dramatic contrast highlighting differences between styles"
        elif mode == "fusion":
            return f"New hybrid style combining best of both approaches"
        else:
            return f"Creative combination using {mode} methodology"


# Node registrations
NODE_CLASS_MAPPINGS = {
    "XDEV_StyleLibrary": XDEV_StyleLibrary,
    "XDEV_PersonaBuilder": XDEV_PersonaBuilder,
    "XDEV_StyleMixer": XDEV_StyleMixer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_StyleLibrary": "Style Library Manager (XDev)",
    "XDEV_PersonaBuilder": "Persona Builder (XDev)",
    "XDEV_StyleMixer": "Style Mixer (XDev)",
}