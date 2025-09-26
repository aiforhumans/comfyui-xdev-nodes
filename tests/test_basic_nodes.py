def test_hello_and_suffix():
    from xdev_nodes.nodes.basic import HelloString
    from xdev_nodes.nodes.text import AppendSuffix

    out = HelloString().hello()
    assert isinstance(out, tuple) and out[0].startswith("Hello")
    out2 = AppendSuffix().run("abc", "++")
    assert out2 == ("abc++",)