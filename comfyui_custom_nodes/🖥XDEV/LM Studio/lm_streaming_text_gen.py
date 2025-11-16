"""LM Studio Streaming Text Generator Node

Generates text with real-time streaming feedback and progress updates.
"""

try:
    from .lm_base_node import LMStudioTextBaseNode
except ImportError:
    from lm_base_node import LMStudioTextBaseNode

import json
import time
import urllib.error
import urllib.request
from typing import Any


class LMStudioStreamingTextGen(LMStudioTextBaseNode):
    """Generate text with streaming updates using LM Studio API."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "prompt": ("STRING", {"default": "Write a creative story about:", "multiline": True}),
                "user_input": ("STRING", {"default": "a time traveler", "multiline": True}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "You are a creative AI assistant.", "multiline": True}),
                **cls.get_common_optional_inputs(),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("generated_text", "token_count", "info")
    FUNCTION = "stream_generate"

    def stream_generate(
        self,
        prompt: str,
        user_input: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: str = "",
        server_url: str = "http://localhost:1234",
        model: str = "",
        seed: int = -1
    ) -> tuple[str, str, str]:
        """Generate text with streaming and progress updates."""
        
        # Initialize info using base class helper
        info_parts = self._init_info("Streaming Text Generator", "🌊")
        self._add_model_info(info_parts, server_url)
        self._add_params_info(info_parts, temperature, max_tokens, seed)
        
        # Build request
        full_prompt = f"{prompt}\n\n{user_input}" if user_input else prompt
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": full_prompt})
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True  # Enable streaming
        }
        
        if model:
            payload["model"] = model
        if seed >= 0:
            payload["seed"] = seed
        
        try:
            info_parts.append("⏳ Streaming generation...")
            start_time = time.time()
            
            url = f"{server_url}/v1/chat/completions"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                }
            )
            
            generated_text = ""
            token_count = 0
            last_update = time.time()
            
            with urllib.request.urlopen(req, timeout=120) as response:
                # Read streaming response line by line
                for line in response:
                    line = line.decode('utf-8').strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # SSE format: "data: {json}"
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        # Check for stream end
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                generated_text += content
                                token_count += 1
                                
                                # Update progress every 0.5 seconds
                                now = time.time()
                                if now - last_update >= 0.5:
                                    try:
                                        # Try to use ComfyUI progress API if available
                                        from comfy_api.latest import Execution
                                        Execution.set_progress(
                                            value=token_count,
                                            max_value=max_tokens
                                        )
                                    except (ImportError, Exception):
                                        # Fallback: just print progress
                                        print(f"⏳ Generated {token_count} tokens...")
                                    last_update = now
                        
                        except json.JSONDecodeError:
                            continue
            
            elapsed = time.time() - start_time
            tokens_per_sec = token_count / elapsed if elapsed > 0 else 0
            
            if not generated_text:
                error_msg = "❌ Error: No response from streaming API"
                info_parts.append(error_msg)
                return (error_msg, "0", "\n".join(info_parts))
            
            # Success info
            info_parts.append("✅ Streaming complete!")
            info_parts.append(f"📊 Tokens: {token_count}")
            info_parts.append(f"⏱️ Time: {elapsed:.2f}s")
            info_parts.append(f"⚡ Speed: {tokens_per_sec:.1f} tok/s")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return (generated_text.strip(), str(token_count), "\n".join(info_parts))
            
        except (urllib.error.URLError, ConnectionRefusedError, OSError) as e:
            error_msg = "❌ Connection Error\n\n"
            error_msg += f"Cannot connect to LM Studio at: {server_url}\n\n"
            error_msg += "🔧 Troubleshooting:\n"
            error_msg += "1. Make sure LM Studio is running\n"
            error_msg += "2. Check that Local Server is started\n"
            error_msg += "3. Verify streaming is supported by model\n"
            error_msg += f"4. Test: {server_url}/v1/models\n\n"
            error_msg += f"Details: {str(e)}"
            
            info_parts.append("❌ Connection failed")
            return (error_msg, "0", "\n".join(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return (error_msg, "0", "\n".join(info_parts))


__all__ = ["LMStudioStreamingTextGen"]
