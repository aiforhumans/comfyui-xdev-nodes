"""LM Studio Prompt Enhancer Node

Takes a simple prompt and expands it into a detailed image generation prompt.
"""

from typing import Any

try:
    from .lm_base_node import LMStudioPromptBaseNode
    from .lm_utils import (
        ErrorFormatter,
        JSONParser,
        LMStudioAPIError,
        LMStudioConnectionError,
    )
    from .prompt_templates import (
        SDXL_SYSTEM_PROMPT,
        build_sdxl_instruction,
        get_detail_instruction,
    )
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode
    from lm_utils import (
        ErrorFormatter,
        JSONParser,
        LMStudioAPIError,
        LMStudioConnectionError,
    )
    from prompt_templates import (
        SDXL_SYSTEM_PROMPT,
        build_sdxl_instruction,
        get_detail_instruction,
    )


class LMStudioPromptEnhancer(LMStudioPromptBaseNode):
    """Enhance simple prompts into detailed image generation prompts."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "simple_prompt": ("STRING", {"default": "a cat", "multiline": True}),
                "style": (["realistic", "artistic", "fantasy", "sci-fi", "anime", "cinematic", "none"], {"default": "none"}),
                "detail_level": (["minimal", "moderate", "detailed", "very detailed"], {"default": "detailed"}),
                "temperature": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
            "optional": {
                "additional_details": ("STRING", {"default": "", "multiline": True}),
                "negative_prompt": ("BOOLEAN", {"default": False}),
                "response_format": (["text", "json"], {"default": "text"}),
                "server_url": ("STRING", {"default": "http://localhost:1234"}),
                "model": ("STRING", {"default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "info")
    FUNCTION = "enhance_prompt"

    def enhance_prompt(
        self,
        simple_prompt: str,
        style: str = "none",
        detail_level: str = "detailed",
        temperature: float = 0.8,
        additional_details: str = "",
        negative_prompt: bool = False,
        response_format: str = "text",
        server_url: str = "http://localhost:1234",
        model: str = ""
    ) -> tuple[str, str, str]:
        """Enhance a simple prompt using LM Studio with detailed feedback."""
        
        # Initialize info output using base class
        info_parts = self._init_info("SDXL Prompt Enhancer", "✨")
        info_parts.append(f"📝 Input: '{simple_prompt[:50]}{'...' if len(simple_prompt) > 50 else ''}''")
        
        # Add model info using base class
        self._add_model_info(info_parts, server_url)
        
        # Add enhancement parameters using base class
        params = {
            "detail_level": detail_level,
            "temperature": temperature,
            "format": response_format,
        }
        if style != "none":
            params["style"] = style
        if additional_details:
            params["additional_details"] = "provided"
        self._add_params_info(info_parts, **params)
        
        # Build enhancement instruction
        detail_instruction = get_detail_instruction(detail_level)
        instruction = build_sdxl_instruction(
            simple_prompt=simple_prompt,
            additional_details=additional_details,
            style=style,
            detail_instruction=detail_instruction,
            response_format=response_format,
            include_negative_prompt=negative_prompt,
        )
        
        try:
            info_parts.append("⏳ Enhancing prompt...")
            
            # Build messages using base class helper
            messages = self._build_messages(
                prompt=instruction,
                system_prompt=SDXL_SYSTEM_PROMPT,
                response_format="text"  # Don't use response_format param, use instruction-based JSON
            )
            
            # Make API request using base class helper
            generated = self._make_api_request(
                server_url=server_url,
                messages=messages,
                temperature=temperature,
                max_tokens=400,
                response_format="text",  # Don't use response_format param
                model=model,
                timeout=60
            )
            
            # Parse response based on format
            neg_prompt = ""
            
            if response_format == "json":
                # Use JSONParser utility for robust parsing
                parsed = JSONParser.parse_response(generated, expected_keys=["positive_prompt", "negative_prompt"])
                enhanced = JSONParser.extract_field(parsed, "positive_prompt", generated.strip())
                neg_prompt = JSONParser.extract_field(parsed, "negative_prompt", "")
            else:
                # Text format - try to split positive and negative if requested
                if negative_prompt:
                    # Look for negative prompt section
                    lines = generated.strip().split('\n')
                    enhanced_lines = []
                    neg_lines = []
                    in_negative = False
                    
                    for line in lines:
                        line_lower = line.lower()
                        if any(marker in line_lower for marker in ['negative prompt:', 'negative:', 'avoid:']):
                            in_negative = True
                            continue
                        
                        if in_negative:
                            neg_lines.append(line.strip())
                        else:
                            enhanced_lines.append(line.strip())
                    
                    enhanced = ", ".join([line for line in enhanced_lines if line])
                    neg_prompt = ", ".join([line for line in neg_lines if line])
                    
                    # Clean up any remaining labels
                    enhanced = enhanced.replace('Positive prompt:', '').replace('Positive:', '').strip()
                    neg_prompt = neg_prompt.replace('Negative prompt:', '').replace('Negative:', '').replace('Avoid:', '').strip()
                else:
                    enhanced = generated.strip()
            
            # Clean up the prompts - remove quotes, extra commas
            enhanced = enhanced.strip('"\' ').replace(',,', ',').strip(', ')
            neg_prompt = neg_prompt.strip('"\' ').replace(',,', ',').strip(', ')
            
            # Success info using base class
            info_parts.append("✅ Enhancement complete!")
            pos_words = len(enhanced.split(','))
            info_parts.append(f"📊 Positive: {pos_words} elements, {len(enhanced)} chars")
            if neg_prompt:
                neg_words = len(neg_prompt.split(','))
                info_parts.append(f"🚫 Negative: {neg_words} elements, {len(neg_prompt)} chars")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            return (enhanced, neg_prompt, self._format_info(info_parts))
            
        except LMStudioConnectionError as e:
            error_msg = ErrorFormatter.format_connection_error(server_url, str(e))
            info_parts.append("❌ Connection failed")
            return (error_msg, "", self._format_info(info_parts))
            
        except LMStudioAPIError as e:
            error_msg = ErrorFormatter.format_api_error(str(e))
            info_parts.append("❌ API error")
            return (error_msg, "", self._format_info(info_parts))
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error\n\n{str(e)}"
            info_parts.append(f"❌ Error: {str(e)}")
            return (error_msg, "", self._format_info(info_parts))