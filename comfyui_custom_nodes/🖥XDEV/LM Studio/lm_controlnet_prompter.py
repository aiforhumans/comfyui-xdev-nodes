"""
LM Studio ControlNet Prompter Node

Optimizes prompts for ControlNet workflows based on control type.
Prevents prompt-control conflicts and balances text vs control influence.
Based on research: ControlNet paper, control strength, guidance patterns
"""

import json
import re
import urllib.error
import urllib.request

try:
    from .lm_base_node import LMStudioPromptBaseNode
except ImportError:
    from lm_base_node import LMStudioPromptBaseNode


class LMStudioControlNetPrompter(LMStudioPromptBaseNode):
    """
    Generates ControlNet-optimized prompts that work harmoniously with control inputs.
    Adjusts emphasis based on control type and strength.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": ""}),
                "control_type": ([
                    "canny_edge", "hed_boundary", "mlsd_lines", "depth", "normal_map",
                    "pose", "segmentation", "scribble", "lineart", "openpose",
                    "tile", "shuffle", "inpaint", "reference", "custom"
                ], {"default": "pose"}),
                "control_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "prompt_strategy": (["complement", "minimal", "descriptive", "creative"], {"default": "complement"}),
            },
            "optional": {
                **cls.get_common_optional_inputs(),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("controlnet_prompt", "guidance_notes", "negative_prompt", "info")
    FUNCTION = "generate_controlnet_prompt"
    
    def generate_controlnet_prompt(self, base_prompt: str, control_type: str, control_strength: float,
                                   prompt_strategy: str, temperature: float = 0.6, 
                                   server_url: str = "http://localhost:1234", model: str = "") -> tuple:
        """Generate ControlNet-optimized prompt."""
        
        if not base_prompt.strip():
            return ("", "", "", "⚠️ Error: Base prompt is required")
        
        # Control type characteristics (from research)
        control_characteristics = {
            "canny_edge": {
                "desc": "Precise, thin edges - best for sharp boundaries and object outlines",
                "emphasize": "sharp edges, clear boundaries, defined shapes, high contrast",
                "avoid": "blurry, soft focus, gradients, smooth transitions",
                "guidance": "Structure is controlled by edges. Prompt controls style, colors, textures."
            },
            "hed_boundary": {
                "desc": "Soft, natural edges - good for recoloring and stylizing",
                "emphasize": "natural edges, artistic style, color harmony, smooth transitions",
                "avoid": "over-sharpening, harsh lines",
                "guidance": "Softer edge control allows more creative freedom in style and colors."
            },
            "mlsd_lines": {
                "desc": "Straight lines only - ideal for architecture and structures",
                "emphasize": "architectural, geometric, straight lines, structural, buildings",
                "avoid": "organic shapes, curves, natural elements",
                "guidance": "Perfect for buildings and man-made structures. Prompt adds materials and details."
            },
            "depth": {
                "desc": "Depth maps preserve geometric structure and spatial relationships",
                "emphasize": "3D arrangement, spatial depth, foreground/background, perspective",
                "avoid": "conflicting depth cues, flat compositions",
                "guidance": "Depth is locked. Prompt controls appearance, lighting, and materials."
            },
            "normal_map": {
                "desc": "Fine geometric details and surface normals",
                "emphasize": "surface details, texture, lighting interaction, 3D form",
                "avoid": "flat appearance, conflicting geometry",
                "guidance": "Better than depth for fine details. Prompt adds materials and lighting."
            },
            "pose": {
                "desc": "Human pose skeleton control - body position is fixed",
                "emphasize": "character appearance, clothing, style, facial features, NOT pose/position",
                "avoid": "pose descriptors, position keywords that conflict with skeleton",
                "guidance": "Pose is FIXED by skeleton. Describe APPEARANCE only, not pose or position."
            },
            "segmentation": {
                "desc": "Semantic region control - colored masks define object areas",
                "emphasize": "object details matching segmentation regions, textures, styles",
                "avoid": "objects not in segmentation map, conflicting layouts",
                "guidance": "Layout is controlled by segments. Prompt refines appearance of each region."
            },
            "scribble": {
                "desc": "Loose structural guidance from rough sketches",
                "emphasize": "match scribble structure, artistic interpretation",
                "avoid": "precise details not in scribble",
                "guidance": "Scribble provides loose structure. Prompt adds detail and refinement."
            },
            "lineart": {
                "desc": "Clean line drawings for anime and illustration styles",
                "emphasize": "linework style, clean lines, illustration quality",
                "avoid": "photorealistic, conflicting art styles",
                "guidance": "Lines are preserved. Prompt controls coloring and shading style."
            },
            "openpose": {
                "desc": "OpenPose body keypoints - detailed pose control",
                "emphasize": "character details, clothing, accessories, NOT pose",
                "avoid": "any pose/position descriptors",
                "guidance": "Identical to pose control. Focus entirely on appearance, not positioning."
            },
            "tile": {
                "desc": "Seamless tiling and texture preservation",
                "emphasize": "texture quality, pattern coherence, seamless edges",
                "avoid": "non-repeating elements",
                "guidance": "Preserves tileability. Prompt enhances texture quality."
            },
            "shuffle": {
                "desc": "Color and style control while maintaining content",
                "emphasize": "color palette, artistic style, mood",
                "avoid": "structural changes",
                "guidance": "Content is preserved. Prompt changes colors and artistic treatment."
            },
            "inpaint": {
                "desc": "Masked region filling with context awareness",
                "emphasize": "seamless integration, match surrounding context",
                "avoid": "elements that clash with existing image",
                "guidance": "Describe what should fill the mask while matching surroundings."
            },
            "reference": {
                "desc": "Style and composition reference from image",
                "emphasize": "elements matching reference style",
                "avoid": "conflicting styles",
                "guidance": "Reference provides style. Prompt can modify subject and details."
            },
            "custom": {
                "desc": "Custom control type",
                "emphasize": "elements that work with control",
                "avoid": "conflicting instructions",
                "guidance": "Adapt prompt to complement custom control input."
            }
        }
        
        control_info = control_characteristics.get(control_type, control_characteristics["custom"])
        
        # Prompt strategy instructions
        strategy_instructions = {
            "complement": "Create a prompt that complements the control without conflicting. Balance text and control influence.",
            "minimal": "Use minimal, essential keywords only. Let the control dominate the generation.",
            "descriptive": "Provide detailed descriptions of elements NOT controlled by the control type.",
            "creative": "Take creative liberties with elements the control doesn't specify."
        }
        
        strategy_instruction = strategy_instructions[prompt_strategy]
        
        # Build system prompt with research findings
        system_prompt = f"""You are a ControlNet prompt optimization expert. ControlNet combines text prompts with visual control inputs.

