# Advanced KSampler System - Native ComfyUI Integration Guide

The XDev Advanced KSampler provides professional-grade multi-variant sampling based on DeepWiki research into ComfyUI's native architecture. Features authentic CFGGuider integration, KSAMPLER_NAMES selection, and advanced learning optimization for production workflows.

## Overview - Enhanced Native Integration

The Advanced KSampler system leverages ComfyUI's authentic sampling patterns discovered through comprehensive DeepWiki research:

- **XDEV_AdvancedKSampler**: Native ComfyUI sampling with CFGGuider integration
- **XDEV_VariantSelector**: Learning feedback with native parameter optimization

Based on analysis of ComfyUI's core sampling architecture including common_ksampler functions, CFGGuider classes, and model_options hooks.

## Key Features - DeepWiki Enhanced

### Native ComfyUI Integration
- **Authentic Sampling**: Uses ComfyUI's common_ksampler function (same as KSampler node)
- **CFGGuider Patterns**: Strategy-specific CFG enhancements via model_options hooks
- **KSAMPLER_NAMES**: Dynamic sampler selection from ComfyUI's native list
- **Native Schedulers**: Karras, exponential, sgm_uniform, and all ComfyUI options

### Strategy-Based Sampling
- **Quality Strategy**: Precision samplers (dpmpp_2m, heun, uni_pc) with enhanced CFG
- **Speed Strategy**: Fast samplers (euler, lcm, dpm_fast) with optimized CFG
- **Creative Strategy**: Ancestral/SDE samplers with experimental CFG variations

### Advanced Learning System
- **Native Parameter Learning**: Adapts ComfyUI samplers and schedulers based on selections
- **CFG Strategy Optimization**: Learns preferred guidance patterns per strategy
- **Confidence Building**: Gradual parameter shifts based on selection frequency
- **Professional Bounds**: All parameters kept within ComfyUI's native ranges

## Architecture - Based on ComfyUI Research

### CFGGuider Integration
```python
# Enhanced CFG per strategy using model_options hooks
def enhanced_cfg_function(args):
    cond, uncond, cond_scale = args["cond"], args["uncond"], args["cond_scale"]
    enhanced_scale = cond_scale * 1.05  # Quality boost
    return uncond + (cond - uncond) * enhanced_scale

model.model_options["sampler_cfg_function"] = enhanced_cfg_function
```

### Native Sampler Selection
```python
# Uses ComfyUI's KSAMPLER_NAMES dynamically
available_samplers = list(KSAMPLER_NAMES) if HAS_COMFY else fallback_list
strategy_sampler = self._get_strategy_sampler(strategy, base_sampler)
```

### Authentic Sampling Call
```python
# Uses same function as ComfyUI's KSampler node
result = nodes.common_ksampler(
    model, seed, steps, cfg, sampler_name, scheduler,
    positive, negative, latent_image, denoise=denoise
)
```

## Sampling Strategies

### Quality Strategy - Precision Focus
- **Samplers**: dpmpp_2m, heun, dpm_2, uni_pc, deis
- **Schedulers**: karras, exponential, sgm_uniform
- **CFG Enhancement**: 1.05x boost via model_options
- **Steps**: 1.5x base steps (capped at 200)
- **Use Case**: Final renders, maximum detail

### Speed Strategy - Efficiency Focus  
- **Samplers**: euler, lcm, dpm_fast, dpmpp_sde_gpu, heunpp2
- **Schedulers**: simple, normal, ddim_uniform
- **CFG Optimization**: Streamlined guidance (cap at 12.0)
- **Steps**: 0.6x base steps (minimum 5)
- **Use Case**: Rapid iteration, concept development

### Creative Strategy - Exploration Focus
- **Samplers**: dpmpp_2s_ancestral, euler_ancestral, dpmpp_sde variants
- **Schedulers**: beta, linear_quadratic, exponential
- **CFG Experimentation**: Dynamic scaling with random variations
- **Steps**: 1.1x base steps with noise
- **Use Case**: Artistic exploration, unexpected results

## Learning System - Native Parameter Optimization

### Selection Tracking
- **Confidence Building**: Gradual parameter shifts over multiple selections
- **Frequency Analysis**: More selections = stronger learning confidence
- **Native Bounds**: All adjustments respect ComfyUI's parameter limits

### Parameter Learning
```python
# Sampler preference learning (after 3+ selections)
if selections >= 3 and learning_factor > 0.2:
    for preferred in strategy_config["preferred_samplers"]:
        if preferred in available_samplers:
            adjusted["sampler_name"] = preferred
            break

# Scheduler optimization
if selections >= 3 and learning_factor > 0.2:
    for preferred in strategy_config["preferred_schedulers"]:
        if preferred in self._NATIVE_SCHEDULERS:
            adjusted["scheduler"] = preferred
            break
```

### CFG Strategy Evolution
- **Enhanced → Optimized**: Learns to balance quality vs speed
- **Experimental Variance**: Adapts randomization ranges based on creativity preferences
- **Model Options**: Preserves successful CFG enhancement patterns

