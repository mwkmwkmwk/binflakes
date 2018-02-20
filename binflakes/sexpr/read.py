import re
from enum import Enum
from io import StringIO

from attr import attrs, attrib
from attr.validators import instance_of

from binflakes.types import BinWord, BinArray
from .string import ESCAPE_TO_CHAR
from .symbol import Symbol
from .location import TextLocationSingle, TextLocationRange
from .nodes import make_node


class ReadError(Exception):
    """An exception class used for all problems noticed by the reader."""
    pass


class State(Enum):
    """Represents the reader state (between tokens, inside a string token,
    inside a BinArray token.
    """
    NORMAL = 'normal'
    STRING = 'string'
    BINARRAY = 'binarray'


@attrs(slots=True)
class StackEntryList:
    """A reader stack entry representing a list currently being parsed.
    ``items`` are the items parsed so far, ``start`` is the location of
    the opening paren.
    """
    start = attrib(validator=instance_of(TextLocationSingle))
    items = attrib(validator=instance_of(list))

    def raise_unclosed_error(self):
        raise ReadError(f'{self.start}: unmatched open paren')


@attrs(slots=True)
class StackEntryComment:
    """A reader stack entry representing a commented-out S-expression
    currently being parsed. ``start`` is the location of the opening
    comment sign.
    """
    start = attrib(validator=instance_of(TextLocationRange))

    def raise_unclosed_error(self):
        raise ReadError(f'{self.start}: unclosed S-expr comment')


RE_TOKEN = re.compile(r'''
    (?P<whitespace>[ \t\r\n\f]+) |
    (?P<line_comment>\#\ .*$) |
    (?P<lparen>\() |
    (?P<rparen>\)) |
    (?P<bool_value>@true|@false) |
    (?P<nil_value>@nil) |
    (?P<string_width>[0-9]+)'" |
    (?P<array_width>[0-9]+)'(?P<array_base>0[box])?\( |
    (?:(?P<word_width>[0-9]+)')? (?P<int_or_word>
        -? 0b [0-1]+ |
        -? 0o [0-7]+ |
        -? 0x [0-9a-fA-F]+ |
        -? [1-9][0-9]* |
        -? 0
    ) |
    (?P<symbol>
        [a-zA-Z*+=<>!?/.$%_][0-9a-zA-Z*+=<>!?/.$%_-]* |
        -[a-zA-Z*+=<>!?/.$%_-][0-9a-zA-Z*+=<>!?/.$%_-]* |
        -
    ) |
    (?P<sexpr_comment>\#\#) |
    (?P<start_quote>")
''', re.VERBOSE)

RE_STRING_ITEM = re.compile(r'''
    (?P<end_quote>") |
    (?P<raw_chars>[^\\"]+) |
    \\(?P<simple_escape>[abtnfre\\"]) |
    \\[xuU](?P<hex_code>
        (?<=x)[0-9a-fA-F]{2} |
        (?<=u)[0-9a-fA-F]{4} |
        (?<=U)[0-9a-fA-F]{6}
    )
''', re.VERBOSE)

RE_BINARRAY_ITEM = {
    2: re.compile(r'''
        (?P<whitespace>[ \t\r\n\f]+) |
        (?P<line_comment>\# .*$) |
        (?P<rparen>\)) |
        (?P<digits>-?[0-1]+)
    ''', re.VERBOSE),
    8: re.compile(r'''
        (?P<whitespace>[ \t\r\n\f]+) |
        (?P<line_comment>\# .*$) |
        (?P<rparen>\)) |
        (?P<digits>-?[0-7]+)
    ''', re.VERBOSE),
    10: re.compile(r'''
        (?P<whitespace>[ \t\r\n\f]+) |
        (?P<line_comment>\# .*$) |
        (?P<rparen>\)) |
        (?P<digits>
            -? [1-9][0-9]* |
            -? 0
        )
    ''', re.VERBOSE),
    16: re.compile(r'''
        (?P<whitespace>[ \t\r\n\f]+) |
        (?P<line_comment>\# .*$) |
        (?P<rparen>\)) |
        (?P<digits>-?[0-9a-fA-F]+)
    ''', re.VERBOSE),
}


