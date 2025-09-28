#!/usr/bin/env python3
"""
Test Auto-Registration System
Verify the registry.py auto-discovery works correctly
"""

import sys
from pathlib import Path

# Add the xdev_nodes directory to path so we can import
sys.path.insert(0, str(Path("xdev_nodes").absolute()))

def test_auto_registration():
    """Test the auto-registration system functionality"""
    
    print("🧪 TESTING AUTO-REGISTRATION SYSTEM")
    print("=" * 60)
    
    try:
        # Import the registry system
        from registry import NodeRegistry
        
        print("✅ Successfully imported NodeRegistry")
        
        # Test node discovery
        print("\n🔍 DISCOVERING NODES:")
        print("-" * 40)
        
        registry = NodeRegistry()
        nodes_dir = Path("xdev_nodes/nodes")
        registry.discover_nodes(nodes_dir)
        node_mappings, display_mappings = registry.get_mappings()
        
        print(f"📊 Discovery Results:")
        print(f"  🔸 Node classes discovered: {len(node_mappings)}")
        print(f"  🏷️ Display names discovered: {len(display_mappings)}")
        
        # Show some examples
        print(f"\n📋 Sample Node Mappings:")
        for i, (key, cls) in enumerate(list(node_mappings.items())[:5]):
            print(f"  {i+1}. {key} -> {cls.__name__}")
        
        print(f"\n🏷️ Sample Display Names:")
        for i, (key, name) in enumerate(list(display_mappings.items())[:5]):
            print(f"  {i+1}. {key} -> {name}")
        
        # Test the __init__.py integration
        print(f"\n🔗 TESTING MODULE INTEGRATION:")
        print("-" * 40)
        
        try:
            # Import the main module
            import xdev_nodes
            
            # Check if NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS exist
            if hasattr(xdev_nodes, 'NODE_CLASS_MAPPINGS'):
                mappings = xdev_nodes.NODE_CLASS_MAPPINGS
                print(f"✅ NODE_CLASS_MAPPINGS found with {len(mappings)} entries")
            else:
                print(f"⚠️ NODE_CLASS_MAPPINGS not found")
            
            if hasattr(xdev_nodes, 'NODE_DISPLAY_NAME_MAPPINGS'):
                display_mappings = xdev_nodes.NODE_DISPLAY_NAME_MAPPINGS
                print(f"✅ NODE_DISPLAY_NAME_MAPPINGS found with {len(display_mappings)} entries")
            else:
                print(f"⚠️ NODE_DISPLAY_NAME_MAPPINGS not found")
                
        except Exception as e:
            print(f"⚠️ Error testing module integration: {e}")
        
        # Validate node structure
        print(f"\n🔍 VALIDATING NODE STRUCTURE:")
        print("-" * 40)
        
        valid_nodes = 0
        invalid_nodes = 0
        
        for class_name, node_class in node_mappings.items():
            try:
                # Check for essential ComfyUI node attributes
                has_input_types = hasattr(node_class, 'INPUT_TYPES')
                has_return_types = hasattr(node_class, 'RETURN_TYPES')
                has_function = hasattr(node_class, 'FUNCTION')
                has_category = hasattr(node_class, 'CATEGORY')
                
                if has_input_types and has_return_types and has_function and has_category:
                    valid_nodes += 1
                else:
                    invalid_nodes += 1
                    missing = []
                    if not has_input_types: missing.append("INPUT_TYPES")
                    if not has_return_types: missing.append("RETURN_TYPES")
                    if not has_function: missing.append("FUNCTION")
                    if not has_category: missing.append("CATEGORY")
                    print(f"  ⚠️ {class_name} missing: {', '.join(missing)}")
                    
            except Exception as e:
                invalid_nodes += 1
                print(f"  ❌ Error validating {class_name}: {e}")
        
        print(f"\n📈 VALIDATION RESULTS:")
        print(f"  ✅ Valid nodes: {valid_nodes}")
        print(f"  ⚠️ Invalid nodes: {invalid_nodes}")
        print(f"  📊 Success rate: {(valid_nodes/(valid_nodes+invalid_nodes)*100):.1f}%")
        
        # Overall assessment
        print(f"\n🎯 PHASE 1 AUTO-REGISTRATION ASSESSMENT:")
        print("=" * 60)
        
        if len(node_mappings) >= 45 and valid_nodes >= 45:
            print("✅ AUTO-REGISTRATION SYSTEM: FULLY OPERATIONAL!")
            print("🚀 Ready for Phase 2 implementation")
        elif len(node_mappings) >= 40:
            print("🔄 AUTO-REGISTRATION SYSTEM: Mostly operational")
            print("🔧 Minor refinements may be needed")
        else:
            print("⚠️ AUTO-REGISTRATION SYSTEM: Needs attention")
            print("🛠️ Significant issues detected")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing auto-registration: {e}")
        print(f"📋 Exception details: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    test_auto_registration()