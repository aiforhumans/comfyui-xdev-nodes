"""
XDev LLM-Builder Nodes - Complete LM Studio Integration Suite
Provides comprehensive LM Studio integration for ComfyUI workflows
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin

# Graceful imports for HTTP clients
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

logger = logging.getLogger(__name__)

# =============================================================================
# 🧩 CORE LM STUDIO NODES
# =============================================================================

class XDEV_LMStudioChatAdvanced(ValidationMixin):
    """
    Advanced LM Studio Chat Node with full OpenAI API compatibility
    Supports streaming, all OpenAI parameters, and model selection
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True, 
                    "tooltip": "Main user message or conversation prompt"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234", 
                    "tooltip": "LM Studio server URL"
                }),
            },
            "optional": {
                "system_message": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "System instructions for the AI model"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model identifier (will fetch from /v1/models if available)"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1,
                    "tooltip": "Sampling temperature (0.0 = deterministic, 2.0 = very creative)"
                }),
                "max_tokens": ("INT", {
                    "default": 150, "min": 1, "max": 4096,
                    "tooltip": "Maximum tokens in response"
                }),
                "top_p": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1,
                    "tooltip": "Nucleus sampling parameter"
                }),
                "frequency_penalty": ("FLOAT", {
                    "default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1,
                    "tooltip": "Frequency penalty (-2.0 to 2.0)"
                }),
                "presence_penalty": ("FLOAT", {
                    "default": 0.0, "min": -2.0, "max": 2.0, "step": 0.1,
                    "tooltip": "Presence penalty (-2.0 to 2.0)"
                }),
                "streaming": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable streaming responses (experimental)"
                }),
                "message_history": ("STRING", {
                    "default": "[]",
                    "tooltip": "JSON array of conversation history [{'role': 'user', 'content': '...'}]"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("response", "full_conversation", "api_info")
    FUNCTION = "generate_chat"
    CATEGORY = "XDev/LLM-Builder/Core"
    DESCRIPTION = "Advanced LM Studio chat integration with full OpenAI API compatibility"

    @performance_monitor("lm_studio_chat_advanced")
    @cached_operation(ttl=300)
    def generate_chat(self, prompt, server_url, system_message="", model="local-model",
                     temperature=0.7, max_tokens=150, top_p=1.0, 
                     frequency_penalty=0.0, presence_penalty=0.0, streaming=False,
                     message_history="[]", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return ("", "", f"Validation Error: {validation['error']}")
        
        try:
            # Build message list
            messages = []
            
            # Add system message if provided
            if system_message.strip():
                messages.append({"role": "system", "content": system_message.strip()})
            
            # Parse history
            try:
                history = json.loads(message_history) if message_history.strip() else []
                if isinstance(history, list):
                    messages.extend(history)
            except json.JSONDecodeError:
                logger.warning("Invalid message_history JSON, ignoring")
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Prepare API request
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stream": streaming
            }
            
            # Make API call
            response_text, api_info = self._make_api_call(server_url, payload)
            
            # Build full conversation
            full_conversation = self._format_conversation(messages, response_text)
            
            return (response_text, full_conversation, api_info)
            
        except Exception as e:
            error_msg = f"LM Studio Chat Error: {str(e)}"
            logger.error(error_msg)
            return ("", "", error_msg)

    def _make_api_call(self, server_url: str, payload: Dict) -> Tuple[str, str]:
        """Make API call with fallback between httpx and requests"""
        
        url = f"{server_url.rstrip('/')}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        if HAS_HTTPX:
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        api_info = f"Model: {data.get('model', 'unknown')}, Tokens: {data.get('usage', {}).get('total_tokens', 'unknown')}"
                        return content, api_info
                    else:
                        return "", "Error: No response from model"
                        
            except Exception as e:
                if HAS_REQUESTS:
                    logger.warning(f"httpx failed, falling back to requests: {e}")
                else:
                    return "", f"HTTP Error: {str(e)}"
        
        if HAS_REQUESTS:
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    api_info = f"Model: {data.get('model', 'unknown')}, Tokens: {data.get('usage', {}).get('total_tokens', 'unknown')}"
                    return content, api_info
                else:
                    return "", "Error: No response from model"
                    
            except Exception as e:
                return "", f"HTTP Error: {str(e)}"
        
        return "", "Error: No HTTP client available (install httpx or requests)"

    def _format_conversation(self, messages: List[Dict], response: str) -> str:
        """Format conversation history for display"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown").title()
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        
        if response:
            formatted.append(f"Assistant: {response}")
        
        return "\n\n".join(formatted)


class XDEV_LMStudioEmbeddings(ValidationMixin):
    """
    LM Studio Embeddings Node - Convert text to vector embeddings
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "tooltip": "Text to convert to embeddings"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                })
            },
            "optional": {
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Embedding model identifier"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("embeddings_json", "dimensions_info", "api_info")
    FUNCTION = "generate_embeddings"
    CATEGORY = "XDev/LLM-Builder/Core"
    DESCRIPTION = "Generate text embeddings using LM Studio embedding models"

    @performance_monitor("lm_studio_embeddings")
    @cached_operation(ttl=600)
    def generate_embeddings(self, text, server_url, model="local-model", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(text, "text")
            if not validation["valid"]:
                return ("[]", "", f"Validation Error: {validation['error']}")
        
        try:
            url = f"{server_url.rstrip('/')}/v1/embeddings"
            payload = {
                "model": model,
                "input": text
            }
            headers = {"Content-Type": "application/json"}
            
            # Make API call
            if HAS_HTTPX:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
            elif HAS_REQUESTS:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                return ("[]", "", "Error: No HTTP client available")
            
            # Extract embeddings
            if "data" in data and len(data["data"]) > 0:
                embeddings = data["data"][0]["embedding"]
                embeddings_json = json.dumps(embeddings)
                dimensions = len(embeddings)
                
                api_info = f"Model: {data.get('model', model)}, Dimensions: {dimensions}, Tokens: {data.get('usage', {}).get('total_tokens', 'unknown')}"
                dimensions_info = f"Vector dimensions: {dimensions}, Length: {len(text)} characters"
                
                return (embeddings_json, dimensions_info, api_info)
            else:
                return ("[]", "", "Error: No embeddings returned from API")
                
        except Exception as e:
            error_msg = f"Embeddings Error: {str(e)}"
            logger.error(error_msg)
            return ("[]", "", error_msg)


class XDEV_LMStudioCompletions(ValidationMixin):
    """
    LM Studio Completions Node - Simple text completion (no chat format)
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "tooltip": "Text prompt for completion"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                })
            },
            "optional": {
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model identifier"
                }),
                "max_tokens": ("INT", {
                    "default": 150, "min": 1, "max": 4096,
                    "tooltip": "Maximum tokens to generate"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1,
                    "tooltip": "Sampling temperature"
                }),
                "top_p": ("FLOAT", {
                    "default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1,
                    "tooltip": "Nucleus sampling parameter"
                }),
                "stop_sequences": ("STRING", {
                    "default": "",
                    "tooltip": "JSON array of stop sequences ['\\n', '###']"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("completion", "api_info")
    FUNCTION = "generate_completion"
    CATEGORY = "XDev/LLM-Builder/Core"
    DESCRIPTION = "Simple text completion using LM Studio (no chat formatting)"

    @performance_monitor("lm_studio_completions")
    @cached_operation(ttl=300)
    def generate_completion(self, prompt, server_url, model="local-model",
                          max_tokens=150, temperature=0.7, top_p=1.0,
                          stop_sequences="", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return ("", f"Validation Error: {validation['error']}")
        
        try:
            # Parse stop sequences
            stop = []
            if stop_sequences.strip():
                try:
                    stop = json.loads(stop_sequences)
                    if not isinstance(stop, list):
                        stop = [str(stop_sequences)]
                except json.JSONDecodeError:
                    stop = [stop_sequences]
            
            url = f"{server_url.rstrip('/')}/v1/completions"
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if stop:
                payload["stop"] = stop
            
            headers = {"Content-Type": "application/json"}
            
            # Make API call
            if HAS_HTTPX:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
            elif HAS_REQUESTS:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                return ("", "Error: No HTTP client available")
            
            # Extract completion
            if "choices" in data and len(data["choices"]) > 0:
                completion = data["choices"][0]["text"]
                api_info = f"Model: {data.get('model', model)}, Tokens: {data.get('usage', {}).get('total_tokens', 'unknown')}"
                return (completion, api_info)
            else:
                return ("", "Error: No completion returned from API")
                
        except Exception as e:
            error_msg = f"Completions Error: {str(e)}"
            logger.error(error_msg)
            return ("", error_msg)


# =============================================================================
# 🔗 WORKFLOW INTEGRATION NODES  
# =============================================================================

# Prompt classes moved to prompts/llm_enhanced/
class XDEV_ImageCaptioningLLM(ValidationMixin):
    """
    Image Captioning via LLM - Enhance captions using LM Studio
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "base_caption": ("STRING", {
                    "multiline": True,
                    "tooltip": "Base caption from CLIP interrogator or other source"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                })
            },
            "optional": {
                "enhancement_style": (["expand_details", "artistic_description", "technical_analysis", "story_context", "prompt_optimization"], {
                    "default": "expand_details",
                    "tooltip": "How to enhance the caption"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "LM Studio model to use"
                }),
                "max_tokens": ("INT", {
                    "default": 200, "min": 50, "max": 1000,
                    "tooltip": "Maximum tokens for enhanced caption"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 1.5, "step": 0.1,
                    "tooltip": "Creativity level"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("enhanced_caption", "original_caption", "enhancement_info")
    FUNCTION = "enhance_caption"
    CATEGORY = "XDev/LLM-Builder/Workflow"
    DESCRIPTION = "Enhance image captions using LM Studio for better prompts"

    # Enhancement prompts for different styles
    _ENHANCEMENT_PROMPTS = {
        "expand_details": "Expand this image description with more specific visual details, colors, lighting, and composition elements:",
        "artistic_description": "Rewrite this image description in a more artistic and evocative style, emphasizing mood and atmosphere:",
        "technical_analysis": "Analyze this image description and add technical photography details like camera settings, lighting setup, and composition techniques:",
        "story_context": "Create a narrative context around this image description, adding story elements and emotional depth:",
        "prompt_optimization": "Optimize this image description specifically for AI image generation, using effective prompt keywords and structure:"
    }

    @performance_monitor("image_captioning_llm")
    @cached_operation(ttl=300)
    def enhance_caption(self, base_caption, server_url, enhancement_style="expand_details",
                       model="local-model", max_tokens=200, temperature=0.7, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(base_caption, "base_caption")
            if not validation["valid"]:
                return ("", base_caption, f"Validation Error: {validation['error']}")
        
        try:
            # Get enhancement prompt
            system_prompt = self._ENHANCEMENT_PROMPTS.get(enhancement_style, 
                                                        self._ENHANCEMENT_PROMPTS["expand_details"])
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": base_caption}
            ]
            
            # Prepare API call
            url = f"{server_url.rstrip('/')}/v1/chat/completions"
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            headers = {"Content-Type": "application/json"}
            
            # Make API call
            if HAS_HTTPX:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
            elif HAS_REQUESTS:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                return (base_caption, base_caption, "Error: No HTTP client available")
            
            # Extract enhanced caption
            if "choices" in data and len(data["choices"]) > 0:
                enhanced_caption = data["choices"][0]["message"]["content"].strip()
                
                # Enhancement info
                enhancement_info = f"Style: {enhancement_style}, Original length: {len(base_caption)}, Enhanced length: {len(enhanced_caption)}"
                
                return (enhanced_caption, base_caption, enhancement_info)
            else:
                return (base_caption, base_caption, "Error: No response from LLM")
                
        except Exception as e:
            error_msg = f"Caption Enhancement Error: {str(e)}"
            logger.error(error_msg)
            return (base_caption, base_caption, error_msg)
