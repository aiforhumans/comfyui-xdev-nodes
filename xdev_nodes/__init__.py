"""
XDev Nodes - ComfyUI Development Toolkit
Professional node development patterns and utilities for ComfyUI workflows.
"""

# Add debug logging for loading process
import sys
def debug_print(message):
    """Print debug messages during loading"""
    print(f"[XDev Debug] {message}")
    sys.stdout.flush()

debug_print("Starting XDev Nodes initialization...")
debug_print("Loading performance utilities...")
try:
    from . import utils
    debug_print("✅ Performance utilities loaded")
except Exception as e:
    debug_print(f"⚠️ Performance utilities failed to load: {e}")

# Optimized imports grouped by functionality
debug_print("Loading basic nodes...")
from .nodes.basic import HelloString, AnyPassthrough
debug_print("✅ Basic nodes loaded")

debug_print("Loading image processing...")
from .nodes.image import PickByBrightness, ImageResize, ImageCrop, ImageRotate, ImageBlend, ImageSplit, ImageTile
debug_print("✅ Image processing loaded")

debug_print("Loading text processing...")
from .nodes.text import AppendSuffix, TextCase
debug_print("✅ Text processing loaded")

debug_print("Loading math operations...")
from .nodes.math import MathBasic
debug_print("✅ Math operations loaded")

debug_print("Loading development tools...")
from .nodes.dev_nodes import OutputDev, InputDev
debug_print("✅ Development tools loaded")

debug_print("Loading VAE tools...")
from .nodes.vae_tools import VAERoundTrip, VAEPreview
debug_print("✅ VAE tools loaded")

debug_print("Loading prompt tools...")
from .nodes.prompt import (
    PromptCombiner, PromptWeighter, PromptCleaner, 
    PromptAnalyzer, PromptRandomizer, PersonBuilder, StyleBuilder,
    PromptMatrix, PromptInterpolator, PromptScheduler, 
    PromptAttention, PromptChainOfThought, PromptFewShot,
    LLMPersonBuilder, LLMStyleBuilder
)
debug_print("✅ Prompt tools loaded")

debug_print("Loading LLM integrations...")
from .nodes.llm_integration import LMStudioChat, LLMPromptAssistant, LLMContextualBuilder, LLMSDXLPhotoEnhancer
debug_print("✅ LLM integrations loaded")

# If you add frontend assets, keep this path relative to this package root.
WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "XDEV_HelloString": HelloString,
    "XDEV_AnyPassthrough": AnyPassthrough,
    "XDEV_PickByBrightness": PickByBrightness,
    "XDEV_AppendSuffix": AppendSuffix,
    "XDEV_OutputDev": OutputDev,
    "XDEV_InputDev": InputDev,
    "XDEV_VAERoundTrip": VAERoundTrip,
    "XDEV_VAEPreview": VAEPreview,
    # Phase 1 Foundation Nodes
    "XDEV_TextCase": TextCase,
    "XDEV_MathBasic": MathBasic,
    # Phase 2 Image Control Nodes
    "XDEV_ImageResize": ImageResize,
    "XDEV_ImageCrop": ImageCrop,
    "XDEV_ImageRotate": ImageRotate,
    "XDEV_ImageBlend": ImageBlend,
    "XDEV_ImageSplit": ImageSplit,
    "XDEV_ImageTile": ImageTile,
    # Phase 3 Prompt Tool Nodes
    "XDEV_PromptCombiner": PromptCombiner,
    "XDEV_PromptWeighter": PromptWeighter,
    "XDEV_PromptCleaner": PromptCleaner,
    "XDEV_PromptAnalyzer": PromptAnalyzer,
    "XDEV_PromptRandomizer": PromptRandomizer,
    # Template Builder Nodes
    "XDEV_PersonBuilder": PersonBuilder,
    "XDEV_StyleBuilder": StyleBuilder,
    # Phase 4 Advanced Prompt Nodes
    "XDEV_PromptMatrix": PromptMatrix,
    "XDEV_PromptInterpolator": PromptInterpolator,
    "XDEV_PromptScheduler": PromptScheduler,
    "XDEV_PromptAttention": PromptAttention,
    "XDEV_PromptChainOfThought": PromptChainOfThought,
    "XDEV_PromptFewShot": PromptFewShot,
    # Phase 5 LLM Integration Nodes
    "XDEV_LMStudioChat": LMStudioChat,
    "XDEV_LLMPromptAssistant": LLMPromptAssistant,
    "XDEV_LLMContextualBuilder": LLMContextualBuilder,
    "XDEV_LLMSDXLPhotoEnhancer": LLMSDXLPhotoEnhancer,
    # Phase 6 LLM-Enhanced Prompt Tools
    "XDEV_LLMPersonBuilder": LLMPersonBuilder,
    "XDEV_LLMStyleBuilder": LLMStyleBuilder,
}

