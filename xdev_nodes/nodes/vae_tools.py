from __future__ import annotations
from typing import Dict, Tuple, Any, Union
import json

class VAERoundTrip:
    """
    VAE Round-Trip Tool: LATENT → DECODE → SHOW → ENCODE → LATENT
    
    This node performs a complete VAE round-trip operation:
    1. Takes LATENT input and VAE
    2. Decodes LATENT to IMAGE (for visual inspection)
    3. Re-encodes IMAGE back to LATENT
    4. Returns both the decoded IMAGE and the re-encoded LATENT
    
    Perfect for:
    - Testing VAE quality and consistency
    - Visual inspection of latent representations
    - Debugging encode/decode cycles
    - Comparing original vs round-trip latents
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "latent": ("LATENT", {
                    "tooltip": "Input latent to decode and re-encode through VAE round-trip"
                }),
                "vae": ("VAE", {
                    "tooltip": "VAE model for decoding latent to image and encoding back to latent"
                })
            },
            "optional": {
                "show_stats": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Display statistics about the round-trip process (latent shapes, memory usage)"
                }),
                "quality_check": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Perform quality analysis comparing input vs output latent"
                }),
                "decode_only": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Only decode to image without re-encoding (useful for preview only)"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "STRING")
    RETURN_NAMES = ("decoded_image", "reencoded_latent", "process_info")
    FUNCTION = "vae_round_trip"
    CATEGORY = "XDev/VAE Tools"
    DESCRIPTION = "Complete VAE round-trip: LATENT → DECODE → IMAGE → ENCODE → LATENT with visual feedback"

    def vae_round_trip(self, latent, vae, show_stats: bool = True, 
                      quality_check: bool = False, decode_only: bool = False):
        """
        Perform VAE round-trip operation with comprehensive analysis.
        
        Args:
            latent: Input LATENT data to process
            vae: VAE model for encode/decode operations
            show_stats: Whether to display processing statistics
            quality_check: Whether to analyze quality differences
            decode_only: Whether to skip re-encoding step
            
        Returns:
            Tuple of (decoded_image, reencoded_latent, process_info)
        """
        try:
            process_steps = []
            
            # Step 1: Analyze input latent
            if show_stats:
                input_info = self._analyze_latent(latent, "Input")
                process_steps.append(input_info)
            
            # Step 2: Decode LATENT → IMAGE
            process_steps.append("🔄 DECODING: LATENT → IMAGE")
            try:
                decoded_image = vae.decode(latent["samples"])
                decode_success = True
                process_steps.append("✅ DECODE: Success")
                
                if show_stats:
                    image_info = self._analyze_image(decoded_image)
                    process_steps.append(image_info)
                    
            except Exception as e:
                process_steps.append(f"❌ DECODE ERROR: {str(e)}")
                # Create fallback black image
                decoded_image = self._create_fallback_image(latent)
                decode_success = False
            
            # Step 3: Re-encode IMAGE → LATENT (unless decode_only)
            if decode_only:
                process_steps.append("ℹ️ ENCODE: Skipped (decode_only=True)")
                reencoded_latent = latent  # Return original latent
            else:
                process_steps.append("🔄 ENCODING: IMAGE → LATENT")
                try:
                    # Encode the decoded image back to latent
                    reencoded_samples = vae.encode(decoded_image)
                    reencoded_latent = {"samples": reencoded_samples}
                    encode_success = True
                    process_steps.append("✅ ENCODE: Success")
                    
                    if show_stats:
                        output_info = self._analyze_latent(reencoded_latent, "Output")
                        process_steps.append(output_info)
                        
                except Exception as e:
                    process_steps.append(f"❌ ENCODE ERROR: {str(e)}")
                    reencoded_latent = latent  # Return original latent
                    encode_success = False
            
            # Step 4: Quality analysis (if requested and both operations succeeded)
            if quality_check and not decode_only and decode_success and encode_success:
                quality_info = self._analyze_quality(latent, reencoded_latent)
                process_steps.append(quality_info)
            
            # Generate comprehensive process info
            process_info = self._generate_process_info(process_steps, decode_success, 
                                                    encode_success if not decode_only else True)
            
            return (decoded_image, reencoded_latent, process_info)
            
        except Exception as e:
            error_msg = f"VAE Round-Trip Error: {str(e)}"
            fallback_image = self._create_fallback_image(latent)
            return (fallback_image, latent, error_msg)

    def _analyze_latent(self, latent: Dict, stage: str) -> str:
        """Analyze latent tensor properties"""
        try:
            samples = latent["samples"]
            shape = tuple(samples.shape)
            
            # Calculate memory usage
            if hasattr(samples, 'element_size') and hasattr(samples, 'numel'):
                memory_bytes = samples.element_size() * samples.numel()
                memory_mb = memory_bytes / (1024 * 1024)
                memory_info = f"{memory_mb:.2f} MB"
            else:
                memory_info = "Unknown"
            
            # Calculate value statistics
            try:
                if hasattr(samples, 'min') and hasattr(samples, 'max'):
                    min_val = float(samples.min())
                    max_val = float(samples.max())
                    mean_val = float(samples.mean()) if hasattr(samples, 'mean') else 0.0
                    stats_info = f"Range: {min_val:.3f} to {max_val:.3f}, Mean: {mean_val:.3f}"
                else:
                    stats_info = "Stats unavailable"
            except:
                stats_info = "Stats calculation failed"
            
            return f"📊 {stage} LATENT: Shape {shape}, Memory: {memory_info}, {stats_info}"
            
        except Exception as e:
            return f"❌ {stage} LATENT Analysis Error: {str(e)}"

    def _analyze_image(self, image) -> str:
        """Analyze decoded image properties"""
        try:
            shape = tuple(image.shape)
            
            # Calculate memory usage
            if hasattr(image, 'element_size') and hasattr(image, 'numel'):
                memory_bytes = image.element_size() * image.numel()
                memory_mb = memory_bytes / (1024 * 1024)
                memory_info = f"{memory_mb:.2f} MB"
            else:
                memory_info = "Unknown"
            
            # Image value range analysis
            try:
                if hasattr(image, 'min') and hasattr(image, 'max'):
                    min_val = float(image.min())
                    max_val = float(image.max())
                    
                    # Check if values are in 0-1 range (typical for ComfyUI)
                    if 0.0 <= min_val <= 1.0 and 0.0 <= max_val <= 1.0:
                        range_status = "✅ Valid range [0-1]"
                    else:
                        range_status = f"⚠️ Unusual range [{min_val:.3f}-{max_val:.3f}]"
                        
                    stats_info = f"{range_status}"
                else:
                    stats_info = "Range check unavailable"
            except:
                stats_info = "Range analysis failed"
            
            return f"🖼️ DECODED IMAGE: Shape {shape}, Memory: {memory_info}, {stats_info}"
            
        except Exception as e:
            return f"❌ IMAGE Analysis Error: {str(e)}"

    def _analyze_quality(self, original_latent: Dict, reencoded_latent: Dict) -> str:
        """Analyze quality differences between original and re-encoded latent"""
        try:
            orig_samples = original_latent["samples"]
            reenc_samples = reencoded_latent["samples"]
            
            # Shape comparison
            if orig_samples.shape != reenc_samples.shape:
                return f"⚠️ QUALITY: Shape mismatch - Original: {orig_samples.shape}, Re-encoded: {reenc_samples.shape}"
            
            # Statistical comparison
            try:
                if hasattr(orig_samples, 'mean') and hasattr(reenc_samples, 'mean'):
                    orig_mean = float(orig_samples.mean())
                    reenc_mean = float(reenc_samples.mean())
                    mean_diff = abs(orig_mean - reenc_mean)
                    
                    orig_std = float(orig_samples.std()) if hasattr(orig_samples, 'std') else 0.0
                    reenc_std = float(reenc_samples.std()) if hasattr(reenc_samples, 'std') else 0.0
                    std_diff = abs(orig_std - reenc_std)
                    
                    # Calculate difference magnitude
                    try:
                        if hasattr(orig_samples, 'sub'):
                            diff_tensor = orig_samples - reenc_samples
                            if hasattr(diff_tensor, 'abs') and hasattr(diff_tensor, 'mean'):
                                avg_abs_diff = float(diff_tensor.abs().mean())
                                max_abs_diff = float(diff_tensor.abs().max()) if hasattr(diff_tensor, 'max') else 0.0
                                
                                return (f"🔍 QUALITY CHECK: Mean diff: {mean_diff:.4f}, "
                                       f"Std diff: {std_diff:.4f}, "
                                       f"Avg abs diff: {avg_abs_diff:.4f}, "
                                       f"Max abs diff: {max_abs_diff:.4f}")
                        else:
                            return f"🔍 QUALITY CHECK: Mean diff: {mean_diff:.4f}, Std diff: {std_diff:.4f}"
                    except:
                        return f"🔍 QUALITY CHECK: Mean diff: {mean_diff:.4f}, Std diff: {std_diff:.4f}"
                        
                else:
                    return "🔍 QUALITY CHECK: Statistical comparison unavailable"
                    
            except Exception as e:
                return f"🔍 QUALITY CHECK: Analysis error - {str(e)}"
                
        except Exception as e:
            return f"❌ QUALITY Analysis Error: {str(e)}"

    def _create_fallback_image(self, latent: Dict):
        """Create a fallback black image when decoding fails"""
        try:
            # Try to use torch if available
            import torch
            
            # Estimate image size from latent (typical 8x downscaling)
            latent_shape = latent["samples"].shape
            if len(latent_shape) >= 4:
                batch, channels, height, width = latent_shape[:4]
                img_height, img_width = height * 8, width * 8
            else:
                # Default fallback size
                img_height, img_width = 512, 512
                batch = 1
            
            # Create black image in ComfyUI format [B, H, W, C]
            fallback = torch.zeros(batch, img_height, img_width, 3, dtype=torch.float32)
            return fallback
            
        except ImportError:
            # If torch not available, create a minimal mock
            return self._create_mock_image_object([1, 512, 512, 3])

    def _create_mock_image_object(self, shape: list):
        """Create a mock image object when torch is unavailable"""
        class MockImage:
            def __init__(self, shape):
                self.shape = tuple(shape)
                self.dtype = "float32"
                
            def min(self):
                return 0.0
                
            def max(self):
                return 0.0
                
            def __str__(self):
                return f"MockImage(shape={self.shape})"
                
        return MockImage(shape)

    def _generate_process_info(self, steps: list, decode_success: bool, 
                             encode_success: bool) -> str:
        """Generate comprehensive process information"""
        
        # Header
        info_lines = [
            "🔄 VAE ROUND-TRIP PROCESS REPORT",
            "=" * 50
        ]
        
        # Process steps
        info_lines.extend(steps)
        
        # Summary
        info_lines.extend([
            "",
            "📋 OPERATION SUMMARY:",
            f"  Decode Success: {'✅ Yes' if decode_success else '❌ No'}",
            f"  Encode Success: {'✅ Yes' if encode_success else '❌ No'}",
            f"  Overall Status: {'✅ Complete' if decode_success and encode_success else '⚠️ Partial' if decode_success or encode_success else '❌ Failed'}"
        ])
        
        # Usage tips
        if not decode_success:
            info_lines.extend([
                "",
                "💡 DECODE TROUBLESHOOTING:",
                "  • Check that VAE model is compatible with latent format",
                "  • Verify latent contains 'samples' key with proper tensor",
                "  • Try using a different VAE model"
            ])
            
        if decode_success and not encode_success:
            info_lines.extend([
                "",
                "💡 ENCODE TROUBLESHOOTING:",
                "  • Check that decoded image is in proper format [B,H,W,C]",
                "  • Verify image values are in expected range [0-1]",
                "  • Ensure sufficient memory for encoding operation"
            ])
        
        return "\n".join(info_lines)

    @classmethod
    def IS_CHANGED(cls, latent, vae, show_stats=True, quality_check=False, decode_only=False):
        """Cache key for ComfyUI caching system"""
        # Create hash based on inputs for proper caching
        latent_hash = hash(str(latent.get("samples", "none"))) if isinstance(latent, dict) else hash(str(latent))
        vae_hash = hash(str(vae)) if vae else 0
        return f"{latent_hash}_{vae_hash}_{show_stats}_{quality_check}_{decode_only}"


class VAEPreview:
    """
    VAE Preview Tool: Quick LATENT → IMAGE decoding for visual inspection
    
    Lightweight version focused on just decoding latents to images
    for quick preview and debugging purposes.
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "latent": ("LATENT", {
                    "tooltip": "Input latent to decode and preview as image"
                }),
                "vae": ("VAE", {
                    "tooltip": "VAE model for decoding latent to image"
                })
            },
            "optional": {
                "add_info_text": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Add informational text overlay showing latent properties"
                }),
                "preview_mode": (["full", "fast", "minimal"], {
                    "default": "full",
                    "tooltip": "Preview processing mode: full (complete analysis), fast (basic), minimal (decode only)"
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("preview_image", "latent_info")
    FUNCTION = "preview_latent"
    CATEGORY = "XDev/VAE Tools"
    DESCRIPTION = "Quick latent preview: LATENT → DECODE → IMAGE with optional analysis"

    def preview_latent(self, latent, vae, add_info_text: bool = True, 
                      preview_mode: str = "full"):
        """
        Decode latent to image for quick preview.
        
        Args:
            latent: Input LATENT data to preview
            vae: VAE model for decoding
            add_info_text: Whether to include informational text
            preview_mode: Level of processing detail
            
        Returns:
            Tuple of (preview_image, latent_info)
        """
        try:
            info_parts = []
            
            # Quick latent analysis
            if preview_mode in ["full", "fast"]:
                latent_analysis = self._quick_latent_analysis(latent)
                info_parts.append(latent_analysis)
            
            # Decode latent to image
            try:
                decoded_image = vae.decode(latent["samples"])
                info_parts.append("✅ DECODE: Successful")
                
                # Image analysis
                if preview_mode == "full":
                    image_analysis = self._quick_image_analysis(decoded_image)
                    info_parts.append(image_analysis)
                    
            except Exception as e:
                info_parts.append(f"❌ DECODE: Failed - {str(e)}")
                decoded_image = self._create_error_image(latent)
            
            # Generate info text
            if add_info_text:
                latent_info = "\n".join([
                    "🔍 VAE PREVIEW ANALYSIS",
                    "-" * 30
                ] + info_parts)
            else:
                latent_info = "Preview generated"
            
            return (decoded_image, latent_info)
            
        except Exception as e:
            error_msg = f"VAE Preview Error: {str(e)}"
            fallback_image = self._create_error_image(latent)
            return (fallback_image, error_msg)

    def _quick_latent_analysis(self, latent: Dict) -> str:
        """Quick analysis of latent properties"""
        try:
            samples = latent["samples"]
            shape = tuple(samples.shape)
            
            # Quick stats
            if hasattr(samples, 'numel'):
                element_count = samples.numel()
                size_info = f"{element_count:,} elements"
            else:
                size_info = "Size unknown"
            
            return f"📊 LATENT: {shape} - {size_info}"
            
        except Exception as e:
            return f"❌ Latent analysis error: {str(e)}"

    def _quick_image_analysis(self, image) -> str:
        """Quick analysis of decoded image"""
        try:
            shape = tuple(image.shape)
            
            # Quick value range check
            if hasattr(image, 'min') and hasattr(image, 'max'):
                min_val = float(image.min())
                max_val = float(image.max())
                range_info = f"Range: [{min_val:.2f}, {max_val:.2f}]"
            else:
                range_info = "Range: Unknown"
            
            return f"🖼️ IMAGE: {shape} - {range_info}"
            
        except Exception as e:
            return f"❌ Image analysis error: {str(e)}"

    def _create_error_image(self, latent: Dict):
        """Create an error placeholder image"""
        try:
            import torch
            
            # Create red error image
            error_image = torch.ones(1, 256, 256, 3, dtype=torch.float32)
            error_image[:, :, :, 0] = 1.0  # Red channel
            error_image[:, :, :, 1] = 0.0  # Green channel  
            error_image[:, :, :, 2] = 0.0  # Blue channel
            
            return error_image
            
        except ImportError:
            # Fallback mock
            class ErrorImage:
                def __init__(self):
                    self.shape = (1, 256, 256, 3)
                    
                def __str__(self):
                    return "ErrorImage(red placeholder)"
            
            return ErrorImage()

    @classmethod
    def IS_CHANGED(cls, latent, vae, add_info_text=True, preview_mode="full"):
        """Cache key for ComfyUI caching system"""
        latent_hash = hash(str(latent.get("samples", "none"))) if isinstance(latent, dict) else hash(str(latent))
        vae_hash = hash(str(vae)) if vae else 0
        return f"{latent_hash}_{vae_hash}_{add_info_text}_{preview_mode}"