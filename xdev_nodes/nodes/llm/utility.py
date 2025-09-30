"""
XDev LLM-Builder Utility Nodes
Text processing, JSON handling, and workflow routing utilities
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin

logger = logging.getLogger(__name__)

# =============================================================================
# 📊 UTILITY NODES
# =============================================================================

class XDEV_TextCleaner(ValidationMixin):
    """
    Text Cleaner Node - Comprehensive text cleaning and formatting
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_text": ("STRING", {
                    "multiline": True,
                    "tooltip": "Text to clean and process"
                })
            },
            "optional": {
                "remove_emojis": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Remove emoji characters"
                }),
                "remove_urls": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Remove URLs and web addresses"
                }),
                "remove_email": ("BOOLEAN", {
                    "default": True, 
                    "tooltip": "Remove email addresses"
                }),
                "remove_phone": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Remove phone numbers"
                }),
                "remove_special_chars": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Remove special characters (keep alphanumeric and spaces)"
                }),
                "normalize_whitespace": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Normalize multiple spaces/newlines to single spaces"
                }),
                "remove_stopwords": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Remove common English stopwords"
                }),
                "case_conversion": (["none", "lower", "upper", "title", "sentence"], {
                    "default": "none",
                    "tooltip": "Apply case conversion"
                }),
                "max_length": ("INT", {
                    "default": 0, "min": 0, "max": 10000,
                    "tooltip": "Maximum text length (0 = no limit)"
                }),
                "custom_replacements": ("STRING", {
                    "default": "{}",
                    "tooltip": "JSON object with custom find/replace pairs {'find': 'replace'}"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("cleaned_text", "cleaning_report", "original_text")
    FUNCTION = "clean_text"
    CATEGORY = "XDev/LLM-Builder/Utility"
    DESCRIPTION = "Comprehensive text cleaning with multiple processing options"

    # Common English stopwords
    _STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
        "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
        "was", "will", "with", "the", "this", "but", "they", "have", "had", "what",
        "said", "each", "which", "she", "do", "how", "their", "if", "up", "out",
        "many", "then", "them", "these", "so", "some", "her", "would", "make",
        "like", "into", "him", "time", "two", "more", "go", "no", "way", "could",
        "my", "than", "first", "water", "been", "call", "who", "oil", "sit", "now"
    }

    @performance_monitor("text_cleaner")
    def clean_text(self, input_text, remove_emojis=True, remove_urls=True, 
                  remove_email=True, remove_phone=True, remove_special_chars=False,
                  normalize_whitespace=True, remove_stopwords=False, 
                  case_conversion="none", max_length=0, custom_replacements="{}", 
                  validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(input_text, "input_text")
            if not validation["valid"]:
                return ("", f"Validation Error: {validation['error']}", input_text)
        
        try:
            original_text = input_text
            cleaned_text = input_text
            cleaning_steps = []
            
            # Apply custom replacements first
            try:
                replacements = json.loads(custom_replacements) if custom_replacements.strip() else {}
                if isinstance(replacements, dict):
                    for find_str, replace_str in replacements.items():
                        old_length = len(cleaned_text)
                        cleaned_text = cleaned_text.replace(str(find_str), str(replace_str))
                        if len(cleaned_text) != old_length:
                            cleaning_steps.append(f"Custom replacement: '{find_str}' -> '{replace_str}'")
            except json.JSONDecodeError:
                cleaning_steps.append("Warning: Invalid custom_replacements JSON")
            
            # Remove URLs
            if remove_urls:
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                old_length = len(cleaned_text)
                cleaned_text = re.sub(url_pattern, '', cleaned_text)
                if len(cleaned_text) != old_length:
                    cleaning_steps.append("Removed URLs")
            
            # Remove email addresses
            if remove_email:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                old_length = len(cleaned_text)
                cleaned_text = re.sub(email_pattern, '', cleaned_text)
                if len(cleaned_text) != old_length:
                    cleaning_steps.append("Removed email addresses")
            
            # Remove phone numbers
            if remove_phone:
                phone_pattern = r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
                old_length = len(cleaned_text)
                cleaned_text = re.sub(phone_pattern, '', cleaned_text)
                if len(cleaned_text) != old_length:
                    cleaning_steps.append("Removed phone numbers")
            
            # Remove emojis
            if remove_emojis:
                emoji_pattern = re.compile("["
                    u"\U0001F600-\U0001F64F"  # emoticons
                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                    u"\U00002702-\U000027B0"
                    u"\U000024C2-\U0001F251"
                    "]+", flags=re.UNICODE)
                old_length = len(cleaned_text)
                cleaned_text = emoji_pattern.sub('', cleaned_text)
                if len(cleaned_text) != old_length:
                    cleaning_steps.append("Removed emojis")
            
            # Remove special characters
            if remove_special_chars:
                old_length = len(cleaned_text)
                cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)
                if len(cleaned_text) != old_length:
                    cleaning_steps.append("Removed special characters")
            
            # Normalize whitespace
            if normalize_whitespace:
                old_length = len(cleaned_text)
                cleaned_text = ' '.join(cleaned_text.split())
                if len(cleaned_text) != old_length:
                    cleaning_steps.append("Normalized whitespace")
            
            # Remove stopwords
            if remove_stopwords:
                words = cleaned_text.split()
                old_word_count = len(words)
                filtered_words = [word for word in words if word.lower() not in self._STOPWORDS]
                cleaned_text = ' '.join(filtered_words)
                if len(filtered_words) != old_word_count:
                    cleaning_steps.append(f"Removed {old_word_count - len(filtered_words)} stopwords")
            
            # Apply case conversion
            if case_conversion != "none":
                if case_conversion == "lower":
                    cleaned_text = cleaned_text.lower()
                elif case_conversion == "upper":
                    cleaned_text = cleaned_text.upper()
                elif case_conversion == "title":
                    cleaned_text = cleaned_text.title()
                elif case_conversion == "sentence":
                    cleaned_text = cleaned_text.capitalize()
                cleaning_steps.append(f"Applied {case_conversion} case conversion")
            
            # Apply length limit
            if max_length > 0 and len(cleaned_text) > max_length:
                cleaned_text = cleaned_text[:max_length].rsplit(' ', 1)[0] + "..."
                cleaning_steps.append(f"Truncated to {max_length} characters")
            
            # Generate cleaning report
            original_length = len(original_text)
            final_length = len(cleaned_text)
            cleaning_report = f"Original: {original_length} chars, Final: {final_length} chars. "
            cleaning_report += f"Steps applied: {', '.join(cleaning_steps) if cleaning_steps else 'None'}"
            
            return (cleaned_text, cleaning_report, original_text)
            
        except Exception as e:
            error_msg = f"Text Cleaning Error: {str(e)}"
            logger.error(error_msg)
            return (input_text, error_msg, input_text)


class XDEV_JSONExtractor(ValidationMixin):
    """
    JSON Extractor Node - Extract and manipulate JSON data from text
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_text": ("STRING", {
                    "multiline": True,
                    "tooltip": "Text containing JSON data"
                })
            },
            "optional": {
                "extraction_mode": (["auto_detect", "extract_first", "extract_all", "parse_direct"], {
                    "default": "auto_detect",
                    "tooltip": "How to find and extract JSON from text"
                }),
                "target_key": ("STRING", {
                    "default": "",
                    "tooltip": "Specific JSON key to extract (leave empty for entire object)"
                }),
                "array_index": ("INT", {
                    "default": 0, "min": 0, "max": 100,
                    "tooltip": "Array index to extract (if JSON contains arrays)"
                }),
                "output_format": (["json_string", "pretty_json", "key_value_pairs", "extracted_value"], {
                    "default": "pretty_json",
                    "tooltip": "Format for the output"
                }),
                "fallback_behavior": (["return_original", "return_empty", "create_json"], {
                    "default": "return_original",
                    "tooltip": "What to do if JSON extraction fails"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("extracted_data", "extraction_info", "raw_json")
    FUNCTION = "extract_json"
    CATEGORY = "XDev/LLM-Builder/Utility"
    DESCRIPTION = "Extract and process JSON data from LLM responses or text"

    @performance_monitor("json_extractor")
    def extract_json(self, input_text, extraction_mode="auto_detect", target_key="",
                    array_index=0, output_format="pretty_json", fallback_behavior="return_original",
                    validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(input_text, "input_text")
            if not validation["valid"]:
                return ("", f"Validation Error: {validation['error']}", "")
        
        try:
            # Extract JSON based on mode
            json_data = None
            raw_json = ""
            
            if extraction_mode == "parse_direct":
                # Try to parse the entire input as JSON
                json_data = json.loads(input_text.strip())
                raw_json = input_text.strip()
                
            elif extraction_mode == "extract_first":
                # Find first JSON object or array
                json_data, raw_json = self._extract_first_json(input_text)
                
            elif extraction_mode == "extract_all":
                # Find all JSON objects (return as array)
                all_json = self._extract_all_json(input_text)
                json_data = all_json
                raw_json = json.dumps(all_json)
                
            else:  # auto_detect
                # Try multiple extraction methods
                json_data, raw_json = self._auto_detect_json(input_text)
            
            # Handle extraction failure
            if json_data is None:
                return self._handle_extraction_failure(input_text, fallback_behavior)
            
            # Extract specific key if requested
            if target_key.strip() and isinstance(json_data, dict):
                if target_key in json_data:
                    json_data = json_data[target_key]
                else:
                    return self._handle_key_not_found(target_key, json_data, fallback_behavior)
            
            # Handle array indexing
            if isinstance(json_data, list) and array_index < len(json_data):
                json_data = json_data[array_index]
            
            # Format output
            extracted_data = self._format_output(json_data, output_format)
            
            # Generate info
            data_type = type(json_data).__name__
            if isinstance(json_data, (list, dict)):
                size_info = f"length: {len(json_data)}"
            else:
                size_info = f"value type: {data_type}"
            
            extraction_info = f"Mode: {extraction_mode}, Target: {target_key or 'none'}, Data: {size_info}"
            
            return (extracted_data, extraction_info, raw_json)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON Parse Error: {str(e)}"
            return self._handle_extraction_failure(input_text, fallback_behavior, error_msg)
            
        except Exception as e:
            error_msg = f"JSON Extraction Error: {str(e)}"
            logger.error(error_msg)
            return self._handle_extraction_failure(input_text, fallback_behavior, error_msg)

    def _extract_first_json(self, text: str) -> Tuple[Any, str]:
        """Extract the first JSON object or array found in text"""
        # Look for JSON objects
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        bracket_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
        
        for pattern in [brace_pattern, bracket_pattern]:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    json_str = match.group()
                    json_data = json.loads(json_str)
                    return json_data, json_str
                except json.JSONDecodeError:
                    continue
        
        return None, ""

    def _extract_all_json(self, text: str) -> List[Any]:
        """Extract all JSON objects and arrays from text"""
        all_json = []
        
        # Find all potential JSON structures
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        bracket_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
        
        for pattern in [brace_pattern, bracket_pattern]:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    json_str = match.group()
                    json_data = json.loads(json_str)
                    all_json.append(json_data)
                except json.JSONDecodeError:
                    continue
        
        return all_json

    def _auto_detect_json(self, text: str) -> Tuple[Any, str]:
        """Auto-detect and extract JSON using multiple strategies"""
        # Strategy 1: Try parsing entire text
        try:
            json_data = json.loads(text.strip())
            return json_data, text.strip()
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Look for JSON blocks marked with ```json
        json_block_pattern = r'```json\s*\n(.*?)\n```'
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1).strip()
                json_data = json.loads(json_str)
                return json_data, json_str
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find first valid JSON object/array
        return self._extract_first_json(text)

    def _format_output(self, data: Any, format_type: str) -> str:
        """Format the extracted data according to output format"""
        if format_type == "json_string":
            return json.dumps(data, ensure_ascii=False)
        
        elif format_type == "pretty_json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        elif format_type == "key_value_pairs":
            if isinstance(data, dict):
                pairs = []
                for key, value in data.items():
                    pairs.append(f"{key}: {value}")
                return "\n".join(pairs)
            else:
                return str(data)
        
        elif format_type == "extracted_value":
            return str(data)
        
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)

    def _handle_extraction_failure(self, original_text: str, fallback_behavior: str, error_msg: str = "") -> Tuple[str, str, str]:
        """Handle cases where JSON extraction fails"""
        if fallback_behavior == "return_empty":
            return ("", f"JSON extraction failed. {error_msg}".strip(), "")
        
        elif fallback_behavior == "create_json":
            fallback_json = {"original_text": original_text, "extraction_failed": True}
            return (json.dumps(fallback_json, indent=2), f"Created fallback JSON. {error_msg}".strip(), "")
        
        else:  # return_original
            return (original_text, f"Returned original text. {error_msg}".strip(), "")

    def _handle_key_not_found(self, target_key: str, json_data: Dict, fallback_behavior: str) -> Tuple[str, str, str]:
        """Handle cases where target key is not found"""
        available_keys = list(json_data.keys()) if isinstance(json_data, dict) else []
        error_msg = f"Key '{target_key}' not found. Available keys: {available_keys}"
        
        if fallback_behavior == "return_empty":
            return ("", error_msg, "")
        elif fallback_behavior == "create_json":
            fallback_json = {"error": f"Key '{target_key}' not found", "available_keys": available_keys}
            return (json.dumps(fallback_json, indent=2), error_msg, "")
        else:
            return (json.dumps(json_data, indent=2), error_msg, "")


class XDEV_Router(ValidationMixin):
    """
    Router Node - Conditional workflow routing based on text analysis
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_text": ("STRING", {
                    "multiline": True,
                    "tooltip": "Text to analyze for routing decisions"
                }),
                "routing_mode": (["keyword_match", "json_field", "text_length", "pattern_match", "sentiment_basic"], {
                    "default": "keyword_match",
                    "tooltip": "Method for determining routing"
                })
            },
            "optional": {
                "route_keywords": ("STRING", {
                    "default": "image,visual,picture|chat,talk,conversation|data,analyze,process",
                    "tooltip": "Keywords for routing (pipe-separated groups)"
                }),
                "json_field": ("STRING", {
                    "default": "action",
                    "tooltip": "JSON field to check for routing (json_field mode)"
                }),
                "json_values": ("STRING", {
                    "default": "image|chat|data",
                    "tooltip": "JSON field values for routing (pipe-separated)"
                }),
                "length_thresholds": ("STRING", {
                    "default": "50|200|500",
                    "tooltip": "Length thresholds for routing (pipe-separated)"
                }),
                "regex_patterns": ("STRING", {
                    "default": "\\b(image|img|photo)\\b|\\b(chat|talk|speak)\\b|\\b(data|json|analyze)\\b",
                    "tooltip": "Regex patterns for routing (pipe-separated)"
                }),
                "default_route": ("STRING", {
                    "default": "route_1",
                    "tooltip": "Default route when no conditions match"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("selected_route", "route_info", "analysis_details", "input_passthrough")
    FUNCTION = "route_text"
    CATEGORY = "XDev/LLM-Builder/Utility"
    DESCRIPTION = "Conditional workflow routing based on text content analysis"

    @performance_monitor("router")
    def route_text(self, input_text, routing_mode="keyword_match", route_keywords="image,visual,picture|chat,talk,conversation|data,analyze,process",
                  json_field="action", json_values="image|chat|data", length_thresholds="50|200|500",
                  regex_patterns="\\b(image|img|photo)\\b|\\b(chat|talk|speak)\\b|\\b(data|json|analyze)\\b",
                  default_route="route_1", validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(input_text, "input_text")
            if not validation["valid"]:
                return (default_route, f"Validation Error: {validation['error']}", "", input_text)
        
        try:
            selected_route = default_route
            analysis_details = ""
            
            if routing_mode == "keyword_match":
                selected_route, analysis_details = self._route_by_keywords(input_text, route_keywords, default_route)
                
            elif routing_mode == "json_field":
                selected_route, analysis_details = self._route_by_json_field(input_text, json_field, json_values, default_route)
                
            elif routing_mode == "text_length":
                selected_route, analysis_details = self._route_by_length(input_text, length_thresholds, default_route)
                
            elif routing_mode == "pattern_match":
                selected_route, analysis_details = self._route_by_pattern(input_text, regex_patterns, default_route)
                
            elif routing_mode == "sentiment_basic":
                selected_route, analysis_details = self._route_by_sentiment(input_text, default_route)
            
            # Generate route info
            route_info = f"Mode: {routing_mode}, Selected: {selected_route}, Input length: {len(input_text)} chars"
            
            return (selected_route, route_info, analysis_details, input_text)
            
        except Exception as e:
            error_msg = f"Router Error: {str(e)}"
            logger.error(error_msg)
            return (default_route, error_msg, "", input_text)

    def _route_by_keywords(self, text: str, route_keywords: str, default_route: str) -> Tuple[str, str]:
        """Route based on keyword matching"""
        text_lower = text.lower()
        keyword_groups = route_keywords.split("|")
        
        for i, group in enumerate(keyword_groups):
            keywords = [kw.strip() for kw in group.split(",")]
            matches = []
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.append(keyword)
            
            if matches:
                route = f"route_{i + 1}"
                details = f"Matched keywords: {', '.join(matches)} -> {route}"
                return route, details
        
        return default_route, f"No keywords matched, using default: {default_route}"

    def _route_by_json_field(self, text: str, json_field: str, json_values: str, default_route: str) -> Tuple[str, str]:
        """Route based on JSON field value"""
        try:
            data = json.loads(text)
            if json_field in data:
                field_value = str(data[json_field]).lower()
                value_options = [v.strip().lower() for v in json_values.split("|")]
                
                for i, value in enumerate(value_options):
                    if value in field_value:
                        route = f"route_{i + 1}"
                        details = f"JSON field '{json_field}': '{field_value}' matched '{value}' -> {route}"
                        return route, details
                
                return default_route, f"JSON field '{json_field}' value '{field_value}' didn't match any options"
            else:
                return default_route, f"JSON field '{json_field}' not found"
                
        except json.JSONDecodeError:
            return default_route, "Input is not valid JSON"

    def _route_by_length(self, text: str, length_thresholds: str, default_route: str) -> Tuple[str, str]:
        """Route based on text length"""
        text_length = len(text)
        thresholds = [int(t.strip()) for t in length_thresholds.split("|")]
        
        for i, threshold in enumerate(thresholds):
            if text_length <= threshold:
                route = f"route_{i + 1}"
                details = f"Text length {text_length} <= threshold {threshold} -> {route}"
                return route, details
        
        # If longer than all thresholds
        route = f"route_{len(thresholds) + 1}"
        details = f"Text length {text_length} > all thresholds -> {route}"
        return route, details

    def _route_by_pattern(self, text: str, regex_patterns: str, default_route: str) -> Tuple[str, str]:
        """Route based on regex pattern matching"""
        patterns = regex_patterns.split("|")
        
        for i, pattern in enumerate(patterns):
            try:
                if re.search(pattern.strip(), text, re.IGNORECASE):
                    route = f"route_{i + 1}"
                    details = f"Pattern '{pattern}' matched -> {route}"
                    return route, details
            except re.error:
                continue  # Skip invalid regex patterns
        
        return default_route, f"No patterns matched, using default: {default_route}"

    def _route_by_sentiment(self, text: str, default_route: str) -> Tuple[str, str]:
        """Basic sentiment-based routing"""
        text_lower = text.lower()
        
        # Simple sentiment word lists
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "happy", "excited"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "sad", "angry", "frustrated", "disappointed", "horrible"]
        question_words = ["what", "how", "when", "where", "why", "who", "which", "can", "could", "would", "should"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        question_count = sum(1 for word in question_words if text_lower.startswith(word) or f" {word} " in text_lower)
        
        if question_count > 0:
            return "route_1", f"Question detected (question words: {question_count}) -> route_1"
        elif positive_count > negative_count and positive_count > 0:
            return "route_2", f"Positive sentiment (positive: {positive_count}, negative: {negative_count}) -> route_2"
        elif negative_count > 0:
            return "route_3", f"Negative sentiment (positive: {positive_count}, negative: {negative_count}) -> route_3"
        else:
            return default_route, f"Neutral sentiment -> {default_route}"
