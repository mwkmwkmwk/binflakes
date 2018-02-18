import pytest

from binflakes.types import BinInt, BinWord, BinArray
from binflakes.sexpr.symbol import Symbol
from binflakes.sexpr.nodes import (
    NodeList, NodeSymbol, NodeNil, NodeBool, NodeInt, NodeWord, NodeArray,
    NodeString, make_node,
)


class TestNodes:
    def test_list(self):
        a = NodeList([NodeNil(), NodeBool(True), NodeList([]),
                      NodeInt(BinInt(123))])
        assert str(a) == '(@nil @true () 123)'
        with pytest.raises(TypeError):
            NodeList([123])
        with pytest.raises(TypeError):
            NodeList('abc')
        b = make_node([None, True, (), 123])
        assert a == b

    def test_symbol(self):
        a = NodeSymbol(Symbol('abc'))
        assert str(a) == 'abc'
        b = make_node(Symbol('abc'))
        assert a == b

    def test_nil(self):
        a = NodeNil()
        assert str(a) == '@nil'
        b = make_node(None)
        assert a == b

    @pytest.mark.parametrize(('val', 'res'), [
        (True, '@true'),
        (False, '@false'),
    ])
    def test_bool(self, val, res):
        a = NodeBool(val)
        assert str(a) == res
        b = make_node(val)
        assert a == b

    @pytest.mark.parametrize(('val', 'res'), [
        (123, '123'),
        (0x456, '1110'),
    ])
    def test_int(self, val, res):
        a = NodeInt(BinInt(val))
        assert str(a) == res
        b = make_node(val)
        assert a == b

    @pytest.mark.parametrize(('val', 'res'), [
        (BinWord(13, 0x1234), '13\'0x1234'),
        (BinWord(0, 0), '0\'0x0'),
    ])
    def test_word(self, val, res):
        a = NodeWord(val)
        assert str(a) == res
        b = make_node(val)
        assert a == b

    @pytest.mark.parametrize(('val', 'res'), [
        (BinArray([0x1234, 0x567], width=13), '13\'0x(1234 0567)'),
        (BinArray([0, 0], width=0), '0\'0x(0 0)'),
        (BinArray(width=123), '123\'0x()'),
    ])
    def test_array(self, val, res):
        a = NodeArray(val)
        assert str(a) == res
        b = make_node(val)
        assert a == b

    def test_string(self):
        a = NodeString('\a\bcd\x1b\f')
        assert str(a) == '"\\a\\bcd\\e\\f"'
        b = make_node('\a\bcd\x1b\f')
        assert a == b

    def test_make_node(self):
        with pytest.raises(TypeError):
            make_node({})
        with pytest.raises(TypeError):
            make_node(1.5)
        a = make_node(13)
        assert make_node(a) == a
