from attr import attrs, attrib
from attr.validators import optional, instance_of

from binflakes.types import BinInt, BinWord, BinArray
from .location import TextLocationRange
from .string import escape_string
from .symbol import Symbol


@attrs(slots=True)
class Node:
    """Represents a parsed S-expression node.  Abstract base class."""


def _location_attrib():
    """Makes a location attribute.  Not included in the base class, so that
    it comes last and can be easily skipped in __init__.
    """
    return attrib(validator=optional(instance_of(TextLocationRange)),
                  default=None, cmp=False)


@attrs(slots=True)
class ListNode(Node):
    """Represents a list S-expression."""

    items = attrib()
    location = _location_attrib()

    @items.validator
    def _items_check(self, attribute, value):
        if not isinstance(value, list):
            raise TypeError
        for item in value:
            if not isinstance(item, Node):
                raise TypeError

    def __str__(self):
        items = ' '.join(str(x) for x in self.items)
        return f'({items})'


@attrs(slots=True)
class SymbolNode(Node):
    """Represents a symbol S-expression."""

    value = attrib(validator=instance_of(Symbol))
    location = _location_attrib()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class NilNode(Node):
    """Represents a nil S-expression."""

    value = None
    location = _location_attrib()

    def __str__(self):
        return '@nil'


@attrs(slots=True)
class BoolNode(Node):
    """Represents a bool S-expression."""

    value = attrib(validator=instance_of(bool))
    location = _location_attrib()

    def __str__(self):
        return '@true' if self.value else '@false'


@attrs(slots=True)
class IntNode(Node):
    """Represents an int S-expression."""

    value = attrib(validator=instance_of(BinInt))
    location = _location_attrib()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class WordNode(Node):
    """Represents a word S-expression."""

    value = attrib(validator=instance_of(BinWord))
    location = _location_attrib()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class ArrayNode(Node):
    """Represents an array S-expression."""

    value = attrib(validator=instance_of(BinArray))
    location = _location_attrib()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class StringNode(Node):
    """Represents a string S-expression."""

    value = attrib(validator=instance_of(str))
    location = _location_attrib()

    def __str__(self):
        return escape_string(self.value)


def make_node(val, loc=None):
    """Converts a bare Python value to a corresponding Node, recursively
    if needed.
    """
    if isinstance(val, Node):
        return val
    if isinstance(val, Symbol):
        return SymbolNode(val, loc)
    if val is None:
        return NilNode(loc)
    if isinstance(val, bool):
        return BoolNode(val, loc)
    if isinstance(val, (BinInt, int)):
        return IntNode(BinInt(val), loc)
    if isinstance(val, BinWord):
        return WordNode(val, loc)
    if isinstance(val, BinArray):
        return ArrayNode(val, loc)
    if isinstance(val, str):
        return StringNode(val, loc)
    if isinstance(val, (list, tuple)):
        val = [
            make_node(x)
            for x in val
        ]
        return ListNode(val, loc)
    raise TypeError('cannot serialize to S-expr')
