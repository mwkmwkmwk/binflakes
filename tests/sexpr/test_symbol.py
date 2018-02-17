from binflakes.sexpr.symbol import Symbol


class TestSymbol:
    def test_symbol(self):
        a = Symbol('abc')
        b = Symbol('abc')
        c = Symbol('def')
        assert a == b
        assert a != c
        assert a.name == 'abc'
        assert c.name == 'def'
        assert str(a) == 'abc'
        hash(a)
