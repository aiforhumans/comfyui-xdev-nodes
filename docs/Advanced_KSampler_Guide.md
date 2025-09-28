# Advanced KSampler - Multi-Variant Learning System

## Overview

The Advanced KSampler is a sophisticated sampling node that generates **3 different renderi### 🚨 Troubleshooting

### Common Issues

**"Learning disabled" message**:
- Ensure `enable_learning` = True
- Check that `variant_selection` is set to your previous choice

**Parameter validation errors**:
- Verify priority weights sum to 1.0
- Check that all required inputs are connected
- Ensure parameters are within valid ranges

**Poor learning performance**:
- Increase `learning_strength` for faster adaptation
- Provide consistent selection feedback
- Use selection notes to clarify preferences

**OutputDev shows IMAGE instead of LATENT**:
- This happens when you add VAE Decode between AdvancedKSampler and OutputDev
- **LATENT analysis**: Connect variants directly to OutputDev for parameter comparison
- **IMAGE analysis**: Use VAE Decode → OutputDev for visual quality comparison
- **Both approaches are valid** - choose based on what you want to analyze

### Analysis Approaches

**Pure LATENT Analysis** (Parameter Focus):
```
AdvancedKSampler → OutputDev
```
- Compare sampling parameters, tensor shapes, memory usage
- Best for understanding algorithmic differences
- OutputDev will show "ComfyUI Type: LATENT"

**Visual IMAGE Analysis** (Quality Focus):
```
AdvancedKSampler → VAE Decode → OutputDev
```
- Compare visual quality, pixel values, image characteristics  
- Best for understanding visual differences
- OutputDev will show "ComfyUI Type: IMAGE/TENSOR"

**Comprehensive Analysis** (Both):
- Use separate OutputDev nodes for LATENT and IMAGE analysis
- See `workflows/advanced_ksampler_comprehensive.json` for example
- Compare both parameter and visual differences simultaneouslyultaneously and learns from your selections to optimize future generations. This system bridges the gap between speed and quality by letting you explore different sampling strategies and automatically improving based on your preferences.

## 🎯 Key Features

### Real ComfyUI Sampling Integration
- **Authentic Results**: Uses ComfyUI's native KSampler for actual image generation
- **Full Compatibility**: Works with all ComfyUI models, samplers, and schedulers
- **Fallback System**: Enhanced mock sampling when ComfyUI modules unavailable
- **Performance Optimized**: Leverages ComfyUI's optimized sampling algorithms

### Multi-Variant Generation
- **Quality Variant**: High-step precision sampling for maximum quality
- **Speed Variant**: Optimized low-step sampling for rapid generation  
- **Creative Variant**: Experimental settings for artistic exploration

### Learning Optimization System
- Tracks your variant selections over time
- Automatically adjusts parameters based on preferences
- Improves quality of future generations
- Maintains learning history across sessions

### Intelligent Parameter Management
- Dynamic step count adjustment per variant
- CFG scale optimization per strategy
- Scheduler/sampler preference learning
- Denoising strength adaptation

## 🚀 Workflow Usage

### Phase 1: Initial Generation
1. **Connect Inputs**: MODEL, positive/negative CONDITIONING, LATENT
2. **Set Base Parameters**: Steps, CFG, sampler, scheduler, denoise
3. **Run Advanced KSampler**: Generates 3 variants automatically
4. **Analyze with OutputDev**: Connect each variant to OutputDev for detailed analysis

### Phase 2: Selection & Learning
1. **Compare Variants**: Use OutputDev analysis to compare quality, parameters, timing
2. **Rate Performance**: Use VariantSelector to rate each variant (1-10)
3. **Select Winner**: Choose your preferred variant
4. **Provide Feedback**: Add selection notes for context

### Phase 3: Iterative Improvement  
1. **Set Previous Selection**: Use `variant_selection` input with your choice
2. **Enable Learning**: Keep `enable_learning` = True
3. **Re-run Sampler**: Get improved variants based on your history
4. **Repeat Process**: Continue refining preferences over multiple generations

## 📊 Node Reference

### XDEV_AdvancedKSampler

**Category**: `XDev/Sampling/Advanced` | **Real ComfyUI Sampling Integration**

**Required Inputs**:
- `model` (MODEL): SDXL model for sampling
- `positive` (CONDITIONING): Positive conditioning/prompt  
- `negative` (CONDITIONING): Negative conditioning/prompt
- `latent_image` (LATENT): Input latent for sampling
- `seed` (INT): Seed for sampling (-1 for random)
- `steps` (INT): Base number of sampling steps (1-200)
- `cfg` (FLOAT): Base CFG scale (0.0-30.0)
- `sampler_name` (COMBO): Primary sampling algorithm
- `scheduler` (COMBO): Noise scheduler type
- `denoise` (FLOAT): Base denoising strength (0.0-1.0)

**Optional Inputs**:
- `enable_learning` (BOOLEAN): Enable learning optimization
- `variant_selection` (COMBO): Previous selection for learning
- `quality_priority` (FLOAT): Priority weight for quality variant
- `speed_priority` (FLOAT): Priority weight for speed variant  
- `creative_priority` (FLOAT): Priority weight for creative variant
- `learning_strength` (FLOAT): Learning adjustment intensity
- `validate_input` (BOOLEAN): Enable input validation

