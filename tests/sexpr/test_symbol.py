import pytest

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
        with pytest.raises(TypeError):
            Symbol(123)

    @pytest.mark.parametrize('name', [
        'abc',
        'def',
        'ABC',
        'a123',
        'abc-def',
        'abc_def',
        '-',
        '*',
        '+',
        '/',
        '%',
        '**',
        '<=',
        '>=',
        '!=',
        '=',
        'abc?',
        '$abc$',
    ])
    def test_valid(self, name):
        Symbol(name)

    @pytest.mark.parametrize('name', [
        '',
        '\x01',
        'abc def',
        '123',
        '1abc',
        '-1',
        '-abc',
        '--',
        '.',
        '\n',
    ])
    def test_invalid(self, name):
        with pytest.raises(ValueError):
            Symbol(name)
