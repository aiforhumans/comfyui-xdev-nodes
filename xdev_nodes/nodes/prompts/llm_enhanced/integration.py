"""
LLM-Enhanced Prompt Tools for XDev Framework
Advanced prompt building using LLM intelligence and context awareness
"""

import json
import httpx
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, field
from ....performance import performance_monitor, cached_operation
from ....mixins import ValidationMixin 
from ....categories import NodeCategories

# Try to import httpx for LLM integration
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    httpx = None
    HAS_HTTPX = False

class LLMPromptFramework:
    """
    Unified LLM framework for prompt tool enhancement.
    
    Provides shared utilities for integrating LLM capabilities into
    existing prompt tools like PersonBuilder and StyleBuilder.
    """
    
    # Default LLM configurations for different use cases
    _LLM_CONFIGS = {
        "character_generation": {
            "temperature": 0.8,
            "max_tokens": 1024,
            "top_p": 0.9,
            "system_prompt": """You are an expert character designer and storyteller. Generate detailed, consistent character descriptions with rich personalities, physical traits, and backgrounds. Focus on creating believable, engaging characters with depth and authenticity."""
        },
        "style_generation": {
            "temperature": 0.7,
            "max_tokens": 800,
            "top_p": 0.8,
            "system_prompt": """You are a master art director and visual designer. Create detailed, cohesive artistic style descriptions that include medium, composition, lighting, color palette, and aesthetic elements. Ensure styles are practical and achievable."""
        },
        "prompt_enhancement": {
            "temperature": 0.6,
            "max_tokens": 1200,
            "top_p": 0.85,
            "system_prompt": """You are an expert prompt engineer specializing in AI image generation. Enhance and improve prompts by adding relevant details, fixing issues, and ensuring clarity while maintaining the original intent."""
        },
        "contextual_building": {
            "temperature": 0.75,
            "max_tokens": 1500,
            "top_p": 0.88,
            "system_prompt": """You are a creative writing and visual storytelling expert. Build comprehensive, contextually rich prompts that tell complete stories through detailed descriptions, maintaining thematic consistency and emotional depth."""
        }
    }
    
    def __init__(self, server_url: str = "http://localhost:1234", model: str = "local-model"):
        self.server_url = server_url
        self.model = model
        self._client = None
    
    def _get_llm_client(self):
        """Get or create LLM client with graceful fallback."""
        if not HAS_HTTPX:
            return MockLLMClient()
        
        if self._client is None:
            self._client = LMStudioClient()
        return self._client
    
    def enhance_prompt(self, base_prompt: str, enhancement_type: str = "prompt_enhancement", 
                      context: str = "", additional_instructions: str = "") -> Tuple[str, str]:
        """Enhance prompt using LLM capabilities."""
        
        if not HAS_HTTPX:
            return base_prompt, "LLM enhancement not available (httpx not installed)"
        
        try:
            config = self._LLM_CONFIGS.get(enhancement_type, self._LLM_CONFIGS["prompt_enhancement"])
            
            # Build enhancement prompt
            enhancement_prompt = self._build_enhancement_prompt(
                base_prompt, enhancement_type, context, additional_instructions
            )
            
            client = self._get_llm_client()
            
            response = client.generate_response(
                prompt=enhancement_prompt,
                server_url=self.server_url,
                model=self.model,
                system_prompt=config["system_prompt"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                top_p=config["top_p"]
            )
            
            return response, f"Enhanced using {enhancement_type} mode"
            
        except Exception as e:
            return base_prompt, f"Enhancement failed: {str(e)}"
    
    def _build_enhancement_prompt(self, base_prompt: str, enhancement_type: str, 
                                context: str, additional_instructions: str) -> str:
        """Build the enhancement prompt based on type and context."""
        
        prompt_templates = {
            "prompt_enhancement": f"Improve this prompt for AI image generation: '{base_prompt}'",
            "character_generation": f"Create a detailed character based on: '{base_prompt}'",
            "style_generation": f"Develop an artistic style description for: '{base_prompt}'",
            "contextual_building": f"Build a comprehensive, contextual prompt around: '{base_prompt}'"
        }
        
        enhancement_prompt = prompt_templates.get(enhancement_type, prompt_templates["prompt_enhancement"])
        
        if context:
            enhancement_prompt += f"\\n\\nContext: {context}"
        
        if additional_instructions:
            enhancement_prompt += f"\\n\\nAdditional instructions: {additional_instructions}"
        
        return enhancement_prompt

class MockLLMClient:
    """Mock client for when httpx is not available."""
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        return f"Enhanced: {prompt} (mock response - install httpx for real LLM integration)"

class LMStudioClient:
    """Simple LM Studio client for LLM calls."""
    
    def generate_response(self, prompt: str, server_url: str = "http://localhost:1234",
                         model: str = "local-model", system_prompt: str = "",
                         temperature: float = 0.7, max_tokens: int = 1024,
                         top_p: float = 0.9, **kwargs) -> str:
        """Generate response from LM Studio server."""
        
        if not HAS_HTTPX:
            return f"Enhanced: {prompt} (httpx not available)"
        
        try:
            headers = {"Content-Type": "application/json"}
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{server_url}/v1/chat/completions", 
                                     headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"Enhanced: {prompt} (LLM server error: {response.status_code})"
                    
        except Exception as e:
            return f"Enhanced: {prompt} (LLM error: {str(e)})"

class XDEV_LLMPromptAssistant(ValidationMixin):
    """
    Intelligent prompt enhancement node using LLM capabilities.
    
    Features:
    - Context-aware prompt improvement
    - Multiple enhancement modes
    - Original prompt preservation
    - Detailed enhancement reporting
    """
    
    DISPLAY_NAME = "LLM Prompt Assistant (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "base_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Original prompt to enhance with LLM intelligence"
                }),
                "enhancement_mode": (["prompt_enhancement", "character_generation", "style_generation", "contextual_building"], {
                    "default": "prompt_enhancement",
                    "tooltip": "Type of LLM enhancement to apply"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name to use for enhancement"
                })
            },
            "optional": {
                "context": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Additional context for the enhancement"
                }),
                "additional_instructions": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Specific instructions for the LLM"
                }),
                "fallback_on_error": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Return original prompt if LLM enhancement fails"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("enhanced_prompt", "original_prompt", "enhancement_info")
    FUNCTION = "enhance_prompt_with_llm"
    CATEGORY = f"{NodeCategories.PROMPTS}/LLM"
    DESCRIPTION = "Enhance prompts using LLM intelligence with context awareness and multiple enhancement modes"
    
    @performance_monitor("llm_prompt_assistant")
    def enhance_prompt_with_llm(
        self,
        base_prompt: str,
        enhancement_mode: str,
        server_url: str,
        model: str,
        context: str = "",
        additional_instructions: str = "",
        fallback_on_error: bool = True,
        validate_input: bool = True
    ) -> Tuple[str, str, str]:
        """Enhance prompt using LLM intelligence."""
        
        if validate_input:
            if not base_prompt.strip():
                return ("", "", "Error: Base prompt cannot be empty")
        
        try:
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model)
            
            # Enhance the prompt
            enhanced_prompt, enhancement_info = llm_framework.enhance_prompt(
                base_prompt=base_prompt,
                enhancement_type=enhancement_mode,
                context=context,
                additional_instructions=additional_instructions
            )
            
            return (enhanced_prompt, base_prompt, enhancement_info)
            
        except Exception as e:
            error_info = f"LLM enhancement failed: {str(e)}"
            
            if fallback_on_error:
                return (base_prompt, base_prompt, error_info)
            else:
                return ("", base_prompt, error_info)

