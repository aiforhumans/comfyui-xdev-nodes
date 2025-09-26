import { app } from "../../scripts/app.js";

app.registerExtension({
  name: "xdev.menu",
  async setup() {},
  async beforeRegisterNodeDef(nodeType, nodeData, appRef) {
    if (!nodeData?.name?.startsWith?.("XDEV_")) return;

    const onMenu = nodeType.prototype.getExtraMenuOptions;
    nodeType.prototype.getExtraMenuOptions = function(_, options) {
      onMenu?.apply(this, arguments);
      options.push({
        content: "XDev: Docs",
        callback: () => window.open("https://github.com/aiforhumans/comfyui-xdev-nodes", "_blank"),
      });
    };
  },
});
