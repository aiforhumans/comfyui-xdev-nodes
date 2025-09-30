"""
XDev LLM-Builder Advanced Integration Nodes
Cutting-edge LLM integrations for multi-modal and workflow control
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin

# Graceful imports for HTTP clients
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    httpx = None
    HAS_HTTPX = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

logger = logging.getLogger(__name__)

# =============================================================================
# 🖥️ ADVANCED INTEGRATION NODES
# =============================================================================

class XDEV_MultiModal(ValidationMixin):
    """
    Multi-Modal Node - Combine text and image data for advanced LLM processing
    Prepares for future vision model integration
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "text_input": ("STRING", {
                    "multiline": True,
                    "tooltip": "Text content for multi-modal analysis"
                })
            },
            "optional": {
                "image_description": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Description of image content (for future image input)"
                }),
                "image_metadata": ("STRING", {
                    "default": "",
                    "tooltip": "Image metadata as JSON string"
                }),
                "analysis_type": (["describe_scene", "generate_caption", "analyze_content", "create_prompt", "compare_elements"], {
                    "default": "describe_scene",
                    "tooltip": "Type of multi-modal analysis to perform"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL for processing"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "Model identifier (future: vision model support)"
                }),
                "max_tokens": ("INT", {
                    "default": 300, "min": 50, "max": 1000,
                    "tooltip": "Maximum tokens for analysis"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7, "min": 0.0, "max": 1.5, "step": 0.1,
                    "tooltip": "Analysis creativity level"
                }),
                "include_technical_details": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Include technical analysis details"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("analysis_result", "multimodal_prompt", "technical_details", "combined_data")
    FUNCTION = "analyze_multimodal"
    CATEGORY = "XDev/LLM-Builder/Advanced"
    DESCRIPTION = "Multi-modal analysis combining text and image data (vision model ready)"

    # Analysis prompts for different types
    _ANALYSIS_PROMPTS = {
        "describe_scene": "Analyze the following text and image description to create a comprehensive scene description:",
        "generate_caption": "Create a detailed caption based on the text content and image description:",
        "analyze_content": "Perform a detailed content analysis of the combined text and visual information:",
        "create_prompt": "Generate an optimized AI image generation prompt based on this multi-modal information:",
        "compare_elements": "Compare and analyze the relationship between the text content and visual elements:"
    }

    @performance_monitor("multimodal_analysis")
    @cached_operation(ttl=300)
    def analyze_multimodal(self, text_input, image_description="", image_metadata="",
                          analysis_type="describe_scene", server_url="http://localhost:1234",
                          model="local-model", max_tokens=300, temperature=0.7,
                          include_technical_details=False, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(text_input, "text_input")
            if not validation["valid"]:
                return ("", "", "", f"Validation Error: {validation['error']}")
        
        try:
            # Build multi-modal context
            context_parts = [f"Text Content: {text_input}"]
            
            if image_description.strip():
                context_parts.append(f"Image Description: {image_description}")
            
            # Parse and include metadata
            metadata_dict = {}
            if image_metadata.strip():
                try:
                    metadata_dict = json.loads(image_metadata)
                    if isinstance(metadata_dict, dict):
                        metadata_summary = self._summarize_metadata(metadata_dict)
                        context_parts.append(f"Image Metadata: {metadata_summary}")
                except json.JSONDecodeError:
                    logger.warning("Invalid image_metadata JSON, ignoring")
            
            # Get analysis prompt
            system_prompt = self._ANALYSIS_PROMPTS.get(analysis_type, 
                                                     self._ANALYSIS_PROMPTS["describe_scene"])
            
            if include_technical_details:
                system_prompt += " Include technical details about composition, lighting, colors, and visual elements."
            
            # Combine context
            combined_context = "\n\n".join(context_parts)
            
            # Build multi-modal prompt for LLM
            multimodal_prompt = f"{system_prompt}\n\n{combined_context}"
            
            # Make API call to LM Studio
            analysis_result = ""
            if HAS_HTTPX or HAS_REQUESTS:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_context}
                ]
                
                analysis_result = self._call_llm_api(server_url, model, messages, max_tokens, temperature)
            else:
                analysis_result = f"Multi-modal analysis: {analysis_type}. Combined context ready for vision model processing."
            
            # Generate technical details
            technical_details = self._generate_technical_details(text_input, image_description, metadata_dict, analysis_type)
            
            # Create combined data structure
            combined_data = {
                "text_input": text_input,
                "image_description": image_description,
                "metadata": metadata_dict,
                "analysis_type": analysis_type,
                "multimodal_prompt": multimodal_prompt,
                "technical_analysis": technical_details
            }
            
            combined_data_json = json.dumps(combined_data, indent=2)
            
            return (analysis_result, multimodal_prompt, technical_details, combined_data_json)
            
        except Exception as e:
            error_msg = f"Multi-Modal Analysis Error: {str(e)}"
            logger.error(error_msg)
            return (error_msg, text_input, "", "")

    def _summarize_metadata(self, metadata: Dict) -> str:
        """Summarize image metadata for LLM context"""
        summary_parts = []
        
        # Common metadata fields
        if "width" in metadata and "height" in metadata:
            summary_parts.append(f"Dimensions: {metadata['width']}x{metadata['height']}")
        
        if "format" in metadata:
            summary_parts.append(f"Format: {metadata['format']}")
        
        if "file_size" in metadata:
            summary_parts.append(f"Size: {metadata['file_size']}")
        
        if "camera" in metadata:
            summary_parts.append(f"Camera: {metadata['camera']}")
        
        if "timestamp" in metadata:
            summary_parts.append(f"Timestamp: {metadata['timestamp']}")
        
        return ", ".join(summary_parts) if summary_parts else "No metadata available"

    def _call_llm_api(self, server_url: str, model: str, messages: List[Dict], 
                     max_tokens: int, temperature: float) -> str:
        """Call LM Studio API for analysis"""
        try:
            url = f"{server_url.rstrip('/')}/v1/chat/completions"
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            headers = {"Content-Type": "application/json"}
            
            if HAS_HTTPX:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
            elif HAS_REQUESTS:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                return "API call failed: No HTTP client available"
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "No response from LLM API"
                
        except Exception as e:
            return f"API Error: {str(e)}"

    def _generate_technical_details(self, text: str, image_desc: str, 
                                  metadata: Dict, analysis_type: str) -> str:
        """Generate technical analysis details"""
        details = []
        
        # Text analysis
        text_length = len(text)
        word_count = len(text.split())
        details.append(f"Text: {word_count} words, {text_length} characters")
        
        # Image analysis
        if image_desc:
            img_word_count = len(image_desc.split())
            details.append(f"Image description: {img_word_count} words")
        
        # Metadata analysis
        if metadata:
            metadata_fields = len(metadata)
            details.append(f"Metadata: {metadata_fields} fields")
        
        # Analysis type info
        details.append(f"Analysis type: {analysis_type}")
        
        return " | ".join(details)