**Outputs**:
- `quality_variant` (LATENT): Quality-focused result
- `speed_variant` (LATENT): Speed-optimized result
- `creative_variant` (LATENT): Creative exploration result
- `variant_info` (STRING): Parameter details for each variant
- `optimization_info` (STRING): Learning status and history
- `selection_guide` (STRING): Usage instructions and tips

### XDEV_VariantSelector

**Category**: `XDev/Sampling/Advanced`

**Required Inputs**:
- `quality_variant` (LATENT): Quality-focused variant
- `speed_variant` (LATENT): Speed-optimized variant
- `creative_variant` (LATENT): Creative exploration variant
- `selected_variant` (COMBO): Choose best variant

**Optional Inputs**:
- `quality_rating` (INT): Rate quality variant (1-10)
- `speed_rating` (INT): Rate speed variant (1-10)
- `creative_rating` (INT): Rate creative variant (1-10)
- `selection_notes` (STRING): Notes about selection criteria

**Outputs**:
- `selected_latent` (LATENT): Your chosen variant
- `selection_feedback` (STRING): Selection summary for learning
- `ratings_summary` (STRING): Rating analysis and insights

## 🎨 Sampling Strategies

### Quality Strategy
- **Purpose**: Maximum image quality and detail
- **Method**: Higher step counts (1.5x base), increased CFG precision
- **Best For**: Final renders, detailed artwork, professional output
- **Trade-off**: Slower generation time

### Speed Strategy  
- **Purpose**: Rapid iteration and experimentation
- **Method**: Reduced steps (0.6x base), optimized schedulers
- **Best For**: Concept exploration, quick previews, batch processing
- **Trade-off**: Slight quality reduction

### Creative Strategy
- **Purpose**: Artistic variation and experimentation
- **Method**: Randomized adjustments, experimental parameters
- **Best For**: Style exploration, unexpected results, creative discovery
- **Trade-off**: Unpredictable results

## 🧠 Learning System

### How Learning Works
1. **Selection Tracking**: Records which variants you choose over time
2. **Parameter Adjustment**: Gradually shifts base parameters toward preferred strategies  
3. **Preference Weighting**: Stronger preferences receive higher adjustment weights
4. **Bounded Optimization**: Adjustments stay within safe parameter ranges

### Learning Parameters
- **Learning Strength**: Controls how much selections influence future generations
- **History Persistence**: Learning accumulates across multiple sessions
- **Adaptive Bounds**: Prevents parameter drift outside valid ranges
- **Gradient Application**: Smooth transitions rather than sudden jumps

### Best Practices
- **Consistent Feedback**: Rate variants consistently for better learning
- **Clear Selection Notes**: Document why you chose specific variants
- **Balanced Exploration**: Try different variants to improve system understanding
- **Patient Iteration**: Learning improves over 5-10 generations

## 🔧 Integration with XDev Ecosystem

### OutputDev Analysis
- Connect each variant to OutputDev for detailed parameter analysis
- Use "detailed" level analysis for comprehensive variant comparison
- Export analysis results for external comparison tools

### Universal Testing Pattern
```
InputDev (MODEL/CONDITIONING/LATENT) → AdvancedKSampler → OutputDev (Analysis)
                                                       ↓
                                     VariantSelector → OutputDev (Selection)
```

### Performance Framework
- All operations use `@performance_monitor` decorators
- TTL-based caching for repeated parameter combinations
- Memory-efficient latent handling
- Graceful fallbacks for missing dependencies

## 🚨 Troubleshooting

### Common Issues

**"Learning disabled" message**:
- Ensure `enable_learning` = True
- Check that `variant_selection` is set to your previous choice

**Parameter validation errors**:
- Verify priority weights sum to 1.0
- Check that all required inputs are connected
- Ensure parameters are within valid ranges

**Poor learning performance**:
- Increase `learning_strength` for faster adaptation
- Provide consistent selection feedback
- Use selection notes to clarify preferences

### Optimization Tips

**For Quality Focus**:
- Set higher `quality_priority` weight
- Select quality variants consistently
- Use higher base step counts

**For Speed Focus**: 
- Set higher `speed_priority` weight
- Select speed variants consistently
- Use lower base step counts

**For Creative Exploration**:
- Set higher `creative_priority` weight
- Vary selections to explore parameter space
- Use moderate learning strength for stability

## 🎯 Example Workflows

### Scenario 1: Portrait Photography
```
Base: 30 steps, CFG 6.0, DPM++ 2M Karras
Learning Target: Quality variants for detail
Expected Outcome: Higher steps, refined CFG for portraits
```

### Scenario 2: Concept Art Iteration
```
Base: 20 steps, CFG 8.0, Euler Ancestral  
Learning Target: Speed variants for rapid iteration
Expected Outcome: Optimized steps/CFG for fast concepts
```

### Scenario 3: Artistic Exploration
```
Base: 25 steps, CFG 7.0, Various samplers
Learning Target: Creative variants for experimentation
Expected Outcome: Dynamic parameter exploration
```

## 🚀 Future Enhancements

- **Batch Variant Generation**: Multiple variants per strategy
- **Custom Strategy Definition**: User-defined sampling approaches  
- **Cross-Session Learning**: Persistent learning across ComfyUI restarts
- **Advanced Analytics**: Detailed performance and preference reporting
- **Integration Expansion**: Support for additional ComfyUI sampling nodes

---

**Part of XDev Nodes v0.4.0 - Professional ComfyUI Development Toolkit**