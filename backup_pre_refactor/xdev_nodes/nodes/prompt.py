"""
Prompt manipulation and processing nodes for XDev toolkit.
Provides professional prompt engineering tools for ComfyUI workflows.
"""

import re
import random
from typing import Dict, List, Tuple, Any, Optional, Union
from collections import Counter
from ..performance import performance_monitor, cached_operation
from ..mixins import ValidationMixin

class PromptCombiner(ValidationMixin):
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
    CATEGORY = "XDev/Prompt/Combination"
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
    CATEGORY = "XDev/Prompt/Weighting"
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


class PromptCleaner(ValidationMixin):
    """
    Clean and format prompts by removing duplicates, fixing spacing, and standardizing format.
    Provides comprehensive text cleanup for better prompt quality.
    """
    
    # Cleanup operations with precompiled patterns
    _CLEANUP_PATTERNS = {
        "extra_spaces": re.compile(r'\s+'),
        "duplicate_commas": re.compile(r',\s*,+'),
        "trailing_commas": re.compile(r',\s*$'),
        "leading_commas": re.compile(r'^\s*,'),
        "empty_parentheses": re.compile(r'\(\s*\)|\[\s*\]'),
        "malformed_weights": re.compile(r'[\(\[][^:\(\)\[\]]*[\)\]](?!:)'),
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt to clean and format"}),
                "remove_duplicates": ("BOOLEAN", {"default": True, "tooltip": "Remove duplicate words/phrases"}),
                "fix_spacing": ("BOOLEAN", {"default": True, "tooltip": "Fix extra spaces and formatting"}),
                "fix_punctuation": ("BOOLEAN", {"default": True, "tooltip": "Fix comma placement and punctuation"}),
                "remove_empty_weights": ("BOOLEAN", {"default": True, "tooltip": "Remove empty weight brackets"})
            },
            "optional": {
                "case_normalize": (["none", "lower", "title", "sentence"], {"default": "none", "tooltip": "Text case normalization"}),
                "sort_alphabetically": ("BOOLEAN", {"default": False, "tooltip": "Sort prompt elements alphabetically"}),
                "max_length": ("INT", {"default": 1000, "min": 10, "max": 10000, "tooltip": "Maximum prompt length"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("cleaned_prompt", "cleanup_info", "changes_made")
    FUNCTION = "clean_prompt"
    CATEGORY = "XDev/Prompt/Cleaning"
    DESCRIPTION = "Clean and format prompts with comprehensive text processing"
    
    @performance_monitor("prompt_cleaning")
    @cached_operation(ttl=300)
    def clean_prompt(self, prompt: str, remove_duplicates: bool = True, fix_spacing: bool = True,
                    fix_punctuation: bool = True, remove_empty_weights: bool = True,
                    case_normalize: str = "none", sort_alphabetically: bool = False,
                    max_length: int = 1000, validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt", max_length=max_length)
            if not validation["valid"]:
                return (prompt, f"Error: {validation['error']}", 0)
        
        if not prompt.strip():
            return ("", "Empty prompt provided", 0)
        
        original_prompt = prompt
        result = prompt
        changes = 0
        operations = []
        
        try:
            # Fix spacing
            if fix_spacing:
                old_result = result
                result = self._CLEANUP_PATTERNS["extra_spaces"].sub(" ", result)
                result = result.strip()
                if result != old_result:
                    changes += 1
                    operations.append("fixed spacing")
            
            # Fix punctuation
            if fix_punctuation:
                old_result = result
                # Fix duplicate commas
                result = self._CLEANUP_PATTERNS["duplicate_commas"].sub(",", result)
                # Remove trailing/leading commas
                result = self._CLEANUP_PATTERNS["trailing_commas"].sub("", result)
                result = self._CLEANUP_PATTERNS["leading_commas"].sub("", result)
                if result != old_result:
                    changes += 1
                    operations.append("fixed punctuation")
            
            # Remove empty weight brackets
            if remove_empty_weights:
                old_result = result
                result = self._CLEANUP_PATTERNS["empty_parentheses"].sub("", result)
                result = self._CLEANUP_PATTERNS["malformed_weights"].sub("", result)
                if result != old_result:
                    changes += 1
                    operations.append("removed empty weights")
            
            # Remove duplicates
            if remove_duplicates:
                old_result = result
                # Split by commas and remove duplicates while preserving order
                parts = [part.strip() for part in result.split(",")]
                seen = set()
                unique_parts = []
                for part in parts:
                    if part and part.lower() not in seen:
                        seen.add(part.lower())
                        unique_parts.append(part)
                
                result = ", ".join(unique_parts)
                if result != old_result:
                    changes += 1
                    operations.append("removed duplicates")
            
            # Sort alphabetically
            if sort_alphabetically:
                old_result = result
                # Split, sort, and rejoin (preserve weights)
                parts = [part.strip() for part in result.split(",") if part.strip()]
                # Sort by the actual text, ignoring weight syntax
                def sort_key(part):
                    # Extract text from weight syntax
                    clean_part = re.sub(r'[\(\[][^:\(\)\[\]]*:([0-9]*\.?[0-9]+)[\)\]]', r'\1', part)
                    return clean_part.lower()
                
                parts.sort(key=sort_key)
                result = ", ".join(parts)
                if result != old_result:
                    changes += 1
                    operations.append("sorted alphabetically")
            
            # Case normalization
            if case_normalize != "none":
                old_result = result
                if case_normalize == "lower":
                    result = result.lower()
                elif case_normalize == "title":
                    result = result.title()
                elif case_normalize == "sentence":
                    result = result.capitalize()
                
                if result != old_result:
                    changes += 1
                    operations.append(f"normalized to {case_normalize} case")
            
            # Truncate if too long
            if len(result) > max_length:
                result = result[:max_length].rsplit(",", 1)[0]  # Cut at last complete phrase
                changes += 1
                operations.append(f"truncated to {max_length} chars")
            
            # Generate info
            if operations:
                info = f"Cleaned prompt: {', '.join(operations)}"
            else:
                info = "No changes needed"
            
            return (result, info, changes)
            
        except Exception as e:
            return (original_prompt, f"Cleaning failed: {str(e)}", 0)


class PromptAnalyzer(ValidationMixin):
    """
    Analyze prompt structure, complexity, and composition.
    Provides detailed statistics and insights about prompt content.
    """
    
    # Analysis categories
    _ANALYSIS_LEVELS = ["basic", "detailed", "comprehensive"]
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt to analyze"}),
                "analysis_level": (cls._ANALYSIS_LEVELS, {"default": "detailed", "tooltip": "Depth of analysis"})
            },
            "optional": {
                "include_weights": ("BOOLEAN", {"default": True, "tooltip": "Analyze attention weights"}),
                "word_frequency": ("BOOLEAN", {"default": True, "tooltip": "Include word frequency analysis"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "FLOAT")
    RETURN_NAMES = ("analysis_report", "statistics", "word_count", "complexity_score")
    FUNCTION = "analyze_prompt"
    CATEGORY = "XDev/Prompt/Analysis"
    DESCRIPTION = "Analyze prompt structure, complexity, and composition"
    
    @performance_monitor("prompt_analysis")
    @cached_operation(ttl=200)
    def analyze_prompt(self, prompt: str, analysis_level: str = "detailed",
                      include_weights: bool = True, word_frequency: bool = True,
                      validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", 0, 0.0)
        
        if not prompt.strip():
            return ("Empty prompt", "No content to analyze", 0, 0.0)
        
        try:
            # Basic statistics
            char_count = len(prompt)
            word_count = len(prompt.split())
            phrase_count = len([p for p in prompt.split(",") if p.strip()])
            
            # Weight analysis
            weight_matches = re.findall(r'[\(\[]([^:\(\)\[\]]+):([0-9]*\.?[0-9]+)[\)\]]', prompt)
            weighted_elements = len(weight_matches)
            
            # Calculate complexity score (0-10)
            complexity_score = min(10.0, (
                (word_count * 0.1) +
                (phrase_count * 0.3) +
                (weighted_elements * 0.5) +
                (char_count * 0.001)
            ))
            
            # Generate analysis report
            report_lines = [
                "📊 PROMPT ANALYSIS REPORT",
                "=" * 40,
                f"📝 Character Count: {char_count}",
                f"🔤 Word Count: {word_count}",
                f"📋 Phrase Count: {phrase_count}",
                f"⚖️ Complexity Score: {complexity_score:.2f}/10"
            ]
            
            if analysis_level in ["detailed", "comprehensive"]:
                # Detailed analysis
                report_lines.extend([
                    "",
                    "🎯 DETAILED ANALYSIS:",
                    f"• Average words per phrase: {word_count / max(phrase_count, 1):.1f}",
                    f"• Average chars per word: {char_count / max(word_count, 1):.1f}",
                ])
                
                if include_weights and weight_matches:
                    weights = [float(w[1]) for w in weight_matches]
                    avg_weight = sum(weights) / len(weights)
                    report_lines.extend([
                        "",
                        "⚖️ WEIGHT ANALYSIS:",
                        f"• Weighted elements: {weighted_elements}",
                        f"• Average weight: {avg_weight:.2f}",
                        f"• Weight range: {min(weights):.2f} - {max(weights):.2f}",
                        f"• Weight distribution: {len([w for w in weights if w > 1.0])} emphasis, {len([w for w in weights if w < 1.0])} de-emphasis"
                    ])
            
            if analysis_level == "comprehensive":
                # Comprehensive analysis
                words = prompt.lower().split()
                
                if word_frequency and words:
                    word_freq = Counter(words)
                    most_common = word_freq.most_common(5)
                    report_lines.extend([
                        "",
                        "📈 WORD FREQUENCY (Top 5):",
                        *[f"• '{word}': {count} times" for word, count in most_common]
                    ])
                
                # Content categorization (basic)
                style_indicators = {
                    "artistic": ["art", "artistic", "style", "painting", "drawing"],
                    "photographic": ["photo", "photograph", "realistic", "camera", "lens"],
                    "character": ["character", "person", "face", "portrait", "human"],
                    "environment": ["landscape", "background", "scene", "environment", "setting"]
                }
                
                detected_categories = []
                prompt_lower = prompt.lower()
                for category, keywords in style_indicators.items():
                    if any(keyword in prompt_lower for keyword in keywords):
                        detected_categories.append(category)
                
                if detected_categories:
                    report_lines.extend([
                        "",
                        "🏷️ DETECTED CATEGORIES:",
                        f"• {', '.join(detected_categories)}"
                    ])
            
            # Generate statistics string
            stats = f"Words: {word_count}, Phrases: {phrase_count}, Weights: {weighted_elements}, Complexity: {complexity_score:.2f}"
            
            return ("\n".join(report_lines), stats, word_count, complexity_score)
            
        except Exception as e:
            return (f"Analysis failed: {str(e)}", "error", 0, 0.0)


class PromptRandomizer(ValidationMixin):
    """
    Randomize and vary prompts by shuffling elements, adding variations, or generating alternatives.
    Useful for creating prompt variations and exploring creative possibilities.
    """
    
    # Randomization modes
    _RANDOMIZATION_MODES = {
        "shuffle_phrases": "Shuffle comma-separated phrases",
        "random_weights": "Apply random weights to elements", 
        "add_variations": "Add random descriptive variations",
        "remove_random": "Randomly remove some elements",
        "boost_random": "Randomly boost specific elements"
    }
    
    # Common descriptive variations by category
    _STYLE_VARIATIONS = {
        "artistic": ["painterly", "stylized", "artistic", "expressive", "creative"],
        "quality": ["high quality", "detailed", "sharp", "crisp", "professional"],
        "lighting": ["dramatic lighting", "soft lighting", "natural lighting", "studio lighting"],
        "mood": ["atmospheric", "moody", "vibrant", "serene", "dynamic"]
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Base prompt to randomize"}),
                "mode": (list(cls._RANDOMIZATION_MODES.keys()), {"default": "shuffle_phrases", "tooltip": "Randomization method"}),
                "intensity": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.1, "tooltip": "Randomization intensity"})
            },
            "optional": {
                "seed": ("INT", {"default": -1, "min": -1, "max": 999999, "tooltip": "Random seed (-1 for random)"}),
                "preserve_weights": ("BOOLEAN", {"default": True, "tooltip": "Keep existing attention weights"}),
                "variation_category": (["artistic", "quality", "lighting", "mood", "mixed"], {"default": "mixed", "tooltip": "Type of variations to add"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("randomized_prompt", "randomization_info", "seed_used")
    FUNCTION = "randomize_prompt"
    CATEGORY = "XDev/Prompt/Randomization"
    DESCRIPTION = "Randomize and vary prompts with multiple randomization strategies"
    
    @performance_monitor("prompt_randomization")
    def randomize_prompt(self, prompt: str, mode: str, intensity: float = 0.5,
                        seed: int = -1, preserve_weights: bool = True,
                        variation_category: str = "mixed", validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return (prompt, f"Error: {validation['error']}", 0)
        
        if not prompt.strip():
            return ("", "Empty prompt provided", 0)
        
        # Set random seed
        if seed == -1:
            seed = random.randint(0, 999999)
        random.seed(seed)
        
        original_prompt = prompt
        
        try:
            if mode == "shuffle_phrases":
                # Split by commas and shuffle
                phrases = [p.strip() for p in prompt.split(",") if p.strip()]
                if len(phrases) > 1:
                    # Shuffle based on intensity
                    num_to_shuffle = max(1, int(len(phrases) * intensity))
                    indices_to_shuffle = random.sample(range(len(phrases)), min(num_to_shuffle, len(phrases)))
                    shuffled_elements = [phrases[i] for i in indices_to_shuffle]
                    random.shuffle(shuffled_elements)
                    
                    for i, idx in enumerate(indices_to_shuffle):
                        phrases[idx] = shuffled_elements[i]
                    
                    result = ", ".join(phrases)
                else:
                    result = prompt
                
                info = f"Shuffled {min(len(phrases), int(len(phrases) * intensity))} phrases"
            
            elif mode == "random_weights":
                # Add random weights to unweighted elements
                phrases = [p.strip() for p in prompt.split(",") if p.strip()]
                weighted_phrases = []
                weights_added = 0
                
                for phrase in phrases:
                    # Check if already has weight
                    if re.search(r'[\(\[].*:.*[\)\]]', phrase):
                        weighted_phrases.append(phrase)
                    else:
                        # Add weight based on intensity and randomness
                        if random.random() < intensity:
                            weight = round(random.uniform(0.8, 1.4), 2)
                            if weight > 1.0:
                                weighted_phrases.append(f"({phrase}:{weight})")
                            else:
                                weighted_phrases.append(f"[{phrase}:{weight}]")
                            weights_added += 1
                        else:
                            weighted_phrases.append(phrase)
                
                result = ", ".join(weighted_phrases)
                info = f"Added {weights_added} random weights"
            
            elif mode == "add_variations":
                # Add random descriptive variations
                variations_to_add = []
                
                if variation_category == "mixed":
                    all_variations = []
                    for cat_variations in self._STYLE_VARIATIONS.values():
                        all_variations.extend(cat_variations)
                    source_variations = all_variations
                else:
                    source_variations = self._STYLE_VARIATIONS.get(variation_category, [])
                
                num_variations = max(1, int(len(source_variations) * intensity))
                selected_variations = random.sample(source_variations, min(num_variations, len(source_variations)))
                
                if preserve_weights:
                    result = f"{prompt}, {', '.join(selected_variations)}"
                else:
                    # Add with random weights
                    weighted_variations = []
                    for var in selected_variations:
                        if random.random() > 0.5:
                            weight = round(random.uniform(0.9, 1.3), 2)
                            weighted_variations.append(f"({var}:{weight})")
                        else:
                            weighted_variations.append(var)
                    result = f"{prompt}, {', '.join(weighted_variations)}"
                
                info = f"Added {len(selected_variations)} {variation_category} variations"
            
            elif mode == "remove_random":
                # Randomly remove elements based on intensity
                phrases = [p.strip() for p in prompt.split(",") if p.strip()]
                if len(phrases) > 1:
                    num_to_remove = max(0, int(len(phrases) * intensity))
                    if num_to_remove > 0:
                        phrases_to_keep = random.sample(phrases, len(phrases) - num_to_remove)
                        result = ", ".join(phrases_to_keep)
                        info = f"Removed {num_to_remove} random elements"
                    else:
                        result = prompt
                        info = "No elements removed (intensity too low)"
                else:
                    result = prompt
                    info = "Cannot remove from single element"
            
            elif mode == "boost_random":
                # Randomly boost specific elements with higher weights
                phrases = [p.strip() for p in prompt.split(",") if p.strip()]
                boosted_phrases = []
                boosts_applied = 0
                
                for phrase in phrases:
                    if random.random() < intensity:
                        # Apply boost
                        boost_weight = round(random.uniform(1.2, 1.8), 2)
                        # Remove existing weights first if preserve_weights is False
                        if not preserve_weights:
                            clean_phrase = re.sub(r'[\(\[]([^:\(\)\[\]]+):([0-9]*\.?[0-9]+)[\)\]]', r'\1', phrase)
                        else:
                            clean_phrase = phrase
                        
                        boosted_phrases.append(f"({clean_phrase}:{boost_weight})")
                        boosts_applied += 1
                    else:
                        boosted_phrases.append(phrase)
                
                result = ", ".join(boosted_phrases)
                info = f"Applied random boosts to {boosts_applied} elements"
            
            else:
                result = prompt
                info = f"Unknown mode: {mode}"
            
            return (result, info, seed)
            
        except Exception as e:
            return (original_prompt, f"Randomization failed: {str(e)}", seed)


class PersonBuilder(ValidationMixin):
    """
    Structured person/character prompt builder with comprehensive template system.
    Generates professional portrait and character prompts with detailed customization.
    """
    
    # Person templates with structured categories
    _PERSON_TEMPLATES = {
        # Age categories
        "age": {
            "child": ["young child", "kid", "little boy", "little girl"],
            "teenager": ["teenager", "teen", "young person", "adolescent"],
            "young_adult": ["young adult", "young person", "20s"],
            "adult": ["adult", "person", "30s", "middle-aged"],
            "elderly": ["elderly person", "senior", "old man", "old woman"]
        },
        # Gender options
        "gender": {
            "male": ["man", "male", "gentleman", "guy"],
            "female": ["woman", "female", "lady", "girl"],
            "person": ["person", "individual", "human", "character"]
        },
        # Physical features
        "hair_color": {
            "blonde": ["blonde hair", "golden hair", "light hair"],
            "brown": ["brown hair", "brunette", "chestnut hair"],
            "black": ["black hair", "dark hair", "raven hair"],
            "red": ["red hair", "ginger hair", "auburn hair"],
            "gray": ["gray hair", "grey hair", "silver hair"],
            "white": ["white hair", "platinum hair"]
        },
        "hair_style": {
            "short": ["short hair", "cropped hair", "pixie cut"],
            "medium": ["medium length hair", "shoulder-length hair"],
            "long": ["long hair", "flowing hair", "waist-length hair"],
            "curly": ["curly hair", "wavy hair", "ringlets"],
            "straight": ["straight hair", "sleek hair"],
            "braided": ["braided hair", "braids", "plaits"]
        },
        "eye_color": {
            "blue": ["blue eyes", "sapphire eyes", "azure eyes"],
            "brown": ["brown eyes", "hazel eyes", "amber eyes"],
            "green": ["green eyes", "emerald eyes", "jade eyes"],
            "gray": ["gray eyes", "grey eyes", "silver eyes"],
            "other": ["striking eyes", "captivating eyes", "expressive eyes"]
        },
        # Expressions and poses
        "expression": {
            "happy": ["smiling", "joyful expression", "cheerful", "beaming"],
            "serious": ["serious expression", "stern look", "focused", "contemplative"],
            "neutral": ["neutral expression", "calm", "serene", "peaceful"],
            "surprised": ["surprised expression", "amazed", "wide-eyed"],
            "confident": ["confident expression", "determined", "self-assured"]
        },
        "pose": {
            "portrait": ["portrait", "headshot", "close-up", "head and shoulders"],
            "full_body": ["full body", "standing pose", "whole figure"],
            "three_quarter": ["three-quarter view", "3/4 pose", "angled view"],
            "profile": ["profile view", "side view", "silhouette"],
            "action": ["dynamic pose", "in motion", "action shot"]
        },
        # Clothing styles
        "clothing": {
            "casual": ["casual clothes", "everyday wear", "relaxed attire"],
            "formal": ["formal attire", "business suit", "elegant dress"],
            "professional": ["professional clothing", "office wear", "business attire"],
            "vintage": ["vintage clothing", "retro fashion", "period costume"],
            "fantasy": ["fantasy outfit", "medieval clothing", "mystical attire"],
            "modern": ["modern fashion", "contemporary style", "trendy outfit"]
        },
        # Character archetypes
        "archetype": {
            "hero": ["heroic character", "protagonist", "brave warrior"],
            "scholar": ["scholar", "intellectual", "wise person", "academic"],
            "artist": ["artist", "creative person", "painter", "musician"],
            "leader": ["leader", "commander", "authority figure"],
            "rebel": ["rebel", "nonconformist", "revolutionary"],
            "mystic": ["mystic", "sage", "spiritual person", "oracle"]
        }
    }
    
    # Quality and style modifiers
    _QUALITY_MODIFIERS = [
        "highly detailed", "photorealistic", "professional photography", 
        "sharp focus", "high resolution", "masterpiece", "best quality",
        "ultra-detailed", "cinematic lighting", "perfect composition"
    ]
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "age": (["auto"] + list(cls._PERSON_TEMPLATES["age"].keys()), {"default": "adult", "tooltip": "Age category of the person"}),
                "gender": (["auto"] + list(cls._PERSON_TEMPLATES["gender"].keys()), {"default": "person", "tooltip": "Gender of the person"}),
                "expression": (["auto"] + list(cls._PERSON_TEMPLATES["expression"].keys()), {"default": "neutral", "tooltip": "Facial expression"})
            },
            "optional": {
                "hair_color": (["auto"] + list(cls._PERSON_TEMPLATES["hair_color"].keys()), {"default": "auto", "tooltip": "Hair color"}),
                "hair_style": (["auto"] + list(cls._PERSON_TEMPLATES["hair_style"].keys()), {"default": "auto", "tooltip": "Hair style"}),
                "eye_color": (["auto"] + list(cls._PERSON_TEMPLATES["eye_color"].keys()), {"default": "auto", "tooltip": "Eye color"}),
                "pose": (["auto"] + list(cls._PERSON_TEMPLATES["pose"].keys()), {"default": "portrait", "tooltip": "Pose/framing"}),
                "clothing": (["auto"] + list(cls._PERSON_TEMPLATES["clothing"].keys()), {"default": "auto", "tooltip": "Clothing style"}),
                "archetype": (["none"] + list(cls._PERSON_TEMPLATES["archetype"].keys()), {"default": "none", "tooltip": "Character archetype"}),
                "custom_traits": ("STRING", {"default": "", "multiline": True, "tooltip": "Additional custom traits/descriptions"}),
                "add_quality": ("BOOLEAN", {"default": True, "tooltip": "Add quality modifiers"}),
                "randomize_traits": ("BOOLEAN", {"default": False, "tooltip": "Randomize unspecified traits"}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 999999, "tooltip": "Random seed for trait selection"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("person_prompt", "template_info", "trait_summary")
    FUNCTION = "build_person"
    CATEGORY = "XDev/Prompt/Templates"
    DESCRIPTION = "Build structured person/character prompts with comprehensive templates"
    
    @performance_monitor("person_building")
    @cached_operation(ttl=300)
    def build_person(self, age: str, gender: str, expression: str,
                    hair_color: str = "auto", hair_style: str = "auto", eye_color: str = "auto",
                    pose: str = "portrait", clothing: str = "auto", archetype: str = "none",
                    custom_traits: str = "", add_quality: bool = True, randomize_traits: bool = False,
                    seed: int = -1, validate_input: bool = True):
        
        if validate_input and custom_traits:
            validation = self.validate_string_input(custom_traits, "custom_traits", allow_empty=True)
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", "")
        
        # Set random seed for consistent randomization
        if seed == -1:
            seed = random.randint(0, 999999)
        random.seed(seed)
        
        # Build prompt components
        prompt_parts = []
        used_traits = []
        
        try:
            # Core person characteristics
            for category, selected in [("age", age), ("gender", gender), ("expression", expression), ("pose", pose)]:
                if selected != "auto" and selected in self._PERSON_TEMPLATES[category]:
                    trait = random.choice(self._PERSON_TEMPLATES[category][selected])
                    prompt_parts.append(trait)
                    used_traits.append(f"{category}: {selected}")
                elif selected == "auto" and randomize_traits:
                    selected_key = random.choice(list(self._PERSON_TEMPLATES[category].keys()))
                    trait = random.choice(self._PERSON_TEMPLATES[category][selected_key])
                    prompt_parts.append(trait)
                    used_traits.append(f"{category}: {selected_key} (auto)")
            
            # Optional physical features
            for category, selected in [("hair_color", hair_color), ("hair_style", hair_style), ("eye_color", eye_color), ("clothing", clothing)]:
                if selected != "auto" and selected in self._PERSON_TEMPLATES[category]:
                    trait = random.choice(self._PERSON_TEMPLATES[category][selected])
                    prompt_parts.append(trait)
                    used_traits.append(f"{category}: {selected}")
                elif selected == "auto" and randomize_traits:
                    selected_key = random.choice(list(self._PERSON_TEMPLATES[category].keys()))
                    trait = random.choice(self._PERSON_TEMPLATES[category][selected_key])
                    prompt_parts.append(trait)
                    used_traits.append(f"{category}: {selected_key} (auto)")
            
            # Character archetype
            if archetype != "none" and archetype in self._PERSON_TEMPLATES["archetype"]:
                trait = random.choice(self._PERSON_TEMPLATES["archetype"][archetype])
                prompt_parts.append(trait)
                used_traits.append(f"archetype: {archetype}")
            
            # Custom traits
            if custom_traits.strip():
                # Split custom traits and clean them
                custom_list = [trait.strip() for trait in custom_traits.split(",") if trait.strip()]
                prompt_parts.extend(custom_list)
                used_traits.append(f"custom: {len(custom_list)} traits")
            
            # Quality modifiers
            if add_quality:
                quality_count = random.randint(2, 4)
                selected_quality = random.sample(self._QUALITY_MODIFIERS, min(quality_count, len(self._QUALITY_MODIFIERS)))
                prompt_parts.extend(selected_quality)
                used_traits.append(f"quality: {len(selected_quality)} modifiers")
            
            # Build final prompt
            result_prompt = ", ".join(prompt_parts)
            
            # Generate info
            template_info = f"Generated person prompt using {len(used_traits)} trait categories"
            if randomize_traits:
                template_info += f" with randomization (seed: {seed})"
            
            # Generate trait summary
            trait_summary = "; ".join(used_traits)
            
            return (result_prompt, template_info, trait_summary)
            
        except Exception as e:
            return (f"Error building person: {str(e)}", "build_failed", "")


class StyleBuilder(ValidationMixin):
    """
    Structured artistic style prompt builder with comprehensive style templates.
    Generates professional artistic style prompts with detailed aesthetic control.
    """
    
    # Style templates with structured categories
    _STYLE_TEMPLATES = {
        # Art movements and periods
        "art_movement": {
            "renaissance": ["Renaissance style", "classical art", "Renaissance painting", "Old Master style"],
            "baroque": ["Baroque style", "dramatic baroque", "ornate baroque art"],
            "impressionist": ["impressionist style", "impressionism", "plein air painting"],
            "expressionist": ["expressionist style", "German expressionism", "emotional expressionism"],
            "cubist": ["cubist style", "geometric cubism", "abstract cubism"],
            "surrealist": ["surrealist style", "dreamlike surrealism", "Salvador Dali style"],
            "pop_art": ["pop art style", "Andy Warhol style", "commercial pop art"],
            "abstract": ["abstract art", "non-representational", "pure abstraction"],
            "modern": ["modern art style", "contemporary art", "avant-garde"],
            "art_nouveau": ["Art Nouveau style", "organic Art Nouveau", "decorative art"]
        },
        # Digital art styles
        "digital_style": {
            "concept_art": ["concept art", "game concept art", "film concept art"],
            "matte_painting": ["matte painting", "digital matte painting", "cinematic matte painting"],
            "digital_painting": ["digital painting", "digital art", "painted digital art"],
            "3d_render": ["3D render", "CGI render", "photorealistic 3D"],
            "pixel_art": ["pixel art", "8-bit art", "retro pixel style"],
            "vector_art": ["vector art", "clean vector illustration", "geometric vector"],
            "photomanipulation": ["photo manipulation", "digital composite", "surreal photomontage"],
            "neon_art": ["neon art", "cyberpunk neon", "glowing neon style"]
        },
        # Traditional media
        "medium": {
            "oil_painting": ["oil painting", "oil on canvas", "traditional oil painting"],
            "watercolor": ["watercolor painting", "watercolor art", "aquarelle"],
            "acrylic": ["acrylic painting", "acrylic on canvas", "modern acrylic"],
            "pencil": ["pencil drawing", "graphite drawing", "detailed pencil art"],
            "charcoal": ["charcoal drawing", "charcoal sketch", "dramatic charcoal"],
            "ink": ["ink drawing", "pen and ink", "India ink illustration"],
            "pastel": ["pastel drawing", "soft pastels", "chalk pastels"],
            "mixed_media": ["mixed media art", "collage art", "multimedia artwork"]
        },
        # Color palettes
        "color_palette": {
            "monochrome": ["monochrome", "black and white", "grayscale"],
            "warm": ["warm colors", "warm palette", "orange and red tones"],
            "cool": ["cool colors", "cool palette", "blue and purple tones"],
            "vibrant": ["vibrant colors", "saturated colors", "bright palette"],
            "muted": ["muted colors", "desaturated palette", "subtle tones"],
            "complementary": ["complementary colors", "contrasting colors"],
            "analogous": ["analogous colors", "harmonious palette"],
            "earth_tones": ["earth tones", "natural colors", "brown and ochre"]
        },
        # Lighting styles
        "lighting": {
            "dramatic": ["dramatic lighting", "chiaroscuro", "high contrast lighting"],
            "soft": ["soft lighting", "diffused light", "gentle illumination"],
            "golden_hour": ["golden hour lighting", "warm sunset light", "magic hour"],
            "studio": ["studio lighting", "professional lighting", "controlled lighting"],
            "natural": ["natural lighting", "daylight", "outdoor lighting"],
            "neon": ["neon lighting", "artificial neon", "colorful neon glow"],
            "candle": ["candlelight", "warm candle glow", "intimate lighting"],
            "rim": ["rim lighting", "backlit", "edge lighting"]
        },
        # Composition styles
        "composition": {
            "rule_of_thirds": ["rule of thirds composition", "balanced composition"],
            "symmetrical": ["symmetrical composition", "perfect symmetry", "mirrored composition"],
            "dynamic": ["dynamic composition", "diagonal composition", "movement"],
            "minimalist": ["minimalist composition", "simple composition", "clean layout"],
            "complex": ["complex composition", "detailed composition", "layered"],
            "centered": ["centered composition", "central focus"],
            "golden_ratio": ["golden ratio composition", "fibonacci spiral"],
            "leading_lines": ["leading lines", "directional composition"]
        },
        # Texture and finish
        "texture": {
            "smooth": ["smooth texture", "clean finish", "polished surface"],
            "rough": ["rough texture", "textured surface", "coarse finish"],
            "glossy": ["glossy finish", "reflective surface", "shiny texture"],
            "matte": ["matte finish", "non-reflective", "flat texture"],
            "metallic": ["metallic texture", "metal finish", "chrome surface"],
            "organic": ["organic texture", "natural surface", "flowing texture"],
            "geometric": ["geometric texture", "angular surface", "structured pattern"],
            "weathered": ["weathered texture", "aged surface", "worn finish"]
        }
    }
    
    # Technical quality terms
    _TECHNICAL_QUALITY = [
        "8k resolution", "ultra high definition", "sharp focus", "perfect clarity",
        "professional photography", "studio quality", "museum quality",
        "award-winning", "trending on artstation", "featured artwork"
    ]
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "primary_style": (["auto"] + list(cls._STYLE_TEMPLATES["art_movement"].keys()) + list(cls._STYLE_TEMPLATES["digital_style"].keys()), 
                                {"default": "digital_painting", "tooltip": "Primary artistic style"}),
                "medium": (["auto"] + list(cls._STYLE_TEMPLATES["medium"].keys()), {"default": "auto", "tooltip": "Art medium/technique"}),
                "color_palette": (["auto"] + list(cls._STYLE_TEMPLATES["color_palette"].keys()), {"default": "vibrant", "tooltip": "Color scheme"})
            },
            "optional": {
                "lighting": (["auto"] + list(cls._STYLE_TEMPLATES["lighting"].keys()), {"default": "dramatic", "tooltip": "Lighting style"}),
                "composition": (["auto"] + list(cls._STYLE_TEMPLATES["composition"].keys()), {"default": "auto", "tooltip": "Composition style"}),
                "texture": (["auto"] + list(cls._STYLE_TEMPLATES["texture"].keys()), {"default": "auto", "tooltip": "Surface texture/finish"}),
                "custom_style": ("STRING", {"default": "", "multiline": True, "tooltip": "Additional custom style elements"}),
                "add_technical": ("BOOLEAN", {"default": True, "tooltip": "Add technical quality terms"}),
                "style_weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Weight for primary style"}),
                "randomize_auto": ("BOOLEAN", {"default": False, "tooltip": "Randomize 'auto' selections"}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 999999, "tooltip": "Random seed for style selection"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("style_prompt", "style_info", "style_breakdown")
    FUNCTION = "build_style"
    CATEGORY = "XDev/Prompt/Templates"
    DESCRIPTION = "Build structured artistic style prompts with comprehensive style control"
    
    @performance_monitor("style_building")
    @cached_operation(ttl=300)
    def build_style(self, primary_style: str, medium: str, color_palette: str,
                   lighting: str = "auto", composition: str = "auto", texture: str = "auto",
                   custom_style: str = "", add_technical: bool = True, style_weight: float = 1.0,
                   randomize_auto: bool = False, seed: int = -1, validate_input: bool = True):
        
        if validate_input and custom_style:
            validation = self.validate_string_input(custom_style, "custom_style", allow_empty=True)
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", "")
        
        # Set random seed for consistent randomization
        if seed == -1:
            seed = random.randint(0, 999999)
        random.seed(seed)
        
        # Build style components
        style_parts = []
        used_elements = []
        
        try:
            # Primary style (weighted)
            primary_found = False
            
            # Check art movements first
            if primary_style in self._STYLE_TEMPLATES["art_movement"]:
                style_term = random.choice(self._STYLE_TEMPLATES["art_movement"][primary_style])
                if style_weight != 1.0:
                    style_term = f"({style_term}:{style_weight})"
                style_parts.append(style_term)
                used_elements.append(f"art_movement: {primary_style}")
                primary_found = True
            
            # Check digital styles
            elif primary_style in self._STYLE_TEMPLATES["digital_style"]:
                style_term = random.choice(self._STYLE_TEMPLATES["digital_style"][primary_style])
                if style_weight != 1.0:
                    style_term = f"({style_term}:{style_weight})"
                style_parts.append(style_term)
                used_elements.append(f"digital_style: {primary_style}")
                primary_found = True
            
            # Auto selection for primary style
            elif primary_style == "auto" and randomize_auto:
                # Randomly choose from all styles
                all_styles = {**self._STYLE_TEMPLATES["art_movement"], **self._STYLE_TEMPLATES["digital_style"]}
                selected_key = random.choice(list(all_styles.keys()))
                style_term = random.choice(all_styles[selected_key])
                if style_weight != 1.0:
                    style_term = f"({style_term}:{style_weight})"
                style_parts.append(style_term)
                used_elements.append(f"style: {selected_key} (auto)")
                primary_found = True
            
            # Medium
            if medium != "auto" and medium in self._STYLE_TEMPLATES["medium"]:
                medium_term = random.choice(self._STYLE_TEMPLATES["medium"][medium])
                style_parts.append(medium_term)
                used_elements.append(f"medium: {medium}")
            elif medium == "auto" and randomize_auto:
                selected_medium = random.choice(list(self._STYLE_TEMPLATES["medium"].keys()))
                medium_term = random.choice(self._STYLE_TEMPLATES["medium"][selected_medium])
                style_parts.append(medium_term)
                used_elements.append(f"medium: {selected_medium} (auto)")
            
            # Color palette
            if color_palette != "auto" and color_palette in self._STYLE_TEMPLATES["color_palette"]:
                color_term = random.choice(self._STYLE_TEMPLATES["color_palette"][color_palette])
                style_parts.append(color_term)
                used_elements.append(f"color: {color_palette}")
            elif color_palette == "auto" and randomize_auto:
                selected_color = random.choice(list(self._STYLE_TEMPLATES["color_palette"].keys()))
                color_term = random.choice(self._STYLE_TEMPLATES["color_palette"][selected_color])
                style_parts.append(color_term)
                used_elements.append(f"color: {selected_color} (auto)")
            
            # Optional style elements
            for category, selected in [("lighting", lighting), ("composition", composition), ("texture", texture)]:
                if selected != "auto" and selected in self._STYLE_TEMPLATES[category]:
                    style_term = random.choice(self._STYLE_TEMPLATES[category][selected])
                    style_parts.append(style_term)
                    used_elements.append(f"{category}: {selected}")
                elif selected == "auto" and randomize_auto:
                    selected_key = random.choice(list(self._STYLE_TEMPLATES[category].keys()))
                    style_term = random.choice(self._STYLE_TEMPLATES[category][selected_key])
                    style_parts.append(style_term)
                    used_elements.append(f"{category}: {selected_key} (auto)")
            
            # Custom style elements
            if custom_style.strip():
                custom_list = [element.strip() for element in custom_style.split(",") if element.strip()]
                style_parts.extend(custom_list)
                used_elements.append(f"custom: {len(custom_list)} elements")
            
            # Technical quality
            if add_technical:
                tech_count = random.randint(1, 3)
                selected_tech = random.sample(self._TECHNICAL_QUALITY, min(tech_count, len(self._TECHNICAL_QUALITY)))
                style_parts.extend(selected_tech)
                used_elements.append(f"technical: {len(selected_tech)} terms")
            
            # Build final prompt
            result_prompt = ", ".join(style_parts)
            
            # Generate info
            style_info = f"Generated style prompt using {len(used_elements)} style categories"
            if randomize_auto:
                style_info += f" with randomization (seed: {seed})"
            if style_weight != 1.0:
                style_info += f", primary style weight: {style_weight}"
            
            # Generate breakdown
            style_breakdown = "; ".join(used_elements)
            
            return (result_prompt, style_info, style_breakdown)
            
        except Exception as e:
            return (f"Error building style: {str(e)}", "build_failed", "")


class PromptMatrix(ValidationMixin):
    """
    Generate all combinations from prompt components using | delimiter syntax.
    Inspired by Stable Diffusion WebUI's Prompt Matrix functionality.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "matrix_prompt": ("STRING", {"default": "a cat | sitting | striped | in garden", "multiline": True, "tooltip": "Prompt with | delimited options"}),
                "combination_mode": (["all_combinations", "incremental", "pairwise"], {"default": "all_combinations", "tooltip": "How to generate combinations"})
            },
            "optional": {
                "base_prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Base prompt always included"}),
                "separator": ("STRING", {"default": ", ", "tooltip": "Separator between prompt parts"}),
                "max_combinations": ("INT", {"default": 50, "min": 1, "max": 1000, "tooltip": "Maximum combinations to generate"}),
                "shuffle_results": ("BOOLEAN", {"default": False, "tooltip": "Randomize combination order"}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 999999, "tooltip": "Random seed for shuffling"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("matrix_prompts", "combination_info", "combination_list")
    FUNCTION = "generate_matrix"
    CATEGORY = "XDev/Prompt/Advanced"
    DESCRIPTION = "Generate prompt combinations using | delimiter syntax for systematic prompt exploration"
    
    @performance_monitor("prompt_matrix")
    @cached_operation(ttl=300)
    def generate_matrix(self, matrix_prompt: str, combination_mode: str = "all_combinations",
                       base_prompt: str = "", separator: str = ", ", max_combinations: int = 50,
                       shuffle_results: bool = False, seed: int = -1, validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(matrix_prompt, "matrix_prompt")
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", "")
        
        # Set random seed for consistent shuffling
        if seed == -1:
            seed = random.randint(0, 999999)
        random.seed(seed)
        
        try:
            # Parse matrix prompt
            if "|" not in matrix_prompt:
                return (matrix_prompt.strip(), "No matrix delimiters found", "Single prompt")
            
            # Split into components
            components = [part.strip() for part in matrix_prompt.split("|")]
            if not components:
                return ("", "No valid components found", "")
            
            # Generate combinations based on mode
            combinations = []
            
            if combination_mode == "all_combinations":
                # Generate all possible combinations (2^n - 1, excluding empty)
                from itertools import combinations as iter_combinations
                for r in range(1, len(components) + 1):
                    for combo in iter_combinations(components, r):
                        combinations.append(list(combo))
                        
            elif combination_mode == "incremental":
                # Incremental: first element + progressively more elements
                base_element = components[0]
                combinations.append([base_element])
                
                for i in range(1, len(components)):
                    combo = [base_element] + components[1:i+1]
                    combinations.append(combo)
                    
            elif combination_mode == "pairwise":
                # Pairwise: first element with each other element individually
                base_element = components[0]
                combinations.append([base_element])
                
                for i in range(1, len(components)):
                    combinations.append([base_element, components[i]])
            
            # Limit combinations
            if len(combinations) > max_combinations:
                combinations = combinations[:max_combinations]
            
            # Shuffle if requested
            if shuffle_results:
                random.shuffle(combinations)
            
            # Build prompt strings
            prompt_strings = []
            for combo in combinations:
                parts = []
                if base_prompt.strip():
                    parts.append(base_prompt.strip())
                parts.extend(combo)
                prompt_strings.append(separator.join(parts))
            
            # Join all prompts
            result_prompts = "\n".join(prompt_strings)
            
            # Generate info
            combination_info = f"Generated {len(combinations)} combinations using {combination_mode} mode"
            if shuffle_results:
                combination_info += f" (shuffled with seed {seed})"
            
            # Generate list summary
            combination_list = "; ".join([f"{i+1}: {len(combo)} elements" for i, combo in enumerate(combinations)])
            
            return (result_prompts, combination_info, combination_list)
            
        except Exception as e:
            return (f"Error generating matrix: {str(e)}", "generation_failed", "")


class PromptInterpolator(ValidationMixin):
    """
    Smooth interpolation between two prompts with ratio control.
    Creates seamless transitions between different prompt concepts.
    """
    
    # Interpolation methods
    _INTERPOLATION_METHODS = {
        "linear": "Simple linear blend between prompts",
        "weighted_blend": "Blend with weight syntax for smooth transitions",
        "token_merge": "Merge tokens intelligently based on ratio",
        "semantic_blend": "Attempt semantic blending of similar concepts"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt_a": ("STRING", {"default": "", "multiline": True, "tooltip": "First prompt for interpolation"}),
                "prompt_b": ("STRING", {"default": "", "multiline": True, "tooltip": "Second prompt for interpolation"}),
                "ratio": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Interpolation ratio (0=A, 1=B)"})
            },
            "optional": {
                "method": (list(cls._INTERPOLATION_METHODS.keys()), {"default": "weighted_blend", "tooltip": "Interpolation method"}),
                "steps": ("INT", {"default": 1, "min": 1, "max": 20, "tooltip": "Number of interpolation steps"}),
                "include_endpoints": ("BOOLEAN", {"default": True, "tooltip": "Include original prompts A and B"}),
                "separator": ("STRING", {"default": ", ", "tooltip": "Separator for blended elements"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("interpolated_prompts", "interpolation_info", "step_ratios")
    FUNCTION = "interpolate_prompts"
    CATEGORY = "XDev/Prompt/Advanced"
    DESCRIPTION = "Create smooth transitions between two prompts using various interpolation methods"
    
    @performance_monitor("prompt_interpolation")
    @cached_operation(ttl=300)
    def interpolate_prompts(self, prompt_a: str, prompt_b: str, ratio: float = 0.5,
                          method: str = "weighted_blend", steps: int = 1, include_endpoints: bool = True,
                          separator: str = ", ", validate_input: bool = True):
        
        if validate_input:
            for prompt_name, prompt_val in [("prompt_a", prompt_a), ("prompt_b", prompt_b)]:
                validation = self.validate_string_input(prompt_val, prompt_name)
                if not validation["valid"]:
                    return (f"Error: {validation['error']}", "validation_failed", "")
        
        try:
            # Generate interpolation steps
            if steps == 1:
                ratios = [ratio]
            else:
                if include_endpoints:
                    ratios = [i / (steps - 1) for i in range(steps)]
                else:
                    ratios = [i / (steps + 1) for i in range(1, steps + 1)]
            
            interpolated_prompts = []
            
            # Clean and tokenize prompts
            tokens_a = [token.strip() for token in prompt_a.split(",") if token.strip()]
            tokens_b = [token.strip() for token in prompt_b.split(",") if token.strip()]
            
            for r in ratios:
                if method == "linear":
                    # Simple linear: choose one prompt based on ratio
                    if r < 0.5:
                        result = prompt_a
                    else:
                        result = prompt_b
                        
                elif method == "weighted_blend":
                    # Use ComfyUI weight syntax for blending
                    weight_a = round(1.0 - r, 2)
                    weight_b = round(r, 2)
                    
                    parts = []
                    if weight_a > 0:
                        if weight_a != 1.0:
                            parts.append(f"({prompt_a}:{weight_a})")
                        else:
                            parts.append(prompt_a)
                    
                    if weight_b > 0:
                        if weight_b != 1.0:
                            parts.append(f"({prompt_b}:{weight_b})")
                        else:
                            parts.append(prompt_b)
                    
                    result = " AND ".join(parts)
                    
                elif method == "token_merge":
                    # Intelligently merge tokens based on ratio
                    merged_tokens = []
                    
                    # Add tokens from A with decreasing probability
                    for token in tokens_a:
                        if random.random() > r:  # Less likely as r increases
                            merged_tokens.append(token)
                    
                    # Add tokens from B with increasing probability
                    for token in tokens_b:
                        if random.random() < r:  # More likely as r increases
                            if token not in merged_tokens:  # Avoid duplicates
                                merged_tokens.append(token)
                    
                    result = separator.join(merged_tokens)
                    
                elif method == "semantic_blend":
                    # Attempt semantic blending (simplified)
                    # Mix tokens while trying to maintain coherence
                    all_tokens = list(set(tokens_a + tokens_b))
                    
                    # Select tokens based on ratio and source
                    selected_tokens = []
                    target_count = max(1, int(len(all_tokens) * (0.5 + 0.3 * (1 - abs(0.5 - r)))))
                    
                    # Prefer tokens from the dominant prompt
                    if r < 0.5:
                        priority_tokens = [t for t in tokens_a if t in all_tokens]
                        secondary_tokens = [t for t in tokens_b if t in all_tokens and t not in priority_tokens]
                    else:
                        priority_tokens = [t for t in tokens_b if t in all_tokens]
                        secondary_tokens = [t for t in tokens_a if t in all_tokens and t not in priority_tokens]
                    
                    # Select tokens
                    selected_tokens.extend(priority_tokens[:max(1, int(target_count * (1 - abs(r - 0.5))))])
                    remaining = target_count - len(selected_tokens)
                    if remaining > 0:
                        selected_tokens.extend(secondary_tokens[:remaining])
                    
                    result = separator.join(selected_tokens)
                
                interpolated_prompts.append(result)
            
            # Join all interpolated prompts
            final_prompts = "\n".join(interpolated_prompts)
            
            # Generate info
            interpolation_info = f"Generated {len(ratios)} interpolation steps using {method} method"
            
            # Generate step ratios
            step_ratios = "; ".join([f"Step {i+1}: {r:.3f}" for i, r in enumerate(ratios)])
            
            return (final_prompts, interpolation_info, step_ratios)
            
        except Exception as e:
            return (f"Error interpolating: {str(e)}", "interpolation_failed", "")


class PromptScheduler(ValidationMixin):
    """
    Dynamic prompt changes with step-based scheduling using [prompt_a:prompt_b:step] syntax.
    Enables prompt evolution during generation process.
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "base_prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Base prompt text"}),
                "schedule_syntax": ("STRING", {"default": "[flowers:roses:10]", "multiline": True, "tooltip": "Scheduling syntax [from:to:step] or [from|to]"})
            },
            "optional": {
                "total_steps": ("INT", {"default": 20, "min": 1, "max": 1000, "tooltip": "Total generation steps"}),
                "schedule_mode": (["step_based", "alternating", "progressive"], {"default": "step_based", "tooltip": "Scheduling mode"}),
                "preview_steps": ("BOOLEAN", {"default": True, "tooltip": "Generate step-by-step preview"}),
                "validate_syntax": ("BOOLEAN", {"default": True, "tooltip": "Validate schedule syntax"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("scheduled_prompt", "schedule_info", "step_breakdown")
    FUNCTION = "schedule_prompts"
    CATEGORY = "XDev/Prompt/Advanced"
    DESCRIPTION = "Create dynamic prompt schedules with step-based transitions using ComfyUI syntax"
    
    @performance_monitor("prompt_scheduling")
    @cached_operation(ttl=300)
    def schedule_prompts(self, base_prompt: str, schedule_syntax: str, total_steps: int = 20,
                        schedule_mode: str = "step_based", preview_steps: bool = True,
                        validate_syntax: bool = True, validate_input: bool = True):
        
        if validate_input:
            for name, value in [("base_prompt", base_prompt), ("schedule_syntax", schedule_syntax)]:
                validation = self.validate_string_input(value, name, allow_empty=(name == "base_prompt"))
                if not validation["valid"]:
                    return (f"Error: {validation['error']}", "validation_failed", "")
        
        try:
            import re
            
            # Parse schedule syntax
            schedule_patterns = []
            
            # Pattern for [from:to:step] syntax
            step_pattern = re.compile(r'\[([^:\]]+):([^:\]]+):(\d+)\]')
            # Pattern for [from|to] alternating syntax  
            alt_pattern = re.compile(r'\[([^|\]]+)\|([^|\]]+)\]')
            
            # Find all scheduling patterns
            step_matches = step_pattern.findall(schedule_syntax)
            alt_matches = alt_pattern.findall(schedule_syntax)
            
            if validate_syntax and not step_matches and not alt_matches:
                return ("Invalid schedule syntax. Use [from:to:step] or [from|to] format", "syntax_error", "")
            
            # Build scheduled prompt
            scheduled_prompt = base_prompt
            schedule_info_parts = []
            step_breakdown_parts = []
            
            # Process step-based scheduling
            for from_text, to_text, step_str in step_matches:
                step_num = int(step_str)
                
                if schedule_mode == "step_based":
                    # Replace in base prompt for step-based mode
                    if step_num <= total_steps:
                        # Use from_text until step, then to_text
                        scheduled_prompt = scheduled_prompt.replace(
                            f"[{from_text}:{to_text}:{step_str}]",
                            f"[{from_text}:{to_text}:{step_str}]"  # Keep syntax for ComfyUI
                        )
                    else:
                        # If step is beyond total, use to_text immediately
                        scheduled_prompt = scheduled_prompt.replace(
                            f"[{from_text}:{to_text}:{step_str}]",
                            to_text
                        )
                
                schedule_info_parts.append(f"Step {step_num}: '{from_text}' → '{to_text}'")
                
                if preview_steps:
                    for s in range(1, min(total_steps + 1, step_num + 5)):
                        if s < step_num:
                            step_breakdown_parts.append(f"Step {s}: {from_text}")
                        else:
                            step_breakdown_parts.append(f"Step {s}: {to_text}")
            
            # Process alternating scheduling
            for from_text, to_text in alt_matches:
                if schedule_mode == "alternating":
                    # Keep alternating syntax for ComfyUI
                    scheduled_prompt = scheduled_prompt.replace(
                        f"[{from_text}|{to_text}]",
                        f"[{from_text}|{to_text}]"
                    )
                elif schedule_mode == "progressive":
                    # Use progressive blending
                    mid_step = total_steps // 2
                    scheduled_prompt = scheduled_prompt.replace(
                        f"[{from_text}|{to_text}]",
                        f"[{from_text}:{to_text}:{mid_step}]"
                    )
                
                schedule_info_parts.append(f"Alternating: '{from_text}' ↔ '{to_text}'")
                
                if preview_steps:
                    for s in range(1, min(total_steps + 1, 6)):
                        current_text = from_text if s % 2 == 1 else to_text
                        step_breakdown_parts.append(f"Step {s}: {current_text}")
            
            # Generate info
            schedule_info = f"Processed {len(step_matches + alt_matches)} schedule patterns in {schedule_mode} mode"
            if schedule_info_parts:
                schedule_info += ": " + "; ".join(schedule_info_parts)
            
            # Generate breakdown
            if step_breakdown_parts:
                step_breakdown = "; ".join(step_breakdown_parts[:20])  # Limit output
                if len(step_breakdown_parts) > 20:
                    step_breakdown += "..."
            else:
                step_breakdown = f"Scheduled for {total_steps} steps using {schedule_mode} mode"
            
            return (scheduled_prompt, schedule_info, step_breakdown)
            
        except Exception as e:
            return (f"Error scheduling: {str(e)}", "scheduling_failed", "")


class PromptAttention(ValidationMixin):
    """
    ComfyUI-style attention weight manipulation using () for emphasis and [] for de-emphasis.
    Supports custom multipliers like (word:1.2) for precise attention control.
    """
    
    # Attention operations
    _ATTENTION_OPERATIONS = {
        "add_emphasis": "Add () emphasis to specified terms",
        "add_deemphasis": "Add [] de-emphasis to specified terms", 
        "set_weights": "Set specific weights like (term:1.2)",
        "auto_enhance": "Automatically enhance important terms",
        "balance_weights": "Balance existing weights for better distribution",
        "remove_weights": "Remove all attention modifiers"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Input prompt to modify"}),
                "operation": (list(cls._ATTENTION_OPERATIONS.keys()), {"default": "add_emphasis", "tooltip": "Attention operation to perform"})
            },
            "optional": {
                "target_terms": ("STRING", {"default": "", "tooltip": "Comma-separated terms to modify (empty = auto-detect)"}),
                "emphasis_weight": ("FLOAT", {"default": 1.2, "min": 0.1, "max": 3.0, "step": 0.1, "tooltip": "Weight for emphasis"}),
                "deemphasis_weight": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 0.95, "step": 0.05, "tooltip": "Weight for de-emphasis"}),
                "important_keywords": ("STRING", {"default": "masterpiece, detailed, high quality, professional, beautiful", "tooltip": "Keywords considered important"}),
                "preserve_existing": ("BOOLEAN", {"default": True, "tooltip": "Preserve existing attention weights"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("weighted_prompt", "attention_info", "weight_analysis")
    FUNCTION = "modify_attention"
    CATEGORY = "XDev/Prompt/Advanced"
    DESCRIPTION = "Manipulate prompt attention weights using ComfyUI () and [] syntax with precise control"
    
    @performance_monitor("attention_modification")
    @cached_operation(ttl=300)
    def modify_attention(self, prompt: str, operation: str = "add_emphasis",
                        target_terms: str = "", emphasis_weight: float = 1.2, deemphasis_weight: float = 0.8,
                        important_keywords: str = "", preserve_existing: bool = True, validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(prompt, "prompt")
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", "")
        
        try:
            import re
            
            # Parse existing weights
            existing_weights = []
            weight_pattern = re.compile(r'\(([^)]+):([0-9.]+)\)')
            emphasis_pattern = re.compile(r'\(([^)]+)\)')
            deemphasis_pattern = re.compile(r'\[([^\]]+)\]')
            
            # Find existing patterns
            existing_weights = weight_pattern.findall(prompt)
            existing_emphasis = emphasis_pattern.findall(prompt)
            existing_deemphasis = deemphasis_pattern.findall(prompt)
            
            result_prompt = prompt
            modifications = []
            
            if operation == "remove_weights":
                # Remove all attention modifiers
                result_prompt = weight_pattern.sub(r'\1', result_prompt)
                result_prompt = emphasis_pattern.sub(r'\1', result_prompt)
                result_prompt = deemphasis_pattern.sub(r'\1', result_prompt)
                modifications.append(f"Removed all weights and attention modifiers")
                
            elif operation == "add_emphasis":
                # Add emphasis to target terms
                terms = [t.strip() for t in target_terms.split(",") if t.strip()] if target_terms else []
                
                if not terms:
                    # Auto-detect important terms
                    important_terms = [t.strip() for t in important_keywords.split(",") if t.strip()]
                    terms = [term for term in important_terms if term.lower() in prompt.lower()]
                
                for term in terms:
                    if preserve_existing and (f"({term}" in result_prompt or f"[{term}" in result_prompt):
                        continue  # Skip if already has attention modifier
                    
                    # Replace term with emphasized version
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    if emphasis_weight == 1.1:
                        replacement = f"({term})"
                    else:
                        replacement = f"({term}:{emphasis_weight})"
                    
                    if pattern.search(result_prompt):
                        result_prompt = pattern.sub(replacement, result_prompt, count=1)
                        modifications.append(f"Emphasized '{term}' with weight {emphasis_weight}")
                
            elif operation == "add_deemphasis":
                # Add de-emphasis to target terms
                terms = [t.strip() for t in target_terms.split(",") if t.strip()] if target_terms else []
                
                for term in terms:
                    if preserve_existing and (f"({term}" in result_prompt or f"[{term}" in result_prompt):
                        continue
                    
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    if deemphasis_weight == (1/1.1):
                        replacement = f"[{term}]"
                    else:
                        replacement = f"({term}:{deemphasis_weight})"
                    
                    if pattern.search(result_prompt):
                        result_prompt = pattern.sub(replacement, result_prompt, count=1)
                        modifications.append(f"De-emphasized '{term}' with weight {deemphasis_weight}")
                
            elif operation == "set_weights":
                # Set specific weights for target terms
                terms = [t.strip() for t in target_terms.split(",") if t.strip()] if target_terms else []
                
                for term in terms:
                    # Remove existing weights for this term
                    clean_term = re.sub(r'[():\[\]0-9.]', '', term).strip()
                    
                    # Find and replace the term with weighted version
                    pattern = re.compile(re.escape(clean_term), re.IGNORECASE)
                    replacement = f"({clean_term}:{emphasis_weight})"
                    
                    if pattern.search(result_prompt):
                        result_prompt = pattern.sub(replacement, result_prompt, count=1)
                        modifications.append(f"Set '{clean_term}' weight to {emphasis_weight}")
                
            elif operation == "auto_enhance":
                # Automatically enhance important terms
                important_terms = [t.strip() for t in important_keywords.split(",") if t.strip()]
                
                for term in important_terms:
                    if term.lower() in result_prompt.lower() and f"({term}" not in result_prompt and f"[{term}" not in result_prompt:
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        replacement = f"({term}:{emphasis_weight})"
                        result_prompt = pattern.sub(replacement, result_prompt, count=1)
                        modifications.append(f"Auto-enhanced '{term}'")
                
            elif operation == "balance_weights":
                # Balance existing weights
                weights = weight_pattern.findall(result_prompt)
                if weights:
                    # Calculate average weight
                    avg_weight = sum(float(w[1]) for w in weights) / len(weights)
                    
                    # Adjust weights toward average
                    for term, weight in weights:
                        old_weight = float(weight)
                        new_weight = round((old_weight + avg_weight) / 2, 2)
                        
                        old_pattern = f"({term}:{old_weight})"
                        new_pattern = f"({term}:{new_weight})"
                        result_prompt = result_prompt.replace(old_pattern, new_pattern)
                        modifications.append(f"Balanced '{term}': {old_weight} → {new_weight}")
            
            # Generate analysis
            final_weights = weight_pattern.findall(result_prompt)
            final_emphasis = emphasis_pattern.findall(result_prompt)
            final_deemphasis = deemphasis_pattern.findall(result_prompt)
            
            # Generate info
            attention_info = f"Applied {operation} operation"
            if modifications:
                attention_info += f": {len(modifications)} modifications made"
            
            # Generate analysis
            analysis_parts = []
            if final_weights:
                analysis_parts.append(f"Weighted terms: {len(final_weights)}")
            if final_emphasis:
                analysis_parts.append(f"Emphasized: {len(final_emphasis)}")
            if final_deemphasis:
                analysis_parts.append(f"De-emphasized: {len(final_deemphasis)}")
                
            weight_analysis = "; ".join(analysis_parts) if analysis_parts else "No attention modifiers found"
            
            return (result_prompt, attention_info, weight_analysis)
            
        except Exception as e:
            return (f"Error modifying attention: {str(e)}", "modification_failed", "")


class PromptChainOfThought(ValidationMixin):
    """
    Advanced reasoning structure generation using Chain-of-Thought prompting techniques.
    Breaks complex prompts into step-by-step reasoning structures for better AI understanding.
    """
    
    # Chain-of-thought templates
    _COT_TEMPLATES = {
        "step_by_step": "Let's think step by step:\n1. {analysis}\n2. {reasoning}\n3. {conclusion}",
        "problem_solving": "Problem: {problem}\nAnalysis: {analysis}\nSolution approach: {approach}\nResult: {result}",
        "creative_process": "Creative concept: {concept}\nInspiration: {inspiration}\nDevelopment: {development}\nFinal vision: {vision}",
        "technical_breakdown": "Objective: {objective}\nRequirements: {requirements}\nImplementation: {implementation}\nExpected outcome: {outcome}",
        "artistic_analysis": "Subject: {subject}\nStyle considerations: {style}\nComposition approach: {composition}\nAesthetic goals: {aesthetic}"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "base_prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Base prompt to enhance with CoT"}),
                "reasoning_style": (list(cls._COT_TEMPLATES.keys()), {"default": "step_by_step", "tooltip": "Chain-of-thought template style"})
            },
            "optional": {
                "complexity_level": (["simple", "moderate", "detailed", "comprehensive"], {"default": "moderate", "tooltip": "Reasoning complexity level"}),
                "include_examples": ("BOOLEAN", {"default": False, "tooltip": "Include reasoning examples"}),
                "custom_structure": ("STRING", {"default": "", "multiline": True, "tooltip": "Custom CoT structure template"}),
                "reasoning_prefix": ("STRING", {"default": "Reasoning: ", "tooltip": "Prefix for reasoning section"}),
                "conclusion_prefix": ("STRING", {"default": "Therefore: ", "tooltip": "Prefix for conclusion"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("cot_prompt", "reasoning_info", "structure_breakdown")
    FUNCTION = "generate_chain_of_thought"
    CATEGORY = "XDev/Prompt/Advanced"  
    DESCRIPTION = "Generate Chain-of-Thought reasoning structures to enhance prompt clarity and AI understanding"
    
    @performance_monitor("chain_of_thought")
    @cached_operation(ttl=300)
    def generate_chain_of_thought(self, base_prompt: str, reasoning_style: str = "step_by_step",
                                 complexity_level: str = "moderate", include_examples: bool = False,
                                 custom_structure: str = "", reasoning_prefix: str = "Reasoning: ",
                                 conclusion_prefix: str = "Therefore: ", validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(base_prompt, "base_prompt")
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", "")
        
        try:
            # Use custom structure if provided
            if custom_structure.strip():
                template = custom_structure
                reasoning_style = "custom"
            else:
                template = self._COT_TEMPLATES[reasoning_style]
            
            # Analyze base prompt to extract components
            prompt_analysis = self._analyze_prompt(base_prompt)
            
            # Generate reasoning components based on complexity level
            reasoning_components = self._generate_reasoning_components(
                prompt_analysis, complexity_level, reasoning_style
            )
            
            # Build Chain-of-Thought structure
            if reasoning_style == "step_by_step":
                cot_structure = self._build_step_by_step(reasoning_components, reasoning_prefix, conclusion_prefix)
            elif reasoning_style == "problem_solving":
                cot_structure = self._build_problem_solving(reasoning_components)
            elif reasoning_style == "creative_process":
                cot_structure = self._build_creative_process(reasoning_components)
            elif reasoning_style == "technical_breakdown":
                cot_structure = self._build_technical_breakdown(reasoning_components)
            elif reasoning_style == "artistic_analysis":
                cot_structure = self._build_artistic_analysis(reasoning_components)
            elif reasoning_style == "custom":
                cot_structure = self._build_custom_structure(template, reasoning_components)
            else:
                cot_structure = self._build_generic_cot(reasoning_components, reasoning_prefix, conclusion_prefix)
            
            # Add examples if requested
            if include_examples:
                examples = self._generate_examples(reasoning_style, complexity_level)
                cot_structure = f"{examples}\n\n{cot_structure}"
            
            # Combine with original prompt
            final_prompt = f"{base_prompt}\n\n{cot_structure}"
            
            # Generate info
            reasoning_info = f"Generated {reasoning_style} CoT structure with {complexity_level} complexity"
            if include_examples:
                reasoning_info += " including examples"
            
            # Generate structure breakdown
            structure_parts = []
            lines = cot_structure.split('\n')
            for i, line in enumerate(lines[:5]):  # First 5 lines
                if line.strip():
                    structure_parts.append(f"L{i+1}: {line[:50]}...")
            
            structure_breakdown = "; ".join(structure_parts)
            
            return (final_prompt, reasoning_info, structure_breakdown)
            
        except Exception as e:
            return (f"Error generating CoT: {str(e)}", "generation_failed", "")
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, str]:
        """Analyze prompt to identify key components"""
        # Simple analysis - extract key elements
        words = prompt.lower().split()
        
        # Identify subject, style, and action words
        subjects = [w for w in words if w in ['person', 'woman', 'man', 'character', 'figure', 'portrait']]
        styles = [w for w in words if w in ['realistic', 'artistic', 'abstract', 'detailed', 'stylized']]
        actions = [w for w in words if w in ['sitting', 'standing', 'walking', 'looking', 'holding']]
        
        return {
            "original": prompt,
            "subjects": ', '.join(subjects) or "unspecified subject",
            "styles": ', '.join(styles) or "default style", 
            "actions": ', '.join(actions) or "static pose",
            "length": len(words),
            "complexity": "complex" if len(words) > 20 else "moderate" if len(words) > 10 else "simple"
        }
    
    def _generate_reasoning_components(self, analysis: Dict[str, str], complexity: str, style: str) -> Dict[str, str]:
        """Generate reasoning components based on analysis"""
        components = {
            "analysis": f"The prompt describes {analysis['subjects']} with {analysis['styles']} characteristics",
            "reasoning": f"This requires attention to {analysis['subjects']} and {analysis['styles']} elements",
            "conclusion": f"Focus on {analysis['subjects']} with emphasis on {analysis['styles']} presentation"
        }
        
        if complexity == "detailed":
            components["analysis"] += f", involving {analysis['actions']}"
            components["reasoning"] += f", considering composition and {analysis['actions']}"
            components["conclusion"] += f" while incorporating {analysis['actions']}"
        elif complexity == "comprehensive":
            components["analysis"] += f", with {analysis['actions']} and complex visual elements"
            components["reasoning"] += f", balancing multiple aspects including lighting, composition, and {analysis['actions']}"
            components["conclusion"] += f", ensuring coherent integration of {analysis['actions']} and visual harmony"
        
        return components
    
    def _build_step_by_step(self, components: Dict[str, str], reasoning_prefix: str, conclusion_prefix: str) -> str:
        """Build step-by-step CoT structure"""
        return f"""Let's think step by step:
1. Analysis: {components['analysis']}
2. {reasoning_prefix}{components['reasoning']}
3. {conclusion_prefix}{components['conclusion']}"""
    
    def _build_problem_solving(self, components: Dict[str, str]) -> str:
        """Build problem-solving CoT structure"""
        return f"""Problem: Generate the described visual content
Analysis: {components['analysis']}
Solution approach: {components['reasoning']}
Result: {components['conclusion']}"""
    
    def _build_creative_process(self, components: Dict[str, str]) -> str:
        """Build creative process CoT structure"""
        return f"""Creative concept: {components['analysis']}
Inspiration: Drawing from artistic traditions and visual storytelling
Development: {components['reasoning']}
Final vision: {components['conclusion']}"""
    
    def _build_technical_breakdown(self, components: Dict[str, str]) -> str:
        """Build technical breakdown CoT structure"""
        return f"""Objective: Create the specified visual content
Requirements: {components['analysis']}
Implementation: {components['reasoning']}
Expected outcome: {components['conclusion']}"""
    
    def _build_artistic_analysis(self, components: Dict[str, str]) -> str:
        """Build artistic analysis CoT structure"""
        return f"""Subject: {components['analysis']}
Style considerations: Focus on artistic coherence and visual impact
Composition approach: {components['reasoning']}
Aesthetic goals: {components['conclusion']}"""
    
    def _build_custom_structure(self, template: str, components: Dict[str, str]) -> str:
        """Build custom CoT structure"""
        # Simple placeholder replacement
        result = template
        for key, value in components.items():
            result = result.replace(f"{{{key}}}", value)
        return result
    
    def _build_generic_cot(self, components: Dict[str, str], reasoning_prefix: str, conclusion_prefix: str) -> str:
        """Build generic CoT structure"""
        return f"""{reasoning_prefix}{components['analysis']}
{reasoning_prefix}{components['reasoning']}
{conclusion_prefix}{components['conclusion']}"""
    
    def _generate_examples(self, style: str, complexity: str) -> str:
        """Generate examples for the CoT structure"""
        examples = {
            "step_by_step": "Example: For 'beautiful sunset', we think:\n1. Analysis: Natural lighting scene\n2. Reasoning: Warm colors and atmospheric effects needed\n3. Therefore: Focus on golden hour lighting with rich color palette",
            "creative_process": "Example: Creative concept: Peaceful landscape → Inspiration: Natural beauty → Development: Soft lighting and composition → Final vision: Serene, harmonious scene"
        }
        
        return examples.get(style, "Example: Break down the prompt into logical components, analyze requirements, and synthesize the final approach.")


class PromptFewShot(ValidationMixin):
    """
    Intelligent example selection and management for few-shot prompting.
    Dynamically selects relevant examples based on similarity and manages example databases.
    """
    
    # Pre-defined example categories
    _EXAMPLE_CATEGORIES = {
        "portrait": [
            "professional headshot of a business woman, confident expression, studio lighting",
            "artistic portrait of an elderly man, wise expression, dramatic lighting",
            "casual portrait of a young person, friendly smile, natural lighting"
        ],
        "landscape": [
            "serene mountain landscape, golden hour lighting, peaceful atmosphere",
            "dramatic seascape with stormy clouds, powerful waves, moody lighting",
            "lush forest scene, dappled sunlight, vibrant green foliage"
        ],
        "artistic": [
            "abstract expressionist painting, bold brushstrokes, vibrant colors",
            "impressionist garden scene, soft pastels, dreamy atmosphere",
            "surrealist composition, impossible geometry, thought-provoking imagery"
        ],
        "technical": [
            "highly detailed mechanical device, precise engineering, technical illustration",
            "architectural blueprint style, clean lines, professional diagram",
            "scientific visualization, accurate data representation, clear labeling"
        ]
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "target_prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Target prompt to find examples for"}),
                "example_category": (["auto"] + list(cls._EXAMPLE_CATEGORIES.keys()), {"default": "auto", "tooltip": "Example category to use"})
            },
            "optional": {
                "num_examples": ("INT", {"default": 3, "min": 1, "max": 10, "tooltip": "Number of examples to include"}),
                "custom_examples": ("STRING", {"default": "", "multiline": True, "tooltip": "Custom examples (one per line)"}),
                "similarity_threshold": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1, "tooltip": "Minimum similarity for auto-selection"}),
                "selection_method": (["similarity", "diversity", "length", "random"], {"default": "similarity", "tooltip": "Example selection method"}),
                "include_instructions": ("BOOLEAN", {"default": True, "tooltip": "Include few-shot instructions"}),
                "format_style": (["numbered", "bulleted", "paragraphs", "templates"], {"default": "numbered", "tooltip": "Output formatting style"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("few_shot_prompt", "selection_info", "example_analysis")
    FUNCTION = "generate_few_shot"
    CATEGORY = "XDev/Prompt/Advanced"
    DESCRIPTION = "Generate few-shot prompts with intelligent example selection and similarity matching"
    
    @performance_monitor("few_shot_generation")
    @cached_operation(ttl=300)
    def generate_few_shot(self, target_prompt: str, example_category: str = "auto",
                         num_examples: int = 3, custom_examples: str = "",
                         similarity_threshold: float = 0.3, selection_method: str = "similarity",
                         include_instructions: bool = True, format_style: str = "numbered",
                         validate_input: bool = True):
        
        if validate_input:
            validation = self.validate_string_input(target_prompt, "target_prompt")
            if not validation["valid"]:
                return (f"Error: {validation['error']}", "validation_failed", "")
        
        try:
            # Prepare example pool
            if custom_examples.strip():
                # Use custom examples
                example_pool = [ex.strip() for ex in custom_examples.split('\n') if ex.strip()]
                selected_category = "custom"
            elif example_category == "auto":
                # Auto-detect category
                selected_category = self._detect_category(target_prompt)
                example_pool = self._EXAMPLE_CATEGORIES[selected_category]
            else:
                # Use specified category
                selected_category = example_category
                example_pool = self._EXAMPLE_CATEGORIES[example_category]
            
            # Select examples based on method
            if selection_method == "similarity":
                selected_examples = self._select_by_similarity(target_prompt, example_pool, num_examples, similarity_threshold)
            elif selection_method == "diversity":
                selected_examples = self._select_by_diversity(example_pool, num_examples)
            elif selection_method == "length":
                selected_examples = self._select_by_length(target_prompt, example_pool, num_examples)
            elif selection_method == "random":
                selected_examples = self._select_randomly(example_pool, num_examples)
            else:
                selected_examples = example_pool[:num_examples]
            
            # Format the few-shot prompt
            few_shot_prompt = self._format_few_shot_prompt(
                target_prompt, selected_examples, format_style, include_instructions
            )
            
            # Generate info
            selection_info = f"Selected {len(selected_examples)} examples from {selected_category} category using {selection_method} method"
            
            # Generate analysis
            analysis_parts = []
            for i, example in enumerate(selected_examples):
                similarity_score = self._calculate_similarity(target_prompt, example)
                analysis_parts.append(f"Ex{i+1}: {similarity_score:.2f} sim, {len(example.split())} words")
            
            example_analysis = "; ".join(analysis_parts)
            
            return (few_shot_prompt, selection_info, example_analysis)
            
        except Exception as e:
            return (f"Error generating few-shot: {str(e)}", "generation_failed", "")
    
    def _detect_category(self, prompt: str) -> str:
        """Auto-detect the most appropriate example category"""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based detection
        category_keywords = {
            "portrait": ["portrait", "person", "face", "headshot", "character", "man", "woman"],
            "landscape": ["landscape", "mountain", "forest", "sea", "nature", "outdoor", "scenery"],
            "artistic": ["art", "painting", "abstract", "style", "artistic", "creative", "expression"],
            "technical": ["technical", "diagram", "blueprint", "mechanical", "engineering", "precise"]
        }
        
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            scores[category] = score
        
        # Return category with highest score, default to portrait
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "portrait"
    
    def _calculate_similarity(self, prompt1: str, prompt2: str) -> float:
        """Calculate simple word-based similarity between prompts"""
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _select_by_similarity(self, target: str, examples: List[str], num: int, threshold: float) -> List[str]:
        """Select examples based on similarity to target prompt"""
        scored_examples = []
        
        for example in examples:
            similarity = self._calculate_similarity(target, example)
            if similarity >= threshold:
                scored_examples.append((example, similarity))
        
        # Sort by similarity and take top N
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        return [ex[0] for ex in scored_examples[:num]]
    
    def _select_by_diversity(self, examples: List[str], num: int) -> List[str]:
        """Select diverse examples to maximize variety"""
        if len(examples) <= num:
            return examples
        
        selected = [examples[0]]  # Start with first example
        
        for _ in range(num - 1):
            best_candidate = None
            best_min_similarity = -1
            
            # Find example with minimum similarity to already selected
            for candidate in examples:
                if candidate in selected:
                    continue
                
                min_similarity = min(
                    self._calculate_similarity(candidate, selected_ex)
                    for selected_ex in selected
                )
                
                if min_similarity > best_min_similarity:
                    best_min_similarity = min_similarity
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
        
        return selected
    
    def _select_by_length(self, target: str, examples: List[str], num: int) -> List[str]:
        """Select examples with similar length to target"""
        target_length = len(target.split())
        
        # Sort by length similarity
        sorted_examples = sorted(
            examples, 
            key=lambda x: abs(len(x.split()) - target_length)
        )
        
        return sorted_examples[:num]
    
    def _select_randomly(self, examples: List[str], num: int) -> List[str]:
        """Randomly select examples"""
        if len(examples) <= num:
            return examples
        
        return random.sample(examples, num)
    
    def _format_few_shot_prompt(self, target: str, examples: List[str], format_style: str, include_instructions: bool) -> str:
        """Format the final few-shot prompt"""
        parts = []
        
        if include_instructions:
            instruction = "Here are some examples of well-constructed prompts:"
            parts.append(instruction)
            parts.append("")
        
        # Format examples
        for i, example in enumerate(examples):
            if format_style == "numbered":
                parts.append(f"{i+1}. {example}")
            elif format_style == "bulleted":
                parts.append(f"• {example}")
            elif format_style == "paragraphs":
                parts.append(example)
                parts.append("")
            elif format_style == "templates":
                parts.append(f"Example {i+1}: {example}")
        
        # Add target prompt section
        if format_style != "paragraphs":
            parts.append("")
        
        if include_instructions:
            parts.append("Now, following the style and quality of the examples above:")
            
        parts.append(target)
        
        return "\n".join(parts)


class LLMPersonBuilder(ValidationMixin):
    """
    LLM-enhanced person/character builder with AI-powered personality analysis
    and intelligent trait generation for consistent, detailed character creation.
    
    Features:
    - AI-powered personality development
    - Trait consistency validation
    - Dynamic character evolution
    - Context-aware generation
    """
    
    @classmethod  
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "character_concept": ("STRING", {
                    "default": "confident professional",
                    "tooltip": "Basic character concept or archetype"
                }),
                "personality_traits": ("STRING", {
                    "multiline": True,
                    "default": "intelligent, charismatic, determined",
                    "tooltip": "Key personality traits (comma-separated)"
                }),
                "physical_description": ("STRING", {
                    "multiline": True,
                    "default": "adult, professional appearance",
                    "tooltip": "Basic physical description"
                }),
                "context": ("STRING", {
                    "default": "professional portrait",
                    "tooltip": "Context or setting for the character"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL for AI enhancement"
                }),
                "model": ("STRING", {
                    "default": "local-model", 
                    "tooltip": "Model name for character generation"
                })
            },
            "optional": {
                "background_story": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Optional background story or history"
                }),
                "profession": ("STRING", {
                    "default": "",
                    "tooltip": "Character's profession or role"
                }),
                "age_range": ("STRING", {
                    "default": "",
                    "tooltip": "Specific age range (e.g., '25-30', 'middle-aged')"
                }),
                "special_features": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Special or unique characteristics"
                }),
                "use_llm_enhancement": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable AI-powered character enhancement"
                }),
                "consistency_check": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Validate trait consistency using AI"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("character_prompt", "personality_analysis", "trait_summary", "enhancement_info")
    FUNCTION = "build_llm_character"
    CATEGORY = "XDev/LLM/Character"
    DESCRIPTION = "Build intelligent, consistent characters using AI-powered personality analysis and trait generation"
    
    @performance_monitor("llm_person_builder")
    def build_llm_character(
        self,
        character_concept: str,
        personality_traits: str,
        physical_description: str,
        context: str,
        server_url: str,
        model: str,
        background_story: str = "",
        profession: str = "",
        age_range: str = "",
        special_features: str = "",
        use_llm_enhancement: bool = True,
        consistency_check: bool = True,
        validate_input: bool = True
    ) -> Tuple[str, str, str, str]:
        """Build AI-enhanced character using LLM intelligence."""
        
        if validate_input:
            if not character_concept.strip():
                return ("", "", "", "Error: Character concept cannot be empty")
        
        try:
            # Import LLM framework
            from .llm_integration import LLMPromptFramework
            
            if use_llm_enhancement:
                # Build character context
                character_context = self._build_character_context(
                    character_concept, personality_traits, physical_description,
                    context, background_story, profession, age_range, special_features
                )
                
                # Create base prompt for enhancement
                base_prompt = f"Character: {character_concept}"
                if profession:
                    base_prompt += f", {profession}"
                
                # Initialize LLM framework
                llm_framework = LLMPromptFramework(server_url, model)
                
                # Enhance character using LLM
                enhanced_prompt, enhancement_info = llm_framework.enhance_prompt(
                    base_prompt=base_prompt,
                    enhancement_type="character_generation",
                    context=character_context,
                    additional_instructions="Focus on creating a cohesive, believable character with consistent traits and compelling details."
                )
                
                # Generate personality analysis
                personality_analysis = self._analyze_personality_with_llm(
                    enhanced_prompt, personality_traits, llm_framework
                )
                
            else:
                # Fallback to template-based generation
                enhanced_prompt = self._build_template_character(
                    character_concept, personality_traits, physical_description,
                    context, profession, age_range, special_features
                )
                enhancement_info = "Template-based generation (LLM disabled)"
                personality_analysis = self._analyze_personality_template(personality_traits)
            
            # Create trait summary
            trait_summary = self._create_trait_summary(
                personality_traits, profession, age_range, context
            )
            
            # Consistency check if enabled
            if consistency_check and use_llm_enhancement:
                consistency_result = self._check_consistency_with_llm(
                    enhanced_prompt, personality_traits, llm_framework
                )
                enhancement_info += f"\nConsistency: {consistency_result}"
            
            return (enhanced_prompt, personality_analysis, trait_summary, enhancement_info)
            
        except Exception as e:
            error_info = f"LLM character building failed: {str(e)}"
            # Fallback to basic character
            fallback_prompt = f"{character_concept}, {personality_traits}, {physical_description}"
            return (fallback_prompt, "Basic character (error fallback)", personality_traits, error_info)
    
    def _build_character_context(self, concept: str, traits: str, physical: str,
                               context: str, background: str, profession: str,
                               age_range: str, special_features: str) -> str:
        """Build comprehensive character context for LLM."""
        
        context_parts = [
            f"Character concept: {concept}",
            f"Personality traits: {traits}",
            f"Physical description: {physical}",
            f"Context/Setting: {context}"
        ]
        
        if profession.strip():
            context_parts.append(f"Profession: {profession}")
        
        if age_range.strip():
            context_parts.append(f"Age range: {age_range}")
        
        if background.strip():
            context_parts.append(f"Background: {background}")
        
        if special_features.strip():
            context_parts.append(f"Special features: {special_features}")
        
        return "\n".join(context_parts)
    
    def _analyze_personality_with_llm(self, character_prompt: str, traits: str,
                                    llm_framework) -> str:
        """Analyze personality using LLM."""
        
        try:
            analysis_prompt = f"Analyze the personality of this character: {character_prompt}"
            analysis_context = f"Focus on these traits: {traits}"
            
            analysis, _ = llm_framework.enhance_prompt(
                base_prompt=analysis_prompt,
                enhancement_type="character_generation",
                context=analysis_context,
                additional_instructions="Provide a detailed personality analysis focusing on consistency, depth, and psychological realism."
            )
            
            return analysis
            
        except Exception as e:
            return f"Personality analysis failed: {str(e)}"
    
    def _check_consistency_with_llm(self, character_prompt: str, traits: str,
                                  llm_framework) -> str:
        """Check character consistency using LLM."""
        
        try:
            consistency_prompt = f"Check the consistency of this character description: {character_prompt}"
            consistency_context = f"Expected traits: {traits}"
            
            consistency, _ = llm_framework.enhance_prompt(
                base_prompt=consistency_prompt,
                enhancement_type="character_generation",
                context=consistency_context,
                additional_instructions="Evaluate consistency, identify conflicts, and suggest improvements if needed. Be concise."
            )
            
            return consistency[:200] + "..." if len(consistency) > 200 else consistency
            
        except Exception as e:
            return f"Consistency check failed: {str(e)}"
    
    def _build_template_character(self, concept: str, traits: str, physical: str,
                                context: str, profession: str, age_range: str,
                                special_features: str) -> str:
        """Build character using templates as fallback."""
        
        parts = [concept]
        
        if profession:
            parts.append(profession)
        
        if age_range:
            parts.append(age_range)
        
        parts.append(physical)
        parts.append(traits)
        
        if special_features:
            parts.append(special_features)
        
        parts.append(context)
        
        return ", ".join(part.strip() for part in parts if part.strip())
    
    def _analyze_personality_template(self, traits: str) -> str:
        """Template-based personality analysis."""
        
        trait_list = [t.strip() for t in traits.split(",") if t.strip()]
        
        analysis = f"Personality Analysis:\n"
        analysis += f"• Primary traits: {', '.join(trait_list[:3])}\n"
        
        if len(trait_list) > 3:
            analysis += f"• Secondary traits: {', '.join(trait_list[3:])}\n"
        
        analysis += f"• Trait count: {len(trait_list)}\n"
        analysis += "• Analysis method: Template-based"
        
        return analysis
    
    def _create_trait_summary(self, traits: str, profession: str, 
                            age_range: str, context: str) -> str:
        """Create a summary of character traits."""
        
        summary = []
        
        trait_count = len([t for t in traits.split(",") if t.strip()])
        summary.append(f"Traits: {trait_count} defined")
        
        if profession.strip():
            summary.append(f"Profession: {profession}")
        
        if age_range.strip():
            summary.append(f"Age: {age_range}")
        
        summary.append(f"Context: {context}")
        
        return " | ".join(summary)


class LLMStyleBuilder(ValidationMixin):
    """
    LLM-enhanced artistic style builder with AI-powered style analysis
    and intelligent style combination for cohesive artistic descriptions.
    
    Features:
    - AI-powered style coherence checking
    - Style combination suggestions
    - Technical accuracy validation
    - Artistic period awareness
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "base_style": ("STRING", {
                    "default": "digital painting",
                    "tooltip": "Primary artistic style or medium"
                }),
                "artistic_elements": ("STRING", {
                    "multiline": True,
                    "default": "vibrant colors, dramatic lighting",
                    "tooltip": "Key artistic elements (comma-separated)"
                }),
                "composition": ("STRING", {
                    "default": "rule of thirds",
                    "tooltip": "Compositional approach or technique"
                }),
                "mood": ("STRING", {
                    "default": "epic",
                    "tooltip": "Overall mood or atmosphere"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL for AI enhancement"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model name for style generation"
                })
            },
            "optional": {
                "reference_artists": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Reference artists or art movements"
                }),
                "color_palette": ("STRING", {
                    "default": "",
                    "tooltip": "Specific color palette or scheme"
                }),
                "technical_details": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Technical aspects (brush strokes, texture, etc.)"
                }),
                "historical_period": ("STRING", {
                    "default": "",
                    "tooltip": "Historical art period or era"
                }),
                "use_llm_enhancement": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable AI-powered style enhancement"
                }),
                "coherence_check": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Validate style coherence using AI"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING") 
    RETURN_NAMES = ("style_prompt", "style_analysis", "coherence_report", "enhancement_info")
    FUNCTION = "build_llm_style"
    CATEGORY = "XDev/LLM/Style"
    DESCRIPTION = "Build intelligent, cohesive artistic styles using AI-powered analysis and style coordination"
    
    @performance_monitor("llm_style_builder")
    def build_llm_style(
        self,
        base_style: str,
        artistic_elements: str,
        composition: str,
        mood: str,
        server_url: str,
        model: str,
        reference_artists: str = "",
        color_palette: str = "",
        technical_details: str = "",
        historical_period: str = "",
        use_llm_enhancement: bool = True,
        coherence_check: bool = True,
        validate_input: bool = True
    ) -> Tuple[str, str, str, str]:
        """Build AI-enhanced artistic style using LLM intelligence."""
        
        if validate_input:
            if not base_style.strip():
                return ("", "", "", "Error: Base style cannot be empty")
        
        try:
            # Import LLM framework
            from .llm_integration import LLMPromptFramework
            
            if use_llm_enhancement:
                # Build style context
                style_context = self._build_style_context(
                    base_style, artistic_elements, composition, mood,
                    reference_artists, color_palette, technical_details, historical_period
                )
                
                # Create base prompt for enhancement
                base_prompt = f"Artistic style: {base_style}"
                if reference_artists:
                    base_prompt += f", inspired by {reference_artists}"
                
                # Initialize LLM framework
                llm_framework = LLMPromptFramework(server_url, model)
                
                # Enhance style using LLM
                enhanced_prompt, enhancement_info = llm_framework.enhance_prompt(
                    base_prompt=base_prompt,
                    enhancement_type="style_generation",
                    context=style_context,
                    additional_instructions="Focus on creating a cohesive, technically accurate, and artistically sound style description."
                )
                
                # Generate style analysis
                style_analysis = self._analyze_style_with_llm(
                    enhanced_prompt, artistic_elements, llm_framework
                )
                
                # Coherence check if enabled
                if coherence_check:
                    coherence_report = self._check_style_coherence_with_llm(
                        enhanced_prompt, base_style, llm_framework
                    )
                else:
                    coherence_report = "Coherence check disabled"
                
            else:
                # Fallback to template-based generation
                enhanced_prompt = self._build_template_style(
                    base_style, artistic_elements, composition, mood,
                    reference_artists, color_palette, technical_details
                )
                enhancement_info = "Template-based generation (LLM disabled)"
                style_analysis = self._analyze_style_template(artistic_elements)
                coherence_report = "No coherence check (LLM disabled)"
            
            return (enhanced_prompt, style_analysis, coherence_report, enhancement_info)
            
        except Exception as e:
            error_info = f"LLM style building failed: {str(e)}"
            # Fallback to basic style
            fallback_prompt = f"{base_style}, {artistic_elements}, {composition}, {mood}"
            return (fallback_prompt, "Basic style (error fallback)", "No analysis (error)", error_info)
    
    def _build_style_context(self, base_style: str, elements: str, composition: str,
                           mood: str, artists: str, palette: str,
                           technical: str, period: str) -> str:
        """Build comprehensive style context for LLM."""
        
        context_parts = [
            f"Primary style: {base_style}",
            f"Artistic elements: {elements}",
            f"Composition: {composition}",
            f"Mood/Atmosphere: {mood}"
        ]
        
        if artists.strip():
            context_parts.append(f"Reference artists: {artists}")
        
        if palette.strip():
            context_parts.append(f"Color palette: {palette}")
        
        if technical.strip():
            context_parts.append(f"Technical details: {technical}")
        
        if period.strip():
            context_parts.append(f"Historical period: {period}")
        
        return "\n".join(context_parts)
    
    def _analyze_style_with_llm(self, style_prompt: str, elements: str,
                              llm_framework) -> str:
        """Analyze artistic style using LLM."""
        
        try:
            analysis_prompt = f"Analyze this artistic style: {style_prompt}"
            analysis_context = f"Focus on these elements: {elements}"
            
            analysis, _ = llm_framework.enhance_prompt(
                base_prompt=analysis_prompt,
                enhancement_type="style_generation",
                context=analysis_context,
                additional_instructions="Provide detailed style analysis covering technical aspects, aesthetic qualities, and artistic merit."
            )
            
            return analysis
            
        except Exception as e:
            return f"Style analysis failed: {str(e)}"
    
    def _check_style_coherence_with_llm(self, style_prompt: str, base_style: str,
                                      llm_framework) -> str:
        """Check style coherence using LLM."""
        
        try:
            coherence_prompt = f"Evaluate the coherence of this artistic style: {style_prompt}"
            coherence_context = f"Base style: {base_style}"
            
            coherence, _ = llm_framework.enhance_prompt(
                base_prompt=coherence_prompt,
                enhancement_type="style_generation",
                context=coherence_context,
                additional_instructions="Check for style consistency, technical accuracy, and artistic coherence. Be concise."
            )
            
            return coherence[:200] + "..." if len(coherence) > 200 else coherence
            
        except Exception as e:
            return f"Coherence check failed: {str(e)}"
    
    def _build_template_style(self, base_style: str, elements: str, composition: str,
                            mood: str, artists: str, palette: str, technical: str) -> str:
        """Build style using templates as fallback."""
        
        parts = [base_style]
        
        if elements:
            parts.append(elements)
        
        if composition:
            parts.append(composition)
        
        if mood:
            parts.append(mood)
        
        if palette:
            parts.append(palette)
        
        if technical:
            parts.append(technical)
        
        if artists:
            parts.append(f"in the style of {artists}")
        
        return ", ".join(part.strip() for part in parts if part.strip())
    
    def _analyze_style_template(self, elements: str) -> str:
        """Template-based style analysis."""
        
        element_list = [e.strip() for e in elements.split(",") if e.strip()]
        
        analysis = f"Style Analysis:\n"
        analysis += f"• Primary elements: {', '.join(element_list[:3])}\n"
        
        if len(element_list) > 3:
            analysis += f"• Additional elements: {', '.join(element_list[3:])}\n"
        
        analysis += f"• Element count: {len(element_list)}\n"
        analysis += "• Analysis method: Template-based"
        
        return analysis