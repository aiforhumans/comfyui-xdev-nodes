"""LM Studio Batch Processor Node

Process multiple prompts efficiently in batch.
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


class LMStudioBatchProcessor(LMStudioTextBaseNode):
    """Process multiple prompts in batch with efficiency optimizations."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "prompts": ("STRING", {"default": "prompt1\nprompt2\nprompt3", "multiline": True, "tooltip": "One prompt per line"}),
            },
            "optional": {
                "system_prompt": ("STRING", {"default": "You are a helpful AI assistant.", "multiline": True}),
                "batch_delay": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 5.0, "step": 0.1, "tooltip": "Delay between requests (seconds)"}),
                **cls.get_common_optional_inputs(),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("results_json", "results_text", "info")
    FUNCTION = "process_batch"
    
    # Enable batch processing optimization
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = False

    def process_batch(
        self,
        prompts: str,
        temperature: float = 0.7,
        max_tokens: int = 200,
        system_prompt: str = "",
        server_url: str = "http://localhost:1234",
        model: str = "",
        batch_delay: float = 0.1
    ) -> tuple[str, str, str]:
        """Process multiple prompts in batch."""
        
        info_parts = self._init_info("Batch Processor", "📦")
        
        # Parse prompts (one per line)
        prompt_list = [p.strip() for p in prompts.split('\n') if p.strip()]
        
        if not prompt_list:
            error_msg = "❌ Error: No prompts provided"
            info_parts.append(error_msg)
            return ("[]", "", self._format_info(info_parts))
        
        info_parts.append(f"📊 Prompts: {len(prompt_list)}")
        self._add_model_info(info_parts, server_url)
        
        info_parts.append(f"🌡️ Temperature: {temperature}")
        info_parts.append(f"📏 Max Tokens: {max_tokens}")
        if batch_delay > 0:
            info_parts.append(f"⏱️ Delay: {batch_delay}s")
        
        results = []
        successful = 0
        failed = 0
        start_time = time.time()
        
        try:
            for i, prompt in enumerate(prompt_list, 1):
                info_parts.append(f"⏳ Processing {i}/{len(prompt_list)}...")
                
                # Build request
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                payload = {
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
                
                if model:
                    payload["model"] = model
                
                try:
                    # Make API request
                    url = f"{server_url}/v1/chat/completions"
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(payload).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    with urllib.request.urlopen(req, timeout=60) as response:
                        result = json.loads(response.read().decode('utf-8'))
                    
                    generated = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    if generated:
                        results.append({
                            "prompt": prompt,
                            "result": generated.strip(),
                            "status": "success"
                        })
                        successful += 1
                    else:
                        results.append({
                            "prompt": prompt,
                            "result": "",
                            "status": "error",
                            "error": "No response"
                        })
                        failed += 1
                
                except Exception as e:
                    results.append({
                        "prompt": prompt,
                        "result": "",
                        "status": "error",
                        "error": str(e)
                    })
                    failed += 1
                
                # Update progress
                try:
                    from comfy_api.latest import Execution
                    Execution.set_progress(value=i, max_value=len(prompt_list))
                except (ImportError, Exception):
                    pass
                
                # Delay between requests
                if i < len(prompt_list) and batch_delay > 0:
                    time.sleep(batch_delay)
            
            elapsed = time.time() - start_time
            
            # Format results
            results_json = json.dumps(results, indent=2)
            
            results_text = ""
            for i, result in enumerate(results, 1):
                status_emoji = "✅" if result["status"] == "success" else "❌"
                results_text += f"{status_emoji} Prompt {i}\n"
                results_text += f"Input: {result['prompt'][:50]}...\n"
                if result["status"] == "success":
                    results_text += f"Output: {result['result'][:100]}...\n"
                else:
                    results_text += f"Error: {result.get('error', 'Unknown')}\n"
                results_text += "\n" + "─" * 50 + "\n\n"
            
            # Summary
            info_parts[-1] = "✅ Batch complete!"
            info_parts.append(f"📊 Success: {successful}/{len(prompt_list)}")
            if failed > 0:
                info_parts.append(f"❌ Failed: {failed}/{len(prompt_list)}")
            info_parts.append(f"⏱️ Time: {elapsed:.2f}s")
            info_parts.append(f"⚡ Avg: {elapsed/len(prompt_list):.2f}s per prompt")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return (results_json, results_text, "\n".join(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Batch Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return ("[]", error_msg, "\n".join(info_parts))


__all__ = ["LMStudioBatchProcessor"]
