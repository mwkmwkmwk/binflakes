"""This module contains three "basic types" used in binflakes in addition
to the usual ones:

- :py:class:`binflakes.types.BinInt` -- an arbitrary-precision integer
  type, with a few extra methods for bit-level manipulation
- :py:class:`binflakes.types.BinWord` -- represents fixed-width binary
  words
- :py:class:`binflakes.types.BinArray` -- represents fixed-width arrays of
  binary words
"""

from .word import BinWord
from .int import BinInt
from .array import BinArray

__all__ = ['BinWord', 'BinInt', 'BinArray']
