"""LM Studio Context Optimizer Node

Truncates and optimizes context to fit within token limits.
"""

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode

from typing import Any


class LMStudioContextOptimizer(LMStudioUtilityBaseNode):
    """Optimize context length using smart truncation strategies."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                "max_tokens": ("INT", {"default": 2000, "min": 100, "max": 100000, "step": 100}),
                "strategy": (["end", "middle", "smart", "summarize"], {"default": "smart"}),
            },
            "optional": {
                "preserve_start": ("INT", {"default": 500, "min": 0, "max": 10000, "tooltip": "Tokens to keep from start"}),
                "preserve_end": ("INT", {"default": 500, "min": 0, "max": 10000, "tooltip": "Tokens to keep from end"}),
                "chars_per_token": ("FLOAT", {"default": 4.0, "min": 1.0, "max": 10.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("optimized_text", "original_tokens", "optimized_tokens", "info")
    FUNCTION = "optimize_context"

    def optimize_context(
        self,
        text: str,
        max_tokens: int = 2000,
        strategy: str = "smart",
        preserve_start: int = 500,
        preserve_end: int = 500,
        chars_per_token: float = 4.0
    ) -> tuple[str, int, int, str]:
        """Optimize context using specified strategy."""
        
        info_parts = self._init_info("Context Optimizer", "✂️")
        info_parts.append(f"📏 Strategy: {strategy}")
        info_parts.append(f"🎯 Target: {max_tokens} tokens")
        
        if not text:
            info_parts.append("⚠️ Empty text")
            return ("", 0, 0, self._format_info(info_parts))
        
        # Estimate original tokens
        original_tokens = int(len(text) / chars_per_token)
        info_parts.append(f"📊 Original: ~{original_tokens} tokens")
        
        # Check if optimization needed
        if original_tokens <= max_tokens:
            info_parts.append("✅ Already within limit")
            return (text, original_tokens, original_tokens, self._format_info(info_parts))
        
        # Calculate target character count
        target_chars = int(max_tokens * chars_per_token)
        
        optimized_text = text
        
        # Apply truncation strategy
        if strategy == "end":
            # Keep from start
            optimized_text = text[:target_chars]
            if len(optimized_text) < len(text):
                optimized_text += "\n\n[... truncated]"
            info_parts.append("✂️ Kept beginning")
            
        elif strategy == "middle":
            # Remove middle, keep start and end
            start_chars = int(target_chars * 0.5)
            end_chars = target_chars - start_chars
            
            optimized_text = text[:start_chars]
            optimized_text += "\n\n[... middle section truncated ...]\n\n"
            optimized_text += text[-end_chars:]
            info_parts.append("✂️ Removed middle")
            
        elif strategy == "smart":
            # Smart truncation: preserve specified amounts from start/end
            start_chars = int(preserve_start * chars_per_token)
            end_chars = int(preserve_end * chars_per_token)
            
            # Ensure we don't exceed target
            total_preserve = start_chars + end_chars
            if total_preserve > target_chars:
                # Scale down proportionally
                scale = target_chars / total_preserve
                start_chars = int(start_chars * scale)
                end_chars = int(end_chars * scale)
            
            if start_chars + end_chars >= len(text):
                optimized_text = text
            else:
                optimized_text = text[:start_chars]
                optimized_text += f"\n\n[... {len(text) - start_chars - end_chars} chars truncated ...]\n\n"
                optimized_text += text[-end_chars:]
            
            info_parts.append(f"✂️ Smart: {preserve_start}+{preserve_end} tokens")
            
        elif strategy == "summarize":
            # Simple summarization (keep first and last sentences of paragraphs)
            paragraphs = text.split('\n\n')
            
            summarized = []
            chars_used = 0
            
            for para in paragraphs:
                sentences = [s.strip() for s in para.split('.') if s.strip()]
                if not sentences:
                    continue
                
                # Keep first and last sentence of each paragraph
                if len(sentences) == 1:
                    summary = sentences[0] + '.'
                else:
                    summary = sentences[0] + '. ... ' + sentences[-1] + '.'
                
                if chars_used + len(summary) > target_chars:
                    break
                
                summarized.append(summary)
                chars_used += len(summary) + 2  # +2 for \n\n
            
            optimized_text = '\n\n'.join(summarized)
            if len(summarized) < len(paragraphs):
                optimized_text += "\n\n[... remaining paragraphs truncated]"
            
            info_parts.append("✂️ Summarized paragraphs")
        
        # Calculate optimized tokens
        optimized_tokens = int(len(optimized_text) / chars_per_token)
        reduction_pct = ((original_tokens - optimized_tokens) / original_tokens) * 100
        
        info_parts.append(f"📊 Optimized: ~{optimized_tokens} tokens")
        info_parts.append(f"📉 Reduced: {reduction_pct:.1f}%")
        info_parts.append(f"📝 Chars: {len(text)} → {len(optimized_text)}")
        
        if optimized_tokens <= max_tokens:
            info_parts.append("✅ Within target limit")
        else:
            info_parts.append(f"⚠️ Still exceeds by ~{optimized_tokens - max_tokens}")
        
        return (optimized_text, original_tokens, optimized_tokens, self._format_info(info_parts))


__all__ = ["LMStudioContextOptimizer"]
