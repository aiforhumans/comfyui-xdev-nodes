"""LM Studio Parameter Presets Node

Quick access to common parameter configurations.
"""

try:
    from .lm_base_node import LMStudioUtilityBaseNode
except ImportError:
    from lm_base_node import LMStudioUtilityBaseNode

from typing import Any, Dict, Tuple


class LMStudioParameterPresets(LMStudioUtilityBaseNode):
    """Manage and apply parameter presets for different use cases."""

    # Preset configurations
    PRESETS = {
        "creative": {
            "temperature": 0.9,
            "top_p": 0.95,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
            "description": "High creativity, diverse outputs"
        },
        "balanced": {
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "description": "Balanced creativity and coherence"
        },
        "precise": {
            "temperature": 0.3,
            "top_p": 0.8,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "description": "Focused, deterministic outputs"
        },
        "factual": {
            "temperature": 0.1,
            "top_p": 0.7,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "description": "Very focused, factual responses"
        },
        "diverse": {
            "temperature": 0.8,
            "top_p": 0.95,
            "frequency_penalty": 1.0,
            "presence_penalty": 1.0,
            "description": "Maximum diversity, avoid repetition"
        },
        "conversational": {
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.3,
            "description": "Natural conversation style"
        },
        "analytical": {
            "temperature": 0.4,
            "top_p": 0.85,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.2,
            "description": "Analytical, structured responses"
        },
        "storytelling": {
            "temperature": 0.85,
            "top_p": 0.95,
            "frequency_penalty": 0.4,
            "presence_penalty": 0.6,
            "description": "Engaging narratives with variety"
        },
        "custom": {
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "description": "Use manual parameter inputs"
        }
    }

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input parameters."""
        preset_names = list(cls.PRESETS.keys())
        
        return {
            "required": {
                "preset": (preset_names, {"default": "balanced"}),
            },
            "optional": {
                "temperature_override": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 2.0, "step": 0.1, "tooltip": "Override preset (-1 = use preset)"}),
                "top_p_override": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.05, "tooltip": "Override preset (-1 = use preset)"}),
                "frequency_penalty_override": ("FLOAT", {"default": -999.0, "min": -999.0, "max": 2.0, "step": 0.1, "tooltip": "Override preset (-999 = use preset)"}),
                "presence_penalty_override": ("FLOAT", {"default": -999.0, "min": -999.0, "max": 2.0, "step": 0.1, "tooltip": "Override preset (-999 = use preset)"}),
            }
        }

    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("temperature", "top_p", "frequency_penalty", "presence_penalty", "info")
    FUNCTION = "apply_preset"

    def apply_preset(
        self,
        preset: str,
        temperature_override: float = -1.0,
        top_p_override: float = -1.0,
        frequency_penalty_override: float = -999.0,
        presence_penalty_override: float = -999.0
    ) -> Tuple[float, float, float, float, str]:
        """Apply parameter preset with optional overrides."""
        
        info_parts = self._init_info("Parameter Presets", "🎛️")
        
        # Get preset config
        config = self.PRESETS.get(preset, self.PRESETS["balanced"])
        info_parts.append(f"📋 Preset: {preset}")
        info_parts.append(f"📝 {config['description']}")
        info_parts.append("─" * 28)
        
        # Apply preset values
        temperature = config["temperature"]
        top_p = config["top_p"]
        frequency_penalty = config["frequency_penalty"]
        presence_penalty = config["presence_penalty"]
        
        # Apply overrides
        overrides = []
        if temperature_override >= 0.0:
            temperature = temperature_override
            overrides.append("temperature")
        if top_p_override >= 0.0:
            top_p = top_p_override
            overrides.append("top_p")
        if frequency_penalty_override > -999.0:
            frequency_penalty = frequency_penalty_override
            overrides.append("frequency_penalty")
        if presence_penalty_override > -999.0:
            presence_penalty = presence_penalty_override
            overrides.append("presence_penalty")
        
        # Display parameters
        info_parts.append(f"🌡️ Temperature: {temperature}")
        info_parts.append(f"🎯 Top P: {top_p}")
        info_parts.append(f"🔁 Freq Penalty: {frequency_penalty}")
        info_parts.append(f"🆕 Presence Penalty: {presence_penalty}")
        
        if overrides:
            info_parts.append("─" * 28)
            info_parts.append(f"⚙️ Overrides: {', '.join(overrides)}")
        
        info_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Add usage tips
        tips = []
        if temperature > 0.8:
            tips.append("💡 High temp = more creative/random")
        elif temperature < 0.4:
            tips.append("💡 Low temp = more focused/deterministic")
        
        if frequency_penalty > 0.5:
            tips.append("💡 High freq penalty = less repetition")
        
        if presence_penalty > 0.5:
            tips.append("💡 High presence penalty = more topic diversity")
        
        return (temperature, top_p, frequency_penalty, presence_penalty, self._format_info(info_parts))


__all__ = ["LMStudioParameterPresets"]
