import pytest

from binflakes.types import BinInt, BinWord, BinArray
from binflakes.sexpr.location import TextLocationRange
from binflakes.sexpr.symbol import Symbol
from binflakes.sexpr.nodes import (
    Node, GenericListNode, SymbolNode, NilNode, BoolNode, IntNode, WordNode,
    ArrayNode, StringNode, ListNode, GenericNode, FormNode, ConvertError,
    AlternativesNode, form_node, form_arg, form_optional_arg, form_rest_arg,
)


@form_node
class MyFormNode(FormNode):
    symbol = Symbol('my-form')
    arg1 = form_arg(IntNode)
    arg2 = form_arg(BoolNode)
    arg3 = form_optional_arg(StringNode)
    rest = form_rest_arg(WordNode)


@form_node
class MyConflictingFormNode(FormNode):
    symbol = Symbol('my-form')
    arg1 = form_arg(ArrayNode)


@form_node
class MyOtherFormNode(FormNode):
    symbol = Symbol('my-other-form')


class MyIntNode(IntNode):
    __slots__ = ()


class MyListNode(ListNode):
    __slots__ = ()

    item_type = MyIntNode


class MyAlternativesNode(AlternativesNode):
    alternatives = [
        MyFormNode,
        MyOtherFormNode,
    ]


class BetterAlternativesNode(AlternativesNode):
    pass


BetterAlternativesNode.set_alternatives([
    MyAlternativesNode,
    MyIntNode,
])


class UninitializedAlternativesNode(AlternativesNode):
    pass


