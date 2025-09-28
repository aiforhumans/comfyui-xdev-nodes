from ..categories import NodeCategories
"""
XDev ComfyUI-Compatible Face Swap Node

Uses proper ComfyUI model management with InsightFace loader integration.
This node accepts loaded InsightFace models from loader nodes.
"""

from typing import Dict, Any, List, Tuple
import os

# XDev framework imports
from ..performance import performance_monitor, cached_operation
from ..mixins import ImageProcessingNode
from ..utils import get_numpy, get_torch

class XDEV_InsightFaceFaceSwap(ImageProcessingNode):
    """
    InsightFace Professional Face Swap (XDev)
    
    Professional face swapping using loaded InsightFace models.
    Integrates with ComfyUI model management system via loader nodes.
    """
    
    # Blending strength presets
    _BLEND_MODES = {
        "natural": "Natural blending (recommended)",
        "strong": "Strong replacement",
        "subtle": "Subtle modification", 
        "precise": "Precise face-only swap",
        "adaptive": "Adaptive strength based on face size"
    }
    
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "source_image": ("IMAGE", {
                    "tooltip": "Source image containing the face to extract"
                }),
                "target_image": ("IMAGE", {
                    "tooltip": "Target image where the face will be swapped"
                }),
                "analysis_model": ("INSIGHTFACE_ANALYSIS", {
                    "tooltip": "Loaded InsightFace analysis model from loader node"
                }),
                "confidence_threshold": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Minimum confidence for face detection"
                }),
                "blend_mode": (list(cls._BLEND_MODES.keys()), {
                    "default": "natural",
                    "tooltip": "Face blending strategy"
                })
            },
            "optional": {
                "swapper_model": ("INSIGHTFACE_SWAPPER", {
                    "tooltip": "Optional loaded InsightFace swapper model for professional swapping"
                }),
                "blend_strength": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Face swap strength (1.0 = full replacement)"
                }),
                "edge_feathering": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Edge blending softness"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("swapped_image", "swap_info", "face_analysis")
    FUNCTION = "swap_faces"
    CATEGORY = NodeCategories.INSIGHTFACE_FACESWAP
    DESCRIPTION = "Professional face swapping using loaded InsightFace models"
    
    @performance_monitor("insightface_face_swap")
    def swap_faces(self, source_image, target_image, analysis_model: Dict, confidence_threshold: float,
                   blend_mode: str, swapper_model: Dict = None, blend_strength: float = 0.8, 
                   edge_feathering: float = 0.3) -> Tuple[Any, str, str]:
        """Perform professional face swapping using loaded InsightFace models."""
        try:
            # Validate analysis model
            if analysis_model.get("error"):
                return target_image, f"Analysis Model Error: {analysis_model['error']}", "Model loading failed"
            
            analysis_wrapper = analysis_model.get("model")
            if not analysis_wrapper or not analysis_wrapper.is_loaded():
                return target_image, "Analysis model not loaded", "Analysis model unavailable"
            
            numpy = get_numpy()
            if numpy is None:
                return target_image, "NumPy not available", "Missing dependencies"
            
            # Convert images to numpy format
            source_np = self._convert_image_to_numpy(source_image)
            target_np = self._convert_image_to_numpy(target_image)
            
            if source_np is None or target_np is None:
                return target_image, "Image conversion failed", "Invalid image format"
            
            # Detect faces in both images
            source_faces = analysis_wrapper.model.get(source_np)
            target_faces = analysis_wrapper.model.get(target_np)
            
            # Filter faces by confidence
            source_faces = [f for f in source_faces if f.det_score >= confidence_threshold]
            target_faces = [f for f in target_faces if f.det_score >= confidence_threshold]
            
            if not source_faces:
                return target_image, f"No faces detected in source image (confidence ≥ {confidence_threshold:.2f})", "Source face detection failed"
            
            if not target_faces:
                return target_image, f"No faces detected in target image (confidence ≥ {confidence_threshold:.2f})", "Target face detection failed"
            
            # Select best faces (highest confidence)
            source_face = max(source_faces, key=lambda f: f.det_score)
            target_face = max(target_faces, key=lambda f: f.det_score)
            
            # Perform face swap
            if swapper_model and not swapper_model.get("error"):
                # Use professional InsightFace swapper if available
                result_image, swap_info = self._professional_face_swap(
                    source_np, target_np, source_face, target_face, 
                    swapper_model, blend_strength, edge_feathering
                )
            else:
                # Use enhanced manual swapping
                result_image, swap_info = self._enhanced_manual_swap(
                    source_np, target_np, source_face, target_face,
                    blend_mode, blend_strength, edge_feathering
                )
            
            # Convert result back to tensor
            result_tensor = self._convert_numpy_to_tensor(result_image, target_image)
            
            # Generate analysis info
            analysis_info = (
                f"Source: {source_face.det_score:.3f} confidence | "
                f"Target: {target_face.det_score:.3f} confidence | "
                f"Model: {analysis_model.get('model_name', 'Unknown')} | "
                f"Swapper: {'Professional' if swapper_model and not swapper_model.get('error') else 'Manual'}"
            )
            
            return result_tensor, swap_info, analysis_info
            
        except Exception as e:
            error_msg = f"InsightFace Face Swap Error: {str(e)}"
            return target_image, error_msg, str(e)
    
    def _convert_image_to_numpy(self, image):
        """Convert ComfyUI image tensor to numpy array for InsightFace."""
        try:
            if hasattr(image, 'cpu'):
                image_np = image.cpu().numpy()
                if len(image_np.shape) == 4:  # [B, H, W, C]
                    image_np = image_np[0]  # Take first batch
                # Convert from [0,1] to [0,255] uint8
                return (image_np * 255).astype('uint8')
            else:
                return image
        except Exception as e:
            print(f"Image conversion error: {e}")
            return None
    
    def _convert_numpy_to_tensor(self, image_np, reference_tensor):
        """Convert numpy array back to ComfyUI tensor format."""
        try:
            torch = get_torch()
            if torch is None:
                return reference_tensor
            
            # Convert from uint8 [0,255] to float32 [0,1]
            image_float = image_np.astype('float32') / 255.0
            result_tensor = torch.from_numpy(image_float)
            
            # Add batch dimension if reference had one
            if len(reference_tensor.shape) == 4:
                result_tensor = result_tensor.unsqueeze(0)
            
            return result_tensor
        except Exception as e:
            print(f"Tensor conversion error: {e}")
            return reference_tensor
    
    def _professional_face_swap(self, source_image, target_image, source_face, target_face,
                               swapper_model: Dict, blend_strength: float, edge_feathering: float) -> Tuple[Any, str]:
        """Professional face swap using InsightFace FaceSwapper model."""
        try:
            swapper_wrapper = swapper_model.get("model")
            if not swapper_wrapper or not swapper_wrapper.is_loaded():
                return self._enhanced_manual_swap(source_image, target_image, source_face, target_face,
                                                "natural", blend_strength, edge_feathering)
            
            # Check if we have a true FaceSwapper or analysis model used for swapping
            if hasattr(swapper_wrapper.model, 'get') and hasattr(swapper_wrapper.model.get, '__call__'):
                # Try to use InsightFace's professional swapper
                try:
                    swapped_image = swapper_wrapper.model.get(target_image, target_face, source_face, paste_back=True)
                except Exception as e:
                    print(f"Professional swapper failed: {e}, falling back to manual swap")
                    return self._enhanced_manual_swap(source_image, target_image, source_face, target_face,
                                                    "natural", blend_strength, edge_feathering)
            else:
                # Fall back to manual swapping
                return self._enhanced_manual_swap(source_image, target_image, source_face, target_face,
                                                "natural", blend_strength, edge_feathering)
            
            # Apply blend strength if < 1.0
            if blend_strength < 1.0:
                numpy = get_numpy()
                if numpy is not None:
                    # Create blend mask from target face bbox
                    bbox = target_face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    
                    mask = numpy.zeros(target_image.shape[:2], dtype=numpy.float32)
                    mask[y1:y2, x1:x2] = 1.0
                    
                    # Apply feathering
                    if edge_feathering > 0:
                        try:
                            import cv2
                            kernel_size = int((x2-x1 + y2-y1) * edge_feathering * 0.02)
                            if kernel_size > 0:
                                mask = cv2.GaussianBlur(mask, (kernel_size*2+1, kernel_size*2+1), 0)
                        except ImportError:
                            pass  # Skip feathering if OpenCV not available
                    
                    # Blend with original
                    mask_3d = mask[:, :, numpy.newaxis] * blend_strength
                    swapped_image = (swapped_image * mask_3d + target_image * (1 - mask_3d)).astype('uint8')
            
            model_name = swapper_model.get("model_name", "Unknown")
            swap_info = f"Professional InsightFace swap ({model_name}) - Strength: {blend_strength:.2f}, Feather: {edge_feathering:.2f}"
            
            return swapped_image, swap_info
            
        except Exception as e:
            print(f"Professional face swap error: {e}")
            return self._enhanced_manual_swap(source_image, target_image, source_face, target_face,
                                            "natural", blend_strength, edge_feathering)
    
    def _enhanced_manual_swap(self, source_image, target_image, source_face, target_face,
                             blend_mode: str, blend_strength: float, edge_feathering: float) -> Tuple[Any, str]:
        """Enhanced manual face swapping using InsightFace landmarks."""
        try:
            numpy = get_numpy()
            if numpy is None:
                return target_image, "NumPy not available for manual swapping"
            
            # Get face regions
            source_bbox = source_face.bbox.astype(int)
            target_bbox = target_face.bbox.astype(int)
            
            sx1, sy1, sx2, sy2 = source_bbox
            tx1, ty1, tx2, ty2 = target_bbox
            
            # Extract face regions
            source_region = source_image[sy1:sy2, sx1:sx2]
            target_region = target_image[ty1:ty2, tx1:tx2]
            
            # Resize source face to match target face size
            target_h, target_w = target_region.shape[:2]
            
            try:
                import cv2
                resized_source = cv2.resize(source_region, (target_w, target_h))
                
                # Create blend mask
                mask = numpy.ones((target_h, target_w), dtype=numpy.float32)
                
                # Apply feathering
                if edge_feathering > 0:
                    kernel_size = int(min(target_w, target_h) * edge_feathering * 0.1)
                    if kernel_size > 0:
                        mask = cv2.GaussianBlur(mask, (kernel_size*2+1, kernel_size*2+1), 0)
                
                # Apply blend mode
                if blend_mode == "natural":
                    alpha = mask * blend_strength * 0.85  # Slightly softer for natural look
                elif blend_mode == "strong":
                    alpha = mask * blend_strength
                elif blend_mode == "subtle": 
                    alpha = mask * blend_strength * 0.6
                elif blend_mode == "precise":
                    # Use landmarks for more precise masking if available
                    if hasattr(source_face, 'kps') and source_face.kps is not None:
                        # Create more precise mask from landmarks
                        landmarks = source_face.kps
                        mask = self._create_landmark_mask(landmarks, (target_h, target_w), source_bbox, target_bbox)
                    alpha = mask * blend_strength
                elif blend_mode == "adaptive":
                    # Adaptive strength based on face size
                    face_size = target_w * target_h
                    adaptive_strength = min(1.0, blend_strength * (1.0 + face_size / 50000))
                    alpha = mask * adaptive_strength
                else:
                    alpha = mask * blend_strength
                
                # Blend faces
                alpha_3d = alpha[:, :, numpy.newaxis]
                blended_region = (resized_source * alpha_3d + target_region * (1 - alpha_3d)).astype('uint8')
                
                # Place blended face back into target image
                result_image = target_image.copy()
                result_image[ty1:ty2, tx1:tx2] = blended_region
                
                swap_info = f"Enhanced manual swap ({blend_mode}) - Strength: {blend_strength:.2f}, Feather: {edge_feathering:.2f}"
                return result_image, swap_info
                
            except ImportError:
                # Fallback without OpenCV
                result_image = target_image.copy()
                # Simple replacement without advanced blending
                resized_source = source_region  # Use original size
                if resized_source.shape[:2] == target_region.shape[:2]:
                    alpha = blend_strength
                    result_image[ty1:ty2, tx1:tx2] = (resized_source * alpha + target_region * (1 - alpha)).astype('uint8')
                
                return result_image, f"Basic face swap (no OpenCV) - Strength: {blend_strength:.2f}"
        
        except Exception as e:
            print(f"Manual face swap error: {e}")
            return target_image, f"Manual swap failed: {str(e)}"
    
    def _create_landmark_mask(self, landmarks, mask_shape, source_bbox, target_bbox):
        """Create precise face mask from landmarks."""
        try:
            numpy = get_numpy()
            import cv2
            
            if numpy is None:
                return numpy.ones(mask_shape, dtype=numpy.float32)
            
            # Scale landmarks from source to target face region
            sx1, sy1, sx2, sy2 = source_bbox
            tx1, ty1, tx2, ty2 = target_bbox
            
            scale_x = (tx2 - tx1) / (sx2 - sx1)
            scale_y = (ty2 - ty1) / (sy2 - sy1)
            
            # Transform landmarks to target face coordinates
            scaled_landmarks = []
            for point in landmarks:
                x, y = point
                # Translate to origin, scale, then translate to target
                new_x = (x - sx1) * scale_x
                new_y = (y - sy1) * scale_y
                scaled_landmarks.append([new_x, new_y])
            
            # Create mask from landmarks
            mask = numpy.zeros(mask_shape, dtype=numpy.uint8)
            points = numpy.array(scaled_landmarks, dtype=numpy.int32)
            
            # Use convex hull of landmarks
            hull = cv2.convexHull(points)
            cv2.fillPoly(mask, [hull], 255)
            
            return mask.astype(numpy.float32) / 255.0
        
        except Exception as e:
            print(f"Landmark mask creation error: {e}")
            numpy = get_numpy()
            return numpy.ones(mask_shape, dtype=numpy.float32) if numpy else None


# Node mappings 
NODE_CLASS_MAPPINGS = {
    "XDEV_InsightFaceFaceSwap": XDEV_InsightFaceFaceSwap
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_InsightFaceFaceSwap": "InsightFace Face Swap (XDev)"
}