class Reader:
    """A class for reading S-expressions and converting them to a node tree.
    Accepts the input line-by-line, yielding top-level S-expressions as they
    are recognized.
    """
    def __init__(self, filename):
        """Initializes internal state.  ``filename`` affects only the location
        tags that will be attached to nodes.
        """
        self.filename = filename
        self.stack = []
        self.state = State.NORMAL
        self.line = 0
        # Only valid when state is STRING.
        self.string_buffer = None
        # Only valid when state is BINARRAY.
        self.binarray_base = None
        self.binarray_data = None
        # Only valid when state is STRING or BINARRAY.
        self.binarray_width = None
        self.token_start = None

    def feed_line(self, line):
        """Feeds one line of input into the reader machine.  This method is
        a generator that yields all top-level S-expressions that have been
        recognized on this line (including multi-line expressions whose last
        character is on this line).
        """
        self.line += 1
        pos = 0
        need_white = False
        while pos < len(line):
            loc_start = TextLocationSingle(self.filename, self.line, pos + 1)
            if self.state is State.NORMAL:
                item_re = RE_TOKEN
                thing = 'token'
            elif self.state is State.STRING:
                item_re = RE_STRING_ITEM
                thing = 'escape sequence'
            elif self.state is State.BINARRAY:
                item_re = RE_BINARRAY_ITEM[self.binarray_base]
                thing = 'binarray item'
            else:
                assert 0
            match = item_re.match(line, pos)
            if not match:
                raise ReadError(f'{loc_start}: unknown {thing}')
            pos = match.end()
            loc_end = TextLocationSingle(self.filename, self.line, pos + 1)
            loc = loc_start - loc_end
            if self.state is State.NORMAL:
                # Normal state -- read tokens.
                if (need_white and match['whitespace'] is None and
                        match['rparen'] is None):
                    raise ReadError(f'{loc}: no whitespace between tokens')
                need_white = (match['whitespace'] is None and
                              match['lparen'] is None)
                if match['lparen'] is not None:
                    self.stack.append(StackEntryList(loc_start, []))
                elif match['rparen'] is not None:
                    if not self.stack:
                        raise ReadError(f'{loc}: unmatched close paren')
                    top = self.stack.pop()
                    if not isinstance(top, StackEntryList):
                        top.raise_unclosed_error()
                    yield from self._feed_node(top.items, top.start - loc_end)
                elif match['start_quote'] is not None:
                    self.state = State.STRING
                    self.token_start = loc_start
                    self.string_buffer = StringIO()
                    self.binarray_width = None
                elif match['symbol'] is not None:
                    value = Symbol(match['symbol'])
                    yield from self._feed_node(value, loc)
                elif match['sexpr_comment'] is not None:
                    self.stack.append(StackEntryComment(loc))
                elif match['bool_value'] is not None:
                    value = match['bool_value'] == '@true'
                    yield from self._feed_node(value, loc)
                elif match['nil_value'] is not None:
                    yield from self._feed_node(None, loc)
                elif match['int_or_word'] is not None:
                    value = int(match['int_or_word'], 0)
                    if match['word_width'] is not None:
                        width = int(match['word_width'])
                        if value < 0:
                            value += 1 << width
                        if value not in range(1 << width):
                            raise ReadError(f'{loc}: word value out of range')
                        value = BinWord(width, value)
                    yield from self._feed_node(value, loc)
                elif match['array_width'] is not None:
                    self.binarray_base = {
                        '0b': 2,
                        '0o': 8,
                        None: 10,
                        '0x': 16,
                    }[match['array_base']]
                    self.binarray_data = []
                    self.binarray_width = int(match['array_width'])
                    self.token_start = loc_start
                    self.state = State.BINARRAY
                    need_white = False
                elif match['string_width'] is not None:
                    self.binarray_width = int(match['string_width'])
                    self.token_start = loc_start
                    self.string_buffer = StringIO()
                    self.state = State.STRING
            elif self.state is State.STRING:
                # Inside a string.
                if match['end_quote'] is not None:
                    self.state = State.NORMAL
                    need_white = True
                    value = self.string_buffer.getvalue()
                    loc = self.token_start - loc_end
                    if self.binarray_width is not None:
                        vals = [ord(x) for x in value]
                        for x in vals:
                            if x not in range(1 << self.binarray_width):
                                raise ReadError(
                                        f'{loc}: character code out of range')
                        value = BinArray(vals, width=self.binarray_width)
                    yield from self._feed_node(value, loc)
                elif match['raw_chars'] is not None:
                    self.string_buffer.write(match['raw_chars'])
                elif match['simple_escape'] is not None:
                    c = ESCAPE_TO_CHAR[match['simple_escape']]
                    self.string_buffer.write(c)
                elif match['hex_code'] is not None:
                    code = int(match['hex_code'], 16)
                    if code not in range(0x110000):
                        raise ReadError(
                                f'{loc}: not a valid unicode codepoint')
                    self.string_buffer.write(chr(code))
                else:
                    assert 0
            elif self.state is State.BINARRAY:
                # In a BinArray.
                if match['rparen'] is not None:
                    self.state = State.NORMAL
                    value = BinArray(self.binarray_data,
                                     width=self.binarray_width)
                    loc = self.token_start - loc_end
                    yield from self._feed_node(value, loc)
                elif match['digits'] is not None:
                    if need_white:
                        raise ReadError(f'{loc}: no whitespace between tokens')
                    value = int(match['digits'], self.binarray_base)
                    if value < 0:
                        value += 1 << self.binarray_width
                    if value not in range(1 << self.binarray_width):
                        raise ReadError(f'{loc}: word value out of range')
                    self.binarray_data.append(value)
                need_white = match['whitespace'] is None
            else:
                assert 0

    def _feed_node(self, value, loc):
        """A helper method called when an S-expression has been recognized.
        Like feed_line, this is a generator that yields newly recognized
        top-level expressions.  If the reader is currently at the top level,
        simply yields the passed expression.  Otherwise, it appends it
        to whatever is currently being parsed and yields nothing.
        """
        node = make_node(value, loc)
        if not self.stack:
            yield node
        else:
            top = self.stack[-1]
            if isinstance(top, StackEntryList):
                top.items.append(node)
            elif isinstance(top, StackEntryComment):
                self.stack.pop()
            else:
                assert 0

    def finish(self):
        """Ensures the reader is in clean state (no unclosed S-expression
        is currently being parsed).  Should be called after the last
        ``feed_line``.
        """
        if self.state is not State.NORMAL:
            raise ReadError(f'EOF while in {self.state.name} state')
        if self.stack:
            top = self.stack[-1]
            top.raise_unclosed_error()


def read_file(file, filename='<input>'):
    """This is a generator that yields all top-level S-expression nodes from
    a given file object."""
    reader = Reader(filename)
    for line in file:
        yield from reader.feed_line(line)
    reader.finish()


def read_string(s, filename='<string>'):
    """Reads all S-expressions from a given string and returns a list
    of nodes."""
    return list(read_file(StringIO(s), filename))
