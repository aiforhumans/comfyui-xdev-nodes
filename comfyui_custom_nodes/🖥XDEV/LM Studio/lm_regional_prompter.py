"""
LM Studio Regional Prompter Helper Node

Generates segmented prompts for ComfyUI regional prompting workflows.
Creates separate descriptions for different image regions with proper spatial awareness.
Based on research: ComfyUI ConditioningSetArea, ConditioningSetMask, ConditioningCombine
"""

import json
import re
import urllib.error
import urllib.request

try:
    from .lm_base_node import LMStudioPromptBaseNode
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode


class LMStudioRegionalPrompterHelper(LMStudioPromptBaseNode):
    """
    Generates region-specific prompts for ComfyUI's regional prompting system.
    Creates separate, spatially-aware descriptions for multiple regions.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "composition_concept": ("STRING", {"multiline": True, "default": ""}),
                "region_count": (["2", "3", "4"], {"default": "2"}),
                "region_layout": (["left_right", "top_bottom", "quadrants", "center_surround", "custom"], {"default": "left_right"}),
                "region_1_description": ("STRING", {"multiline": True, "default": ""}),
                "region_2_description": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "region_3_description": ("STRING", {"multiline": True, "default": ""}),
                "region_4_description": ("STRING", {"multiline": True, "default": ""}),
                "blend_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                **cls.get_common_optional_inputs(),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("region_1_prompt", "region_2_prompt", "region_3_prompt", "region_4_prompt", "composition_guide", "info")
    FUNCTION = "generate_regional_prompts"
    
    def generate_regional_prompts(self, composition_concept: str, region_count: str, region_layout: str,
                                  region_1_description: str, region_2_description: str,
                                  region_3_description: str = "", region_4_description: str = "",
                                  blend_strength: float = 1.0, temperature: float = 0.7,
                                  server_url: str = "http://localhost:1234", model: str = "") -> tuple:
        """Generate region-specific prompts."""
        
        num_regions = int(region_count)
        
        if not composition_concept.strip():
            return ("", "", "", "", "", "⚠️ Error: Composition concept is required")
        
        # Build region descriptions list
        region_descriptions = [region_1_description, region_2_description, region_3_description, region_4_description]
        region_descriptions = [desc for desc in region_descriptions[:num_regions] if desc.strip()]
        
        if len(region_descriptions) < num_regions:
            return ("", "", "", "", "", f"⚠️ Error: {num_regions} regions requested but only {len(region_descriptions)} descriptions provided")
        
        # Layout information for spatial awareness
        layout_info = {
            "left_right": {
                "2": ["Left half of image", "Right half of image"],
                "3": ["Left third", "Center third", "Right third"],
                "4": ["Far left quarter", "Center-left quarter", "Center-right quarter", "Far right quarter"]
            },
            "top_bottom": {
                "2": ["Top half of image", "Bottom half of image"],
                "3": ["Top third", "Middle third", "Bottom third"],
                "4": ["Top quarter", "Upper-middle quarter", "Lower-middle quarter", "Bottom quarter"]
            },
            "quadrants": {
                "4": ["Top-left quadrant", "Top-right quadrant", "Bottom-left quadrant", "Bottom-right quadrant"]
            },
            "center_surround": {
                "2": ["Center/focal area", "Surrounding area/edges"],
                "3": ["Center focal point", "Mid-range surrounding", "Outer edges/background"],
            },
            "custom": {
                "2": ["Region 1", "Region 2"],
                "3": ["Region 1", "Region 2", "Region 3"],
                "4": ["Region 1", "Region 2", "Region 3", "Region 4"]
            }
        }
        
        spatial_info = layout_info.get(region_layout, layout_info["custom"]).get(region_count, [f"Region {i+1}" for i in range(num_regions)])
        
        # Build system prompt with research findings
        system_prompt = f"""You are an expert in ComfyUI regional prompting. Generate separate, cohesive prompts for different image regions.

COMPOSITION CONCEPT:
{composition_concept}

REGIONAL PROMPTING RESEARCH:
- Each region has separate conditioning with spatial masks/areas
- Regions are combined using ConditioningCombine node
- Strength parameter controls regional influence (current: {blend_strength})
- Proper spatial awareness prevents element bleed-through
- Each region should be self-contained but harmonious with overall composition

LAYOUT: {region_layout}
NUMBER OF REGIONS: {num_regions}

SPATIAL LAYOUT:
{chr(10).join([f"- Region {i+1}: {spatial_info[i]}" for i in range(num_regions)])}

REGION DESCRIPTIONS PROVIDED:
{chr(10).join([f"Region {i+1}: {region_descriptions[i]}" for i in range(num_regions)])}

OPTIMIZATION RULES:
1. Create prompts that work within the defined spatial region
2. Avoid elements that would naturally span multiple regions
3. Ensure visual coherence between adjacent regions
4. Use spatial descriptors appropriate for each region
5. Maintain consistent lighting and atmosphere across regions
6. Prevent element duplication between regions
7. Each prompt should enhance the overall composition