class TestNodes:
    def test_base_constructor(self):
        with pytest.raises(NotImplementedError):
            Node(123)

    def test_isinstance(self):
        assert isinstance(BoolNode(True), GenericNode)
        assert not isinstance(BoolNode(True), AlternativesNode)
        mfn = MyFormNode(arg1=IntNode(BinInt(123)), arg2=BoolNode(True))
        assert not isinstance(mfn, GenericNode)

    def test_uninitialized_alternatives(self):
        with pytest.raises(RuntimeError):
            UninitializedAlternativesNode(123)

    def test_list(self):
        a = GenericListNode([
            NilNode(), BoolNode(True), GenericListNode([]),
            IntNode(BinInt(123)),
        ])
        assert str(a) == '(@nil @true () 123)'
        with pytest.raises(TypeError):
            GenericListNode([123.5])
        with pytest.raises(ConvertError):
            GenericListNode('abc')
        with pytest.raises(ConvertError):
            GenericListNode(123)
        b = GenericNode([None, True, (), 123])
        assert a == b

    @pytest.mark.parametrize(('val', 'node_type', 'res'), [
        (Symbol('abc'), SymbolNode, 'abc'),
        (None, NilNode, '@nil'),
        (True, BoolNode, '@true'),
        (False, BoolNode, '@false'),
        (123, IntNode, '123'),
        (0x456, IntNode, '1110'),
        (BinInt(0x456), IntNode, '1110'),
        (BinWord(13, 0x1234), WordNode, '13\'0x1234'),
        (BinWord(0, 0), WordNode, '0\'0x0'),
        (BinArray([0x1234, 0x567], width=13), ArrayNode, '13\'0x(1234 0567)'),
        (BinArray([0, 0], width=0), ArrayNode, '0\'0x(0 0)'),
        (BinArray(width=123), ArrayNode, '123\'0x()'),
        ('\a\bcd\x1b\f', StringNode, '"\\a\\bcd\\e\\f"'),
    ])
    def test_atom(self, val, node_type, res):
        loc = TextLocationRange('abc', 1, 2, 3, 4)
        a = node_type(val)
        assert str(a) == res
        b = GenericNode(val)
        assert a == b
        c = GenericNode(val, loc)
        assert a == c
        assert c.location == loc
        d = node_type(val, loc)
        assert a == d
        assert d.location == loc
        e = node_type(c)
        assert a == e
        assert e.location == loc
        f = GenericNode(c)
        assert a == f
        assert f.location == loc
        with pytest.raises(TypeError):
            node_type(a, loc)
        with pytest.raises(TypeError):
            GenericNode(a, loc)

    @pytest.mark.parametrize(('val', 'node_type'), [
        (True, IntNode),
        (1, BoolNode),
        ('abc', IntNode),
        (13, StringNode),
        (13, GenericListNode),
    ])
    def test_wrong_type(self, val, node_type):
        with pytest.raises(ConvertError):
            node_type(val)

    def test_nil(self):
        a = NilNode()
        assert str(a) == '@nil'
        b = GenericNode(None)
        assert a == b

    def test_generic_node(self):
        with pytest.raises(TypeError):
            GenericNode({})
        with pytest.raises(TypeError):
            GenericNode(1.5)

    def test_to_list(self):
        loc = TextLocationRange('abc', 1, 2, 3, 4)
        loc2 = TextLocationRange('def', 5, 6, 7, 8)
        a = MyFormNode(
                arg1=123,
                arg2=True,
                arg3='abc',
                rest=(BinWord(12, 0x123),),
                location=loc, symbol_location=loc2,
            )
        b = MyFormNode([
            SymbolNode(Symbol('my-form'), location=loc),
            123, True, 'abc', BinWord(12, 0x123),
        ], location=loc2)
        assert a.location == loc
        assert a.symbol_location == loc2
        assert a.to_list()[0].location == loc2
        assert b.location == loc2
        assert b.symbol_location == loc
        assert b.to_list()[0].location == loc
        assert a == b
        assert a.arg1 == IntNode(123)
        assert a.arg2 == BoolNode(True)
        assert a.arg3 == StringNode('abc')
        assert a.rest == (WordNode(BinWord(12, 0x123)),)
        al = a.to_list()
        assert al == (
            SymbolNode(Symbol('my-form')),
            IntNode(123),
            BoolNode(True),
            StringNode('abc'),
            WordNode(BinWord(12, 0x123)),
        )
        al = GenericNode(a)
        assert al == GenericNode([
            Symbol('my-form'),
            123,
            True,
            'abc',
            BinWord(12, 0x123),
        ])
        assert str(a) == '(my-form 123 @true "abc" 12\'0x123)'
        c = MyOtherFormNode()
        cl = (SymbolNode(Symbol('my-other-form')),)
        assert c.to_list() == cl
        c = MyOtherFormNode([Symbol('my-other-form')])
        assert c.to_list() == cl
        d = MyFormNode(
                arg1=456,
                arg2=False,
            )
        assert d.to_list() == (
            SymbolNode(Symbol('my-form')),
            IntNode(456),
            BoolNode(False),
        )
        assert d.arg3 is None
        assert d.rest == ()
        assert str(d) == '(my-form 456 @false)'
        e = MyFormNode(
                arg1=456,
                arg2=False,
                arg3=None,
            )
        assert d == e
        f = MyFormNode([Symbol('my-form'), 456, False])
        assert d == f
        g = MyAlternativesNode([Symbol('my-other-form')])
        assert c == g
        h = BetterAlternativesNode([Symbol('my-other-form')])
        assert c == h
        i = BetterAlternativesNode(123)
        assert i == MyIntNode(123)

    def test_form_errors(self):
        with pytest.raises(RuntimeError):
            FormNode()
        with pytest.raises(ConvertError) as err:
            MyFormNode(123)
        assert 'expected a list' in str(err)
        with pytest.raises(ConvertError) as err:
            MyFormNode([])
        assert 'empty form' in str(err)
        with pytest.raises(ConvertError) as err:
            MyFormNode([123])
        assert 'must start with a symbol' in str(err)
        with pytest.raises(ConvertError) as err:
            MyFormNode([Symbol('not-my-form')])
        assert 'expected form (my-form)' in str(err)
        with pytest.raises(ConvertError) as err:
            MyFormNode([Symbol('my-form')])
        assert 'too few arguments to form my-form' in str(err)
        with pytest.raises(ConvertError) as err:
            MyOtherFormNode([Symbol('my-other-form'), 123])
        assert 'too many arguments to form my-other-form' in str(err)
        with pytest.raises(TypeError):
            MyFormNode([Symbol('my-form'), 123, True], arg1=123)
        with pytest.raises(TypeError):
            MyFormNode([Symbol('my-form'), 123, True], rest=())
        with pytest.raises(TypeError) as err:
            MyFormNode()
        assert 'no value for arg1' in str(err)
        with pytest.raises(TypeError) as err:
            MyFormNode(arg1=123, arg2=True, rest=[BinWord(0, 0)])
        assert 'passing argument after a missing argument' in str(err)
        with pytest.raises(TypeError) as err:
            MyFormNode(arg1=123, arg2=True, meh=True)
        assert 'unknown field meh' in str(err)

        with pytest.raises(RuntimeError) as err:
            @form_node
            class A(FormNode):
                symbol = Symbol('a')
                a = form_rest_arg(IntNode)
                b = form_rest_arg(WordNode)
        assert 'rest argument must be last' in str(err)

        with pytest.raises(RuntimeError) as err:
            @form_node
            class B(FormNode):
                symbol = Symbol('b')
                a = form_optional_arg(IntNode)
                b = form_arg(WordNode)
        assert 'required arg after optional arg' in str(err)

    def test_alternatives_errors(self):
        with pytest.raises(ConvertError) as err:
            MyAlternativesNode(123)
        assert 'IntNode not allowed' in str(err)
        with pytest.raises(ConvertError) as err:
            MyAlternativesNode([])
        assert 'empty form' in str(err)
        with pytest.raises(ConvertError) as err:
            MyAlternativesNode([123])
        assert 'form must start with a symbol' in str(err)
        with pytest.raises(ConvertError) as err:
            MyAlternativesNode([SymbolNode(Symbol('not-my-form'))])
        assert 'unknown form not-my-form' in str(err)
        assert 'available forms: my-form, my-other-form' in str(err)

        class A(AlternativesNode):
            pass

        A.set_alternatives([IntNode])
        with pytest.raises(RuntimeError):
            A.set_alternatives([IntNode])

        class B(AlternativesNode):
            pass

        with pytest.raises(RuntimeError):
            B.set_alternatives([IntNode, MyIntNode])

        class C(AlternativesNode):
            pass

        with pytest.raises(RuntimeError):
            C.set_alternatives([GenericListNode, MyListNode])

        class D(AlternativesNode):
            pass

        with pytest.raises(RuntimeError):
            D.set_alternatives([GenericListNode, MyFormNode])

        class E(AlternativesNode):
            pass

        with pytest.raises(RuntimeError):
            E.set_alternatives([MyFormNode, MyConflictingFormNode])

        class F(AlternativesNode):
            pass

        with pytest.raises(RuntimeError):
            F.set_alternatives([Node])
