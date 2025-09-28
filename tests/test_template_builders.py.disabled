#!/usr/bin/env python3
"""
Test suite for XDev template builder nodes (PersonBuilder, StyleBuilder).
Tests comprehensive template generation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from xdev_nodes.nodes.prompt import PersonBuilder, StyleBuilder


class TestPersonBuilder:
    """Test PersonBuilder template functionality"""
    
    def test_person_builder_import(self):
        """Test that PersonBuilder can be imported"""
        assert PersonBuilder is not None
        assert hasattr(PersonBuilder, 'INPUT_TYPES')
        assert hasattr(PersonBuilder, 'build_person')
    
    def test_basic_person_generation(self):
        """Test basic person prompt generation"""
        builder = PersonBuilder()
        
        # Test basic person generation
        result = builder.build_person(
            age="adult",
            gender="person", 
            expression="neutral",
            seed=12345
        )
        
        prompt, info, summary = result
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "adult" in prompt.lower() or "person" in prompt.lower()
        assert isinstance(info, str)
        assert isinstance(summary, str)
        
    def test_detailed_person_generation(self):
        """Test detailed person generation with all options"""
        builder = PersonBuilder()
        
        result = builder.build_person(
            age="young_adult",
            gender="female",
            expression="happy",
            hair_color="blonde",
            hair_style="long",
            eye_color="blue", 
            pose="portrait",
            clothing="casual",
            archetype="artist",
            custom_traits="creative, inspiring",
            add_quality=True,
            seed=12345
        )
        
        prompt, info, summary = result
        assert isinstance(prompt, str)
        assert len(prompt) > 50  # Should be detailed
        assert "," in prompt  # Should have multiple elements
        assert "creative" in prompt
        assert "inspiring" in prompt
        
    def test_randomization(self):
        """Test randomized trait generation"""
        builder = PersonBuilder()
        
        # Test with randomization
        result1 = builder.build_person(
            age="auto",
            gender="auto", 
            expression="auto",
            randomize_traits=True,
            seed=12345
        )
        
        result2 = builder.build_person(
            age="auto",
            gender="auto",
            expression="auto", 
            randomize_traits=True,
            seed=54321
        )
        
        # Different seeds should produce different results
        assert result1[0] != result2[0]
        
    def test_validation_handling(self):
        """Test input validation"""
        builder = PersonBuilder()
        
        # Test with invalid custom traits (empty should be fine)
        result = builder.build_person(
            age="adult",
            gender="person",
            expression="neutral",
            custom_traits="",
            validate_input=True
        )
        
        # Should not error on empty custom traits
        assert not result[0].startswith("Error:")


class TestStyleBuilder:
    """Test StyleBuilder template functionality"""
    
    def test_style_builder_import(self):
        """Test that StyleBuilder can be imported"""
        assert StyleBuilder is not None
        assert hasattr(StyleBuilder, 'INPUT_TYPES')
        assert hasattr(StyleBuilder, 'build_style')
    
    def test_basic_style_generation(self):
        """Test basic style prompt generation"""
        builder = StyleBuilder()
        
        result = builder.build_style(
            primary_style="digital_painting",
            medium="auto",
            color_palette="vibrant",
            seed=12345
        )
        
        prompt, info, breakdown = result
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "digital" in prompt.lower() or "painting" in prompt.lower()
        assert "vibrant" in prompt.lower() or "bright" in prompt.lower()
        assert isinstance(info, str)
        assert isinstance(breakdown, str)
        
    def test_detailed_style_generation(self):
        """Test detailed style generation with all options"""
        builder = StyleBuilder()
        
        result = builder.build_style(
            primary_style="impressionist",
            medium="oil_painting",
            color_palette="warm",
            lighting="golden_hour",
            composition="rule_of_thirds", 
            texture="smooth",
            custom_style="ethereal, dreamlike",
            add_technical=True,
            style_weight=1.2,
            seed=12345
        )
        
        prompt, info, breakdown = result
        assert isinstance(prompt, str)
        assert len(prompt) > 50  # Should be detailed
        assert "ethereal" in prompt
        assert "dreamlike" in prompt
        assert "1.2" in prompt  # Weight should be applied
        
    def test_art_movement_styles(self):
        """Test different art movement styles"""
        builder = StyleBuilder()
        
        movements = ["renaissance", "baroque", "impressionist", "surrealist"]
        
        for movement in movements:
            result = builder.build_style(
                primary_style=movement,
                medium="auto",
                color_palette="auto",
                seed=12345
            )
            
            prompt, info, breakdown = result
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            # Should contain style information
            assert movement in breakdown.lower() or movement in info.lower()
            
    def test_digital_styles(self):
        """Test digital art styles"""
        builder = StyleBuilder()
        
        digital_styles = ["concept_art", "3d_render", "pixel_art", "vector_art"]
        
        for style in digital_styles:
            result = builder.build_style(
                primary_style=style,
                medium="auto",
                color_palette="auto",
                seed=12345
            )
            
            prompt, info, breakdown = result
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            
    def test_style_weighting(self):
        """Test style weight functionality"""
        builder = StyleBuilder()
        
        # Test with weight
        result = builder.build_style(
            primary_style="cubist",
            medium="auto",
            color_palette="auto",
            style_weight=1.5,
            seed=12345
        )
        
        prompt, info, breakdown = result
        # Should contain weighted style notation
        assert ":1.5" in prompt
        
    def test_randomization(self):
        """Test randomized style selection"""
        builder = StyleBuilder()
        
        # Test with randomization
        result1 = builder.build_style(
            primary_style="auto",
            medium="auto",
            color_palette="auto",
            randomize_auto=True,
            seed=12345
        )
        
        result2 = builder.build_style(
            primary_style="auto", 
            medium="auto",
            color_palette="auto",
            randomize_auto=True,
            seed=54321
        )
        
        # Different seeds should produce different results
        assert result1[0] != result2[0]
        
    def test_technical_quality_addition(self):
        """Test technical quality term addition"""
        builder = StyleBuilder()
        
        # With technical terms
        result_with = builder.build_style(
            primary_style="digital_painting",
            medium="auto",
            color_palette="vibrant",
            add_technical=True,
            seed=12345
        )
        
        # Without technical terms
        result_without = builder.build_style(
            primary_style="digital_painting",
            medium="auto", 
            color_palette="vibrant",
            add_technical=False,
            seed=12345
        )
        
        # With technical should be longer
        assert len(result_with[0]) > len(result_without[0])


def run_all_tests():
    """Run all template builder tests"""
    
    # PersonBuilder tests
    person_tests = TestPersonBuilder()
    print("🧪 Testing PersonBuilder...")
    
    person_tests.test_person_builder_import()
    print("  ✅ Import test passed")
    
    person_tests.test_basic_person_generation()
    print("  ✅ Basic generation test passed")
    
    person_tests.test_detailed_person_generation()
    print("  ✅ Detailed generation test passed")
    
    person_tests.test_randomization()
    print("  ✅ Randomization test passed")
    
    person_tests.test_validation_handling()
    print("  ✅ Validation test passed")
    
    # StyleBuilder tests
    style_tests = TestStyleBuilder()
    print("\n🎨 Testing StyleBuilder...")
    
    style_tests.test_style_builder_import()
    print("  ✅ Import test passed")
    
    style_tests.test_basic_style_generation()
    print("  ✅ Basic generation test passed")
    
    style_tests.test_detailed_style_generation()
    print("  ✅ Detailed generation test passed")
    
    style_tests.test_art_movement_styles()
    print("  ✅ Art movement test passed")
    
    style_tests.test_digital_styles()
    print("  ✅ Digital styles test passed")
    
    style_tests.test_style_weighting()
    print("  ✅ Style weighting test passed")
    
    style_tests.test_randomization()
    print("  ✅ Randomization test passed")
    
    style_tests.test_technical_quality_addition()
    print("  ✅ Technical quality test passed")
    
    print(f"\n🎉 All template builder tests passed! Tested 2 nodes with 13 test functions.")


if __name__ == "__main__":
    run_all_tests()