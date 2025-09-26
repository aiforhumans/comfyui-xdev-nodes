def test_hello_string():
    from xdev_nodes.nodes.basic import HelloString
    out = HelloString().hello()
    assert isinstance(out, tuple) and out[0].startswith("Hello")

def test_append_suffix():
    from xdev_nodes.nodes.text import AppendSuffix
    out = AppendSuffix().run("abc", "++")
    assert out == ("abc++",)
