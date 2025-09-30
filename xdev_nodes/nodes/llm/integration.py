from ...categories import NodeCategories
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
from ...mixins import ValidationMixin
from ...performance import performance_monitor, cached_operation

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
    DISPLAY_NAME = "LM Studio Chat (XDev)"
    """
    Advanced LM Studio integration node with OpenAI-compatible API support.
    
    Features:
    - OpenAI-compatible chat completions API
    - Automatic server discovery and health checks
    - Easy-to-edit message history with individual input blocks
    - Legacy JSON history support for backward compatibility
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
                    "tooltip": "Previous conversation history in JSON format (legacy format)"
                }),
                "history_user_1": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous user message 1 (easy editing)"
                }),
                "history_assistant_1": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous assistant response 1 (easy editing)"
                }),
                "history_user_2": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous user message 2 (easy editing)"
                }),
                "history_assistant_2": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous assistant response 2 (easy editing)"
                }),
                "history_user_3": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous user message 3 (easy editing)"
                }),
                "history_assistant_3": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Previous assistant response 3 (easy editing)"
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
    CATEGORY = NodeCategories.LLM_INTEGRATION
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
        history_user_1: str = "",
        history_assistant_1: str = "",
        history_user_2: str = "",
        history_assistant_2: str = "",
        history_user_3: str = "",
        history_assistant_3: str = "",
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
            messages = self._build_message_list(
                prompt, system_prompt, message_history,
                history_user_1, history_assistant_1,
                history_user_2, history_assistant_2, 
                history_user_3, history_assistant_3
            )
            
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
        message_history: str,
        history_user_1: str = "",
        history_assistant_1: str = "",
        history_user_2: str = "",
        history_assistant_2: str = "",
        history_user_3: str = "",
        history_assistant_3: str = ""
    ) -> List[Dict[str, str]]:
        """Build OpenAI-compatible message list with easy-to-edit history blocks."""
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        
        # Parse legacy JSON message history if provided
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
        
        # Add easy-to-edit individual history messages (in chronological order)
        history_pairs = [
            (history_user_1, history_assistant_1),
            (history_user_2, history_assistant_2),
            (history_user_3, history_assistant_3)
        ]
        
        for user_msg, assistant_msg in history_pairs:
            if user_msg.strip():
                messages.append({"role": "user", "content": user_msg.strip()})
            if assistant_msg.strip():
                messages.append({"role": "assistant", "content": assistant_msg.strip()})
        
        # Add current user prompt
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
    DISPLAY_NAME = "LLM Prompt Framework (XDev)"
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
    CATEGORY = NodeCategories.LLM_PROMPT_TOOLS
    DISPLAY_NAME = "LLM Prompt Assistant (XDev)"
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
    CATEGORY = NodeCategories.LLM_PROMPT_TOOLS
    DISPLAY_NAME = "LLM Contextual Builder (XDev)"
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


class LLMDevFramework(ValidationMixin):
    """
    LLM-DEV Framework - Development-focused LLM interaction node.
    
    Features:
    - Simple system instruction + prompt interface
    - Raw request/response tracking for development
    - Minimal configuration for rapid testing
    - Clean development workflow integration
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "system_instruction": ("STRING", {
                    "multiline": True,
                    "default": "You are a helpful assistant. Provide clear, accurate, and concise responses.",
                    "tooltip": "System instruction that defines the LLM's behavior and role"
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Hello, please introduce yourself and explain what you can help with.",
                    "tooltip": "User prompt or query to send to the LLM"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio or compatible server URL"
                }),
                "model_name": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name to use on the server"
                })
            },
            "optional": {
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "Response creativity (0.0=deterministic, 2.0=very creative)"
                }),
                "max_tokens": ("INT", {
                    "default": 1024,
                    "min": 50,
                    "max": 8192,
                    "step": 50,
                    "tooltip": "Maximum response length in tokens"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "request_made")
    FUNCTION = "dev_llm_call"
    CATEGORY = NodeCategories.LLM_DEVELOPMENT
    DISPLAY_NAME = "LLM-DEV Framework (XDev)"
    DESCRIPTION = "LLM-DEV Framework - Simple system instruction + prompt interface for development and testing"
    
    @performance_monitor("llm_dev_framework")
    def dev_llm_call(
        self,
        system_instruction: str,
        prompt: str,
        server_url: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        validate_input: bool = True
    ) -> Tuple[str, str]:
        """Execute LLM call with development tracking."""
        
        if validate_input:
            if not prompt.strip():
                return ("", "Error: Prompt cannot be empty")
            if not system_instruction.strip():
                return ("", "Error: System instruction cannot be empty")
        
        try:
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model_name)
            llm_client = llm_framework._get_llm_client()
            
            # Build request details for tracking
            request_details = self._build_request_details(
                system_instruction, prompt, server_url, model_name, temperature, max_tokens
            )
            
            # Make LLM call
            response = llm_client.generate_response(
                prompt=prompt,
                server_url=server_url,
                model=model_name,
                preset="custom",
                system_prompt=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                validate_input=True
            )
            
            # Extract response
            if isinstance(response, tuple) and len(response) >= 1:
                llm_response = response[0].strip()
                generation_stats = response[3] if len(response) > 3 else "No stats available"
                
                # Update request details with response info
                request_made = self._build_request_summary(request_details, llm_response, generation_stats)
                
                return (llm_response, request_made)
            else:
                raise Exception("Invalid LLM response format")
            
        except Exception as e:
            error_msg = f"LLM-DEV Framework error: {str(e)}"
            request_made = self._build_error_request_summary(
                system_instruction, prompt, server_url, model_name, str(e)
            )
            return (error_msg, request_made)
    
    def _build_request_details(
        self, 
        system_instruction: str, 
        prompt: str, 
        server_url: str, 
        model_name: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Build detailed request information for tracking."""
        
        import time
        
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server_url": server_url,
            "model_name": model_name,
            "system_instruction": system_instruction[:100] + "..." if len(system_instruction) > 100 else system_instruction,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system_length": len(system_instruction),
            "prompt_length": len(prompt)
        }
    
    def _build_request_summary(self, request_details: Dict[str, Any], response: str, stats: str) -> str:
        """Build comprehensive request summary."""
        
        summary_parts = [
            f"🕐 Timestamp: {request_details['timestamp']}",
            f"🌐 Server: {request_details['server_url']}",
            f"🤖 Model: {request_details['model_name']}",
            f"🎛️ Settings: temp={request_details['temperature']}, max_tokens={request_details['max_tokens']}",
            "",
            f"📥 System Instruction ({request_details['system_length']} chars):",
            f"   {request_details['system_instruction']}",
            "",
            f"📝 Prompt ({request_details['prompt_length']} chars):",
            f"   {request_details['prompt']}",
            "",
            f"📤 Response ({len(response)} chars):",
            f"   {response[:150]}{'...' if len(response) > 150 else ''}",
            "",
            f"📊 Generation Stats: {stats}"
        ]
        
        return "\n".join(summary_parts)
    
    def _build_error_request_summary(
        self, 
        system_instruction: str, 
        prompt: str, 
        server_url: str, 
        model_name: str,
        error: str
    ) -> str:
        """Build error request summary for debugging."""
        
        import time
        
        summary_parts = [
            f"❌ ERROR - {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"🌐 Server: {server_url}",
            f"🤖 Model: {model_name}",
            "",
            f"📥 System Instruction ({len(system_instruction)} chars):",
            f"   {system_instruction[:100]}{'...' if len(system_instruction) > 100 else ''}",
            "",
            f"📝 Prompt ({len(prompt)} chars):",
            f"   {prompt[:100]}{'...' if len(prompt) > 100 else ''}",
            "",
            f"🚨 Error: {error}"
        ]
        
        return "\n".join(summary_parts)


class LLMSDXLExpertWriter(ValidationMixin):
    """
    Expert SDXL prompt writer for direct, concise prompt generation.
    
    Features:
    - Streamlined USER_PROMPT + STYLE_SETTINGS + RULES analysis
    - Single optimized SDXL prompt output
    - Model-friendly, directly usable prompts
    - Focused on efficiency and clarity
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "user_prompt": ("STRING", {
                    "multiline": True,
                    "default": "young woman reading by a window",
                    "tooltip": "Main subject/scene description - what you want to generate"
                }),
                "style_settings": ("STRING", {
                    "multiline": True,
                    "default": "natural lighting, soft colors, cozy atmosphere",
                    "tooltip": "Visual style, lighting, mood, artistic direction"
                }),
                "rules": ("STRING", {
                    "multiline": True,
                    "default": "photorealistic, high quality, detailed, no anime style",
                    "tooltip": "Technical requirements, constraints, what to avoid"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name to use"
                })
            },
            "optional": {
                "temperature": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "LLM creativity level (lower = more consistent)"
                }),
                "max_tokens": ("INT", {
                    "default": 800,
                    "min": 100,
                    "max": 4096,
                    "step": 50,
                    "tooltip": "Maximum response length"
                }),
                "fallback_on_error": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Return basic prompt if LLM fails"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("sdxl_prompt", "generation_info")
    FUNCTION = "write_sdxl_prompt"
    CATEGORY = NodeCategories.LLM_SDXL
    DISPLAY_NAME = "LLM SDXL Expert Writer (XDev)"
    DESCRIPTION = "Expert SDXL prompt writer - analyzes USER_PROMPT + STYLE_SETTINGS + RULES to produce optimized SDXL prompts"
    
    def __init__(self):
        super().__init__()
        self._expert_system_prompt = self._create_expert_system_prompt()
    
    def _create_expert_system_prompt(self) -> str:
        """Create the expert SDXL prompt writing system prompt."""
        return """You are an expert SDXL prompt writer for photorealistic images.

GOAL
- Analyze USER_PROMPT + STYLE_SETTINGS + RULES
- Produce a single best SDXL prompt based on the user USER_PROMPT implementing STYLE_SETTINGS + RULES
- Keep it concise, model-friendly, and directly usable

ANALYSIS PROCESS
1. Extract core subject/scene from USER_PROMPT
2. Apply STYLE_SETTINGS for visual direction
3. Integrate RULES as constraints and quality guidelines
4. Optimize for SDXL model performance

OUTPUT REQUIREMENTS
- Single comma-separated prompt string
- 50-150 words maximum
- No explanations, just the optimized prompt
- Include technical quality terms if specified in RULES
- Maintain photorealistic focus unless STYLE_SETTINGS specify otherwise

PROMPT STRUCTURE PRIORITY
1. Main subject (from USER_PROMPT)
2. Key descriptors (physical, emotional)
3. Style/mood elements (from STYLE_SETTINGS)
4. Technical quality (from RULES)
5. Lighting/composition details
6. Camera/lens specifications if relevant

Return only the optimized SDXL prompt, nothing else."""
    
    @performance_monitor("sdxl_expert_writer")
    def write_sdxl_prompt(
        self,
        user_prompt: str,
        style_settings: str,
        rules: str,
        server_url: str,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 800,
        fallback_on_error: bool = True,
        validate_input: bool = True
    ) -> Tuple[str, str]:
        """Write expert SDXL prompt based on user inputs."""
        
        if validate_input:
            if not user_prompt.strip():
                return ("", "Error: User prompt cannot be empty")
        
        try:
            # Build analysis context
            analysis_context = self._build_analysis_context(user_prompt, style_settings, rules)
            
            # Initialize LLM framework
            llm_framework = LLMPromptFramework(server_url, model)
            llm_client = llm_framework._get_llm_client()
            
            # Generate optimized SDXL prompt
            response = llm_client.generate_response(
                prompt=analysis_context,
                server_url=server_url,
                model=model,
                preset="custom",
                system_prompt=self._expert_system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                validate_input=True
            )
            
            # Extract and clean the response
            if isinstance(response, tuple) and len(response) >= 1:
                sdxl_prompt = response[0].strip()
                generation_stats = response[3] if len(response) > 3 else "Generation completed"
                
                # Clean up the prompt (remove quotes, extra formatting)
                sdxl_prompt = self._clean_prompt_output(sdxl_prompt)
                
                generation_info = f"Expert SDXL prompt generated - {generation_stats}"
                
                return (sdxl_prompt, generation_info)
            else:
                raise Exception("Invalid LLM response format")
            
        except Exception as e:
            error_info = f"SDXL expert writing failed: {str(e)}"
            
            if fallback_on_error:
                # Generate basic fallback prompt
                fallback_prompt = self._generate_expert_fallback(user_prompt, style_settings, rules)
                return (fallback_prompt, f"Used fallback - {error_info}")
            else:
                return ("", error_info)
    
    def _build_analysis_context(self, user_prompt: str, style_settings: str, rules: str) -> str:
        """Build the context for SDXL prompt analysis."""
        
        context_parts = [
            f"USER_PROMPT: {user_prompt.strip()}",
            f"STYLE_SETTINGS: {style_settings.strip()}",
            f"RULES: {rules.strip()}"
        ]
        
        return "\n\n".join(context_parts)
    
    def _clean_prompt_output(self, prompt: str) -> str:
        """Clean and optimize the prompt output."""
        
        # Remove common formatting artifacts
        prompt = prompt.strip()
        prompt = prompt.strip('"\'')
        prompt = prompt.replace('\n', ', ')
        prompt = prompt.replace('  ', ' ')
        
        # Remove common prefixes/suffixes
        unwanted_prefixes = ["prompt:", "sdxl prompt:", "optimized prompt:", "here is", "here's"]
        for prefix in unwanted_prefixes:
            if prompt.lower().startswith(prefix):
                prompt = prompt[len(prefix):].strip(': ')
        
        return prompt.strip()
    
    def _generate_expert_fallback(self, user_prompt: str, style_settings: str, rules: str) -> str:
        """Generate a basic expert fallback when LLM fails."""
        
        # Combine inputs intelligently
        prompt_parts = [user_prompt.strip()]
        
        if style_settings.strip():
            prompt_parts.append(style_settings.strip())
        
        # Add quality terms from rules
        if rules.strip():
            quality_terms = []
            rule_words = rules.lower().split()
            
            quality_keywords = ["photorealistic", "high quality", "detailed", "professional", "8k", "4k", "hdr"]
            for keyword in quality_keywords:
                if any(word in keyword or keyword in word for word in rule_words):
                    quality_terms.append(keyword)
            
            if quality_terms:
                prompt_parts.extend(quality_terms)
            else:
                prompt_parts.append("photorealistic, high quality, detailed")
        
        return ", ".join(prompt_parts)


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
                "custom_system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Override default system prompt - leave empty to use built-in SDXL expert prompt"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.4,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                    "tooltip": "LLM creativity level (0.0=deterministic, 2.0=very creative)"
                }),
                "max_tokens": ("INT", {
                    "default": 2000,
                    "min": 100,
                    "max": 8192,
                    "step": 100,
                    "tooltip": "Maximum tokens for LLM response"
                }),
                "top_p": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Nucleus sampling threshold"
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
    CATEGORY = NodeCategories.LLM_SDXL
    DISPLAY_NAME = "LLM SDXL Photo Enhancer (XDev)"
    DESCRIPTION = "Professional SDXL prompt enhancer for photorealistic images with structured prompts and technical settings"
    
    @performance_monitor("llm_sdxl_photo_enhancement")
    def enhance_sdxl_photo_prompt(
        self,
        user_brief: str,
        aspect_ratio: str,
        server_url: str,
        model: str,
        style_notes: str = "",
        custom_system_prompt: str = "",
        temperature: float = 0.4,
        max_tokens: int = 2000,
        top_p: float = 0.7,
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
            
            # Generate SDXL enhancement with custom settings
            if custom_system_prompt.strip():
                # Use custom system prompt and settings
                enhanced_result, enhancement_info = self._enhance_with_custom_prompt(
                    llm_framework, enhancement_context, custom_system_prompt,
                    temperature, max_tokens, top_p
                )
            else:
                # Use built-in SDXL enhancement
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
    
    def _enhance_with_custom_prompt(
        self, 
        llm_framework: LLMPromptFramework, 
        enhancement_context: str, 
        custom_system_prompt: str,
        temperature: float,
        max_tokens: int,
        top_p: float
    ) -> Tuple[str, str]:
        """Enhance prompt using custom system prompt and settings."""
        
        # Get the LLM client
        llm_client = llm_framework._get_llm_client()
        
        # Make direct LLM request with custom system prompt using the correct method
        try:
            response = llm_client.generate_response(
                prompt=enhancement_context,
                server_url=llm_framework.server_url,
                model=llm_framework.model,
                preset="custom",
                system_prompt=custom_system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                validate_input=True
            )
            
            # Extract response and info - generate_response returns (response, conversation, server_info, stats)
            if isinstance(response, tuple) and len(response) >= 4:
                enhanced_text = response[0]  # Main LLM response
                generation_stats = response[3]  # Generation statistics
                generation_info = f"Custom enhancement completed - {generation_stats}"
            else:
                enhanced_text = str(response)
                generation_info = "Custom enhancement completed"
            
            return enhanced_text, generation_info
            
        except Exception as e:
            return enhancement_context, f"Custom enhancement failed: {str(e)}"
    
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
__all__ = ["LMStudioChat"]
