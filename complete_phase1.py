"""
Phase 1 Completion Script - Automated category migration
Converts all remaining string categories to NodeCategories constants
"""

import re
from pathlib import Path

def complete_phase1_migration():
    """Complete the Phase 1 category migration"""
    
    # Category mapping from string literals to NodeCategories constants
    CATEGORY_MAPPINGS = {
        '"XDev/Prompt/Cleaning"': 'NodeCategories.PROMPT_CLEANING',
        '"XDev/Prompt/Analysis"': 'NodeCategories.PROMPT_ANALYSIS', 
        '"XDev/Prompt/Randomization"': 'NodeCategories.PROMPT_RANDOMIZATION',
        '"XDev/Prompt/Templates"': 'NodeCategories.PROMPT_TEMPLATES',
        '"XDev/LLM/Character"': 'NodeCategories.LLM_CHARACTER',
        '"XDev/LLM/Style"': 'NodeCategories.LLM_STYLE',
        '"XDev/LLM/PromptTools"': 'NodeCategories.LLM_PROMPT_TOOLS',
        '"XDev/LLM/Development"': 'NodeCategories.LLM_DEVELOPMENT',
        '"XDev/LLM/SDXL"': 'NodeCategories.LLM_SDXL',
        '"XDev/Model/Advanced"': 'NodeCategories.MODEL_ADVANCED',
        '"XDev/Sampling/Advanced"': 'NodeCategories.SAMPLING_ADVANCED',
        '"XDev/Face Processing/Advanced"': 'NodeCategories.FACE_PROCESSING_ADVANCED',
        '"XDev/Face Processing/Batch"': 'NodeCategories.FACE_PROCESSING_BATCH',
        '"XDev/Face Processing/Analysis"': 'NodeCategories.FACE_PROCESSING_ANALYSIS',
        '"XDev/InsightFace/Loaders"': 'NodeCategories.INSIGHTFACE_LOADERS',
        '"XDev/InsightFace/Processing"': 'NodeCategories.INSIGHTFACE_PROCESSING',
        '"XDev/InsightFace/FaceSwap"': 'NodeCategories.INSIGHTFACE_FACESWAP',
    }
    
    # Display name mappings for nodes that need them
    DISPLAY_NAME_MAPPINGS = {
        'PromptCleaner': 'Prompt Cleaner (XDev)',
        'PromptAnalyzer': 'Prompt Analyzer (XDev)',
        'PromptRandomizer': 'Prompt Randomizer (XDev)',
        'PersonBuilder': 'Person Builder (XDev)',
        'StyleBuilder': 'Style Builder (XDev)',
        'PromptMatrix': 'Prompt Matrix (XDev)',
        'PromptInterpolator': 'Prompt Interpolator (XDev)',
        'PromptScheduler': 'Prompt Scheduler (XDev)',
        'PromptAttention': 'Prompt Attention (XDev)',
        'PromptChainOfThought': 'Prompt Chain-of-Thought (XDev)',
        'PromptFewShot': 'Prompt Few-Shot (XDev)',
        'LLMPersonBuilder': 'LLM Person Builder (XDev)',
        'LLMStyleBuilder': 'LLM Style Builder (XDev)',
        'LLMPromptAssistant': 'LLM Prompt Assistant (XDev)',
        'LLMContextualBuilder': 'LLM Contextual Builder (XDev)',
        'LLMDevFramework': 'LLM-DEV Framework (XDev)',
        'LLMSDXLPhotoEnhancer': 'LLM SDXL Photo Enhancer (XDev)',
        'LLMSDXLExpertWriter': 'LLM SDXL Expert Writer (XDev)',
        'SDXLModelMixer': 'SDXL Model Mixer (XDev)',
        'AdvancedKSampler': 'Advanced KSampler (XDev)',
        'VariantSelector': 'Variant Selector (XDev)',
    }
    
    nodes_dir = Path("xdev_nodes/nodes")
    updated_files = []
    
    print("🔧 COMPLETING PHASE 1 MIGRATION")
    print("=" * 50)
    
    for py_file in nodes_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
            
        print(f"\n📁 Processing: {py_file.name}")
        
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Replace category string literals with constants
        for old_cat, new_cat in CATEGORY_MAPPINGS.items():
            if f'CATEGORY = {old_cat}' in content:
                content = content.replace(f'CATEGORY = {old_cat}', f'CATEGORY = {new_cat}')
                changes_made += 1
                print(f"  ✅ Updated category: {old_cat} → {new_cat}")
        
        # Add DISPLAY_NAME where missing
        for class_name, display_name in DISPLAY_NAME_MAPPINGS.items():
            # Look for class definitions
            class_pattern = rf'class {class_name}[\s\S]*?CATEGORY = [^\n]+\n'
            matches = re.finditer(class_pattern, content)
            
            for match in matches:
                class_block = match.group(0)
                if 'DISPLAY_NAME' not in class_block:
                    # Insert DISPLAY_NAME after CATEGORY
                    old_block = class_block
                    new_block = class_block.rstrip('\n') + f'\n    DISPLAY_NAME = "{display_name}"\n'
                    content = content.replace(old_block, new_block)
                    changes_made += 1
                    print(f"  ✅ Added DISPLAY_NAME for {class_name}")
        
        # Write back if changes were made
        if changes_made > 0:
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_files.append((py_file.name, changes_made))
            print(f"  📝 Saved {changes_made} changes")
        else:
            print(f"  ℹ️ No changes needed")
    
    print(f"\n📊 PHASE 1 MIGRATION COMPLETE!")
    print(f"✅ Updated {len(updated_files)} files:")
    for filename, changes in updated_files:
        print(f"  {filename}: {changes} changes")
    
    return updated_files

if __name__ == "__main__":
    complete_phase1_migration()