class XDEV_LLMWorkflowController(ValidationMixin):
    """
    LLM Workflow Controller - Experimental node for LLM-driven ComfyUI workflow modification
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "workflow_description": ("STRING", {
                    "multiline": True,
                    "tooltip": "Natural language description of desired workflow changes"
                })
            },
            "optional": {
                "current_workflow": ("STRING", {
                    "multiline": True,
                    "default": "{}",
                    "tooltip": "Current workflow JSON (optional)"
                }),
                "available_nodes": ("STRING", {
                    "default": "KSampler,CLIPTextEncode,VAEDecode,CheckpointLoaderSimple",
                    "tooltip": "Available node types (comma-separated)"
                }),
                "control_mode": (["suggest_changes", "generate_workflow", "modify_existing", "analyze_description"], {
                    "default": "suggest_changes",
                    "tooltip": "How to process the workflow description"
                }),
                "server_url": ("STRING", {
                    "default": "http://localhost:1234",
                    "tooltip": "LM Studio server URL"
                }),
                "model": ("STRING", {
                    "default": "local-model",
                    "tooltip": "LLM model for workflow analysis"
                }),
                "max_tokens": ("INT", {
                    "default": 500, "min": 100, "max": 2000,
                    "tooltip": "Maximum tokens for workflow suggestions"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1,
                    "tooltip": "LLM creativity (lower = more structured)"
                }),
                "include_connections": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Include node connection suggestions"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("workflow_suggestions", "structured_plan", "node_analysis", "implementation_notes")
    FUNCTION = "control_workflow"
    CATEGORY = "XDev/LLM-Builder/Advanced"
    DESCRIPTION = "Experimental LLM-driven ComfyUI workflow control and modification"

    # System prompts for different control modes
    _CONTROL_PROMPTS = {
        "suggest_changes": """You are a ComfyUI workflow expert. Analyze the user's description and suggest specific workflow modifications. Focus on:
