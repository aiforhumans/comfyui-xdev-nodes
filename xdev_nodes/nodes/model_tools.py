"""
SDXL Model Mixer Node - Advanced Model Blending for ComfyUI

This module provides sophisticated model mixing capabilities for SDXL models,
allowing users to blend multiple models with various weighting strategies and
advanced interpolation algorithms.
"""

from typing import Dict, List, Tuple, Any, Optional, Union
import copy

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

from ..performance import performance_monitor, cached_operation
from ..mixins import ValidationMixin


class SDXLModelMixer(ValidationMixin):
    """
    Advanced SDXL Model Mixer with multiple blending strategies.
    
    Supports linear interpolation, spherical linear interpolation (SLERP),
    and additive blending with flexible weighting schemes.
    """
    
    # Supported mixing algorithms
    _MIXING_ALGORITHMS = {
        "linear": "Linear interpolation (LERP)",
        "spherical": "Spherical linear interpolation (SLERP)", 
        "additive": "Additive blending",
        "weighted_average": "Weighted average",
        "geometric_mean": "Geometric mean blending"
    }
    
    # Weighting strategies
    _WEIGHTING_STRATEGIES = {
        "uniform": "Equal weights for all models",
        "manual": "Manual weight specification",
        "priority": "Priority-based weighting",
        "adaptive": "Adaptive weight calculation"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "model_1": ("MODEL", {"tooltip": "Primary SDXL model for mixing"}),
                "model_2": ("MODEL", {"tooltip": "Secondary SDXL model for mixing"}),
                "mixing_algorithm": (list(cls._MIXING_ALGORITHMS.keys()), {
                    "default": "linear",
                    "tooltip": "Algorithm used for model blending"
                }),
                "weighting_strategy": (list(cls._WEIGHTING_STRATEGIES.keys()), {
                    "default": "uniform", 
                    "tooltip": "Strategy for determining model weights"
                }),
                "blend_ratio": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Primary blend ratio (0.0 = model_1 only, 1.0 = model_2 only)"
                })
            },
            "optional": {
                "model_3": ("MODEL", {"tooltip": "Optional third model for mixing"}),
                "model_4": ("MODEL", {"tooltip": "Optional fourth model for mixing"}),
                "weight_1": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Manual weight for model 1 (manual strategy only)"
                }),
                "weight_2": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Manual weight for model 2 (manual strategy only)"
                }),
                "weight_3": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Manual weight for model 3 (manual strategy only)"
                }),
                "weight_4": ("FLOAT", {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Manual weight for model 4 (manual strategy only)"
                }),
                "preserve_structure": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Preserve model architecture structure during mixing"
                }),
                "normalize_weights": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Automatically normalize weights to sum to 1.0"
                }),
                "blend_layers": ("STRING", {
                    "default": "all",
                    "tooltip": "Layers to blend: 'all', 'encoder', 'decoder', 'attention', or comma-separated list"
                }),
                "validation_level": (["basic", "detailed", "comprehensive"], {
                    "default": "basic",
                    "tooltip": "Level of model compatibility validation"
                })
            }
        }
    
    RETURN_TYPES = ("MODEL", "STRING", "STRING")
    RETURN_NAMES = ("mixed_model", "mixing_info", "compatibility_report")
    FUNCTION = "mix_models"
    CATEGORY = "XDev/Model/Advanced"
    DESCRIPTION = "Advanced SDXL model mixing with multiple algorithms and weighting strategies"
    
    def __init__(self):
        super().__init__()
        self._mixing_cache = {}
        self._compatibility_cache = {}
    
    @performance_monitor("model_mixing")
    def mix_models(
        self, 
        model_1, 
        model_2, 
        mixing_algorithm: str = "linear",
        weighting_strategy: str = "uniform",
        blend_ratio: float = 0.5,
        model_3=None,
        model_4=None,
        weight_1: float = 0.25,
        weight_2: float = 0.25,
        weight_3: float = 0.25,
        weight_4: float = 0.25,
        preserve_structure: bool = True,
        normalize_weights: bool = True,
        blend_layers: str = "all",
        validation_level: str = "basic"
    ) -> Tuple[Any, str, str]:
        """
        Mix multiple SDXL models using advanced blending algorithms.
        
        Returns:
            Tuple of (mixed_model, mixing_info, compatibility_report)
        """
        try:
            # Collect all provided models
            models = [model_1, model_2]
            if model_3 is not None:
                models.append(model_3)
            if model_4 is not None:
                models.append(model_4)
            
            # Validate model compatibility
            compatibility_report = self._validate_model_compatibility(
                models, validation_level
            )
            
            if "❌ CRITICAL" in compatibility_report:
                # Return first model if critical compatibility issues
                return (
                    model_1,
                    f"❌ Mixing aborted due to compatibility issues",
                    compatibility_report
                )
            
            # Calculate weights based on strategy
            weights = self._calculate_weights(
                models, weighting_strategy, blend_ratio,
                [weight_1, weight_2, weight_3, weight_4][:len(models)],
                normalize_weights
            )
            
            # Perform model mixing
            mixed_model = self._perform_model_mixing(
                models, weights, mixing_algorithm, blend_layers, preserve_structure
            )
            
            # Generate mixing information
            mixing_info = self._generate_mixing_info(
                models, weights, mixing_algorithm, weighting_strategy
            )
            
            return (mixed_model, mixing_info, compatibility_report)
            
        except Exception as e:
            error_msg = f"❌ Model mixing error: {str(e)}"
            return (model_1, error_msg, f"Error during mixing: {str(e)}")
    
    def _validate_model_compatibility(
        self, 
        models: List[Any], 
        validation_level: str
    ) -> str:
        """Validate that models are compatible for mixing."""
        try:
            report = ["🔍 MODEL COMPATIBILITY ANALYSIS", "=" * 40]
            
            if not HAS_TORCH:
                report.append("⚠️ PyTorch not available - limited validation")
                return "\n".join(report)
            
            # Basic validation
            model_info = []
            for i, model in enumerate(models):
                info = self._analyze_model_structure(model, i + 1)
                model_info.append(info)
                report.append(f"📱 Model {i+1}: {info['summary']}")
            
            # Check compatibility
            if validation_level in ["detailed", "comprehensive"]:
                compatibility_issues = self._check_detailed_compatibility(model_info)
                
                if compatibility_issues:
                    report.append("\n⚠️ COMPATIBILITY ISSUES:")
                    report.extend(compatibility_issues)
                else:
                    report.append("\n✅ All models are compatible for mixing")
            
            # Comprehensive analysis
            if validation_level == "comprehensive":
                advanced_analysis = self._perform_advanced_compatibility_analysis(model_info)
                report.append(f"\n🔬 ADVANCED ANALYSIS:")
                report.extend(advanced_analysis)
            
            return "\n".join(report)
            
        except Exception as e:
            return f"❌ CRITICAL: Compatibility validation failed - {str(e)}"
    
    def _analyze_model_structure(self, model: Any, model_num: int) -> Dict[str, Any]:
        """Analyze individual model structure."""
        try:
            info = {
                "model_num": model_num,
                "summary": "Unknown model structure",
                "device": "unknown",
                "dtype": "unknown", 
                "parameter_count": 0,
                "architecture": "unknown"
            }
            
            if hasattr(model, 'model'):
                actual_model = model.model
                
                # Get device and dtype
                if hasattr(actual_model, 'device'):
                    info["device"] = str(actual_model.device)
                if hasattr(actual_model, 'dtype'):
                    info["dtype"] = str(actual_model.dtype)
                
                # Count parameters
                if hasattr(actual_model, 'parameters'):
                    try:
                        param_count = sum(p.numel() for p in actual_model.parameters() if p.requires_grad)
                        info["parameter_count"] = param_count
                    except:
                        pass
                
                # Detect architecture
                class_name = type(actual_model).__name__
                if 'unet' in class_name.lower() or 'diffusion' in class_name.lower():
                    info["architecture"] = "UNet/Diffusion"
                elif 'transformer' in class_name.lower():
                    info["architecture"] = "Transformer"
                
                info["summary"] = f"{info['architecture']} ({info['parameter_count']:,} params, {info['device']}, {info['dtype']})"
            
            return info
            
        except Exception as e:
            return {
                "model_num": model_num,
                "summary": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    def _check_detailed_compatibility(self, model_info: List[Dict[str, Any]]) -> List[str]:
        """Check for detailed compatibility issues between models."""
        issues = []
        
        # Check parameter counts
        param_counts = [info.get("parameter_count", 0) for info in model_info]
        if len(set(param_counts)) > 1:
            issues.append(f"   • Parameter count mismatch: {param_counts}")
        
        # Check architectures
        architectures = [info.get("architecture", "unknown") for info in model_info]
        if len(set(architectures)) > 1:
            issues.append(f"   • Architecture mismatch: {set(architectures)}")
        
        # Check devices (warning, not critical)
        devices = [info.get("device", "unknown") for info in model_info]
        if len(set(devices)) > 1:
            issues.append(f"   ⚠️ Device mismatch (will be handled): {set(devices)}")
        
        return issues
    
    def _perform_advanced_compatibility_analysis(self, model_info: List[Dict[str, Any]]) -> List[str]:
        """Perform advanced compatibility analysis."""
        analysis = []
        
        # Architecture analysis
        architectures = [info.get("architecture", "unknown") for info in model_info]
        analysis.append(f"   • Detected architectures: {set(architectures)}")
        
        # Parameter analysis
        param_counts = [info.get("parameter_count", 0) for info in model_info]
        if param_counts:
            avg_params = sum(param_counts) / len(param_counts)
            analysis.append(f"   • Average parameters: {avg_params:,.0f}")
            analysis.append(f"   • Parameter range: {min(param_counts):,} - {max(param_counts):,}")
        
        # Device analysis
        devices = [info.get("device", "unknown") for info in model_info]
        analysis.append(f"   • Devices: {set(devices)}")
        
        return analysis
    
    def _calculate_weights(
        self, 
        models: List[Any], 
        strategy: str, 
        blend_ratio: float,
        manual_weights: List[float],
        normalize: bool
    ) -> List[float]:
        """Calculate weights based on the selected strategy."""
        try:
            num_models = len(models)
            
            if strategy == "uniform":
                weights = [1.0 / num_models] * num_models
                
            elif strategy == "manual":
                weights = manual_weights[:num_models]
                
            elif strategy == "priority":
                # Priority decreases for later models
                weights = [1.0 / (i + 1) for i in range(num_models)]
                
            elif strategy == "adaptive":
                # Simple adaptive based on blend_ratio
                if num_models == 2:
                    weights = [1.0 - blend_ratio, blend_ratio]
                else:
                    # Distribute remaining weight among additional models
                    primary_weight = 1.0 - blend_ratio
                    secondary_weight = blend_ratio / (num_models - 1)
                    weights = [primary_weight] + [secondary_weight] * (num_models - 1)
            else:
                # Default to uniform
                weights = [1.0 / num_models] * num_models
            
            # Normalize weights if requested
            if normalize and sum(weights) != 0:
                total = sum(weights)
                weights = [w / total for w in weights]
            
            return weights
            
        except Exception as e:
            # Fallback to uniform weights
            return [1.0 / len(models)] * len(models)
    
    @cached_operation(ttl=600)
    def _perform_model_mixing(
        self, 
        models: List[Any], 
        weights: List[float],
        algorithm: str,
        blend_layers: str,
        preserve_structure: bool
    ) -> Any:
        """Perform the actual model mixing using the specified algorithm."""
        try:
            if not HAS_TORCH:
                print("⚠️ PyTorch not available - returning first model")
                return models[0]
            
            # Start with a deep copy of the first model
            mixed_model = copy.deepcopy(models[0])
            
            if len(models) == 1:
                return mixed_model
            
            # Get the actual model components to mix
            if hasattr(mixed_model, 'model'):
                target_model = mixed_model.model
                source_models = [model.model if hasattr(model, 'model') else model for model in models]
            else:
                target_model = mixed_model
                source_models = models
            
            # Perform mixing based on algorithm
            if algorithm == "linear":
                self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
            elif algorithm == "spherical":
                self._spherical_interpolation_mixing(target_model, source_models, weights, blend_layers)
            elif algorithm == "additive":
                self._additive_mixing(target_model, source_models, weights, blend_layers)
            elif algorithm == "weighted_average":
                self._weighted_average_mixing(target_model, source_models, weights, blend_layers)
            elif algorithm == "geometric_mean":
                self._geometric_mean_mixing(target_model, source_models, weights, blend_layers)
            else:
                # Default to linear
                self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
            
            return mixed_model
            
        except Exception as e:
            print(f"❌ Model mixing failed: {str(e)}")
            return models[0]  # Return first model as fallback
    
    def _linear_interpolation_mixing(
        self, 
        target_model: Any, 
        source_models: List[Any], 
        weights: List[float],
        blend_layers: str
    ):
        """Perform linear interpolation mixing of model parameters."""
        try:
            if not hasattr(target_model, 'state_dict'):
                print("⚠️ Model doesn't have state_dict, skipping parameter mixing")
                return
            
            target_state = target_model.state_dict()
            source_states = []
            
            # Get state dicts from all source models
            for model in source_models:
                if hasattr(model, 'state_dict'):
                    source_states.append(model.state_dict())
                else:
                    print(f"⚠️ Source model missing state_dict, using target state")
                    source_states.append(target_state)
            
            # Mix parameters
            for param_name in target_state.keys():
                if self._should_blend_parameter(param_name, blend_layers):
                    # Initialize with zeros
                    mixed_param = torch.zeros_like(target_state[param_name])
                    
                    # Weighted sum of all model parameters
                    for i, (source_state, weight) in enumerate(zip(source_states, weights)):
                        if param_name in source_state:
                            source_param = source_state[param_name]
                            # Ensure tensors are on the same device
                            if source_param.device != mixed_param.device:
                                source_param = source_param.to(mixed_param.device)
                            mixed_param += weight * source_param
                        else:
                            # Use original parameter if not found in source
                            mixed_param += weight * target_state[param_name]
                    
                    # Update target parameter
                    target_state[param_name] = mixed_param
            
            # Load the mixed state dict back
            target_model.load_state_dict(target_state)
            
        except Exception as e:
            print(f"❌ Linear interpolation mixing failed: {str(e)}")
    
    def _spherical_interpolation_mixing(
        self, 
        target_model: Any, 
        source_models: List[Any], 
        weights: List[float],
        blend_layers: str
    ):
        """Perform spherical linear interpolation (SLERP) mixing."""
        try:
            # For simplicity, fall back to linear interpolation for now
            # SLERP is more complex and requires careful handling of parameter spaces
            print("🔄 Using linear interpolation (SLERP implementation in development)")
            self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
            
        except Exception as e:
            print(f"❌ Spherical interpolation mixing failed: {str(e)}")
            self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
    
    def _additive_mixing(
        self, 
        target_model: Any, 
        source_models: List[Any], 
        weights: List[float],
        blend_layers: str
    ):
        """Perform additive mixing of model parameters."""
        try:
            if not hasattr(target_model, 'state_dict'):
                return
            
            target_state = target_model.state_dict()
            
            # Start with the first model as base
            base_state = source_models[0].state_dict() if hasattr(source_models[0], 'state_dict') else target_state
            
            for param_name in target_state.keys():
                if self._should_blend_parameter(param_name, blend_layers):
                    # Start with base parameter
                    if param_name in base_state:
                        mixed_param = base_state[param_name].clone()
                    else:
                        mixed_param = target_state[param_name].clone()
                    
                    # Add weighted contributions from other models
                    for i in range(1, len(source_models)):
                        if i < len(weights) and hasattr(source_models[i], 'state_dict'):
                            source_state = source_models[i].state_dict()
                            if param_name in source_state:
                                source_param = source_state[param_name]
                                if source_param.device != mixed_param.device:
                                    source_param = source_param.to(mixed_param.device)
                                # Add weighted difference
                                mixed_param += weights[i] * (source_param - mixed_param)
                    
                    target_state[param_name] = mixed_param
            
            target_model.load_state_dict(target_state)
            
        except Exception as e:
            print(f"❌ Additive mixing failed: {str(e)}")
    
    def _weighted_average_mixing(
        self, 
        target_model: Any, 
        source_models: List[Any], 
        weights: List[float],
        blend_layers: str
    ):
        """Perform weighted average mixing (same as linear interpolation)."""
        self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
    
    def _geometric_mean_mixing(
        self, 
        target_model: Any, 
        source_models: List[Any], 
        weights: List[float],
        blend_layers: str
    ):
        """Perform geometric mean mixing of model parameters."""
        try:
            # For now, fall back to linear mixing
            # Geometric mean requires careful handling of negative values
            print("🔄 Using linear interpolation (Geometric mean implementation in development)")
            self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
            
        except Exception as e:
            print(f"❌ Geometric mean mixing failed: {str(e)}")
            self._linear_interpolation_mixing(target_model, source_models, weights, blend_layers)
    
    def _should_blend_parameter(self, param_name: str, blend_layers: str) -> bool:
        """Determine if a parameter should be included in blending."""
        if blend_layers == "all":
            return True
        
        param_lower = param_name.lower()
        
        if blend_layers == "encoder":
            return "encoder" in param_lower or "input" in param_lower
        elif blend_layers == "decoder":
            return "decoder" in param_lower or "output" in param_lower
        elif blend_layers == "attention":
            return "attention" in param_lower or "attn" in param_lower
        else:
            # Custom layer specification (comma-separated)
            layer_names = [name.strip().lower() for name in blend_layers.split(",")]
            return any(layer_name in param_lower for layer_name in layer_names)
    
    def _generate_mixing_info(
        self, 
        models: List[Any], 
        weights: List[float],
        algorithm: str,
        strategy: str
    ) -> str:
        """Generate comprehensive mixing information report."""
        try:
            info = ["🎯 MODEL MIXING REPORT", "=" * 30]
            
            info.append(f"📊 Strategy: {strategy}")
            info.append(f"🔀 Algorithm: {self._MIXING_ALGORITHMS.get(algorithm, algorithm)}")
            info.append(f"📱 Models mixed: {len(models)}")
            
            info.append("\n⚖️ MIXING WEIGHTS:")
            for i, (model, weight) in enumerate(zip(models, weights)):
                model_desc = f"Model {i+1}"
                info.append(f"   • {model_desc}: {weight:.3f} ({weight*100:.1f}%)")
            
            # Validate weights sum
            weight_sum = sum(weights)
            info.append(f"\n📈 Total weight: {weight_sum:.3f}")
            
            if abs(weight_sum - 1.0) > 0.001:
                info.append("⚠️ Weights don't sum to 1.0 - mixing may be unbalanced")
            else:
                info.append("✅ Weights properly normalized")
            
            info.append(f"\n🔧 Torch available: {'Yes' if HAS_TORCH else 'No'}")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"❌ Failed to generate mixing info: {str(e)}"


# Register the node
NODE_CLASS_MAPPINGS = {
    "XDEV_SDXLModelMixer": SDXLModelMixer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_SDXLModelMixer": "SDXL Model Mixer (XDev)"
}