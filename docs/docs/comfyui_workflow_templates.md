# ComfyUI Prompt Mastering Workflow Templates

## Template 1: Master Portrait Generator with Character Consistency

### Description
A professional portrait generator that maintains character consistency across different poses and lighting conditions using FLUX models and ControlNet integration.

### Node Configuration
```
Main Workflow:
1. Load FLUX Model (flux1-dev-fp8.safetensors)
2. DualCLIPLoader (t5xxl_fp8_e4m3fn.safetensors + clip_l.safetensors)
3. Load VAE (ae.safetensors)
4. ControlNet Loader (OpenPose/Union Flux ControlNet)
5. Load Image (Character Reference or Pose Sheet)
6. ControlNet Preprocessor (OpenPose)
7. Apply ControlNet
8. CLIP Text Encode (Character Description)
9. CLIP Text Encode (Negative Prompts)
10. KSampler (DPM++ 2M Karras, 35 steps, CFG 7.5)
11. Load Upscale Model (4x-ClearRealityV1.pth)
12. VAE Decode
13. Image Upscale with Model
14. Save Image
```

### Recommended Settings
- **Steps**: 35
- **CFG Scale**: 7.5
- **Sampler**: DPM++ 2M Karras
- **Resolution**: 1024x1024 (SDXL) or 1024x1536 (portrait)
- **Seed**: Fixed for consistency

### Character Prompt Template
```
"professional portrait, [character description], [pose/lighting], studio quality, sharp focus, perfect skin, detailed hair, award winning photography"
```

### Negative Prompt
```
"low quality, blurry, out of focus, bad anatomy, extra limbs, deformed, ugly, watermark, signature, text, oversaturated"
```

---

## Template 2: Advanced Style Transfer with IPAdapter

### Description
A sophisticated style transfer system that combines multiple reference images with spatial control for consistent artistic results.

### Node Configuration
```
Main Workflow:
1. Load SDXL Model (base model of choice)
2. Load IPAdapter Advanced
3. Load Image (Source Subject)
4. Load Image (Style Reference)
5. Load ControlNet Model
6. ControlNet Preprocessor (Canny/Depth based on subject)
7. Apply IPAdapter
8. Apply ControlNet
9. CLIP Text Encode (Style Description)
10. CLIP Text Encode (Negative Prompts)
11. KSampler (DPM++ 2M Karras, 40 steps, CFG 8.0)
12. VAE Decode
13. Save Image
```

### IPAdapter Settings
- **Weight**: 0.7
- **Weight Type**: Style Transfer (SDXL)
- **Noise**: 0.0
- **Sharpness**: 0.5

### ControlNet Settings
- **Strength**: 0.8
- **Start %**: 0.0
- **End %**: 0.7

### Style Prompt Template
```
"[style description], [subject description], [lighting], professional photography, ultra detailed, sharp focus"
```

---

## Template 3: Dynamic Product Photography Generator

### Description
An automated system for generating consistent product shots with customizable backgrounds, lighting, and compositions.

### Node Configuration
```
Main Workflow:
1. Load SDXL Model (dreamshaper_8.safetensors)
2. Dynamic Prompts Text Box
3. CLIP Text Encode (Product Prompts)
4. CLIP Text Encode (Background Prompts)
5. CLIP Text Encode (Negative Prompts)
6. KSampler (DPM++ 2M Karras, 30 steps, CFG 8.5)
7. VAE Decode
8. Load Upscale Model (4x_ClearRealityV1.pth)
9. Image Upscale with Model
10. Save Image
```

### Dynamic Prompt Setup
```
Base Product: "{iPhone 15 Pro|macBook Pro|Gaming Chair|Sneaker}"
Background: "{modern office|minimalist white|industrial loft|studio setup}"
Lighting: "{dramatic lighting|soft box|golden hour|neon accent}"
Angle: "{three quarter view|front view|side profile|top down}"
```

### Professional Settings
- **Batch Size**: 4
- **Steps**: 30
- **CFG Scale**: 8.5
- **Sampler**: DPM++ 2M Karras
- **Resolution**: 1024x1024

---

## Template 4: Multi-Model Style Fusion

### Description
A complex workflow that combines different models and techniques for creating unique artistic styles with maximum control.

### Node Configuration
```
Main Workflow:
1. Load Base Model (SDXL)
2. Load LoRA Stack
3. Load ControlNet Stack
4. Load Image (Reference)
5. Regional Prompt (Foreground)
6. Regional Prompt (Background)
7. Combine Prompts
8. Apply LoRA Stack
9. Apply ControlNet Stack
10. CLIP Text Encode
11. CLIP Text Encode (Negative)
12. KSampler Advanced (Per-step control)
13. VAE Decode
14. Post-Processing Stack
15. Save Image
```

### LoRA Stack Configuration
```
LoRA 1: Style_LinearArt_LoRA (Weight: 0.7, Strength: 0.8)
LoRA 2: Texture_Enhancement_LoRA (Weight: 0.5, Strength: 0.6)
LoRA 3: Color_Grading_LoRA (Weight: 0.3, Strength: 0.4)
```

### ControlNet Stack Configuration
```
ControlNet 1: Canny (Strength: 0.8, Start: 0.0, End: 0.6)
ControlNet 2: Depth (Strength: 0.6, Start: 0.2, End: 0.8)
ControlNet 3: OpenPose (Strength: 0.7, Start: 0.0, End: 0.5)
```

---

## Template 5: Video Generation with AnimateDiff

