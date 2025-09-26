from __future__ import annotations
from typing import Dict, Tuple, Any

class HelloString:
    """A trivial example node that returns a constant string."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "hello"
    CATEGORY = "XDev/Basic"

    def hello(self) -> Tuple[str]:
        return ("Hello ComfyUI!",)


class AnyPassthrough:
    """Demonstrates the `ANY` datatype: accepts any input and returns it unchanged."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {"required": {"value": ("*", {})}}

    RETURN_TYPES = ("*",)
    FUNCTION = "do_it"
    CATEGORY = "XDev/Basic"

    def do_it(self, value):
        return (value,)