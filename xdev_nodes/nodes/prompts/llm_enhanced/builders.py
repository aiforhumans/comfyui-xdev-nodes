"""
Prompt Building and Bridge Tools for XDev Framework
Advanced prompt construction, variable substitution, and format conversion
"""

import json
import re
from typing import Dict, List, Tuple, Any, Optional, Union
from ....performance import performance_monitor, cached_operation
from ....mixins import ValidationMixin
from ....categories import NodeCategories

class XDEV_PromptBuilderAdvanced(ValidationMixin):
    """
    Advanced Prompt Builder - Merge multiple text blocks with variables
    """
    
    DISPLAY_NAME = "Advanced Prompt Builder (XDev)"
    
    @classmethod 
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "template": ("STRING", {
                    "multiline": True,
                    "default": "Create an image of {subject} in {style} with {details}",
                    "tooltip": "Template with {variable} placeholders"
                })
            },
            "optional": {
                "subject": ("STRING", {
                    "default": "",
                    "tooltip": "Subject variable for {subject} placeholder"
                }),
                "style": ("STRING", {
                    "default": "",
                    "tooltip": "Style variable for {style} placeholder"  
                }),
                "details": ("STRING", {
                    "default": "",
                    "tooltip": "Details variable for {details} placeholder"
                }),
                "environment": ("STRING", {
                    "default": "",
                    "tooltip": "Environment variable for {environment} placeholder"
                }),
                "quality": ("STRING", {
                    "default": "",
                    "tooltip": "Quality variable for {quality} placeholder"
                }),
                "additional_vars": ("STRING", {
                    "default": "{}",
                    "tooltip": "JSON object with additional variables {'var_name': 'value'}"
                }),
                "output_format": (["string", "json"], {
                    "default": "string",
                    "tooltip": "Output format: string or structured JSON"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("built_prompt", "variables_info")
    FUNCTION = "build_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Builder"
    DESCRIPTION = "Advanced prompt builder with variable substitution and JSON output"

    @performance_monitor("prompt_builder_advanced")
    def build_prompt(self, template, subject="", style="", details="", 
                    environment="", quality="", additional_vars="{}", 
                    output_format="string", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(template, "template")
            if not validation["valid"]:
                return ("", f"Validation Error: {validation['error']}")
        
        try:
            # Build variables dictionary
            variables = {
                "subject": subject,
                "style": style, 
                "details": details,
                "environment": environment,
                "quality": quality
            }
            
            # Add additional variables
            try:
                extra_vars = json.loads(additional_vars) if additional_vars.strip() else {}
                if isinstance(extra_vars, dict):
                    variables.update(extra_vars)
            except json.JSONDecodeError:
                # Invalid JSON, continue without additional vars
                pass
            
            # Filter out empty variables
            variables = {k: v for k, v in variables.items() if v.strip()}
            
            # Build prompt
            try:
                built_prompt = template.format(**variables)
            except KeyError as e:
                missing_var = str(e).strip("'")
                built_prompt = template  # Return template as-is if variable missing
                variables_info = f"Warning: Missing variable {missing_var}"
                return (built_prompt, variables_info)
            
            # Format output
            if output_format == "json":
                output_data = {
                    "prompt": built_prompt,
                    "variables": variables,
                    "template": template
                }
                built_prompt = json.dumps(output_data, indent=2)
            
            # Build info
            var_count = len(variables)
            var_names = list(variables.keys())
            variables_info = f"Variables used: {var_count} ({', '.join(var_names)})"
            
            return (built_prompt, variables_info)
            
        except Exception as e:
            error_msg = f"Prompt Builder Error: {str(e)}"
            return (template, error_msg)

class XDEV_TextToImagePromptBridge(ValidationMixin):
    """
    Text-to-Image Prompt Bridge - Convert LLM response to SDXL prompt
    """
    
    DISPLAY_NAME = "Text-to-Image Prompt Bridge (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "llm_response": ("STRING", {
                    "multiline": True,
                    "tooltip": "Response from LM Studio or other LLM"
                })
            },
            "optional": {
                "extraction_mode": (["direct", "extract_description", "extract_json", "clean_and_format"], {
                    "default": "clean_and_format",
                    "tooltip": "How to process LLM response into image prompt"
                }),
                "style_suffix": ("STRING", {
                    "default": "highly detailed, professional photography, 8k resolution",
                    "tooltip": "Quality/style terms to append"
                }),
                "negative_terms": ("STRING", {
                    "default": "blurry, low quality, distorted",
                    "tooltip": "Terms to remove or add to negative prompt"
                }),
                "max_length": ("INT", {
                    "default": 500, "min": 50, "max": 2000,
                    "tooltip": "Maximum prompt length"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("sdxl_prompt", "negative_prompt", "processing_info")
    FUNCTION = "convert_to_image_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Builder"
    DESCRIPTION = "Convert LLM text response to SDXL-compatible image prompt"

    @performance_monitor("text_to_image_bridge")
    def convert_to_image_prompt(self, llm_response, extraction_mode="clean_and_format",
                               style_suffix="highly detailed, professional photography, 8k resolution",
                               negative_terms="blurry, low quality, distorted",
                               max_length=500, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(llm_response, "llm_response")
            if not validation["valid"]:
                return ("", "", f"Validation Error: {validation['error']}")
        
        try:
            # Process based on extraction mode
            if extraction_mode == "direct":
                prompt = llm_response.strip()
                
            elif extraction_mode == "extract_description":
                # Extract descriptive text, remove conversational elements
                prompt = self._extract_description(llm_response)
                
            elif extraction_mode == "extract_json":
                # Try to extract from JSON response
                prompt = self._extract_from_json(llm_response)
                
            elif extraction_mode == "clean_and_format":
                # Clean and format for image generation
                prompt = self._clean_and_format(llm_response)
            
            else:
                prompt = llm_response.strip()
            
            # Truncate if too long
            if len(prompt) > max_length:
                prompt = prompt[:max_length].rsplit(' ', 1)[0] + "..."
            
            # Add style suffix if provided
            if style_suffix.strip():
                prompt = f"{prompt}, {style_suffix}"
            
            # Build negative prompt
            negative_prompt = negative_terms.strip()
            
            # Build processing info
            processing_info = f"Mode: {extraction_mode}\\nLength: {len(prompt)} chars"
            if len(llm_response) > max_length:
                processing_info += "\\nTruncated: Yes"
            
            return (prompt, negative_prompt, processing_info)
            
        except Exception as e:
            error_msg = f"Bridge conversion failed: {str(e)}"
            return (llm_response, negative_terms, error_msg)
    
    def _extract_description(self, text: str) -> str:
        """Extract descriptive content from conversational text."""
        # Remove common conversational elements
        lines = text.split('\\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip if line is too short or looks conversational
            if len(line) < 10:
                continue
            if line.lower().startswith(('here', 'i hope', 'please', 'thank', 'let me', 'would you')):
                continue
            if line.endswith('?'):
                continue
            cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def _extract_from_json(self, text: str) -> str:
        """Try to extract prompt from JSON response."""
        try:
            # Look for JSON in the text
            json_match = re.search(r'\\{.*\\}', text, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                # Look for common prompt fields
                for field in ['prompt', 'description', 'text', 'content']:
                    if field in json_data:
                        return str(json_data[field])
            return text.strip()
        except:
            return text.strip()
    
    def _clean_and_format(self, text: str) -> str:
        """Clean and format text for image generation."""
        # Remove line breaks and normalize whitespace
        cleaned = ' '.join(text.split())
        
        # Remove common conversational patterns
        patterns_to_remove = [
            r'^(Here is|Here\'s|I would suggest|I recommend)\\s+',
            r'\\b(please|thank you|hope this helps)\\b',
            r'[.!?]\\s*$'  # Remove ending punctuation
        ]
        
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\\s+', ' ', cleaned).strip()
        
        return cleaned

class XDEV_PromptFormatter(ValidationMixin):
    """
    Advanced prompt formatter with multiple output styles and structure options.
    """
    
    DISPLAY_NAME = "Prompt Formatter (XDev)"
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Prompt to format and structure"
                }),
                "format_style": (["comma_separated", "structured", "weighted", "sdxl_optimized", "minimal"], {
                    "default": "comma_separated",
                    "tooltip": "Output formatting style"
                })
            },
            "optional": {
                "quality_level": (["basic", "enhanced", "professional"], {
                    "default": "enhanced",
                    "tooltip": "Quality enhancement level"
                }),
                "add_technical": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Add technical quality terms"
                }),
                "remove_redundancy": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Remove redundant terms"
                }),
                "max_length": ("INT", {
                    "default": 400, "min": 100, "max": 1000,
                    "tooltip": "Maximum output length"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("formatted_prompt", "negative_prompt", "format_info")
    FUNCTION = "format_prompt"
    CATEGORY = f"{NodeCategories.PROMPTS}/Builder"
    DESCRIPTION = "Format and structure prompts with multiple style options"
    
    @performance_monitor("prompt_formatter")
    def format_prompt(self, input_prompt, format_style="comma_separated", 
                     quality_level="enhanced", add_technical=True, 
                     remove_redundancy=True, max_length=400, validate_input=True):
        
        if validate_input:
            if not input_prompt.strip():
                return ("", "", "Error: Input prompt cannot be empty")
        
        try:
            # Clean and normalize input
            cleaned_prompt = self._clean_input(input_prompt, remove_redundancy)
            
            # Apply formatting style
            if format_style == "comma_separated":
                formatted = self._format_comma_separated(cleaned_prompt)
            elif format_style == "structured":
                formatted = self._format_structured(cleaned_prompt)
            elif format_style == "weighted":
                formatted = self._format_weighted(cleaned_prompt)
            elif format_style == "sdxl_optimized":
                formatted = self._format_sdxl_optimized(cleaned_prompt)
            elif format_style == "minimal":
                formatted = self._format_minimal(cleaned_prompt)
            else:
                formatted = cleaned_prompt
            
            # Add quality enhancement
            if add_technical:
                formatted = self._add_quality_terms(formatted, quality_level)
            
            # Truncate if needed
            if len(formatted) > max_length:
                formatted = formatted[:max_length].rsplit(',', 1)[0]
            
            # Generate negative prompt based on quality level
            negative_prompt = self._generate_negative_prompt(quality_level)
            
            # Build format info
            format_info = f"Style: {format_style}\\nQuality: {quality_level}\\nLength: {len(formatted)} chars"
            
            return (formatted, negative_prompt, format_info)
            
        except Exception as e:
            return (input_prompt, "", f"Formatting error: {str(e)}")
    
    def _clean_input(self, text: str, remove_redundancy: bool) -> str:
        """Clean and normalize input text."""
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.split())
        
        if remove_redundancy:
            # Remove duplicate words (basic redundancy removal)
            words = cleaned.split()
            seen = set()
            deduplicated = []
            for word in words:
                word_lower = word.lower().strip('.,')
                if word_lower not in seen:
                    seen.add(word_lower)
                    deduplicated.append(word)
            cleaned = ' '.join(deduplicated)
        
        return cleaned
    
    def _format_comma_separated(self, text: str) -> str:
        """Format as comma-separated terms."""
        # Split on various delimiters and rejoin with commas
        delimiters = ['.', ';', '\\n', ' and ', ' with ', ' of ']
        for delimiter in delimiters:
            text = text.replace(delimiter, ',')
        
        # Clean up multiple commas and spaces
        text = re.sub(r',+', ',', text)
        text = re.sub(r'\\s*,\\s*', ', ', text)
        
        return text.strip(', ')
    
    def _format_structured(self, text: str) -> str:
        """Format with structured organization."""
        # Attempt to identify different components
        words = text.split()
        
        # Simple categorization (could be enhanced)
        subjects = []
        styles = []
        qualities = []
        
        style_keywords = ['style', 'painting', 'digital', 'photographic', 'art']
        quality_keywords = ['detailed', 'quality', 'resolution', 'realistic']
        
        for word in words:
            word_lower = word.lower()
            if any(kw in word_lower for kw in style_keywords):
                styles.append(word)
            elif any(kw in word_lower for kw in quality_keywords):
                qualities.append(word)
            else:
                subjects.append(word)
        
        # Rebuild with structure
        parts = []
        if subjects:
            parts.append(' '.join(subjects))
        if styles:
            parts.append(' '.join(styles))
        if qualities:
            parts.append(' '.join(qualities))
        
        return ', '.join(parts)
    
    def _format_weighted(self, text: str) -> str:
        """Format with weight emphasis using parentheses."""
        # Add weights to important terms
        weighted = text
        
        # High importance terms get double parentheses
        high_importance = ['masterpiece', 'detailed', 'professional', 'high quality']
        for term in high_importance:
            if term in weighted.lower():
                weighted = re.sub(f'\\b{term}\\b', f'(({term}))', weighted, flags=re.IGNORECASE)
        
        # Medium importance terms get single parentheses
        medium_importance = ['beautiful', 'stunning', 'intricate', 'elegant']
        for term in medium_importance:
            if term in weighted.lower():
                weighted = re.sub(f'\\b{term}\\b', f'({term})', weighted, flags=re.IGNORECASE)
        
        return weighted
    
    def _format_sdxl_optimized(self, text: str) -> str:
        """Format optimized for SDXL model."""
        # SDXL-specific formatting
        sdxl_optimized = text
        
        # Add SDXL-friendly terms
        if 'photo' in text.lower() or 'photograph' in text.lower():
            sdxl_optimized += ", RAW photo, natural lighting"
        
        if 'art' in text.lower() or 'painting' in text.lower():
            sdxl_optimized += ", digital art, concept art"
        
        return sdxl_optimized
    
    def _format_minimal(self, text: str) -> str:
        """Format as minimal, essential terms only."""
        # Keep only essential words (remove common adjectives)
        stop_words = ['very', 'really', 'quite', 'somewhat', 'rather', 'pretty']
        words = text.split()
        
        filtered = [word for word in words if word.lower() not in stop_words]
        
        return ' '.join(filtered)
    
    def _add_quality_terms(self, text: str, quality_level: str) -> str:
        """Add quality enhancement terms."""
        quality_terms = {
            "basic": ["good quality"],
            "enhanced": ["high quality", "detailed"],
            "professional": ["masterpiece", "professional", "highly detailed", "8k resolution"]
        }
        
        terms = quality_terms.get(quality_level, quality_terms["enhanced"])
        return f"{text}, {', '.join(terms)}"
    
    def _generate_negative_prompt(self, quality_level: str) -> str:
        """Generate appropriate negative prompt."""
        base_negative = "blurry, low quality"
        
        if quality_level == "professional":
            return f"{base_negative}, distorted, ugly, bad anatomy, worst quality"
        elif quality_level == "enhanced":
            return f"{base_negative}, distorted, bad quality"
        else:
            return base_negative

# Node registrations
NODE_CLASS_MAPPINGS = {
    "XDEV_PromptBuilderAdvanced": XDEV_PromptBuilderAdvanced,
    "XDEV_TextToImagePromptBridge": XDEV_TextToImagePromptBridge,
    "XDEV_PromptFormatter": XDEV_PromptFormatter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_PromptBuilderAdvanced": "Advanced Prompt Builder (XDev)",
    "XDEV_TextToImagePromptBridge": "Text-to-Image Prompt Bridge (XDev)",
    "XDEV_PromptFormatter": "Prompt Formatter (XDev)",
}