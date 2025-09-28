"""
Quick test script to debug the Advanced KSampler output issue
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

def test_without_torch():
    """Test the sampling logic without torch dependencies"""
    
    print("=== Testing AdvancedKSampler Output Types ===")
    
    # Create mock LATENT data (similar to what InputDev would generate)
    mock_latent = {
        "samples": "mock_tensor_placeholder"  # Placeholder since we don't have torch
    }
    
    print(f"Input LATENT type: {type(mock_latent)}")
    print(f"Input LATENT keys: {list(mock_latent.keys())}")
    
    # Test the variant generation logic
    try:
        from xdev_nodes.nodes.sampling_advanced import AdvancedKSampler
        
        sampler = AdvancedKSampler()
        
        # Mock parameters
        model = "mock_model"
        positive = "mock_positive"
        negative = "mock_negative"
        seed = 42
        steps = 20
        cfg = 7.0
        sampler_name = "euler"
        scheduler = "normal"
        denoise = 1.0
        
        # Call the generation method
        result = sampler.generate_variants(
            model, positive, negative, mock_latent, 
            seed, steps, cfg, sampler_name, scheduler, denoise
        )
        
        print(f"\nResult tuple length: {len(result)}")
        print("Result types:")
        for i, item in enumerate(result):
            print(f"  [{i}]: {type(item)} - {type(item).__name__}")
            if isinstance(item, dict):
                print(f"       Keys: {list(item.keys())}")
            elif isinstance(item, str):
                print(f"       Preview: {item[:100]}...")
        
        # Check if first 3 outputs are LATENT dicts
        for i in range(3):
            is_latent = isinstance(result[i], dict) and "samples" in result[i]
            print(f"  Output {i+1} is LATENT dict: {is_latent}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_without_torch()