debug_print("Registering node mappings...")

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_HelloString": "Hello String (XDev)",
    "XDEV_AnyPassthrough": "Any Passthrough (XDev)",
    "XDEV_PickByBrightness": "Pick Image by Brightness (XDev)",
    "XDEV_AppendSuffix": "Append Suffix (XDev)",
    "XDEV_OutputDev": "Output Dev (XDev)",
    "XDEV_InputDev": "Input Dev (XDev)",
    "XDEV_VAERoundTrip": "VAE Round-Trip (XDev)",
    "XDEV_VAEPreview": "VAE Preview (XDev)",
    # Phase 1 Foundation Nodes
    "XDEV_TextCase": "Text Case Converter (XDev)",
    "XDEV_MathBasic": "Math Basic Operations (XDev)",
    # Phase 2 Image Control Nodes
    "XDEV_ImageResize": "Image Resize (XDev)",
    "XDEV_ImageCrop": "Image Crop (XDev)",
    "XDEV_ImageRotate": "Image Rotate (XDev)",
    "XDEV_ImageBlend": "Image Blend (XDev)",
    "XDEV_ImageSplit": "Image Split (XDev)",
    "XDEV_ImageTile": "Image Tile (XDev)",
    # Phase 3 Prompt Tool Nodes
    "XDEV_PromptCombiner": "Prompt Combiner (XDev)",
    "XDEV_PromptWeighter": "Prompt Weighter (XDev)",
    "XDEV_PromptCleaner": "Prompt Cleaner (XDev)",
    "XDEV_PromptAnalyzer": "Prompt Analyzer (XDev)",
    "XDEV_PromptRandomizer": "Prompt Randomizer (XDev)",
    # Template Builder Nodes
    "XDEV_PersonBuilder": "Person Builder (XDev)",
    "XDEV_StyleBuilder": "Style Builder (XDev)",
    # Phase 4 Advanced Prompt Nodes
    "XDEV_PromptMatrix": "Prompt Matrix (XDev)",
    "XDEV_PromptInterpolator": "Prompt Interpolator (XDev)",
    "XDEV_PromptScheduler": "Prompt Scheduler (XDev)",
    "XDEV_PromptAttention": "Prompt Attention (XDev)",
    "XDEV_PromptChainOfThought": "Prompt Chain-of-Thought (XDev)",
    "XDEV_PromptFewShot": "Prompt Few-Shot (XDev)",
    # Phase 5 LLM Integration Nodes
    "XDEV_LMStudioChat": "LM Studio Chat (XDev)",
    # Phase 6 LLM-Enhanced Prompt Tools
    "XDEV_LLMPromptAssistant": "LLM Prompt Assistant (XDev)",
    "XDEV_LLMContextualBuilder": "LLM Contextual Builder (XDev)",
    "XDEV_LLMSDXLPhotoEnhancer": "LLM SDXL Photo Enhancer (XDev)",
    "XDEV_LLMPersonBuilder": "LLM Person Builder (XDev)",
    "XDEV_LLMStyleBuilder": "LLM Style Builder (XDev)",
}

debug_print(f"✅ XDev Nodes initialization complete! Registered {len(NODE_CLASS_MAPPINGS)} nodes:")
for node_id, display_name in NODE_DISPLAY_NAME_MAPPINGS.items():
    debug_print(f"  • {node_id} → {display_name}")

# Add custom API routes for debugging
try:
    from aiohttp import web
    from server import PromptServer
    
    @PromptServer.instance.routes.get("/xdev/status")
    async def get_xdev_status(request):
        """Get XDev nodes status and performance info"""
        return web.json_response({
            "status": "active",
            "nodes_registered": len(NODE_CLASS_MAPPINGS),
            "nodes": list(NODE_DISPLAY_NAME_MAPPINGS.keys()),
            "version": "v0.2.0",
            "features": ["lazy_evaluation", "advanced_inputs", "performance_optimized"],
            "debug_enabled": True
        })
    
    @PromptServer.instance.routes.get("/xdev/nodes")
    async def get_xdev_nodes(request):
        """Get detailed information about all XDev nodes"""
        node_info = {}
        for node_id, node_class in NODE_CLASS_MAPPINGS.items():
            node_info[node_id] = {
                "display_name": NODE_DISPLAY_NAME_MAPPINGS[node_id],
                "category": getattr(node_class, 'CATEGORY', 'Unknown'),
                "description": getattr(node_class, 'DESCRIPTION', ''),
                "function": getattr(node_class, 'FUNCTION', ''),
                "return_types": getattr(node_class, 'RETURN_TYPES', ()),
                "output_node": getattr(node_class, 'OUTPUT_NODE', False)
            }
        return web.json_response(node_info)
    
    debug_print("✅ Custom API endpoints registered: /xdev/status, /xdev/nodes")
except Exception as e:
    debug_print(f"⚠️ Could not register API endpoints: {e}")

debug_print("XDev Nodes ready for ComfyUI! 🎉")

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]