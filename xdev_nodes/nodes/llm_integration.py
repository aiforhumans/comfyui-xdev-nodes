"""
LLM Integration Nodes - Local LLM server support for ComfyUI

This module provides nodes for integrating with local Language Model servers
including LM Studio, Ollama, and other OpenAI-compatible APIs.

Features:
- OpenAI-compatible API support
- Automatic server detection and health checks
- Streaming and non-streaming responses  
- Message history management
- Advanced configuration options
- Robust error handling and fallbacks
"""

import json
import time
from typing import Dict, List, Tuple, Any, Optional, Union
from ..mixins import ValidationMixin
from ..performance import performance_monitor, cached_operation

# HTTP client with graceful fallbacks
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    httpx = None
    HAS_HTTPX = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

# For JSON parsing and validation
import re
from urllib.parse import urljoin, urlparse


class LMStudioChat(ValidationMixin):
    """
    Advanced LM Studio integration node with OpenAI-compatible API support.
    
    Features:
    - OpenAI-compatible chat completions API
    - Automatic server discovery and health checks
    - Message history management with system prompts
    - Streaming and non-streaming responses
    - Advanced configuration (temperature, max_tokens, etc.)
    - Robust error handling with connection fallbacks
    - Performance monitoring and caching
    """
    
    # Common LM Studio and local LLM server ports
    _DEFAULT_PORTS = [1234, 8000, 8080, 11434, 5000, 3000]
    
    # OpenAI-compatible endpoints
    _ENDPOINTS = {
        "chat": "/v1/chat/completions",
        "models": "/v1/models",
        "health": "/health"
    }
    
    # Default configuration for different use cases
    _PRESETS = {
        "creative": {"temperature": 0.9, "top_p": 0.9, "max_tokens": 2048},
        "balanced": {"temperature": 0.7, "top_p": 0.8, "max_tokens": 1024},
        "focused": {"temperature": 0.3, "top_p": 0.7, "max_tokens": 512},
        "precise": {"temperature": 0.1, "top_p": 0.5, "max_tokens": 256},
        "custom": {"temperature": 0.7, "top_p": 0.8, "max_tokens": 1024}
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Hello! How are you?",
                    "tooltip": "The user message to send to the LLM"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL (e.g., http://localhost:1234)"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name or ID to use (auto-detected if available)"
                }),
                "preset": (list(cls._PRESETS.keys()), {
                    "default": "balanced",
                    "tooltip": "Configuration preset for different use cases"
                })
            },
            "optional": {
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "System message to set LLM behavior and context"
                }),
                "message_history": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous conversation history in JSON format"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "Randomness in response generation (0=deterministic, 2=very random)"
                }),
                "max_tokens": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 8192,
                    "tooltip": "Maximum number of tokens to generate"
                }),
                "top_p": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "Nucleus sampling threshold"
                }),
                "stream": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable streaming responses (experimental)"
                }),
                "auto_detect_server": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Automatically detect running LM Studio servers"
                }),
                "timeout": ("INT", {
                    "default": 30,
                    "min": 5,
                    "max": 300,
                    "tooltip": "Request timeout in seconds"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation and error checking"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("response", "full_conversation", "server_info", "generation_stats")
    FUNCTION = "generate_response"
    CATEGORY = "XDev/LLM/Integration"
    DESCRIPTION = "Connect to LM Studio local API for chat completions with advanced configuration and error handling"
    
    def __init__(self):
        super().__init__()
        self._client = None
        self._server_cache = {}
        
    @performance_monitor("lm_studio_response")
    def generate_response(
        self,
        prompt: str,
        server_url: str,
        model: str,
        preset: str,
        system_prompt: str = "",
        message_history: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.8,
        stream: bool = False,
        auto_detect_server: bool = True,
        timeout: int = 30,
        validate_input: bool = True
    ) -> Tuple[str, str, str, str]:
        """Generate response using LM Studio local API."""
        
        if validate_input:
            # Validate inputs
            if not prompt.strip():
                return ("", "", "Error: Empty prompt provided", "Error: No generation attempted")
            
            if not self._is_valid_url(server_url):
                return ("", "", f"Error: Invalid server URL: {server_url}", "Error: Invalid configuration")
        
        # Check HTTP client availability
        if not HAS_HTTPX and not HAS_REQUESTS:
            return (
                "", 
                "", 
                "Error: No HTTP client available. Please install 'httpx' or 'requests'",
                "Error: Missing dependencies"
            )
        
        try:
            # Auto-detect server if enabled
            if auto_detect_server:
                detected_url = self._detect_server()
                if detected_url:
                    server_url = detected_url
            
            # Apply preset configuration
            config = self._get_preset_config(preset, temperature, max_tokens, top_p)
            
            # Build message list
            messages = self._build_message_list(prompt, system_prompt, message_history)
            
            # Generate response
            start_time = time.time()
            
            if stream:
                response = self._generate_streaming_response(
                    server_url, model, messages, config, timeout
                )
            else:
                response = self._generate_standard_response(
                    server_url, model, messages, config, timeout
                )
            
            generation_time = time.time() - start_time
            
            # Build full conversation
            messages.append({"role": "assistant", "content": response})
            full_conversation = json.dumps(messages, indent=2)
            
            # Server info
            server_info = self._get_server_info(server_url, timeout)
            
            # Generation stats
            stats = self._build_generation_stats(
                response, generation_time, config, len(messages)
            )
            
            return (response, full_conversation, server_info, stats)
            
        except Exception as e:
            error_msg = f"LM Studio Error: {str(e)}"
            return ("", "", error_msg, f"Error: {type(e).__name__}")
    
    @cached_operation(ttl=300)
    def _detect_server(self) -> Optional[str]:
        """Automatically detect running LM Studio servers."""
        
        for port in self._DEFAULT_PORTS:
            url = f"http://localhost:{port}"
            if self._test_server_connection(url):
                return url
        
        return None
    
    def _test_server_connection(self, server_url: str, timeout: int = 5) -> bool:
        """Test connection to LM Studio server."""
        
        try:
            # Try health check endpoint first
            health_url = urljoin(server_url, "/health")
            
            if HAS_HTTPX:
                with httpx.Client() as client:
                    response = client.get(health_url, timeout=timeout)
                    return response.status_code == 200
            elif HAS_REQUESTS:
                response = requests.get(health_url, timeout=timeout)
                return response.status_code == 200
                
        except:
            pass
        
        try:
            # Fallback: try models endpoint
            models_url = urljoin(server_url, self._ENDPOINTS["models"])
            
            if HAS_HTTPX:
                with httpx.Client() as client:
                    response = client.get(models_url, timeout=timeout)
                    return response.status_code == 200
            elif HAS_REQUESTS:
                response = requests.get(models_url, timeout=timeout)
                return response.status_code == 200
                
        except:
            return False
        
        return False
    
    def _generate_standard_response(
        self, 
        server_url: str, 
        model: str, 
        messages: List[Dict], 
        config: Dict,
        timeout: int
    ) -> str:
        """Generate standard (non-streaming) response."""
        
        chat_url = urljoin(server_url, self._ENDPOINTS["chat"])
        
        payload = {
            "model": model,
            "messages": messages,
            **config
        }
        
        if HAS_HTTPX:
            with httpx.Client() as client:
                response = client.post(
                    chat_url,
                    json=payload,
                    timeout=timeout,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
        elif HAS_REQUESTS:
            response = requests.post(
                chat_url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
        else:
            raise RuntimeError("No HTTP client available")
        
        # Extract response from OpenAI-compatible format
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        else:
            raise ValueError("Unexpected response format from server")
    
    def _generate_streaming_response(
        self, 
        server_url: str, 
        model: str, 
        messages: List[Dict], 
        config: Dict,
        timeout: int
    ) -> str:
        """Generate streaming response (concatenated result)."""
        
        chat_url = urljoin(server_url, self._ENDPOINTS["chat"])
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **config
        }
        
        full_response = ""
        
        if HAS_HTTPX:
            with httpx.Client() as client:
                with client.stream(
                    "POST", 
                    chat_url, 
                    json=payload, 
                    timeout=timeout,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str.strip() == "[DONE]":
                                break
                                
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_response += content
                            except json.JSONDecodeError:
                                continue
        
        elif HAS_REQUESTS:
            response = requests.post(
                chat_url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix
                    
                    if data_str.strip() == "[DONE]":
                        break
                        
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                full_response += content
                    except json.JSONDecodeError:
                        continue
        else:
            raise RuntimeError("No HTTP client available")
        
        return full_response
    
    def _build_message_list(
        self, 
        prompt: str, 
        system_prompt: str, 
        message_history: str
    ) -> List[Dict[str, str]]:
        """Build OpenAI-compatible message list."""
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        
        # Parse message history if provided
        if message_history.strip():
            try:
                history = json.loads(message_history)
                if isinstance(history, list):
                    for msg in history:
                        if isinstance(msg, dict) and "role" in msg and "content" in msg:
                            messages.append(msg)
            except json.JSONDecodeError:
                # Ignore invalid JSON history
                pass
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _get_preset_config(
        self, 
        preset: str, 
        temperature: float, 
        max_tokens: int, 
        top_p: float
    ) -> Dict[str, Any]:
        """Get configuration based on preset and custom values."""
        
        if preset == "custom":
            return {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            }
        else:
            return self._PRESETS.get(preset, self._PRESETS["balanced"]).copy()
    
    @cached_operation(ttl=60)
    def _get_server_info(self, server_url: str, timeout: int) -> str:
        """Get information about the LM Studio server."""
        
        try:
            models_url = urljoin(server_url, self._ENDPOINTS["models"])
            
            if HAS_HTTPX:
                with httpx.Client() as client:
                    response = client.get(models_url, timeout=timeout)
                    response.raise_for_status()
                    data = response.json()
            elif HAS_REQUESTS:
                response = requests.get(models_url, timeout=timeout)
                response.raise_for_status()
                data = response.json()
            else:
                return "Server: Connected (no HTTP client details available)"
            
            # Extract available models
            models = []
            if "data" in data:
                models = [model.get("id", "unknown") for model in data["data"]]
            
            info = [
                f"Server: {server_url}",
                f"Status: Connected",
                f"Available models: {len(models)}",
                f"Models: {', '.join(models[:3])}" + ("..." if len(models) > 3 else "")
            ]
            
            return "\n".join(info)
            
        except Exception as e:
            return f"Server: {server_url}\nStatus: Connected (info unavailable)\nError: {str(e)}"
    
    def _build_generation_stats(
        self, 
        response: str, 
        generation_time: float,
        config: Dict[str, Any],
        message_count: int
    ) -> str:
        """Build generation statistics string."""
        
        stats = [
            f"Generation time: {generation_time:.2f}s",
            f"Response length: {len(response)} characters",
            f"Estimated tokens: ~{len(response.split())}",
            f"Messages in conversation: {message_count}",
            f"Temperature: {config.get('temperature', 'N/A')}",
            f"Max tokens: {config.get('max_tokens', 'N/A')}",
            f"Top-p: {config.get('top_p', 'N/A')}"
        ]
        
        return "\n".join(stats)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False


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
        },
        "sdxl_photo_enhancement": {
            "temperature": 0.4,
            "max_tokens": 2000,
            "top_p": 0.7,
            "system_prompt": """You are an expert SDXL prompt writer for photorealistic images.

GOAL
- Produce a single best SDXL prompt (and a matching negative prompt + render settings) for a PHOTO (not illustration).
- Keep it concise, model-friendly, and directly usable.

INPUT
- You receive a short user brief (subject, mood, setting, constraints). If any field is missing, make sensible choices.

STYLE RULES
- Prioritize realism: RAW photo, natural lighting, plausible optics.
- Use simple, concrete words; avoid purple prose.
- Prefer neutral, descriptive tags over hype (avoid "masterpiece, 8k, ultra" spam).
- Never use real person/celebrity names or brand logos; invent look-alikes with generic descriptors.
- Avoid NSFW or violent content.

PROMPT SHAPE (in this order; commas between items, short phrases)
1) subject focus (1–2 short phrases, the core idea)
2) scene & setting (place, time, weather/atmosphere)
3) wardrobe/props (only if relevant)
4) lighting (1–2 terms: e.g., soft window light, golden hour, overcast, studio strobe)
5) camera & optics (camera type, lens focal length in mm, aperture, ISO, shutter if needed)
6) composition & perspective (framing, angle, rule-of-thirds, depth of field cues)
7) quality & realism tags (RAW photo, natural skin texture, color-accurate, unedited look)
8) optional post-process look (subtle film emulation, Kodak Portra, slight grain)

NEGATIVE PROMPT
- Remove artifacts: deformed hands/eyes, extra limbs, over-smoothing, plastic skin, watermark, jpeg artifacts, text, logo, mutation, lowres, oversaturated, HDR halos.
- Remove style leaks: anime, illustration, CGI, 3D, painting (unless requested).

SDXL SETTINGS (defaults you may adapt to fit the brief)
- width & height chosen to respect aspect ratio from the brief (portrait 832x1216, landscape 1216x832, square 1024x1024).
- steps: 28–35
- cfg: 4.5–7.0 (start 5.5 for realism)
- sampler: DPM++ 2M Karras (or a good SDXL sampler available)
- refiner: optional; if used, allocate ~20–30% steps
- seed: set a number for reproducibility (randomize only if asked)
- highres/fix: off by default; enable only for very detailed scenes
- loras: none by default; include only if explicitly requested (with subtle weights 0.4–0.7)

OUTPUT FORMAT (JSON — no extra text)
{
  "prompt": "<comma-separated SDXL prompt text>",
  "negative_prompt": "<comma-separated negatives>",
  "settings": {
    "width": <int>,
    "height": <int>,
    "steps": <int>,
    "cfg": <float>,
    "sampler": "DPM++ 2M Karras",
    "seed": <int>,
    "refiner": false
  },
  "notes": "1–2 sentences on key choices (lighting/composition) for the user."
}

BEHAVIOR
- If the user specifies aspect ratio, translate to nearest SDXL-friendly resolution.
- If the user asks for a specific style (e.g., film stock), add it subtly; don't overpower realism.
- If the brief is ambiguous, choose one coherent interpretation and proceed.
- Return only the JSON object, no explanations."""
        }
    }
    
    def __init__(self, server_url: str = "http://localhost:1234", model: str = "local-model"):
        self.server_url = server_url
        self.model = model
        self._llm_client = None
    
    @cached_operation(ttl=300)
    def _get_llm_client(self):
        """Get or create LLM client instance."""
        if self._llm_client is None:
            self._llm_client = LMStudioChat()
        return self._llm_client
    
    @performance_monitor("llm_prompt_enhancement")
    def enhance_prompt(self, base_prompt: str, enhancement_type: str = "prompt_enhancement", 
                      context: str = "", additional_instructions: str = "") -> Tuple[str, str]:
        """
        Enhance a prompt using LLM intelligence.
        
        Args:
            base_prompt: Original prompt to enhance
            enhancement_type: Type of enhancement (character_generation, style_generation, etc.)
            context: Additional context for the enhancement
            additional_instructions: Specific instructions for the LLM
            
        Returns:
            Tuple of (enhanced_prompt, enhancement_info)
        """
        try:
            config = self._LLM_CONFIGS.get(enhancement_type, self._LLM_CONFIGS["prompt_enhancement"])
            
            # Build enhancement request
            enhancement_prompt = self._build_enhancement_prompt(
                base_prompt, enhancement_type, context, additional_instructions
            )
            
            # Get LLM response
            client = self._get_llm_client()
            response, conversation, server_info, stats = client.generate_response(
                prompt=enhancement_prompt,
                server_url=self.server_url,
                model=self.model,
                preset="custom",
                system_prompt=config["system_prompt"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                top_p=config["top_p"],
                validate_input=True
            )
            
            if response and not response.startswith("Error:"):
                return response.strip(), f"Enhanced using {enhancement_type} mode"
            else:
                # Fallback to original prompt on error
                return base_prompt, f"LLM enhancement failed: {response[:100]}..."
                
        except Exception as e:
            return base_prompt, f"LLM enhancement error: {str(e)}"
    
    def _build_enhancement_prompt(self, base_prompt: str, enhancement_type: str, 
                                 context: str, additional_instructions: str) -> str:
        """Build the enhancement request prompt."""
        
        prompt_templates = {
            "character_generation": f"""
Please enhance this character description: "{base_prompt}"

Context: {context if context else 'General character for creative projects'}

Requirements:
- Expand personality traits with specific examples
- Add physical details that match the character type
- Include background elements that support the character
- Ensure consistency across all traits
- Make the description vivid and specific

{additional_instructions}

Provide a detailed, cohesive character description:""",
            
            "style_generation": f"""
Please enhance this art style description: "{base_prompt}"

Context: {context if context else 'General artistic style for visual projects'}

Requirements:
- Specify artistic medium and techniques
- Define color palette and lighting approach
- Include composition and framing details
- Add texture and material qualities
- Ensure the style is achievable and coherent

{additional_instructions}

Provide a comprehensive, detailed style description:""",
            
            "prompt_enhancement": f"""
Please enhance this prompt: "{base_prompt}"

Context: {context if context else 'General prompt for AI image generation'}

Requirements:
- Improve clarity and specificity
- Add relevant artistic and technical details
- Fix any ambiguities or conflicts
- Maintain the original creative intent
- Optimize for AI image generation

{additional_instructions}

Provide an enhanced, detailed prompt:""",
            
            "contextual_building": f"""
Please build a comprehensive prompt based on: "{base_prompt}"

Context: {context if context else 'Creative visual storytelling'}

Requirements:
- Create a complete narrative context
- Include environmental and atmospheric details
- Add emotional and thematic elements
- Ensure all elements work together cohesively
- Make it rich and immersive

{additional_instructions}

Provide a complete, contextually rich prompt:"""
        }
        
        return prompt_templates.get(enhancement_type, prompt_templates["prompt_enhancement"])


class LLMPromptAssistant(ValidationMixin):
    """
    Intelligent prompt enhancement node using LLM capabilities.
    
    Features:
    - Context-aware prompt improvement
    - Multiple enhancement modes
    - Original prompt preservation
    - Detailed enhancement reporting
    """
    
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
    CATEGORY = "XDev/LLM/PromptTools"
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


class LLMContextualBuilder(ValidationMixin):
    """
    Smart contextual prompt builder using LLM understanding.
    
    Features:
    - Theme-based prompt generation
    - Multi-element coordination
    - Contextual coherence
    - Adaptive complexity
    """
    
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
    CATEGORY = "XDev/LLM/PromptTools"
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
        
        return "\n".join(context_parts)
    
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
        
        return "\n".join(breakdown)


class LLMSDXLPhotoEnhancer(ValidationMixin):
    """
    Professional SDXL prompt enhancer for photorealistic images.
    
    Features:
    - Structured 8-part prompt construction
    - Negative prompt generation
    - Technical SDXL settings optimization
    - JSON-formatted output with camera specifications
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "user_brief": ("STRING", {
                    "multiline": True,
                    "default": "young woman reading by a window",
                    "tooltip": "Describe the subject, mood, setting, and any constraints for the photo"
                }),
                "aspect_ratio": (["portrait", "landscape", "square"], {
                    "default": "portrait",
                    "tooltip": "Image aspect ratio - determines SDXL dimensions"
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
                "style_notes": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Additional style instructions (film stock, lighting preferences, etc.)"
                }),
                "fallback_on_error": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Return basic prompt if LLM enhancement fails"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("sdxl_prompt", "negative_prompt", "settings_json", "enhancement_notes")
    FUNCTION = "enhance_sdxl_photo_prompt"
    CATEGORY = "XDev/LLM/SDXL"
    DESCRIPTION = "Professional SDXL prompt enhancer for photorealistic images with structured prompts and technical settings"
    
    @performance_monitor("llm_sdxl_photo_enhancement")
    def enhance_sdxl_photo_prompt(
        self,
        user_brief: str,
        aspect_ratio: str,
        server_url: str,
        model: str,
        style_notes: str = "",
        fallback_on_error: bool = True,
        validate_input: bool = True
    ) -> Tuple[str, str, str, str]:
        """Enhance user brief into professional SDXL photo prompt with technical specifications."""
        
        if validate_input:
            if not user_brief.strip():
                return ("", "", "", "Error: User brief cannot be empty")
        
        try:
            # Build the enhancement context
            enhancement_context = self._build_enhancement_context(user_brief, aspect_ratio, style_notes)
            
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model)
            
            # Generate SDXL enhancement
            enhanced_result, enhancement_info = llm_framework.enhance_prompt(
                base_prompt=enhancement_context,
                enhancement_type="sdxl_photo_enhancement",
                context="",
                additional_instructions=""
            )
            
            # Parse JSON response
            sdxl_prompt, negative_prompt, settings_json, notes = self._parse_sdxl_response(enhanced_result)
            
            return (sdxl_prompt, negative_prompt, settings_json, notes)
            
        except Exception as e:
            error_info = f"SDXL enhancement failed: {str(e)}"
            
            if fallback_on_error:
                # Generate basic fallback
                fallback_prompt = self._generate_fallback_prompt(user_brief, aspect_ratio)
                fallback_negative = "deformed hands, extra limbs, plastic skin, watermark, text, logo, CGI, anime"
                fallback_settings = self._generate_fallback_settings(aspect_ratio)
                return (fallback_prompt, fallback_negative, fallback_settings, error_info)
            else:
                return ("", "", "", error_info)
    
    def _build_enhancement_context(self, user_brief: str, aspect_ratio: str, style_notes: str) -> str:
        """Build the context for SDXL enhancement."""
        
        context_parts = [f"Brief: {user_brief.strip()}"]
        
        if aspect_ratio:
            context_parts.append(f"Aspect ratio: {aspect_ratio}")
        
        if style_notes.strip():
            context_parts.append(f"Style notes: {style_notes.strip()}")
        
        return "\n".join(context_parts)
    
    def _parse_sdxl_response(self, response: str) -> Tuple[str, str, str, str]:
        """Parse JSON response from SDXL enhancement."""
        
        try:
            import json
            
            # Try to find JSON in the response
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            # Parse JSON
            data = json.loads(response_clean)
            
            # Extract components
            prompt = data.get("prompt", "")
            negative_prompt = data.get("negative_prompt", "")
            settings = data.get("settings", {})
            notes = data.get("notes", "")
            
            # Format settings as readable JSON
            settings_json = json.dumps(settings, indent=2) if settings else "{}"
            
            return (prompt, negative_prompt, settings_json, notes)
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fallback parsing for malformed JSON
            lines = response.strip().split('\n')
            prompt = ""
            negative_prompt = ""
            
            # Try to extract basic prompt from response
            for line in lines:
                if 'prompt' in line.lower() and ':' in line:
                    prompt = line.split(':', 1)[1].strip().strip('"')
                elif 'negative' in line.lower() and ':' in line:
                    negative_prompt = line.split(':', 1)[1].strip().strip('"')
            
            if not prompt:
                prompt = response.strip()
            
            return (prompt, negative_prompt, "{}", f"JSON parsing failed: {str(e)}")
    
    def _generate_fallback_prompt(self, user_brief: str, aspect_ratio: str) -> str:
        """Generate a basic fallback prompt when LLM fails."""
        
        return f"{user_brief.strip()}, RAW photo, natural lighting, realistic, high quality, detailed"
    
    def _generate_fallback_settings(self, aspect_ratio: str) -> str:
        """Generate fallback SDXL settings."""
        
        import json
        
        # Map aspect ratio to dimensions
        dimensions = {
            "portrait": {"width": 832, "height": 1216},
            "landscape": {"width": 1216, "height": 832},
            "square": {"width": 1024, "height": 1024}
        }
        
        dims = dimensions.get(aspect_ratio, dimensions["portrait"])
        
        settings = {
            "width": dims["width"],
            "height": dims["height"],
            "steps": 30,
            "cfg": 5.5,
            "sampler": "DPM++ 2M Karras",
            "seed": 12345,
            "refiner": False
        }
        
        return json.dumps(settings, indent=2)


# Export for node registration
__all__ = ["LMStudioChat", "LLMPromptAssistant", "LLMContextualBuilder", "LLMSDXLPhotoEnhancer", "LLMPromptFramework"]