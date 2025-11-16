"""End-to-end SDXL workflow smoke tests using prompt tools + LM Studio nodes."""

import json

import pytest

from comfyui_custom_nodes.xdev import LMStudioPromptEnhancer, MultilinePromptBuilder


@pytest.mark.usefixtures("monkeypatch")
def test_prompt_builder_into_enhancer(monkeypatch):
    """Ensure prompt builders feed into the enhancer with JSON parsing."""
    builder = MultilinePromptBuilder()
    positive, _ = builder.build_prompt(
        subject="a cyberpunk city",
        style="cinematic",
        composition="wide shot",
        lighting="neon",
        quality="highly detailed, 8k",
    )

    enhancer = LMStudioPromptEnhancer()

    def fake_api(self, **kwargs):
        return json.dumps(
            {
                "positive_prompt": f"{positive}, cinematic color grading",
                "negative_prompt": "low quality",
            }
        )

    monkeypatch.setattr(LMStudioPromptEnhancer, "_make_api_request", fake_api)

    enhanced, negative, info = enhancer.enhance_prompt(
        simple_prompt=positive,
        additional_details="keep the skyline sharp",
        negative_prompt=True,
        response_format="json",
        server_url="http://fake",
    )

    assert "cyberpunk" in enhanced
    assert "low quality" == negative
    assert "Enhancement" in info