STRENGTH GUIDANCE (current: {blend_strength}):
- 1.0: Normal influence (balanced)
- >1.0: Stronger regional control (more distinct regions)
- <1.0: Softer regional control (more blending)

IMPORTANT: Always respond with valid JSON format.

Respond with JSON:
{{
  "region_1": "detailed prompt for region 1",
  "region_2": "detailed prompt for region 2",
  {"region_3": "detailed prompt for region 3"," if num_regions >= 3 else ""}
  {"region_4": "detailed prompt for region 4"," if num_regions >= 4 else ""}
  "composition_guide": "how regions work together spatially",
  "blending_notes": "notes on regional boundaries and transitions",
  "negative_prompt": "universal negative prompt for all regions"
}}"""
        
        user_prompt = f"""Generate {num_regions} regional prompts for this composition:

Overall Concept: {composition_concept}
Layout: {region_layout}

Region Descriptions:
{chr(10).join([f"{i+1}. {spatial_info[i]}: {region_descriptions[i]}" for i in range(num_regions)])}

Create spatially-aware prompts that work together cohesively."""
        
        # Build API payload
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "stream": False
        }
        
        if model.strip():
            payload["model"] = model.strip()
        
        lm_studio_url = f"{server_url}/v1/chat/completions"

        try:
            # Make API request
            req = urllib.request.Request(
                lm_studio_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result['choices'][0]['message']['content']
            
            # Parse JSON response
            json_match = re.search(r'\{[^{}]*"region_1"[^{}]*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    
                    region_1 = parsed.get("region_1", region_descriptions[0])
                    region_2 = parsed.get("region_2", region_descriptions[1] if len(region_descriptions) > 1 else "")
                    region_3 = parsed.get("region_3", region_descriptions[2] if len(region_descriptions) > 2 else "")
                    region_4 = parsed.get("region_4", region_descriptions[3] if len(region_descriptions) > 3 else "")
                    composition_guide = parsed.get("composition_guide", "")
                    blending_notes = parsed.get("blending_notes", "")
                    negative_prompt = parsed.get("negative_prompt", "")
                    
                    # Build comprehensive guide
                    guide = f"""COMPOSITION GUIDE:
{composition_guide}

LAYOUT: {region_layout}
REGIONS: {num_regions}

SPATIAL ARRANGEMENT:
{chr(10).join([f"Region {i+1} - {spatial_info[i]}: {['region_1', 'region_2', 'region_3', 'region_4'][i][:50]}..." for i in range(num_regions)])}

BLENDING NOTES:
{blending_notes}

RECOMMENDED NEGATIVE PROMPT:
{negative_prompt}

COMFYUI WORKFLOW TIPS:
1. Use ConditioningSetArea or ConditioningSetMask for each region
2. Set strength to {blend_strength} for each region
3. Combine all regions with ConditioningCombine node
4. Connect combined conditioning to KSampler positive input"""
                    
                    # Build info string
                    info = f"""Layout: {region_layout}
Regions: {num_regions}
Blend Strength: {blend_strength}
Temperature: {temperature}

Spatial Layout:
{chr(10).join([f"  {i+1}. {spatial_info[i]}" for i in range(num_regions)])}"""
                    
                    return (region_1, region_2, region_3, region_4, guide, info)
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            region_1 = region_descriptions[0] if len(region_descriptions) > 0 else ""
            region_2 = region_descriptions[1] if len(region_descriptions) > 1 else ""
            region_3 = region_descriptions[2] if len(region_descriptions) > 2 else ""
            region_4 = region_descriptions[3] if len(region_descriptions) > 3 else ""
            
            guide = f"""Layout: {region_layout}
Regions: {num_regions}
⚠️ JSON parsing failed, using original descriptions"""
            
            info = f"Layout: {region_layout}\nRegions: {num_regions}\n⚠️ JSON parsing failed"
            
            return (region_1, region_2, region_3, region_4, guide, info)
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No details"
            error_msg = f"❌ HTTP Error {e.code}: {e.reason}\n{error_body}"
            print(f"[LM Studio Regional Prompter Helper] {error_msg}")
            return ("", "", "", "", "", error_msg)
        
        except urllib.error.URLError as e:
            error_msg = f"❌ Connection Error: {e.reason}\nIs LM Studio running at {lm_studio_url}?"
            print(f"[LM Studio Regional Prompter Helper] {error_msg}")
            return ("", "", "", "", "", error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"[LM Studio Regional Prompter Helper] {error_msg}")
            return ("", "", "", "", "", error_msg)


NODE_CLASS_MAPPINGS = {
    "XDEVLMStudioRegionalPrompterHelper": LMStudioRegionalPrompterHelper,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVLMStudioRegionalPrompterHelper": "LM Studio Regional Prompter Helper",
}
