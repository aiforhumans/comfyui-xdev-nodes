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
                weight_info = ", ".join(f"P{i+1}:{w}" for i, w in enumerate(weights))
                info += f" (weights: {weight_info})"
            
            return (combined, info, len(prompts))
            
        except Exception as e:
            return (prompt_1, f"Combination failed: {str(e)}", 1)


class PromptWeighter(ValidationMixin):
    DISPLAY_NAME = "Prompt Weighter (XDev)"
    """
    Add, modify, or remove attention weights from prompts.
    Supports ComfyUI weight syntax: (text:weight) and [text:weight]
    """
    
    # Weight operations
    _WEIGHT_OPERATIONS = {
        "add_emphasis": lambda text, weight: f"({text}:{weight})",
        "add_deemphasis": lambda text, weight: f"[{text}:{weight}]",
        "multiply_existing": "multiply",
        "remove_weights": "remove",
        "normalize_weights": "normalize"
    }
    
    # Precompiled regex patterns for performance
    _WEIGHT_PATTERN = re.compile(r'[\(\[]([^:\(\)\[\]]+):([0-9]*\.?[0-9]+)[\)\]]')
    _PARENTHESES_PATTERN = re.compile(r'\(([^:\(\)]+)\)')
    _BRACKETS_PATTERN = re.compile(r'\[([^:\[\]]+)\]')
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Input prompt to process"}),
                "operation": (list(cls._WEIGHT_OPERATIONS.keys()), {"default": "add_emphasis", "tooltip": "Weight operation to perform"}),
                "weight_value": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 3.0, "step": 0.1, "tooltip": "Weight value to apply"}),
                "target_text": ("STRING", {"default": "", "tooltip": "Specific text to weight (empty = whole prompt)"})
            },
            "optional": {
                "multiplier": ("FLOAT", {"default": 1.1, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Multiplier for existing weights"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("weighted_prompt", "operation_info", "weights_modified")
    FUNCTION = "process_weights"
    CATEGORY = NodeCategories.PROMPT_WEIGHTING
    DESCRIPTION = "Add, modify, or remove attention weights from prompts"
    
    @performance_monitor("prompt_weighting")
    def process_weights(self, prompt: str, operation: str, weight_value: float, 
                       target_text: str = "", multiplier: float = 1.1, validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return (prompt, f"Error: {validation['error']}", 0)
        
        if not prompt.strip():
            return ("", "Empty prompt provided", 0)
        
        original_prompt = prompt
        weights_count = 0
        
        try:
            if operation == "add_emphasis":
                if target_text.strip():
                    # Weight specific text
                    if target_text in prompt:
                        result = prompt.replace(target_text, f"({target_text}:{weight_value})")
                        weights_count = 1
                    else:
                        result = prompt
                else:
                    # Weight entire prompt
                    result = f"({prompt}:{weight_value})"
                    weights_count = 1
            
            elif operation == "add_deemphasis":
                if target_text.strip():
                    if target_text in prompt:
                        result = prompt.replace(target_text, f"[{target_text}:{weight_value}]")
                        weights_count = 1
                    else:
                        result = prompt
                else:
                    result = f"[{prompt}:{weight_value}]"
                    weights_count = 1
            
            elif operation == "multiply_existing":
                def multiply_weight(match):
                    nonlocal weights_count
                    text, weight = match.groups()
                    new_weight = round(float(weight) * multiplier, 2)
                    weights_count += 1
                    bracket_type = '(' if match.group(0).startswith('(') else '['
                    close_bracket = ')' if bracket_type == '(' else ']'
                    return f"{bracket_type}{text}:{new_weight}{close_bracket}"
                
                result = self._WEIGHT_PATTERN.sub(multiply_weight, prompt)
            
            elif operation == "remove_weights":
                def extract_text(match):
                    nonlocal weights_count
                    weights_count += 1
                    return match.group(1)
                
                result = self._WEIGHT_PATTERN.sub(extract_text, prompt)
                # Also remove simple parentheses/brackets without weights
                result = self._PARENTHESES_PATTERN.sub(r'\1', result)
                result = self._BRACKETS_PATTERN.sub(r'\1', result)
            
            elif operation == "normalize_weights":
                weights = self._WEIGHT_PATTERN.findall(prompt)
                if weights:
                    # Calculate average weight
                    avg_weight = sum(float(w[1]) for w in weights) / len(weights)
                    
                    def normalize_weight(match):
                        nonlocal weights_count
                        text, weight = match.groups()
                        # Normalize to average or specified weight
                        new_weight = round(weight_value, 2)
                        weights_count += 1
                        bracket_type = '(' if match.group(0).startswith('(') else '['
                        close_bracket = ')' if bracket_type == '(' else ']'
                        return f"{bracket_type}{text}:{new_weight}{close_bracket}"
                    
                    result = self._WEIGHT_PATTERN.sub(normalize_weight, prompt)
                else:
                    result = prompt
            
            else:
                result = prompt
            
            # Generate operation info
            info = f"Applied '{operation}' operation"
            if operation in ["add_emphasis", "add_deemphasis"] and target_text:
                info += f" to '{target_text[:20]}{'...' if len(target_text) > 20 else ''}'"
            elif operation == "multiply_existing":
                info += f" with multiplier {multiplier}"
            elif operation == "normalize_weights":
                info += f" to weight {weight_value}"
            
            info += f" - Modified {weights_count} weights"
            
            return (result, info, weights_count)
            
        except Exception as e:
            return (original_prompt, f"Weight processing failed: {str(e)}", 0)
