"""Tests for XDEV Prompt Tools"""

import json

import pytest
from comfyui_custom_nodes.xdev import (
    MultilinePromptBuilder,
    PromptTemplateSystem,
    RandomPromptSelector,
    StyleTagsInjector,
    TextConcatenate,
)


class TestTextConcatenate:
    """Tests for TextConcatenate node."""
    
    def test_single_text(self):
        node = TextConcatenate()
        result = node.concatenate("Hello")
        assert result == ("Hello",)
    
    def test_multiple_texts(self):
        node = TextConcatenate()
        result = node.concatenate("Hello", "World", "Test")
        assert result == ("Hello, World, Test",)
    
    def test_custom_separator(self):
        node = TextConcatenate()
        result = node.concatenate("A", "B", "C", separator=" | ")
        assert result == ("A | B | C",)
    
    def test_empty_texts_ignored(self):
        node = TextConcatenate()
        result = node.concatenate("Hello", "", "World", separator=", ")
        assert result == ("Hello, World",)


class TestMultilinePromptBuilder:
    """Tests for MultilinePromptBuilder node."""
    
    def test_subject_only(self):
        node = MultilinePromptBuilder()
        positive, negative = node.build_prompt("a cat")
        assert positive == "a cat"
        assert negative == ""
    
    def test_full_prompt(self):
        node = MultilinePromptBuilder()
        positive, negative = node.build_prompt(
            subject="a cat",
            style="watercolor",
            quality="masterpiece",
            negative="blurry"
        )
        assert "a cat" in positive
        assert "watercolor" in positive
        assert "masterpiece" in positive
        assert negative == "blurry"
    
    def test_return_tuple(self):
        node = MultilinePromptBuilder()
        result = node.build_prompt("test")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestStyleTagsInjector:
    """Tests for StyleTagsInjector node."""
    
    def test_no_style(self):
        node = StyleTagsInjector()
        result = node.inject_style("a portrait", "None")
        assert result == ("a portrait",)
    
    def test_photorealistic_suffix(self):
        node = StyleTagsInjector()
        result = node.inject_style("a portrait", "Photorealistic", position="suffix")
        assert "a portrait" in result[0]
        assert "photorealistic" in result[0].lower()
    
    def test_cinematic_prefix(self):
        node = StyleTagsInjector()
        result = node.inject_style("a scene", "Cinematic", position="prefix")
        assert "cinematic" in result[0].lower()
        assert "a scene" in result[0]
    
    def test_style_strength(self):
        node = StyleTagsInjector()
        result = node.inject_style("test", "Anime", style_strength=1.5)
        assert "1.5" in result[0]


class TestRandomPromptSelector:
    """Tests for RandomPromptSelector node."""
    
    def test_single_prompt(self):
        node = RandomPromptSelector()
        result, index = node.select_random("only one prompt", seed=42)
        assert result == "only one prompt"
        assert index == 0
    
    def test_newline_delimiter(self):
        node = RandomPromptSelector()
        prompts = "prompt1\nprompt2\nprompt3"
        result, index = node.select_random(prompts, delimiter="newline", seed=42)
        assert result in ["prompt1", "prompt2", "prompt3"]
        assert 0 <= index <= 2
    
    def test_comma_delimiter(self):
        node = RandomPromptSelector()
        prompts = "prompt1,prompt2,prompt3"
        result, index = node.select_random(prompts, delimiter="comma", seed=42)
        assert result in ["prompt1", "prompt2", "prompt3"]
    
    def test_disabled_random(self):
        node = RandomPromptSelector()
        prompts = "first\nsecond\nthird"
        result, index = node.select_random(prompts, seed=42, enable_random=False)
        assert result == "first"
        assert index == 0
    
    def test_same_seed_same_result(self):
        node = RandomPromptSelector()
        prompts = "a\nb\nc\nd\ne"
        result1, _ = node.select_random(prompts, seed=123, enable_random=True)
        result2, _ = node.select_random(prompts, seed=123, enable_random=True)
        assert result1 == result2


class TestPromptTemplateSystem:
    """Tests for PromptTemplateSystem node."""
    
    def test_simple_substitution(self):
        node = PromptTemplateSystem()
        result = node.apply_template("A {animal} in {location}", var_1="cat", var_2="garden")
        assert result == ("A cat in garden",)
    
    def test_multiple_variables(self):
        node = PromptTemplateSystem()
        template = "{adj1} {subject} with {adj2} {object}"
        result = node.apply_template(template, var_1="red", var_2="car", var_3="blue", var_4="wheels")
        assert "red" in result[0]
        assert "car" in result[0]
    
    def test_missing_variables(self):
        node = PromptTemplateSystem()
        result = node.apply_template("A {something}", var_1="")
        assert result[0].strip() == "A"
    
    def test_no_template_variables(self):
        node = PromptTemplateSystem()
        result = node.apply_template("plain text without variables")
        assert result == ("plain text without variables",)

    def test_json_response_format(self):
        node = PromptTemplateSystem()
        result = node.apply_template(
            "A {var_1} with {var_2}",
            var_1="dragon",
            var_2="silver scales",
            response_format="json",
        )
        payload = json.loads(result[0])
        assert payload["prompt"].startswith("A dragon")
        assert payload["token_count"] >= 3
        assert "silver" in payload["prompt"]


# Smoke tests for manual execution
if __name__ == "__main__":
    print("Running XDEV Prompt Tools smoke tests...\n")
    
    # Test TextConcatenate
    print("Testing TextConcatenate...")
    tc = TestTextConcatenate()
    tc.test_single_text()
    tc.test_multiple_texts()
    tc.test_custom_separator()
    print("✓ TextConcatenate tests passed\n")
    
    # Test MultilinePromptBuilder
    print("Testing MultilinePromptBuilder...")
    mp = TestMultilinePromptBuilder()
    mp.test_subject_only()
    mp.test_full_prompt()
    mp.test_return_tuple()
    print("✓ MultilinePromptBuilder tests passed\n")
    
    # Test StyleTagsInjector
    print("Testing StyleTagsInjector...")
    si = TestStyleTagsInjector()
    si.test_no_style()
    si.test_photorealistic_suffix()
    si.test_cinematic_prefix()
    print("✓ StyleTagsInjector tests passed\n")
    
    # Test RandomPromptSelector
    print("Testing RandomPromptSelector...")
    rp = TestRandomPromptSelector()
    rp.test_single_prompt()
    rp.test_newline_delimiter()
    rp.test_disabled_random()
    rp.test_same_seed_same_result()
    print("✓ RandomPromptSelector tests passed\n")
    
    # Test PromptTemplateSystem
    print("Testing PromptTemplateSystem...")
    pt = TestPromptTemplateSystem()
    pt.test_simple_substitution()
    pt.test_multiple_variables()
    pt.test_no_template_variables()
    print("✓ PromptTemplateSystem tests passed\n")
    
    print("✅ All XDEV Prompt Tools tests passed!")
