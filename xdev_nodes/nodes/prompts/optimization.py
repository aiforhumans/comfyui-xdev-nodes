"""
Advanced Prompt Optimization and Validation Suite for XDev Framework
Professional prompt analysis, optimization, and quality assurance tools
"""

import re
import math
import json
import statistics
from typing import Dict, List, Tuple, Any, Optional, Union, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin
from ...categories import NodeCategories

@dataclass
class PromptAnalysis:
    """Comprehensive prompt analysis results"""
    token_count: int
    word_count: int
    character_count: int
    complexity_score: float
    readability_score: float
    redundancy_score: float
    technical_terms: List[str]
    style_indicators: List[str]
    quality_metrics: Dict[str, float]
    suggestions: List[str]
    
class XDEV_PromptOptimizer(ValidationMixin):
    """
    Advanced prompt optimization with token efficiency, redundancy removal, and quality enhancement.
    Provides intelligent suggestions for improving prompt effectiveness.
    """
    
    DISPLAY_NAME = "Prompt Optimizer (XDev)"
    
    # Optimization strategies
    _OPTIMIZATION_MODES = {
        "token_efficiency": "Minimize token count while preserving meaning",
        "clarity": "Improve readability and structure",
        "redundancy_removal": "Remove duplicate and unnecessary terms",
        "quality_enhancement": "Add quality descriptors and improvements",
        "technical_focus": "Optimize for technical accuracy and specificity",
        "creative_focus": "Enhance artistic and creative elements",
        "balanced": "Balance all optimization factors"
    }
    
    # Common redundant patterns
    _REDUNDANT_PATTERNS = [
        (r'\\bhigh quality\\b.*\\bquality\\b', 'high quality'),
        (r'\\bdetailed\\b.*\\bhighly detailed\\b', 'highly detailed'),
        (r'\\bprofessional\\b.*\\bprofessional quality\\b', 'professional quality'),
        (r'\\brealistic\\b.*\\bphotorealistic\\b', 'photorealistic'),
        (r'\\bbeautiful\\b.*\\bstunning\\b', 'stunning'),
        (r'\\bvibrant\\b.*\\bvivid\\b', 'vivid'),
    ]
    
    # Quality enhancement terms by category
    _QUALITY_TERMS = {
        "technical": ["sharp focus", "perfect exposure", "color accurate", "noise-free", "professional grade"],
        "artistic": ["masterpiece", "award-winning", "gallery worthy", "artistic excellence", "creative vision"],
        "visual": ["stunning detail", "breathtaking", "visually striking", "compelling composition", "eye-catching"],
        "photography": ["professional photography", "studio lighting", "perfect composition", "bokeh", "depth of field"],
        "rendering": ["8k resolution", "ray tracing", "global illumination", "subsurface scattering", "physically accurate"]
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt to optimize"}),
                "optimization_mode": (list(cls._OPTIMIZATION_MODES.keys()), {"default": "balanced", "tooltip": "Optimization strategy"}),
                "target_tokens": ("INT", {"default": 75, "min": 10, "max": 200, "tooltip": "Target token count"}),
            },
            "optional": {
                "preserve_structure": ("BOOLEAN", {"default": True, "tooltip": "Maintain original prompt structure"}),
                "add_quality_terms": ("BOOLEAN", {"default": True, "tooltip": "Add quality enhancement terms"}),
                "remove_redundancy": ("BOOLEAN", {"default": True, "tooltip": "Remove redundant terms"}),
                "optimize_weights": ("BOOLEAN", {"default": True, "tooltip": "Optimize attention weights"}),
                "focus_category": (["auto", "technical", "artistic", "visual", "photography", "rendering"], {"default": "auto", "tooltip": "Focus optimization on category"}),
                "aggressiveness": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.1, "tooltip": "Optimization aggressiveness"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("optimized_prompt", "analysis_report", "optimization_log", "suggestions")
    FUNCTION = "optimize_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Advanced"
    DESCRIPTION = "Advanced prompt optimization with token efficiency and quality enhancement"
    
    @performance_monitor("prompt_optimization")
    @cached_operation(ttl=300)
    def optimize_prompt(self, input_prompt, optimization_mode, target_tokens,
                       preserve_structure=True, add_quality_terms=True, remove_redundancy=True,
                       optimize_weights=True, focus_category="auto", aggressiveness=0.5, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(input_prompt, "input_prompt")
            if not validation["valid"]:
                return ("", f"Error: {validation['error']}", "", "")
        
        try:
            # Analyze original prompt
            original_analysis = self._analyze_prompt(input_prompt)
            
            # Apply optimization based on mode
            optimized = input_prompt
            optimization_log = []
            
            if remove_redundancy:
                optimized, log = self._remove_redundancy(optimized, aggressiveness)
                optimization_log.extend(log)
            
            if optimize_weights:
                optimized, log = self._optimize_weights(optimized, aggressiveness)
                optimization_log.extend(log)
            
            # Apply mode-specific optimizations
            optimized, log = self._apply_mode_optimization(optimized, optimization_mode, aggressiveness)
            optimization_log.extend(log)
            
            # Add quality terms if requested
            if add_quality_terms:
                optimized, log = self._add_quality_terms(optimized, focus_category, aggressiveness)
                optimization_log.extend(log)
            
            # Token count optimization
            if len(optimized.split()) > target_tokens:
                optimized, log = self._optimize_token_count(optimized, target_tokens, preserve_structure)
                optimization_log.extend(log)
            
            # Analyze optimized prompt
            optimized_analysis = self._analyze_prompt(optimized)
            
            # Generate reports
            analysis_report = self._generate_analysis_report(original_analysis, optimized_analysis)
            optimization_report = "\\n".join(optimization_log)
            suggestions = self._generate_suggestions(optimized_analysis, target_tokens)
            
            return (optimized, analysis_report, optimization_report, suggestions)
            
        except Exception as e:
            return ("", f"Error: {str(e)}", "", "")
    
    def _analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """Comprehensive prompt analysis"""
        words = prompt.split()
        word_count = len(words)
        char_count = len(prompt)
        token_count = self._estimate_tokens(prompt)
        
        # Calculate complexity (based on unique words, technical terms, etc.)
        unique_words = len(set(word.lower().strip('.,!?()[]') for word in words))
        complexity_score = unique_words / max(word_count, 1)
        
        # Calculate readability (simple metric based on sentence length and word complexity)
        sentences = len(re.split(r'[.!?]+', prompt))
        avg_sentence_length = word_count / max(sentences, 1)
        readability_score = max(0, 1 - (avg_sentence_length - 10) / 20)
        
        # Calculate redundancy
        word_counts = Counter(word.lower().strip('.,!?()[]') for word in words)
        repeated_words = sum(count - 1 for count in word_counts.values() if count > 1)
        redundancy_score = repeated_words / max(word_count, 1)
        
        # Identify technical and style terms
        technical_terms = self._identify_technical_terms(words)
        style_indicators = self._identify_style_indicators(words)
        
        # Quality metrics
        quality_metrics = {
            "specificity": self._calculate_specificity(words),
            "balance": self._calculate_balance(prompt),
            "coherence": self._calculate_coherence(prompt)
        }
        
        suggestions = self._generate_optimization_suggestions(
            token_count, complexity_score, redundancy_score, quality_metrics
        )
        
        return PromptAnalysis(
            token_count=token_count,
            word_count=word_count,
            character_count=char_count,
            complexity_score=complexity_score,
            readability_score=readability_score,
            redundancy_score=redundancy_score,
            technical_terms=technical_terms,
            style_indicators=style_indicators,
            quality_metrics=quality_metrics,
            suggestions=suggestions
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (simplified)"""
        # Rough estimation: average word is ~1.3 tokens
        words = len(text.split())
        punctuation_bonus = len(re.findall(r'[.,!?()[\]:;]', text)) * 0.2
        return int(words * 1.3 + punctuation_bonus)
    
    def _remove_redundancy(self, prompt: str, aggressiveness: float) -> Tuple[str, List[str]]:
        """Remove redundant terms and phrases"""
        log = []
        optimized = prompt
        
        # Apply redundancy patterns
        for pattern, replacement in self._REDUNDANT_PATTERNS:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                log.append(f"Removed redundancy: {pattern} → {replacement}")
        
        # Remove duplicate words (aggressive mode)
        if aggressiveness > 0.7:
            words = optimized.split()
            seen = set()
            filtered_words = []
            for word in words:
                clean_word = word.lower().strip('.,!?()[]')
                if clean_word not in seen or len(clean_word) <= 3:
                    filtered_words.append(word)
                    seen.add(clean_word)
                else:
                    log.append(f"Removed duplicate word: {word}")
            optimized = " ".join(filtered_words)
        
        return optimized, log
    
    def _optimize_weights(self, prompt: str, aggressiveness: float) -> Tuple[str, List[str]]:
        """Optimize attention weights"""
        log = []
        
        # Find existing weights
        weight_pattern = r'\\(([^)]+):(\\d*\\.?\\d+)\\)'
        weights = re.findall(weight_pattern, prompt)
        
        if weights and aggressiveness > 0.5:
            optimized = prompt
            for term, weight in weights:
                old_weight = float(weight)
                # Optimize weight based on term importance
                if any(keyword in term.lower() for keyword in ['quality', 'detailed', 'professional']):
                    new_weight = min(1.5, old_weight * 1.2)
                elif any(keyword in term.lower() for keyword in ['background', 'minor', 'subtle']):
                    new_weight = max(0.5, old_weight * 0.8)
                else:
                    new_weight = old_weight
                
                if abs(new_weight - old_weight) > 0.1:
                    optimized = optimized.replace(f"({term}:{weight})", f"({term}:{new_weight:.1f})")
                    log.append(f"Adjusted weight: {term} {old_weight} → {new_weight:.1f}")
            
            return optimized, log
        
        return prompt, log
    
    def _apply_mode_optimization(self, prompt: str, mode: str, aggressiveness: float) -> Tuple[str, List[str]]:
        """Apply mode-specific optimizations"""
        log = []
        optimized = prompt
        
        if mode == "token_efficiency":
            # Replace verbose phrases with concise alternatives
            replacements = {
                "high quality": "HQ",
                "extremely detailed": "detailed",
                "professional quality": "professional",
                "beautiful and": "",
                "very ": ""
            }
            
            for verbose, concise in replacements.items():
                if verbose in optimized.lower():
                    optimized = re.sub(verbose, concise, optimized, flags=re.IGNORECASE)
                    log.append(f"Shortened: '{verbose}' → '{concise}'")
        
        elif mode == "clarity":
            # Improve structure and readability
            # Add commas for better parsing
            optimized = re.sub(r'(\\w+)\\s+(\\w+ing)', r'\\1, \\2', optimized)
            log.append("Improved punctuation for clarity")
        
        elif mode == "technical_focus":
            # Emphasize technical terms
            tech_terms = ["sharp focus", "professional", "technical", "precise", "accurate"]
            for term in tech_terms:
                if term in optimized.lower() and f"({term}" not in optimized:
                    optimized = optimized.replace(term, f"({term}:1.2)")
                    log.append(f"Enhanced technical term: {term}")
        
        return optimized, log
    
    def _add_quality_terms(self, prompt: str, category: str, aggressiveness: float) -> Tuple[str, List[str]]:
        """Add quality enhancement terms"""
        log = []
        
        if aggressiveness < 0.3:
            return prompt, log
        
        # Detect category if auto
        if category == "auto":
            category = self._detect_category(prompt)
        
        # Add appropriate quality terms
        if category in self._QUALITY_TERMS:
            available_terms = self._QUALITY_TERMS[category]
            terms_to_add = available_terms[:int(aggressiveness * 3)]
            
            for term in terms_to_add:
                if term.lower() not in prompt.lower():
                    prompt += f", {term}"
                    log.append(f"Added quality term: {term}")
        
        return prompt, log
    
    def _detect_category(self, prompt: str) -> str:
        """Detect prompt category for targeted optimization"""
        prompt_lower = prompt.lower()
        
        photo_keywords = ["photograph", "photo", "camera", "lens", "aperture", "iso"]
        art_keywords = ["painting", "drawing", "artwork", "style", "artistic", "creative"]
        tech_keywords = ["render", "3d", "cgi", "ray", "lighting", "technical"]
        
        if any(keyword in prompt_lower for keyword in photo_keywords):
            return "photography"
        elif any(keyword in prompt_lower for keyword in tech_keywords):
            return "rendering"
        elif any(keyword in prompt_lower for keyword in art_keywords):
            return "artistic"
        else:
            return "visual"
    
    def _optimize_token_count(self, prompt: str, target: int, preserve_structure: bool) -> Tuple[str, List[str]]:
        """Optimize to target token count"""
        log = []
        current_tokens = self._estimate_tokens(prompt)
        
        if current_tokens <= target:
            return prompt, log
        
        words = prompt.split()
        reduction_needed = current_tokens - target
        
        if preserve_structure:
            # Remove less important words while preserving structure
            stop_words = ["a", "an", "the", "and", "or", "but", "very", "quite", "rather"]
            filtered_words = [word for word in words if word.lower() not in stop_words]
            
            if len(filtered_words) < len(words):
                log.append(f"Removed {len(words) - len(filtered_words)} stop words")
                return " ".join(filtered_words), log
        
        # More aggressive reduction
        words = words[:int(len(words) * (target / current_tokens))]
        log.append(f"Truncated to {len(words)} words to meet token target")
        
        return " ".join(words), log
    
    def _identify_technical_terms(self, words: List[str]) -> List[str]:
        """Identify technical photography/art terms"""
        technical_keywords = {
            "aperture", "iso", "shutter", "focal", "bokeh", "dof", "f/", "mm",
            "render", "ray", "lighting", "shader", "texture", "polygon",
            "composition", "exposure", "contrast", "saturation", "hue"
        }
        
        return [word for word in words if word.lower() in technical_keywords]
    
    def _identify_style_indicators(self, words: List[str]) -> List[str]:
        """Identify artistic style indicators"""
        style_keywords = {
            "realistic", "abstract", "surreal", "minimalist", "baroque", "gothic",
            "impressionist", "cubist", "art nouveau", "pop art", "digital art",
            "oil painting", "watercolor", "sketch", "photograph", "cinematic"
        }
        
        return [word for word in words if word.lower() in style_keywords]
    
    def _calculate_specificity(self, words: List[str]) -> float:
        """Calculate prompt specificity score"""
        specific_terms = sum(1 for word in words if len(word) > 6)
        return specific_terms / max(len(words), 1)
    
    def _calculate_balance(self, prompt: str) -> float:
        """Calculate balance between different prompt elements"""
        # Simple heuristic: balance of subjects, styles, and quality terms
        subjects = len(re.findall(r'\\b(person|man|woman|character|figure)\\b', prompt, re.IGNORECASE))
        styles = len(re.findall(r'\\b(style|artistic|creative)\\b', prompt, re.IGNORECASE))
        quality = len(re.findall(r'\\b(quality|detailed|professional)\\b', prompt, re.IGNORECASE))
        
        total = subjects + styles + quality
        if total == 0:
            return 0.5
        
        balance_score = 1 - abs(subjects - styles) / total - abs(styles - quality) / total
        return max(0, balance_score)
    
    def _calculate_coherence(self, prompt: str) -> float:
        """Calculate prompt coherence score"""
        # Simple coherence based on sentence structure and flow
        sentences = re.split(r'[.!?]+', prompt)
        if len(sentences) <= 1:
            return 0.8  # Single sentence, likely coherent
        
        # Check for transition words and logical flow
        transition_words = ["with", "featuring", "in", "under", "during", "while"]
        transitions = sum(1 for word in transition_words if word in prompt.lower())
        
        return min(1.0, 0.5 + (transitions / len(sentences)))
    
    def _generate_optimization_suggestions(self, tokens: int, complexity: float, 
                                        redundancy: float, quality_metrics: Dict[str, float]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if tokens > 75:
            suggestions.append("Consider reducing token count for better efficiency")
        if tokens < 20:
            suggestions.append("Consider adding more descriptive elements")
        
        if complexity < 0.3:
            suggestions.append("Add more specific and varied terms")
        if complexity > 0.8:
            suggestions.append("Simplify complex terminology for better results")
        
        if redundancy > 0.2:
            suggestions.append("Remove redundant and repeated terms")
        
        if quality_metrics["specificity"] < 0.3:
            suggestions.append("Add more specific descriptive terms")
        if quality_metrics["balance"] < 0.4:
            suggestions.append("Balance different prompt elements better")
        if quality_metrics["coherence"] < 0.5:
            suggestions.append("Improve logical flow and structure")
        
        return suggestions
    
    def _generate_analysis_report(self, original: PromptAnalysis, optimized: PromptAnalysis) -> str:
        """Generate comprehensive analysis report"""
        report = f"ORIGINAL ANALYSIS:\\n"
        report += f"Tokens: {original.token_count}, Words: {original.word_count}, Characters: {original.character_count}\\n"
        report += f"Complexity: {original.complexity_score:.2f}, Readability: {original.readability_score:.2f}\\n"
        report += f"Redundancy: {original.redundancy_score:.2f}\\n\\n"
        
        report += f"OPTIMIZED ANALYSIS:\\n"
        report += f"Tokens: {optimized.token_count}, Words: {optimized.word_count}, Characters: {optimized.character_count}\\n"
        report += f"Complexity: {optimized.complexity_score:.2f}, Readability: {optimized.readability_score:.2f}\\n"
        report += f"Redundancy: {optimized.redundancy_score:.2f}\\n\\n"
        
        report += f"IMPROVEMENTS:\\n"
        token_change = optimized.token_count - original.token_count
        report += f"Token change: {token_change:+d} ({token_change/max(original.token_count, 1)*100:+.1f}%)\\n"
        
        redundancy_change = optimized.redundancy_score - original.redundancy_score
        report += f"Redundancy change: {redundancy_change:+.2f}\\n"
        
        if optimized.suggestions:
            report += f"\\nSUGGESTIONS:\\n" + "\\n".join(f"• {s}" for s in optimized.suggestions[:5])
        
        return report


class XDEV_PromptValidator(ValidationMixin):
    """
    Comprehensive prompt validation with quality scoring and compatibility checking.
    Validates prompts against best practices and common issues.
    """
    
    DISPLAY_NAME = "Prompt Validator (XDev)"
    
    # Validation rules and their weights
    _VALIDATION_RULES = {
        "token_count": {"min": 5, "max": 150, "weight": 0.2, "description": "Appropriate token count"},
        "redundancy": {"max": 0.3, "weight": 0.15, "description": "Low redundancy"},
        "specificity": {"min": 0.2, "weight": 0.15, "description": "Sufficient specificity"},
        "balance": {"min": 0.3, "weight": 0.1, "description": "Balanced elements"},
        "coherence": {"min": 0.4, "weight": 0.1, "description": "Logical coherence"},
        "quality_terms": {"min": 1, "weight": 0.1, "description": "Quality descriptors present"},
        "technical_accuracy": {"weight": 0.1, "description": "Technical accuracy"},
        "style_consistency": {"weight": 0.1, "description": "Consistent style"}
    }
    
    # Common issues and their patterns
    _COMMON_ISSUES = {
        "redundant_quality": r"\\b(high quality|quality|detailed)\\b.*\\b(high quality|quality|detailed)\\b",
        "excessive_adjectives": r"\\b(very|extremely|incredibly|amazingly|absolutely)\\b",
        "conflicting_styles": r"\\b(realistic|photorealistic)\\b.*\\b(cartoon|anime|abstract)\\b",
        "vague_terms": r"\\b(nice|good|cool|awesome|amazing)\\b",
        "excessive_weights": r"\\([^)]+:[2-9]\\d*\\.?\\d*\\)",
        "incomplete_technical": r"\\b(f/)\\b(?!\\d+)",
        "mixed_mediums": r"\\b(photograph|photo)\\b.*\\b(painting|drawing|artwork)\\b"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "prompt_to_validate": ("STRING", {"default": "", "multiline": True, "tooltip": "Prompt to validate and score"}),
                "validation_mode": (["comprehensive", "basic", "technical", "artistic"], {"default": "comprehensive", "tooltip": "Validation depth"}),
            },
            "optional": {
                "target_use": (["general", "photography", "art", "character", "environment", "technical"], {"default": "general", "tooltip": "Intended use case"}),
                "quality_threshold": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 1.0, "step": 0.1, "tooltip": "Quality score threshold"}),
                "check_compatibility": ("BOOLEAN", {"default": True, "tooltip": "Check model compatibility"}),
                "suggest_improvements": ("BOOLEAN", {"default": True, "tooltip": "Provide improvement suggestions"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("FLOAT", "STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("quality_score", "validation_report", "issues_found", "passes_validation")
    FUNCTION = "validate_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Advanced"
    DESCRIPTION = "Comprehensive prompt validation with quality scoring and issue detection"
    
    @performance_monitor("prompt_validation")
    @cached_operation(ttl=300)
    def validate_prompt(self, prompt_to_validate, validation_mode, target_use="general",
                       quality_threshold=0.7, check_compatibility=True, suggest_improvements=True, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(prompt_to_validate, "prompt_to_validate")
            if not validation["valid"]:
                return (0.0, f"Error: {validation['error']}", "", False)
        
        try:
            # Run comprehensive analysis
            analysis = self._analyze_prompt_quality(prompt_to_validate, target_use)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(analysis, validation_mode)
            
            # Detect issues
            issues = self._detect_issues(prompt_to_validate, target_use)
            
            # Check compatibility if requested
            compatibility_issues = []
            if check_compatibility:
                compatibility_issues = self._check_compatibility(prompt_to_validate, target_use)
            
            # Generate validation report
            report = self._generate_validation_report(analysis, quality_score, validation_mode)
            
            # Compile issues
            all_issues = issues + compatibility_issues
            issues_text = "\\n".join(f"• {issue}" for issue in all_issues) if all_issues else "No issues detected"
            
            # Add suggestions if requested
            if suggest_improvements and quality_score < quality_threshold:
                suggestions = self._generate_improvement_suggestions(analysis, issues, target_use)
                issues_text += f"\\n\\nSUGGESTIONS:\\n" + "\\n".join(f"→ {s}" for s in suggestions)
            
            passes = quality_score >= quality_threshold and len(issues) == 0
            
            return (quality_score, report, issues_text, passes)
            
        except Exception as e:
            return (0.0, f"Error: {str(e)}", "", False)
    
    def _analyze_prompt_quality(self, prompt: str, target_use: str) -> Dict[str, Any]:
        """Analyze prompt quality metrics"""
        words = prompt.split()
        word_count = len(words)
        token_count = len(prompt.split()) * 1.3  # Rough estimate
        
        # Calculate various metrics
        analysis = {
            "token_count": token_count,
            "word_count": word_count,
            "character_count": len(prompt),
            "unique_words": len(set(word.lower().strip('.,!?()[]') for word in words)),
            "redundancy": self._calculate_redundancy(words),
            "specificity": self._calculate_specificity(words),
            "balance": self._calculate_balance(prompt),
            "coherence": self._calculate_coherence(prompt),
            "quality_terms": self._count_quality_terms(prompt),
            "technical_terms": len(self._identify_technical_terms(words)),
            "style_consistency": self._check_style_consistency(prompt),
            "target_alignment": self._check_target_alignment(prompt, target_use)
        }
        
        return analysis
    
    def _calculate_quality_score(self, analysis: Dict[str, Any], mode: str) -> float:
        """Calculate overall quality score"""
        score = 0.0
        max_score = 0.0
        
        for rule_name, rule_config in self._VALIDATION_RULES.items():
            weight = rule_config["weight"]
            max_score += weight
            
            if mode == "basic" and weight < 0.15:
                continue  # Skip minor rules in basic mode
            
            # Score each rule
            rule_score = self._score_rule(rule_name, analysis, rule_config)
            score += rule_score * weight
        
        return min(1.0, score / max_score)
    
    def _score_rule(self, rule_name: str, analysis: Dict[str, Any], rule_config: Dict[str, Any]) -> float:
        """Score individual validation rule"""
        value = analysis.get(rule_name, 0)
        
        if "min" in rule_config and "max" in rule_config:
            # Range rule
            min_val, max_val = rule_config["min"], rule_config["max"]
            if min_val <= value <= max_val:
                return 1.0
            elif value < min_val:
                return max(0.0, value / min_val)
            else:
                return max(0.0, 1.0 - (value - max_val) / max_val)
        
        elif "min" in rule_config:
            # Minimum rule
            min_val = rule_config["min"]
            return min(1.0, max(0.0, value / min_val))
        
        elif "max" in rule_config:
            # Maximum rule
            max_val = rule_config["max"]
            return 1.0 if value <= max_val else max(0.0, 1.0 - (value - max_val) / max_val)
        
        else:
            # Custom scoring for complex rules
            if rule_name == "technical_accuracy":
                return self._score_technical_accuracy(analysis)
            elif rule_name == "style_consistency":
                return analysis.get("style_consistency", 0.5)
            
        return 0.5  # Default neutral score
    
    def _detect_issues(self, prompt: str, target_use: str) -> List[str]:
        """Detect common prompt issues"""
        issues = []
        
        for issue_name, pattern in self._COMMON_ISSUES.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                issue_descriptions = {
                    "redundant_quality": "Redundant quality descriptors detected",
                    "excessive_adjectives": "Excessive use of intensifying adjectives",
                    "conflicting_styles": "Conflicting style descriptors",
                    "vague_terms": "Vague or non-specific terms",
                    "excessive_weights": "Potentially excessive attention weights",
                    "incomplete_technical": "Incomplete technical specifications",
                    "mixed_mediums": "Mixed medium descriptors may cause confusion"
                }
                issues.append(issue_descriptions.get(issue_name, f"Issue detected: {issue_name}"))
        
        # Additional context-specific checks
        if target_use == "photography" and "painting" in prompt.lower():
            issues.append("Photography target but contains painting references")
        
        if target_use == "technical" and len(self._identify_technical_terms(prompt.split())) < 2:
            issues.append("Technical target but lacks sufficient technical terms")
        
        return issues
    
    def _check_compatibility(self, prompt: str, target_use: str) -> List[str]:
        """Check compatibility with common models and use cases"""
        compatibility_issues = []
        
        # Check token count for different models
        estimated_tokens = len(prompt.split()) * 1.3
        if estimated_tokens > 75:
            compatibility_issues.append("High token count may exceed some model limits")
        
        # Check for problematic combinations
        if "nsfw" in prompt.lower() or "nude" in prompt.lower():
            compatibility_issues.append("NSFW content may be rejected by some models")
        
        # Check for weight syntax issues
        weight_matches = re.findall(r'\\([^)]+:(\\d*\\.?\\d+)\\)', prompt)
        for term, weight in weight_matches:
            try:
                weight_val = float(weight)
                if weight_val > 2.0:
                    compatibility_issues.append(f"Very high weight ({weight_val}) may cause instability")
                elif weight_val < 0.1:
                    compatibility_issues.append(f"Very low weight ({weight_val}) may be ineffective")
            except ValueError:
                compatibility_issues.append(f"Invalid weight format: {weight}")
        
        return compatibility_issues
    
    def _generate_improvement_suggestions(self, analysis: Dict[str, Any], issues: List[str], target_use: str) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if analysis["redundancy"] > 0.3:
            suggestions.append("Remove redundant terms and consolidate similar concepts")
        
        if analysis["specificity"] < 0.2:
            suggestions.append("Add more specific descriptive terms")
        
        if analysis["quality_terms"] < 1:
            suggestions.append("Include quality descriptors like 'high quality', 'detailed', or 'professional'")
        
        if analysis["token_count"] > 100:
            suggestions.append("Consider reducing prompt length for better performance")
        
        if analysis["technical_terms"] < 1 and target_use in ["photography", "technical"]:
            suggestions.append("Add technical terms relevant to your use case")
        
        if analysis["balance"] < 0.3:
            suggestions.append("Balance different elements (subject, style, quality, technical)")
        
        return suggestions
    
    def _generate_validation_report(self, analysis: Dict[str, Any], quality_score: float, mode: str) -> str:
        """Generate comprehensive validation report"""
        report = f"PROMPT VALIDATION REPORT ({mode.upper()} MODE)\\n"
        report += f"{'='*50}\\n\\n"
        
        report += f"OVERALL QUALITY SCORE: {quality_score:.2f}/1.00\\n\\n"
        
        report += f"METRICS:\\n"
        report += f"• Token Count: {analysis['token_count']:.0f}\\n"
        report += f"• Word Count: {analysis['word_count']}\\n"
        report += f"• Unique Words: {analysis['unique_words']}\\n"
        report += f"• Redundancy: {analysis['redundancy']:.2f}\\n"
        report += f"• Specificity: {analysis['specificity']:.2f}\\n"
        report += f"• Balance: {analysis['balance']:.2f}\\n"
        report += f"• Coherence: {analysis['coherence']:.2f}\\n"
        report += f"• Quality Terms: {analysis['quality_terms']}\\n"
        report += f"• Technical Terms: {analysis['technical_terms']}\\n\\n"
        
        # Grade the prompt
        if quality_score >= 0.9:
            grade = "EXCELLENT"
        elif quality_score >= 0.8:
            grade = "VERY GOOD"
        elif quality_score >= 0.7:
            grade = "GOOD"
        elif quality_score >= 0.6:
            grade = "FAIR"
        elif quality_score >= 0.5:
            grade = "NEEDS IMPROVEMENT"
        else:
            grade = "POOR"
        
        report += f"GRADE: {grade}\\n"
        
        return report
    
    def _calculate_redundancy(self, words: List[str]) -> float:
        """Calculate redundancy score"""
        word_counts = Counter(word.lower().strip('.,!?()[]') for word in words)
        repeated_words = sum(count - 1 for count in word_counts.values() if count > 1)
        return repeated_words / max(len(words), 1)
    
    def _calculate_specificity(self, words: List[str]) -> float:
        """Calculate specificity score"""
        specific_terms = sum(1 for word in words if len(word) > 6)
        return specific_terms / max(len(words), 1)
    
    def _calculate_balance(self, prompt: str) -> float:
        """Calculate balance score"""
        subjects = len(re.findall(r'\\b(person|man|woman|character|figure|object)\\b', prompt, re.IGNORECASE))
        styles = len(re.findall(r'\\b(style|artistic|creative|painted|drawn)\\b', prompt, re.IGNORECASE))
        quality = len(re.findall(r'\\b(quality|detailed|professional|masterpiece)\\b', prompt, re.IGNORECASE))
        
        total = subjects + styles + quality
        if total == 0:
            return 0.3
        
        # Balance is better when elements are more evenly distributed
        variance = statistics.variance([subjects, styles, quality]) if total > 0 else 0
        return max(0, 1 - variance / (total * total))
    
    def _calculate_coherence(self, prompt: str) -> float:
        """Calculate coherence score"""
        sentences = re.split(r'[.!?]+', prompt)
        if len(sentences) <= 1:
            return 0.8
        
        transition_words = ["with", "featuring", "in", "under", "during", "while", "showing", "depicting"]
        transitions = sum(1 for word in transition_words if word in prompt.lower())
        
        return min(1.0, 0.4 + (transitions / len(sentences)))
    
    def _count_quality_terms(self, prompt: str) -> int:
        """Count quality enhancement terms"""
        quality_terms = [
            "quality", "detailed", "professional", "masterpiece", "award", "stunning",
            "beautiful", "perfect", "excellent", "premium", "fine", "superior"
        ]
        return sum(1 for term in quality_terms if term in prompt.lower())
    
    def _identify_technical_terms(self, words: List[str]) -> List[str]:
        """Identify technical terms"""
        technical_keywords = {
            "aperture", "iso", "shutter", "focal", "bokeh", "dof", "f/", "mm",
            "render", "ray", "lighting", "shader", "texture", "polygon", "wireframe",
            "composition", "exposure", "contrast", "saturation", "hue", "gamma",
            "resolution", "megapixel", "macro", "telephoto", "wide-angle"
        }
        
        return [word for word in words if word.lower() in technical_keywords]
    
    def _check_style_consistency(self, prompt: str) -> float:
        """Check style consistency"""
        realistic_terms = ["realistic", "photorealistic", "photograph", "photo"]
        artistic_terms = ["painting", "drawing", "artwork", "sketch", "illustration"]
        
        realistic_count = sum(1 for term in realistic_terms if term in prompt.lower())
        artistic_count = sum(1 for term in artistic_terms if term in prompt.lower())
        
        if realistic_count > 0 and artistic_count > 0:
            return 0.3  # Conflicting styles
        elif realistic_count > 0 or artistic_count > 0:
            return 0.8  # Consistent style
        else:
            return 0.6  # Neutral/unclear style
    
    def _check_target_alignment(self, prompt: str, target_use: str) -> float:
        """Check alignment with target use case"""
        alignment_keywords = {
            "photography": ["photo", "camera", "lens", "shot", "portrait", "landscape"],
            "art": ["painting", "drawing", "artistic", "creative", "canvas", "brush"],
            "character": ["person", "character", "figure", "portrait", "face", "expression"],
            "environment": ["landscape", "scene", "environment", "background", "setting"],
            "technical": ["render", "3d", "technical", "precise", "accurate", "specification"]
        }
        
        if target_use in alignment_keywords:
            keywords = alignment_keywords[target_use]
            matches = sum(1 for keyword in keywords if keyword in prompt.lower())
            return min(1.0, matches / len(keywords))
        
        return 0.5  # Neutral for general use
    
    def _score_technical_accuracy(self, analysis: Dict[str, Any]) -> float:
        """Score technical accuracy"""
        # Simple heuristic based on technical terms and specificity
        tech_score = min(1.0, analysis["technical_terms"] / 3)
        specificity_score = analysis["specificity"]
        
        return (tech_score + specificity_score) / 2


# Node registrations
NODE_CLASS_MAPPINGS = {
    "XDEV_PromptOptimizer": XDEV_PromptOptimizer,
    "XDEV_PromptValidator": XDEV_PromptValidator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_PromptOptimizer": "Prompt Optimizer (XDev)",
    "XDEV_PromptValidator": "Prompt Validator (XDev)",
}