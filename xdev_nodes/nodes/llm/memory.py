"""
XDev LLM-Builder Memory & Control Nodes
Advanced conversation management and control nodes
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from ...performance import performance_monitor, cached_operation
from ...mixins import ValidationMixin

logger = logging.getLogger(__name__)

# =============================================================================
# 🧠 MEMORY & CONTROL NODES
# =============================================================================

class XDEV_ConversationMemory(ValidationMixin):
    """
    Conversation Memory Node - Advanced conversation history management
    """
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "current_message": ("STRING", {
                    "multiline": True,
                    "tooltip": "Current message to add to conversation"
                }),
                "role": (["user", "assistant", "system"], {
                    "default": "user",
                    "tooltip": "Role of the current message"
                })
            },
            "optional": {
                "existing_history": ("STRING", {
                    "default": "[]",
                    "multiline": True,
                    "tooltip": "Existing conversation history as JSON array"
                }),
                "max_messages": ("INT", {
                    "default": 10, "min": 1, "max": 50,
                    "tooltip": "Maximum number of messages to keep"
                }),
                "max_tokens": ("INT", {
                    "default": 4000, "min": 100, "max": 16000,
                    "tooltip": "Maximum total tokens (approximate)"
                }),
                "truncation_strategy": (["oldest_first", "newest_first", "summarize_old"], {
                    "default": "oldest_first",
                    "tooltip": "How to handle memory overflow"
                }),
                "reset_memory": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reset conversation history (clear all)"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("updated_history", "conversation_summary", "memory_info")
    FUNCTION = "manage_memory"
    CATEGORY = "XDev/LLM-Builder/Memory"
    DESCRIPTION = "Advanced conversation memory management with truncation and summarization"

    @performance_monitor("conversation_memory")
    def manage_memory(self, current_message, role="user", existing_history="[]",
                     max_messages=10, max_tokens=4000, truncation_strategy="oldest_first",
                     reset_memory=False, validate_input=True):
        
        if validate_input:
            validation = self.validate_string_input(current_message, "current_message")
            if not validation["valid"]:
                return ("[]", "", f"Validation Error: {validation['error']}")
        
        try:
            # Reset memory if requested
            if reset_memory:
                new_history = [{"role": role, "content": current_message}]
                history_json = json.dumps(new_history, indent=2)
                summary = f"Memory reset. New conversation started with {role} message."
                info = f"Messages: 1, Reset: True"
                return (history_json, summary, info)
            
            # Parse existing history
            try:
                history = json.loads(existing_history) if existing_history.strip() else []
                if not isinstance(history, list):
                    history = []
            except json.JSONDecodeError:
                history = []
                logger.warning("Invalid existing_history JSON, starting fresh")
            
            # Add current message
            history.append({
                "role": role,
                "content": current_message,
                "timestamp": self._get_timestamp()
            })
            
            # Apply truncation if needed
            if len(history) > max_messages:
                history = self._truncate_by_messages(history, max_messages, truncation_strategy)
            
            # Check token count and truncate if needed
            estimated_tokens = self._estimate_tokens(history)
            if estimated_tokens > max_tokens:
                history = self._truncate_by_tokens(history, max_tokens, truncation_strategy)
            
            # Generate summary
            summary = self._generate_summary(history)
            
            # Memory info
            final_tokens = self._estimate_tokens(history)
            info = f"Messages: {len(history)}, Est. tokens: {final_tokens}, Strategy: {truncation_strategy}"
            
            # Return updated history
            history_json = json.dumps(history, indent=2)
            
            return (history_json, summary, info)
            
        except Exception as e:
            error_msg = f"Memory Management Error: {str(e)}"
            logger.error(error_msg)
            return (existing_history, "", error_msg)

    def _get_timestamp(self) -> str:
        """Get current timestamp for message tracking"""
        import datetime
        return datetime.datetime.now().isoformat()

    def _truncate_by_messages(self, history: List[Dict], max_messages: int, strategy: str) -> List[Dict]:
        """Truncate conversation by message count"""
        if strategy == "oldest_first":
            return history[-max_messages:]
        elif strategy == "newest_first":
            return history[:max_messages]
        else:  # summarize_old
            # Keep most recent messages, summarize the rest
            if len(history) <= max_messages:
                return history
            
            old_messages = history[:-max_messages]
            recent_messages = history[-max_messages:]
            
            # Create summary of old messages
            summary_content = self._create_summary(old_messages)
            summary_message = {
                "role": "system",
                "content": f"[Conversation Summary]: {summary_content}",
                "timestamp": self._get_timestamp()
            }
            
            return [summary_message] + recent_messages

    def _truncate_by_tokens(self, history: List[Dict], max_tokens: int, strategy: str) -> List[Dict]:
        """Truncate conversation by estimated token count"""
        current_tokens = self._estimate_tokens(history)
        
        if current_tokens <= max_tokens:
            return history
        
        if strategy == "oldest_first":
            # Remove oldest messages until under limit
            while len(history) > 1 and self._estimate_tokens(history) > max_tokens:
                history.pop(0)
        elif strategy == "newest_first":
            # Remove newest messages until under limit
            while len(history) > 1 and self._estimate_tokens(history) > max_tokens:
                history.pop()
        else:  # summarize_old
            # Summarize older messages
            target_messages = max(3, len(history) // 2)  # Keep at least 3 recent messages
            
            while len(history) > target_messages and self._estimate_tokens(history) > max_tokens:
                old_messages = history[:len(history)//2]
                recent_messages = history[len(history)//2:]
                
                summary_content = self._create_summary(old_messages)
                summary_message = {
                    "role": "system", 
                    "content": f"[Summary]: {summary_content}",
                    "timestamp": self._get_timestamp()
                }
                
                history = [summary_message] + recent_messages
                
                # Prevent infinite loop
                if len(recent_messages) <= 1:
                    break
        
        return history

    def _estimate_tokens(self, history: List[Dict]) -> int:
        """Estimate token count (rough approximation: 4 chars = 1 token)"""
        total_chars = 0
        for message in history:
            total_chars += len(message.get("content", ""))
        return total_chars // 4

    def _create_summary(self, messages: List[Dict]) -> str:
        """Create a summary of message history"""
        if not messages:
            return "No messages to summarize."
        
        user_messages = [m for m in messages if m.get("role") == "user"]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"]
        
        summary_parts = []
        
        if user_messages:
            summary_parts.append(f"User discussed: {len(user_messages)} topics")
        if assistant_messages:
            summary_parts.append(f"Assistant provided {len(assistant_messages)} responses")
        
        return f"Conversation with {len(messages)} messages. " + ", ".join(summary_parts)

    def _generate_summary(self, history: List[Dict]) -> str:
        """Generate a human-readable conversation summary"""
        if not history:
            return "Empty conversation"
        
        message_count = len(history)
        roles = [msg.get("role", "unknown") for msg in history]
        role_counts = {role: roles.count(role) for role in set(roles)}
        
        latest_message = history[-1]
        latest_role = latest_message.get("role", "unknown")
        latest_preview = latest_message.get("content", "")[:50] + "..." if len(latest_message.get("content", "")) > 50 else latest_message.get("content", "")
        
        summary = f"Conversation: {message_count} messages. "
        for role, count in role_counts.items():
            summary += f"{role.title()}: {count}, "
        
        summary = summary.rstrip(", ") + f". Latest ({latest_role}): {latest_preview}"
        
        return summary


class XDEV_PersonaSystemMessage(ValidationMixin):
    """
    Persona / System Message Node - Dynamic AI persona and system instruction builder
    """
    
    # Predefined persona templates
    _PERSONA_TEMPLATES = {
        "creative_assistant": {
            "name": "Creative Assistant",
            "system_message": "You are a highly creative and imaginative AI assistant specialized in artistic and creative tasks. You excel at generating vivid descriptions, creative writing, and innovative ideas. Your responses are expressive, detailed, and inspiring.",
            "traits": ["creative", "imaginative", "expressive", "inspiring"]
        },
        "technical_expert": {
            "name": "Technical Expert", 
            "system_message": "You are a technical expert AI with deep knowledge across programming, engineering, and scientific domains. You provide precise, accurate, and well-structured technical information. Your responses are clear, methodical, and backed by expertise.",
            "traits": ["precise", "analytical", "methodical", "expert"]
        },
        "friendly_helper": {
            "name": "Friendly Helper",
            "system_message": "You are a warm, friendly, and helpful AI assistant. You approach every interaction with kindness, patience, and enthusiasm to help. Your tone is conversational, supportive, and encouraging.",
            "traits": ["warm", "friendly", "supportive", "patient"]
        },
        "professional_advisor": {
            "name": "Professional Advisor",
            "system_message": "You are a professional business and strategic advisor AI. You provide well-reasoned advice, strategic insights, and professional guidance. Your communication is formal, structured, and results-oriented.",
            "traits": ["professional", "strategic", "formal", "results-oriented"]
        },
        "artistic_mentor": {
            "name": "Artistic Mentor",
            "system_message": "You are an experienced artistic mentor with expertise in visual arts, design principles, and creative processes. You guide others in developing their artistic vision and technical skills with patience and insight.",
            "traits": ["artistic", "experienced", "patient", "insightful"]
        },
        "custom": {
            "name": "Custom Persona",
            "system_message": "Define your own custom persona and system instructions.",
            "traits": ["customizable"]
        }
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        persona_names = list(cls._PERSONA_TEMPLATES.keys())
        
        return {
            "required": {
                "persona_type": (persona_names, {
                    "default": "creative_assistant",
                    "tooltip": "Select a predefined persona or choose 'custom'"
                })
            },
            "optional": {
                "custom_system_message": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Custom system message (used when persona_type='custom')"
                }),
                "task_context": ("STRING", {
                    "default": "",
                    "tooltip": "Specific task context to add to system message"
                }),
                "personality_traits": ("STRING", {
                    "default": "",
                    "tooltip": "Additional personality traits (comma-separated)"
                }),
                "domain_expertise": ("STRING", {
                    "default": "",
                    "tooltip": "Domain expertise to emphasize (e.g., 'photography', 'writing')"
                }),
                "response_style": (["conversational", "formal", "creative", "technical", "friendly"], {
                    "default": "conversational", 
                    "tooltip": "Preferred response style"
                }),
                "output_format": (["system_message", "full_persona_json"], {
                    "default": "system_message",
                    "tooltip": "Output format: just system message or full persona data"
                }),
                "validate_input": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable input validation"
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("system_message", "persona_info", "persona_data")
    FUNCTION = "build_persona"
    CATEGORY = "XDev/LLM-Builder/Memory"
    DESCRIPTION = "Dynamic AI persona and system message builder with templates"

    @performance_monitor("persona_system_message")
    def build_persona(self, persona_type="creative_assistant", custom_system_message="",
                     task_context="", personality_traits="", domain_expertise="",
                     response_style="conversational", output_format="system_message", 
                     validate_input=True):
        
        try:
            # Get base persona
            if persona_type == "custom" and custom_system_message.strip():
                base_system_message = custom_system_message.strip()
                persona_name = "Custom Persona"
                base_traits = []
            else:
                persona_template = self._PERSONA_TEMPLATES.get(persona_type, self._PERSONA_TEMPLATES["creative_assistant"])
                base_system_message = persona_template["system_message"]
                persona_name = persona_template["name"]
                base_traits = persona_template["traits"].copy()
            
            # Build enhanced system message
            system_message_parts = [base_system_message]
            
            # Add task context
            if task_context.strip():
                system_message_parts.append(f"Task Context: {task_context.strip()}")
            
            # Add domain expertise
            if domain_expertise.strip():
                system_message_parts.append(f"You have specialized expertise in {domain_expertise.strip()}.")
            
            # Add personality traits
            if personality_traits.strip():
                traits_list = [t.strip() for t in personality_traits.split(",") if t.strip()]
                if traits_list:
                    system_message_parts.append(f"Additional traits: You are {', '.join(traits_list)}.")
            
            # Add response style guidance
            style_guidance = self._get_style_guidance(response_style)
            if style_guidance:
                system_message_parts.append(style_guidance)
            
            # Combine system message
            final_system_message = " ".join(system_message_parts)
            
            # Build persona info
            all_traits = base_traits.copy()
            if personality_traits.strip():
                additional_traits = [t.strip() for t in personality_traits.split(",") if t.strip()]
                all_traits.extend(additional_traits)
            
            persona_info = f"Persona: {persona_name}, Style: {response_style}, Traits: {', '.join(all_traits)}"
            
            # Build persona data (JSON)
            persona_data_dict = {
                "persona_name": persona_name,
                "persona_type": persona_type,
                "system_message": final_system_message,
                "response_style": response_style,
                "traits": all_traits,
                "task_context": task_context,
                "domain_expertise": domain_expertise
            }
            
            persona_data = json.dumps(persona_data_dict, indent=2)
            
            # Return based on output format
            if output_format == "full_persona_json":
                return (persona_data, persona_info, persona_data)
            else:
                return (final_system_message, persona_info, persona_data)
            
        except Exception as e:
            error_msg = f"Persona Builder Error: {str(e)}"
            logger.error(error_msg)
            default_message = "You are a helpful AI assistant."
            return (default_message, error_msg, "{}")

    def _get_style_guidance(self, response_style: str) -> str:
        """Get response style guidance text"""
        style_guidance = {
            "conversational": "Use a natural, conversational tone that feels like talking with a knowledgeable friend.",
            "formal": "Maintain a professional, formal tone appropriate for business or academic contexts.",
            "creative": "Express yourself with creativity, using vivid language and imaginative descriptions.",
            "technical": "Focus on precision and clarity, using appropriate technical terminology when needed.",
            "friendly": "Be warm, approachable, and encouraging in all your communications."
        }
        
        return style_guidance.get(response_style, "")
