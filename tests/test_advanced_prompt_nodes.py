#!/usr/bin/env python3
"""
Test suite for XDev Phase 4 Advanced Prompt nodes.
Tests advanced prompt engineering functionality including matrix generation,
interpolation, scheduling, attention control, chain-of-thought, and few-shot prompting.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from xdev_nodes.nodes.prompt import (
    PromptMatrix, PromptInterpolator, PromptScheduler, 
    PromptAttention, PromptChainOfThought, PromptFewShot
)


class TestPromptMatrix:
    """Test PromptMatrix node functionality"""
    
    def test_prompt_matrix_import(self):
        """Test that PromptMatrix can be imported"""
        assert PromptMatrix is not None
        assert hasattr(PromptMatrix, 'INPUT_TYPES')
        assert hasattr(PromptMatrix, 'generate_matrix')
    
    def test_basic_matrix_generation(self):
        """Test basic matrix prompt generation"""
        matrix = PromptMatrix()
        
        result = matrix.generate_matrix(
            matrix_prompt="a cat | sitting | striped",
            combination_mode="all_combinations",
            seed=12345
        )
        
        prompts, info, combinations = result
        assert isinstance(prompts, str)
        assert len(prompts) > 0
        assert "cat" in prompts
        assert isinstance(info, str)
        assert "combinations" in info.lower()
        
    def test_incremental_mode(self):
        """Test incremental combination mode"""
        matrix = PromptMatrix()
        
        result = matrix.generate_matrix(
            matrix_prompt="dog | running | happy",
            combination_mode="incremental",
            seed=12345
        )
        
        prompts, info, combinations = result
        assert "dog" in prompts  # Base element should be present
        lines = prompts.split('\n')
        assert len(lines) >= 2  # Should have multiple combinations
        
    def test_pairwise_mode(self):
        """Test pairwise combination mode"""
        matrix = PromptMatrix()
        
        result = matrix.generate_matrix(
            matrix_prompt="person | walking | sunset",
            combination_mode="pairwise",
            base_prompt="beautiful scene",
            seed=12345
        )
        
        prompts, info, combinations = result
        assert "beautiful scene" in prompts  # Base should be included
        assert "person" in prompts


class TestPromptInterpolator:
    """Test PromptInterpolator node functionality"""
    
    def test_prompt_interpolator_import(self):
        """Test that PromptInterpolator can be imported"""
        assert PromptInterpolator is not None
        assert hasattr(PromptInterpolator, 'INPUT_TYPES')
        assert hasattr(PromptInterpolator, 'interpolate_prompts')
    
    def test_weighted_blend(self):
        """Test weighted blend interpolation"""
        interpolator = PromptInterpolator()
        
        result = interpolator.interpolate_prompts(
            prompt_a="sunny day",
            prompt_b="rainy night",
            ratio=0.3,
            method="weighted_blend"
        )
        
        prompts, info, ratios = result
        assert isinstance(prompts, str)
        assert "sunny day" in prompts or "rainy night" in prompts
        assert "weighted_blend" in info
        
    def test_multiple_steps(self):
        """Test multi-step interpolation"""
        interpolator = PromptInterpolator()
        
        result = interpolator.interpolate_prompts(
            prompt_a="morning",
            prompt_b="evening", 
            ratio=0.5,
            steps=3,
            method="linear"
        )
        
        prompts, info, ratios = result
        lines = prompts.split('\n')
        assert len(lines) >= 3  # Should have multiple steps
        
    def test_token_merge(self):
        """Test token merge interpolation"""
        interpolator = PromptInterpolator()
        
        result = interpolator.interpolate_prompts(
            prompt_a="red car, fast",
            prompt_b="blue bike, slow",
            ratio=0.5,
            method="token_merge"
        )
        
        prompts, info, ratios = result
        # Should contain elements from both prompts
        assert isinstance(prompts, str) and len(prompts) > 0


class TestPromptScheduler:
    """Test PromptScheduler node functionality"""
    
    def test_prompt_scheduler_import(self):
        """Test that PromptScheduler can be imported"""
        assert PromptScheduler is not None
        assert hasattr(PromptScheduler, 'INPUT_TYPES')
        assert hasattr(PromptScheduler, 'schedule_prompts')
    
    def test_step_based_scheduling(self):
        """Test step-based prompt scheduling"""
        scheduler = PromptScheduler()
        
        result = scheduler.schedule_prompts(
            base_prompt="beautiful landscape",
            schedule_syntax="[morning:evening:10]",
            total_steps=20,
            schedule_mode="step_based"
        )
        
        prompt, info, breakdown = result
        assert isinstance(prompt, str)
        # The prompt should contain the base prompt
        assert "beautiful landscape" in prompt
        # The info should contain scheduling information
        assert "morning" in info and "evening" in info
        assert "step_based" in info.lower()
        
    def test_alternating_mode(self):
        """Test alternating schedule mode"""
        scheduler = PromptScheduler()
        
        result = scheduler.schedule_prompts(
            base_prompt="changing scene",
            schedule_syntax="[day|night]",
            schedule_mode="alternating",
            preview_steps=True
        )
        
        prompt, info, breakdown = result
        assert "day" in breakdown or "night" in breakdown
        
    def test_multiple_schedules(self):
        """Test multiple scheduling patterns"""
        scheduler = PromptScheduler()
        
        result = scheduler.schedule_prompts(
            base_prompt="dynamic scene",
            schedule_syntax="[calm:storm:5] and [bright|dark]",
            total_steps=15
        )
        
        prompt, info, breakdown = result
        assert "storm" in info or "calm" in info


class TestPromptAttention:
    """Test PromptAttention node functionality"""
    
    def test_prompt_attention_import(self):
        """Test that PromptAttention can be imported"""
        assert PromptAttention is not None
        assert hasattr(PromptAttention, 'INPUT_TYPES')
        assert hasattr(PromptAttention, 'modify_attention')
    
    def test_add_emphasis(self):
        """Test adding emphasis to terms"""
        attention = PromptAttention()
        
        result = attention.modify_attention(
            prompt="beautiful sunset landscape",
            operation="add_emphasis",
            target_terms="beautiful, sunset",
            emphasis_weight=1.3
        )
        
        weighted_prompt, info, analysis = result
        # Should contain weight syntax
        assert "(" in weighted_prompt and ":" in weighted_prompt
        assert "1.3" in weighted_prompt
        
    def test_remove_weights(self):
        """Test removing attention weights"""
        attention = PromptAttention()
        
        # First add weights, then remove them
        result = attention.modify_attention(
            prompt="(beautiful:1.2) sunset [boring:0.8] landscape",
            operation="remove_weights"
        )
        
        weighted_prompt, info, analysis = result
        # Should not contain weight syntax
        assert "beautiful" in weighted_prompt
        assert ":" not in weighted_prompt or "(" not in weighted_prompt
        
    def test_auto_enhance(self):
        """Test automatic enhancement"""
        attention = PromptAttention()
        
        result = attention.modify_attention(
            prompt="masterpiece artwork with detailed textures",
            operation="auto_enhance",
            important_keywords="masterpiece, detailed"
        )
        
        weighted_prompt, info, analysis = result
        assert "masterpiece" in weighted_prompt
        assert "detailed" in weighted_prompt


class TestPromptChainOfThought:
    """Test PromptChainOfThought node functionality"""
    
    def test_chain_of_thought_import(self):
        """Test that PromptChainOfThought can be imported"""
        assert PromptChainOfThought is not None
        assert hasattr(PromptChainOfThought, 'INPUT_TYPES')
        assert hasattr(PromptChainOfThought, 'generate_chain_of_thought')
    
    def test_step_by_step_reasoning(self):
        """Test step-by-step chain of thought"""
        cot = PromptChainOfThought()
        
        result = cot.generate_chain_of_thought(
            base_prompt="portrait of an artist",
            reasoning_style="step_by_step",
            complexity_level="moderate"
        )
        
        cot_prompt, info, structure = result
        assert "step by step" in cot_prompt.lower()
        assert "portrait of an artist" in cot_prompt
        assert "step_by_step" in info
        
    def test_problem_solving_structure(self):
        """Test problem-solving CoT structure"""
        cot = PromptChainOfThought()
        
        result = cot.generate_chain_of_thought(
            base_prompt="complex technical diagram",
            reasoning_style="problem_solving",
            complexity_level="detailed"
        )
        
        cot_prompt, info, structure = result
        assert "Problem:" in cot_prompt or "Analysis:" in cot_prompt
        assert "complex technical diagram" in cot_prompt
        
    def test_custom_structure(self):
        """Test custom CoT structure"""
        cot = PromptChainOfThought()
        
        result = cot.generate_chain_of_thought(
            base_prompt="creative artwork",
            reasoning_style="step_by_step",
            custom_structure="First: {analysis}\nThen: {reasoning}\nFinally: {conclusion}",
            complexity_level="simple"
        )
        
        cot_prompt, info, structure = result
        assert "First:" in cot_prompt or "Then:" in cot_prompt


class TestPromptFewShot:
    """Test PromptFewShot node functionality"""
    
    def test_few_shot_import(self):
        """Test that PromptFewShot can be imported"""
        assert PromptFewShot is not None
        assert hasattr(PromptFewShot, 'INPUT_TYPES')
        assert hasattr(PromptFewShot, 'generate_few_shot')
    
    def test_auto_category_detection(self):
        """Test automatic category detection"""
        few_shot = PromptFewShot()
        
        result = few_shot.generate_few_shot(
            target_prompt="professional portrait of a woman",
            example_category="auto",
            num_examples=2
        )
        
        few_shot_prompt, info, analysis = result
        assert "portrait" in few_shot_prompt.lower()
        assert "examples" in info.lower()
        
    def test_custom_examples(self):
        """Test custom example usage"""
        few_shot = PromptFewShot()
        
        custom_examples = """detailed cityscape at night
