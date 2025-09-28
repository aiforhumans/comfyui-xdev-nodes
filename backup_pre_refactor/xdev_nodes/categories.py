"""
XDev Node Categories - Centralized category definitions
Ensures consistent categorization across all nodes.
"""

class NodeCategories:
    """Centralized node category definitions"""
    
    # Base categories
    BASIC = "XDev/Basic"
    DEVELOPMENT = "XDev/Development" 
    MATH = "XDev/Math"
    TEXT = "XDev/Text"
    
    # Image processing
    IMAGE_BASIC = "XDev/Image/Basic"
    IMAGE_MANIPULATION = "XDev/Image/Manipulation"
    IMAGE_ANALYSIS = "XDev/Image/Analysis"
    
    # VAE operations
    VAE_TOOLS = "XDev/VAE Tools"
    
    # Prompt engineering
    PROMPT_COMBINATION = "XDev/Prompt/Combination"
    PROMPT_WEIGHTING = "XDev/Prompt/Weighting"
    PROMPT_CLEANING = "XDev/Prompt/Cleaning"
    PROMPT_ANALYSIS = "XDev/Prompt/Analysis"
    PROMPT_RANDOMIZATION = "XDev/Prompt/Randomization"
    PROMPT_TEMPLATES = "XDev/Prompt/Templates"
    PROMPT_ADVANCED = "XDev/Prompt/Advanced"
    
    # LLM integration
    LLM_INTEGRATION = "XDev/LLM/Integration"
    LLM_PROMPT_TOOLS = "XDev/LLM/PromptTools"
    LLM_DEVELOPMENT = "XDev/LLM/Development"
    LLM_SDXL = "XDev/LLM/SDXL"
    LLM_CHARACTER = "XDev/LLM/Character"
    LLM_STYLE = "XDev/LLM/Style"
    
    # Model operations
    MODEL_ADVANCED = "XDev/Model/Advanced"
    
    # Sampling
    SAMPLING_ADVANCED = "XDev/Sampling/Advanced"
    
    # Face processing
    FACE_SWAP = "XDev/FaceSwap"
    FACE_PROCESSING_ADVANCED = "XDev/Face Processing/Advanced"
    FACE_PROCESSING_BATCH = "XDev/Face Processing/Batch"
    FACE_PROCESSING_ANALYSIS = "XDev/Face Processing/Analysis"
    
    # InsightFace specific
    INSIGHTFACE_LOADERS = "XDev/InsightFace/Loaders"
    INSIGHTFACE_PROCESSING = "XDev/InsightFace/Processing"
    INSIGHTFACE_FACESWAP = "XDev/InsightFace/FaceSwap"
    
    @classmethod
    def get_all_categories(cls) -> list[str]:
        """Get all available categories"""
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str)
        ]
    
    @classmethod
    def validate_category(cls, category: str) -> bool:
        """Check if a category is valid"""
        return category in cls.get_all_categories()

# Backwards compatibility aliases
CATEGORIES = NodeCategories