1. Required nodes and their configurations
2. Node connections and data flow
3. Parameter settings
4. Workflow optimization tips""",

        "generate_workflow": """You are a ComfyUI workflow generator. Create a complete workflow plan based on the user's description. Include:
1. List of required nodes in execution order
2. Node connections (input/output relationships)  
3. Recommended parameter values
4. Workflow structure and organization""",

        "modify_existing": """You are a ComfyUI workflow modifier. Analyze the existing workflow and the user's modification request. Provide:
1. Specific nodes to add, remove, or modify
2. New connections to establish
3. Parameter changes needed
4. Impact analysis of modifications""",

        "analyze_description": """You are a ComfyUI workflow analyst. Break down the user's description into technical requirements:
1. Identify the workflow goal and requirements
2. List required ComfyUI node types
3. Suggest workflow architecture
4. Highlight potential challenges or considerations"""
    }

    @performance_monitor("llm_workflow_controller")
    def control_workflow(self, workflow_description, current_workflow="{}", 
                        available_nodes="KSampler,CLIPTextEncode,VAEDecode,CheckpointLoaderSimple",
                        control_mode="suggest_changes", server_url="http://localhost:1234",
                        model="local-model", max_tokens=500, temperature=0.3,
                        include_connections=True, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(workflow_description, "workflow_description")
            if not validation["valid"]:
                return ("", "", "", f"Validation Error: {validation['error']}")
        
        try:
            # Parse available nodes
            node_list = [node.strip() for node in available_nodes.split(",") if node.strip()]
            
            # Parse current workflow if provided
            current_workflow_data = {}
            if current_workflow.strip() and current_workflow != "{}":
                try:
                    current_workflow_data = json.loads(current_workflow)
                except json.JSONDecodeError:
                    current_workflow_data = {"error": "Invalid workflow JSON"}
            
            # Build context for LLM
            context = self._build_workflow_context(workflow_description, current_workflow_data, 
                                                 node_list, control_mode, include_connections)
            
            # Get system prompt
            system_prompt = self._CONTROL_PROMPTS.get(control_mode, self._CONTROL_PROMPTS["suggest_changes"])
            
            # Make API call
            workflow_suggestions = ""
            if HAS_HTTPX or HAS_REQUESTS:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ]
                
                workflow_suggestions = self._call_workflow_api(server_url, model, messages, max_tokens, temperature)
            else:
                workflow_suggestions = self._generate_fallback_suggestions(workflow_description, node_list, control_mode)
            
            # Generate structured plan
            structured_plan = self._create_structured_plan(workflow_description, node_list, control_mode)
            
            # Analyze nodes
            node_analysis = self._analyze_node_requirements(workflow_description, node_list)
            
            # Implementation notes
            implementation_notes = self._generate_implementation_notes(workflow_description, control_mode, include_connections)
            
            return (workflow_suggestions, structured_plan, node_analysis, implementation_notes)
            
        except Exception as e:
            error_msg = f"Workflow Controller Error: {str(e)}"
            logger.error(error_msg)
            return (error_msg, "", "", "")

    def _build_workflow_context(self, description: str, current_workflow: Dict, 
                               node_list: List[str], control_mode: str, include_connections: bool) -> str:
        """Build context string for LLM analysis"""
        context_parts = [f"Workflow Description: {description}"]
        
        if node_list:
            context_parts.append(f"Available Nodes: {', '.join(node_list)}")
        
        if current_workflow and "error" not in current_workflow:
            workflow_summary = self._summarize_workflow(current_workflow)
            context_parts.append(f"Current Workflow: {workflow_summary}")
        
        context_parts.append(f"Control Mode: {control_mode}")
        
        if include_connections:
            context_parts.append("Please include specific node connection recommendations.")
        
        return "\n\n".join(context_parts)

    def _summarize_workflow(self, workflow_data: Dict) -> str:
        """Summarize existing workflow structure"""
        if not workflow_data:
            return "Empty workflow"
        
        node_count = len(workflow_data.get("nodes", {}))
        node_types = set()
        
        for node_data in workflow_data.get("nodes", {}).values():
            if isinstance(node_data, dict) and "class_type" in node_data:
                node_types.add(node_data["class_type"])
        
        return f"{node_count} nodes ({len(node_types)} types: {', '.join(list(node_types)[:5])})"

    def _call_workflow_api(self, server_url: str, model: str, messages: List[Dict],
                          max_tokens: int, temperature: float) -> str:
        """Call LM Studio API for workflow analysis"""
        try:
            url = f"{server_url.rstrip('/')}/v1/chat/completions"
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            headers = {"Content-Type": "application/json"}
            
            if HAS_HTTPX:
                with httpx.Client(timeout=45.0) as client:  # Longer timeout for complex analysis
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
            elif HAS_REQUESTS:
                response = requests.post(url, json=payload, headers=headers, timeout=45)
                response.raise_for_status()
                data = response.json()
            else:
                return "API call failed: No HTTP client available"
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "No response from LLM API"
                
        except Exception as e:
            return f"API Error: {str(e)}"

    def _generate_fallback_suggestions(self, description: str, node_list: List[str], control_mode: str) -> str:
        """Generate basic suggestions without LLM API"""
        description_lower = description.lower()
        suggestions = []
        
        # Basic keyword-based suggestions
        if "image" in description_lower or "generate" in description_lower:
            if "KSampler" in node_list:
                suggestions.append("- Use KSampler for image generation")
            if "VAEDecode" in node_list:
                suggestions.append("- Add VAEDecode to convert latents to images")
        
        if "prompt" in description_lower or "text" in description_lower:
            if "CLIPTextEncode" in node_list:
                suggestions.append("- Use CLIPTextEncode for text prompt processing")
        
        if "model" in description_lower or "checkpoint" in description_lower:
            if "CheckpointLoaderSimple" in node_list:
                suggestions.append("- Add CheckpointLoaderSimple to load the model")
        
        if not suggestions:
            suggestions = [f"- Analyze workflow requirements for: {description[:100]}..."]
        
        return f"Workflow Suggestions ({control_mode}):\n" + "\n".join(suggestions)

    def _create_structured_plan(self, description: str, node_list: List[str], control_mode: str) -> str:
        """Create a structured workflow plan"""
        plan_parts = [
            f"Workflow Plan: {control_mode}",
            f"Description: {description[:200]}..." if len(description) > 200 else f"Description: {description}",
            f"Available Nodes: {len(node_list)} types",
            "",
            "Execution Steps:",
            "1. Analyze workflow requirements",
            "2. Select appropriate nodes",
            "3. Configure node parameters", 
            "4. Establish node connections",
            "5. Test and optimize workflow"
        ]
        
        return "\n".join(plan_parts)

    def _analyze_node_requirements(self, description: str, node_list: List[str]) -> str:
        """Analyze which nodes might be needed"""
        description_lower = description.lower()
        required_nodes = []
        optional_nodes = []
        
        # Analysis based on keywords
        keyword_node_map = {
            "sample": ["KSampler", "AdvancedKSampler"],
            "encode": ["CLIPTextEncode", "VAEEncode"],
            "decode": ["VAEDecode"],
            "load": ["CheckpointLoaderSimple", "ModelLoader"],
            "control": ["ControlNet", "ControlNetApply"],
            "upscale": ["UpscaleModel", "ImageScale"],
            "save": ["SaveImage", "ImageSave"]
        }
        
        for keyword, nodes in keyword_node_map.items():
            if keyword in description_lower:
                for node in nodes:
                    if node in node_list:
                        required_nodes.append(node)
        
        analysis = f"Node Analysis:\n"
        analysis += f"Required: {', '.join(required_nodes) if required_nodes else 'None identified'}\n"
        analysis += f"Available: {', '.join(node_list[:10])}{'...' if len(node_list) > 10 else ''}\n"
        analysis += f"Total Available: {len(node_list)} node types"
        
        return analysis

    def _generate_implementation_notes(self, description: str, control_mode: str, include_connections: bool) -> str:
        """Generate implementation notes and warnings"""
        notes = [
            "Implementation Notes:",
            f"- Mode: {control_mode}",
            f"- Connections: {'Included' if include_connections else 'Basic only'}",
            "",
            "Important:",
            "- This is an experimental feature",
            "- Always validate generated workflows",
            "- Test workflows before production use",
            "- LLM suggestions may need manual refinement"
        ]
        
        if len(description) > 1000:
            notes.append("- Large description detected, may need chunking")
        
        return "\n".join(notes)
