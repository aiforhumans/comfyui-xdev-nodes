def test_module_import():
    import xdev_nodes
    assert hasattr(xdev_nodes, "NODE_CLASS_MAPPINGS")
    assert "XDEV_HelloString" in xdev_nodes.NODE_CLASS_MAPPINGS