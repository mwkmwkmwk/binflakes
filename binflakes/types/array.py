import operator

from .word import BinWord
from .int import BinInt

# list/bytearray operations that we may want to implement some day:
#
# - __setitem__ with slice and binarray of different length
# - __contains__
# - __lt__, ...:  lex sorting
# - append
# - clear
# - copy
# - count
# - extend aka __iadd__
# - index
# - insert
# - pop
# - remove
# - reverse


class BinArray:
    """Represents an array of equal-width BinWords.  Conceptually behaves
    like bytearray, except that element width can be different than 8,
    and item accesses return BinWord instances.
    """

    def __init__(self, data=None, *, width=None, length=None):
        """Creates a new BinArray.  The following forms are valid:

        - ``BinArray(bytes or bytearray)``: creates a BinArray of width 8
          with items from the given bytearray.
        - ``BinArray(BinArray instance)``: creates a copy of a BinArray.
        - ``BinArray(width=w)``: creates empty BinArray of given width.
        - ``BinArray(width=w, length=n)``: creates a zero-filled BinArray of
          given width and length.
        - ``BinArray(iterable, width=n)``: creates a BinArray from the given
          iterable of items.  Items should be ints, BinInts, or BinWords
          of the correct width.
        - ``BinArray(iterable)``: creates a BinArray from a non-empty array
          of BinWords.
        """
        if data is not None and length is not None:
            raise TypeError('data and length are mutually exclusive')
        if data is None:
            if length is None:
                length = 0
            if width is None:
                raise TypeError('width not specified')
            length = operator.index(length)
            width = operator.index(width)
            if width < 0:
                raise ValueError('width cannot be negative')
            self._init(width, length)
        else:
            try:
                len(data)
            except TypeError:
                data = list(data)
            if width is None:
                if isinstance(data, (bytes, bytearray)):
                    width = 8
                elif isinstance(data, BinArray):
                    width = data.width
                else:
                    raise TypeError('width not specified')
            width = operator.index(width)
            if width < 0:
                raise ValueError('width cannot be negative')
            self._init(width, len(data))
            for i, x in enumerate(data):
                self[i] = x

    def _init(self, width, len_):
        """Initializes internal data representation of the BinArray to all-0.
        The internal data representation is simply tightly-packed bits of all
        words, starting from LSB, split into bytes and stored in a bytearray.
        The unused trailing padding bits in the last byte must always be set
        to 0.
        """
        self._width = width
        self._len = len_
        bits = len_ * width
        self._data = bytearray(BinInt(bits).ceildiv(8))

    def _locate(self, idx):
        """Locates an element in the internal data representation.  Returns
        starting byte index, starting bit index in the starting byte, and
        one past the final byte index.
        """
        start = idx * self._width
        end = (idx + 1) * self._width
        sbyte, sbit = divmod(start, 8)
        ebyte = BinInt(end).ceildiv(8)
        return sbyte, sbit, ebyte

    @property
    def width(self):
        """Returns word width of the BinArray."""
        return self._width

    def __len__(self):
        """Returns length of the array in words."""
        return self._len

    def __getitem__(self, idx):
        """Returns a word at the given index (as a BinWord instance),
        or a slice of the array (as a new BinArray instance).
        """
        if isinstance(idx, slice):
            start, stop, step = idx.indices(len(self))
            r = range(start, stop, step)
            res = BinArray(width=self._width, length=len(r))
            for opos, ipos in enumerate(r):
                res[opos] = self[ipos]
            return res
        else:
            idx = operator.index(idx)
            if idx < 0:
                idx += len(self)
            if idx not in range(len(self)):
                raise IndexError('index out of range')
            sbyte, sbit, ebyte = self._locate(idx)
            raw = self._data[sbyte:ebyte]
            raw = BinInt.from_bytes(raw, 'little')
            return raw.extract(sbit, self._width)

    def __setitem__(self, idx, val):
        """Assigns to the word at a given index, or to a subslice of
        the array.  When assigning words, the assigned value must be
        a BinWord instance of the same width as the array, or an int
        or BinInt instance that will be automatically converted
        to BinWord.  It is an error if an int or BinInt is assigned
        that does not fit in ``width`` bits.
        """
        if isinstance(idx, slice):
            if not isinstance(val, BinArray):
                raise TypeError('assigning non-BinArray to a slice')
            if self._width != val._width:
                raise ValueError('mismatched widths in slice assignment')
            start, stop, step = idx.indices(len(self))
            r = range(start, stop, step)
            if len(r) != len(val):
                raise ValueError('mismatched lengths in slice assignment')
            for idx, item in zip(r, val):
                self[idx] = item
        else:
            idx = operator.index(idx)
            if idx < 0:
                idx += len(self)
            if idx not in range(len(self)):
                raise IndexError('index out of range')
            if isinstance(val, BinWord) and val._width != self._width:
                raise ValueError('word width mismatch')
            val = BinWord(self._width, val)
            sbyte, sbit, ebyte = self._locate(idx)
            raw = self._data[sbyte:ebyte]
            raw = BinInt.from_bytes(raw, 'little')
            raw = raw.deposit(sbit, val)
            self._data[sbyte:ebyte] = raw.to_bytes(ebyte - sbyte, 'little')

    def __repr__(self):
        width_nibbles = BinInt(self._width).ceildiv(4)
        fmt = f'0{width_nibbles}x'
        elems = ', '.join(f'0x{x.to_uint():{fmt}}' for x in self)
        return f'BinArray([{elems}], width={self._width})'

    def __str__(self):
        """Returns a textual representation in the following format:
        ``#<width as a decimal number>x(<space-separated words as hexadecimal
        numbers>)``.  This format is directly accepted by the S-expression
        parser.
        """
        width_nibbles = BinInt(self._width).ceildiv(4)
        fmt = f'0{width_nibbles}x'
        elems = ' '.join(format(x.to_uint(), fmt) for x in self)
        return f'#{self._width}x({elems})'

    def __eq__(self, other):
        """Compares for equality with another object.  BinArrays are only
        considered equal to other BinArrays with the same width, length,
        and contents.
        """
        if not isinstance(other, BinArray):
            return False
        if self._width != other._width:
            return False
        if self._len != other._len:
            return False
        return self._data == other._data

    def _check_match(self, other):
        if not isinstance(other, BinArray):
            raise TypeError(
                'argument to bitwise operation must be another BinArray')
        if self._width != other._width:
            raise ValueError('mismatched widths for bitwise operation')
        if self._len != other._len:
            raise ValueError('mismatched lengths for bitwise operation')

    def __and__(self, other):
        """Creates a new BinArray from two equal-width, equal-length
        BinArrays by applying the bitwise AND operation to every pair
        of corresponding words.
        """
        self._check_match(other)
        res = BinArray.__new__(BinArray)
        res._width = self._width
        res._len = self._len
        res._data = bytearray(x & y for x, y in zip(self._data, other._data))
        return res

    def __or__(self, other):
        """Creates a new BinArray from two equal-width, equal-length
        BinArrays by applying the bitwise OR operation to every pair
        of corresponding words.
        """
        self._check_match(other)
        res = BinArray.__new__(BinArray)
        res._width = self._width
        res._len = self._len
        res._data = bytearray(x | y for x, y in zip(self._data, other._data))
        return res

    def __xor__(self, other):
        """Creates a new BinArray from two equal-width, equal-length
        BinArrays by applying the bitwise XOR operation to every pair
        of corresponding words.
        """
        self._check_match(other)
        res = BinArray.__new__(BinArray)
        res._width = self._width
        res._len = self._len
        res._data = bytearray(x ^ y for x, y in zip(self._data, other._data))
        return res

    def __iand__(self, other):
        self._check_match(other)
        for idx, val in enumerate(other._data):
            self._data[idx] &= val
        return self

    def __ior__(self, other):
        self._check_match(other)
        for idx, val in enumerate(other._data):
            self._data[idx] |= val
        return self

    def __ixor__(self, other):
        self._check_match(other)
        for idx, val in enumerate(other._data):
            self._data[idx] ^= val
        return self

    def __invert__(self):
        """Creates a new BinArray with all bits inverted."""
        return BinArray([~x for x in self], width=self._width)

    def __add__(self, other):
        """Concatenates two equal-width BinArray instances together, returning
        a new BinArray.
        """
        if not isinstance(other, BinArray):
            raise TypeError(
                'argument to concatenation must be another BinArray')
        if self._width != other._width:
            raise ValueError('mismatched widths for concatenation')
        res = BinArray(width=self._width, length=len(self) + len(other))
        res[:len(self)] = self
        res[len(self):] = other
        return res

    def __mul__(self, count):
        """Repeats a BinArray count times, returning a new BinArray."""
        count = operator.index(count)
        if count < 0:
            raise ValueError('negative repetition count')
        sl = len(self)
        res = BinArray(width=self._width, length=sl * count)
        for idx in range(count):
            res[idx * sl:(idx + 1) * sl] = self
        return res

    __rmul__ = __mul__

    def repack(self, to_width, *, msb_first, start=0, start_bit=0,
               length=None):
        """Extracts a part of a BinArray's data and converts it to a BinArray
        of a different width.

        For the purposes of this conversion, words in this BinArray are joined
        side-by-side, starting from a given start index (defaulting to 0),
        skipping ``start_bit`` first bits of the first word, then the resulting
        stream is split into ``to_width``-sized words and ``length`` first
        such words are returned as a new BinArray.

        If ``msb_first`` is False, everything proceeds with little endian
        ordering: the first word provides the least significant bits of the
        combined stream, ``start_bit`` skips bits starting from the LSB,
        and the first output word is made from the lowest bits of the combined
        stream.  Otherwise (``msb_first`` is True), everything proceeds
        with big endian ordering: the first word provides the most
        significant bits of the combined stream, ``start_bit`` skips bits
        starting from the MSB, and the first output word is made from the
        highest bits of the combined stream.

        ``start_bits`` must be smaller than the width of the input word.
        It is an error to request a larger length than can be provided from
        the input array.  If ``length`` is not provided, this function
        returns as many words as can be extracted.

        For example, consider a 10-to-3 repack with start_bit=2, length=4
        msb_first=True:

        +---------+-+-+-+-+-+-+-+-+-+-+
        |         | MSB ... LSB       |
        +---------+-+-+-+-+-+-+-+-+-+-+
        |         | ...               |
        +---------+-+-+-+-+-+-+-+-+-+-+
        | start   |X|X|a|b|c|d|e|f|g|h|
        +---------+-+-+-+-+-+-+-+-+-+-+
        | start+1 |i|j|k|l|X|X|X|X|X|X|
        +---------+-+-+-+-+-+-+-+-+-+-+
        |         | ...               |
        +---------+-+-+-+-+-+-+-+-+-+-+

        is repacked to:

        +-+-+-+-+
        |0|a|b|c|
        +-+-+-+-+
        |1|d|e|f|
        +-+-+-+-+
        |2|g|h|i|
        +-+-+-+-+
        |3|j|k|l|
        +-+-+-+-+

        The same repack for msb_first=False is performed as follows:

        +---------+-+-+-+-+-+-+-+-+-+-+
        |         | MSB ... LSB       |
        +---------+-+-+-+-+-+-+-+-+-+-+
        |         | ...               |
        +---------+-+-+-+-+-+-+-+-+-+-+
        | start   |h|g|f|e|d|c|b|a|X|X|
        +---------+-+-+-+-+-+-+-+-+-+-+
        | start+1 |X|X|X|X|X|X|l|k|j|i|
        +---------+-+-+-+-+-+-+-+-+-+-+
        |         | ...               |
        +---------+-+-+-+-+-+-+-+-+-+-+

        into:

        +-+-+-+-+
        |0|c|b|a|
        +-+-+-+-+
        |1|f|e|d|
        +-+-+-+-+
        |2|i|h|g|
        +-+-+-+-+
        |3|l|k|j|
        +-+-+-+-+
        """
        to_width = operator.index(to_width)
        if not isinstance(msb_first, bool):
            raise TypeError('msb_first must be a bool')
        available = self.repack_data_available(
                to_width, start=start, start_bit=start_bit)
        if length is None:
            length = available
        else:
            length = operator.index(length)
            if length > available:
                raise ValueError('not enough data available')
            if length < 0:
                raise ValueError('length cannot be negative')
        start = operator.index(start)
        start_bit = operator.index(start_bit)
        pos = start
        accum = BinWord(0, 0)
        if start_bit:
            accum = self[pos]
            pos += 1
            rest = accum.width - start_bit
            if msb_first:
                accum = accum.extract(0, rest)
            else:
                accum = accum.extract(start_bit, rest)
        res = BinArray(width=to_width, length=length)
        for idx in range(length):
            while len(accum) < to_width:
                cur = self[pos]
                pos += 1
                if msb_first:
                    accum = BinWord.concat(cur, accum)
                else:
                    accum = BinWord.concat(accum, cur)
            rest = accum.width - to_width
            if msb_first:
                cur = accum.extract(rest, to_width)
                accum = accum.extract(0, rest)
            else:
                cur = accum.extract(0, to_width)
                accum = accum.extract(to_width, rest)
            res[idx] = cur
        return res

    def repack_source_required(src_width, to_width, length, *, start_bit=0):
        """Calculates how many source words would be read for an invocation of
        repack with a given length, including possible partial words at
        the beginning and the end of the repack source.  This can be called
        either on a concrete BinArray instance (assuming its width as the
        source width), or on the BinArray class (providing the source width
        as an extra first argument).  This function doesn't take ``start``
        or ``msb_first`` parameters, since they wouldn't affect the
        computation.
        """
        if isinstance(src_width, BinArray):
            src_width = src_width._width
        src_width = operator.index(src_width)
        to_width = operator.index(to_width)
        length = operator.index(length)
        start_bit = operator.index(start_bit)
        if src_width <= 0:
            raise ValueError('source width must be positive')
        if to_width <= 0:
            raise ValueError('destination width must be positive')
        if length < 0:
            raise ValueError('length must not be negative')
        if start_bit not in range(src_width):
            raise ValueError('start bit must be in [0, src_width)')
        return BinInt(start_bit + to_width * length).ceildiv(src_width)

    def repack_data_available(src_width, to_width, *, src_length=None,
                              start=None, start_bit=0):
        """Calculates the maximum number of words that can be requested
        from a repack invocation with the given settings.

        This function can be called either on a BinArray instance (assuming
        its width as the source width), or on the BinArray class (passing
        the source width as an extra first argument).  If called in the
        second form, ``src_length`` must be provided.  Otherwise, it will
        default to the number of words in the source array from the given
        ``start`` index (defaulting to 0) until the end.
        """
        start_bit = operator.index(start_bit)
        if isinstance(src_width, BinArray):
            self = src_width
            if src_length is None:
                if start is None:
                    start = 0
                else:
                    start = operator.index(start)
                    if start < 0:
                        raise ValueError('start must not be negative')
                src_length = len(self) - start
                start = None
            src_width = self.width
        if src_length is None:
            raise TypeError('no length given')
        if start is not None:
            raise TypeError('start is redundant with explicit src_length')
        src_width = operator.index(src_width)
        to_width = operator.index(to_width)
        src_length = operator.index(src_length)
        start_bit = operator.index(start_bit)
        if src_width <= 0:
            raise ValueError('source width must be positive')
        if to_width <= 0:
            raise ValueError('destination width must be positive')
        if src_length < 0:
            raise ValueError('src_length must not be negative')
        if start_bit not in range(src_width):
            raise ValueError('start bit must be in [0, src_width)')
        if src_length == 0 and start_bit != 0:
            raise ValueError(
                    'src_length must be positive if start_bit is not zero')
        return (src_width * src_length - start_bit) // to_width