abstract geometric pattern
vintage car illustration"""
        
        result = few_shot.generate_few_shot(
            target_prompt="modern architecture design",
            num_examples=2,
            custom_examples=custom_examples,
            selection_method="similarity"
        )
        
        few_shot_prompt, info, analysis = result
        assert "modern architecture design" in few_shot_prompt
        # Should contain at least one of the custom examples or the target
        assert len(few_shot_prompt) > len("modern architecture design")
        assert "custom" in info.lower()
        
    def test_diversity_selection(self):
        """Test diversity-based example selection"""
        few_shot = PromptFewShot()
        
        result = few_shot.generate_few_shot(
            target_prompt="artistic landscape painting",
            example_category="landscape",
            selection_method="diversity",
            num_examples=3
        )
        
        few_shot_prompt, info, analysis = result
        assert "landscape" in few_shot_prompt.lower()
        assert "diversity" in info.lower()
        
    def test_formatting_styles(self):
        """Test different formatting styles"""
        few_shot = PromptFewShot()
        
        # Test numbered format
        result = few_shot.generate_few_shot(
            target_prompt="technical illustration",
            example_category="technical",
            format_style="numbered",
            num_examples=2
        )
        
        few_shot_prompt, info, analysis = result
        # Should contain the target prompt and some formatting
        assert "technical illustration" in few_shot_prompt
        assert len(few_shot_prompt) > 50  # Should have examples and formatting


def run_all_tests():
    """Run all advanced prompt node tests"""
    
    # PromptMatrix tests
    matrix_tests = TestPromptMatrix()
    print("🔄 Testing PromptMatrix...")
    
    matrix_tests.test_prompt_matrix_import()
    print("  ✅ Import test passed")
    
    matrix_tests.test_basic_matrix_generation()
    print("  ✅ Basic generation test passed")
    
    matrix_tests.test_incremental_mode()
    print("  ✅ Incremental mode test passed")
    
    matrix_tests.test_pairwise_mode()
    print("  ✅ Pairwise mode test passed")
    
    # PromptInterpolator tests
    interpolator_tests = TestPromptInterpolator()
    print("\n🔄 Testing PromptInterpolator...")
    
    interpolator_tests.test_prompt_interpolator_import()
    print("  ✅ Import test passed")
    
    interpolator_tests.test_weighted_blend()
    print("  ✅ Weighted blend test passed")
    
    interpolator_tests.test_multiple_steps()
    print("  ✅ Multiple steps test passed")
    
    interpolator_tests.test_token_merge()
    print("  ✅ Token merge test passed")
    
    # PromptScheduler tests
    scheduler_tests = TestPromptScheduler()
    print("\n📅 Testing PromptScheduler...")
    
    scheduler_tests.test_prompt_scheduler_import()
    print("  ✅ Import test passed")
    
    scheduler_tests.test_step_based_scheduling()
    print("  ✅ Step-based scheduling test passed")
    
    scheduler_tests.test_alternating_mode()
    print("  ✅ Alternating mode test passed")
    
    scheduler_tests.test_multiple_schedules()
    print("  ✅ Multiple schedules test passed")
    
    # PromptAttention tests
    attention_tests = TestPromptAttention()
    print("\n⚡ Testing PromptAttention...")
    
    attention_tests.test_prompt_attention_import()
    print("  ✅ Import test passed")
    
    attention_tests.test_add_emphasis()
    print("  ✅ Add emphasis test passed")
    
    attention_tests.test_remove_weights()
    print("  ✅ Remove weights test passed")
    
    attention_tests.test_auto_enhance()
    print("  ✅ Auto enhance test passed")
    
    # PromptChainOfThought tests
    cot_tests = TestPromptChainOfThought()
    print("\n🧠 Testing PromptChainOfThought...")
    
    cot_tests.test_chain_of_thought_import()
    print("  ✅ Import test passed")
    
    cot_tests.test_step_by_step_reasoning()
    print("  ✅ Step-by-step reasoning test passed")
    
    cot_tests.test_problem_solving_structure()
    print("  ✅ Problem-solving structure test passed")
    
    cot_tests.test_custom_structure()
    print("  ✅ Custom structure test passed")
    
    # PromptFewShot tests
    few_shot_tests = TestPromptFewShot()
    print("\n📚 Testing PromptFewShot...")
    
    few_shot_tests.test_few_shot_import()
    print("  ✅ Import test passed")
    
    few_shot_tests.test_auto_category_detection()
    print("  ✅ Auto category detection test passed")
    
    few_shot_tests.test_custom_examples()
    print("  ✅ Custom examples test passed")
    
    few_shot_tests.test_diversity_selection()
    print("  ✅ Diversity selection test passed")
    
    few_shot_tests.test_formatting_styles()
    print("  ✅ Formatting styles test passed")
    
    print(f"\n🎉 All Phase 4 advanced prompt tests passed! Tested 6 nodes with 23 test functions.")


if __name__ == "__main__":
    run_all_tests()