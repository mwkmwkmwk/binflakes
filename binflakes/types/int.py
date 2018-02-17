import operator


class BinInt(int):
    """A class representing an arbitrary-precision binary integer number.

    This is just a python int with some extra methods.

    Can be treated as an infinite sequence of individual bits (which are
    represented as BinWords of width 1), with bit 0 being the LSB.
    For non-negative numbers, all bits from a certain point are equal to 0.
    For negative numbers, all bits from a certain point are equal to 1
    (following two's complement convention).
    """

    __slots__ = ()

    @classmethod
    def mask(cls, width):
        """Creates a new BinInt with low ``width`` bits set."""
        return cls((1 << width) - 1)

    def __getitem__(self, idx):
        """Extracts a given bit or a range of bits, with python indexing
        semantics.  Use ``extract`` to extract by position and width.

        Since BinInt is, conceptually, an infinite sequence of bits,
        it is an error to use negative indices.  However, it is fine
        to omit the stop index, returning an infinite subsequence
        of bits -- a BigInt is returned in this case.  For finite
        sequences, a BinWord is returned.
        """
        if not isinstance(idx, slice):
            return self.extract(idx, 1)
        step = 1 if idx.step is None else operator.index(idx.step)
        if step == 0:
            raise ValueError('step cannot be 0')
        if step < 0 and idx.start is None:
            raise ValueError('start cannot be None for reverse slicing')
        start = 0 if idx.start is None else operator.index(idx.start)
        stop = None if idx.stop is None else operator.index(idx.stop)
        if start < 0:
            raise ValueError(
                'indexing from the end doesn\'t make sense for a BinInt')
        if stop is not None and stop < 0:
            raise ValueError(
                'indexing from the end doesn\'t make sense for a BinInt')
        if stop is None and step > 0:
            if step == 1:
                return self >> start
            bits = self.bit_length()
            r = range(start, bits, step)
            val = 0
            for opos, ipos in enumerate(r):
                val |= (self >> ipos & 1) << opos
            if self < 0:
                val |= -1 << len(r)
            return BinInt(val)
        else:
            if stop is None:
                stop = -1
            if step == 1:
                if stop <= start:
                    return BinWord(0, 0)
                return self.extract(start, stop - start)
            r = range(start, stop, step)
            val = 0
            for opos, ipos in enumerate(r):
                val |= (self >> ipos & 1) << opos
            return BinWord(len(r), val)

    def extract(self, pos, width):
        """Extracts a subword with a given width, starting from a given
        bit position.
        """
        pos = operator.index(pos)
        width = operator.index(width)
        if width < 0:
            raise ValueError('width must not be negative')
        if pos < 0:
            raise ValueError('extracting out of range')
        return BinWord(width, self >> pos, trunc=True)

    def deposit(self, pos, val):
        """Returns a copy of this BinInt, with a given word deposited
        at a given position (ie. with bits pos:pos+len(val) replaced
        with bits from val).
        """
        if not isinstance(val, BinWord):
            raise TypeError('deposit needs a BinWord')
        pos = operator.index(pos)
        if pos < 0:
            raise ValueError('depositing out of range')
        res = self
        res &= ~(val.mask << pos)
        res |= val.to_uint() << pos
        return res

    def __repr__(self):
        return f'BinInt({self})'

    def __add__(self, other):
        return BinInt(super().__add__(other))

    def __radd__(self, other):
        return BinInt(super().__radd__(other))

    def __sub__(self, other):
        return BinInt(super().__sub__(other))

    def __rsub__(self, other):
        return BinInt(super().__rsub__(other))

    def __mul__(self, other):
        return BinInt(super().__mul__(other))

    def __rmul__(self, other):
        return BinInt(super().__rmul__(other))

    def __floordiv__(self, other):
        return BinInt(super().__floordiv__(other))

    def __rfloordiv__(self, other):
        return BinInt(super().__rfloordiv__(other))

    def __mod__(self, other):
        return BinInt(super().__mod__(other))

    def __rmod__(self, other):
        return BinInt(super().__rmod__(other))

    def __and__(self, other):
        return BinInt(super().__and__(other))

    def __rand__(self, other):
        return BinInt(super().__rand__(other))

    def __or__(self, other):
        return BinInt(super().__or__(other))

    def __ror__(self, other):
        return BinInt(super().__ror__(other))

    def __xor__(self, other):
        return BinInt(super().__xor__(other))

    def __rxor__(self, other):
        return BinInt(super().__rxor__(other))

    def __lshift__(self, other):
        return BinInt(super().__lshift__(other))

    def __rshift__(self, other):
        return BinInt(super().__rshift__(other))

    def __neg__(self):
        return BinInt(super().__neg__())

    def __invert__(self):
        return BinInt(super().__invert__())

    def __abs__(self):
        return BinInt(super().__abs__())

    def __pos__(self):
        return BinInt(super().__pos__())

    def ceildiv(self, other):
        """Returns ceil(a / b)."""
        return -(-self // other)


from .word import BinWord  # noqa: E402
