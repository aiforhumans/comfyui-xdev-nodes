#!/usr/bin/env python3
"""
Final DISPLAY_NAME Addition Script
Add DISPLAY_NAME to the remaining 10 classes that need them
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

def add_final_display_names():
    """Add DISPLAY_NAME to the remaining classes based on accurate detection"""
    
    # Missing DISPLAY_NAME classes from accurate check
    missing_mappings = {
        "faceswap_professional.py": [
            ("XDEV_FaceExtractEmbed", "Face Extract Embed (XDev)")
        ],
        "face_swap.py": [
            ("XDEV_FaceSwapBatch", "Face Swap Batch (XDev)")
        ],
        "image.py": [
            ("ImageResize", "Image Resize (XDev)"),
            ("ImageCrop", "Image Crop (XDev)"),
            ("ImageRotate", "Image Rotate (XDev)"),
            ("ImageBlend", "Image Blend (XDev)"),
            ("ImageSplit", "Image Split (XDev)"),
            ("ImageTile", "Image Tile (XDev)")
        ],
        "insightface_loaders.py": [
            ("XDEV_InsightFaceModelLoader", "InsightFace Model Loader (XDev)")
        ],
        "text.py": [
            ("TextCase", "Text Case (XDev)")
        ]
    }
    
    nodes_dir = Path("xdev_nodes/nodes")
    total_changes = 0
    files_processed = []
    
    for filename, class_mappings in missing_mappings.items():
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
            class_pattern = rf'(class\s+{re.escape(class_name)}\s*(?:\([^)]*\))?:\s*\n)'
            match = re.search(class_pattern, content)
            
            if match:
                # Check if this class already has DISPLAY_NAME
                class_start_pos = match.end()
                
                # Look ahead to find the next class or end of file
                next_class_pattern = r'\nclass\s+[A-Za-z_][A-Za-z0-9_]*\s*(?:\([^)]*\))?:'
                next_class_match = re.search(next_class_pattern, content[class_start_pos:])
                
                if next_class_match:
                    class_body = content[class_start_pos:class_start_pos + next_class_match.start()]
                else:
                    class_body = content[class_start_pos:]
                
                # Check if DISPLAY_NAME already exists
                if 'DISPLAY_NAME' not in class_body:
                    # Add DISPLAY_NAME right after the class definition
                    display_name_line = f'    DISPLAY_NAME = "{display_name}"\n'
                    replacement = match.group(1) + display_name_line
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
    print("🚀 FINAL DISPLAY_NAME COMPLETION - 10 REMAINING CLASSES")
    print("=" * 60)
    
    changes, files = add_final_display_names()
    
    print(f"\n📊 COMPLETION SUMMARY:")
    print("=" * 60)
    print(f"📁 Files processed: {len(files)}")
    print(f"🏷️ Display names added: {changes}")
    
    if files:
        print(f"\n📋 Modified files:")
        for file in files:
            print(f"  📄 {file}")
    
    print(f"\n✅ FINAL DISPLAY_NAME COMPLETION FINISHED!")
    print("Run 'python check_display_names.py' to verify 100% completion")

if __name__ == "__main__":
    main()