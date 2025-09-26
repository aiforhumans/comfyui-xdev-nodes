class AppendSuffix:
    """
    Simple STRING transformer used in tests and examples.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": " - xdev"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "XDev/Text"

    def run(self, text: str, suffix: str):
        return (f"{text}{suffix}",)
