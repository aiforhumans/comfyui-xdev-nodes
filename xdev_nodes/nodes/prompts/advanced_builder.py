"""
Advanced Modular Prompt Building Tools for XDev Framework
Professional prompt engineering with template system, composition tools, and optimization
"""

import re
import json
import random
from typing import Dict, List, Tuple, Any, Optional, Union, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin
from ...categories import NodeCategories

# Advanced Template System
@dataclass
class PromptTemplate:
    """Advanced prompt template with variables, conditions, and inheritance"""
    name: str
    content: str
    variables: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent: Optional[str] = None
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render template with context variables"""
        rendered = self.content
        
        # Apply variable substitution
        for var, default in self.variables.items():
            value = context.get(var, default)
            rendered = rendered.replace(f"{{{var}}}", str(value))
        
        # Apply conditional logic
        for condition, replacement in self.conditions.items():
            if self._evaluate_condition(condition, context):
                rendered = rendered.replace(f"{{?{condition}}}", replacement)
            else:
                rendered = re.sub(f"\\{{\\?{re.escape(condition)}\\}}.*?\\{{\\/{re.escape(condition)}\\}}", "", rendered)
        
        return rendered.strip()
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate simple conditional logic"""
        # Simple condition parsing: var==value, var!=value, var
        if "==" in condition:
            var, val = condition.split("==", 1)
            return str(context.get(var.strip(), "")) == val.strip()
        elif "!=" in condition:
            var, val = condition.split("!=", 1)
            return str(context.get(var.strip(), "")) != val.strip()
        else:
            return bool(context.get(condition.strip(), False))

