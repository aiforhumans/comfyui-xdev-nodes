"""LM Studio Token Counter Node

Estimates token usage for prompts before API calls.
"""

from typing import Any

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode


class LMStudioTokenCounter(LMStudioUtilityBaseNode):
    """Estimate token count for prompts to manage costs and limits."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                "estimation_method": (["rough", "whitespace", "chars_per_token"], {"default": "rough"}),
            },
            "optional": {
                "chars_per_token": ("FLOAT", {"default": 4.0, "min": 1.0, "max": 10.0, "step": 0.1, "tooltip": "Average characters per token"}),
                "context_limit": ("INT", {"default": 4096, "min": 0, "max": 128000, "tooltip": "Model context window"}),
                "max_completion": ("INT", {"default": 500, "min": 0, "max": 4096, "tooltip": "Planned completion tokens"}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("estimated_tokens", "available_tokens", "within_limit", "warning", "info")
    FUNCTION = "count_tokens"

    def count_tokens(
        self,
        text: str,
        estimation_method: str = "rough",
        chars_per_token: float = 4.0,
        context_limit: int = 4096,
        max_completion: int = 500
    ) -> tuple[int, int, bool, str, str]:
        """Estimate token count using various methods."""
        
        info_parts = self._init_info("Token Counter", "🔢")
        info_parts.append(f"📏 Method: {estimation_method}")
        
        if not text:
            info_parts.append("⚠️ Empty text")
            info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            return (0, context_limit, True, "", self._format_info(info_parts))
        
        # Estimate tokens
        if estimation_method == "rough":
            # Rough estimate: ~1 token per 4 characters for English
            estimated_tokens = len(text) // 4
            info_parts.append("📝 Rough: ~4 chars/token")
            
        elif estimation_method == "whitespace":
            # Word-based estimate: ~1.3 tokens per word
            words = len(text.split())
            estimated_tokens = int(words * 1.3)
            info_parts.append(f"📝 Words: {words} × 1.3")
            
        elif estimation_method == "chars_per_token":
            # Custom chars per token
            estimated_tokens = int(len(text) / chars_per_token)
            info_parts.append(f"📝 Custom: {chars_per_token} chars/token")
        
        else:
            estimated_tokens = len(text) // 4
        
        # Calculate available tokens
        total_needed = estimated_tokens + max_completion
        available_tokens = context_limit - estimated_tokens
        within_limit = total_needed <= context_limit
        
        # Generate warning if needed
        warning = ""
        if not within_limit:
            overflow = total_needed - context_limit
            warning = (
                f"⚠️ TOKEN LIMIT EXCEEDED\n\n"
                f"Prompt: ~{estimated_tokens} tokens\n"
                f"Completion: {max_completion} tokens\n"
                f"Total needed: {total_needed} tokens\n"
                f"Context limit: {context_limit} tokens\n"
                f"Overflow: {overflow} tokens\n\n"
                f"💡 Solutions:\n"
                f"1. Reduce prompt length by {overflow} tokens\n"
                f"2. Decrease max_completion tokens\n"
                f"3. Use a model with larger context window"
            )
        elif available_tokens < max_completion * 0.5:
            warning = (
                f"⚠️ Low available tokens\n"
                f"Available: {available_tokens} tokens\n"
                f"May limit completion quality"
            )
        
        # Build info
        info_parts.append(f"📊 Input: ~{estimated_tokens} tokens")
        info_parts.append(f"📊 Chars: {len(text)}")
        info_parts.append(f"📊 Completion: {max_completion} tokens")
        info_parts.append(f"📊 Total: ~{total_needed} tokens")
        info_parts.append("─" * 28)
        info_parts.append(f"🎯 Context Limit: {context_limit}")
        info_parts.append(f"✓ Available: {available_tokens} tokens")
        
        if within_limit:
            usage_pct = (total_needed / context_limit) * 100
            info_parts.append(f"✅ Within limit ({usage_pct:.1f}%)")
        else:
            info_parts.append("❌ Exceeds limit!")
        
        info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return (estimated_tokens, available_tokens, within_limit, warning, self._format_info(info_parts))


__all__ = ["LMStudioTokenCounter"]
