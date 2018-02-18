import operator

import pytest

from binflakes.types import BinWord, BinInt


class TestBinWord:
    @pytest.mark.parametrize((
        'width', 'val', 'trunc', 'uval', 'sval', 'mask',
    ), [
        (0, 0, False, 0, 0, 0),
        (12, 0, False, 0, 0, 0xfff),
        (12, 0x123, False, 0x123, 0x123, 0xfff),
        (12, 0xfff, False, 0xfff, -1, 0xfff),
        (12, 0x1234, True, 0x234, 0x234, 0xfff),
        (12, 0xabcd, True, 0xbcd, -0x433, 0xfff),
        (12, -1, True, 0xfff, -1, 0xfff),
    ])
    def test_construct(self, width, val, trunc, uval, sval, mask):
        a = BinWord(width, val, trunc=trunc)
        assert a.width == width
        assert a.to_uint() == uval
        assert a.to_sint() == sval
        assert a.mask == mask
        assert int(a) == uval
        assert isinstance(a.to_uint(), BinInt)
        assert isinstance(a.to_sint(), BinInt)
        assert isinstance(a.mask, BinInt)

    @pytest.mark.parametrize(('width', 'val', 'e'), [
        (12, 0x1000, ValueError),
        (12, 0x1234, ValueError),
        (12, -1, ValueError),
        (-1, 0, ValueError),
        (12.0, 0, TypeError),
        (object(), 0, TypeError),
        (12, 1.0, TypeError),
    ])
    def test_construct_fail(self, width, val, e):
        with pytest.raises(e):
            BinWord(width, val)

    def test_display(self):
        a = BinWord(0, 0)
        assert str(a) == '0\'0x0'
        assert repr(a) == 'BinWord(0, 0x0)'
        a = BinWord(1, 1)
        assert str(a) == '1\'0x1'
        assert repr(a) == 'BinWord(1, 0x1)'
        a = BinWord(4, 0xd)
        assert str(a) == '4\'0xd'
        assert repr(a) == 'BinWord(4, 0xd)'
        a = BinWord(13, 0x1234)
        assert str(a) == '13\'0x1234'
        assert repr(a) == 'BinWord(13, 0x1234)'
        a = BinWord(13, 0)
        assert str(a) == '13\'0x0000'
        assert repr(a) == 'BinWord(13, 0x0000)'
        a = BinWord(12, 0)
        assert str(a) == '12\'0x000'
        assert repr(a) == 'BinWord(12, 0x000)'

    def test_eq(self):
        a = BinWord(12, 0x123)
        b = BinWord(12, 0x123)
        assert a == b
        assert not a != b
        assert hash(a) == hash(b)
        b = BinWord(11, 0x123)
        assert not a == b
        assert a != b
        b = BinInt(0x123)
        assert not a == b
        assert a != b
        b = BinWord(12, 0x122)
        assert not a == b
        assert a != b

    def test_seq(self):
        a = BinWord(0, 0)
        assert len(a) == 0
        with pytest.raises(ValueError):
            a[0]
        with pytest.raises(ValueError):
            a[-1]
        with pytest.raises(ValueError):
            a[12]
        assert a[0:0] == BinWord(0, 0)
        assert a[:] == BinWord(0, 0)
        assert a[-13:13] == BinWord(0, 0)
        with pytest.raises(TypeError):
            a[object()]
        a = BinWord(12, 0x123)
        assert a[-4] == BinWord(1, 0x1)
        assert a[-3] == BinWord(1, 0x0)
        assert a[-2] == BinWord(1, 0x0)
        assert a[-1] == BinWord(1, 0x0)
        assert a[0] == BinWord(1, 0x1)
        assert a[1] == BinWord(1, 0x1)
        assert a[BinWord(17, 1)] == BinWord(1, 0x1)
        assert a[2] == BinWord(1, 0x0)
        assert a[11] == BinWord(1, 0x0)
        assert a[-12] == BinWord(1, 0x1)
        with pytest.raises(ValueError):
            a[12]
        with pytest.raises(ValueError):
            a[-13]
        assert a[:4] == BinWord(4, 0x3)
        assert a[4:8] == BinWord(4, 0x2)
        assert a[4:] == BinWord(8, 0x12)
        assert a[4:123] == BinWord(8, 0x12)
        assert a[4:-1] == BinWord(7, 0x12)
        assert a[2:2] == BinWord(0, 0x0)
        assert a[2:1] == BinWord(0, 0x0)
        assert a[::4] == BinWord(3, 0x5)
        assert a[1::4] == BinWord(3, 0x3)
        assert a[1:9:4] == BinWord(2, 0x3)
        assert a[1:10:4] == BinWord(3, 0x3)
        with pytest.raises(ValueError):
            a[1:10:0]
        with pytest.raises(TypeError):
            a[1:10:object()]
        with pytest.raises(TypeError):
            a[1:object()]
        with pytest.raises(TypeError):
            a[object():2]
        assert a[::-1] == BinWord(12, 0xc48)
        assert a[1:4:-1] == BinWord(0, 0)
        assert a[4:0:-1] == BinWord(4, 0x8)
        assert a[4::-1] == BinWord(5, 0x18)

    def test_extract(self):
        a = BinWord(12, 0x123)
        assert a.extract(0, 4) == BinWord(4, 0x3)
        assert a.extract(4, 4) == BinWord(4, 0x2)
        assert a.extract(8, 4) == BinWord(4, 0x1)
        assert a.extract(8, 0) == BinWord(0, 0x0)
        assert a.extract(BinWord(4, 4), BinWord(10, 4)) == BinWord(4, 0x2)
        with pytest.raises(ValueError):
            a.extract(9, 4)
        with pytest.raises(ValueError):
            a.extract(-1, 4)
        with pytest.raises(ValueError):
            a.extract(4, -1)
        with pytest.raises(TypeError):
            a.extract(object(), -1)
        with pytest.raises(TypeError):
            a.extract(0, object())

    @pytest.mark.parametrize(('v', 'b'), [
        (BinWord(0, 0), False),
        (BinWord(1, 0), False),
        (BinWord(1, 1), True),
        (BinWord(123, 0), False),
        (BinWord(123, 1), True),
        (BinWord(123, 2), True),
        (BinWord(123, -1, trunc=True), True),
        (BinWord(123, 1 << 122), True),
    ])
    def test_bool(self, v, b):
        assert bool(v) == b

    @pytest.mark.parametrize(('w', 'v', 'ri', 'rn'), [
        (12, 0x123, 0xedc, 0xedd),
        (12, 0x456, 0xba9, 0xbaa),
        (12, 0xabc, 0x543, 0x544),
        (12, 0xdef, 0x210, 0x211),
        (11, 0x123, 0x6dc, 0x6dd),
        (11, 0x7ff, 0x000, 0x001),
        (11, 0x000, 0x7ff, 0x000),
        (11, 0x001, 0x7fe, 0x7ff),
    ])
    def test_unary(self, w, v, ri, rn):
        v = BinWord(w, v)
        ri = BinWord(w, ri)
        rn = BinWord(w, rn)
        assert ~v == ri
        assert -v == rn

    @pytest.mark.parametrize((
        'w', 'a',  'b',   'rp',  'rm',  'rrm',  'rt',  'ra',  'ro',  'rx',
    ), [
        #                  a + b  a - b  b - a  a * b  a & b  a | b  a ^ b
        (12, 0x123, 0x456, 0x579, 0xccd, 0x333, 0xdc2, 0x002, 0x577, 0x575),
        (12, 0x123, 0xabc, 0xbdf, 0x667, 0x999, 0x3b4, 0x020, 0xbbf, 0xb9f),
        (12, 0x456, 0xdef, 0x245, 0x667, 0x999, 0xa4a, 0x446, 0xdff, 0x9b9),
    ])
    def test_binary(self, w, a, b, rp, rm, rrm, rt, ra, ro, rx):
        a = BinWord(w, a)
        b = BinWord(w, b)
        assert a + b == BinWord(w, rp)
        assert a - b == BinWord(w, rm)
        assert b - a == BinWord(w, rrm)
        assert a * b == BinWord(w, rt)
        assert a & b == BinWord(w, ra)
        assert a | b == BinWord(w, ro)
        assert a ^ b == BinWord(w, rx)

    @pytest.mark.parametrize('op', [
        operator.add,
        operator.sub,
        operator.mul,
        operator.and_,
        operator.or_,
        operator.xor,
    ])
    @pytest.mark.parametrize(('a', 'b', 'e'), [
        (BinWord(12, 0x123), BinWord(11, 0x123), ValueError),
        (BinWord(12, 0x123), 0x123, TypeError),
        (0x123, BinWord(12, 0x123), TypeError),
        (BinWord(12, 0x123), object(), TypeError),
        (object(), BinWord(12, 0x123), TypeError),
    ])
    def test_binary_fail(self, op, a, b, e):
        with pytest.raises(e):
            op(a, b)

    @pytest.mark.parametrize((
        'w', 'a', 's', 'rl', 'rr', 'ra',
    ), [
        #              <<     >>     sar
        (12, 0x123, 0, 0x123, 0x123, 0x123),
        (12, 0xabc, 0, 0xabc, 0xabc, 0xabc),
        (12, 0x123, 1, 0x246, 0x091, 0x091),
        (12, 0xabc, 1, 0x578, 0x55e, 0xd5e),
        (12, 0x123, 4, 0x230, 0x012, 0x012),
        (12, 0xabc, 4, 0xbc0, 0x0ab, 0xfab),
        (12, 0x123, 2**128, 0, 0, 0),
        (12, 0xabc, 2**128, 0, 0, 0xfff),
        (12, 0x123, BinWord(10, 2), 0x48c, 0x048, 0x048),
        (12, 0xabc, BinWord(10, 2), 0xaf0, 0x2af, 0xeaf),
        (12, 0x123, BinWord(128, 2**127), 0, 0, 0),
        (12, 0xabc, BinWord(128, 2**127), 0, 0, 0xfff),
    ])
    def test_shift(self, w, a, s, rl, rr, ra):
        a = BinWord(w, a)
        assert a << s == BinWord(w, rl)
        assert a >> s == BinWord(w, rr)
        assert a.sar(s) == BinWord(w, ra)

    @pytest.mark.parametrize('op', [
        operator.lshift,
        operator.rshift,
        BinWord.sar,
    ])
    @pytest.mark.parametrize(('shift', 'e'), [
        (1.0, TypeError),
        (-1, ValueError),
    ])
    def test_shift_fail(self, op, shift, e):
        a = BinWord(12, 0x123)
        with pytest.raises(e):
            op(a, shift)

    def test_cmp(self):
        a = BinWord(12, 0x123)
        b = BinWord(12, 0x456)
        c = BinWord(12, 0xabc)
        d = BinWord(13, 0xabc)
        assert not a < a
        assert a < b
        assert a < c
        assert not b < a
        assert not b < b
        assert b < c
        assert not c < a
        assert not c < b
        assert not c < c
        with pytest.raises(ValueError):
            a < d
        with pytest.raises(TypeError):
            a < 3
        assert a <= a
        assert a <= b
        assert a <= c
        assert not b <= a
        assert b <= b
        assert b <= c
        assert not c <= a
        assert not c <= b
        assert c <= c
        with pytest.raises(ValueError):
            a <= d
        with pytest.raises(TypeError):
            a <= 3
        assert not a > a
        assert not a > b
        assert not a > c
        assert b > a
        assert not b > b
        assert not b > c
        assert c > a
        assert c > b
        assert not c > c
        with pytest.raises(ValueError):
            a > d
        with pytest.raises(TypeError):
            a > 3
        assert a >= a
        assert not a >= b
        assert not a >= c
        assert b >= a
        assert b >= b
        assert not b >= c
        assert c >= a
        assert c >= b
        assert c >= c
        with pytest.raises(ValueError):
            a >= d
        with pytest.raises(TypeError):
            a >= 3
        assert not a.slt(a)
        assert a.slt(b)
        assert not a.slt(c)
        assert not b.slt(a)
        assert not b.slt(b)
        assert not b.slt(c)
        assert c.slt(a)
        assert c.slt(b)
        assert not c.slt(c)
        with pytest.raises(ValueError):
            a.slt(d)
        with pytest.raises(TypeError):
            a.slt(3)
        assert a.sle(a)
        assert a.sle(b)
        assert not a.sle(c)
        assert not b.sle(a)
        assert b.sle(b)
        assert not b.sle(c)
        assert c.sle(a)
        assert c.sle(b)
        assert c.sle(c)
        with pytest.raises(ValueError):
            a.sle(d)
        with pytest.raises(TypeError):
            a.sle(3)
        assert not a.sgt(a)
        assert not a.sgt(b)
        assert a.sgt(c)
        assert b.sgt(a)
        assert not b.sgt(b)
        assert b.sgt(c)
        assert not c.sgt(a)
        assert not c.sgt(b)
        assert not c.sgt(c)
        with pytest.raises(ValueError):
            a.sgt(d)
        with pytest.raises(TypeError):
            a.sgt(3)
        assert a.sge(a)
        assert not a.sge(b)
        assert a.sge(c)
        assert b.sge(a)
        assert b.sge(b)
        assert b.sge(c)
        assert not c.sge(a)
        assert not c.sge(b)
        assert c.sge(c)
        with pytest.raises(ValueError):
            a.sge(d)
        with pytest.raises(TypeError):
            a.sge(3)

    def test_ext(self):
        a = BinWord(12, 0x123)
        b = BinWord(12, 0xabc)
        assert a.sext(12) == a
        assert a.zext(12) == a
        assert b.sext(12) == b
        assert b.zext(12) == b
        with pytest.raises(ValueError):
            a.sext(11)
        with pytest.raises(ValueError):
            a.zext(11)
        with pytest.raises(TypeError):
            a.zext(object())
        with pytest.raises(TypeError):
            a.sext(object())
        assert a.sext(16) == BinWord(16, 0x0123)
        assert a.zext(16) == BinWord(16, 0x0123)
        assert b.sext(16) == BinWord(16, 0xfabc)
        assert b.zext(16) == BinWord(16, 0x0abc)
        assert b.sext(BinWord(11, 16)) == BinWord(16, 0xfabc)
        assert b.zext(BinWord(11, 16)) == BinWord(16, 0x0abc)

    def test_concat(self):
        a = BinWord(12, 0x123)
        b = BinWord(8, 0xab)
        c = BinWord(12, 0xdef)
        d = BinWord(0, 0)
        assert BinWord.concat(a, b, c) == BinWord(32, 0xdefab123)
        assert BinWord.concat(a, d, a, d, d, a) == BinWord(36, 0x123123123)
        assert BinWord.concat() == d
        assert BinWord.concat(a) == a
        with pytest.raises(TypeError):
            BinWord.concat(a, 12)
        with pytest.raises(TypeError):
            BinWord.concat(a, object())

    def test_deposit(self):
        a = BinWord(12, 0x123)
        assert a.deposit(0, BinWord(4, 0x5)) == BinWord(12, 0x125)
        assert a.deposit(4, BinWord(4, 0x5)) == BinWord(12, 0x153)
        assert a.deposit(8, BinWord(4, 0x5)) == BinWord(12, 0x523)
        with pytest.raises(TypeError):
            a.deposit(0, 5)
        with pytest.raises(ValueError):
            a.deposit(-1, BinWord(4, 0x5))
        with pytest.raises(ValueError):
            a.deposit(9, BinWord(4, 0x5))
