"""Test the prompt manipulation nodes"""
import pytest

def test_prompt_combiner():
    """Test the XDEV_PromptCombiner node"""
    from xdev_nodes.nodes.prompt import XDEV_PromptCombiner
    
    node = XDEV_PromptCombiner()
    
    # Test basic concatenation
    result, info, count = node.combine_prompts(
        "beautiful landscape", 
        "dramatic lighting", 
        "concatenate", 
        "comma"
    )
    
    assert "beautiful landscape, dramatic lighting" in result
    assert count == 2
    assert "Combined 2 prompts" in info
    print(f"✅ PromptCombiner concatenation: {result}")
    
    # Test weighted merge
    result, info, count = node.combine_prompts(
        "portrait", 
        "detailed", 
        "weighted_merge", 
        "comma",
        weight_1=1.2,
        weight_2=0.8
    )
    
    assert "(portrait:1.2)" in result
    assert "(detailed:0.8)" in result
    print(f"✅ PromptCombiner weighted: {result}")


def test_prompt_weighter():
    """Test the XDEV_PromptWeighter node"""
    from xdev_nodes.nodes.prompt import XDEV_PromptWeighter
    
    node = XDEV_PromptWeighter()
    
    # Test adding emphasis
    result, info, count = node.process_weights(
        "beautiful sunset",
        "add_emphasis", 
        1.3,
        "beautiful"
    )
    
    assert "(beautiful:1.3)" in result
    assert count == 1
    print(f"✅ PromptWeighter emphasis: {result}")
    
    # Test removing weights
    weighted_prompt = "(beautiful:1.2) sunset, [water:0.8]"
    result, info, count = node.process_weights(
        weighted_prompt,
        "remove_weights",
        1.0
    )
    
    assert "beautiful sunset, water" == result.strip()
    assert count == 2
    print(f"✅ PromptWeighter remove: {result}")


@pytest.mark.skip(reason="PromptCleaner not migrated to XDEV_ system yet")
def test_prompt_cleaner():
    """Test the PromptCleaner node"""
    pytest.skip("Node not yet migrated")
    from xdev_nodes.nodes.prompt import PromptCleaner
    
    node = PromptCleaner()
    
    # Test cleaning messy prompt
    messy_prompt = "beautiful   landscape,, beautiful landscape  , dramatic lighting,   "
    result, info, count = node.clean_prompt(
        messy_prompt,
        remove_duplicates=True,
        fix_spacing=True,
        fix_punctuation=True
    )
    
    assert result == "beautiful landscape, dramatic lighting"
    assert count >= 1
    print(f"✅ PromptCleaner cleaning: '{messy_prompt}' → '{result}'")


@pytest.mark.skip(reason="PromptAnalyzer not migrated to XDEV_ system yet")
def test_prompt_analyzer():
    """Test the PromptAnalyzer node"""
    pytest.skip("Node not yet migrated")
    from xdev_nodes.nodes.prompt import PromptAnalyzer
    
    node = PromptAnalyzer()
    
    # Test analysis
    prompt = "beautiful (landscape:1.2), dramatic lighting, [noise:0.7], detailed artwork"
    report, stats, word_count, complexity = node.analyze_prompt(
        prompt,
        "comprehensive",
        include_weights=True,
        word_frequency=True
    )
    
    assert word_count > 0
    assert complexity > 0
    assert "PROMPT ANALYSIS REPORT" in report
    assert "WEIGHT ANALYSIS" in report
    print(f"✅ PromptAnalyzer: {word_count} words, complexity {complexity:.1f}")


@pytest.mark.skip(reason="PromptRandomizer not migrated to XDEV_ system yet") 
def test_prompt_randomizer():
    """Test the PromptRandomizer node"""
    pytest.skip("Node not yet migrated")
    from xdev_nodes.nodes.prompt import PromptRandomizer
    
    node = PromptRandomizer()
    
    # Test shuffle
    original = "beautiful, landscape, dramatic, lighting"
    result, info, seed = node.randomize_prompt(
        original,
        "shuffle_phrases",
        0.8,
        seed=12345
    )
    
    # Result should contain same elements but potentially different order
    original_words = set(original.replace(" ", "").split(","))
    result_words = set(result.replace(" ", "").split(","))
    assert original_words == result_words
    print(f"✅ PromptRandomizer shuffle: {original} → {result}")
    
    # Test adding variations
    result, info, seed = node.randomize_prompt(
        "portrait",
        "add_variations",
        0.5,
        variation_category="quality",
        seed=54321
    )
    
    assert "portrait" in result
    assert len(result) > len("portrait")  # Should be longer with additions
    print(f"✅ PromptRandomizer variations: {result}")


if __name__ == "__main__":
    test_prompt_combiner()
    test_prompt_weighter() 
    test_prompt_cleaner()
    test_prompt_analyzer()
    test_prompt_randomizer()
    print("\n🎉 All prompt tool tests passed!")