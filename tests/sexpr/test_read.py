import textwrap

import pytest

from binflakes.types import BinInt, BinWord, BinArray
from binflakes.sexpr.symbol import Symbol
from binflakes.sexpr.nodes import (
    GenericListNode, SymbolNode, NilNode, BoolNode, IntNode, WordNode,
    ArrayNode, StringNode, GenericNode,
)
from binflakes.sexpr.read import read_string, ReadError
from binflakes.sexpr.location import TextLocationRange


class TestRead:
    @pytest.mark.parametrize(('s', 't', 'v'), [
        ('abcDEF', SymbolNode, Symbol('abcDEF')),
        ('-', SymbolNode, Symbol('-')),
        ('@nil', NilNode, None),
        ('@false', BoolNode, False),
        ('@true', BoolNode, True),
        ('0', IntNode, BinInt(0)),
        ('123', IntNode, BinInt(123)),
        ('0x123', IntNode, BinInt(0x123)),
        ('0o123', IntNode, BinInt(0o123)),
        ('0b101', IntNode, BinInt(0b101)),
        ('-123', IntNode, BinInt(-123)),
        ('-0x123', IntNode, BinInt(-0x123)),
        ('-0o123', IntNode, BinInt(-0o123)),
        ('-0b101', IntNode, BinInt(-0b101)),
        ('123456789', IntNode, BinInt(123456789)),
        ('0o01234567', IntNode, BinInt(0o1234567)),
        ('0x0123456789abcdefABCDEF', IntNode,
         BinInt(0x0123456789abcdefabcdef)),
        ('12\'0x123', WordNode, BinWord(12, 0x123)),
        ('12\'0o1234', WordNode, BinWord(12, 0o1234)),
        ('12\'1234', WordNode, BinWord(12, 1234)),
        ('3\'0b101', WordNode, BinWord(3, 0b101)),
        ('12\'-0x123', WordNode, BinWord(12, -0x123, trunc=True)),
        ('12\'-0o1234', WordNode, BinWord(12, -0o1234, trunc=True)),
        ('12\'-1234', WordNode, BinWord(12, -1234, trunc=True)),
        ('3\'-0b101', WordNode, BinWord(3, -0b101, trunc=True)),
        ('3\'0b111', WordNode, BinWord(3, 0b111)),
        ('3\'-0b1000', WordNode, BinWord(3, 0)),
        ('12\'0x()', ArrayNode, BinArray(width=12)),
        ('12\'0x(123  456)', ArrayNode,
         BinArray([0x123, 0x456], width=12)),
        ('12\'0x(-123 -456)', ArrayNode,
         BinArray([0xedd, 0xbaa], width=12)),
        ('12\'0x(fff -1000)', ArrayNode, BinArray([0xfff, 0], width=12)),
        ('0\'0x()', ArrayNode, BinArray(width=0)),
        ('0\'0x(0 0)', ArrayNode, BinArray([0, 0], width=0)),
        ('7\'"abc"', ArrayNode, BinArray([0x61, 0x62, 0x63], width=7)),
        ('5\'0b(10101 1010)', ArrayNode, BinArray([0x15, 0xa], width=5)),
        ('5\'(12 0 20 9)', ArrayNode, BinArray([12, 0, 20, 9], width=5)),
        ('6\'0o(12 23)', ArrayNode, BinArray([0o12, 0o23], width=6)),
        ('"abc"', StringNode, 'abc'),
        ('"\\a\\bcd\\e\\f\\r\\n\\\\\\"ghi"', StringNode,
         '\a\bcd\x1b\f\r\n\\"ghi'),
        ('"\\x12\\u1234\\U102345"', StringNode, '\x12\u1234\U00102345'),
        ('"\\x1234"', StringNode, '\x1234'),
        ('"\\u123456"', StringNode, '\u123456'),
        ('"\\U10234567"', StringNode, '\U0010234567'),
    ])
    def test_atom(self, s, t, v):
        # on its own
        res = read_string(s)
        assert len(res) == 1
        assert isinstance(res[0], t)
        assert res[0].value == v
        # surrounded by whitespace
        res = read_string(f' {s} ')
        assert len(res) == 1
        assert isinstance(res[0], t)
        assert res[0].value == v
        # surrounded by parens
        res = read_string(f'({s})')
        assert len(res) == 1
        assert isinstance(res[0], GenericListNode)
        assert isinstance(res[0].items[0], t)
        assert res[0].items[0].value == v

    @pytest.mark.parametrize(('s', 'e'), [
        ('1abc', 'no whitespace'),
        ('-1abc', 'no whitespace'),
        ('-abc', 'no whitespace'),
        ('--', 'no whitespace'),
        ('@true@true', 'no whitespace'),
        ('@truer', 'no whitespace'),
        ('@falser', 'no whitespace'),
        ('@dunno', 'unknown token'),
        ('@tru', 'unknown token'),
        ('0123', 'no whitespace'),
        ('123l', 'no whitespace'),
        ('3\'0b1000', 'value out of range'),
        ('3\'-0b1001', 'value out of range'),
        ('12\'0x(-123-456)', 'no whitespace'),
        ('12\'0x(-1001)', 'value out of range'),
        ('12\'0x(1000)', 'value out of range'),
        ('12\'0x(12z)', 'no whitespace'),
        ('12\'(0123)', 'no whitespace'),
        ('12\'0x(', 'EOF while in BINARRAY state'),
        ('12\'0x(123', 'EOF while in BINARRAY state'),
        ('12\'(@true)', 'unknown binarray item'),
        ('12\'"abc', 'EOF while in STRING state'),
        ('"abc', 'EOF while in STRING state'),
        ('"', 'EOF while in STRING state'),
        ('6\'"abc"', 'character code out of range'),
        ('"abc\\U123456"', 'not a valid unicode codepoint'),
        ('"\\d"', 'unknown escape'),
        ('"\\x1"', 'unknown escape'),
        ('"\\u123"', 'unknown escape'),
        ('"\\U12345"', 'unknown escape'),
        ('"\\x1z"', 'unknown escape'),
        ('"\\u123z"', 'unknown escape'),
        ('"\\U12345z"', 'unknown escape'),
        ('(', 'unmatched opening paren'),
        (')', 'unmatched closing paren'),
        ('()()', 'no whitespace'),
        ('##', 'unclosed S-expr comment'),
        ('(abc ##) def', 'unclosed S-expr comment'),
    ])
    def test_fails(self, s, e):
        with pytest.raises(ReadError) as ei:
            read_string(s)
        assert ei.match(e)

    @pytest.mark.parametrize(('s', 'v'), [
        ('(abc def) ghi', [
            GenericListNode([
                SymbolNode(Symbol('abc')),
                SymbolNode(Symbol('def')),
            ]),
            SymbolNode(Symbol('ghi')),
        ]),
        ('(abc def (ghi ##jkl) ##(mno ## pqr stq) uvw)', [
            GenericListNode([
                SymbolNode(Symbol('abc')),
                SymbolNode(Symbol('def')),
                GenericListNode([
                    SymbolNode(Symbol('ghi')),
                ]),
                SymbolNode(Symbol('uvw')),
            ]),
        ]),
        ('''
            (abc def (ghi # jkl mno )(
            pqr) # (mno ## pqr stq) uvw)
            )
        ''', [
            GenericListNode([
                SymbolNode(Symbol('abc')),
                SymbolNode(Symbol('def')),
                GenericListNode([
                    SymbolNode(Symbol('ghi')),
                    SymbolNode(Symbol('pqr')),
                ]),
            ]),
        ]),
    ])
    def test_list(self, s, v):
        a = read_string(s)
        assert a == v

    @pytest.mark.parametrize('t', [
        Symbol('a'),
        Symbol('+'),
        Symbol('-'),
        Symbol('*'),
        Symbol('/'),
        Symbol('%'),
        Symbol('_'),
        Symbol('='),
        Symbol('>='),
        Symbol('<='),
        Symbol('$'),
        Symbol('abc!'),
        Symbol('abc?'),
        None,
        True,
        False,
        123,
        0,
        -123,
        BinWord(12, 0x123),
        BinWord(11, 0x7ff),
        BinWord(13, 0x1fff),
        BinWord(13, 0),
        BinWord(0, 0),
        BinArray(width=0),
        BinArray(width=33),
        BinArray([1, 2, 3], width=123),
        BinArray([0, 0], width=0),
        BinArray([0, 0x1fffd], width=17),
        'abc',
        '\x0000\x1234\u111234\U0010101010',
        ['a', 'b', ['c', 'd', 'e'], True, 123],
        ''.join(chr(x) for x in range(0x200)),
        ''.join(chr(x) for x in range(0, 0x110000, 0x100)),
        ''.join(chr(x) for x in range(0xff, 0x110000, 0x100)),
    ])
    def test_roundtrip(self, t):
        n = GenericNode(t)
        assert read_string(str(n)) == [n]

    def test_location(self):
        a = read_string(textwrap.dedent("""\
            (abc def # abc
              (ghi 123 12'(12 # meh
                 34 # meh
                 56)
                 "abc # meh
                 def"
              )
            )
        """).strip())
        assert a[0].location == TextLocationRange('<string>', 1, 1, 8, 1)
        assert (a[0].items[0].location ==
                TextLocationRange('<string>', 1, 2, 1, 4))
        assert (a[0].items[1].location ==
                TextLocationRange('<string>', 1, 6, 1, 8))
        assert (a[0].items[2].location ==
                TextLocationRange('<string>', 2, 3, 7, 3))
        assert (a[0].items[2].items[0].location ==
                TextLocationRange('<string>', 2, 4, 2, 6))
        assert (a[0].items[2].items[1].location ==
                TextLocationRange('<string>', 2, 8, 2, 10))
        assert (a[0].items[2].items[2].location ==
                TextLocationRange('<string>', 2, 12, 4, 8))
        assert (a[0].items[2].items[3].location ==
                TextLocationRange('<string>', 5, 6, 6, 9))
