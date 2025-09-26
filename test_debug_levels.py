#!/usr/bin/env python3
"""
Test script demonstrating XDev Nodes startup debugging configuration
"""

def test_debug_levels():
    """Test different debug levels"""
    
    print("🧪 Testing XDev Nodes Debug Levels")
    print("=" * 50)
    
    # Test with minimal debugging
    print("\n1️⃣ Testing MINIMAL debugging (ERROR only)...")
    import sys
    
    # Modify debug config temporarily
    import xdev_nodes.debug_config as config
    original_level = config.DEBUG_LEVEL
    original_summary = config.DEBUG_SUMMARY
    
    # Set minimal debug
    config.DEBUG_LEVEL = "ERROR"
    config.DEBUG_SUMMARY = False
    
    # Reload (simulation - in practice you'd restart ComfyUI)
    print("   (Set DEBUG_LEVEL='ERROR', DEBUG_SUMMARY=False)")
    print("   In ComfyUI, only errors would be shown during startup")
    
    # Test with detailed debugging  
    print("\n2️⃣ Testing DETAILED debugging (DEBUG level)...")
    config.DEBUG_LEVEL = "DEBUG"
    config.DEBUG_SUMMARY = True
    config.DEBUG_TIMING = True
    
    print("   (Set DEBUG_LEVEL='DEBUG', DEBUG_TIMING=True)")
    print("   In ComfyUI, you'd see detailed import info with timing")
    
    # Test with trace debugging
    print("\n3️⃣ Testing TRACE debugging (maximum detail)...")
    config.DEBUG_LEVEL = "TRACE" 
    config.DEBUG_TRACEBACK = True
    
    print("   (Set DEBUG_LEVEL='TRACE', DEBUG_TRACEBACK=True)")
    print("   In ComfyUI, you'd see maximum detail including file traces")
    
    # Restore original settings
    config.DEBUG_LEVEL = original_level
    config.DEBUG_SUMMARY = original_summary
    
    print(f"\n✅ Debug configuration restored to DEBUG_LEVEL='{original_level}'")
    
    print("\n🔧 Configuration Guide:")
    print("   • Edit xdev_nodes/debug_config.py to customize startup output")
    print("   • Set DEBUG_ENABLED=False to disable all debugging")
    print("   • Use DEBUG_LEVEL='ERROR' for production (minimal output)")
    print("   • Use DEBUG_LEVEL='DEBUG' for development (detailed output)")
    print("   • Use DEBUG_LEVEL='TRACE' for troubleshooting (maximum output)")
    
    print("\n📋 Available Debug Settings:")
    print("   • DEBUG_IMPORTS: Show import success/failure")
    print("   • DEBUG_WEB: Show web asset scanning")
    print("   • DEBUG_VALIDATION: Show node validation details")
    print("   • DEBUG_SUMMARY: Show startup summary")
    print("   • DEBUG_TIMING: Show timing information")
    print("   • DEBUG_TRACEBACK: Show full error tracebacks")

if __name__ == "__main__":
    test_debug_levels()