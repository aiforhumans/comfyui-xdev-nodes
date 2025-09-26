from .nodes.basic import HelloString, AnyPassthrough
from .nodes.image import PickByBrightness
from .nodes.text import AppendSuffix

WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "XDEV_HelloString": HelloString,
    "XDEV_AnyPassthrough": AnyPassthrough,
    "XDEV_PickByBrightness": PickByBrightness,
    "XDEV_AppendSuffix": AppendSuffix,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_HelloString": "Hello String (XDev)",
    "XDEV_AnyPassthrough": "Any Passthrough (XDev)",
    "XDEV_PickByBrightness": "Pick Image by Brightness (XDev)",
    "XDEV_AppendSuffix": "Append Suffix (XDev)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
