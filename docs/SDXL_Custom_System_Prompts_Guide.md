# SDXL Photo Enhancer - Custom System Prompt Guide

## Overview
The **XDEV_LLMSDXLPhotoEnhancer** now supports fully customizable system prompts and LLM settings, giving you complete control over how the AI generates your SDXL prompts.

## New Custom Options

### 🎯 **Custom System Prompt**
- **Parameter**: `custom_system_prompt` (multiline text, optional)
- **Default**: Empty (uses built-in SDXL expert prompt)
- **Purpose**: Override the default system prompt with your own specialized instructions

**When to use custom prompts**:
- Specialized photography styles (cyberpunk, vintage, architectural, etc.)
- Specific artistic movements or aesthetics  
- Brand-specific or project-specific requirements
- Different output formats or structures
- Alternative creative approaches

### ⚙️ **LLM Settings Control**

#### **Temperature**
- **Range**: 0.0 to 2.0 (step: 0.1)
- **Default**: 0.4 (precise, technical)
- **Low (0.0-0.3)**: More deterministic, technical, consistent
- **Medium (0.4-0.8)**: Balanced creativity and structure
- **High (0.9-2.0)**: More creative, varied, experimental

#### **Max Tokens**  
- **Range**: 100 to 8192 (step: 100)
- **Default**: 2000
- **Purpose**: Controls response length and detail level
- **Recommendations**: 
  - Simple prompts: 1000-1500
  - Complex scenes: 2000-3000
  - Detailed technical specs: 3000-4000+

#### **Top P (Nucleus Sampling)**
- **Range**: 0.0 to 1.0 (step: 0.05)  
- **Default**: 0.7
- **Purpose**: Controls response diversity
- **Low (0.5-0.6)**: More focused, predictable
- **Medium (0.7-0.8)**: Balanced variety
- **High (0.9-1.0)**: More diverse, creative

## Custom System Prompt Examples

### 1. **Cyberpunk Photography Specialist**
```
You are an expert in cyberpunk and futuristic photography. Create detailed SDXL prompts that capture the essence of cyberpunk aesthetics with neon lighting, urban decay, and high-tech elements. Focus on creating atmospheric, moody images with strong contrast and vibrant neon colors.

Output format should be JSON:
{
  "prompt": "detailed cyberpunk prompt with neon, urban elements, mood",
  "negative_prompt": "things to avoid for cyberpunk aesthetic",
  "settings": {"width": int, "height": int, "steps": int, "cfg": float, "sampler": "string", "seed": int},
  "notes": "technical and aesthetic explanation"
}
```

### 2. **Film Photography Expert**
```
You are a master of analog film photography and vintage aesthetics. Generate SDXL prompts that recreate the look and feel of classic film stocks like Kodak Portra, Fuji films, and black & white emulsions. Include proper grain structure, color science, and period-appropriate composition.

Focus on:
- Authentic film grain and color rendition
- Period-appropriate lighting and composition  
- Classic lens characteristics and depth of field
- Vintage wardrobe and environmental details

Return JSON with film-specific technical settings.
```

### 3. **Architectural Photography**  
```
You are a specialist in architectural and interior design photography. Create SDXL prompts for stunning architectural images with perfect perspective, dramatic lighting, and professional composition. Emphasize geometric forms, materials, and spatial relationships.

Technical focus:
- Wide-angle perspective correction
- HDR-style lighting (but natural looking)
- Material textures (concrete, glass, steel, wood)
- Leading lines and compositional geometry
- Professional architectural photography standards

Output detailed camera settings for architectural work.
```

### 4. **Portrait Specialist**
```
You are a master portrait photographer specializing in professional headshots and artistic portraits. Generate SDXL prompts that create compelling human portraits with perfect lighting, natural expressions, and technical excellence.

Expertise areas:
- Studio and natural lighting setups
- Flattering angles and compositions  
- Skin tone accuracy and texture
- Eye contact and expression guidance
- Professional wardrobe and styling
- Background selection and bokeh control

Focus on creating connection between subject and viewer.
```

## Usage Patterns

### **Default Mode** (Built-in Expert)
- Leave `custom_system_prompt` empty
- Uses the comprehensive SDXL photorealistic expert prompt
- Best for: General photography, beginners, consistent results
- Settings: Default values work well

### **Custom Specialization Mode**
- Provide specialized system prompt
- Adjust temperature for creativity level
- Increase max_tokens for detailed responses  
- Fine-tune top_p for response variety
- Best for: Specialized styles, advanced users, specific projects

### **Experimental Mode**
- Creative custom prompts
- Higher temperature (0.8-1.2)
- Higher top_p (0.8-0.9)
- More tokens for exploration
- Best for: Artistic experimentation, unique styles

## Best Practices

### **System Prompt Design**
1. **Be Specific**: Define your expertise area clearly
2. **Set Expectations**: Explain the desired output style
3. **Include Examples**: Show the format you want
4. **Technical Focus**: Mention camera/technical requirements
5. **JSON Structure**: Always specify the expected output format

### **Parameter Tuning**
1. **Start Conservative**: Begin with default settings
2. **Adjust Gradually**: Small increments for testing
3. **Match Style to Settings**: 
   - Technical work: Lower temperature
   - Creative work: Higher temperature
   - Detailed scenes: More tokens
4. **Test and Iterate**: Compare outputs with different settings

### **Workflow Integration**  
1. **Template Library**: Create system prompt templates for different styles
2. **Setting Presets**: Save parameter combinations that work well
3. **A/B Testing**: Compare custom vs built-in prompts
4. **Quality Control**: Use fallback options for reliability

## Example Workflow

1. **Define Your Style**: Choose your photographic specialty
2. **Write System Prompt**: Create detailed instructions for the AI
3. **Tune Parameters**: Adjust creativity and response length
4. **Test Enhancement**: Run with sample briefs
5. **Refine Approach**: Iterate on prompt and settings
6. **Save Template**: Document successful combinations

## Troubleshooting

### **Poor Results**
- Check system prompt clarity and specificity
- Reduce temperature for more consistent output
- Increase max_tokens if responses seem cut off
- Verify JSON format requirements in prompt

### **Inconsistent Output**
- Lower temperature and top_p values
- Add more specific instructions in system prompt
- Include format examples in the prompt
- Use fallback_on_error for reliability

### **Creative Limitations**
- Increase temperature and top_p
- Add creative freedom language to system prompt
- Allow more tokens for exploration
- Encourage experimentation in instructions

## Advanced Features

### **Multi-Style Prompts**
Create system prompts that can handle multiple styles based on user brief keywords.

### **Quality Levels** 
Define different detail levels (quick, standard, professional, cinematic).

### **Format Variations**
Support different output formats beyond the standard JSON structure.

### **Adaptive Prompting**
Create prompts that adjust their approach based on the input brief content.

The custom system prompt feature transforms the SDXL Photo Enhancer from a general tool into a specialized expert system tailored to your exact creative vision and technical requirements.