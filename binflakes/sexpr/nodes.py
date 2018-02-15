from attr import attrs, attrib
from attr.validators import optional, instance_of

from binflakes.types import BinInt, BinWord, BinArray

from .location import TextLocationRange
from .string import escape_string
from .symbol import Symbol


class Node:
    """Represents a parsed S-expression node.  Abstract base class."""


def _location_attr():
    """Makes a location argument.  Not included in the base class, so that
    it comes last and can be easily skipped in __init__.
    """
    return attrib(validator=optional(instance_of(TextLocationRange)),
                  default=None, cmp=False)


@attrs(slots=True)
class NodeList(Node):
    """Represents a list S-expression."""

    items = attrib()
    location = _location_attr()

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
class NodeSymbol(Node):
    """Represents a symbol S-expression."""

    value = attrib(validator=instance_of(Symbol))
    location = _location_attr()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class NodeNil(Node):
    """Represents a nil S-expression."""

    value = None
    location = _location_attr()

    def __str__(self):
        return '@nil'


@attrs(slots=True)
class NodeBool(Node):
    """Represents a bool S-expression."""

    value = attrib(validator=instance_of(bool))
    location = _location_attr()

    def __str__(self):
        return '@true' if self.value else '@false'


@attrs(slots=True)
class NodeInt(Node):
    """Represents an int S-expression."""

    value = attrib(validator=instance_of(BinInt))
    location = _location_attr()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class NodeWord(Node):
    """Represents a word S-expression."""

    value = attrib(validator=instance_of(BinWord))
    location = _location_attr()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class NodeArray(Node):
    """Represents an array S-expression."""

    value = attrib(validator=instance_of(BinArray))
    location = _location_attr()

    def __str__(self):
        return str(self.value)


@attrs(slots=True)
class NodeString(Node):
    """Represents a string S-expression."""

    value = attrib(validator=instance_of(str))
    location = _location_attr()

    def __str__(self):
        return escape_string(self.value)


def make_node(val, loc=None):
    """Converts a bare python value to a corresponding Node, recursively
    if needed.
    """
    if isinstance(val, Node):
        return val
    if isinstance(val, Symbol):
        return NodeSymbol(val, loc)
    if val is None:
        return NodeNil(loc)
    if isinstance(val, bool):
        return NodeBool(val, loc)
    if isinstance(val, (BinInt, int)):
        return NodeInt(BinInt(val), loc)
    if isinstance(val, BinWord):
        return NodeWord(val, loc)
    if isinstance(val, BinArray):
        return NodeArray(val, loc)
    if isinstance(val, str):
        return NodeString(val, loc)
    if isinstance(val, (list, tuple)):
        val = [
            make_node(x)
            for x in val
        ]
        return NodeList(val, loc)
    raise TypeError('cannot serialize to S-expr')
