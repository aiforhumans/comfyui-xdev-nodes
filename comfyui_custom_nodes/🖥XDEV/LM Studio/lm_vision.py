"""LM Studio Vision Model Node

Analyzes images and generates descriptions using vision models like Qwen3-VL.
"""

import base64
import json
import urllib.error
import urllib.request
from io import BytesIO
from typing import Any

try:
    from .lm_base_node import LMStudioBaseNode
    from .lm_model_manager import check_model_loaded
    from .lm_utils import (
        get_numpy,
        get_pil_image,
    )
except ImportError:
    from lm_base_node import LMStudioBaseNode
    from lm_model_manager import check_model_loaded
    from lm_utils import (
        get_numpy,
        get_pil_image,
    )


class LMStudioVision(LMStudioBaseNode):
    """Analyze images using LM Studio vision models."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "Describe this image in detail for use as an AI image generation prompt.", "multiline": True}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 300, "min": -1, "max": 4096, "step": 1}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "You are a vision AI that creates detailed, structured descriptions of images.", "multiline": True}),
                "response_format": (["text", "json"], {"default": "text"}),
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "model": ("STRING", {"default": "qwen/qwen3-vl-4b", "forceInput": True}),
                "detail_level": (["low", "high", "auto"], {"default": "auto"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("description", "prompt_ready", "info")
    FUNCTION = "analyze_image"
    DEFAULT_TIMEOUT = 120  # Vision models need more time

    def tensor_to_base64(self, image_tensor) -> str:
        """Convert ComfyUI image tensor to base64 string."""
        # ComfyUI images are in format [batch, height, width, channels] with values 0-1
        np = get_numpy()
        Image = get_pil_image()
        
        if isinstance(image_tensor, list):
            image_tensor = image_tensor[0]
        
        # Get first image from batch
        img_array = np.array(image_tensor)
        if len(img_array.shape) == 4:
            img_array = img_array[0]
        
        # Convert from 0-1 float to 0-255 uint8
        img_array = (img_array * 255).astype(np.uint8)
        
        # Convert to PIL Image for encoding
        img = Image.fromarray(img_array)
        
        # Convert to PNG in memory
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        
        # Encode to base64
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"

    def analyze_image(
        self,
        image,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
        system_prompt: str = "",
        response_format: str = "text",
        server_url: str = "http://localhost:1234",
        model: str = "qwen/qwen3-vl-4b",
        detail_level: str = "auto"
    ) -> tuple[str, str, str]:
        """Analyze image using LM Studio vision model with enhanced feedback."""
        
        # Initialize info output
        info_parts = []
        info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        info_parts.append("👁️ LM Studio Vision Analyzer")
        info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Check if model is already loaded (memory optimization hint)
        model_loaded, loaded_model, warning = check_model_loaded(server_url)
        if model_loaded:
            info_parts.append(f"🔵 Model: {loaded_model}")
            if warning:
                print(warning)
        else:
            info_parts.append("⚪ No model loaded")
        
        # Add parameters
        info_parts.append(f"🌡️ Temperature: {temperature}")
        info_parts.append(f"📏 Max Tokens: {max_tokens}")
        info_parts.append(f"🔍 Detail Level: {detail_level}")
        info_parts.append(f"📋 Format: {response_format.upper()}")
        
        # Convert image to base64
        info_parts.append("⏳ Processing image...")
        image_base64 = self.tensor_to_base64(image)
        
        if image_base64.startswith("Error"):
            error_msg = f"❌ Image Processing Error\n\n{image_base64}"
            info_parts.append("❌ Image conversion failed")
            return (error_msg, "", "\n".join(info_parts))
        
        # Build messages array with image
        messages = []
        if system_prompt:
            # Append JSON instruction if format is JSON (but don't use response_format param)
            sys_prompt = system_prompt
            if response_format == "json":
                sys_prompt += " Always respond with valid JSON format. Structure your response as a JSON object."
            messages.append({"role": "system", "content": sys_prompt})
        
        # Modify prompt for JSON if requested
        user_prompt = prompt
        if response_format == "json":
            user_prompt = f"{prompt}\n\nIMPORTANT: Return your response as a valid JSON object."
        
        # Add user message with text and image
        user_content = [
            {
                "type": "text",
                "text": user_prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_base64,
                    "detail": detail_level
                }
            }
        ]
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Build request payload
        # NOTE: Vision models don't support response_format parameter in LM Studio
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            info_parts.append("⏳ Analyzing image...")
            
            # Make API request
            url = f"{server_url}/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            # Extract generated description
            description = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not description:
                error_msg = "❌ Error: No response from LM Studio vision model"
                info_parts.append(error_msg)
                return (error_msg, "", "\n".join(info_parts))
            
            # Clean up description - remove extra whitespace
            description = description.strip()
            
            # Parse JSON if requested (vision models return JSON in text, not via response_format)
            if response_format == "json":
                try:
                    import re
                    # Try to extract JSON object from response
                    json_match = re.search(r'\{.*\}', description, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        parsed = json.loads(json_str)
                        # Keep the JSON as-is for description output
                        description = json.dumps(parsed, indent=2)
                        # Extract description field for prompt-ready if available
                        prompt_ready = parsed.get("description", parsed.get("prompt", description))
                    else:
                        # JSON not found, keep original
                        prompt_ready = description
                except (json.JSONDecodeError, Exception):
                    # If JSON parsing fails, use original text
                    prompt_ready = description
            else:
                # Create prompt-ready version (remove explanations, keep visual details)
                prompt_ready = description.strip()
            
            # Success info
            word_count = len(description.split())
            char_count = len(description)
            info_parts.append("✅ Analysis complete!")
            info_parts.append(f"📊 Output: ~{word_count} words, {char_count} chars")
            if response_format == "json":
                info_parts.append("📋 Parsed JSON response")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Format outputs with headers
            desc_output = f"{'='*60}\n"
            desc_output += "👁️ IMAGE ANALYSIS\n"
            desc_output += f"{'='*60}\n\n"
            desc_output += description
            desc_output += f"\n\n{'='*60}"
            
            # Prompt output is clean text only (no headers)
            prompt_output = prompt_ready
            
            return (desc_output, prompt_output, "\n".join(info_parts))
            
        except (urllib.error.URLError, ConnectionRefusedError, OSError) as e:
            error_msg = "❌ Connection Error\n\n"
            error_msg += f"Cannot connect to LM Studio at:\n{server_url}\n\n"
            error_msg += "🔧 Troubleshooting:\n"
            error_msg += "1. Make sure LM Studio is running\n"
            error_msg += "2. Check that Local Server is started\n"
            error_msg += "3. Load a VISION model (e.g., qwen3-vl-4b)\n"
            error_msg += "4. Vision models need more time to load\n"
            error_msg += f"5. Test: {server_url}/v1/models\n\n"
            error_msg += f"Details: {str(e)}"
            
            info_parts.append("❌ Connection failed")
            return (error_msg, "", "\n".join(info_parts))
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            error_msg = f"❌ HTTP Error {e.code}: {e.reason}\n\n"
            error_msg += f"Server response: {error_body}\n\n"
            error_msg += "🔧 Common causes:\n"
            error_msg += "• No vision model loaded (load a model like Qwen3-VL)\n"
            error_msg += "• Model doesn't support vision (check model capabilities)\n"
            error_msg += "• Image format issue (ComfyUI tensors should auto-convert)\n"
            error_msg += "• JSON format: Vision models use instruction-based JSON\n"
            error_msg += "  (not response_format parameter like text models)\n\n"
            error_msg += "💡 Tips:\n"
            error_msg += "1. Load a vision model in LM Studio (e.g., Qwen/Qwen3-VL)\n"
            error_msg += "2. Verify model supports image inputs\n"
            error_msg += "3. For JSON output: Model interprets JSON instructions from prompts"
            
            info_parts.append(f"❌ HTTP Error {e.code}")
            return (error_msg, "", "\n".join(info_parts))
            
        except json.JSONDecodeError as e:
            error_msg = "❌ Invalid Response\n\n"
            error_msg += "Server returned invalid JSON.\n"
            error_msg += "The vision model may still be loading.\n"
            error_msg += "Wait a moment and try again.\n\n"
            error_msg += f"Details: {str(e)}"
            
            info_parts.append("❌ Invalid response")
            return (error_msg, "", "\n".join(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return (error_msg, "", "\n".join(info_parts))


__all__ = ["LMStudioVision"]
