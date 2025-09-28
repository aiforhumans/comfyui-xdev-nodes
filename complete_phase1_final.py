#!/usr/bin/env python3
"""
Phase 1 Completion Script - Final Fixes
Fix remaining string category and add all DISPLAY_NAME attributes
"""

import os
import re
from pathlib import Path

# Backup tracking
BACKUP_DIR = Path("backups")
processed_files = []

def backup_file(file_path):
    """Create backup of file before modification"""
    backup_path = BACKUP_DIR / f"{file_path.name}.backup"
    BACKUP_DIR.mkdir(exist_ok=True)
    
    if not backup_path.exists():
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"    📁 Backup created: {backup_path}")
    return backup_path

def fix_remaining_string_category():
    """Fix the one remaining string category in image.py"""
    image_file = Path("xdev_nodes/nodes/image.py")
    
    print(f"\n🔧 FIXING STRING CATEGORY: {image_file}")
    print("-" * 50)
    
    backup_file(image_file)
    content = image_file.read_text(encoding='utf-8')
    
    # Fix PickByBrightness category
    old_pattern = r'CATEGORY\s*=\s*"XDev/Image"'
    new_value = 'CATEGORY = NodeCategories.IMAGE_ANALYSIS'
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_value, content)
        image_file.write_text(content, encoding='utf-8')
        print(f"    ✅ Fixed PickByBrightness category")
        return True
    else:
        print(f"    ⚠️ Pattern not found in {image_file}")
        return False

