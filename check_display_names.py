#!/usr/bin/env python3
"""
Quick DISPLAY_NAME Coverage Check
Count actual DISPLAY_NAME coverage in all node files
"""

import os
import re
from pathlib import Path

def count_display_names():
    """Count DISPLAY_NAME coverage in all node files"""
    
    nodes_dir = Path("xdev_nodes/nodes")
    python_files = [f for f in nodes_dir.glob("*.py") if f.name != "__init__.py"]
    
    total_classes = 0
    classes_with_display_name = 0
    
    print("🔍 DISPLAY_NAME COVERAGE CHECK")
    print("=" * 50)
    
    for file_path in python_files:
        content = file_path.read_text(encoding='utf-8')
        
        # Find all ComfyUI node classes
        class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?:'
        classes = re.findall(class_pattern, content)
        
        # Filter for ComfyUI nodes (classes with INPUT_TYPES, RETURN_TYPES, etc.)
        comfyui_classes = []
        for class_name in classes:
            # Look for class content that suggests this is a ComfyUI node
            class_section_pattern = rf'class\s+{re.escape(class_name)}.*?(?=class\s+|\Z)'
            class_section_match = re.search(class_section_pattern, content, re.DOTALL)
            
            if class_section_match:
                class_section = class_section_match.group(0)
                # Check if it has ComfyUI node characteristics
                if ('INPUT_TYPES' in class_section or 
                    'RETURN_TYPES' in class_section or
                    'FUNCTION' in class_section or
                    'CATEGORY' in class_section):
                    comfyui_classes.append(class_name)
        
        # Count DISPLAY_NAME attributes in this file
        display_name_matches = re.findall(r'DISPLAY_NAME\s*=\s*"([^"]+)"', content)
        
        print(f"\n📄 {file_path.name}:")
        print(f"  🔸 ComfyUI classes: {len(comfyui_classes)}")
        print(f"  🏷️ DISPLAY_NAME attributes: {len(display_name_matches)}")
        
        for class_name in comfyui_classes:
            total_classes += 1
            
            # Check if this specific class has DISPLAY_NAME
            class_section_pattern = rf'class\s+{re.escape(class_name)}.*?(?=class\s+|\Z)'
            class_section_match = re.search(class_section_pattern, content, re.DOTALL)
            
            if class_section_match:
                class_section = class_section_match.group(0)
                if 'DISPLAY_NAME' in class_section:
                    classes_with_display_name += 1
                    display_match = re.search(r'DISPLAY_NAME\s*=\s*"([^"]+)"', class_section)
                    if display_match:
                        print(f"    ✅ {class_name}: {display_match.group(1)}")
                    else:
                        print(f"    ✅ {class_name}: DISPLAY_NAME found")
                else:
                    print(f"    ⚠️ {class_name}: Missing DISPLAY_NAME")
    
    print(f"\n📊 SUMMARY:")
    print("=" * 50)
    print(f"📂 Files scanned: {len(python_files)}")
    print(f"🔸 Total ComfyUI classes: {total_classes}")
    print(f"🏷️ Classes with DISPLAY_NAME: {classes_with_display_name}")
    
    if total_classes > 0:
        coverage_percent = (classes_with_display_name / total_classes) * 100
        print(f"📈 Coverage: {coverage_percent:.1f}%")
        
        if coverage_percent >= 95:
            print(f"✅ PHASE 1 DISPLAY_NAME: COMPLETE!")
        elif coverage_percent >= 80:
            print(f"🔄 PHASE 1 DISPLAY_NAME: Nearly complete")
        else:
            print(f"⚠️ PHASE 1 DISPLAY_NAME: Needs more work")
    
    return total_classes, classes_with_display_name

if __name__ == "__main__":
    count_display_names()