CONTROL TYPE: {control_type}
DESCRIPTION: {control_info['desc']}
CONTROL STRENGTH: {control_strength}

RESEARCH-BACKED GUIDANCE:
{control_info['guidance']}

CONTROL STRENGTH INTERPRETATION:
- {control_strength} < 0.5: Control has minimal influence, prompt dominates
- {control_strength} = 1.0: Balanced control and prompt (DEFAULT)
- {control_strength} > 1.0: Control dominates, prompt has less influence

PROMPT STRATEGY: {prompt_strategy}
{strategy_instruction}

OPTIMIZATION RULES:
1. EMPHASIZE: {control_info['emphasize']}
2. AVOID: {control_info['avoid']}
3. For HIGH control strength (>{control_strength if control_strength > 1.0 else '1.0'}): Focus on colors, materials, style - avoid structural descriptors
4. For LOW control strength (<{control_strength if control_strength < 1.0 else '1.0'}): Add more structural and compositional descriptors
5. NEVER conflict with what the control input specifies
6. Describe elements the control DOESN'T control

SPECIAL RULES FOR POSE/OPENPOSE:
- NEVER mention pose, position, stance, posture, gesture in prompt
- NEVER use keywords like "standing", "sitting", "running", "arms raised"
- ONLY describe appearance: face, body type, clothing, style, lighting
- The skeleton LOCKS the pose - your prompt CANNOT change it

IMPORTANT: Always respond with valid JSON format.

Respond with JSON:
{{
  "optimized_prompt": "the ControlNet-optimized prompt",
  "guidance_notes": "how the prompt works with this control type",
  "negative_prompt": "negative prompt to avoid conflicts",
  "added_keywords": ["keyword1", "keyword2"],
  "removed_keywords": ["keyword1", "keyword2"],
  "reasoning": "brief explanation"
}}"""
        
        user_prompt = f"""Optimize this prompt for ControlNet:

Base Prompt:
{base_prompt}

Control Type: {control_type}
Control Strength: {control_strength}
Strategy: {prompt_strategy}

Generate the ControlNet-optimized prompt."""
        
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
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result['choices'][0]['message']['content']
            
            # Parse JSON response
            json_match = re.search(r'\{[^{}]*"optimized_prompt"[^{}]*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    
                    optimized_prompt = parsed.get("optimized_prompt", base_prompt)
                    guidance_notes = parsed.get("guidance_notes", "")
                    negative_prompt = parsed.get("negative_prompt", "")
                    added_keywords = parsed.get("added_keywords", [])
                    removed_keywords = parsed.get("removed_keywords", [])
                    reasoning = parsed.get("reasoning", "")
                    
                    # Build comprehensive guidance notes
                    notes = f"""Control Type: {control_type}
{control_info['desc']}

Optimization Strategy:
{guidance_notes}

Added Keywords: {', '.join(added_keywords) if added_keywords else 'None'}
Removed Keywords: {', '.join(removed_keywords) if removed_keywords else 'None'}

Reasoning:
{reasoning}"""
                    
                    # Build info string
                    info = f"""Control: {control_type}
Strength: {control_strength}
Strategy: {prompt_strategy}
Temperature: {temperature}
Keywords Added: {len(added_keywords)}
Keywords Removed: {len(removed_keywords)}"""
                    
                    return (optimized_prompt, notes, negative_prompt, info)
                    
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            optimized_prompt = response_text.strip()
            notes = f"Control: {control_type}\n{control_info['guidance']}"
            negative_prompt = control_info['avoid']
            info = f"Control: {control_type}\nStrength: {control_strength}\n⚠️ JSON parsing failed"
            
            return (optimized_prompt, notes, negative_prompt, info)
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else "No details"
            error_msg = f"❌ HTTP Error {e.code}: {e.reason}\n{error_body}"
            print(f"[LM Studio ControlNet Prompter] {error_msg}")
            return (base_prompt, "", "", error_msg)
        
        except urllib.error.URLError as e:
            error_msg = f"❌ Connection Error: {e.reason}\nIs LM Studio running at {lm_studio_url}?"
            print(f"[LM Studio ControlNet Prompter] {error_msg}")
            return (base_prompt, "", "", error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"[LM Studio ControlNet Prompter] {error_msg}")
            return (base_prompt, "", "", error_msg)


NODE_CLASS_MAPPINGS = {
    "XDEVLMStudioControlNetPrompter": LMStudioControlNetPrompter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEVLMStudioControlNetPrompter": "LM Studio ControlNet Prompter",
}
