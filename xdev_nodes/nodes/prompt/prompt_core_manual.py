"""
Core prompt combination and weighting functionality
Part of the XDev Nodes modular architecture.
"""

import re
import random
from typing import Dict, List, Tuple, Any, Optional, Union
from collections import Counter
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin
from ...categories import NodeCategories


# ----- PromptCombiner -----
class PromptCombiner(ValidationMixin):
    DISPLAY_NAME = "Prompt Combiner (XDev)"
    """
    Combine multiple prompts with advanced weighting and formatting options.
    Supports prompt merging, weighting, and intelligent concatenation.
    """
    
    # Precomputed combination strategies
    _COMBINATION_MODES = {
        "concatenate": lambda prompts, sep: sep.join(p.strip() for p in prompts if p.strip()),
        "weighted_merge": lambda prompts, weights: ", ".join(f"({p.strip()}:{w})" for p, w in zip(prompts, weights) if p.strip()),
        "alternating": lambda prompts, sep: sep.join(prompts[i].strip() for i in range(len(prompts)) if prompts[i].strip()),
        "priority_merge": lambda prompts, sep: sep.join(sorted([p.strip() for p in prompts if p.strip()], key=len, reverse=True)),
    }
    
    # Common separators with descriptions
    _SEPARATORS = {
        "comma": ", ",
        "space": " ",
        "newline": "\n",
        "pipe": " | ",
        "semicolon": "; ",
        "custom": ""
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt_1": ("STRING", {"default": "", "multiline": True, "tooltip": "First prompt to combine"}),
                "prompt_2": ("STRING", {"default": "", "multiline": True, "tooltip": "Second prompt to combine"}),
                "mode": (list(cls._COMBINATION_MODES.keys()), {"default": "concatenate", "tooltip": "How to combine prompts"}),
                "separator": (list(cls._SEPARATORS.keys()), {"default": "comma", "tooltip": "Separator between prompts"})
            },
            "optional": {
                "prompt_3": ("STRING", {"default": "", "multiline": True, "tooltip": "Optional third prompt"}),
                "prompt_4": ("STRING", {"default": "", "multiline": True, "tooltip": "Optional fourth prompt"}),
                "weight_1": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1, "tooltip": "Weight for prompt 1 (weighted_merge mode)"}),
                "weight_2": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1, "tooltip": "Weight for prompt 2 (weighted_merge mode)"}),
                "weight_3": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1, "tooltip": "Weight for prompt 3 (weighted_merge mode)"}),
                "weight_4": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1, "tooltip": "Weight for prompt 4 (weighted_merge mode)"}),
                "custom_separator": ("STRING", {"default": ", ", "tooltip": "Custom separator (when separator=custom)"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("combined_prompt", "combination_info", "total_prompts")
    FUNCTION = "combine_prompts"
    CATEGORY = NodeCategories.PROMPT_COMBINATION
    DESCRIPTION = "Combine multiple prompts with advanced weighting and formatting"
    
    @performance_monitor("prompt_combination")
    @cached_operation(ttl=600)
    def combine_prompts(self, prompt_1: str, prompt_2: str, mode: str, separator: str,
                       prompt_3: str = "", prompt_4: str = "", 
                       weight_1: float = 1.0, weight_2: float = 1.0, 
                       weight_3: float = 1.0, weight_4: float = 1.0,
                       custom_separator: str = ", ", validate_input: bool = True):
        
        if validate_input:
            # Validate all string inputs
            for i, prompt in enumerate([prompt_1, prompt_2, prompt_3, prompt_4], 1):
                validation = self.validate_string_input(prompt, f"prompt_{i}", allow_empty=True)
                if not validation["valid"]:
                    return (f"Error: {validation['error']}", "validation_failed", 0)
        
        # Collect non-empty prompts
        prompts = [p for p in [prompt_1, prompt_2, prompt_3, prompt_4] if p.strip()]
        weights = [weight_1, weight_2, weight_3, weight_4][:len(prompts)]
        
        if not prompts:
            return ("", "No valid prompts provided", 0)
        
        # Get separator
        sep = self._SEPARATORS.get(separator, custom_separator if separator == "custom" else ", ")
        
        # Combine prompts using selected mode
        try:
            if mode == "weighted_merge" and len(prompts) > 1:
                combined = self._COMBINATION_MODES[mode](prompts, weights)
            else:
                combined = self._COMBINATION_MODES[mode](prompts, sep)
            
            # Generate info string
            info = f"Combined {len(prompts)} prompts using '{mode}' mode with '{separator}' separator"
            if mode == "weighted_merge":
                info += f" (weights: {', '.join(f'{w:.1f}' for w in weights)})"
            
            return (combined, info, len(prompts))
            
        except Exception as e:
            return (f"Error: {str(e)}", "combination_failed", 0)


# ----- PromptWeighter -----  
class PromptWeighter(ValidationMixin):
    DISPLAY_NAME = "Prompt Weighter (XDev)"
    """
    Apply precise weights to prompt elements with ComfyUI formatting.
    Supports multiple weighting schemes and automatic weight optimization.
    """
    
    # Weight formatting strategies
    _WEIGHT_FORMATS = {
        "parentheses": lambda text, weight: f"({text}:{weight:.2f})" if weight != 1.0 else text,
        "brackets": lambda text, weight: f"[{text}:{weight:.2f}]" if weight != 1.0 else text,
        "braces": lambda text, weight: f"{{{text}:{weight:.2f}}}" if weight != 1.0 else text,
        "attention": lambda text, weight: f"({text})" * max(1, int(weight)) if weight >= 1.0 else f"[{text}]" * max(1, int(1.0/weight)) if weight < 1.0 else text,
    }
    
    # Weight adjustment methods
    _ADJUSTMENT_METHODS = {
        "linear": lambda base, factor: base * factor,
        "exponential": lambda base, factor: base ** factor,
        "logarithmic": lambda base, factor: base * (1 + 0.1 * factor),
        "sigmoid": lambda base, factor: base / (1 + abs(factor - 1)),
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt to apply weights to"}),
                "weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1, "tooltip": "Primary weight value"}),
                "format_style": (list(cls._WEIGHT_FORMATS.keys()), {"default": "parentheses", "tooltip": "Weight formatting style"}),
                "adjustment_method": (list(cls._ADJUSTMENT_METHODS.keys()), {"default": "linear", "tooltip": "Weight calculation method"})
            },
            "optional": {
                "element_weights": ("STRING", {"default": "", "tooltip": "Per-element weights (comma-separated)"}),
                "weight_multiplier": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1, "tooltip": "Global weight multiplier"}),
                "auto_normalize": ("BOOLEAN", {"default": False, "tooltip": "Auto-normalize weights"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("weighted_prompt", "weight_info", "effective_weight")
    FUNCTION = "apply_weights"
    CATEGORY = NodeCategories.PROMPT_WEIGHTING
    DESCRIPTION = "Apply precise weights to prompt elements with multiple formatting options"
    
    @performance_monitor("prompt_weighting")
    @cached_operation(ttl=600)
    def apply_weights(self, prompt: str, weight: float, format_style: str, adjustment_method: str,
                     element_weights: str = "", weight_multiplier: float = 1.0, 
                     auto_normalize: bool = False, validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", 0.0)
        
        if not prompt.strip():
            return ("", "Empty prompt provided", 0.0)
        
        # Parse element-specific weights
        element_weight_list = []
        if element_weights.strip():
            try:
                element_weight_list = [float(w.strip()) for w in element_weights.split(',') if w.strip()]
            except ValueError:
                return (f"Error: Invalid element weights format", "parsing_failed", 0.0)
        
        # Split prompt into elements (comma-separated)
        elements = [elem.strip() for elem in prompt.split(',') if elem.strip()]
        
        # Apply weights
        weighted_elements = []
        total_weight = 0.0
        
        formatter = self._WEIGHT_FORMATS[format_style]
        adjuster = self._ADJUSTMENT_METHODS[adjustment_method]
        
        for i, element in enumerate(elements):
            # Determine weight for this element
            if i < len(element_weight_list):
                element_weight = element_weight_list[i]
            else:
                element_weight = weight
            
            # Apply adjustment method and multiplier
            adjusted_weight = adjuster(element_weight, weight_multiplier)
            total_weight += adjusted_weight
            
            # Format with weight
            weighted_element = formatter(element, adjusted_weight)
            weighted_elements.append(weighted_element)
        
        # Auto-normalize if requested
        if auto_normalize and len(elements) > 1:
            target_avg = 1.0
            current_avg = total_weight / len(elements)
            normalize_factor = target_avg / current_avg if current_avg > 0 else 1.0
            
            # Reprocess with normalization
            weighted_elements = []
            for i, element in enumerate(elements):
                if i < len(element_weight_list):
                    element_weight = element_weight_list[i] * normalize_factor
                else:
                    element_weight = weight * normalize_factor
                
                adjusted_weight = adjuster(element_weight, weight_multiplier)
                weighted_element = formatter(element, adjusted_weight)
                weighted_elements.append(weighted_element)
        
        weighted_prompt = ", ".join(weighted_elements)
        effective_weight = total_weight / len(elements) if elements else 0.0
        
        info = f"Applied {format_style} weighting to {len(elements)} elements (avg: {effective_weight:.2f})"
        if auto_normalize:
            info += " [normalized]"
        
        return (weighted_prompt, info, effective_weight)