def add_display_names():
    """Add DISPLAY_NAME attributes to all nodes"""
    
    # Mapping of node class names to display names
    DISPLAY_NAME_MAPPINGS = {
        # Basic nodes
        "HelloString": "Hello String (XDev)",
        "AnyPassthrough": "Any Passthrough (XDev)", 
        
        # Development nodes
        "OutputDev": "Output Dev (XDev)",
        "InputDev": "Input Dev (XDev)",
        
        # Face swap nodes
        "InsightFaceModelManager": "InsightFace Model Manager (XDev)",
        "XDEV_FaceSwapApply": "Face Swap Apply (XDev)",
        "XDEV_AdvancedFaceSwap": "Advanced Face Swap (XDev)",
        "ErrorImage": "Error Image (XDev)",
        "XDEV_FaceQualityAnalyzer": "Face Quality Analyzer (XDev)",
        "XDEV_InsightFaceFaceSwap": "InsightFace Face Swap (XDev)",
        "InsightFaceModelWrapper": "InsightFace Model Wrapper (XDev)",
        "XDEV_InsightFaceSwapperLoader": "InsightFace Swapper Loader (XDev)",
        "XDEV_InsightFaceProcessor": "InsightFace Processor (XDev)",
        
        # Image nodes
        "PickByBrightness": "Pick By Brightness (XDev)",
        
        # LLM nodes
        "LMStudioChat": "LM Studio Chat (XDev)",
        "LLMPromptFramework": "LLM Prompt Framework (XDev)",
        "LLMContextualBuilder": "LLM Contextual Builder (XDev)",
        "LLMDevFramework": "LLM Dev Framework (XDev)",
        "LLMSDXLExpertWriter": "LLM SDXL Expert Writer (XDev)",
        "LLMSDXLPhotoEnhancer": "LLM SDXL Photo Enhancer (XDev)",
        
        # Math nodes
        "MathBasic": "Math Basic (XDev)",
        
        # Model nodes
        "SDXLModelMixer": "SDXL Model Mixer (XDev)",
        
        # Prompt nodes
        "PromptCombiner": "Prompt Combiner (XDev)",
        "PromptWeighter": "Prompt Weighter (XDev)",
        "PromptCleaner": "Prompt Cleaner (XDev)",
        "PromptAnalyzer": "Prompt Analyzer (XDev)",
        "PromptRandomizer": "Prompt Randomizer (XDev)",
        "PersonBuilder": "Person Builder (XDev)",
        "StyleBuilder": "Style Builder (XDev)",
        "PromptMatrix": "Prompt Matrix (XDev)",
        "PromptInterpolator": "Prompt Interpolator (XDev)",
        "PromptScheduler": "Prompt Scheduler (XDev)",
        "PromptAttention": "Prompt Attention (XDev)",
        "PromptChainOfThought": "Prompt Chain Of Thought (XDev)",
        "PromptFewShot": "Prompt Few Shot (XDev)",
        "LLMPersonBuilder": "LLM Person Builder (XDev)",
        "LLMStyleBuilder": "LLM Style Builder (XDev)",
        
        # Sampling nodes
        "AdvancedKSampler": "Advanced K-Sampler (XDev)",
        "VariantSelector": "Variant Selector (XDev)",
        
        # Text nodes
        "AppendSuffix": "Append Suffix (XDev)",
        
        # VAE nodes
        "VAERoundTrip": "VAE Round Trip (XDev)",
        "StructuredMockImage": "Structured Mock Image (XDev)",
    }
    
    nodes_dir = Path("xdev_nodes/nodes")
    python_files = [f for f in nodes_dir.glob("*.py") if f.name != "__init__.py"]
    
    total_changes = 0
    
    for file_path in python_files:
        print(f"\n🔧 ADDING DISPLAY NAMES: {file_path.name}")
        print("-" * 50)
        
        backup_file(file_path)
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        file_changes = 0
        
        # Find all ComfyUI node classes in this file
        class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?:'
        classes = re.findall(class_pattern, content)
        
        for class_name in classes:
            if class_name in DISPLAY_NAME_MAPPINGS:
                # Check if class already has DISPLAY_NAME
                class_section_pattern = rf'class\s+{re.escape(class_name)}.*?(?=class\s+|\Z)'
                class_section_match = re.search(class_section_pattern, content, re.DOTALL)
                
                if class_section_match:
                    class_section = class_section_match.group(0)
                    
                    # Check if DISPLAY_NAME already exists
                    if 'DISPLAY_NAME' not in class_section:
                        # Find the class definition line and add DISPLAY_NAME after it
                        class_def_pattern = rf'(class\s+{re.escape(class_name)}\s*(?:\([^)]*\))?:\s*\n)'
                        display_name = DISPLAY_NAME_MAPPINGS[class_name]
                        replacement = rf'\1    DISPLAY_NAME = "{display_name}"\n'
                        
                        if re.search(class_def_pattern, content):
                            content = re.sub(class_def_pattern, replacement, content)
                            print(f"    ✅ Added DISPLAY_NAME to {class_name}")
                            file_changes += 1
                            total_changes += 1
        
        # Write file if changes were made
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            processed_files.append(file_path.name)
            print(f"    📝 File updated with {file_changes} changes")
        else:
            print(f"    ℹ️ No changes needed")
    
    return total_changes

def main():
    print("🚀 PHASE 1 FINAL COMPLETION")
    print("=" * 60)
    
    # Fix remaining string category
    string_fixed = fix_remaining_string_category()
    
    # Add all DISPLAY_NAME attributes
    display_names_added = add_display_names()
    
    print(f"\n📊 COMPLETION SUMMARY:")
    print("=" * 60)
    print(f"📁 Files processed: {len(processed_files)}")
    print(f"🔧 String categories fixed: {1 if string_fixed else 0}")
    print(f"🏷️ Display names added: {display_names_added}")
    print(f"📝 Total changes: {display_names_added + (1 if string_fixed else 0)}")
    
    if processed_files:
        print(f"\n📋 Modified files:")
        for file in processed_files:
            print(f"  📄 {file}")
    
    print(f"\n✅ PHASE 1 COMPLETION READY FOR VALIDATION!")
    print("Run 'python validate_phase1.py' to verify 100% completion")

if __name__ == "__main__":
    main()