class XDEV_PromptTemplateEngine(ValidationMixin):
    """
    Advanced modular prompt template system with inheritance, variables, and conditional logic.
    Supports template composition, reusable components, and dynamic content generation.
    """
    
    DISPLAY_NAME = "Prompt Template Engine (XDev)"
    
    # Built-in template library
    _BUILTIN_TEMPLATES = {
        "photography": {
            "content": "A {style} photograph of {subject}, {lighting} lighting, {composition}, {quality}",
            "variables": {"style": "professional", "subject": "", "lighting": "natural", "composition": "centered", "quality": "high quality, detailed"},
            "metadata": {"category": "photography", "complexity": "medium"}
        },
        "character": {
            "content": "{age} {gender} {ethnicity} {appearance}, {clothing}, {expression}, {pose}",
            "variables": {"age": "young adult", "gender": "", "ethnicity": "", "appearance": "", "clothing": "casual clothes", "expression": "friendly smile", "pose": "standing"},
            "metadata": {"category": "character", "complexity": "high"}
        },
        "environment": {
            "content": "{location} scene, {time_of_day}, {weather}, {atmosphere}, {details}",
            "variables": {"location": "", "time_of_day": "daytime", "weather": "clear", "atmosphere": "peaceful", "details": "highly detailed"},
            "metadata": {"category": "environment", "complexity": "medium"}
        },
        "artistic": {
            "content": "In the style of {artist}, {medium}, {technique}, {color_palette}, {mood}",
            "variables": {"artist": "", "medium": "digital art", "technique": "", "color_palette": "vibrant colors", "mood": "inspiring"},
            "metadata": {"category": "artistic", "complexity": "high"}
        },
        "technical": {
            "content": "{camera} shot, {lens}, {aperture}, {focal_length}, {iso}, {shutter_speed}",
            "variables": {"camera": "DSLR", "lens": "50mm", "aperture": "f/2.8", "focal_length": "medium", "iso": "100", "shutter_speed": "1/125s"},
            "metadata": {"category": "technical", "complexity": "expert"}
        }
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "template_name": (list(cls._BUILTIN_TEMPLATES.keys()) + ["custom"], {"default": "photography", "tooltip": "Select built-in template or use custom"}),
                "custom_template": ("STRING", {"default": "", "multiline": True, "tooltip": "Custom template with {variables} and {?conditions}"}),
            },
            "optional": {
                "variables_json": ("STRING", {"default": "{}", "multiline": True, "tooltip": "JSON object with variable values"}),
                "style": ("STRING", {"default": "", "tooltip": "Style variable"}),
                "subject": ("STRING", {"default": "", "tooltip": "Subject variable"}),
                "quality": ("STRING", {"default": "high quality, detailed", "tooltip": "Quality descriptors"}),
                "lighting": ("STRING", {"default": "natural", "tooltip": "Lighting conditions"}),
                "composition": ("STRING", {"default": "centered", "tooltip": "Composition style"}),
                "mood": ("STRING", {"default": "", "tooltip": "Mood/atmosphere"}),
                "artist": ("STRING", {"default": "", "tooltip": "Artist reference"}),
                "medium": ("STRING", {"default": "digital art", "tooltip": "Art medium"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("rendered_prompt", "template_info", "variable_report")
    FUNCTION = "build_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Advanced"
    DESCRIPTION = "Advanced modular prompt template system with variables, conditions, and inheritance"
    
    @performance_monitor("template_render")
    @cached_operation(ttl=300)
    def build_prompt(self, template_name, custom_template, variables_json="{}", 
                    style="", subject="", quality="high quality, detailed", 
                    lighting="natural", composition="centered", mood="", 
                    artist="", medium="digital art", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(custom_template if template_name == "custom" else template_name, "template")
            if not validation["valid"]:
                return ("", f"Error: {validation['error']}", "")
        
        try:
            # Parse variables from JSON
            variables = {}
            if variables_json.strip():
                variables = json.loads(variables_json)
            
            # Add direct variables
            direct_vars = {
                "style": style, "subject": subject, "quality": quality,
                "lighting": lighting, "composition": composition, "mood": mood,
                "artist": artist, "medium": medium
            }
            variables.update({k: v for k, v in direct_vars.items() if v})
            
            # Get template
            if template_name == "custom":
                template = PromptTemplate("custom", custom_template, variables)
            else:
                template_data = self._BUILTIN_TEMPLATES[template_name]
                template = PromptTemplate(
                    name=template_name,
                    content=template_data["content"],
                    variables=template_data["variables"],
                    metadata=template_data.get("metadata", {})
                )
            
            # Render prompt
            rendered = template.render(variables)
            
            # Generate reports
            template_info = f"Template: {template.name}\\nCategory: {template.metadata.get('category', 'custom')}\\nComplexity: {template.metadata.get('complexity', 'unknown')}"
            
            used_vars = [f"{k}: {v}" for k, v in variables.items() if v]
            variable_report = f"Variables used: {len(used_vars)}\\n" + "\\n".join(used_vars)
            
            return (rendered, template_info, variable_report)
            
        except json.JSONDecodeError:
            return ("", "Error: Invalid JSON in variables", "")
        except Exception as e:
            return ("", f"Error: {str(e)}", "")

class XDEV_PromptComposer(ValidationMixin):
    """
    Intelligent prompt composition with AI-assisted generation and smart suggestions.
    Combines multiple elements into cohesive, optimized prompts.
    """
    
    DISPLAY_NAME = "Smart Prompt Composer (XDev)"
    
    # Composition strategies
    _COMPOSITION_MODES = {
        "layered": "Build prompt in logical layers (subject → style → technical)",
        "weighted": "Combine elements with importance weights",
        "hierarchical": "Organize by priority and detail level",
        "narrative": "Create narrative flow between elements",
        "technical": "Focus on technical photography/art parameters",
        "artistic": "Emphasize artistic and creative elements"
    }
    
    # Quality enhancement presets
    _QUALITY_PRESETS = {
        "ultra_high": "8k uhd, highly detailed, professional quality, masterpiece, award winning",
        "photorealistic": "photorealistic, hyperrealistic, sharp focus, professional photography",
        "artistic": "artistic masterpiece, creative composition, stunning visual",
        "cinematic": "cinematic lighting, dramatic composition, film quality",
        "technical": "sharp focus, perfect exposure, color accurate, noise-free",
        "custom": ""
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "main_subject": ("STRING", {"default": "", "multiline": True, "tooltip": "Primary subject or scene"}),
                "composition_mode": (list(cls._COMPOSITION_MODES.keys()), {"default": "layered", "tooltip": "How to compose the prompt"}),
                "quality_preset": (list(cls._QUALITY_PRESETS.keys()), {"default": "ultra_high", "tooltip": "Quality enhancement preset"}),
            },
            "optional": {
                "style_elements": ("STRING", {"default": "", "multiline": True, "tooltip": "Style and artistic elements"}),
                "technical_details": ("STRING", {"default": "", "multiline": True, "tooltip": "Technical photography/rendering details"}),
                "lighting_atmosphere": ("STRING", {"default": "", "multiline": True, "tooltip": "Lighting and atmospheric elements"}),
                "negative_prompts": ("STRING", {"default": "", "multiline": True, "tooltip": "Elements to exclude"}),
                "custom_quality": ("STRING", {"default": "", "tooltip": "Custom quality descriptors"}),
                "weight_subject": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Subject importance weight"}),
                "weight_style": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Style importance weight"}),
                "weight_technical": ("FLOAT", {"default": 0.6, "min": 0.1, "max": 2.0, "step": 0.1, "tooltip": "Technical importance weight"}),
                "optimize_tokens": ("BOOLEAN", {"default": True, "tooltip": "Optimize for token efficiency"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("composed_prompt", "negative_prompt", "composition_analysis", "optimization_report")
    FUNCTION = "compose_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Advanced"
    DESCRIPTION = "Intelligent prompt composition with AI-assisted generation and optimization"
    
    @performance_monitor("prompt_composition")
    @cached_operation(ttl=300)
    def compose_prompt(self, main_subject, composition_mode, quality_preset,
                      style_elements="", technical_details="", lighting_atmosphere="",
                      negative_prompts="", custom_quality="", weight_subject=1.0,
                      weight_style=0.8, weight_technical=0.6, optimize_tokens=True, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(main_subject, "main_subject")
            if not validation["valid"]:
                return ("", "", f"Error: {validation['error']}", "")
        
        try:
            # Prepare elements
            elements = []
            weights = []
            
            if main_subject.strip():
                elements.append(("subject", main_subject.strip(), weight_subject))
            if style_elements.strip():
                elements.append(("style", style_elements.strip(), weight_style))
            if technical_details.strip():
                elements.append(("technical", technical_details.strip(), weight_technical))
            if lighting_atmosphere.strip():
                elements.append(("lighting", lighting_atmosphere.strip(), 0.7))
            
            # Get quality descriptors
            quality = custom_quality if quality_preset == "custom" else self._QUALITY_PRESETS[quality_preset]
            if quality:
                elements.append(("quality", quality, 0.5))
            
            # Compose based on mode
            composed = self._compose_by_mode(elements, composition_mode, optimize_tokens)
            
            # Generate analysis
            analysis = self._analyze_composition(elements, composition_mode)
            
            # Generate optimization report
            optimization = self._generate_optimization_report(composed, elements, optimize_tokens)
            
            return (composed, negative_prompts, analysis, optimization)
            
        except Exception as e:
            return ("", "", f"Error: {str(e)}", "")
    
    def _compose_by_mode(self, elements: List[Tuple[str, str, float]], mode: str, optimize: bool) -> str:
        """Compose prompt based on selected mode"""
        if mode == "layered":
            # Organize by logical layers
            order = ["subject", "style", "lighting", "technical", "quality"]
            sorted_elements = []
            for category in order:
                for elem_type, content, weight in elements:
                    if elem_type == category:
                        sorted_elements.append(content)
            return ", ".join(sorted_elements)
        
        elif mode == "weighted":
            # Sort by weight and format with weights
            sorted_elements = sorted(elements, key=lambda x: x[2], reverse=True)
            if optimize:
                return ", ".join(f"({content}:{weight:.1f})" if weight != 1.0 else content 
                               for _, content, weight in sorted_elements)
            else:
                return ", ".join(content for _, content, _ in sorted_elements)
        
        elif mode == "hierarchical":
            # Group by importance levels
            high_priority = [content for _, content, weight in elements if weight >= 1.0]
            medium_priority = [content for _, content, weight in elements if 0.5 <= weight < 1.0]
            low_priority = [content for _, content, weight in elements if weight < 0.5]
            
            result = []
            if high_priority: result.extend(high_priority)
            if medium_priority: result.extend(medium_priority)
            if low_priority: result.extend(low_priority)
            return ", ".join(result)
        
        elif mode == "narrative":
            # Create narrative flow
            narrative_order = ["subject", "lighting", "style", "technical", "quality"]
            connectors = ["", "with", "in", "featuring", "achieving"]
            
            result = []
            for i, category in enumerate(narrative_order):
                for elem_type, content, weight in elements:
                    if elem_type == category:
                        if i > 0 and i < len(connectors):
                            result.append(f"{connectors[i]} {content}")
                        else:
                            result.append(content)
            return " ".join(result)
        
        elif mode == "technical":
            # Emphasize technical elements first
            tech_order = ["technical", "quality", "subject", "lighting", "style"]
            result = []
            for category in tech_order:
                for elem_type, content, weight in elements:
                    if elem_type == category:
                        result.append(content)
            return ", ".join(result)
        
        elif mode == "artistic":
            # Emphasize artistic elements
            art_order = ["style", "lighting", "subject", "quality", "technical"]
            result = []
            for category in art_order:
                for elem_type, content, weight in elements:
                    if elem_type == category:
                        result.append(content)
            return ", ".join(result)
        
        else:
            # Default: simple concatenation
            return ", ".join(content for _, content, _ in elements)
    
    def _analyze_composition(self, elements: List[Tuple[str, str, float]], mode: str) -> str:
        """Generate composition analysis"""
        total_elements = len(elements)
        avg_weight = sum(weight for _, _, weight in elements) / max(total_elements, 1)
        
        element_types = [elem_type for elem_type, _, _ in elements]
        type_counts = Counter(element_types)
        
        analysis = f"Composition Mode: {mode}\\n"
        analysis += f"Total Elements: {total_elements}\\n"
        analysis += f"Average Weight: {avg_weight:.2f}\\n"
        analysis += f"Element Types: {dict(type_counts)}\\n"
        analysis += f"Strategy: {self._COMPOSITION_MODES[mode]}"
        
        return analysis
    
    def _generate_optimization_report(self, prompt: str, elements: List[Tuple[str, str, float]], optimized: bool) -> str:
        """Generate optimization report"""
        token_count = len(prompt.split())
        char_count = len(prompt)
        
        report = f"Optimization: {'Enabled' if optimized else 'Disabled'}\\n"
        report += f"Estimated Tokens: {token_count}\\n"
        report += f"Character Count: {char_count}\\n"
        
        # Check for redundancy
        words = prompt.lower().split()
        word_counts = Counter(words)
        repeated = [word for word, count in word_counts.items() if count > 1 and len(word) > 3]
        
        if repeated:
            report += f"Potential Redundancy: {', '.join(repeated[:5])}\\n"
        
        # Efficiency recommendations
        if token_count > 75:
            report += "⚠️ Consider reducing prompt length\\n"
        if len(repeated) > 3:
            report += "⚠️ Consider removing redundant terms\\n"
        if token_count < 20:
            report += "💡 Consider adding more descriptive elements\\n"
        
        return report

class XDEV_PromptVariableInjector(ValidationMixin):
    """
    Dynamic context injection system for prompts with smart variable replacement.
    Supports conditional logic, data binding, and context-aware substitution.
    """
    
    DISPLAY_NAME = "Dynamic Context Injector (XDev)"
    
    # Variable types and their processors
    _VARIABLE_TYPES = {
        "text": lambda x: str(x).strip(),
        "number": lambda x: str(float(x)) if '.' in str(x) else str(int(float(x))),
        "boolean": lambda x: "true" if bool(x) else "false",
        "list": lambda x: ", ".join(str(i).strip() for i in (x if isinstance(x, list) else [x])),
        "choice": lambda x: str(x).strip(),
        "weighted": lambda x: f"({x[0]}:{x[1]})" if isinstance(x, (list, tuple)) and len(x) == 2 else str(x)
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "template": ("STRING", {"default": "", "multiline": True, "tooltip": "Template with {{variables}} and {{?conditions}}"}),
                "context_json": ("STRING", {"default": "{}", "multiline": True, "tooltip": "JSON context with variable values"}),
            },
            "optional": {
                "var_name_1": ("STRING", {"default": "", "tooltip": "Variable name 1"}),
                "var_value_1": ("STRING", {"default": "", "tooltip": "Variable value 1"}),
                "var_type_1": (list(cls._VARIABLE_TYPES.keys()), {"default": "text", "tooltip": "Variable type 1"}),
                "var_name_2": ("STRING", {"default": "", "tooltip": "Variable name 2"}),
                "var_value_2": ("STRING", {"default": "", "tooltip": "Variable value 2"}),
                "var_type_2": (list(cls._VARIABLE_TYPES.keys()), {"default": "text", "tooltip": "Variable type 2"}),
                "var_name_3": ("STRING", {"default": "", "tooltip": "Variable name 3"}),
                "var_value_3": ("STRING", {"default": "", "tooltip": "Variable value 3"}),
                "var_type_3": (list(cls._VARIABLE_TYPES.keys()), {"default": "text", "tooltip": "Variable type 3"}),
                "fallback_mode": (["empty", "keep_placeholder", "error"], {"default": "empty", "tooltip": "What to do with missing variables"}),
                "validate_input": ("BOOLEAN", {"default": True, "tooltip": "Enable input validation"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("processed_prompt", "variable_report", "debug_info")
    FUNCTION = "inject_variables"
    CATEGORY = f"{NodeCategories.PROMPTS}/Advanced"
    DESCRIPTION = "Dynamic context injection with smart variable replacement and conditional logic"
    
    @performance_monitor("variable_injection")
    @cached_operation(ttl=300)
    def inject_variables(self, template, context_json="{}", var_name_1="", var_value_1="", var_type_1="text",
                        var_name_2="", var_value_2="", var_type_2="text", var_name_3="", var_value_3="", var_type_3="text",
                        fallback_mode="empty", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(template, "template")
            if not validation["valid"]:
                return ("", f"Error: {validation['error']}", "")
        
        try:
            # Parse context from JSON
            context = {}
            if context_json.strip():
                context = json.loads(context_json)
            
            # Add direct variables
            direct_vars = [
                (var_name_1, var_value_1, var_type_1),
                (var_name_2, var_value_2, var_type_2),
                (var_name_3, var_value_3, var_type_3)
            ]
            
            for name, value, var_type in direct_vars:
                if name.strip() and value.strip():
                    processor = self._VARIABLE_TYPES.get(var_type, self._VARIABLE_TYPES["text"])
                    context[name.strip()] = processor(value)
            
            # Process template
            processed, debug_info = self._process_template(template, context, fallback_mode)
            
            # Generate variable report
            var_report = self._generate_variable_report(context, template)
            
            return (processed, var_report, debug_info)
            
        except json.JSONDecodeError:
            return ("", "Error: Invalid JSON in context", "")
        except Exception as e:
            return ("", f"Error: {str(e)}", "")
    
    def _process_template(self, template: str, context: Dict[str, Any], fallback_mode: str) -> Tuple[str, str]:
        """Process template with variable substitution and conditional logic"""
        debug_info = []
        processed = template
        
        # Find all variables in template
        var_pattern = r'\\{\\{([^}]+)\\}\\}'
        variables_found = re.findall(var_pattern, processed)
        
        for var_expr in variables_found:
            debug_info.append(f"Processing: {var_expr}")
            
            # Handle conditional expressions
            if var_expr.startswith('?'):
                processed, debug = self._process_conditional(processed, var_expr, context)
                debug_info.append(debug)
            else:
                # Simple variable substitution
                if var_expr in context:
                    replacement = str(context[var_expr])
                    processed = processed.replace(f'{{{{{var_expr}}}}}', replacement)
                    debug_info.append(f"  → Replaced with: {replacement}")
                else:
                    # Handle missing variables
                    if fallback_mode == "empty":
                        processed = processed.replace(f'{{{{{var_expr}}}}}', "")
                        debug_info.append(f"  → Removed (missing)")
                    elif fallback_mode == "keep_placeholder":
                        debug_info.append(f"  → Kept placeholder (missing)")
                    elif fallback_mode == "error":
                        raise ValueError(f"Missing variable: {var_expr}")
        
        debug_report = "\\n".join(debug_info) if debug_info else "No variables processed"
        return processed.strip(), debug_report
    
    def _process_conditional(self, template: str, condition_expr: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """Process conditional expressions in template"""
        # Simple conditional: ?variable or ?variable==value
        condition = condition_expr[1:]  # Remove '?'
        
        if "==" in condition:
            var, expected = condition.split("==", 1)
            var = var.strip()
            expected = expected.strip()
            condition_met = str(context.get(var, "")) == expected
            debug = f"  → Condition {var}=={expected}: {condition_met}"
        else:
            condition_met = bool(context.get(condition.strip(), False))
            debug = f"  → Condition {condition}: {condition_met}"
        
        # Find and process conditional blocks
        if condition_met:
            # Keep content, remove condition markers
            pattern = f'\\{{\\?{re.escape(condition_expr)}\\}}(.*?)\\{{/{re.escape(condition_expr)}\\}}'
            matches = re.finditer(pattern, template, re.DOTALL)
            for match in matches:
                content = match.group(1)
                template = template.replace(match.group(0), content)
        else:
            # Remove entire conditional block
            pattern = f'\\{{\\?{re.escape(condition_expr)}\\}}.*?\\{{/{re.escape(condition_expr)}\\}}'
            template = re.sub(pattern, "", template, flags=re.DOTALL)
        
        return template, debug
    
    def _generate_variable_report(self, context: Dict[str, Any], template: str) -> str:
        """Generate report on variable usage"""
        var_pattern = r'\\{\\{([^}]+)\\}\\}'
        template_vars = set(re.findall(var_pattern, template))
        
        # Filter out conditional expressions
        template_vars = {var for var in template_vars if not var.startswith('?') and not var.startswith('/')}
        
        available_vars = set(context.keys())
        used_vars = template_vars.intersection(available_vars)
        missing_vars = template_vars - available_vars
        unused_vars = available_vars - template_vars
        
        report = f"Variables in template: {len(template_vars)}\\n"
        report += f"Available in context: {len(available_vars)}\\n"
        report += f"Successfully used: {len(used_vars)}\\n"
        
        if missing_vars:
            report += f"Missing variables: {', '.join(missing_vars)}\\n"
        if unused_vars:
            report += f"Unused variables: {', '.join(list(unused_vars)[:5])}\\n"
        
        return report


# Node registrations for the system
NODE_CLASS_MAPPINGS = {
    "XDEV_PromptTemplateEngine": XDEV_PromptTemplateEngine,
    "XDEV_PromptComposer": XDEV_PromptComposer,
    "XDEV_PromptVariableInjector": XDEV_PromptVariableInjector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_PromptTemplateEngine": "Prompt Template Engine (XDev)",
    "XDEV_PromptComposer": "Smart Prompt Composer (XDev)",
    "XDEV_PromptVariableInjector": "Dynamic Context Injector (XDev)",
}