class XDEV_LLMContextualBuilder(ValidationMixin):
    """
    Smart contextual prompt builder using LLM understanding.
    
    Features:
    - Theme-based prompt generation
    - Multi-element coordination
    - Contextual coherence
    - Adaptive complexity
    """
    
    DISPLAY_NAME = "LLM Contextual Builder (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "theme": ("STRING", {
                    "default": "fantasy landscape",
                    "tooltip": "Main theme or concept for the prompt"
                }),
                "complexity_level": (["simple", "detailed", "comprehensive", "epic"], {
                    "default": "detailed",
                    "tooltip": "Level of detail and complexity"
                }),
                "art_style": ("STRING", {
                    "default": "digital painting",
                    "tooltip": "Artistic style or medium"
                }),
                "mood": ("STRING", {
                    "default": "mystical",
                    "tooltip": "Emotional tone or atmosphere"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name for prompt generation"
                })
            },
            "optional": {
                "elements": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Specific elements to include (comma-separated)"
                }),
                "avoid": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Elements to avoid or exclude"
                }),
                "reference_style": ("STRING", {
                    "default": "",
                    "tooltip": "Reference artist or style to emulate"
                }),
                "technical_quality": ("STRING", {
                    "default": "high quality, detailed",
                    "tooltip": "Technical quality descriptors"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("contextual_prompt", "prompt_breakdown", "generation_info")
    FUNCTION = "build_contextual_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/LLM"
    DESCRIPTION = "Build intelligent, contextually coherent prompts using LLM understanding and thematic coordination"
    
    @performance_monitor("llm_contextual_builder")
    def build_contextual_prompt(
        self,
        theme: str,
        complexity_level: str,
        art_style: str,
        mood: str,
        server_url: str,
        model: str,
        elements: str = "",
        avoid: str = "",
        reference_style: str = "",
        technical_quality: str = "high quality, detailed",
        validate_input: bool = True
    ) -> Tuple[str, str, str]:
        """Build contextual prompt using LLM intelligence."""
        
        if validate_input:
            if not theme.strip():
                return ("", "", "Error: Theme cannot be empty")
        
        try:
            # Build comprehensive context
            context = self._build_context(
                theme, complexity_level, art_style, mood, 
                elements, avoid, reference_style, technical_quality
            )
            
            # Create building prompt
            building_prompt = f"Create a comprehensive prompt for: {theme}"
            
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model)
            
            # Generate contextual prompt
            contextual_prompt, generation_info = llm_framework.enhance_prompt(
                base_prompt=building_prompt,
                enhancement_type="contextual_building",
                context=context,
                additional_instructions=f"Complexity: {complexity_level}"
            )
            
            # Create breakdown
            breakdown = self._create_prompt_breakdown(
                theme, art_style, mood, elements, complexity_level
            )
            
            return (contextual_prompt, breakdown, generation_info)
            
        except Exception as e:
            error_info = f"Contextual building failed: {str(e)}"
            fallback_prompt = f"{theme}, {art_style}, {mood}, {technical_quality}"
            return (fallback_prompt, "Fallback prompt used", error_info)
    
    def _build_context(self, theme: str, complexity: str, art_style: str, 
                      mood: str, elements: str, avoid: str, 
                      reference_style: str, technical_quality: str) -> str:
        """Build comprehensive context for LLM."""
        
        context_parts = [
            f"Theme: {theme}",
            f"Artistic style: {art_style}",
            f"Mood/Atmosphere: {mood}",
            f"Complexity level: {complexity}"
        ]
        
        if elements.strip():
            context_parts.append(f"Required elements: {elements}")
        
        if avoid.strip():
            context_parts.append(f"Avoid: {avoid}")
        
        if reference_style.strip():
            context_parts.append(f"Reference style: {reference_style}")
        
        if technical_quality.strip():
            context_parts.append(f"Technical quality: {technical_quality}")
        
        return "\\n".join(context_parts)
    
    def _create_prompt_breakdown(self, theme: str, art_style: str, 
                               mood: str, elements: str, complexity: str) -> str:
        """Create a breakdown of the prompt components."""
        
        breakdown = [
            f"🎯 Core Theme: {theme}",
            f"🎨 Art Style: {art_style}",
            f"🌟 Mood: {mood}",
            f"📊 Complexity: {complexity}"
        ]
        
        if elements.strip():
            breakdown.append(f"🔧 Elements: {elements}")
        
        return "\\n".join(breakdown)

class XDEV_LLMPersonBuilder(ValidationMixin):
    """
    LLM-enhanced person builder using intelligent character generation.
    """
    
    DISPLAY_NAME = "LLM Person Builder (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "person_type": (["character", "portrait", "historical", "fantasy", "modern", "professional"], {
                    "default": "character",
                    "tooltip": "Type of person to generate"
                }),
                "detail_level": (["basic", "detailed", "comprehensive"], {
                    "default": "detailed",
                    "tooltip": "Amount of detail to generate"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name for generation"
                })
            },
            "optional": {
                "base_concept": ("STRING", {
                    "default": "",
                    "tooltip": "Starting concept or description"
                }),
                "style_context": ("STRING", {
                    "default": "",
                    "tooltip": "Artistic or photographic style context"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("person_prompt", "character_details", "generation_info")
    FUNCTION = "build_llm_person"
    CATEGORY = f"{NodeCategories.PROMPTS}/LLM"
    DESCRIPTION = "Build detailed person descriptions using LLM intelligence"
    
    @performance_monitor("llm_person_builder")
    def build_llm_person(
        self,
        person_type: str,
        detail_level: str,
        server_url: str,
        model: str,
        base_concept: str = "",
        style_context: str = "",
        validate_input: bool = True
    ) -> Tuple[str, str, str]:
        """Build person using LLM."""
        
        try:
            # Build generation prompt
            if base_concept:
                generation_prompt = f"Create a {detail_level} {person_type} based on: {base_concept}"
            else:
                generation_prompt = f"Create a {detail_level} {person_type}"
            
            # Add style context if provided
            context = ""
            if style_context:
                context = f"Style context: {style_context}"
            
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model)
            
            # Generate person
            person_prompt, generation_info = llm_framework.enhance_prompt(
                base_prompt=generation_prompt,
                enhancement_type="character_generation",
                context=context,
                additional_instructions=f"Focus on {person_type} with {detail_level} level of detail"
            )
            
            # Create character details breakdown
            details = f"Type: {person_type}\\nDetail Level: {detail_level}"
            if base_concept:
                details += f"\\nBase Concept: {base_concept}"
            if style_context:
                details += f"\\nStyle Context: {style_context}"
            
            return (person_prompt, details, generation_info)
            
        except Exception as e:
            error_info = f"LLM person generation failed: {str(e)}"
            fallback = f"{person_type}, {detail_level} details"
            return (fallback, "Fallback used", error_info)

class XDEV_LLMStyleBuilder(ValidationMixin):
    """
    LLM-enhanced style builder for creating detailed artistic styles.
    """
    
    DISPLAY_NAME = "LLM Style Builder (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "style_type": (["artistic", "photographic", "cinematic", "digital", "traditional", "experimental"], {
                    "default": "artistic",
                    "tooltip": "Type of style to generate"
                }),
                "complexity": (["simple", "moderate", "complex"], {
                    "default": "moderate",
                    "tooltip": "Style complexity level"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name for generation"
                })
            },
            "optional": {
                "base_style": ("STRING", {
                    "default": "",
                    "tooltip": "Starting style or reference"
                }),
                "mood_direction": ("STRING", {
                    "default": "",
                    "tooltip": "Mood or emotional direction"
                }),
                "technical_focus": ("STRING", {
                    "default": "",
                    "tooltip": "Technical aspects to emphasize"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("style_prompt", "style_breakdown", "generation_info")
    FUNCTION = "build_llm_style"
    CATEGORY = f"{NodeCategories.PROMPTS}/LLM"
    DESCRIPTION = "Build detailed artistic styles using LLM intelligence"
    
    @performance_monitor("llm_style_builder")
    def build_llm_style(
        self,
        style_type: str,
        complexity: str,
        server_url: str,
        model: str,
        base_style: str = "",
        mood_direction: str = "",
        technical_focus: str = "",
        validate_input: bool = True
    ) -> Tuple[str, str, str]:
        """Build style using LLM."""
        
        try:
            # Build generation prompt
            if base_style:
                generation_prompt = f"Create a {complexity} {style_type} style based on: {base_style}"
            else:
                generation_prompt = f"Create a {complexity} {style_type} style"
            
            # Build context
            context_parts = [f"Style type: {style_type}", f"Complexity: {complexity}"]
            if mood_direction:
                context_parts.append(f"Mood direction: {mood_direction}")
            if technical_focus:
                context_parts.append(f"Technical focus: {technical_focus}")
            
            context = "\\n".join(context_parts)
            
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model)
            
            # Generate style
            style_prompt, generation_info = llm_framework.enhance_prompt(
                base_prompt=generation_prompt,
                enhancement_type="style_generation",
                context=context,
                additional_instructions=f"Focus on {style_type} with {complexity} complexity"
            )
            
            # Create style breakdown
            breakdown = f"Type: {style_type}\\nComplexity: {complexity}"
            if base_style:
                breakdown += f"\\nBase Style: {base_style}"
            if mood_direction:
                breakdown += f"\\nMood: {mood_direction}"
            if technical_focus:
                breakdown += f"\\nTechnical Focus: {technical_focus}"
            
            return (style_prompt, breakdown, generation_info)
            
        except Exception as e:
            error_info = f"LLM style generation failed: {str(e)}"
            fallback = f"{style_type} style, {complexity} complexity"
            return (fallback, "Fallback used", error_info)

# Node registrations
NODE_CLASS_MAPPINGS = {
    "XDEV_LLMPromptAssistant": XDEV_LLMPromptAssistant,
    "XDEV_LLMContextualBuilder": XDEV_LLMContextualBuilder,
    "XDEV_LLMPersonBuilder": XDEV_LLMPersonBuilder,
    "XDEV_LLMStyleBuilder": XDEV_LLMStyleBuilder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_LLMPromptAssistant": "LLM Prompt Assistant (XDev)",
    "XDEV_LLMContextualBuilder": "LLM Contextual Builder (XDev)",
    "XDEV_LLMPersonBuilder": "LLM Person Builder (XDev)",
    "XDEV_LLMStyleBuilder": "LLM Style Builder (XDev)",
}