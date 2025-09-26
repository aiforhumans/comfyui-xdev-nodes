from __future__ import annotations
from typing import Dict, Tuple, Any, Union, List
import json

class OutputDev:
    """
    Universal output/sink node for testing and debugging any ComfyUI data type.
    
    This development node can receive and display information about any type of 
    ComfyUI data including IMAGE, STRING, INT, FLOAT, LATENT, MODEL, CONDITIONING, etc.
    Perfect for workflow debugging and connection testing.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        # Define all ComfyUI types that the OutputDev can accept
        # Using a union type list instead of "*" for better compatibility
        accepted_types = [
            "STRING", "INT", "FLOAT", "BOOLEAN",
            "IMAGE", "MASK", "LATENT", 
            "MODEL", "CLIP", "VAE", "CONDITIONING",
            "CONTROL_NET", "STYLE_MODEL", "UPSCALE_MODEL",
            "SAMPLER", "SIGMAS", "NOISE",
            "*"  # Keep * as fallback for any other types
        ]
        
        return {
            "required": {
                "input_1": (accepted_types, {
                    "forceInput": True,
                    "tooltip": "Primary input - accepts any ComfyUI data type for analysis and display"
                })
            },
            "optional": {
                "input_2": (accepted_types, {
                    "forceInput": True,
                    "tooltip": "Optional secondary input for comparing multiple data streams"
                }),
                "input_3": (accepted_types, {
                    "forceInput": True, 
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
    CATEGORY = "XDev/Development"
    DESCRIPTION = "Universal debugging output node - accepts and analyzes any ComfyUI data type"

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

    def _show_content_preview(self, data: Any):
        """Show a safe preview of the data content"""
        try:
            print("\n📋 CONTENT PREVIEW:")
            
            if isinstance(data, str):
                preview = data[:100] + "..." if len(data) > 100 else data
                print(f"Text: '{preview}'")
            elif hasattr(data, 'shape') and len(data.shape) > 0:
                # For tensors/arrays
                if hasattr(data, 'flatten'):
                    flat = data.flatten()
                    if len(flat) > 0:
                        preview_size = min(5, len(flat))
                        values = []
                        for i in range(preview_size):
                            try:
                                val = float(flat[i])
                                values.append(f"{val:.4f}")
                            except:
                                values.append(str(flat[i]))
                        preview_str = ", ".join(values)
                        if len(flat) > preview_size:
                            preview_str += f", ... ({len(flat)-preview_size} more)"
                        print(f"Values: [{preview_str}]")
                        
                        # Show statistics for numeric data
                        try:
                            if hasattr(data, 'min') and hasattr(data, 'max'):
                                min_val = float(data.min())
                                max_val = float(data.max())
                                mean_val = float(data.mean()) if hasattr(data, 'mean') else 'N/A'
                                print(f"Range: {min_val:.4f} to {max_val:.4f}")
                                print(f"Mean: {mean_val:.4f}" if mean_val != 'N/A' else "Mean: N/A")
                        except:
                            pass
                            
            elif hasattr(data, '__len__') and len(data) > 0:
                # For lists/tuples
                preview_size = min(3, len(data))
                items = []
                for i in range(preview_size):
                    item_str = str(data[i])
                    if len(item_str) > 50:
                        item_str = item_str[:47] + "..."
                    items.append(item_str)
                if len(data) > preview_size:
                    items.append(f"... ({len(data)-preview_size} more items)")
                print(f"Items: {items}")
                
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
                    "LIST", "DICT", "MOCK_TENSOR"
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
                    "tooltip": "Seed for reproducible random data generation"
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
    CATEGORY = "XDev/Development"
    DESCRIPTION = "Universal test data generator - creates any ComfyUI data type for connection testing"

    def generate_data(self, output_type: str, output_mode: str = "realistic", 
                     custom_value: str = "", size_parameter: int = 512, 
                     seed: int = 0, include_metadata: bool = True):
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
            elif output_type == "MOCK_TENSOR":
                data = self._generate_mock_tensor(output_mode, size_parameter)
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
        """Generate mock IMAGE tensor (ComfyUI format: B,H,W,C)"""
        try:
            # Try to create actual tensor if torch is available
            import torch
            
            if mode == "simple":
                # Single pixel image
                return torch.zeros(1, 1, 1, 3, dtype=torch.float32)
            elif mode == "realistic":
                # Standard image size with random values
                h = w = min(size, 1024)  # Cap at 1024 for memory
                return torch.rand(1, h, w, 3, dtype=torch.float32)
            else:  # stress_test
                # Large image or unusual dimensions
                return torch.rand(1, size, size, 3, dtype=torch.float32)
                
        except ImportError:
            # Fallback: create mock tensor object
            return self._create_mock_tensor_object([1, size, size, 3], "image")

    def _generate_latent(self, mode: str, size: int):
        """Generate mock LATENT dict"""
        try:
            import torch
            
            # ComfyUI latent format
            latent_size = size // 8  # Typical VAE downscaling
            
            if mode == "simple":
                samples = torch.zeros(1, 4, 8, 8, dtype=torch.float32)
            elif mode == "realistic":
                samples = torch.randn(1, 4, latent_size, latent_size, dtype=torch.float32)
            else:  # stress_test
                samples = torch.randn(1, 4, latent_size, latent_size, dtype=torch.float32) * 10
            
            return {"samples": samples}
            
        except ImportError:
            # Fallback mock latent
            return {
                "samples": self._create_mock_tensor_object([1, 4, size//8, size//8], "latent")
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

    def _generate_mock_tensor(self, mode: str, size: int):
        """Generate mock tensor object for testing"""
        if mode == "simple":
            shape = [1, 1, 1]
        elif mode == "realistic":
            shape = [1, size, size, 3]
        else:  # stress_test
            shape = [1, size, size, size, 4]  # 4D tensor
        
        return self._create_mock_tensor_object(shape, "mock")

    def _create_mock_tensor_object(self, shape: list, tensor_type: str):
        """Create a mock tensor object that behaves like a real tensor"""
        class MockTensor:
            def __init__(self, shape, tensor_type):
                self.shape = tuple(shape)
                self.dtype = "float32"
                self.device = "cpu"
                self.requires_grad = False
                self.tensor_type = tensor_type
                
            def numel(self):
                result = 1
                for dim in self.shape:
                    result *= dim
                return result
            
            def element_size(self):
                return 4  # float32
                
            def is_contiguous(self):
                return True
                
            def flatten(self):
                # Return a simple list for preview
                import random
                return [random.uniform(0, 1) for _ in range(min(10, self.numel()))]
            
            def __str__(self):
                return f"MockTensor({self.tensor_type}, shape={self.shape})"
                
        return MockTensor(shape, tensor_type)

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
        """Generate MASK data (similar to IMAGE but single channel)"""
        try:
            import torch
            
            if mode == "simple":
                return torch.ones(1, 1, 1, dtype=torch.float32)
            elif mode == "realistic":
                h = w = min(size, 1024)
                return torch.rand(1, h, w, dtype=torch.float32)
            else:  # stress_test
                return torch.rand(1, size, size, dtype=torch.float32)
                
        except ImportError:
            # Fallback: create mock mask object
            return self._create_mock_tensor_object([1, size, size], "mask")

    def _generate_model(self, mode: str):
        """Generate mock MODEL object"""
        class MockModel:
            def __init__(self, mode):
                self.mode = mode
                self.model_type = "mock_model"
                self.device = "cpu"
                self.dtype = "float32"
                
            def __str__(self):
                return f"MockModel(mode={self.mode})"
                
            def to(self, device):
                self.device = str(device)
                return self
                
            def parameters(self):
                return []
                
        return MockModel(mode)

    def _generate_conditioning(self, mode: str, size: int):
        """Generate CONDITIONING data (list of conditioning tensors)"""
        try:
            import torch
            
            if mode == "simple":
                # Simple conditioning with single token
                cond_tensor = torch.randn(1, 1, 768, dtype=torch.float32)
            elif mode == "realistic":
                # Realistic conditioning with multiple tokens
                seq_len = min(size // 10, 77)  # Typical max 77 tokens
                cond_tensor = torch.randn(1, seq_len, 768, dtype=torch.float32)
            else:  # stress_test
                # Large conditioning
                seq_len = min(size // 5, 200)
                cond_tensor = torch.randn(1, seq_len, 1024, dtype=torch.float32)
            
            # ComfyUI conditioning format: list of [tensor, dict]
            return [[cond_tensor, {"pooled_output": torch.randn(1, 768, dtype=torch.float32)}]]
            
        except ImportError:
            # Fallback: create mock conditioning
            mock_tensor = self._create_mock_tensor_object([1, size//10, 768], "conditioning")
            return [[mock_tensor, {"pooled_output": mock_tensor}]]

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