### Description
A specialized workflow for generating consistent video sequences with motion and temporal coherence.

### Node Configuration
```
Main Workflow:
1. Load Base Model (SD 1.5 or SDXL)
2. Load AnimateDiff Model
3. Load Image (First Frame)
4. CLIP Text Encode (Scene Description)
5. CLIP Text Encode (Motion Prompts)
6. CLIP Text Encode (Negative Prompts)
7. KSampler (Euler, 25 steps, CFG 7.0)
8. AnimateDiff-SVD
9. Latent Composite
10. VAE Decode
11. Video Combine
12. Save Video
```

### Video Settings
- **Frames**: 16-24
- **FPS**: 8-12
- **Resolution**: 512x512 (start) → 1024x1024 (upscaled)
- **Motion Scale**: 0.8
- **CFG Scale**: 7.0

### Motion Prompts
```
"[camera movement], [character movement], [environmental motion], smooth animation, cinematic quality"
```

---

## Template 6: Batch Character Sheet Generator

### Description
An efficient system for generating multiple character variations with consistent identity across different poses and expressions.

### Node Configuration
```
Main Workflow:
1. Load FLUX Model
2. DualCLIPLoader
3. Load VAE
4. Character LoRA Stack
5. ControlNet (OpenPose)
6. Load Pose Sheet Image
7. OpenPose Preprocessor
8. Apply ControlNet
9. Dynamic Prompts Generator (Variations)
10. CLIP Text Encode (Character + Pose)
11. CLIP Text Encode (Negative)
12. KSampler (DPM++ 2M Karras, 35 steps)
13. VAE Decode
14. Batch Processing
15. Character Sheet Assembly
```

### Variation Templates
```
Poses: "{standing|seated|walking|dancing|action pose|reclining}"
Expressions: "{smile|serious|surprised|confident|peaceful|energetic}"
Outfits: "{casual|formal|armor|fantasy|modern|historical}"
Lighting: "{soft|dramatic|golden hour|neon|backlit|side lit}"
```

---

## Template 7: Industrial Design Concept Generator

### Description
A professional workflow for generating product concepts with precise control over form, materials, and lighting.

### Node Configuration
```
Main Workflow:
1. Load Base Model (SDXL)
2. ControlNet (LineArt/MLSD for precision)
3. Load Reference Image (Inspiration)
4. LineArt Preprocessor
5. Apply ControlNet
6. Material LoRA Stack
7. CLIP Text Encode (Product Description)
8. CLIP Text Encode (Material Prompts)
9. CLIP Text Encode (Negative)
10. KSampler (DPM++ 2M Karras, 40 steps, CFG 9.0)
11. VAE Decode
12. Image Upscale
13. Save Image
```

### Product Prompt Structure
```
"[product category], [material], [color], [finish], [lighting setup], [camera angle], industrial design, CAD rendering, technical drawing, professional photography"
```

---

## Template 8: Fantasy World Builder

### Description
A comprehensive system for generating consistent fantasy environments with architectural, atmospheric, and character elements.

### Node Configuration
```
Main Workflow:
1. Load Model Stack (SDXL + Specialized LoRAs)
2. Environment LoRA Stack
3. Architecture LoRA Stack
4. Character LoRA Stack
5. ControlNet Stack (Depth + LineArt)
6. Load Reference Images
7. Regional Prompts (Environment/Characters/Architecture)
8. Combine All Prompts
9. Apply LoRA Stack
10. Apply ControlNet Stack
11. CLIP Text Encode (World Description)
12. CLIP Text Encode (Style/Negative)
13. KSampler Advanced
14. Post-Processing
15. Save Image
```

### LoRA Stack Categories
```
Environment: fantasy_environment, magical_atmosphere, mystical_lighting
Architecture: medieval_architecture, fantasy_buildings, magical_structures
Characters: fantasy_characters, mythical_beings, heroic_postures
Style: painterly_style, dramatic_lighting, epic_composition
```

---

## Implementation Guide

### Step 1: Setup Environment
1. Install ComfyUI from official repository
2. Install ComfyUI-Manager
3. Download required models via Manager
4. Set up model directories:
   ```
   ComfyUI/models/
   ├── checkpoints/
   ├── loras/
   ├── controlnet/
   ├── upscale_models/
   └── vae/
   ```

### Step 2: Create Workflows
1. Save these templates as JSON files
2. Import into ComfyUI using "Load Workflow"
3. Install any missing custom nodes
4. Adjust settings based on your hardware

### Step 3: Optimize Performance
1. Start with lower resolutions for testing
2. Use `--lowvram` mode if needed
3. Adjust batch sizes based on VRAM
4. Enable attention optimization in settings

### Step 4: Customize and Iterate
1. Modify prompts for your specific needs
2. Adjust LoRA weights and timings
3. Experiment with different ControlNet combinations
4. Save successful configurations as templates

---

## Advanced Tips

### Memory Optimization
- Use fp16 precision when possible
- Implement model switching for different tasks
- Use `LatentRotate` nodes instead of re-encoding
- Cache intermediate results for batch processing

### Quality Enhancement
- Stack multiple detail enhancers
- Use progressive refinement passes
- Implement automatic quality scoring
- Use seed control for reproducibility

### Automation Integration
- Connect to external APIs for dynamic prompts
- Implement webhook triggers for batch processing
- Use queue management for large-scale generation
- Set up monitoring and logging systems

---

*For detailed explanations of each technique, refer to the main guide: `comfyui_prompt_mastering_guide.md`*