import unittest
import pytest

from binflakes.types import BinWord, BinInt


class TestBinInt(unittest.TestCase):
    def test_construct(self):
        a = BinInt(12)
        assert a == 12
        a = BinInt(BinWord(12, 0x123))
        assert a == 0x123
        a = BinInt(a)
        assert a == 0x123

    def test_display(self):
        a = BinInt(12)
        assert repr(a) == 'BinInt(12)'
        assert str(a) == '12'
        a = BinInt(-12)
        assert repr(a) == 'BinInt(-12)'
        assert str(a) == '-12'

    def test_mask(self):
        a = BinInt.mask(12)
        assert isinstance(a, BinInt)
        assert a == 0xfff
        a = BinInt.mask(0)
        assert isinstance(a, BinInt)
        assert a == 0
        with pytest.raises(ValueError):
            a = BinInt.mask(-1)

    def test_index(self):
        a = BinInt(0x123)
        b = BinInt(-0x123)
        assert a[0] == BinWord(1, 1)
        assert a[1] == BinWord(1, 1)
        assert a[2] == BinWord(1, 0)
        assert a[3] == BinWord(1, 0)
        assert b[0] == BinWord(1, 1)
        assert b[1] == BinWord(1, 0)
        assert b[2] == BinWord(1, 1)
        assert b[3] == BinWord(1, 1)
        assert a[1337] == BinWord(1, 0)
        assert b[1337] == BinWord(1, 1)
        with pytest.raises(TypeError):
            a[object()]
        with pytest.raises(ValueError):
            a[-1]

    def test_slice(self):
        a = BinInt(0x123)
        b = BinInt(-0x123)
        assert a[:8] == BinWord(8, 0x23)
        assert b[:8] == BinWord(8, 0xdd)
        assert a[4:8] == BinWord(4, 2)
        assert b[4:8] == BinWord(4, 0xd)
        assert a[4:] == BinInt(0x12)
        assert b[4:] == BinInt(-0x13)
        assert a[:] == a
        assert b[:] == b
        assert b[4:4] == BinWord(0, 0)
        assert b[8:4] == BinWord(0, 0)
        assert isinstance(a[4:], BinInt)
        assert isinstance(a[:], BinInt)
        with pytest.raises(ValueError):
            a[-2:]
        with pytest.raises(ValueError):
            a[:-2]
        with pytest.raises(TypeError):
            a[object():]
        with pytest.raises(TypeError):
            a[:object()]
        assert a[:16:2] == BinWord(8, 0x11)
        assert b[:16:2] == BinWord(8, 0xef)
        assert a[1:16:2] == BinWord(8, 0x05)
        assert b[1:16:2] == BinWord(8, 0xfa)
        assert a[::2] == 0x11
        assert b[::2] == -0x11
        assert a[1::2] == 0x5
        assert b[1::2] == -0x6
        assert isinstance(a[::2], BinInt)
        assert b[16:1:2] == BinWord(0, 0)
        with pytest.raises(ValueError):
            a[::0]
        with pytest.raises(ValueError):
            a[1:2:0]
        with pytest.raises(ValueError):
            a[::-1]
        with pytest.raises(ValueError):
            a[:7:-1]
        assert a[7:0:-1] == BinWord(7, 0x44)
        assert b[7:0:-1] == BinWord(7, 0x3b)
        assert a[7::-1] == BinWord(8, 0xc4)
        assert b[7::-1] == BinWord(8, 0xbb)
        with pytest.raises(ValueError):
            a[::-2]
        with pytest.raises(ValueError):
            a[:7:-2]
        assert a[7:0:-2] == BinWord(4, 0xa)
        assert b[7:0:-2] == BinWord(4, 0x5)
        assert a[7::-2] == BinWord(4, 0xa)
        assert b[7::-2] == BinWord(4, 0x5)

    def test_extract(self):
        a = BinInt(0x123)
        b = BinInt(-0x123)
        assert a.extract(0, 4) == BinWord(4, 3)
        assert b.extract(0, 4) == BinWord(4, 0xd)
        assert a.extract(4, 4) == BinWord(4, 2)
        assert b.extract(4, 4) == BinWord(4, 0xd)
        assert a.extract(0, 0) == BinWord(0, 0)
        with pytest.raises(ValueError):
            a.extract(0, -1)
        with pytest.raises(ValueError):
            a.extract(-1, 4)
        with pytest.raises(TypeError):
            a.extract(object(), 4)
        with pytest.raises(TypeError):
            a.extract(0, object())

    def test_type(self):
        a = BinInt(1)
        assert isinstance(a + a, BinInt)
        assert isinstance(a + 1, BinInt)
        assert isinstance(1 + a, BinInt)
        assert isinstance(a - a, BinInt)
        assert isinstance(a - 1, BinInt)
        assert isinstance(1 - a, BinInt)
        assert isinstance(a // a, BinInt)
        assert isinstance(a // 1, BinInt)
        assert isinstance(1 // a, BinInt)
        assert isinstance(a % a, BinInt)
        assert isinstance(a % 1, BinInt)
        assert isinstance(1 % a, BinInt)
        assert isinstance(a * a, BinInt)
        assert isinstance(a * 1, BinInt)
        assert isinstance(1 * a, BinInt)
        assert isinstance(a & a, BinInt)
        assert isinstance(a & 1, BinInt)
        assert isinstance(1 & a, BinInt)
        assert isinstance(a | a, BinInt)
        assert isinstance(a | 1, BinInt)
        assert isinstance(1 | a, BinInt)
        assert isinstance(a ^ a, BinInt)
        assert isinstance(a ^ 1, BinInt)
        assert isinstance(1 ^ a, BinInt)
        assert isinstance(-a, BinInt)
        assert isinstance(~a, BinInt)
        assert isinstance(+a, BinInt)
        assert isinstance(abs(a), BinInt)
        assert isinstance(a << a, BinInt)
        assert isinstance(a << 1, BinInt)
        assert isinstance(a >> a, BinInt)
        assert isinstance(a >> 1, BinInt)
        with pytest.raises(TypeError):
            len(a)
        assert isinstance(BinInt.from_bytes(b'a', 'little'), BinInt)

    def test_ceildiv(self):
        assert BinInt(15).ceildiv(BinInt(8)) == 2
        assert BinInt(16).ceildiv(BinInt(8)) == 2
        assert BinInt(17).ceildiv(BinInt(8)) == 3
        assert BinInt(-15).ceildiv(BinInt(8)) == -1
        assert BinInt(-16).ceildiv(BinInt(8)) == -2
        assert BinInt(-17).ceildiv(BinInt(8)) == -2
        assert BinInt(15).ceildiv(BinInt(-8)) == -1
        assert BinInt(16).ceildiv(BinInt(-8)) == -2
        assert BinInt(17).ceildiv(BinInt(-8)) == -2
        assert BinInt(-15).ceildiv(BinInt(-8)) == 2
        assert BinInt(-16).ceildiv(BinInt(-8)) == 2
        assert BinInt(-17).ceildiv(BinInt(-8)) == 3

    def test_deposit(self):
        assert BinInt(0x123).deposit(0, BinWord(4, 0x5)) == 0x125
        assert BinInt(0x123).deposit(4, BinWord(4, 0x5)) == 0x153
        with pytest.raises(TypeError):
            BinInt(0x123).deposit(0, 5)
        with pytest.raises(ValueError):
            BinInt(0x123).deposit(-1, BinWord(4, 0x5))
