===================
S-expression syntax
===================

The binflakes definition language is built on top of a custom variant
of Lisp-like S-expressions, which is documented here.  The S-expression
syntax can also be used for generic data serialization (like JSON).

S-expressions are made of the following:

- single-line comments, starting with ``;``
- commented-out expressions: ``#; <arbitrary S-expression>`` -- makes
  the reader parse a complete sub-expression and discard it.  Can be used
  to temporarily disable a single element of a list.  For example::

    (abc
     (def 1 2 3)
     #; (ghi
       4
       (5 6)
       7)
     (jkl #;8 9)
    )

  parses the same as ``(abc (def 1 2 3) (jkl 9))``.

- ``(`` (an opening paren) -- starts a list
- ``)`` (a closing paren) -- ends a list
- symbols: any string of characters from the set ``[a-zA-Z0-9*+=<>!?/.@$%_-]``
  that does not start with a digit, or with a minus sign followed by a digit.
  Used to name variables, functions, and special forms.
- the NULL constant: ``#nil``.
- boolean constants:

  - ``#f``: false.
  - ``#t``: true.

- integer constants (converted to BinInt by the reader):

  - ``-?[0-9]+``: a decimal number, eg. ``123``, ``-4``.
  - ``#x-?[0-9a-fA-F]+``: a hexadecimal number, eg. ``#x1234``, ``#x-abcd``
    (same as ``-43981``).
  - ``#o-?[0-7]+``: an octal number, eg. ``#o664``.
  - ``#b-?[01]+``: a binary number, eg. ``#b1101``.

- binary word constants (converted to BinWord by the reader):

  - ``#[0-9]+x-?[0-9a-fA-F]+``: a hexadecimal number converted to a word
    of the specified width, eg. ``#32xdeadbeef`` (a 32-bit word).
  - ``#[0-9]+d-?[0-9]+``: a decimal number, eg. ``#12d123``
    (same as ``#12x07b``), ``#12d-123`` (same as ``#12xf85``).
  - ``#[0-9]+o-?[0-7]+``: an octal number, eg. ``#12o664`` (same as
    ``#12x1b4``).
  - ``#[0-9]+b-?[01]+``: a binary number, eg. ``#4b0110`` (same as
    ``#4x6``).

  Positive numbers must be smaller than ``2**width``.  Negative numbers
  must be at least ``-2**width`` (ie. it is allowed to specify a negative
  number that would wrap to positives if interpreted as a signed int
  of the given width, but not to specify a number that would wrap all
  the way back to negatives or further).

- string constants: ``"<char|escape>*"``, where any non-control character
  except ``\\`` and ``"`` can be written directly, and escape is one of:

  - ``\\\\``, ``\\"``: represents a literal ``\\`` or ``"``.
  - ``\\a``, ``\\b``, ``\\t``, ``\\n``, ``\\f``, ``\\r``, ``\\e``: represent
    the usual control characters (``\\e`` is the ESCape character, ASCII 0x1b).
  - ``\x[0-9a-fA-F]{2}``: a two-digit hexadecimal character code escape.
  - ``\u[0-9a-fA-F]{4}``: a four-digit hexadecimal character code escape.
  - ``\U[0-9a-fA-F]{6}``: a six-digit hexadecimal character code escape.

  All string constants are unicode.

- binary array constants (converted to BinArray by the reader):

  - ``#[0-9]+x(<hex-number>*)``: a BinArray with every word written
    as a hexadecimal number, eg. ``#12x(123 456 abc)``.  Line comments
    are allowed between individual elements.
  - ``#[0-9]+d(<dec-number>*)``, likewise for decimal numbers, eg.
    ``#10d(123 456)`` (equivalent to ``#10x(07b 1c8)``).
  - ``#[0-9]+o(<oct-number>*)``: likewise for octal numbers.
  - ``#[0-9]+b(<bin-number>*)``: likewise for binary numbers.
  - ``#[0-9]+"<char|escape>*"``: the chars and escapes are parsed as
    in a string constant, then each resulting character code is
    converted to a word of the given width, and the words concatenated
    to a BinArray.  For example, ``#8"abc"`` is the same as ``#8x(61 62 63)``.

  The range of allowed numbers is the same as for binary word constants.

.. todo::

  - Non-integer numbers (``0.1`` etc)
  - Single-character consts -- are they needed as a separate token?
  - Some kind of block comment
  - A generic vector constant?
  - Namespaced symbols (eg. enum-name:value-name)?

.. note::

  The following ASCII characters are reserved for now: ``:~`',^&|\\[]{}``.
