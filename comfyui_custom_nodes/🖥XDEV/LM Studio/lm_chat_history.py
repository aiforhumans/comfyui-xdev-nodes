"""LM Studio Chat History Manager Node

Maintains conversation context across workflow execution.
"""

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode

import json
from typing import Any

# Global storage for chat histories (keyed by session_id)
CHAT_HISTORIES: dict[str, list[dict[str, str]]] = {}


class LMStudioChatHistory(LMStudioUtilityBaseNode):
    """Manage conversation history for stateful chat interactions."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "session_id": ("STRING", {"default": "default", "tooltip": "Unique identifier for this conversation"}),
                "role": (["user", "assistant", "system"], {"default": "user"}),
                "message": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "reset_history": ("BOOLEAN", {"default": False, "tooltip": "Clear history and start fresh"}),
                "max_messages": ("INT", {"default": 20, "min": 1, "max": 100, "tooltip": "Maximum messages to keep"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("messages_json", "formatted_history", "info")
    FUNCTION = "manage_history"

    @classmethod
    def IS_CHANGED(cls, session_id: str, **kwargs) -> float:
        """Always execute to maintain stateful behavior."""
        import time
        return time.time()

    def manage_history(
        self,
        session_id: str,
        role: str,
        message: str,
        reset_history: bool = False,
        max_messages: int = 20
    ) -> tuple[str, str, str]:
        """Manage chat history with automatic truncation."""
        
        info_parts = self._init_info("Chat History Manager", "💬")
        info_parts.append(f"📌 Session: {session_id}")
        
        # Reset if requested
        if reset_history:
            CHAT_HISTORIES[session_id] = []
            info_parts.append("🔄 History reset")
        
        # Initialize history if needed
        if session_id not in CHAT_HISTORIES:
            CHAT_HISTORIES[session_id] = []
        
        # Add new message if provided
        if message.strip():
            CHAT_HISTORIES[session_id].append({
                "role": role,
                "content": message.strip()
            })
            info_parts.append(f"➕ Added {role} message")
        
        # Truncate to max messages (keep system messages)
        history = CHAT_HISTORIES[session_id]
        if len(history) > max_messages:
            # Separate system messages from others
            system_msgs = [m for m in history if m["role"] == "system"]
            other_msgs = [m for m in history if m["role"] != "system"]
            
            # Keep all system messages + recent other messages
            available_slots = max_messages - len(system_msgs)
            if available_slots > 0:
                recent_msgs = other_msgs[-available_slots:]
            else:
                recent_msgs = []
            
            CHAT_HISTORIES[session_id] = system_msgs + recent_msgs
            info_parts.append(f"✂️ Truncated to {len(CHAT_HISTORIES[session_id])} msgs")
        
        # Get current history
        current_history = CHAT_HISTORIES[session_id]
        
        # Format as JSON for API
        messages_json = json.dumps(current_history, indent=2)
        
        # Format as readable text
        formatted = ""
        for i, msg in enumerate(current_history, 1):
            role_emoji = {"system": "⚙️", "user": "👤", "assistant": "🤖"}.get(msg["role"], "💬")
            formatted += f"{role_emoji} {msg['role'].upper()}\n"
            formatted += f"{msg['content']}\n"
            if i < len(current_history):
                formatted += "\n" + "─" * 40 + "\n\n"
        
        # Stats
        msg_count = len(current_history)
        total_chars = sum(len(m["content"]) for m in current_history)
        info_parts.append(f"📊 Messages: {msg_count}/{max_messages}")
        info_parts.append(f"📝 Total: {total_chars} chars")
        
        return (messages_json, formatted, self._format_info(info_parts))


class LMStudioChatHistoryLoader(LMStudioUtilityBaseNode):
    """Load existing chat history for use in text generation."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters."""
        return {
            "required": {
                "session_id": ("STRING", {"default": "default"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("messages_json",)
    FUNCTION = "load_history"

    @classmethod
    def IS_CHANGED(cls, session_id: str) -> float:
        """Always execute to get latest history."""
        import time
        return time.time()

    def load_history(self, session_id: str) -> tuple[str]:
        """Load chat history as JSON."""
        history = CHAT_HISTORIES.get(session_id, [])
        messages_json = json.dumps(history, indent=2)
        return (messages_json,)


__all__ = ["LMStudioChatHistory", "LMStudioChatHistoryLoader"]
