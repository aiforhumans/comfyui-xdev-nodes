from __future__ import annotations
from typing import Dict, Tuple, Any, Union, List
import json
import sys
from ..categories import NodeCategories

class OutputDev:
    """
    Universal output/sink node for testing and debugging any ComfyUI data type.
    
    This development node can receive and display information about any type of 
    ComfyUI data including IMAGE, STRING, INT, FLOAT, LATENT, MODEL, CONDITIONING, etc.
    Perfect for workflow debugging and connection testing.
    
    Class methods
    -------------
    INPUT_TYPES (dict):
        Defines input parameters with advanced configurations including lazy evaluation.
    check_lazy_status:
        Controls lazy evaluation for performance optimization.
    IS_CHANGED:
        Controls when the node is re-executed for caching optimization.

    Attributes
    ----------
    RETURN_TYPES (`tuple`):
        Returns analysis results as strings.
    RETURN_NAMES (`tuple`):
        Human-readable names for each output.
    FUNCTION (`str`):
        Entry-point method name for execution.
    OUTPUT_NODE (`bool`):
        Marks this as an output node for workflow execution.
    CATEGORY (`str`):
        UI category placement.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_1": ("*", {
                    "tooltip": "Primary input - accepts any ComfyUI data type for analysis and display"
                })
            },
            "optional": {
                "input_2": ("*", {
                    "tooltip": "Optional secondary input for comparing multiple data streams"
                }),
                "input_3": ("*", {
                    "tooltip": "Optional tertiary input for complex workflow debugging"
                }),
                "display_level": (["summary", "detailed", "full"], {
                    "default": "detailed",
                    "tooltip": "Amount of information to display: summary (type+size), detailed (adds shape/device), full (includes content preview)"
                }),
                "save_to_file": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Save analysis results to a text file for external review"
                }),
                "compare_inputs": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "When multiple inputs connected, compare and highlight differences"
                })
            }
        }

    # This is an output node - it terminates the workflow branch
    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "analyze_and_display"
    CATEGORY = NodeCategories.DEVELOPMENT
    DESCRIPTION = "Universal debugging output node - accepts and analyzes any ComfyUI data type"
    DISPLAY_NAME = "Output Dev (XDev)"
    
    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        """
        Custom input validation that accepts any type.
        This overrides ComfyUI's default type validation to allow any input type.
        """
        # Always return True to accept any type - this is a universal debugging node
        return True

    def analyze_and_display(self, input_1, input_2=None, input_3=None, 
                          display_level: str = "detailed", save_to_file: bool = False, 
                          compare_inputs: bool = False):
        """
        Analyze and display comprehensive information about input data.
        
        Args:
            input_1: Primary input data (required)
            input_2: Optional secondary input for comparison
            input_3: Optional tertiary input for comparison
            display_level: Level of analysis detail
            save_to_file: Whether to save results to file
            compare_inputs: Whether to compare multiple inputs
            
        Returns:
            Empty tuple (output node doesn't return data)
        """
        try:
            print("\n" + "="*60)
            print("🔍 OUTPUT DEV NODE ANALYSIS")
            print("="*60)
            
            # Analyze primary input
            self._analyze_single_input("INPUT_1", input_1, display_level)
            
            # Analyze additional inputs if provided
            inputs_to_analyze = []
            if input_2 is not None:
                self._analyze_single_input("INPUT_2", input_2, display_level)
                inputs_to_analyze.append(("INPUT_1", input_1))
                inputs_to_analyze.append(("INPUT_2", input_2))
            
            if input_3 is not None:
                self._analyze_single_input("INPUT_3", input_3, display_level)
                if input_2 is not None:
                    inputs_to_analyze.append(("INPUT_3", input_3))
            
            # Compare inputs if requested and multiple inputs available
            if compare_inputs and len(inputs_to_analyze) > 1:
                self._compare_inputs(inputs_to_analyze)
            
            # Save to file if requested
            if save_to_file:
                self._save_analysis_to_file([
                    ("INPUT_1", input_1),
                    ("INPUT_2", input_2) if input_2 is not None else None,
                    ("INPUT_3", input_3) if input_3 is not None else None
                ], display_level)
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ OUTPUT DEV ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        return ()

    def _analyze_single_input(self, input_name: str, data: Any, level: str):
        """Analyze a single input comprehensively"""
        print(f"\n📊 {input_name} ANALYSIS:")
        print("-" * 30)
        
        try:
            # Basic information (always shown)
            data_type = type(data).__name__
            print(f"Type: {data_type}")
            print(f"Module: {getattr(type(data), '__module__', 'unknown')}")
            
            # Detect and analyze ComfyUI-specific data types
            comfy_type = self._detect_comfyui_type(data)
            if comfy_type:
                print(f"ComfyUI Type: {comfy_type}")
                self._analyze_comfyui_object(data, comfy_type, level)
                return
            
            # Size/shape information
            if hasattr(data, 'shape'):
                shape = tuple(int(x) for x in data.shape)
                total_elements = 1
                for dim in shape:
                    total_elements *= dim
                print(f"Shape: {shape}")
                print(f"Total Elements: {total_elements:,}")
                
                # Memory information for tensors
                if hasattr(data, 'element_size') and hasattr(data, 'numel'):
                    memory_bytes = data.element_size() * data.numel()
                    memory_mb = memory_bytes / (1024 * 1024)
                    print(f"Memory Usage: {memory_mb:.2f} MB")
                    
            elif hasattr(data, '__len__') and not isinstance(data, str):
                length = len(data)
                print(f"Length: {length:,}")
                
                # Special handling for lists that might contain ComfyUI objects
                if isinstance(data, list) and length > 0:
                    first_item = data[0]
                    first_type = self._detect_comfyui_type(first_item)
                    if first_type:
                        print(f"List contains: {first_type} objects")
                        if level in ["detailed", "full"]:
                            print(f"Analyzing first item:")
                            self._analyze_comfyui_object(first_item, first_type, level)
                    
            elif isinstance(data, str):
                char_count = len(data)
                word_count = len(data.split()) if data else 0
                print(f"Characters: {char_count:,}")
                print(f"Words: {word_count:,}")
            elif isinstance(data, (int, float)):
                print(f"Value: {data}")
                
            # Detailed information
            if level in ["detailed", "full"]:
                if hasattr(data, 'dtype'):
                    print(f"Data Type: {data.dtype}")
                if hasattr(data, 'device'):
                    print(f"Device: {data.device}")
                if hasattr(data, 'requires_grad'):
                    print(f"Requires Gradient: {data.requires_grad}")
                if hasattr(data, 'is_contiguous'):
                    print(f"Is Contiguous: {data.is_contiguous()}")
                    
            # Full information includes content preview
            if level == "full":
                self._show_content_preview(data)
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
    
    def _detect_comfyui_type(self, data: Any) -> str:
        """Detect ComfyUI-specific data types"""
        try:
            # Check for common ComfyUI object patterns
            class_name = type(data).__name__
            module_name = getattr(type(data), '__module__', '')
            
            # Noise and Sampler detection (new)
            if 'noise' in class_name.lower():
                return "NOISE"
            elif 'sampler' in class_name.lower():
                return "SAMPLER"
            elif 'scheduler' in class_name.lower():
                return "SCHEDULER"
            elif 'sigmas' in class_name.lower():
                return "SIGMAS"
            # Model detection
            elif 'model' in class_name.lower() or 'unet' in class_name.lower():
                return "MODEL"
            elif 'clip' in class_name.lower():
                return "CLIP"
            elif 'vae' in class_name.lower():
                return "VAE"
            elif 'condition' in class_name.lower() or hasattr(data, 'cond'):
                return "CONDITIONING"
            elif hasattr(data, 'samples') and hasattr(data, '__getitem__'):
                return "LATENT"
            elif hasattr(data, 'shape') and len(getattr(data, 'shape', [])) == 4:
                # Could be IMAGE (B,H,W,C) or MASK
                if hasattr(data, 'dtype'):
                    return "IMAGE/TENSOR"
            elif isinstance(data, dict):
                # Enhanced dict structure detection
                return self._analyze_dict_type(data)
            
            return None
        except Exception:
            return None
    
    def _analyze_dict_type(self, data: dict) -> str:
        """Analyze dictionary to determine ComfyUI type"""
        try:
            keys = list(data.keys())
            
            # LATENT detection
            if 'samples' in keys:
                return "LATENT"
            elif 'batch_index' in keys:
                return "LATENT"  # Sometimes latents have batch_index
            
            # CONDITIONING detection
            if any(key in keys for key in ['cond', 'uncond', 'conditioning']):
                return "CONDITIONING"
            elif len(keys) == 1 and isinstance(list(data.values())[0], list):
                # Could be conditioning in list format
                return "CONDITIONING"
            
            # Model/Pipeline configuration
            if any(key in keys for key in ['model_type', 'config', 'state_dict']):
                return "MODEL_CONFIG"
            
            # Check for workflow/node data
            if any(key in keys for key in ['nodes', 'links', 'workflow']):
                return "WORKFLOW"
            
            # Parameters or settings dict
            if any(key in keys for key in ['steps', 'cfg', 'seed', 'sampler_name']):
                return "PARAMETERS"
            
            return "DICT"  # Generic dict type
        except Exception:
            return "DICT"
    
    def _analyze_comfyui_object(self, data: Any, comfy_type: str, level: str):
        """Analyze ComfyUI-specific objects in detail"""
        try:
            print(f"🎯 {comfy_type} Object Analysis:")
            
            if comfy_type == "MODEL":
                self._analyze_model(data, level)
            elif comfy_type == "CLIP":
                self._analyze_clip(data, level)
            elif comfy_type == "VAE":
                self._analyze_vae(data, level)
            elif comfy_type == "CONDITIONING":
                self._analyze_conditioning(data, level)
            elif comfy_type == "LATENT":
                self._analyze_latent(data, level)
            elif comfy_type == "IMAGE/TENSOR":
                self._analyze_image_tensor(data, level)
            elif comfy_type == "NOISE":
                self._analyze_noise(data, level)
            elif comfy_type == "SAMPLER":
                self._analyze_sampler(data, level)
            elif comfy_type == "SCHEDULER":
                self._analyze_scheduler(data, level)
            elif comfy_type == "SIGMAS":
                self._analyze_sigmas(data, level)
            elif comfy_type in ["DICT", "MODEL_CONFIG", "WORKFLOW", "PARAMETERS"]:
                self._analyze_enhanced_dict(data, comfy_type, level)
            else:
                print(f"   Detected as {comfy_type} but no specific analyzer available")
                self._analyze_generic_object(data, level)
                
        except Exception as e:
            print(f"   ❌ ComfyUI object analysis error: {e}")
    
    def _analyze_model(self, model, level: str):
        """Analyze MODEL objects"""
        try:
            print(f"   📱 Model Information:")
            
            # Try to get model properties
            if hasattr(model, 'model'):
                actual_model = model.model
                print(f"   - Model Class: {type(actual_model).__name__}")
                
                if hasattr(actual_model, 'device'):
                    print(f"   - Device: {actual_model.device}")
                if hasattr(actual_model, 'dtype'):
                    print(f"   - Data Type: {actual_model.dtype}")
                    
                # Try to get parameter count
                if hasattr(actual_model, 'parameters'):
                    try:
                        param_count = sum(p.numel() for p in actual_model.parameters())
                        print(f"   - Parameters: {param_count:,}")
                    except:
                        pass
            
            # Check for common model attributes
            common_attrs = ['model_options', 'model_config', 'load_device', 'offload_device']
            for attr in common_attrs:
                if hasattr(model, attr):
                    value = getattr(model, attr)
                    print(f"   - {attr}: {type(value).__name__}")
                    
        except Exception as e:
            print(f"   ❌ Model analysis error: {e}")
    
    def _analyze_clip(self, clip, level: str):
        """Analyze CLIP objects"""
        try:
            print(f"   🖼️ CLIP Information:")
            
            if hasattr(clip, 'cond_stage_model'):
                print(f"   - Conditioning Model: {type(clip.cond_stage_model).__name__}")
            
            if hasattr(clip, 'tokenizer'):
                print(f"   - Tokenizer: Available")
            
            if hasattr(clip, 'load_device'):
                print(f"   - Load Device: {clip.load_device}")
                
            # Check for common CLIP attributes
            common_attrs = ['dtype', 'layer_idx']
            for attr in common_attrs:
                if hasattr(clip, attr):
                    value = getattr(clip, attr)
                    print(f"   - {attr}: {value}")
                    
        except Exception as e:
            print(f"   ❌ CLIP analysis error: {e}")
    
    def _analyze_vae(self, vae, level: str):
        """Analyze VAE objects"""
        try:
            print(f"   🎨 VAE Information:")
            
            if hasattr(vae, 'first_stage_model'):
                print(f"   - VAE Model: {type(vae.first_stage_model).__name__}")
                
            if hasattr(vae, 'device'):
                print(f"   - Device: {vae.device}")
            if hasattr(vae, 'dtype'):
                print(f"   - Data Type: {vae.dtype}")
                
            # Check for VAE-specific attributes
            vae_attrs = ['scale_factor', 'load_device', 'offload_device']
            for attr in vae_attrs:
                if hasattr(vae, attr):
                    value = getattr(vae, attr)
                    print(f"   - {attr}: {value}")
                    
        except Exception as e:
            print(f"   ❌ VAE analysis error: {e}")
    
    def _analyze_conditioning(self, cond, level: str):
        """Analyze CONDITIONING objects"""
        try:
            print(f"   🎭 Conditioning Information:")
            
            if isinstance(cond, list):
                print(f"   - Conditioning List Length: {len(cond)}")
                if len(cond) > 0:
                    first_cond = cond[0]
                    if isinstance(first_cond, list) and len(first_cond) > 0:
                        tensor = first_cond[0]
                        if hasattr(tensor, 'shape'):
                            print(f"   - Tensor Shape: {tensor.shape}")
                        if hasattr(tensor, 'device'):
                            print(f"   - Device: {tensor.device}")
                        if hasattr(tensor, 'dtype'):
                            print(f"   - Data Type: {tensor.dtype}")
            elif isinstance(cond, dict):
                print(f"   - Conditioning Dict Keys: {list(cond.keys())}")
                if 'cond' in cond and hasattr(cond['cond'], 'shape'):
                    print(f"   - Cond Tensor Shape: {cond['cond'].shape}")
                    
        except Exception as e:
            print(f"   ❌ Conditioning analysis error: {e}")
    
    def _analyze_latent(self, latent, level: str):
        """Analyze LATENT objects"""
        try:
            print(f"   🔮 Latent Information:")
            
            if isinstance(latent, dict) and 'samples' in latent:
                samples = latent['samples']
                if hasattr(samples, 'shape'):
                    print(f"   - Samples Shape: {samples.shape}")
                if hasattr(samples, 'device'):
                    print(f"   - Device: {samples.device}")
                if hasattr(samples, 'dtype'):
                    print(f"   - Data Type: {samples.dtype}")
                
                # Calculate memory usage
                if hasattr(samples, 'element_size') and hasattr(samples, 'numel'):
                    memory_bytes = samples.element_size() * samples.numel()
                    memory_mb = memory_bytes / (1024 * 1024)
                    print(f"   - Memory Usage: {memory_mb:.2f} MB")
                    
        except Exception as e:
            print(f"   ❌ Latent analysis error: {e}")
    
    def _analyze_image_tensor(self, tensor, level: str):
        """Analyze IMAGE/TENSOR objects"""
        try:
            print(f"   🖼️ Image/Tensor Information:")
            
            if hasattr(tensor, 'shape'):
                shape = tensor.shape
                print(f"   - Shape: {shape}")
                
                if len(shape) == 4:  # Typical image format (B,H,W,C) or (B,C,H,W)
                    batch, dim1, dim2, dim3 = shape
                    print(f"   - Batch Size: {batch}")
                    print(f"   - Dimensions: {dim1}×{dim2}×{dim3}")
                    
            if hasattr(tensor, 'dtype'):
                print(f"   - Data Type: {tensor.dtype}")
            if hasattr(tensor, 'device'):
                print(f"   - Device: {tensor.device}")
                
            # Value range analysis
            if level == "full" and hasattr(tensor, 'min') and hasattr(tensor, 'max'):
                try:
                    min_val = float(tensor.min())
                    max_val = float(tensor.max())
                    mean_val = float(tensor.mean())
                    print(f"   - Value Range: {min_val:.4f} to {max_val:.4f}")
                    print(f"   - Mean Value: {mean_val:.4f}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Image/Tensor analysis error: {e}")
    
    def _analyze_noise(self, noise, level: str):
        """Analyze NOISE objects (like Noise_RandomNoise)"""
        try:
            print(f"   🎲 Noise Information:")
            
            noise_class = type(noise).__name__
            print(f"   - Noise Class: {noise_class}")
            
            # Check for common noise attributes
            noise_attrs = ['seed', 'noise_type', 'normalize', 'device']
            for attr in noise_attrs:
                if hasattr(noise, attr):
                    value = getattr(noise, attr)
                    print(f"   - {attr}: {value}")
            
            # Check for callable methods
            if hasattr(noise, 'generate_noise'):
                print(f"   - Can Generate Noise: Yes")
            if hasattr(noise, '__call__'):
                print(f"   - Callable: Yes")
                
        except Exception as e:
            print(f"   ❌ Noise analysis error: {e}")
    
    def _analyze_sampler(self, sampler, level: str):
        """Analyze SAMPLER objects"""
        try:
            print(f"   🎯 Sampler Information:")
            
            sampler_class = type(sampler).__name__
            print(f"   - Sampler Class: {sampler_class}")
            
            # Check for sampler attributes
            sampler_attrs = ['sampler_name', 'steps', 'cfg', 'denoise', 'scheduler']
            for attr in sampler_attrs:
                if hasattr(sampler, attr):
                    value = getattr(sampler, attr)
                    print(f"   - {attr}: {value}")
                    
        except Exception as e:
            print(f"   ❌ Sampler analysis error: {e}")
    
    def _analyze_scheduler(self, scheduler, level: str):
        """Analyze SCHEDULER objects"""
        try:
            print(f"   📅 Scheduler Information:")
            
            scheduler_class = type(scheduler).__name__
            print(f"   - Scheduler Class: {scheduler_class}")
            
            # Check for scheduler attributes
            scheduler_attrs = ['schedule_name', 'steps', 'sigma_min', 'sigma_max']
            for attr in scheduler_attrs:
                if hasattr(scheduler, attr):
                    value = getattr(scheduler, attr)
                    print(f"   - {attr}: {value}")
                    
        except Exception as e:
            print(f"   ❌ Scheduler analysis error: {e}")
    
    def _analyze_sigmas(self, sigmas, level: str):
        """Analyze SIGMAS objects"""
        try:
            print(f"   📊 Sigmas Information:")
            
            if hasattr(sigmas, 'shape'):
                print(f"   - Shape: {sigmas.shape}")
            if hasattr(sigmas, 'dtype'):
                print(f"   - Data Type: {sigmas.dtype}")
            if hasattr(sigmas, 'device'):
                print(f"   - Device: {sigmas.device}")
                
            # Show value range for sigmas
            if level == "full" and hasattr(sigmas, 'min') and hasattr(sigmas, 'max'):
                try:
                    min_val = float(sigmas.min())
                    max_val = float(sigmas.max())
                    print(f"   - Value Range: {min_val:.6f} to {max_val:.6f}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Sigmas analysis error: {e}")
    
    def _analyze_enhanced_dict(self, data: dict, dict_type: str, level: str):
        """Analyze dictionary objects with enhanced type detection"""
        try:
            print(f"   📚 {dict_type} Information:")
            
            keys = list(data.keys())
            print(f"   - Keys ({len(keys)}): {keys[:10]}")  # Show first 10 keys
            if len(keys) > 10:
                print(f"     ... and {len(keys) - 10} more keys")
            
            # Show values for each key with type information
            if level in ["detailed", "full"] and len(keys) <= 10:
                print(f"   - Key-Value Analysis:")
                for key in keys[:5]:  # Limit to 5 keys for readability
                    try:
                        value = data[key]
                        value_type = type(value).__name__
                        if hasattr(value, 'shape'):
                            print(f"     • {key}: {value_type} {getattr(value, 'shape', '')}")
                        elif isinstance(value, (list, tuple)) and len(value) > 0:
                            print(f"     • {key}: {value_type}[{len(value)}] (first: {type(value[0]).__name__})")
                        else:
                            print(f"     • {key}: {value_type}")
                    except Exception as e:
                        print(f"     • {key}: <analysis error>")
            
            # Specific analysis based on dict type
            if dict_type == "LATENT" and 'samples' in data:
                samples = data['samples']
                if hasattr(samples, 'shape'):
                    print(f"   - Latent Shape: {samples.shape}")
                if hasattr(samples, 'device'):
                    print(f"   - Device: {samples.device}")
            elif dict_type == "PARAMETERS":
                param_count = len([k for k, v in data.items() if not k.startswith('_')])
                print(f"   - Parameter Count: {param_count}")
                
        except Exception as e:
            print(f"   ❌ Enhanced dict analysis error: {e}")

    def _analyze_generic_object(self, obj, level: str):
        """Analyze generic objects with common attributes"""
        try:
            print(f"   🔍 Generic Object Analysis:")
            
            # List common attributes
            interesting_attrs = []
            for attr_name in dir(obj):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(obj, attr_name)
                        if not callable(attr_value):
                            interesting_attrs.append((attr_name, type(attr_value).__name__))
                    except:
                        pass
            
            if interesting_attrs:
                print(f"   - Attributes ({len(interesting_attrs)}):")
                for name, type_name in interesting_attrs[:10]:  # Limit to first 10
                    print(f"     • {name}: {type_name}")
                if len(interesting_attrs) > 10:
                    print(f"     ... and {len(interesting_attrs) - 10} more")
                    
        except Exception as e:
            print(f"   ❌ Generic object analysis error: {e}")

    def _show_content_preview(self, data: Any):
        """Show a safe preview of the data content"""
        print("\n📋 CONTENT PREVIEW:")
        try:
            if isinstance(data, str):
                preview = data[:100] + "..." if len(data) > 100 else data
                print(f"Text: '{preview}'")
            elif isinstance(data, dict):
                # Enhanced dict preview
                if len(data) == 0:
                    print("Empty dictionary")
                else:
                    items = []
                    for key, value in list(data.items())[:3]:
                        value_str = str(type(value).__name__)
                        if hasattr(value, 'shape'):
                            value_str += f" {value.shape}"
                        elif isinstance(value, (list, tuple)):
                            value_str += f"[{len(value)}]"
                        items.append(f"{key}: {value_str}")
                    if len(data) > 3:
                        items.append(f"... and {len(data) - 3} more keys")
                    print("Dict contents: " + ", ".join(items))
            elif hasattr(data, 'shape') and len(getattr(data, 'shape', [])) > 0:
                # For tensors/arrays
                try:
                    shape = data.shape
                    print(f"Tensor shape: {shape}")
                    
                    # Try to show some values if possible
                    if hasattr(data, 'flatten') and hasattr(data, '__getitem__'):
                        flat = data.flatten()
                        if len(flat) > 0:
                            preview_size = min(5, len(flat))
                            values = []
                            for i in range(preview_size):
                                try:
                                    val = float(flat[i])
                                    values.append(f"{val:.4f}")
                                except Exception as e:
                                    values.append(f"<{type(e).__name__}>")
                            preview_str = ", ".join(values)
                            if len(flat) > preview_size:
                                preview_str += f", ... ({len(flat)-preview_size} more)"
                            print(f"Values: [{preview_str}]")
                            
                    # Show statistics for numeric data
                    if hasattr(data, 'min') and hasattr(data, 'max'):
                        try:
                            min_val = float(data.min())
                            max_val = float(data.max())
                            mean_val = float(data.mean()) if hasattr(data, 'mean') else None
                            print(f"Range: {min_val:.4f} to {max_val:.4f}")
                            if mean_val is not None:
                                print(f"Mean: {mean_val:.4f}")
                        except Exception as stat_e:
                            print(f"Statistics unavailable: {type(stat_e).__name__}")
                except Exception as tensor_e:
                    print(f"Tensor analysis failed: {type(tensor_e).__name__}: {str(tensor_e)}")
                    
            elif hasattr(data, '__len__'):
                # For lists/tuples  
                length = len(data)
                if length == 0:
                    print("Empty container")
                else:
                    preview_size = min(3, length)
                    items = []
                    for i in range(preview_size):
                        try:
                            item = data[i]
                            item_type = type(item).__name__
                            if hasattr(item, 'shape'):
                                item_str = f"{item_type} {item.shape}"
                            else:
                                item_str = str(item)
                                if len(item_str) > 50:
                                    item_str = item_str[:47] + "..."
                            items.append(item_str)
                        except Exception as item_e:
                            items.append(f"<{type(item_e).__name__}>")
                    if length > preview_size:
                        items.append(f"... and {length - preview_size} more items")
                    print(f"Items ({length}): " + " | ".join(items))
            else:
                # For other objects
                obj_str = str(data)
                if len(obj_str) > 100:
                    obj_str = obj_str[:97] + "..."
                print(f"Object: {obj_str}")
                    
        except Exception as e:
            print(f"Preview error: {type(e).__name__}: {str(e)}")
            # Try to show basic info even if preview fails
            try:
                print(f"Fallback info - Type: {type(data).__name__}")
                if hasattr(data, '__len__'):
                    print(f"Length: {len(data)}")
            except:
                print("No additional info available")
                
        except Exception as e:
            print(f"Content preview error: {e}")

    def _compare_inputs(self, inputs: List[Tuple[str, Any]]):
        """Compare multiple inputs and highlight differences"""
        print(f"\n🔄 INPUT COMPARISON ({len(inputs)} inputs):")
        print("-" * 40)
        
        try:
            # Compare types
            types = [(name, type(data).__name__) for name, data in inputs]
            print("Types:", ", ".join([f"{name}: {t}" for name, t in types]))
            
            # Check if all types are the same
            unique_types = set(t for _, t in types)
            if len(unique_types) == 1:
                print("✅ All inputs have the same type")
            else:
                print("⚠️ Inputs have different types")
            
            # Compare shapes for tensor-like objects
            shapes = []
            for name, data in inputs:
                if hasattr(data, 'shape'):
                    shapes.append((name, tuple(data.shape)))
                else:
                    shapes.append((name, 'No shape'))
            
            if shapes:
                print("Shapes:", ", ".join([f"{name}: {s}" for name, s in shapes]))
                unique_shapes = set(s for _, s in shapes if s != 'No shape')
                if len(unique_shapes) <= 1:
                    print("✅ Compatible shapes")
                else:
                    print("⚠️ Different shapes detected")
                    
        except Exception as e:
            print(f"Comparison error: {e}")

    def _save_analysis_to_file(self, inputs: List[Tuple[str, Any]], level: str):
        """Save analysis results to a file"""
        try:
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output_dev_analysis_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Output Dev Node Analysis - {datetime.now()}\n")
                f.write("="*60 + "\n\n")
                
                for input_name, data in inputs:
                    if data is not None:
                        f.write(f"{input_name} Analysis:\n")
                        f.write("-" * 30 + "\n")
                        f.write(f"Type: {type(data).__name__}\n")
                        f.write(f"Module: {getattr(type(data), '__module__', 'unknown')}\n")
                        
                        if hasattr(data, 'shape'):
                            f.write(f"Shape: {tuple(data.shape)}\n")
                        elif hasattr(data, '__len__') and not isinstance(data, str):
                            f.write(f"Length: {len(data)}\n")
                        
                        f.write("\n")
            
            print(f"💾 Analysis saved to: {filename}")
            
        except Exception as e:
            print(f"Save error: {e}")


class InputDev:
    """
    Universal input/source node for testing and generating any ComfyUI data type.
    
    This development node can generate and output various types of test data
    including IMAGE tensors, strings, numbers, lists, and mock objects.
    Perfect for testing node connections and workflow development.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "output_type": ([
                    "STRING", "INT", "FLOAT", "BOOLEAN",
                    "IMAGE", "LATENT", "MASK", 
                    "MODEL", "CONDITIONING", 
                    "LIST", "DICT"
                ], {
                    "default": "STRING",
                    "tooltip": "Type of data to generate and output for testing connections"
                }),
                "output_mode": (["simple", "realistic", "stress_test"], {
                    "default": "realistic", 
                    "tooltip": "Data generation mode: simple (minimal), realistic (typical values), stress_test (edge cases)"
                })
            },
            "optional": {
                "custom_value": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Custom value to use instead of generated data (will be converted to target type if possible)"
                }),
                "size_parameter": ("INT", {
                    "default": 512,
                    "min": 1,
                    "max": 4096,
                    "tooltip": "Size parameter for generated data (image dimensions, list length, etc.)"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Seed for reproducible random data generation",
                    "lazy": True
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "step": 1,
                    "display": "slider",
                    "tooltip": "Number of items to generate (for batch data types)",
                    "lazy": True
                }),
                "quality_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.1,
                    "round": 0.01,
                    "display": "slider",
                    "tooltip": "Quality multiplier for generated data complexity",
                    "lazy": True
                }),
                "include_metadata": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Include metadata string describing the generated data"
                })
            }
        }

    RETURN_TYPES = ("*", "STRING")
    RETURN_NAMES = ("generated_data", "metadata")
    FUNCTION = "generate_data"
    CATEGORY = NodeCategories.DEVELOPMENT
    DESCRIPTION = "Universal test data generator - creates any ComfyUI data type for connection testing"
    DISPLAY_NAME = "Input Dev (XDev)"
    
    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        """
        Custom input validation for InputDev node.
        Always returns True since this is a universal test data generator.
        """
        return True

    def check_lazy_status(self, output_type, output_mode="realistic", custom_value="", 
                         size_parameter=512, seed=0, batch_size=1, quality_factor=1.0, include_metadata=True):
        """
        Control lazy evaluation for performance optimization.
        
        Only evaluate expensive parameters when actually needed for data generation.
        For simple output types, we don't need complex parameters.
        """
        # For simple types, we don't need expensive parameters
        if output_type in ["STRING", "INT", "FLOAT", "BOOLEAN"]:
            return []  # No lazy params needed
        
        # For complex types, we need all parameters
        if output_type in ["IMAGE", "LATENT"]:
            return ["seed", "batch_size", "quality_factor", "size_parameter"]
        
        # For other types, we need basic parameters
        return ["seed", "batch_size"]

    def generate_data(self, output_type: str, output_mode: str = "realistic", 
                     custom_value: str = "", size_parameter: int = 512, 
                     seed: int = 0, batch_size: int = 1, quality_factor: float = 1.0, 
                     include_metadata: bool = True):
        """
        Generate test data of the specified type.
        
        Args:
            output_type: Type of data to generate
            output_mode: Generation mode (simple/realistic/stress_test)
            custom_value: Custom value to convert/use
            size_parameter: Size parameter for data generation
            seed: Random seed for reproducibility
            include_metadata: Whether to include metadata description
            
        Returns:
            Tuple of (generated_data, metadata_string)
        """
        try:
            # Set random seed for reproducibility
            import random
            random.seed(seed)
            
            # Generate data based on type
            if output_type == "STRING":
                data = self._generate_string(output_mode, custom_value, size_parameter)
            elif output_type == "INT":
                data = self._generate_int(output_mode, custom_value)
            elif output_type == "FLOAT":
                data = self._generate_float(output_mode, custom_value)
            elif output_type == "BOOLEAN":
                data = self._generate_boolean(output_mode, custom_value)
            elif output_type == "IMAGE":
                data = self._generate_image(output_mode, size_parameter)
            elif output_type == "LATENT":
                data = self._generate_latent(output_mode, size_parameter)
            elif output_type == "MASK":
                data = self._generate_mask(output_mode, size_parameter)
            elif output_type == "MODEL":
                data = self._generate_model(output_mode)
            elif output_type == "CONDITIONING":
                data = self._generate_conditioning(output_mode, size_parameter)
            elif output_type == "LIST":
                data = self._generate_list(output_mode, size_parameter)
            elif output_type == "DICT":
                data = self._generate_dict(output_mode, size_parameter)

            else:
                data = "Unknown type"
            
            # Generate metadata
            if include_metadata:
                metadata = self._generate_metadata(output_type, output_mode, data, size_parameter, seed)
            else:
                metadata = f"Generated {output_type}"
            
            return (data, metadata)
            
        except Exception as e:
            error_data = f"Error generating {output_type}: {str(e)}"
            error_metadata = f"Generation failed: {str(e)}"
            return (error_data, error_metadata)

    def _generate_string(self, mode: str, custom: str, size: int) -> str:
        """Generate string data"""
        if custom:
            return custom
        
        if mode == "simple":
            return "test_string"
        elif mode == "realistic":
            return f"Generated test string with {size} characters: " + "A" * max(0, size - 40)
        else:  # stress_test
            # Generate string with special characters and unicode
            import random
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
            special_chars = "αβγδεζηθικλμνξοπρστυφχψω🔥💯✨🎯🚀"
            all_chars = chars + special_chars
            return ''.join(random.choice(all_chars) for _ in range(size))

    def _generate_int(self, mode: str, custom: str) -> int:
        """Generate integer data"""
        if custom:
            try:
                return int(float(custom))
            except:
                return 0
        
        import random
        if mode == "simple":
            return 42
        elif mode == "realistic":
            return random.randint(-1000, 1000)
        else:  # stress_test
            return random.choice([-2147483648, 2147483647, 0, 1, -1])

    def _generate_float(self, mode: str, custom: str) -> float:
        """Generate float data"""
        if custom:
            try:
                return float(custom)
            except:
                return 0.0
        
        import random
        if mode == "simple":
            return 3.14159
        elif mode == "realistic":
            return random.uniform(-100.0, 100.0)
        else:  # stress_test
            return random.choice([float('inf'), float('-inf'), 0.0, 1e-10, 1e10])

    def _generate_image(self, mode: str, size: int):
        """Generate authentic ComfyUI IMAGE tensor (format: B,H,W,C)"""
        try:
            import torch
            # Try to import ComfyUI device management for proper device placement
            try:
                import comfy.model_management
                device = comfy.model_management.intermediate_device()
            except ImportError:
                device = "cpu"
            
            if mode == "simple":
                # Single pixel image with neutral gray (0.5)
                return torch.ones(1, 1, 1, 3, dtype=torch.float32, device=device) * 0.5
            elif mode == "realistic":
                # Standard image size with structured pattern (not random noise)
                h = w = min(size, 1024)  # Cap at 1024 for memory
                # Create a gradient pattern typical for real images
                x = torch.linspace(0, 1, w, device=device).unsqueeze(0).unsqueeze(0).unsqueeze(-1)
                y = torch.linspace(0, 1, h, device=device).unsqueeze(1).unsqueeze(0).unsqueeze(-1)
                gradient = (x + y) / 2
                image = gradient.expand(1, h, w, 3)
                # Add some structured noise
                noise = torch.randn_like(image) * 0.1
                return torch.clamp(image + noise, 0.0, 1.0).to(dtype=torch.float32)
            else:  # stress_test
                # Large image with checkered pattern
                h = w = min(size, 2048)
                checker_size = max(1, size // 32)
                x_checker = ((torch.arange(w, device=device) // checker_size) % 2).float()
                y_checker = ((torch.arange(h, device=device) // checker_size) % 2).float()
                pattern = (x_checker.unsqueeze(0) + y_checker.unsqueeze(1)) % 2
                image = pattern.unsqueeze(0).unsqueeze(-1).expand(1, h, w, 3)
                return image.to(dtype=torch.float32)
                
        except ImportError:
            # Numpy fallback for authentic tensor-like behavior
            try:
                import numpy as np
                if mode == "simple":
                    return np.ones((1, 1, 1, 3), dtype=np.float32) * 0.5
                elif mode == "realistic":
                    h = w = min(size, 1024)
                    # Create gradient pattern
                    x = np.linspace(0, 1, w).reshape(1, 1, w, 1)
                    y = np.linspace(0, 1, h).reshape(1, h, 1, 1)
                    gradient = (x + y) / 2
                    image = np.broadcast_to(gradient, (1, h, w, 3))
                    return np.clip(image + np.random.randn(1, h, w, 3) * 0.1, 0.0, 1.0).astype(np.float32)
                else:
                    h = w = min(size, 2048)
                    checker_size = max(1, size // 32)
                    x_idx, y_idx = np.meshgrid(np.arange(w) // checker_size, np.arange(h) // checker_size)
                    pattern = (x_idx + y_idx) % 2
                    return np.expand_dims(pattern, (0, -1)).repeat(3, axis=-1).astype(np.float32)
            except ImportError:
                # Ultimate fallback - return structured data description
                return {
                    "tensor_type": "IMAGE",
                    "shape": [1, size, size, 3],
                    "dtype": "float32",
                    "note": "Authentic ComfyUI IMAGE tensor - install torch for real tensor"
                }

    def _generate_latent(self, mode: str, size: int):
        """Generate authentic ComfyUI LATENT dict based on DeepWiki research"""
        try:
            import torch
            # Try to use ComfyUI device management
            try:
                import comfy.model_management
                device = comfy.model_management.intermediate_device()
            except ImportError:
                device = "cpu"
            
            # Standard ComfyUI latent dimensions: [batch_size, 4, height//8, width//8]
            latent_h = max(1, size // 8)  # VAE downscaling factor
            latent_w = max(1, size // 8)
            
            if mode == "simple":
                # Empty latent (zeros) - following ComfyUI EmptyLatentImage pattern
                samples = torch.zeros(1, 4, latent_h, latent_w, dtype=torch.float32, device=device)
            elif mode == "realistic":
                # Normal distributed latent values typical for encoded images
                samples = torch.randn(1, 4, latent_h, latent_w, dtype=torch.float32, device=device) * 0.5
            else:  # stress_test
                # Extreme latent values for stress testing
                samples = torch.randn(1, 4, latent_h, latent_w, dtype=torch.float32, device=device) * 5.0
                # Add some structured patterns
                samples[0, 0] = torch.ones_like(samples[0, 0]) * 2.0
                samples[0, 1] = -torch.ones_like(samples[0, 1]) * 2.0
            
            # Return proper ComfyUI LATENT dict format
            latent_dict = {"samples": samples}
            
            # Add optional metadata following ComfyUI patterns
            if mode == "stress_test":
                latent_dict["batch_index"] = [0]  # Optional batch indexing
                
            return latent_dict
            
        except ImportError:
            # Numpy fallback maintaining authentic structure
            try:
                import numpy as np
                latent_h = max(1, size // 8)
                latent_w = max(1, size // 8)
                
                if mode == "simple":
                    samples = np.zeros((1, 4, latent_h, latent_w), dtype=np.float32)
                elif mode == "realistic":
                    samples = np.random.randn(1, 4, latent_h, latent_w).astype(np.float32) * 0.5
                else:
                    samples = np.random.randn(1, 4, latent_h, latent_w).astype(np.float32) * 5.0
                
                return {"samples": samples}
                
            except ImportError:
                # Ultimate fallback - structured description
                return {
                    "samples": {
                        "tensor_type": "LATENT_SAMPLES",
                        "shape": [1, 4, max(1, size//8), max(1, size//8)],
                        "dtype": "float32",
                        "note": "Authentic ComfyUI LATENT format - install torch for real tensor"
                    },
                    "format": "ComfyUI_LATENT_v1"
                }

    def _generate_list(self, mode: str, size: int) -> list:
        """Generate list data"""
        import random
        
        if mode == "simple":
            return [1, 2, 3]
        elif mode == "realistic":
            return [random.randint(0, 100) for _ in range(min(size, 1000))]
        else:  # stress_test
            # Mixed type list with edge cases
            return [
                0, 1, -1, float('inf'), "string", None, [], {}, 
                random.randint(-1000000, 1000000)
            ] * (size // 9 + 1)

    def _generate_dict(self, mode: str, size: int) -> dict:
        """Generate dictionary data"""
        import random
        
        if mode == "simple":
            return {"key": "value", "number": 42}
        elif mode == "realistic":
            return {
                f"key_{i}": random.choice([
                    random.randint(0, 1000),
                    random.uniform(0, 100),
                    f"value_{i}",
                    [random.randint(0, 10) for _ in range(3)]
                ])
                for i in range(min(size, 100))
            }
        else:  # stress_test
            return {
                "empty_string": "",
                "long_string": "x" * 10000,
                "zero": 0,
                "negative": -999999,
                "infinity": float('inf'),
                "none_value": None,
                "nested_dict": {"deep": {"deeper": {"deepest": "value"}}},
                "list": list(range(1000)),
                "unicode": "🎯🔥💯✨🚀αβγδε"
            }



    def _generate_boolean(self, mode: str, custom: str) -> bool:
        """Generate boolean data"""
        if custom:
            return custom.lower() in ('true', '1', 'yes', 'on', 'enabled')
        
        import random
        if mode == "simple":
            return True
        elif mode == "realistic":
            return random.choice([True, False])
        else:  # stress_test
            return random.choice([True, False, True, False])  # Still boolean

    def _generate_mask(self, mode: str, size: int):
        """Generate authentic ComfyUI MASK tensor based on DeepWiki research"""
        try:
            import torch
            # Use ComfyUI device management if available
            try:
                import comfy.model_management
                device = comfy.model_management.intermediate_device()
            except ImportError:
                device = "cpu"
            
            if mode == "simple":
                # Single pixel mask (fully opaque)
                return torch.ones(1, 1, 1, dtype=torch.float32, device=device)
            elif mode == "realistic":
                # Structured mask pattern (not random)
                h = w = min(size, 1024)
                # Create circular mask pattern
                center_h, center_w = h // 2, w // 2
                y, x = torch.meshgrid(torch.arange(h, device=device), torch.arange(w, device=device), indexing='ij')
                distance = torch.sqrt((x - center_w) ** 2 + (y - center_h) ** 2)
                radius = min(h, w) // 3
                mask = (distance <= radius).float()
                return mask.unsqueeze(0)  # Add batch dimension
            else:  # stress_test
                # Complex mask with multiple regions
                h = w = min(size, 2048)
                mask = torch.zeros(h, w, dtype=torch.float32, device=device)
                # Create gradient mask
                for i in range(0, h, h//4):
                    for j in range(0, w, w//4):
                        mask[i:i+h//8, j:j+w//8] = torch.rand(min(h//8, h-i), min(w//8, w-j), device=device)
                return mask.unsqueeze(0)  # Add batch dimension
                
        except ImportError:
            # Numpy fallback maintaining authentic structure
            try:
                import numpy as np
                if mode == "simple":
                    return np.ones((1, 1, 1), dtype=np.float32)
                elif mode == "realistic":
                    h = w = min(size, 1024)
                    center_h, center_w = h // 2, w // 2
                    y, x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
                    distance = np.sqrt((x - center_w) ** 2 + (y - center_h) ** 2)
                    radius = min(h, w) // 3
                    mask = (distance <= radius).astype(np.float32)
                    return np.expand_dims(mask, 0)
                else:
                    h = w = min(size, 2048)
                    mask = np.zeros((h, w), dtype=np.float32)
                    for i in range(0, h, h//4):
                        for j in range(0, w, w//4):
                            mask[i:i+h//8, j:j+w//8] = np.random.rand(min(h//8, h-i), min(w//8, w-j))
                    return np.expand_dims(mask, 0)
            except ImportError:
                # Ultimate fallback
                return {
                    "tensor_type": "MASK",
                    "shape": [1, size, size],
                    "dtype": "float32", 
                    "note": "Authentic ComfyUI MASK tensor - install torch for real tensor"
                }

    def _generate_model(self, mode: str):
        """Generate authentic ComfyUI MODEL-like object based on ModelPatcher patterns"""
        try:
            # Try to import actual ComfyUI model classes for authenticity
            try:
                import comfy.model_patcher
                import comfy.model_management
                # This would be the authentic approach, but requires actual model loading
                # For InputDev testing purposes, we create a realistic structure
                device = comfy.model_management.intermediate_device()
            except ImportError:
                device = "cpu"
                
            class AuthenticModelStructure:
                """Authentic ComfyUI MODEL structure based on ModelPatcher patterns"""
                def __init__(self, mode, device):
                    self.mode = mode
                    self.device_name = str(device)
                    self.model_type = "unet"  # Standard diffusion model type
                    self.model_config = {
                        "unet_config": {
                            "model_channels": 320 if mode == "simple" else 640,
                            "in_channels": 4,  # Latent input channels
                            "out_channels": 4,  # Latent output channels
                            "attention_resolutions": [4, 2, 1] if mode != "simple" else [4],
                            "num_res_blocks": 2 if mode == "simple" else 4,
                            "context_dim": 768 if mode != "stress_test" else 2048
                        }
                    }
                    # ModelPatcher-like attributes
                    self.model_options = {}
                    self.model_size_mb = 100 if mode == "simple" else (800 if mode == "realistic" else 2000)
                    
                def clone(self):
                    """ModelPatcher clone method"""
                    return AuthenticModelStructure(self.mode, self.device_name)
                    
                def to(self, device):
                    """Device movement like ModelPatcher"""
                    self.device_name = str(device)
                    return self
                    
                def get_model_object(self, name):
                    """ModelPatcher method simulation"""
                    return f"model_component_{name}"
                    
                def __str__(self):
                    return f"ComfyUI_Model(type={self.model_type}, device={self.device_name}, size_mb={self.model_size_mb})"
                    
            return AuthenticModelStructure(mode, device)
            
        except Exception:
            # Fallback structure maintaining ComfyUI patterns
            return {
                "model_type": "unet",
                "device": "cpu", 
                "model_config": {"in_channels": 4, "out_channels": 4},
                "model_options": {},
                "note": "Authentic ComfyUI MODEL structure - requires ComfyUI environment for full functionality"
            }

    def _generate_conditioning(self, mode: str, size: int):
        """Generate authentic ComfyUI CONDITIONING based on DeepWiki research"""
        try:
            import torch
            # Use ComfyUI device management if available
            try:
                import comfy.model_management
                device = comfy.model_management.intermediate_device()
            except ImportError:
                device = "cpu"
            
            if mode == "simple":
                # Simple conditioning: single token embedding
                seq_len = 1
                hidden_dim = 768  # Standard CLIP embedding dimension
                cond_tensor = torch.zeros(1, seq_len, hidden_dim, dtype=torch.float32, device=device)
                pooled = torch.zeros(1, hidden_dim, dtype=torch.float32, device=device)
            elif mode == "realistic":
                # Realistic conditioning: typical prompt length with structured embeddings
                seq_len = min(size // 10, 77)  # CLIP typical max 77 tokens
                hidden_dim = 768
                # Create structured embeddings (not random noise)
                cond_tensor = torch.randn(1, seq_len, hidden_dim, dtype=torch.float32, device=device) * 0.5
                # Add positional pattern
                for i in range(seq_len):
                    cond_tensor[0, i] += torch.sin(torch.tensor(i / seq_len * 3.14159, device=device)) * 0.2
                pooled = torch.randn(1, hidden_dim, dtype=torch.float32, device=device) * 0.3
            else:  # stress_test  
                # Large conditioning for stress testing
                seq_len = min(size // 5, 200)
                hidden_dim = 1024  # Larger embedding dimension
                cond_tensor = torch.randn(1, seq_len, hidden_dim, dtype=torch.float32, device=device)
                pooled = torch.randn(1, hidden_dim, dtype=torch.float32, device=device)
                # Add extreme values for stress testing
                cond_tensor[0, 0] = torch.ones_like(cond_tensor[0, 0]) * 10.0
                
            # Authentic ComfyUI CONDITIONING format: list of [tensor, PooledDict]
            # Based on DeepWiki: each tuple contains a tensor and a PooledDict
            conditioning = [[
                cond_tensor, 
                {
                    "pooled_output": pooled,
                    # Add optional conditioning parameters following ComfyUI patterns
                    **({"strength": 1.0, "start_percent": 0.0, "end_percent": 1.0} if mode == "stress_test" else {})
                }
            ]]
            
            return conditioning
            
        except ImportError:
            # Numpy fallback maintaining authentic structure
            try:
                import numpy as np
                if mode == "simple":
                    seq_len, hidden_dim = 1, 768
                    cond_tensor = np.zeros((1, seq_len, hidden_dim), dtype=np.float32)
                    pooled = np.zeros((1, hidden_dim), dtype=np.float32)
                elif mode == "realistic":
                    seq_len = min(size // 10, 77)
                    hidden_dim = 768
                    cond_tensor = np.random.randn(1, seq_len, hidden_dim).astype(np.float32) * 0.5
                    pooled = np.random.randn(1, hidden_dim).astype(np.float32) * 0.3
                else:
                    seq_len = min(size // 5, 200)
                    hidden_dim = 1024
                    cond_tensor = np.random.randn(1, seq_len, hidden_dim).astype(np.float32)
                    pooled = np.random.randn(1, hidden_dim).astype(np.float32)
                
                return [[cond_tensor, {"pooled_output": pooled}]]
                
            except ImportError:
                # Ultimate fallback - structured description
                return [[
                    {
                        "tensor_type": "CONDITIONING_TENSOR", 
                        "shape": [1, min(size//10, 77), 768],
                        "dtype": "float32"
                    },
                    {
                        "pooled_output": {
                            "tensor_type": "POOLED_OUTPUT",
                            "shape": [1, 768],
                            "dtype": "float32"
                        },
                        "note": "Authentic ComfyUI CONDITIONING format - install torch for real tensors"
                    }
                ]]

    def _generate_metadata(self, output_type: str, mode: str, data: Any, size: int, seed: int) -> str:
        """Generate comprehensive metadata about the generated data"""
        metadata_parts = [
            f"Type: {output_type}",
            f"Mode: {mode}", 
            f"Size Parameter: {size}",
            f"Seed: {seed}"
        ]
        
        # Add data-specific information
        try:
            if hasattr(data, 'shape'):
                metadata_parts.append(f"Shape: {tuple(data.shape)}")
            elif hasattr(data, '__len__') and not isinstance(data, str):
                metadata_parts.append(f"Length: {len(data)}")
            elif isinstance(data, (int, float)):
                metadata_parts.append(f"Value: {data}")
            elif isinstance(data, str):
                metadata_parts.append(f"String Length: {len(data)}")
                
        except Exception:
            pass
        
        return " | ".join(metadata_parts)

    @classmethod
    def IS_CHANGED(cls, output_type, output_mode="realistic", custom_value="", 
                   size_parameter=512, seed=0, include_metadata=True):
        """Cache key for reproducible generation"""
        return f"{output_type}_{output_mode}_{hash(custom_value)}_{size_parameter}_{seed}_{include_metadata}"