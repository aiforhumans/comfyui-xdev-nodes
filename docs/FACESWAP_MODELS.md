# 🎭 Professional Face Swapping Setup Guide

## XDev Face Swapping Nodes (6 Professional Nodes)

The XDev toolkit provides **6 professional-grade face swapping nodes** with production-quality results:

### 🚀 **Available Nodes**
- **XDEV_AdvancedFaceSwap** - High-quality face swapping with advanced blending
- **XDEV_FaceSwapBatch** - Batch processing for multiple face swaps  
- **XDEV_FaceQualityAnalyzer** - Analyze face quality and compatibility
- **XDEV_InsightFaceModelLoader** - Load and manage InsightFace detection models
- **XDEV_InsightFaceSwapperLoader** - Load InSwapper face replacement models
- **XDEV_InsightFaceProcessor** - Advanced face processing and enhancement

### 📁 **Model Directory Structure**

The XDev nodes automatically create the following directory structure in your ComfyUI models folder:

```
ComfyUI/models/
├── insightface/              # InsightFace detection & analysis
│   ├── detectors/           # Face detection models (SCRFD, RetinaFace)  
│   ├── embedders/           # ArcFace identity embedding models
│   └── parsers/             # BiSeNet face parsing models (optional)
└── faceswap/                # InSwapper face replacement
    ├── inswapper/           # InSwapper ONNX models
    └── checkpoints/         # Alternative checkpoint formats
```

## 📥 **Required Model Downloads**

### 🎯 **Core Models (Required)**

