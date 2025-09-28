"""
Test Phase 1 Implementation - Auto-registration system
"""

import sys
sys.path.append('..')

try:
    from xdev_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    from xdev_nodes.categories import NodeCategories
    
    print("🚀 PHASE 1 STATUS CHECK")
    print("=" * 50)
    
    # Test auto-registration
    print(f"✅ Auto-registration successful!")
    print(f"📊 Registered {len(NODE_CLASS_MAPPINGS)} nodes")
    print(f"📋 Display names: {len(NODE_DISPLAY_NAME_MAPPINGS)} entries")
    
    # Test categories
    print(f"\n🏷️ CATEGORY SYSTEM:")
    print(f"✅ NodeCategories class available")
    print(f"📚 Available categories: {len(NodeCategories.get_all_categories())}")
    
    # Sample nodes
    print(f"\n🔍 SAMPLE REGISTERED NODES:")
    for i, (node_id, display_name) in enumerate(NODE_DISPLAY_NAME_MAPPINGS.items()):
        print(f"  {node_id} → {display_name}")
        if i >= 4:
            print(f"  ... and {len(NODE_DISPLAY_NAME_MAPPINGS)-5} more")
            break
    
    # Test specific functionality
    print(f"\n🧪 FUNCTIONALITY TESTS:")
    
    # Check if categories are being used
    category_usage = {}
    for node_id, node_class in NODE_CLASS_MAPPINGS.items():
        category = getattr(node_class, 'CATEGORY', 'Unknown')
        category_usage[category] = category_usage.get(category, 0) + 1
    
    print(f"📈 Category usage:")
    for category, count in sorted(category_usage.items()):
        print(f"  {category}: {count} nodes")
    
    # Check for NodeCategories usage
    using_constants = sum(1 for cat in category_usage.keys() 
                         if not cat.startswith('"') and cat in NodeCategories.get_all_categories())
    
    print(f"\n📊 PHASE 1 COMPLETION:")
    print(f"  ✅ Auto-registration: IMPLEMENTED")
    print(f"  ✅ Centralized categories: IMPLEMENTED")
    print(f"  📈 Nodes using category constants: {using_constants}/{len(NODE_CLASS_MAPPINGS)}")
    
    if using_constants > len(NODE_CLASS_MAPPINGS) * 0.8:
        print(f"  🎉 PHASE 1: COMPLETE!")
    else:
        print(f"  ⚠️ PHASE 1: PARTIALLY COMPLETE (need to migrate remaining categories)")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("⚠️ Phase 1 not fully implemented yet")
except Exception as e:
    print(f"❌ Error: {e}")