import unittest
import pytest

from binflakes.types import BinWord, BinInt


class TestBinWord(unittest.TestCase):
    def test_construct(self):
        a = BinWord(0, 0)
        assert a.width == 0
        assert a.to_uint() == 0
        assert a.to_sint() == 0
        assert a.mask == 0
        assert int(a) == 0
        a = BinWord(12, 0)
        assert a.width == 12
        assert a.to_uint() == 0
        assert a.to_sint() == 0
        assert a.mask == 0xfff
        assert int(a) == 0
        a = BinWord(12, 0x123)
        assert a.width == 12
        assert a.to_uint() == 0x123
        assert a.to_sint() == 0x123
        assert a.mask == 0xfff
        assert int(a) == 0x123
        a = BinWord(12, 0xfff)
        assert a.width == 12
        assert a.to_uint() == 0xfff
        assert a.to_sint() == -1
        assert a.mask == 0xfff
        assert int(a) == 0xfff
        a = BinWord(12, 0x1234, trunc=True)
        assert a.width == 12
        assert a.to_uint() == 0x234
        assert a.to_sint() == 0x234
        assert a.mask == 0xfff
        assert int(a) == 0x234
        a = BinWord(12, -1, trunc=True)
        assert a.width == 12
        assert a.to_uint() == 0xfff
        assert a.to_sint() == -1
        assert a.mask == 0xfff
        assert int(a) == 0xfff
        assert isinstance(a.to_uint(), BinInt)
        assert isinstance(a.to_sint(), BinInt)
        assert isinstance(a.mask, BinInt)
        with pytest.raises(ValueError):
            BinWord(12, 0x1000)
        with pytest.raises(ValueError):
            BinWord(12, 0x1234)
        with pytest.raises(ValueError):
            BinWord(12, -1)
        with pytest.raises(ValueError):
            BinWord(-1, 0)
        with pytest.raises(TypeError):
            BinWord(12.0, 0)
        with pytest.raises(TypeError):
            BinWord(object(), 0)
        with pytest.raises(TypeError):
            BinWord(12, object())

    def test_display(self):
        a = BinWord(0, 0)
        assert str(a) == '#0x0'
        assert repr(a) == 'BinWord(0, 0x0)'
        a = BinWord(1, 1)
        assert str(a) == '#1x1'
        assert repr(a) == 'BinWord(1, 0x1)'
        a = BinWord(4, 0xd)
        assert str(a) == '#4xd'
        assert repr(a) == 'BinWord(4, 0xd)'
        a = BinWord(13, 0x1234)
        assert str(a) == '#13x1234'
        assert repr(a) == 'BinWord(13, 0x1234)'
        a = BinWord(13, 0)
        assert str(a) == '#13x0000'
        assert repr(a) == 'BinWord(13, 0x0000)'
        a = BinWord(12, 0)
        assert str(a) == '#12x000'
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
        assert a.extr(0, 4) == BinWord(4, 0x3)
        assert a.extr(4, 4) == BinWord(4, 0x2)
        assert a.extr(8, 4) == BinWord(4, 0x1)
        assert a.extr(8, 0) == BinWord(0, 0x0)
        assert a.extr(BinWord(4, 4), BinWord(10, 4)) == BinWord(4, 0x2)
        with pytest.raises(ValueError):
            a.extr(9, 4)
        with pytest.raises(ValueError):
            a.extr(-1, 4)
        with pytest.raises(ValueError):
            a.extr(4, -1)
        with pytest.raises(TypeError):
            a.extr(object(), -1)
        with pytest.raises(TypeError):
            a.extr(0, object())

    def test_bool(self):
        a = BinWord(0, 0)
        assert not a
        a = BinWord(1, 0)
        assert not a
        a = BinWord(1, 1)
        assert a
        a = BinWord(12, 0)
        assert not a
        a = BinWord(12, 1)
        assert a
        a = BinWord(12, 2)
        assert a
        a = BinWord(12, -1, trunc=True)
        assert a
        a = BinWord(12, 0x800)
        assert a

    def test_arith(self):
        a = BinWord(12, 0x123)
        b = BinWord(12, 0x456)
        c = BinWord(12, 0xabc)
        d = BinWord(12, 0xdef)
        e = BinWord(11, 0x123)
        assert a + b == BinWord(12, 0x579)
        assert a + c == BinWord(12, 0xbdf)
        assert b + d == BinWord(12, 0x245)
        with pytest.raises(ValueError):
            a + e
        with pytest.raises(TypeError):
            a + 0x123
        with pytest.raises(TypeError):
            0x123 + a
        with pytest.raises(TypeError):
            a + object()
        with pytest.raises(TypeError):
            object() + a
        assert a - b == BinWord(12, 0xccd)
        assert b - a == BinWord(12, 0x333)
        assert a - c == BinWord(12, 0x667)
        assert b - d == BinWord(12, 0x667)
        with pytest.raises(ValueError):
            a - e
        with pytest.raises(TypeError):
            a - 0x123
        with pytest.raises(TypeError):
            0x123 - a
        with pytest.raises(TypeError):
            a - object()
        with pytest.raises(TypeError):
            object() - a
        assert a * b == BinWord(12, 0xdc2)
        assert a * c == BinWord(12, 0x3b4)
        assert b * d == BinWord(12, 0xa4a)
        with pytest.raises(ValueError):
            a * e
        with pytest.raises(TypeError):
            a * 0x123
        with pytest.raises(TypeError):
            0x123 * a
        with pytest.raises(TypeError):
            a * object()
        with pytest.raises(TypeError):
            object() * a
        assert -a == BinWord(12, 0xedd)
        assert -b == BinWord(12, 0xbaa)
        assert -c == BinWord(12, 0x544)
        assert -d == BinWord(12, 0x211)
        assert -e == BinWord(11, 0x6dd)

    def test_bitop(self):
        a = BinWord(12, 0x123)
        b = BinWord(12, 0x456)
        c = BinWord(12, 0xabc)
        d = BinWord(12, 0xdef)
        e = BinWord(11, 0x123)
        assert a & b == BinWord(12, 0x002)
        assert a & c == BinWord(12, 0x020)
        assert b & d == BinWord(12, 0x446)
        with pytest.raises(ValueError):
            a & e
        with pytest.raises(TypeError):
            a & 0x123
        with pytest.raises(TypeError):
            0x123 & a
        with pytest.raises(TypeError):
            a & object()
        with pytest.raises(TypeError):
            object() & a
        assert a | b == BinWord(12, 0x577)
        assert a | c == BinWord(12, 0xbbf)
        assert b | d == BinWord(12, 0xdff)
        with pytest.raises(ValueError):
            a | e
        with pytest.raises(TypeError):
            a | 0x123
        with pytest.raises(TypeError):
            0x123 | a
        with pytest.raises(TypeError):
            a | object()
        with pytest.raises(TypeError):
            object() | a
        assert a ^ b == BinWord(12, 0x575)
        assert a ^ c == BinWord(12, 0xb9f)
        assert b ^ d == BinWord(12, 0x9b9)
        with pytest.raises(ValueError):
            a ^ e
        with pytest.raises(TypeError):
            a ^ 0x123
        with pytest.raises(TypeError):
            0x123 ^ a
        with pytest.raises(TypeError):
            a ^ object()
        with pytest.raises(TypeError):
            object() ^ a
        assert ~a == BinWord(12, 0xedc)
        assert ~b == BinWord(12, 0xba9)
        assert ~c == BinWord(12, 0x543)
        assert ~d == BinWord(12, 0x210)
        assert ~e == BinWord(11, 0x6dc)

    def test_shift(self):
        a = BinWord(12, 0x123)
        b = BinWord(12, 0xabc)
        assert a << 0 == a
        assert b << 0 == b
        assert a << 1 == BinWord(12, 0x246)
        assert b << 1 == BinWord(12, 0x578)
        assert a << 4 == BinWord(12, 0x230)
        assert b << 4 == BinWord(12, 0xbc0)
        assert a << 2**128 == BinWord(12, 0x000)
        assert b << 2**128 == BinWord(12, 0x000)
        assert a << BinWord(10, 2) == BinWord(12, 0x48c)
        assert b << BinWord(10, 2) == BinWord(12, 0xaf0)
        assert a << BinWord(128, 2**127) == BinWord(12, 0x000)
        assert b << BinWord(128, 2**127) == BinWord(12, 0x000)
        with pytest.raises(TypeError):
            a << object()
        with pytest.raises(ValueError):
            a << -1
        assert a >> 0 == a
        assert b >> 0 == b
        assert a >> 1 == BinWord(12, 0x091)
        assert b >> 1 == BinWord(12, 0x55e)
        assert a >> 4 == BinWord(12, 0x012)
        assert b >> 4 == BinWord(12, 0x0ab)
        assert a >> 2**128 == BinWord(12, 0x000)
        assert b >> 2**128 == BinWord(12, 0x000)
        assert a >> BinWord(10, 2) == BinWord(12, 0x048)
        assert b >> BinWord(10, 2) == BinWord(12, 0x2af)
        assert a >> BinWord(128, 2**127) == BinWord(12, 0x000)
        assert b >> BinWord(128, 2**127) == BinWord(12, 0x000)
        with pytest.raises(TypeError):
            a >> object()
        with pytest.raises(ValueError):
            a >> -1
        assert a.sar(0) == a
        assert b.sar(0) == b
        assert a.sar(1) == BinWord(12, 0x091)
        assert b.sar(1) == BinWord(12, 0xd5e)
        assert a.sar(4) == BinWord(12, 0x012)
        assert b.sar(4) == BinWord(12, 0xfab)
        assert a.sar(2**128) == BinWord(12, 0x000)
        assert b.sar(2**128) == BinWord(12, 0xfff)
        assert a.sar(BinWord(10, 2)) == BinWord(12, 0x048)
        assert b.sar(BinWord(10, 2)) == BinWord(12, 0xeaf)
        assert a.sar(BinWord(128, 2**127)) == BinWord(12, 0x000)
        assert b.sar(BinWord(128, 2**127)) == BinWord(12, 0xfff)
        with pytest.raises(TypeError):
            a.sar(object())
        with pytest.raises(ValueError):
            a.sar(-1)

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

    def test_insrt(self):
        a = BinWord(12, 0x123)
        assert a.insrt(0, BinWord(4, 0x5)) == BinWord(12, 0x125)
        assert a.insrt(4, BinWord(4, 0x5)) == BinWord(12, 0x153)
        assert a.insrt(8, BinWord(4, 0x5)) == BinWord(12, 0x523)
        with pytest.raises(TypeError):
            a.insrt(0, 5)
        with pytest.raises(ValueError):
            a.insrt(-1, BinWord(4, 0x5))
        with pytest.raises(ValueError):
            a.insrt(9, BinWord(4, 0x5))
