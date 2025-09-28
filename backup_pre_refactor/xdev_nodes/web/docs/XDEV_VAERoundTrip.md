# VAE Round-Trip Tool (XDev)

## Overview

The **VAE Round-Trip** node performs a complete encode/decode cycle: **LATENT → DECODE → IMAGE → ENCODE → LATENT**. This powerful tool lets you visually inspect what your latents look like as images while also testing VAE quality and consistency.

## Features

### Complete Round-Trip Process
1. **DECODE**: Convert input LATENT to IMAGE using VAE
2. **SHOW**: Visual representation of the decoded image  
3. **ENCODE**: Convert the decoded IMAGE back to LATENT
4. **ANALYZE**: Compare original vs re-encoded latent quality

### Advanced Analysis Options
- **Memory Usage**: Track tensor memory consumption
- **Statistical Analysis**: Compare original vs round-trip latent statistics  
- **Quality Metrics**: Analyze differences and degradation
- **Shape Validation**: Verify tensor dimensions throughout process

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **latent** | LATENT | Required | Input latent to decode and re-encode |
| **vae** | VAE | Required | VAE model for encode/decode operations |
| **show_stats** | Boolean | True | Display processing statistics and memory usage |
| **quality_check** | Boolean | False | Perform quality analysis comparing input vs output |
| **decode_only** | Boolean | False | Only decode to image without re-encoding |

## Output Types

| Output | Type | Description |
|--------|------|-------------|
| **decoded_image** | IMAGE | The decoded image from input latent |
| **reencoded_latent** | LATENT | The re-encoded latent from decoded image |
| **process_info** | STRING | Detailed analysis and processing information |

## Use Cases

### 1. VAE Quality Testing
Test how well your VAE preserves information through a complete encode/decode cycle:
```
YourLatent → VAERoundTrip → Compare original vs reencoded latent
```

### 2. Visual Latent Inspection  
See what your latents actually look like as images:
```
ModelOutput(LATENT) → VAERoundTrip → View decoded_image output
```

### 3. VAE Comparison
Compare different VAE models with the same latent:
```
SameLatent → VAERoundTrip(VAE_A) → OutputDev(input_1)
          → VAERoundTrip(VAE_B) → OutputDev(input_2)
```

### 4. Quality Analysis Pipeline
Full analysis of VAE performance:
```
Latent → VAERoundTrip(quality_check=True) → Detailed quality metrics
```

## Analysis Information

### Processing Statistics
When `show_stats=True`, displays:
- **Input Latent**: Shape, memory usage, value range and statistics
- **Decoded Image**: Dimensions, memory usage, value range validation
- **Output Latent**: Shape comparison, memory analysis
- **Operation Status**: Success/failure for each step

### Quality Metrics  
When `quality_check=True`, provides:
- **Mean Difference**: Average statistical difference between latents
- **Standard Deviation**: Variability comparison
- **Absolute Difference**: Average and maximum absolute differences
- **Shape Validation**: Ensures consistent tensor dimensions

### Example Process Report
```
🔄 VAE ROUND-TRIP PROCESS REPORT
==================================================
📊 Input LATENT: Shape (1, 4, 64, 64), Memory: 0.25 MB, Range: -2.341 to 3.892, Mean: 0.123
🔄 DECODING: LATENT → IMAGE  
✅ DECODE: Success
🖼️ DECODED IMAGE: Shape (1, 512, 512, 3), Memory: 3.00 MB, ✅ Valid range [0-1]
🔄 ENCODING: IMAGE → LATENT
✅ ENCODE: Success  
📊 Output LATENT: Shape (1, 4, 64, 64), Memory: 0.25 MB, Range: -2.298 to 3.847, Mean: 0.119
🔍 QUALITY CHECK: Mean diff: 0.0040, Std diff: 0.0023, Avg abs diff: 0.0156, Max abs diff: 0.2341

📋 OPERATION SUMMARY:
  Decode Success: ✅ Yes
  Encode Success: ✅ Yes  
  Overall Status: ✅ Complete
```

## Advanced Options

### Decode Only Mode
Set `decode_only=True` to skip re-encoding:
- Faster processing for preview purposes
- Useful when you only need visual inspection
- Returns original latent unchanged

### Memory Optimization
For large latents:
- Monitor memory usage in process_info
- Use decode_only mode to reduce memory pressure
- Process smaller batches if needed

### Error Handling
Robust fallback mechanisms:
- **Decode Failure**: Creates black fallback image
- **Encode Failure**: Returns original latent  
- **Analysis Errors**: Provides diagnostic information

## Integration Patterns

### With Sampling Workflows
```
KSampler → VAERoundTrip → Preview decoded image
                       → Continue with reencoded latent
```

### With VAE Comparison
```
LatentInput → VAERoundTrip(VAE_SD15) → OutputDev(input_1)
           → VAERoundTrip(VAE_SDXL) → OutputDev(input_2)
           → Compare quality metrics
```

### With Image Processing
```
VAERoundTrip → decoded_image → ImageProcessor → NewImage
            → reencoded_latent → Continue sampling
```

## Performance Notes

### Memory Usage
- **Input Latent**: ~0.25 MB for 512x512 equivalent
- **Decoded Image**: ~3 MB for 512x512 RGB  
- **Total Peak**: ~6-7 MB during full round-trip

### Processing Speed
- **Decode**: Depends on VAE model and latent size
- **Analysis**: Minimal overhead
- **Encode**: Similar to decode timing

### Optimization Tips
- Use `decode_only=True` for preview workflows
- Disable `quality_check` for faster processing  
- Monitor memory usage with large batches

## Troubleshooting

### Decode Failures
- **Incompatible VAE**: Check VAE model matches latent format
- **Invalid Latent**: Ensure latent contains 'samples' key
- **Memory Issues**: Reduce batch size or latent dimensions

### Encode Failures  
- **Image Format**: Verify decoded image is [B,H,W,C] format
- **Value Range**: Check image values are in [0-1] range
- **Memory**: Ensure sufficient RAM for encoding operation

### Quality Issues
- **High Differences**: May indicate VAE quality limitations
- **Shape Mismatches**: Check for VAE model consistency
- **Statistical Drift**: Normal small variations expected

## Technical Details

### ComfyUI Compatibility
- **LATENT Format**: Expects `{"samples": tensor}` dictionary
- **IMAGE Format**: Returns [Batch, Height, Width, Channels] tensors  
- **VAE Interface**: Compatible with all ComfyUI VAE models
- **Caching**: Proper `IS_CHANGED` implementation for efficiency

### Tensor Operations
- Safe tensor operations with fallback handling
- Memory-efficient processing with cleanup
- Cross-platform compatibility (CPU/GPU)
- Robust error handling for edge cases