"""
XDev Face Swap Model Status Checker
Check availability of required models and dependencies for professional face swapping.
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required Python packages are available."""
    deps = {}
    
    try:
        import numpy
        deps['numpy'] = f"✅ {numpy.__version__}"
    except ImportError:
        deps['numpy'] = "❌ Not installed"
    
    try:
        import cv2
        deps['opencv'] = f"✅ {cv2.__version__}"
    except ImportError:
        deps['opencv'] = "❌ Not installed"
    
    try:
        import torch
        deps['torch'] = f"✅ {torch.__version__}"
    except ImportError:
        deps['torch'] = "❌ Not installed"
    
    try:
        import onnxruntime as ort
        deps['onnxruntime'] = f"✅ {ort.__version__}"
        
        # Check ONNX providers
        providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in providers:
            deps['onnx_cuda'] = "✅ CUDA support available"
        else:
            deps['onnx_cuda'] = "⚠️ CUDA support not available"
            
    except ImportError:
        deps['onnxruntime'] = "❌ Not installed"
        deps['onnx_cuda'] = "❌ ONNX not available"
    
    try:
        import insightface
        deps['insightface'] = f"✅ {insightface.__version__}"
    except ImportError:
        deps['insightface'] = "❌ Not installed"
    
    return deps

def check_models():
    """Check if required ONNX models are available."""
    models = {}
    
    # Try to find ComfyUI models directory
    possible_paths = [
        "C:/comfy/ComfyUI/models/insightface",
        "./models/insightface",
        "../models/insightface",
        os.path.expanduser("~/ComfyUI/models/insightface")
    ]
    
    models_dir = None
    for path in possible_paths:
        if os.path.exists(path):
            models_dir = path
            break
    
    if not models_dir:
        return {"models_dir": "❌ InsightFace models directory not found"}
    
    models['models_dir'] = f"✅ Found at {models_dir}"
    
    # Check for required model files
    required_models = {
        'detector': 'detectors/scrfd_10g_bnkps.onnx',
        'embedder': 'embedders/w600k_r50.onnx', 
        'swapper': 'swappers/inswapper_128.onnx',
        'parser': 'parsers/bisenet.onnx'
    }
    
    for model_type, model_path in required_models.items():
        full_path = os.path.join(models_dir, model_path)
        if os.path.exists(full_path):
            size_mb = os.path.getsize(full_path) / (1024 * 1024)
            models[model_type] = f"✅ Found ({size_mb:.1f}MB)"
        else:
            models[model_type] = f"❌ Missing: {model_path}"
    
    return models

def main():
    print("🔍 XDev Face Swap Model Status Check")
    print("=" * 50)
    
    print("\n📦 Python Dependencies:")
    deps = check_dependencies()
    for dep, status in deps.items():
        print(f"   {dep:12} : {status}")
    
    print("\n🤖 ONNX Models:")
    models = check_models()
    for model, status in models.items():
        print(f"   {model:12} : {status}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    missing_deps = [dep for dep, status in deps.items() if "❌" in status]
    if missing_deps:
        print(f"   📥 Install missing dependencies: pip install {' '.join(missing_deps)}")
    
    missing_models = [model for model, status in models.items() if "❌" in status and model != 'models_dir']
    if missing_models:
        print(f"   📥 Download missing models - see docs/FACESWAP_MODELS.md")
    
    if "❌" not in str(deps.values()) and "❌" not in str(models.values()):
        print("   🎉 All requirements satisfied! Professional face swapping ready.")
    elif "❌" in str(models.values()):
        print("   ⚠️  Models missing - face swapping will use fallback mode.")
    else:
        print("   ❌ Dependencies missing - face swapping may not work.")
    
    print(f"\n📖 For setup instructions, see:")
    print(f"   docs/FACESWAP_MODELS.md")

if __name__ == "__main__":
    main()