# ComfyUI Prompt Mastering Quick Reference Guide

## Essential Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| `Ctrl + ↑` | Increase prompt weight by 0.05 |
| `Ctrl + ↓` | Decrease prompt weight by 0.05 |
| `Double-click output socket` | Create Reroute node |
| `Ctrl + C` | Copy nodes |
| `Ctrl + V` | Paste nodes |
| `Delete` | Delete selected nodes |

## Prompt Syntax Reference

### Weighting
- **Direct specification**: `(keyword:1.1)` - Sets exact weight
- **Parentheses**: `(keyword)` - Implicitly increases weight 1.1x
- **Multiple parentheses**: `((keyword))` - 1.21x weight, `(2.2x)`

### Brackets for Time/Weight Control
- **Switching**: `[word1::0.1] [word2::0.2]` - Switch at 10% to word1, 20% to word2
- **Weight control**: `[(word::0.1):0.1]` - Apply word at 10% with initial weight
- **Conditional**: `[word1:word2:0.3]` - Switch from word1 to word2 at 30% progress

### Region/Style Control
- **LoRA loading**: `<lora:filename:weight>` - Load and apply LoRA
- **Masking**: `MASK(x1 x2, y1 y2, weight)` - Apply to region
- **SDXL parameters**: `SDXL(width height, target_width target_height, crop_w crop_h)`

## Common Workflow Patterns

### Basic Text-to-Image Setup
```
Load Checkpoint → CLIP Text Encode (+) → CLIP Text Encode (-) → KSampler → VAE Decode → Save Image
```

### Advanced Workflow with LoRA
```
Load Checkpoint → Load LoRA → Combine Prompts → CLIP Text Encode → KSampler → VAE Decode
```

### Style Transfer Setup
```
Input Image → IPAdapter → ControlNet → Load Checkpoint → KSampler → VAE Decode → Save Image
```

### Character Consistency Workflow
```
Input Image → ControlNet (OpenPose) → Load Checkpoint → Character LoRA → KSampler → Upscale → Save Image
```

## Node Color Coding

| Data Type | Color | Example Nodes |
|-----------|-------|---------------|
| Model/Checkpoint | Lavender | Load Checkpoint, Load LoRA |
| CLIP Model | Yellow | CLIP Text Encode, DualCLIP Loader |
| VAE Model | Rose | Load VAE |
| Conditioning | Orange | CLIP Text Encode, Apply ControlNet |
| Latent Image | Pink | Empty Latent Image, KSampler |
| Image | Blue | Load Image, Save Image, IPAdapter |
| Mask | Green | Mask Editor, Inpaint |
| Number | Light Green | Seed, CFG Scale |
| String | Light Blue | Text Input, String |

## Sampler Recommendations

| Purpose | Sampler | Steps | CFG | Notes |
|---------|---------|-------|-----|-------|
| **Fast Testing** | Euler | 20-30 | 6-8 | Quick previews |
| **Quality Portrait** | DPM++ 2M Karras | 30-40 | 7-9 | Excellent detail |
| **Artistic Styles** | DPM++ SDE | 25-35 | 7-10 | Good for creative work |
| **Realistic Photos** | Euler a | 25-35 | 7-9 | Fast but detailed |

## Quality Prompts Library

### Photography Terms
- `professional photography, award winning shot, gallery quality`
- `DSLR photography, shallow depth of field, bokeh background`
- `high resolution, ultra detailed, sharp focus, 8k`
- `studio lighting, professional headshot, clean background`

### Lighting Effects
- `cinematic lighting, dramatic shadows, rim lighting`
- `soft diffused lighting, golden hour, natural light`
- `neon lighting, cyberpunk aesthetic, colorful accents`
- `dramatic lighting, moody atmosphere, volumetric lighting`

### Detail Enhancement
- `highly detailed, intricate texture work, fine detail`
- `hyperrealistic skin, perfect pores and texture, natural details`
- `fabric texture, clothing details, material accuracy`
- `hair detail, individual strands, natural flow, perfect texture definition`

## Troubleshooting Quick Fixes