#### 1. Face Detector: SCRFD (Recommended)
- **Model**: `scrfd_10g_bnkps.onnx`
- **Size**: ~17MB
- **Purpose**: Robust face detection with landmark points
- **Download**: [InsightFace Model Zoo](https://github.com/deepinsight/insightface/tree/master/model_zoo)
- **Location**: `ComfyUI/models/insightface/detectors/scrfd_10g_bnkps.onnx`

#### 2. Identity Embedder: ArcFace (Recommended)  
- **Model**: `w600k_r50.onnx`
- **Size**: ~249MB
- **Purpose**: Generate 512-D face identity embeddings
- **Download**: [InsightFace Model Zoo](https://github.com/deepinsight/insightface/tree/master/model_zoo)
- **Location**: `ComfyUI/models/insightface/embedders/w600k_r50.onnx`

#### 3. Face Swapper: InSwapper (Essential)
- **Model**: `inswapper_128.onnx`
- **Size**: ~554MB
- **Purpose**: High-quality face swapping using identity embeddings
- **Download**: Multiple sources available (respect licensing):
  - [Hugging Face Collections](https://huggingface.co/models?search=inswapper)
  - [ONNX Model Zoo](https://github.com/onnx/models)
  - [Community Repositories](https://github.com/search?q=inswapper_128)
- **Location**: `ComfyUI/models/insightface/swappers/inswapper_128.onnx`

#### 4. Face Parser: BiSeNet (Optional)
- **Model**: `bisenet.onnx`
- **Size**: ~50MB
- **Purpose**: Advanced face parsing for precise masking
- **Download**: [Face Parsing Models](https://github.com/zllrunning/face-parsing.PyTorch)
- **Location**: `ComfyUI/models/insightface/parsers/bisenet.onnx`

### Quick Download Commands (Example)

```bash
# Navigate to ComfyUI models directory
cd /path/to/ComfyUI/models/insightface

# Create directories
mkdir -p detectors embedders swappers parsers

# Example download commands (adjust URLs as needed)
# Note: These are example commands - actual download links may vary

# Detector
curl -L "https://github.com/deepinsight/insightface/releases/download/v0.7/scrfd_10g_bnkps.onnx" \
     -o detectors/scrfd_10g_bnkps.onnx

# Embedder  
curl -L "https://github.com/deepinsight/insightface/releases/download/v0.7/w600k_r50.onnx" \
     -o embedders/w600k_r50.onnx

# Swapper (from community source)
curl -L "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx" \
     -o swappers/inswapper_128.onnx
```

### Installation Verification

1. **Check Model Files**: Ensure all required .onnx files are in correct directories
2. **ComfyUI Restart**: Restart ComfyUI to detect new models
3. **Node Availability**: Verify XDEV_FaceExtractEmbed and XDEV_FaceSwapApply nodes appear
4. **Test Workflow**: Load the professional_faceswap_demo.json workflow

### Performance Optimization

#### CUDA Setup (RTX 5080)
- **ONNX Runtime GPU**: `pip install onnxruntime-gpu`
- **CUDA Toolkit**: Version 11.8+ recommended
- **Memory**: 8GB+ VRAM for comfortable operation
- **Batch Size**: Start with 1 face, increase based on VRAM

#### Model Loading Optimization
```python
# XDev automatically optimizes with:
providers = [
    "CUDAExecutionProvider",    # Primary (RTX 5080)
    "CPUExecutionProvider"      # Fallback
]
```

### Troubleshooting

#### Common Issues
1. **Model Not Found**: Check file paths and permissions
2. **ONNX Import Error**: Install `pip install onnxruntime`
3. **CUDA Provider Missing**: Install `onnxruntime-gpu`
4. **Memory Errors**: Reduce image resolution or batch size

#### Model Quality
- **SCRFD vs RetinaFace**: SCRFD generally faster, RetinaFace more accurate
- **ArcFace Variants**: w600k_r50 balances quality/speed, r100 higher quality
- **InSwapper Versions**: inswapper_128 is standard, some communities have enhanced versions

## 🎬 **Practical Usage Workflows**

### **Basic Face Swap Workflow**
```
InputDev(IMAGE) → XDEV_AdvancedFaceSwap → OutputDev
                     ↑
              XDEV_InsightFaceModelLoader
```

### **Professional Quality Pipeline**
```
Source Image → XDEV_FaceQualityAnalyzer → Quality Check
              ↓
Target Image → XDEV_AdvancedFaceSwap → XDEV_FaceSwapBatch → Final Output
              ↑                         ↑
       Model Loader              Processor Enhancement
```

### **Batch Processing Setup**
```
Multiple Images → XDEV_FaceSwapBatch → Batch Results
                     ↑
              Shared Model Loaders
```

## 📊 **Node Performance Guide**

### **XDEV_AdvancedFaceSwap Features**
- **Multi-face Detection**: Automatically handles multiple faces
- **Quality Assessment**: Built-in compatibility scoring  
- **Pose Matching**: Advanced geometry alignment
- **Skin Tone Adaptation**: Intelligent color matching
- **Edge Blending**: Professional seamless integration

### **XDEV_FaceQualityAnalyzer Metrics**
- **Resolution Score**: Face size and clarity rating
- **Angle Score**: Face orientation compatibility  
- **Lighting Score**: Illumination matching assessment
- **Expression Score**: Facial expression similarity
- **Overall Compatibility**: Combined quality rating (0-100)

### **Professional Tips**
1. **Image Preparation**: Use high-resolution images (1024px+ faces)
2. **Angle Matching**: Similar face angles produce better results  
3. **Lighting Consistency**: Match lighting conditions when possible
4. **Quality Threshold**: Use analyzer scores >70 for production work
5. **Batch Optimization**: Group similar-quality faces together

## 🔧 **Advanced Configuration**

### **Model Selection Strategy**
```
For Speed:     SCRFD + w600k_r50 + inswapper_128
For Quality:   RetinaFace + r100 + enhanced_inswapper  
For Balance:   SCRFD + w600k_r50 + inswapper_128 (Recommended)
```

### **Memory Optimization** 
```
RTX 5080 (16GB):  Batch size 4-8 faces (1024px)
RTX 4080 (12GB):  Batch size 2-4 faces (1024px)  
RTX 3080 (8GB):   Batch size 1-2 faces (768px)
CPU Fallback:     Single face processing only
```

## 📝 **Licensing Notes**

⚠️ **Important**: Respect model licensing when downloading:
- **InsightFace Models**: Apache 2.0 License (most models)
- **InSwapper**: Check specific repository licensing
- **InSwapper**: Community model, verify source licensing  
- **Commercial Use**: Ensure compliance for commercial applications
- **Attribution**: Follow author attribution requirements

### Alternative Models

#### Detector Alternatives
- `retinaface_r50.onnx` - Higher accuracy, slower
- `scrfd_2.5g_bnkps.onnx` - Lighter version

#### Embedder Alternatives  
- `r100.onnx` - Higher quality, larger file
- `glint360k_r100.onnx` - Latest training data

#### Swapper Alternatives
- `simswap_512.onnx` - Alternative architecture
- `faceshifter.onnx` - Another option (if available)

### Usage Examples

#### Basic Face Swap
```
Load Image (Reference) → XDEV_FaceExtractEmbed → XDEV_FaceSwapApply ← Load Image (Target)
                                    ↓
                             Preview Result
```

#### Advanced Pipeline
```
Reference → FaceExtractEmbed → FaceSwapApply (strength: 1.0, mask: auto)
Target ────────────────────→ ↑
                             │
                             FaceSwapApply (strength: 0.8, mask: expand, blend: poisson)
                             │
                             FaceSwapApply (strength: 0.9, mask: face_parser)
                             │
                             Save Final Result
```

### Model Update Strategy

1. **Version Tracking**: Keep model versions documented
2. **Performance Testing**: Test quality vs speed tradeoffs  
3. **Backup Models**: Keep working versions backed up
4. **Community Updates**: Monitor for improved model releases

For the latest model recommendations and download links, check:
- [InsightFace Official Repository](https://github.com/deepinsight/insightface)
- [XDev Nodes Documentation](./README.md)
- [ComfyUI Community Forums](https://github.com/comfyanonymous/ComfyUI/discussions)