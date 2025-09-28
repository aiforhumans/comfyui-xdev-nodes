#!/usr/bin/env python3
"""
Phase 1 Final DISPLAY_NAME Script
Add remaining DISPLAY_NAME attributes to complete Phase 1
"""

import os
import re
from pathlib import Path

def backup_file(file_path):
    """Create backup of file before modification"""
    backup_dir = Path("backups")
    backup_path = backup_dir / f"{file_path.name}.backup"
    backup_dir.mkdir(exist_ok=True)
    
    if not backup_path.exists():
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"    📁 Backup created: {backup_path}")
    return backup_path

def add_remaining_display_names():
    """Add missing DISPLAY_NAME attributes based on validation output"""
    
    # Files and their missing DISPLAY_NAME classes
    missing_display_names = {
        "dev_nodes.py": [
            ("OutputDev", "Output Dev (XDev)"),
            ("InputDev", "Input Dev (XDev)")
        ],
        "insightface_faceswap.py": [
            ("XDEV_InsightFaceFaceSwap", "InsightFace Face Swap (XDev)")
        ],
        "insightface_loaders.py": [
            ("XDEV_InsightFaceProcessor", "InsightFace Processor (XDev)")
        ],
        "llm_integration.py": [
            ("LLMContextualBuilder", "LLM Contextual Builder (XDev)"),
            ("LLMDevFramework", "LLM Dev Framework (XDev)"),
            ("LLMSDXLExpertWriter", "LLM SDXL Expert Writer (XDev)"),
            ("LLMSDXLPhotoEnhancer", "LLM SDXL Photo Enhancer (XDev)")
        ],
        "model_tools.py": [
            ("SDXLModelMixer", "SDXL Model Mixer (XDev)")
        ],
        "prompt.py": [
            ("PromptWeighter", "Prompt Weighter (XDev)"),
            ("PromptCleaner", "Prompt Cleaner (XDev)"),
            ("PromptAnalyzer", "Prompt Analyzer (XDev)"),
            ("PromptRandomizer", "Prompt Randomizer (XDev)"),
            ("PersonBuilder", "Person Builder (XDev)"),
            ("StyleBuilder", "Style Builder (XDev)"),
            ("PromptMatrix", "Prompt Matrix (XDev)"),
            ("PromptInterpolator", "Prompt Interpolator (XDev)"),
            ("PromptScheduler", "Prompt Scheduler (XDev)"),
            ("PromptAttention", "Prompt Attention (XDev)"),
            ("PromptChainOfThought", "Prompt Chain Of Thought (XDev)"),
            ("PromptFewShot", "Prompt Few Shot (XDev)"),
            ("LLMPersonBuilder", "LLM Person Builder (XDev)"),
            ("LLMStyleBuilder", "LLM Style Builder (XDev)")
        ],
        "sampling_advanced.py": [
            ("AdvancedKSampler", "Advanced K-Sampler (XDev)"),
            ("VariantSelector", "Variant Selector (XDev)")
        ],
        "vae_tools.py": [
            ("VAERoundTrip", "VAE Round Trip (XDev)")
        ]
    }
    
    nodes_dir = Path("xdev_nodes/nodes")
    total_changes = 0
    files_processed = []
    
    for filename, class_mappings in missing_display_names.items():
        file_path = nodes_dir / filename
        
        if not file_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
            
        print(f"\n🔧 PROCESSING: {filename}")
        print("-" * 50)
        
        backup_file(file_path)
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        file_changes = 0
        
        for class_name, display_name in class_mappings:
            # Look for the class definition
            class_pattern = rf'class\s+{re.escape(class_name)}\s*(?:\([^)]*\))?:\s*\n'
            match = re.search(class_pattern, content)
            
            if match:
                # Check if DISPLAY_NAME already exists in the class
                class_start = match.end()
                
                # Find the next class or end of file to define the class body
                next_class_pattern = r'\nclass\s+[A-Za-z_][A-Za-z0-9_]*\s*(?:\([^)]*\))?:'
                next_class_match = re.search(next_class_pattern, content[class_start:])
                
                if next_class_match:
                    class_body = content[class_start:class_start + next_class_match.start()]
                else:
                    class_body = content[class_start:]
                
                # Check if DISPLAY_NAME already exists
                if 'DISPLAY_NAME' not in class_body:
                    # Add DISPLAY_NAME right after the class definition
                    display_name_line = f'    DISPLAY_NAME = "{display_name}"\n'
                    replacement = match.group(0) + display_name_line
                    content = content.replace(match.group(0), replacement, 1)
                    
                    print(f"    ✅ Added DISPLAY_NAME to {class_name}")
                    file_changes += 1
                    total_changes += 1
                else:
                    print(f"    ℹ️ {class_name} already has DISPLAY_NAME")
            else:
                print(f"    ⚠️ Class {class_name} not found")
        
        # Write file if changes were made
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            files_processed.append(filename)
            print(f"    📝 File updated with {file_changes} changes")
        else:
            print(f"    ℹ️ No changes needed")
    
    return total_changes, files_processed

def main():
    print("🚀 PHASE 1 FINAL DISPLAY_NAME COMPLETION")
    print("=" * 60)
    
    changes, files = add_remaining_display_names()
    
    print(f"\n📊 COMPLETION SUMMARY:")
    print("=" * 60)
    print(f"📁 Files processed: {len(files)}")
    print(f"🏷️ Display names added: {changes}")
    
    if files:
        print(f"\n📋 Modified files:")
        for file in files:
            print(f"  📄 {file}")
    
    print(f"\n✅ PHASE 1 DISPLAY_NAME COMPLETION FINISHED!")
    print("Run 'python validate_phase1.py' to verify 100% completion")

if __name__ == "__main__":
    main()