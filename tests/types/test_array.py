import random

import pytest

from binflakes.types import BinArray, BinWord


class TestBinArray:
    def test_construct(self):
        a = BinArray(width=12)
        assert len(a) == 0
        assert a.width == 12
        with pytest.raises(ValueError):
            BinArray(width=-1)
        a = BinArray(b'\x12\x34')
        assert len(a) == 2
        assert a.width == 8
        assert a[0] == BinWord(8, 0x12)
        assert a[1] == BinWord(8, 0x34)
        a = BinArray([0x123, 0x456], width=12)
        with pytest.raises(ValueError):
            BinArray([], width=-1)
        with pytest.raises(TypeError):
            BinArray([0x123])
        assert a[0] == BinWord(12, 0x123)
        assert a[1] == BinWord(12, 0x456)
        a = BinArray(width=12, length=3)
        assert len(a) == 3
        assert a.width == 12
        assert a[0] == BinWord(12, 0)
        with pytest.raises(ValueError):
            BinArray(width=12, length=-1)
        with pytest.raises(TypeError):
            BinArray()
        with pytest.raises(TypeError):
            BinArray(object())
        with pytest.raises(TypeError):
            BinArray(object(), width=12)
        with pytest.raises(TypeError):
            BinArray(width=object())
        with pytest.raises(TypeError):
            BinArray(width=12, length=object())
        with pytest.raises(TypeError):
            BinArray(12, width=12)
        with pytest.raises(TypeError):
            BinArray([0x123], width=12, length=1)
        a = BinArray([0, 1, 1, 0, 1, 0], width=1)
        assert len(a) == 6
        assert a.width == 1
        assert a[0] == BinWord(1, 0)
        assert a[1] == BinWord(1, 1)
        assert a[2] == BinWord(1, 1)
        assert a[3] == BinWord(1, 0)
        assert a[4] == BinWord(1, 1)
        assert a[5] == BinWord(1, 0)
        b = BinArray(a)
        assert a == b
        assert a is not b
        for width in range(2, 18):
            a = BinArray([0, 1, 2, 3, 3, 2], width=width)
            assert len(a) == 6
            assert a.width == width
            assert a[0] == BinWord(width, 0)
            assert a[1] == BinWord(width, 1)
            assert a[2] == BinWord(width, 2)
            assert a[3] == BinWord(width, 3)
            assert a[4] == BinWord(width, 3)
            assert a[5] == BinWord(width, 2)
        a = BinArray(width=0, length=12)
        assert len(a) == 12
        assert a.width == 0
        assert a[0] == BinWord(0, 0)
        assert a[11] == BinWord(0, 0)
        a = BinArray((x * 3 for x in range(6)), width=4)
        assert len(a) == 6
        assert a.width == 4
        assert a[0] == BinWord(4, 0)
        assert a[1] == BinWord(4, 3)
        assert a[2] == BinWord(4, 6)
        assert a[3] == BinWord(4, 9)
        assert a[4] == BinWord(4, 12)
        assert a[5] == BinWord(4, 15)

    def test_display(self):
        a = BinArray(width=0)
        assert repr(a) == 'BinArray([], width=0)'
        assert str(a) == '0\'0x()'
        a = BinArray(width=1)
        assert repr(a) == 'BinArray([], width=1)'
        assert str(a) == '1\'0x()'
        a = BinArray(width=13)
        assert repr(a) == 'BinArray([], width=13)'
        assert str(a) == '13\'0x()'
        a = BinArray(width=0, length=3)
        assert repr(a) == 'BinArray([0x0, 0x0, 0x0], width=0)'
        assert str(a) == '0\'0x(0 0 0)'
        a = BinArray([1, 0, 1, 1], width=1)
        assert repr(a) == 'BinArray([0x1, 0x0, 0x1, 0x1], width=1)'
        assert str(a) == '1\'0x(1 0 1 1)'
        a = BinArray([0x1234, 0x567, 0x89a, 0xbcd], width=13)
        assert (repr(a) ==
                'BinArray([0x1234, 0x0567, 0x089a, 0x0bcd], width=13)')
        assert str(a) == '13\'0x(1234 0567 089a 0bcd)'
        a = BinArray([0x123, 0x456, 0x789, 0xabc], width=12)
        assert repr(a) == 'BinArray([0x123, 0x456, 0x789, 0xabc], width=12)'
        assert str(a) == '12\'0x(123 456 789 abc)'

    def test_eq(self):
        a = BinArray([0x1, 0x2, 0x3], width=2)
        b = BinArray([0x1, 0x2, 0x3], width=2)
        c = BinArray([0x1, 0x2, 0x0], width=2)
        d = BinArray([0x1, 0x2, 0x3, 0x0], width=2)
        e = BinArray([0x1, 0x2, 0x3], width=3)
        f = BinArray(width=0)
        g = BinArray([0], width=0)
        h = BinArray(width=1)
        i = BinWord(1, 1)
        j = 1
        k = 'abc'
        assert a == b
        assert not a != b
        for x in [b, c, d, e, f, g, h, i, j, k]:
            for y in [b, c, d, e, f, g, h, i, j, k]:
                if x is y:
                    assert x == y
                    assert not x != y
                else:
                    assert x != y
                    assert not x == y

    def test_getitem(self):
        for width in range(1, 80):
            tries = 10 if width < 10 else 2
            for _ in range(tries):
                num = random.randrange(100, 128)
                data = [random.getrandbits(width) for _ in range(num)]
                a = BinArray(data, width=width)
                assert len(a) == len(data)
                for i in range(-len(a), len(a)):
                    assert a[i] == BinWord(width, data[i])
                for x, y in zip(a, data):
                    assert x == BinWord(width, y)
                with pytest.raises(IndexError):
                    a[-len(a)-1]
                with pytest.raises(IndexError):
                    a[len(a)]

    def test_setitem(self):
        for width in range(1, 80):
            num = random.randrange(100, 128)
            data = [random.getrandbits(width) for _ in range(num)]
            a = BinArray(data, width=width)
            for _ in range(10):
                idx = random.randrange(len(a))
                nval = random.getrandbits(width)
                data[idx] = nval
                if random.getrandbits(1):
                    nval = BinWord(width, nval)
                a[idx] = nval
                assert len(a) == len(data)
                for x, y in zip(a, data):
                    assert x == BinWord(width, y)
            with pytest.raises(ValueError):
                a[0] = BinWord(width+1, 0)
            with pytest.raises(TypeError):
                a[0] = object()
            with pytest.raises(IndexError):
                a[-len(a)-1] = 0
            with pytest.raises(IndexError):
                a[len(a)] = 0
            with pytest.raises(ValueError):
                a[0] = 1 << 100

    def test_getslice(self):
        a = BinArray([0x123, 0x456, 0x789, 0xabc, 0xdef], width=13)
        assert a[1:3] == BinArray([0x456, 0x789], width=13)
        assert a[1:1] == BinArray(width=13)
        assert a[3:1] == BinArray(width=13)
        assert a[:] == a
        assert a[:] is not a
        assert a[:3] == BinArray([0x123, 0x456, 0x789], width=13)
        assert a[3:] == BinArray([0xabc, 0xdef], width=13)
        assert a[1:3:-1] == BinArray(width=13)
        assert a[3:1:-1] == BinArray([0xabc, 0x789], width=13)
        assert a[3::-1] == BinArray([0xabc, 0x789, 0x456, 0x123], width=13)
        assert a[:1:-1] == BinArray([0xdef, 0xabc, 0x789], width=13)
        assert a[::-1] == BinArray([0xdef, 0xabc, 0x789, 0x456, 0x123],
                                   width=13)
        assert a[::3] == BinArray([0x123, 0xabc], width=13)
        assert a[1::3] == BinArray([0x456, 0xdef], width=13)
        assert a[2::3] == BinArray([0x789], width=13)
        assert a[::-3] == BinArray([0xdef, 0x456], width=13)
        assert a[1::-3] == BinArray([0x456], width=13)
        assert a[2::-3] == BinArray([0x789], width=13)
        assert a[3::-3] == BinArray([0xabc, 0x123], width=13)
        assert a[3:0:-3] == BinArray([0xabc], width=13)
        with pytest.raises(TypeError):
            a[object():]
        with pytest.raises(TypeError):
            a[:object()]

    def test_setslice(self):
        t = BinArray([0x123, 0x456, 0x789, 0xabc, 0xdef], width=13)
        a = t[:]
        a[1:3] = BinArray([0x1234, 0x1567], width=13)
        assert a == BinArray([0x123, 0x1234, 0x1567, 0xabc, 0xdef], width=13)
        with pytest.raises(TypeError):
            a[1:3] = [0x1234, 0x1567]
        with pytest.raises(ValueError):
            a[1:3] = BinArray([0x1234], width=13)
        with pytest.raises(ValueError):
            a[1:3] = BinArray([0x123, 0x456], width=12)
        a[1:1] = BinArray(width=13)
        a[3:1] = BinArray(width=13)
        a = t[:]
        a[3:1:-1] = BinArray([0x1234, 0x1567], width=13)
        assert a == BinArray([0x123, 0x456, 0x1567, 0x1234, 0xdef], width=13)
        a = t[:]
        a[::2] = BinArray([0x1234, 0x1567, 0x189a], width=13)
        assert a == BinArray([0x1234, 0x456, 0x1567, 0xabc, 0x189a], width=13)
        a = t[:]
        a[::-2] = BinArray([0x1234, 0x1567, 0x189a], width=13)
        assert a == BinArray([0x189a, 0x456, 0x1567, 0xabc, 0x1234], width=13)

    def test_bitop(self):
        a = BinArray([0x123, 0x456], width=13)
        b = BinArray([0x789, 0xabc], width=13)
        c = BinArray([0x123, 0x456, 0x789], width=13)
        d = BinArray([0x123, 0x456], width=12)
        assert (a & b) == BinArray([0x101, 0x014], width=13)
        assert (a | b) == BinArray([0x7ab, 0xefe], width=13)
        assert (a ^ b) == BinArray([0x6aa, 0xeea], width=13)
        with pytest.raises(ValueError):
            a & c
        with pytest.raises(ValueError):
            a & d
        with pytest.raises(TypeError):
            a & 3
        with pytest.raises(ValueError):
            a | c
        with pytest.raises(ValueError):
            a | d
        with pytest.raises(TypeError):
            a | 3
        with pytest.raises(ValueError):
            a ^ c
        with pytest.raises(ValueError):
            a ^ d
        with pytest.raises(TypeError):
            a ^ 3
        e = f = a[:]
        f &= b
        assert e is f
        assert f == (a & b)
        e = f = a[:]
        f |= b
        assert e is f
        assert f == (a | b)
        e = f = a[:]
        f ^= b
        assert e is f
        assert f == (a ^ b)
        with pytest.raises(ValueError):
            e &= c
        with pytest.raises(ValueError):
            e |= c
        with pytest.raises(ValueError):
            e ^= c
        with pytest.raises(ValueError):
            e &= d
        with pytest.raises(ValueError):
            e |= d
        with pytest.raises(ValueError):
            e ^= d
        with pytest.raises(TypeError):
            e &= 3
        with pytest.raises(TypeError):
            e |= 3
        with pytest.raises(TypeError):
            e ^= 3
        assert ~a == BinArray([0x1edc, 0x1ba9], width=13)

    def test_concat(self):
        a = BinArray([0x123, 0x456], width=13)
        b = BinArray([0x789, 0xabc, 0xdef], width=13)
        c = BinArray([0x123], width=12)
        d = BinArray(width=14)
        assert a + b == BinArray([0x123, 0x456, 0x789, 0xabc, 0xdef], width=13)
        assert b + a == BinArray([0x789, 0xabc, 0xdef, 0x123, 0x456], width=13)
        with pytest.raises(ValueError):
            a + c
        with pytest.raises(ValueError):
            a + d
        with pytest.raises(TypeError):
            a + 0x123
        with pytest.raises(TypeError):
            a + [0x123]
        with pytest.raises(TypeError):
            [0x123] + a
        with pytest.raises(TypeError):
            0x123 + a
        assert a * 0 == BinArray(width=13)
        assert a * 1 == a
        assert a * 2 == BinArray([0x123, 0x456, 0x123, 0x456], width=13)
        assert 3 * a == BinArray([
            0x123, 0x456, 0x123, 0x456, 0x123, 0x456,
        ], width=13)
        with pytest.raises(ValueError):
            -1 * a
        with pytest.raises(TypeError):
            object() * a

    def test_repack(self):
        a = BinArray(b'\x12\x34\x56\x78')
        b = BinArray([0x12, 0x03, 0x14, 0x05, 0x16], width=5)
        assert (a.repack(16, msb_first=True) ==
                BinArray([0x1234, 0x5678], width=16))
        assert (a.repack(16, msb_first=False) ==
                BinArray([0x3412, 0x7856], width=16))
        assert (a.repack(10, msb_first=False, start=1, start_bit=2) ==
                BinArray([0x18d, 0x385], width=10))
        assert (a.repack(10, msb_first=False, start=1, start_bit=2,
                         length=1) == BinArray([0x18d], width=10))
        assert (a.repack(10, msb_first=True, start=1, start_bit=2) ==
                BinArray([0x345, 0x19e], width=10))
        assert (b.repack(9, msb_first=False, start_bit=1) ==
                BinArray([0x039, 0x0b4], width=9))
        assert (b.repack(9, msb_first=True, start_bit=2) ==
                BinArray([0x087, 0x085], width=9))
        assert (b.repack(9, msb_first=True, length=0) ==
                BinArray([], width=9))
        assert (b.repack(9, msb_first=True, start=4) ==
                BinArray([], width=9))
        with pytest.raises(ValueError):
            a.repack(0, msb_first=True)
        with pytest.raises(ValueError):
            a.repack(-1, msb_first=True)
        with pytest.raises(TypeError):
            a.repack(2, msb_first='a')
        with pytest.raises(ValueError):
            a.repack(3, msb_first=True, start=-1)
        with pytest.raises(ValueError):
            a.repack(3, msb_first=True, length=-1)
        with pytest.raises(ValueError):
            a.repack(3, msb_first=True, length=11)
        with pytest.raises(ValueError):
            a.repack(3, msb_first=True, start=5)
        with pytest.raises(ValueError):
            a.repack(3, msb_first=True, start=4, start_bit=1)

    def test_repack_source_required(self):
        # As class method.
        assert BinArray.repack_source_required(8, 3, 0) == 0
        assert BinArray.repack_source_required(8, 3, 1) == 1
        assert BinArray.repack_source_required(8, 3, 2) == 1
        assert BinArray.repack_source_required(8, 3, 3) == 2
        assert BinArray.repack_source_required(8, 3, 4) == 2
        assert BinArray.repack_source_required(8, 3, 5) == 2
        assert BinArray.repack_source_required(8, 3, 6) == 3
        assert BinArray.repack_source_required(8, 3, 2, start_bit=0) == 1
        assert BinArray.repack_source_required(8, 3, 2, start_bit=2) == 1
        assert BinArray.repack_source_required(8, 3, 2, start_bit=3) == 2
        assert BinArray.repack_source_required(8, 3, 2, start_bit=7) == 2
        assert BinArray.repack_source_required(8, 3, 0, start_bit=1) == 1
        with pytest.raises(TypeError):
            BinArray.repack_source_required('8', 3, 1)
        with pytest.raises(TypeError):
            BinArray.repack_source_required(8, '3', 1)
        with pytest.raises(TypeError):
            BinArray.repack_source_required(8, 3, '1')
        with pytest.raises(TypeError):
            BinArray.repack_source_required(8, 3, 1, start_bit='1')
        with pytest.raises(ValueError):
            BinArray.repack_source_required(0, 3, 2)
        with pytest.raises(ValueError):
            BinArray.repack_source_required(-1, 3, 1)
        with pytest.raises(ValueError):
            BinArray.repack_source_required(8, 0, 1)
        with pytest.raises(ValueError):
            BinArray.repack_source_required(8, -1, 1)
        with pytest.raises(ValueError):
            BinArray.repack_source_required(8, 3, -1)
        with pytest.raises(ValueError):
            BinArray.repack_source_required(8, 3, 2, start_bit=-1)
        with pytest.raises(ValueError):
            BinArray.repack_source_required(8, 3, 2, start_bit=8)
        # As instance method.
        a = BinArray(width=8)
        assert a.repack_source_required(3, 0) == 0
        assert a.repack_source_required(3, 1) == 1
        assert a.repack_source_required(3, 5) == 2
        assert a.repack_source_required(3, 6) == 3
        assert a.repack_source_required(3, 5, start_bit=2) == 3

    def test_repack_data_available(self):
        # As class method.
        assert BinArray.repack_data_available(8, 3, src_length=0) == 0
        assert BinArray.repack_data_available(8, 3, src_length=1) == 2
        assert BinArray.repack_data_available(8, 3, src_length=2) == 5
        assert BinArray.repack_data_available(8, 3, src_length=2,
                                              start_bit=0) == 5
        assert BinArray.repack_data_available(8, 3, src_length=2,
                                              start_bit=1) == 5
        assert BinArray.repack_data_available(8, 3, src_length=2,
                                              start_bit=2) == 4
        assert BinArray.repack_data_available(8, 3, src_length=2,
                                              start_bit=7) == 3
        with pytest.raises(TypeError):
            BinArray.repack_data_available(8, 3)
        with pytest.raises(TypeError):
            BinArray.repack_data_available(8, 3, start=0)
        with pytest.raises(TypeError):
            BinArray.repack_data_available(8, 3, src_length=2, start=0)
        with pytest.raises(TypeError):
            BinArray.repack_data_available('8', 3, src_length=1)
        with pytest.raises(TypeError):
            BinArray.repack_data_available(8, '3', src_length=1)
        with pytest.raises(TypeError):
            BinArray.repack_data_available(8, 3, src_length='1')
        with pytest.raises(ValueError):
            BinArray.repack_data_available(0, 3, src_length=2)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(-1, 3, src_length=2)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(8, 0, src_length=2)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(8, -1, src_length=2)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(8, 3, src_length=-1)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(8, 3, src_length=2, start_bit=-1)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(8, 3, src_length=2, start_bit=8)
        with pytest.raises(ValueError):
            BinArray.repack_data_available(8, 3, src_length=0, start_bit=1)
        # As instance method.
        a = BinArray(width=8, length=3)
        assert a.repack_data_available(3) == 8
        assert a.repack_data_available(3, src_length=0) == 0
        assert a.repack_data_available(3, src_length=1) == 2
        assert a.repack_data_available(3, src_length=2) == 5
        assert a.repack_data_available(3, start=3) == 0
        assert a.repack_data_available(3, start=2) == 2
        assert a.repack_data_available(3, start=1) == 5
        assert a.repack_data_available(3, start_bit=0) == 8
        assert a.repack_data_available(3, start_bit=1) == 7
        assert a.repack_data_available(3, start=2, start_bit=2) == 2
        assert a.repack_data_available(3, start=2, start_bit=7) == 0
        with pytest.raises(TypeError):
            a.repack_data_available(3, start=0, src_length=3)
        with pytest.raises(ValueError):
            a.repack_data_available(3, start=-1)
        with pytest.raises(ValueError):
            a.repack_data_available(3, start=3, start_bit=1)
        with pytest.raises(ValueError):
            a.repack_data_available(3, start=4)
