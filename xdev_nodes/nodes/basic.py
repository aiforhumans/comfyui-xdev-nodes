class HelloString:
    """
    A trivial example node that returns a constant string.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "hello"
    CATEGORY = "XDev/Basic"

    def hello(self):
        return ("Hello ComfyUI!",)


class AnyPassthrough:
    """
    Demonstrates the 'ANY' datatype: accepts any input and returns it unchanged.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("*", {})}}  # also works with ("ANY", {})

    RETURN_TYPES = ("*",)  # pass-through of the same type
    FUNCTION = "do_it"
    CATEGORY = "XDev/Basic"

    def do_it(self, value):
        return (value,)
