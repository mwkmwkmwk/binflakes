import operator

# Possibly useful operations to be implemented later:
#
# - add/sub with carry
# - overflow predicates for add/sub
# - wide multiplication
#   - signed
#   - unsigned
# - division
#   - unsigned, floor
#   - unsigned, ceiling
#   - signed, floor
#   - signed, ceiling
#   - signed, to zero
# - modulus
#   - unsigned
#   - signed, result same sign as divisor (matching floor division)
#   - signed, matching round to 0 division
# - bit scans etc
#   - lowest bit set aka count trailing zeros
#   - count leading zeros
#   - count leading bits equal to sign
#   - highest bit set
#   - highest bit not equal to sign
# - population count
# - carry-less multiplication
# - polynomial reduction (CRCs etc)
#
# A few of these also apply to BinInt.


class BinWord:
    """A class representing a binary word value.  Its width (in bits) can be
    an arbitrary positive integer and is specified on creation.

    Values of this class are immutable once created.

    Most operations on BinWords treat them as two's complement numbers,
    complete with wrapping semantics (and require their widths to match).

    Can be treated as a sequence of individual bits (which are represented
    as BinWords of width 1), with bit 0 being the LSB and width-1 being
    the MSB.
    """

    __slots__ = '_width', '_val'

    def __init__(self, width, val, *, trunc=False):
        """Creates a word with a given width corresponding to a given
        unsigned integer value.

        If ``trunc`` is True, values out of range are masked to fit.
        Otherwise, it is an error to pass a value that doesn't fit in
        the given width.
        """
        width = operator.index(width)
        if width < 0:
            raise ValueError('width must not be negative')
        self._width = width
        val = BinInt(operator.index(val))
        if trunc:
            val &= self.mask
        elif val & ~self.mask:
            raise ValueError('value does not fit in the given bit width')
        assert isinstance(val, BinInt)
        self._val = val

    @property
    def width(self):
        """Returns the width of this word in bits."""
        return self._width

    @property
    def mask(self):
        """Returns a BinInt with low self.width bits set, corresponding
        to a bitmask of valid bits for words of this size.
        """
        return BinInt.mask(self._width)

    def to_uint(self):
        """Converts the word to a BinInt, treating it as an unsigned number."""
        return self._val

    def to_sint(self):
        """Converts the word to a BinInt, treating it as a signed number."""
        if self._width == 0:
            return BinInt(0)
        sbit = 1 << (self._width - 1)
        return BinInt((self._val - sbit) ^ -sbit)

    def __index__(self):
        """Converts the word to an int, treating it as an unsigned number."""
        return int(self._val)

    __int__ = __index__

    def __eq__(self, other):
        """Compares for equality with another object.  BinWords are only
        considered equal to other BinWords with the same width and value.
        """
        if not isinstance(other, BinWord):
            return False
        return self._width == other._width and self._val == other._val

    def __hash__(self):
        return hash((self._width, self._val))

    def __len__(self):
        """Returns the width of this word in bits."""
        return self._width

    def __getitem__(self, idx):
        """Extracts a given bit or a range of bits, with python indexing
        semantics.  Use ``extract`` to extract by position and width.
        """
        if isinstance(idx, slice):
            start, stop, step = idx.indices(self._width)
            if step == 1:
                if stop <= start:
                    return BinWord(0, 0)
                return self.extract(start, stop - start)
            else:
                r = range(start, stop, step)
                val = 0
                for opos, ipos in enumerate(r):
                    val |= (self._val >> ipos & 1) << opos
                return BinWord(len(r), val)
        else:
            idx = operator.index(idx)
            if idx < 0:
                idx += self._width
            return self.extract(idx, 1)

    def __bool__(self):
        """Converts a BinWord to a bool.  All words not equal to all-zeros
        are considered to be true.
        """
        return bool(self._val)

    def _check_match(self, other):
        if not isinstance(other, BinWord):
            raise TypeError('need another BinWord')
        if self._width != other._width:
            raise ValueError('mismatched widths in BinWord operation')

    def __add__(self, other):
        """Performs a wrapping addition of two equal-sized BinWords."""
        self._check_match(other)
        return BinWord(self._width, self._val + other._val, trunc=True)

    def __sub__(self, other):
        """Performs a wrapping subtraction of two equal-sized BinWords."""
        self._check_match(other)
        return BinWord(self._width, self._val - other._val, trunc=True)

    def __mul__(self, other):
        """Performs a wrapping multiplication of two equal-sized BinWords."""
        self._check_match(other)
        return BinWord(self._width, self._val * other._val, trunc=True)

    def __and__(self, other):
        """Performs a bitwise AND of two equal-sized BinWords."""
        self._check_match(other)
        return BinWord(self._width, self._val & other._val)

    def __or__(self, other):
        """Performs a bitwise OR of two equal-sized BinWords."""
        self._check_match(other)
        return BinWord(self._width, self._val | other._val)

    def __xor__(self, other):
        """Performs a bitwise XOR of two equal-sized BinWords."""
        self._check_match(other)
        return BinWord(self._width, self._val ^ other._val)

    def __lshift__(self, count):
        """Performs a left-shift of a BinWord by the given number of bits.
        Bits shifted out of the word are lost.

        The shift count can be an arbitrary non-negative number, including
        counts larger than the word (0 is returned in this case).
        """
        count = operator.index(count)
        if count < 0:
            raise ValueError('negative shift')
        if count > self._width:
            count = self._width
        return BinWord(self._width, self._val << count, trunc=True)

    def __rshift__(self, count):
        """Performs a logical right-shift of a BinWord by the given number
        of bits.  Bits shifted out of the word are lost.  The word is
        filled on the left with 0 bits.

        The shift count can be an arbitrary non-negative number, including
        counts larger than the word (0 is returned in this case).
        """
        count = operator.index(count)
        if count < 0:
            raise ValueError('negative shift')
        if count > self._width:
            count = self._width
        return BinWord(self._width, self._val >> count)

    def sar(self, count):
        """Performs an arithmetic right-shift of a BinWord by the given number
        of bits.  Bits shifted out of the word are lost.  The word is
        filled on the left with copies of the top bit.

        The shift count can be an arbitrary non-negative number, including
        counts larger than the word (a word filled with copies of the sign bit
        is returned in this case).
        """
        count = operator.index(count)
        if count < 0:
            raise ValueError('negative shift')
        if count > self._width:
            count = self._width
        return BinWord(self._width, self.to_sint() >> count, trunc=True)

    def __neg__(self):
        """Returns a two's complement of the BinWord."""
        return BinWord(self._width, -self._val, trunc=True)

    def __invert__(self):
        """Returns a one's complement of the BinWord (ie. inverts all bits)."""
        return BinWord(self._width, ~self._val, trunc=True)

    def extract(self, pos, width):
        """Extracts a subword with a given width, starting from a given
        bit position.  It is an error to extract out-of-range bits.
        """
        pos = operator.index(pos)
        width = operator.index(width)
        if width < 0:
            raise ValueError('width must not be negative')
        if pos < 0 or pos + width > self._width:
            raise ValueError('extracting out of range')
        return BinWord(width, self._val >> pos, trunc=True)

    def sext(self, width):
        """Sign-extends a word to a larger width.  It is an error to specify
        a smaller width (use ``extract`` instead to crop off the extra bits).
        """
        width = operator.index(width)
        if width < self._width:
            raise ValueError('sign extending to a smaller width')
        return BinWord(width, self.to_sint(), trunc=True)

    def zext(self, width):
        """Zero-extends a word to a larger width.  It is an error to specify
        a smaller width (use ``extract`` instead to crop off the extra bits).
        """
        width = operator.index(width)
        if width < self._width:
            raise ValueError('zero extending to a smaller width')
        return BinWord(width, self._val)

    def deposit(self, pos, val):
        """Returns a copy of this BinWord, with a given word deposited
        at a given position (ie. with bits pos:pos+len(val) replaced
        bit bits from val).
        """
        if not isinstance(val, BinWord):
            raise TypeError('deposit needs a BinWord')
        pos = operator.index(pos)
        if pos < 0 or val._width + pos > self._width:
            raise ValueError('depositing out of range')
        res = self._val
        res &= ~(val.mask << pos)
        res |= val.to_uint() << pos
        return BinWord(self._width, res)

    def __lt__(self, other):
        """Compares two equal-sized BinWords, treating them as unsigned
        integers, and returning True if the first is smaller.  Use ``slt``
        to compare as signed integers instead.
        """
        self._check_match(other)
        return self._val < other._val

    def __le__(self, other):
        """Compares two equal-sized BinWords, treating them as unsigned
        integers, and returning True if the first is smaller or equal.
        Use ``sle`` to compare as signed integers instead.
        """
        self._check_match(other)
        return self._val <= other._val

    def __gt__(self, other):
        """Compares two equal-sized BinWords, treating them as unsigned
        integers, and returning True if the first is bigger.  Use ``sgt``
        to compare as signed integers instead.
        """
        self._check_match(other)
        return self._val > other._val

    def __ge__(self, other):
        """Compares two equal-sized BinWords, treating them as unsigned
        integers, and returning True if the first is bigger or equal.
        Use ``sge`` to compare as signed integers instead.
        """
        self._check_match(other)
        return self._val >= other._val

    def slt(self, other):
        """Compares two equal-sized BinWords, treating them as signed
        integers, and returning True if the first is smaller.
        """
        self._check_match(other)
        return self.to_sint() < other.to_sint()

    def sle(self, other):
        """Compares two equal-sized BinWords, treating them as signed
        integers, and returning True if the first is smaller or equal.
        """
        self._check_match(other)
        return self.to_sint() <= other.to_sint()

    def sgt(self, other):
        """Compares two equal-sized BinWords, treating them as signed
        integers, and returning True if the first is bigger.
        """
        self._check_match(other)
        return self.to_sint() > other.to_sint()

    def sge(self, other):
        """Compares two equal-sized BinWords, treating them as signed
        integers, and returning True if the first is bigger or equal.
        """
        self._check_match(other)
        return self.to_sint() >= other.to_sint()

    @classmethod
    def concat(cls, *args):
        """Returns a BinWord made from concatenating several BinWords,
        in LSB-first order.
        """
        width = 0
        val = 0
        for arg in args:
            if not isinstance(arg, BinWord):
                raise TypeError('need BinWord in concat')
            val |= arg._val << width
            width += arg._width
        return cls(width, val)

    @property
    def _width_in_nibbles(self):
        return (self._width + 3) // 4

    def __repr__(self):
        val = f'0x{self._val:0{self._width_in_nibbles}x}'
        return f'BinWord({self._width}, {val})'

    def __str__(self):
        """Returns a textual representation in the following format:
        ``#<width as a decimal number>x<value as a hexadecimal number>``.
        This format is directly accepted by the S-expression parser.
        """
        return f'#{self._width}x{self._val:0{self._width_in_nibbles}x}'


from .int import BinInt  # noqa: E402
