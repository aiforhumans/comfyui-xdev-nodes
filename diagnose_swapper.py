#!/usr/bin/env python3
"""
InsightFace Swapper Diagnostic
Check what's available in InsightFace for face swapping
"""

def test_insightface_swapper():
    print("🔍 Testing InsightFace Swapper availability...")
    
    try:
        import insightface
        print(f"✅ InsightFace version: {insightface.__version__}")
        
        # Test FaceAnalysis (this works)
        from insightface.app import FaceAnalysis
        print("✅ FaceAnalysis imported successfully")
        
        # Test FaceSwapper (this might be the issue)
        try:
            from insightface.app import FaceSwapper
            print("✅ FaceSwapper imported successfully")
            
            # Try to create a swapper instance
            try:
                swapper = FaceSwapper(name='inswapper_128.onnx')
                print("✅ FaceSwapper instance created successfully")
                return True
            except Exception as e:
                print(f"❌ FaceSwapper creation failed: {e}")
                print("   This might indicate missing swapper model files")
                return False
                
        except ImportError as e:
            print(f"❌ FaceSwapper import failed: {e}")
            print("   FaceSwapper might not be available in this InsightFace version")
            return False
            
    except Exception as e:
        print(f"❌ InsightFace test failed: {e}")
        return False

def check_alternative_swapping():
    print("\n🔧 Checking alternative face swapping approaches...")
    
    try:
        import insightface
        from insightface.app import FaceAnalysis
        
        # Create analysis app
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        print("✅ FaceAnalysis app created for swapping")
        
        # Check available methods
        methods = [method for method in dir(app) if not method.startswith('_')]
        print(f"📝 Available methods: {methods}")
        
        # Look for swapping-related methods
        swap_methods = [m for m in methods if 'swap' in m.lower() or 'get' in m.lower()]
        print(f"🔄 Potential swap methods: {swap_methods}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative check failed: {e}")
        return False

if __name__ == "__main__":
    print("🎭 InsightFace Swapper Diagnostic")
    print("=" * 50)
    
    test1 = test_insightface_swapper()
    test2 = check_alternative_swapping()
    
    print("\n" + "=" * 50)
    if not test1:
        print("⚠️ FaceSwapper not available or not working")
        print("💡 We'll need to implement manual face swapping using FaceAnalysis")
    else:
        print("✅ FaceSwapper should work - there might be a different issue")