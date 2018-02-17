import unittest
import pytest

from binflakes.types import BinInt, BinWord, BinArray
from binflakes.sexpr.symbol import Symbol
from binflakes.sexpr.nodes import (
    NodeList, NodeSymbol, NodeNil, NodeBool, NodeInt, NodeWord, NodeArray,
    NodeString, make_node
)


class TestNodes(unittest.TestCase):
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

    def test_bool(self):
        a = NodeBool(True)
        assert str(a) == '@true'
        b = make_node(True)
        assert a == b
        a = NodeBool(False)
        assert str(a) == '@false'
        b = make_node(False)
        assert a == b

    def test_int(self):
        a = NodeInt(BinInt(123))
        assert str(a) == '123'
        b = make_node(123)
        assert a == b
        a = NodeInt(BinInt(0x456))
        assert str(a) == '1110'
        b = make_node(0x456)
        assert a == b

    def test_word(self):
        a = NodeWord(BinWord(13, 0x1234))
        assert str(a) == '13\'0x1234'
        b = make_node(BinWord(13, 0x1234))
        assert a == b
        a = NodeWord(BinWord(0, 0))
        assert str(a) == '0\'0x0'
        b = make_node(BinWord(0, 0))
        assert a == b

    def test_array(self):
        a = NodeArray(BinArray([0x1234, 0x567], width=13))
        assert str(a) == '13\'0x(1234 0567)'
        a = NodeArray(BinArray([0, 0], width=0))
        assert str(a) == '0\'0x(0 0)'
        a = NodeArray(BinArray(width=123))
        assert str(a) == '123\'0x()'
        b = make_node(BinArray(width=123))
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