### Common Issues
| Problem | Solution |
|---------|----------|
| **Out of Memory** | Reduce batch size, lower resolution, use `--lowvram` mode |
| **Black Images** | Check seed, increase steps, adjust CFG scale |
| **Blurry Results** | Increase steps, use better sampler, add detail enhancers |
| **Wrong Colors** | Try different VAE, adjust color prompts |
| **Poor Quality** | Increase CFG, add quality keywords, use better model |

### Model-Specific Notes
- **SD 1.5**: Use 512x512, focus on detailed prompts
- **SDXL**: Use 1024x1024+, better prompt understanding
- **Flux**: Use dual CLIP models, excellent prompt adherence
- **FLUX**: Use fp8 variants, great for professional work

## Batch Processing Tips

### Efficient Settings
- Test at low resolution first (512x512)
- Use deterministic seeds for consistency
- Batch similar operations together
- Enable attention optimization in settings
- Use fp16 precision for memory efficiency

### Automation Patterns
- Use Dynamic Prompts for variation
- Implement quality control filters
- Use seed stepping for systematic variation
- Group related tasks together
- Monitor GPU usage and temperature

## Performance Optimization

### Memory Management
- **Low VRAM (6GB)**: Use `--lowvram`, batch size 1, lower resolution
- **Medium VRAM (8-12GB)**: Standard settings, batch size 2-4
- **High VRAM (16GB+)**: Larger batches, higher resolutions

### Speed Optimization
- Use draft mode (lower steps) for iterations
- Enable attention optimization
- Reduce node connections
- Use efficient samplers (Euler a, DPM++ 2M Karras)
- Batch similar operations

## Essential Custom Nodes

### Must-Have Extensions
- **ComfyUI-Manager**: One-click node management
- **Dynamic Prompts**: Advanced prompt generation
- **WAS Node Suite**: Comprehensive utility nodes
- **Impact Pack**: Advanced editing and enhancement

### Specialized Nodes
- **IPAdapter Plus**: Advanced style transfer
- **ControlNet**: Spatial control and composition
- **Regional Prompting**: Area-specific prompts
- **Prompt Control**: Advanced prompt manipulation

## Production Workflows

### E-commerce Product Shots
```
Product Image → ControlNet (Canny) → IPAdapter (Style) → Upscale → Final Enhancement
```

### Character Design Sheets
```
Input Character → Multiple ControlNets → LoRA Stack → Batch Generation → Sheet Assembly
```

### Style Transfer Pipeline
```
Input Image → Style Reference → IPAdapter → ControlNet → Refinement → Output
```

## Hardware Recommendations

### Minimum Requirements
- **GPU**: 6GB VRAM (GTX 1070/RTX 3060 or equivalent)
- **RAM**: 16GB system memory
- **Storage**: 50GB free space for models and cache

### Recommended Setup
- **GPU**: 12-16GB VRAM (RTX 4070Ti/4090)
- **RAM**: 32GB system memory
- **Storage**: 100GB+ SSD with 2TB data drive

### Professional Setup
- **GPU**: 24GB+ VRAM (A6000, H100, or multiple GPUs)
- **RAM**: 64GB+ system memory
- **Storage**: NVMe SSDs, networked storage
- **Network**: High-speed connection for model downloads

## Model Recommendations

### Base Models
- **SD 1.5**: `realisticVisionV20_v20.safetensors` - Photorealistic
- **SDXL**: `dreamshaper_8.safetensors` - Versatile and stable
- **FLUX**: `flux1-dev-fp8.safetensors` - Professional quality

### LoRA Models
- **Character**: FaceV2, Character Consistency LoRA
- **Style**: Art Nouveau, Impressionist, Cyberpunk
- **Quality**: Detail Enhancer, Skin Smoother

### Upscale Models
- `4x_NMKD-Superscale-SP_178000_G.pth` - General purpose
- `4x_ClearRealityV1.pth` - Photorealistic
- `4x_ReJesus_2.0.pth` - Art and anime

## Version Compatibility

### ComfyUI v0.3.68+ (November 2025)
- Native LoRA masking and scheduling
- V3 node schema improvements
- Async API nodes
- Enhanced memory management

### Recent Additions
- TemporalScoreRescaling node (October 2025)
- Subgraph widget editing (October 2025)
- Epsilon Scaling node (October 2025)
- HunyuanVAE support (October 2025)

---

*Last Updated: November 2025*  
*For the complete guide, see: `comfyui_prompt_mastering_guide.md`*