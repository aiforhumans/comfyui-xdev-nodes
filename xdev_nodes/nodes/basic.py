from __future__ import annotations
from typing import Dict, Tuple, Any
import datetime

class HelloString:
    """
    Enhanced greeting node demonstrating XDev best practices.
    
    This node showcases:
    - Rich tooltip documentation
    - Optional customization parameters
    - Comprehensive error handling
    - Dynamic content generation
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {},
            "optional": {
                "custom_message": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Optional custom message to append to the greeting. Leave empty to use default ComfyUI greeting."
                }),
                "include_timestamp": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Include current timestamp in the greeting message. Useful for debugging and workflow tracking."
                }),
                "format_style": (["simple", "formal", "casual", "technical"], {
                    "default": "simple",
                    "tooltip": "Choose greeting format style. Simple: basic message, Formal: professional tone, Casual: friendly tone, Technical: includes system info."
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("greeting", "metadata")
    FUNCTION = "hello"
    CATEGORY = "XDev/Basic"
    DESCRIPTION = "Enhanced greeting generator with customizable formatting and optional timestamp"

    def hello(self, custom_message: str = "", include_timestamp: bool = False, format_style: str = "simple") -> Tuple[str, str]:
        """
        Generate customized greeting message with optional enhancements.
        
        Args:
            custom_message: Optional custom text to append
            include_timestamp: Whether to include current timestamp
            format_style: Formatting style for the greeting
            
        Returns:
            Tuple of (greeting_message, metadata_info)
        """
        try:
            # Base greeting based on style
            if format_style == "formal":
                base_greeting = "Greetings from ComfyUI!"
            elif format_style == "casual":
                base_greeting = "Hey there from ComfyUI! 👋"
            elif format_style == "technical":
                base_greeting = "ComfyUI Node System: Status Active"
            else:  # simple
                base_greeting = "Hello ComfyUI!"
            
            # Add custom message if provided
            if custom_message.strip():
                greeting = f"{base_greeting} {custom_message.strip()}"
            else:
                greeting = base_greeting
            
            # Add timestamp if requested
            metadata = f"Format: {format_style}"
            if include_timestamp:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                greeting = f"{greeting} (Generated: {timestamp})"
                metadata += f", Timestamp: {timestamp}"
            
            return (greeting, metadata)
            
        except Exception as e:
            error_msg = f"Error generating greeting: {str(e)}"
            return (error_msg, f"Error: {str(e)}")
    
    @classmethod
    def IS_CHANGED(cls, custom_message="", include_timestamp=False, format_style="simple"):
        # Include timestamp in cache key when timestamp is enabled to ensure refresh
        if include_timestamp:
            return datetime.datetime.now().isoformat()
        return f"{custom_message}_{format_style}"


class AnyPassthrough:
    """
    Robust passthrough node for any ComfyUI data type with advanced debugging capabilities.
    
    Features:
    - Universal data type support (IMAGE, STRING, INT, FLOAT, LATENT, MODEL, etc.)
    - Safe JSON serialization for ComfyUI compatibility
    - Comprehensive data analysis and reporting
    - Graceful error handling and fallback mechanisms
    - Performance-optimized caching system
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "value": ("*", {
                    "forceInput": True,  # This ensures ComfyUI treats it as a proper input
                    "tooltip": "Any input data to pass through unchanged. Supports all ComfyUI types: IMAGE tensors, text strings, numbers, latents, models, conditioning, etc."
                })
            },
            "optional": {
                "analysis_level": (["basic", "detailed", "debug"], {
                    "default": "basic",
                    "tooltip": "Level of data analysis: 'basic' shows type and size, 'detailed' adds shape/device info, 'debug' includes memory and performance data."
                }),
                "show_content_preview": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Include a preview of the actual data content (first few elements for arrays/tensors, truncated text for strings)."
                }),
                "track_performance": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Track processing time and memory usage. Useful for workflow optimization and debugging."
                }),
            }
        }

    RETURN_TYPES = ("*", "STRING", "STRING")
    RETURN_NAMES = ("output", "data_report", "performance_info")
    FUNCTION = "process"
    CATEGORY = "XDev/Basic"
    DESCRIPTION = "Universal passthrough with comprehensive data analysis and debugging capabilities"

    def process(self, value, analysis_level: str = "basic", show_content_preview: bool = False, track_performance: bool = False):
        """
        Process any input data with comprehensive analysis and safe passthrough.
        
        Args:
            value: Any input data to pass through
            analysis_level: Level of analysis detail
            show_content_preview: Whether to show data content preview
            track_performance: Whether to track performance metrics
            
        Returns:
            Tuple of (original_data, analysis_report, performance_info)
        """
        import time
        start_time = time.time() if track_performance else None
        
        try:
            # Generate data analysis report
            data_report = self._generate_data_report(value, analysis_level, show_content_preview)
            
            # Generate performance info if requested
            if track_performance:
                end_time = time.time()
                processing_time = (end_time - start_time) * 1000  # Convert to ms
                performance_info = f"Processing time: {processing_time:.2f}ms"
                
                # Add memory info if available
                try:
                    import psutil
                    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                    performance_info += f" | Memory: {memory_mb:.1f}MB"
                except ImportError:
                    performance_info += " | Memory: N/A (psutil not available)"
            else:
                performance_info = "Performance tracking disabled"
            
            return (value, data_report, performance_info)
            
        except Exception as e:
            error_report = f"Analysis error: {str(e)}"
            fallback_performance = "Error during processing"
            return (value, error_report, fallback_performance)

    def _generate_data_report(self, data, level: str, show_preview: bool) -> str:
        """Generate comprehensive data analysis report"""
        report_parts = []
        
        try:
            # Basic type information (always included)
            data_type = type(data).__name__
            report_parts.append(f"Type: {data_type}")
            
            # Basic size/shape information
            self._add_size_info(data, report_parts)
            
            # Detailed analysis
            if level in ["detailed", "debug"]:
                self._add_detailed_info(data, report_parts)
            
            # Debug level analysis
            if level == "debug":
                self._add_debug_info(data, report_parts)
            
            # Content preview
            if show_preview:
                self._add_content_preview(data, report_parts)
                
        except Exception as e:
            report_parts.append(f"Analysis error: {str(e)}")
        
        return " | ".join(report_parts) if report_parts else "No analysis available"

    def _add_size_info(self, data, report_parts: list):
        """Add size/shape information safely"""
        try:
            if hasattr(data, 'shape'):  # Tensors, numpy arrays
                shape_str = str(tuple(int(x) for x in data.shape))
                report_parts.append(f"Shape: {shape_str}")
                
                # Calculate total elements
                total_elements = 1
                for dim in data.shape:
                    total_elements *= int(dim)
                report_parts.append(f"Elements: {total_elements:,}")
                
            elif hasattr(data, '__len__') and not isinstance(data, str):
                length = len(data)
                report_parts.append(f"Length: {length:,}")
            elif isinstance(data, (int, float)):
                report_parts.append(f"Value: {data}")
            elif isinstance(data, str):
                char_count = len(data)
                word_count = len(data.split())
                report_parts.append(f"Chars: {char_count:,}, Words: {word_count:,}")
        except Exception:
            report_parts.append("Size: Unknown")

    def _add_detailed_info(self, data, report_parts: list):
        """Add detailed technical information"""
        try:
            # Module information
            module = getattr(type(data), '__module__', 'unknown')
            if module != 'builtins':
                report_parts.append(f"Module: {module}")
            
            # Tensor-specific details
            if hasattr(data, 'dtype'):
                report_parts.append(f"DType: {str(data.dtype)}")
            
            if hasattr(data, 'device'):
                report_parts.append(f"Device: {str(data.device)}")
                
            # Memory usage for tensors
            if hasattr(data, 'element_size') and hasattr(data, 'numel'):
                memory_bytes = data.element_size() * data.numel()
                memory_mb = memory_bytes / (1024 * 1024)
                if memory_mb >= 1:
                    report_parts.append(f"Memory: {memory_mb:.1f}MB")
                else:
                    memory_kb = memory_bytes / 1024
                    report_parts.append(f"Memory: {memory_kb:.1f}KB")
                    
        except Exception:
            pass  # Silently skip if details can't be retrieved

    def _add_debug_info(self, data, report_parts: list):
        """Add debug-level information"""
        try:
            # Object ID for tracking
            obj_id = hex(id(data))
            report_parts.append(f"ObjectID: {obj_id}")
            
            # Gradient information for tensors
            if hasattr(data, 'requires_grad'):
                report_parts.append(f"Gradients: {'enabled' if data.requires_grad else 'disabled'}")
            
            # Additional tensor properties
            if hasattr(data, 'is_contiguous'):
                report_parts.append(f"Contiguous: {data.is_contiguous()}")
                
        except Exception:
            pass  # Silently skip debug info on error

    def _add_content_preview(self, data, report_parts: list):
        """Add safe content preview"""
        try:
            if isinstance(data, str):
                preview = data[:50] + "..." if len(data) > 50 else data
                report_parts.append(f"Preview: '{preview}'")
            elif hasattr(data, 'shape') and len(data.shape) > 0:
                # For tensors/arrays, show first few values safely
                if hasattr(data, 'flatten'):
                    flat = data.flatten()
                    if len(flat) > 0:
                        preview_size = min(3, len(flat))
                        preview_vals = [f"{float(flat[i]):.3f}" for i in range(preview_size)]
                        preview_str = ", ".join(preview_vals)
                        if len(flat) > preview_size:
                            preview_str += "..."
                        report_parts.append(f"Values: [{preview_str}]")
            elif hasattr(data, '__len__') and len(data) > 0:
                # For lists/tuples
                preview_size = min(3, len(data))
                preview_items = [str(data[i])[:20] for i in range(preview_size)]
                if len(data) > preview_size:
                    preview_items.append("...")
                report_parts.append(f"Items: {preview_items}")
        except Exception:
            report_parts.append("Preview: Unable to generate")

    @classmethod
    def IS_CHANGED(cls, value, analysis_level="basic", show_content_preview=False, track_performance=False):
        """
        Generate cache key that's safe for JSON serialization.
        Uses only basic, serializable properties to avoid ComfyUI JSON errors.
        """
        try:
            # Create base cache key from settings
            cache_parts = [
                type(value).__name__,
                analysis_level,
                str(show_content_preview),
                str(track_performance)
            ]
            
            # Add safe shape information for tensors
            if hasattr(value, 'shape'):
                try:
                    shape_tuple = tuple(int(x) for x in value.shape)
                    cache_parts.append(f"shape{shape_tuple}")
                except:
                    cache_parts.append("shape_unknown")
            
            # Add safe size information for other containers
            elif hasattr(value, '__len__') and not isinstance(value, str):
                try:
                    cache_parts.append(f"len{len(value)}")
                except:
                    cache_parts.append("len_unknown")
            
            return "_".join(cache_parts)
            
        except Exception:
            # Ultimate fallback - always works
            return f"passthrough_{analysis_level}_{show_content_preview}_{track_performance}"