## Usage Workflow

### Basic Setup
1. **Connect Inputs**: MODEL, positive/negative CONDITIONING, LATENT
2. **Configure Base Parameters**: steps, CFG, base sampler, scheduler
3. **Enable Learning**: Set `enable_learning=True` for optimization

### Generation Process
1. **Run AdvancedKSampler**: Generates 3 strategy variants simultaneously
2. **Visual Analysis**: Connect variants to VAE Preview for image comparison
3. **LATENT Analysis**: Connect variants to OutputDev for parameter examination
4. **Strategy Comparison**: Review variant_info for sampling details

### Learning Optimization
1. **Evaluate Results**: Compare quality, speed, creativity of variants
2. **Select Best**: Use VariantSelector with ratings (1-10 per strategy)
3. **Provide Feedback**: Add selection notes for learning context
4. **Iterate**: Next generation uses optimized parameters based on selection

### Advanced Analysis
```
InputDev(MODEL/CONDITIONING/LATENT) → AdvancedKSampler → [3 Variants]
                                                       ↓
                                    VAEPreview (Visual) + OutputDev (LATENT)
                                                       ↓
                                    VariantSelector → Learning Feedback
```

## Native ComfyUI Compatibility

### Fallback System
- **Primary**: Native ComfyUI sampling with common_ksampler
- **Secondary**: Direct comfy.sample calls with CFGGuider
- **Tertiary**: Enhanced mock sampling with strategy-specific variations

### Parameter Validation
- **Steps**: 1-200 (ComfyUI standard range)
- **CFG**: 0.1-30.0 (ComfyUI standard range)  
- **Denoise**: 0.0-1.0 (ComfyUI standard range)
- **Samplers**: Validated against KSAMPLER_NAMES
- **Schedulers**: Validated against native ComfyUI options

### Performance Features
- **@performance_monitor**: Automatic timing and profiling
- **TTL Caching**: Cached operations for repeated parameter combinations
- **Memory Management**: Efficient tensor handling with ComfyUI patterns
- **Device Management**: Proper GPU/CPU placement following ComfyUI conventions

## Troubleshooting

### Native Integration Issues
**"ComfyUI modules not available"**:
- Ensure running within ComfyUI environment
- Check for proper XDev installation via dev-link script
- Verify ComfyUI version compatibility

**"KSAMPLER_NAMES not found"**:
- ComfyUI version too old - fallback samplers used
- Update ComfyUI for full native integration
- Fallback provides full functionality

### Learning System Issues
**"No learning history yet"**:
- Normal for first run - provide selections to build history
- Use VariantSelector after each generation for feedback
- Minimum 2-3 selections needed for parameter adaptation

**Learning too slow/fast**:
- Adjust `learning_strength` parameter (0.0-1.0)
- Higher values = faster adaptation, lower values = gradual learning
- Default 0.1 provides conservative, stable learning

### Visual Output Issues
**"Getting LATENT data but no images"**:
- **Expected behavior**: AdvancedKSampler outputs LATENT data
- **For visual output**: Connect variants to VAEPreview or VAEDecode nodes
- **For analysis**: Use OutputDev to examine LATENT metadata and parameters
- **Both paths valid**: Choose based on analysis needs (visual vs technical)

## Integration Examples

### Quality-Focused Workflow
```
Model → AdvancedKSampler(steps=40, cfg=8.5, sampler="dpmpp_2m")
                ↓
        Quality Variant → VAEPreview → Final Output
```

### Speed Iteration Workflow  
```
Model → AdvancedKSampler(steps=15, cfg=6.0, sampler="euler")
                ↓
        Speed Variant → Quick Analysis → Rapid Iteration
```

### Creative Exploration Workflow
```
Model → AdvancedKSampler(steps=25, cfg=7.0, sampler="euler_ancestral")
                ↓
        Creative Variant → Artistic Analysis → Style Development
```

### Learning Optimization Workflow
```
Generation 1: Base parameters → 3 variants → Select best → Learning feedback
Generation 2: Adapted parameters → 3 variants → Select best → Enhanced learning  
Generation N: Optimized parameters → Preferred results → Personalized sampling
```

## Best Practices

### Parameter Selection
- **Start Conservative**: Use moderate steps (20-30), CFG (6-8) for baseline
- **Strategy Testing**: Try all 3 variants to understand differences
- **Consistent Feedback**: Regular VariantSelector usage improves learning

### Performance Optimization
- **Batch Processing**: Generate multiple variants efficiently in single pass
- **Caching Benefits**: Repeated parameter combinations use cached results
- **Resource Management**: Native ComfyUI integration optimizes GPU usage

### Educational Value
- **Architecture Study**: Examine code to understand ComfyUI sampling patterns
- **Parameter Learning**: Observe how selections affect future generations
- **Strategy Analysis**: Compare technical differences between sampling approaches

The Advanced KSampler represents the culmination of DeepWiki research into ComfyUI's sampling architecture, providing both production-quality results and educational insight into professional ComfyUI development patterns.