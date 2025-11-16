"""LM Studio Prompt Mixer Node

Intelligently blends two prompts with different blending modes and strategies.
Uses LM Studio's text generation to create coherent merged prompts.
"""

try:
    from .lm_base_node import LMStudioPromptBaseNode
    from .lm_utils import JSONParser, ErrorFormatter
    from .lm_model_manager import check_model_loaded
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode
    from lm_utils import JSONParser, ErrorFormatter
    from lm_model_manager import check_model_loaded


class LMStudioPromptMixer(LMStudioPromptBaseNode):
    """
    Blends two prompts together using LM Studio's AI.
    Supports multiple blending modes: merge, alternate, hybrid.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_a": ("STRING", {"multiline": True, "default": ""}),
                "prompt_b": ("STRING", {"multiline": True, "default": ""}),
                "blend_ratio": ("INT", {"default": 50, "min": 0, "max": 100, "step": 5}),
                "blend_mode": (["merge", "alternate", "hybrid", "creative_fusion"], {"default": "merge"}),
            },
            "optional": {
                **cls.get_common_optional_inputs(),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("mixed_prompt", "element_breakdown", "info")
    FUNCTION = "mix_prompts"
    
    def mix_prompts(self, prompt_a: str, prompt_b: str, blend_ratio: int, blend_mode: str,
                    temperature: float = 0.7, server_url: str = "http://localhost:1234", model: str = "") -> tuple:
        """Mix two prompts using AI-powered blending."""
        
        # Check if model is loaded
        check_model_loaded()
        
        # Validate inputs
        if not prompt_a.strip() and not prompt_b.strip():
            return ("", "No prompts provided", "⚠️ Error: Both prompts are empty")
        
        if not prompt_a.strip():
            return (prompt_b, "Only Prompt B provided", f"ℹ️ Using Prompt B only\nRatio: {blend_ratio}%")
        
        if not prompt_b.strip():
            return (prompt_a, "Only Prompt A provided", f"ℹ️ Using Prompt A only\nRatio: {blend_ratio}%")
        
        # Build system prompt based on blend mode
        system_prompts = {
            "merge": f"""You are a prompt mixing expert. Blend the two prompts into a single coherent prompt.

Blend Ratio: {blend_ratio}% towards Prompt B (0% = all A, 100% = all B)

Instructions:
- At {blend_ratio}%, emphasize elements from Prompt B proportionally
- Maintain natural language flow
- Combine complementary elements
- Remove redundant or conflicting elements
- Keep the result concise and focused

Respond with JSON:
{{"mixed_prompt": "the blended prompt", "elements_from_a": ["element1", "element2"], "elements_from_b": ["element3", "element4"], "reasoning": "brief explanation"}}""",
            
            "alternate": f"""You are a prompt mixing expert. Create a prompt that alternates between elements of both prompts.

Blend Ratio: {blend_ratio}% towards Prompt B

Instructions:
- Alternate key elements from both prompts
- At {blend_ratio}%, include more elements from Prompt B
- Create rhythm and balance
- Maintain logical flow
- Ensure complementary concepts work together

Respond with JSON:
{{"mixed_prompt": "the alternating prompt", "elements_from_a": ["element1", "element2"], "elements_from_b": ["element3", "element4"], "reasoning": "brief explanation"}}""",
            
            "hybrid": f"""You are a prompt mixing expert. Create a hybrid prompt that merges the core concepts of both prompts into something new.

Blend Ratio: {blend_ratio}% towards Prompt B

Instructions:
- Identify core concepts in each prompt
- Synthesize them into a unified concept
- At {blend_ratio}%, weight towards Prompt B's concepts
- Create something cohesive, not just concatenated
- Maintain artistic coherence

Respond with JSON:
{{"mixed_prompt": "the hybrid prompt", "elements_from_a": ["element1", "element2"], "elements_from_b": ["element3", "element4"], "reasoning": "brief explanation"}}""",
            
            "creative_fusion": f"""You are a prompt mixing expert. Creatively fuse both prompts into something unexpected and innovative.

Blend Ratio: {blend_ratio}% towards Prompt B

Instructions:
- Look for creative connections between the prompts
- Generate surprising but logical combinations
- At {blend_ratio}%, favor Prompt B's themes
- Take artistic risks while maintaining coherence
- Aim for "what if" scenarios and mashups

Respond with JSON:
{{"mixed_prompt": "the creatively fused prompt", "elements_from_a": ["element1", "element2"], "elements_from_b": ["element3", "element4"], "reasoning": "brief explanation"}}"""
        }
        
        system_prompt = system_prompts.get(blend_mode, system_prompts["merge"])
        
        user_prompt = f"""Prompt A (Weight: {100-blend_ratio}%):
{prompt_a}

Prompt B (Weight: {blend_ratio}%):
{prompt_b}

Create the blended prompt following the instructions."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Use base class API request
            result = self._make_api_request(server_url, messages, temperature, 1000, model)
            response_text = result['choices'][0]['message']['content']
            
            # Parse JSON response using utility
            parsed = JSONParser.parse_response(response_text)
            
            if parsed:
                mixed_prompt = parsed.get("mixed_prompt", "")
                elements_a = parsed.get("elements_from_a", [])
                elements_b = parsed.get("elements_from_b", [])
                reasoning = parsed.get("reasoning", "")
                
                # Build element breakdown
                breakdown = f"""Prompt A Elements ({100-blend_ratio}%):
{', '.join(elements_a) if elements_a else 'None extracted'}

Prompt B Elements ({blend_ratio}%):
{', '.join(elements_b) if elements_b else 'None extracted'}

Blending Strategy: {blend_mode}
{reasoning}"""
                
                # Build info string
                info = f"""Mode: {blend_mode}
Ratio: {100-blend_ratio}% A / {blend_ratio}% B
Temperature: {temperature}
Elements from A: {len(elements_a)}
Elements from B: {len(elements_b)}"""
                
                return (mixed_prompt, breakdown, info)
            else:
                # Fallback to raw text if JSON parsing fails
                mixed_prompt = response_text.strip()
                info = f"""Mode: {blend_mode}
Ratio: {100-blend_ratio}% A / {blend_ratio}% B
Temperature: {temperature}
⚠️ JSON parsing failed, using raw text"""
                
                return (mixed_prompt, "Unable to parse element breakdown", info)
        
        except Exception as e:
            error_msg = ErrorFormatter.format_api_error(e, "mix prompts")
            return ("", "", error_msg)


__all__ = ["LMStudioPromptMixer"]
