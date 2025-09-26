from .nodes.basic import HelloString, AnyPassthrough
from .nodes.image import PickByBrightness
from .nodes.text import AppendSuffix
from .nodes.dev_nodes import OutputDev, InputDev
from .nodes.vae_tools import VAERoundTrip, VAEPreview

# If you add frontend assets, keep this path relative to this package root.
WEB_DIRECTORY = "./web"

NODE_CLASS_MAPPINGS = {
    "XDEV_HelloString": HelloString,
    "XDEV_AnyPassthrough": AnyPassthrough,
    "XDEV_PickByBrightness": PickByBrightness,
    "XDEV_AppendSuffix": AppendSuffix,
    "XDEV_OutputDev": OutputDev,
    "XDEV_InputDev": InputDev,
    "XDEV_VAERoundTrip": VAERoundTrip,
    "XDEV_VAEPreview": VAEPreview,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XDEV_HelloString": "Hello String (XDev)",
    "XDEV_AnyPassthrough": "Any Passthrough (XDev)",
    "XDEV_PickByBrightness": "Pick Image by Brightness (XDev)",
    "XDEV_AppendSuffix": "Append Suffix (XDev)",
    "XDEV_OutputDev": "Output Dev (XDev)",
    "XDEV_InputDev": "Input Dev (XDev)",
    "XDEV_VAERoundTrip": "VAE Round-Trip (XDev)",
    "XDEV_VAEPreview": "VAE Preview (XDev)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]