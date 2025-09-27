# SDXL Expert Writer - Streamlined Prompt Generation

## Overview
The **XDEV_LLMSDXLExpertWriter** is a focused, streamlined SDXL prompt generation tool that analyzes three key inputs to produce optimized, model-friendly prompts.

## Key Features

### 🎯 **Three-Input Analysis**
- **USER_PROMPT**: What you want to generate (subject, scene, action)
- **STYLE_SETTINGS**: Visual style, lighting, mood, artistic direction
- **RULES**: Technical requirements, constraints, quality standards

### ⚡ **Streamlined Output**
- Single optimized SDXL prompt string
- 50-150 words maximum
- No explanations - just the prompt
- Directly usable in SDXL workflows

### 🔧 **Expert Optimization**
- Analyzes inputs for core elements
- Prioritizes SDXL-friendly structure
- Maintains photorealistic focus
- Includes technical quality terms

## Input Fields

### **USER_PROMPT** (Required)
- **Purpose**: Main subject/scene description
- **Examples**: 
  - "young woman reading by a window"
  - "cyberpunk street scene at night"
  - "professional headshot portrait"
- **Tips**: Be specific about subject, action, and basic setting

### **STYLE_SETTINGS** (Required)
- **Purpose**: Visual style, lighting, mood, artistic direction  
- **Examples**:
  - "natural lighting, soft colors, cozy atmosphere, golden hour"
  - "neon lighting, urban decay, futuristic elements, rain reflections"
  - "studio lighting, neutral background, clean composition"
- **Tips**: Focus on lighting, color palette, mood, artistic elements

### **RULES** (Required)
- **Purpose**: Technical requirements, constraints, quality standards
- **Examples**:
  - "photorealistic, high quality, detailed, no anime style"
  - "cinematic quality, high contrast, no cartoons"
  - "commercial quality, sharp focus, professional standards"
- **Tips**: Specify quality level, avoid unwanted styles, set technical standards

## Expert System Prompt

The node uses a specialized system prompt that:

1. **Analyzes** USER_PROMPT + STYLE_SETTINGS + RULES
2. **Extracts** core subject/scene from USER_PROMPT
3. **Applies** STYLE_SETTINGS for visual direction
4. **Integrates** RULES as constraints and quality guidelines
5. **Optimizes** for SDXL model performance

### **Prompt Structure Priority**:
1. Main subject (from USER_PROMPT)
2. Key descriptors (physical, emotional)
3. Style/mood elements (from STYLE_SETTINGS)
4. Technical quality (from RULES)
5. Lighting/composition details
6. Camera/lens specifications if relevant

## Configuration Options

### **Temperature** (0.0-2.0, default: 0.3)
- **Low (0.0-0.3)**: More consistent, predictable results
- **Medium (0.4-0.7)**: Balanced creativity and structure
- **High (0.8-2.0)**: More creative variations

### **Max Tokens** (100-4096, default: 800)
- Controls response length
- 800 tokens is optimal for concise SDXL prompts
- Lower values for very brief prompts
- Higher values for detailed descriptions

### **Fallback Support**
- Automatically generates basic prompt if LLM fails
- Combines inputs intelligently
- Includes quality terms from RULES
- Ensures workflow continues even on errors

## Usage Examples

### **Example 1: Cozy Portrait**
```
USER_PROMPT: "young woman reading by a window"
STYLE_SETTINGS: "natural lighting, soft colors, cozy atmosphere, golden hour" 
RULES: "photorealistic, high quality, detailed, no anime style"

Output: "young woman reading book by large window, soft natural lighting, golden hour glow, cozy atmosphere, warm colors, peaceful expression, detailed facial features, photorealistic, high quality"
```

### **Example 2: Cyberpunk Scene**
```
USER_PROMPT: "cyberpunk street scene at night"
STYLE_SETTINGS: "neon lighting, urban decay, futuristic elements, rain reflections"
RULES: "cinematic quality, high contrast, no cartoons"

Output: "cyberpunk street scene at night, neon lighting, urban decay, futuristic elements, rain-soaked pavement with reflections, high contrast lighting, cinematic quality, detailed architecture"
```

### **Example 3: Professional Portrait**
```
USER_PROMPT: "professional headshot portrait"
STYLE_SETTINGS: "studio lighting, neutral background, clean composition"
RULES: "commercial quality, sharp focus, professional standards"

Output: "professional headshot portrait, studio lighting setup, neutral gray background, clean composition, sharp focus, commercial photography quality, professional business attire"
```

## Comparison with SDXL Photo Enhancer

| Feature | SDXL Expert Writer | SDXL Photo Enhancer |
|---------|-------------------|---------------------|
| **Focus** | Single optimized prompt | Full JSON with settings |
| **Inputs** | 3 focused fields | Complex brief + style notes |
| **Output** | Clean prompt string | JSON with negatives + settings |
| **Use Case** | Quick, direct prompts | Complete SDXL workflows |
| **Complexity** | Streamlined | Comprehensive |
| **Speed** | Fast generation | Detailed analysis |

## Best Practices

### **Input Optimization**
1. **USER_PROMPT**: Be specific but concise
2. **STYLE_SETTINGS**: Focus on visual elements
3. **RULES**: Set clear quality standards

### **Style Combinations**
- **Portrait**: Natural/studio lighting + professional quality
- **Landscapes**: Golden hour/dramatic lighting + cinematic quality  
- **Urban**: Neon/street lighting + gritty atmosphere
- **Architecture**: Clean lighting + professional standards

### **Quality Control**
- Use lower temperature (0.2-0.3) for consistent results
- Include specific "no X style" rules for unwanted elements
- Test different STYLE_SETTINGS for variety
- Enable fallback for reliability

## Integration Tips

### **Workflow Position**
- Use early in workflow to generate base prompts
- Feed output to SDXL nodes or prompt refinement tools
- Combine with other prompt tools for variations

### **Prompt Chaining**
- Use output as base for PromptWeighter
- Combine with PromptCombiner for multi-aspect prompts
- Process through PromptCleaner for optimization

### **Quality Assurance**
- Monitor generation_info output for LLM performance
- Use fallback mode during development
- Test with different temperature settings

The **SDXL Expert Writer** is perfect when you need fast, focused SDXL prompts without the complexity of full JSON outputs. It excels at translating natural descriptions into SDXL-optimized prompts while maintaining creative control through the three-input analysis system.