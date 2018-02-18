import operator

import pytest

from binflakes.types import BinWord, BinInt


class _MakeSlice:
    """Dummy class to easily make slice objects"""

    def __getitem__(self, idx):
        return idx


_ = _MakeSlice()


class TestBinInt:
    @pytest.mark.parametrize(('a', 'b'), [
        (12, 12),
        (BinWord(12, 0x123), 0x123),
        (BinInt(0x123), 0x123),
    ])
    def test_construct(self, a, b):
        v = BinInt(a)
        assert v == b

    @pytest.mark.parametrize(('v', 'r', 's'), [
        (12, 'BinInt(12)', '12'),
        (-12, 'BinInt(-12)', '-12'),
    ])
    def test_display(self, v, r, s):
        a = BinInt(v)
        assert repr(a) == r
        assert str(a) == s

    @pytest.mark.parametrize(('a', 'r'), [
        (12, 0xfff),
        (2, 3),
        (1, 1),
        (0, 0),
    ])
    def test_mask(self, a, r):
        v = BinInt.mask(a)
        assert isinstance(v, BinInt)
        assert v == r

    def test_mask_negative(self):
        with pytest.raises(ValueError):
            BinInt.mask(-1)

    @pytest.mark.parametrize(('a', 'i', 'e'), [
        (0x123, 0, 1),
        (0x123, 1, 1),
        (0x123, 2, 0),
        (0x123, 3, 0),
        (0x123, 1337, 0),
        (-0x123, 0, 1),
        (-0x123, 1, 0),
        (-0x123, 2, 1),
        (-0x123, 3, 1),
        (-0x123, 1337, 1),
    ])
    def test_index(self, a, i, e):
        a = BinInt(a)
        assert a[i] == BinWord(1, e)

    def test_index_fail(self):
        a = BinInt(0x123)
        with pytest.raises(TypeError):
            a[object()]
        with pytest.raises(ValueError):
            a[-1]

    @pytest.mark.parametrize(('v', 'i', 'e'), [
        (0x123, _[4:], 0x12),
        (-0x123, _[4:], -0x13),
        (0x123, _[:], 0x123),
        (-0x123, _[:], -0x123),
        (0x123, _[::2], 0x11),
        (-0x123, _[::2], -0x11),
        (0x123, _[1::2], 0x5),
        (-0x123, _[1::2], -0x6),
    ])
    def test_slice_int(self, v, i, e):
        a = BinInt(v)
        r = a[i]
        assert r == e
        assert isinstance(r, BinInt)

    @pytest.mark.parametrize(('v', 'i', 'e'), [
        (0x123, _[:8], BinWord(8, 0x23)),
        (-0x123, _[:8], BinWord(8, 0xdd)),
        (0x123, _[4:8], BinWord(4, 2)),
        (-0x123, _[4:8], BinWord(4, 0xd)),
        (-0x123, _[4:4], BinWord(0, 0)),
        (-0x123, _[8:4], BinWord(0, 0)),
        (0x123, _[:16:2], BinWord(8, 0x11)),
        (-0x123, _[:16:2], BinWord(8, 0xef)),
        (0x123, _[1:16:2], BinWord(8, 0x05)),
        (-0x123, _[1:16:2], BinWord(8, 0xfa)),
        (-0x123, _[16:1:2], BinWord(0, 0)),
        (0x123, _[7:0:-1], BinWord(7, 0x44)),
        (-0x123, _[7:0:-1], BinWord(7, 0x3b)),
        (0x123, _[7::-1], BinWord(8, 0xc4)),
        (-0x123, _[7::-1], BinWord(8, 0xbb)),
        (0x123, _[7:0:-2], BinWord(4, 0xa)),
        (-0x123, _[7:0:-2], BinWord(4, 0x5)),
        (0x123, _[7::-2], BinWord(4, 0xa)),
        (-0x123, _[7::-2], BinWord(4, 0x5)),
    ])
    def test_slice_word(self, v, i, e):
        a = BinInt(v)
        r = a[i]
        assert r == e

    @pytest.mark.parametrize(('s', 'e'), [
        (_[-2:], ValueError),
        (_[:-2], ValueError),
        (_[:object()], TypeError),
        (_[object():], TypeError),
        (_[::0], ValueError),
        (_[1:2:0], ValueError),
        (_[::-1], ValueError),
        (_[:7:-1], ValueError),
        (_[::-2], ValueError),
        (_[:7:-2], ValueError),
    ])
    def test_slice_fail(self, s, e):
        a = BinInt(0x123)
        with pytest.raises(e):
            a[s]

    @pytest.mark.parametrize(('val', 'pos', 'width', 'res'), [
        (0x123, 0, 4, BinWord(4, 3)),
        (-0x123, 0, 4, BinWord(4, 0xd)),
        (0x123, 4, 4, BinWord(4, 2)),
        (-0x123, 4, 4, BinWord(4, 0xd)),
        (0x123, 0, 0, BinWord(0, 0)),
    ])
    def test_extract(self, val, pos, width, res):
        a = BinInt(val)
        assert a.extract(pos, width) == res

    @pytest.mark.parametrize(('pos', 'width', 'e'), [
        (0, -1, ValueError),
        (-1, 4, ValueError),
        (object(), 4, TypeError),
        (0, object(), TypeError),
    ])
    def test_extract_fail(self, pos, width, e):
        a = BinInt(0x123)
        with pytest.raises(e):
            a.extract(pos, width)

    @pytest.mark.parametrize('op', [
        operator.add,
        operator.sub,
        operator.mul,
        operator.floordiv,
        operator.mod,
        operator.and_,
        operator.or_,
        operator.xor,
    ])
    def test_type_binary(self, op):
        a = BinInt(1)
        assert isinstance(op(a, a), BinInt)
        assert isinstance(op(a, 1), BinInt)
        assert isinstance(op(1, a), BinInt)

    @pytest.mark.parametrize('op', [
        operator.neg,
        operator.pos,
        operator.invert,
        operator.abs,
    ])
    def test_type_unary(self, op):
        a = BinInt(1)
        assert isinstance(op(a), BinInt)

    @pytest.mark.parametrize('op', [
        operator.lshift,
        operator.rshift,
    ])
    def test_type_shift(self, op):
        a = BinInt(1)
        assert isinstance(op(a, a), BinInt)
        assert isinstance(op(a, 1), BinInt)

    def test_type_misc(self):
        a = BinInt(1)
        with pytest.raises(TypeError):
            len(a)
        assert isinstance(BinInt.from_bytes(b'a', 'little'), BinInt)

    @pytest.mark.parametrize(('a', 'b', 'r'), [
        (15, 8, 2),
        (16, 8, 2),
        (17, 8, 3),
        (-15, 8, -1),
        (-16, 8, -2),
        (-17, 8, -2),
        (15, -8, -1),
        (16, -8, -2),
        (17, -8, -2),
        (-15, -8, 2),
        (-16, -8, 2),
        (-17, -8, 3),
    ])
    def test_ceildiv(self, a, b, r):
        assert BinInt(a).ceildiv(BinInt(b)) == r

    @pytest.mark.parametrize(('val', 'pos', 'word', 'res'), [
        (0x123, 0, BinWord(4, 0x5), 0x125),
        (0x123, 4, BinWord(4, 0x5), 0x153),
    ])
    def test_deposit(self, val, pos, word, res):
        assert BinInt(val).deposit(pos, word) == res

    @pytest.mark.parametrize(('pos', 'word', 'e'), [
        (0, 5, TypeError),
        (-1, BinWord(4, 0x5), ValueError),
        (1.5, BinWord(4, 0x5), TypeError),
    ])
    def test_deposit_fail(self, pos, word, e):
        a = BinInt(0x123)
        with pytest.raises(e):
            a.deposit(pos, word)
