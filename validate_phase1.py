"""
Phase 1 Validation Report - Auto-registration + Categories
Comprehensive validation of the completed Phase 1 refactoring.
"""

import re
from pathlib import Path
from collections import defaultdict

def validate_phase1_completion():
    """Validate Phase 1 implementation is complete and working"""
    
    print("🎯 PHASE 1 VALIDATION REPORT")
    print("=" * 60)
    
    nodes_dir = Path("xdev_nodes/nodes")
    results = {
        'total_files': 0,
        'has_categories_import': 0,
        'uses_constants': 0,
        'has_display_name': 0,
        'string_categories': 0,
        'node_classes_found': 0
    }
    
    category_usage = defaultdict(int)
    string_categories = []
    missing_display_names = []
    node_classes = []
    
    print("📂 SCANNING NODE FILES:")
    print("-" * 40)
    
    for py_file in nodes_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
            
        results['total_files'] += 1
        print(f"\n📄 {py_file.name}")
        
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for categories import
        if 'from ..categories import NodeCategories' in content:
            results['has_categories_import'] += 1
            print("  ✅ Has NodeCategories import")
        else:
            print("  ❌ Missing NodeCategories import")
        
        # Use a simpler approach - find all CATEGORY declarations
        category_matches = re.findall(r'class (\w+)[\s\S]*?CATEGORY = ([^\n]+)', content, re.MULTILINE)
        
        for class_name, category in category_matches:
            node_classes.append(class_name)
            results['node_classes_found'] += 1
            print(f"    🔸 Node class: {class_name}")
            
            # Check category usage
            category = category.strip()
            category_usage[category] += 1
            
            if category.startswith('NodeCategories.'):
                results['uses_constants'] += 1
                print(f"      ✅ Uses constant: {category}")
            elif category.startswith('"'):
                results['string_categories'] += 1
                string_categories.append(f"{py_file.name}: {class_name} -> {category}")
                print(f"      ⚠️ Uses string: {category}")
            
            # Check for DISPLAY_NAME in this class
            class_content_match = re.search(rf'class {class_name}[\s\S]*?(?=class|\Z)', content)
            if class_content_match:
                class_content = class_content_match.group(0)
                if 'DISPLAY_NAME = ' in class_content:
                    results['has_display_name'] += 1
                    display_match = re.search(r'DISPLAY_NAME = "([^"]+)"', class_content)
                    if display_match:
                        print(f"      ✅ Display name: {display_match.group(1)}")
                else:
                    missing_display_names.append(f"{py_file.name}: {class_name}")
                    print(f"      ⚠️ Missing DISPLAY_NAME")
    
    # Print comprehensive results
    print(f"\n📊 PHASE 1 VALIDATION RESULTS:")
    print("=" * 60)
    
    print(f"📁 Files processed: {results['total_files']}")
    print(f"🔗 Files with NodeCategories import: {results['has_categories_import']}/{results['total_files']}")
    print(f"🏷️ Node classes found: {results['node_classes_found']}")
    print(f"✅ Using category constants: {results['uses_constants']}")
    print(f"❌ Using string categories: {results['string_categories']}")
    print(f"🏆 Has DISPLAY_NAME: {results['has_display_name']}")
    
    # Category analysis
    print(f"\n📈 CATEGORY USAGE ANALYSIS:")
    print("-" * 40)
    
    constants_used = sum(1 for cat in category_usage.keys() if cat.startswith('NodeCategories.'))
    strings_used = sum(1 for cat in category_usage.keys() if cat.startswith('"'))
    
    print(f"Constants: {constants_used} categories")
    print(f"Strings: {strings_used} categories")
    
    for category, count in sorted(category_usage.items()):
        status = "✅" if category.startswith('NodeCategories.') else "❌"
        print(f"  {status} {category}: {count} nodes")
    
    # Issues report
    if string_categories:
        print(f"\n⚠️ REMAINING STRING CATEGORIES:")
        print("-" * 40)
        for issue in string_categories:
            print(f"  {issue}")
    
    if missing_display_names:
        print(f"\n⚠️ MISSING DISPLAY NAMES:")
        print("-" * 40)
        for issue in missing_display_names:
            print(f"  {issue}")
    
    # Success metrics
    print(f"\n🎯 PHASE 1 COMPLETION METRICS:")
    print("=" * 60)
    
    category_completion = (results['uses_constants'] / max(results['node_classes_found'], 1)) * 100
    display_completion = (results['has_display_name'] / max(results['node_classes_found'], 1)) * 100
    import_completion = (results['has_categories_import'] / max(results['total_files'], 1)) * 100
    
    print(f"📊 Category constants usage: {category_completion:.1f}%")
    print(f"🏷️ Display name coverage: {display_completion:.1f}%")
    print(f"🔗 Import coverage: {import_completion:.1f}%")
    
    overall_score = (category_completion + display_completion + import_completion) / 3
    print(f"🎯 Overall Phase 1 completion: {overall_score:.1f}%")
    
    if overall_score >= 95:
        print("\n🎉 PHASE 1: COMPLETE!")
        print("✅ Ready for Phase 2 (Module Splitting)")
    elif overall_score >= 80:
        print("\n⚠️ PHASE 1: MOSTLY COMPLETE")
        print("📋 Address remaining issues above")
    else:
        print("\n❌ PHASE 1: NEEDS MORE WORK")
        print("📋 Significant issues need to be resolved")
    
    return {
        'score': overall_score,
        'results': results,
        'issues': {
            'string_categories': string_categories,
            'missing_display_names': missing_display_names
        }
    }

if __name__ == "__main__":
    validate_phase1_completion()