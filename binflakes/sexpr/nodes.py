from enum import Enum

from attr import attrs, attrib, validate, fields, NOTHING
from attr.validators import optional, instance_of

from binflakes.types import BinInt, BinWord, BinArray
from .location import TextLocationRange
from .string import escape_string
from .symbol import Symbol


class ConvertError(Exception):
    """Raised by Node subclass constructors when given value cannot
    be represented as an instance of a given class.
    """
    pass


def _unwrap(value, location=None):
    """A helper function for Node subclass constructors -- if ``value``
    is a Node instance, extracts raw Python value and location from it,
    and returns them as a tuple.  Otherwise, ensures that ``value`` is
    of a type representable by S-expressions and returns it along with
    explicitly-passed location, if any.
    """
    if isinstance(value, Node) and location is not None:
        raise TypeError(
                'explicit location should only be given for bare values')
    if isinstance(value, AtomNode):
        return value.value, value.location
    if isinstance(value, ListNode):
        return value.items, value.location
    if isinstance(value, FormNode):
        return value.to_list(), value.location
    if value is None or isinstance(value, (
            bool, BinInt, BinWord, BinArray, str, Symbol, tuple)):
        return value, location
    if isinstance(value, list):
        return tuple(value), location
    if isinstance(value, int):
        return BinInt(value), location
    raise TypeError(
            f'{type(value).__name__} is not representable by S-expressions.')


@attrs(slots=True, init=False)
class Node:
    """Represents a parsed S-expression node.  Abstract base class.
    There are four immediately derived classes:

    - ``AtomNode``: represents atomic value nodes (everything except lists).
    - ``ListNode``: represents lists of values of uniform type.
    - ``FormNode``: represents forms -- compound nodes represented in
      S-expression files by a list starting from a preset symbol and followed
      by pre-defined arguments of possibly non-uniform types.
    - ``AlternativesNode``: a pseudo-class representing an alternative of
      several disjoint node types.  Cannot be instantiated -- when constructor
      is called, the value is matched to one of the contained node type
      and an instance of the found type is returned instead.

    This module provides a base class for every supported atom type, as well
    as a generic list type and alternatives type.  These classes can be
    used to represent any S-expression and are returned by the reader.
    To create an S-expression based language, one can create a hierarchy
    of custom node subclasses and call the top node constructor on the generic
    tree returned by the reader -- it will be resursively converted to the
    custom node set.
    """

    location = attrib(validator=optional(instance_of(TextLocationRange)),
                      cmp=False)

    def __init__(self, value, location=None):
        """Converts a value to an instance of this class, recursively
        converting subnodes as necessary.  The input value can be another
        compatible Node instance, or a bare Python value of the corresponding
        type.

        Can be used to convert a bare Python value to a node tree, a generic
        node tree to a specific node tree, or a specific node tree back to
        a generic node tree.
        """
        raise NotImplementedError


@attrs(slots=True, init=False)
class AtomNode(Node):
    """Represents a parsed atomic S-expression node (i.e. anything but a list).
    Abstract base class.  Subclasses need to define ``value_type`` class
    attribute.  No new direct subclasses should be defined by the user
    (all types need direct support from the base machinery), but the derived
    types can be arbitrarily subclassed further for extra methods.
    """

    value = attrib()

    def __init__(self, value, location=None):
        self.value, self.location = _unwrap(value, location)
        validate(self)

    @value.validator
    def _value_validate(self, attribute, value):
        if not isinstance(value, self.value_type):
            raise ConvertError(
                    f'{self.location}: expected {self.value_type.__name__}')


@attrs(slots=True, init=False)
class SymbolNode(AtomNode):
    """Represents a symbol S-expression."""

    value_type = Symbol

    def __str__(self):
        return str(self.value)


@attrs(slots=True, init=False)
class NilNode(AtomNode):
    """Represents a nil S-expression."""

    value_type = type(None)

    def __init__(self, value=None, location=None):
        super().__init__(value, location)

    def __str__(self):
        return '@nil'


@attrs(slots=True, init=False)
class BoolNode(AtomNode):
    """Represents a bool S-expression."""

    value_type = bool

    def __str__(self):
        return '@true' if self.value else '@false'


@attrs(slots=True, init=False)
class IntNode(AtomNode):
    """Represents an int S-expression."""

    value_type = BinInt

    def __str__(self):
        return str(self.value)


@attrs(slots=True, init=False)
class WordNode(AtomNode):
    """Represents a word S-expression."""

    value_type = BinWord

    def __str__(self):
        return str(self.value)


@attrs(slots=True, init=False)
class ArrayNode(AtomNode):
    """Represents an array S-expression."""

    value_type = BinArray

    def __str__(self):
        return str(self.value)


@attrs(slots=True, init=False)
class StringNode(AtomNode):
    """Represents a string S-expression."""

    value_type = str

    def __str__(self):
        return escape_string(self.value)


ATOM_TYPES = [
    SymbolNode,
    NilNode,
    BoolNode,
    IntNode,
    WordNode,
    ArrayNode,
    StringNode,
]


@attrs(slots=True, init=False)
class ListNode(Node):
    """Represents a uniform list S-expression.  Abstract base class --
    should be subclassed with ``item_type`` class attribute set to the type of
    list items.
    """

    items = attrib(validator=instance_of(tuple))

    def __init__(self, value, location=None):
        items, self.location = _unwrap(value, location)
        if not isinstance(items, tuple):
            raise ConvertError(f'{self.location}: expected a list')
        self.items = tuple(
            self.item_type(item)
            for item in items
        )
        validate(self)

    def __str__(self):
        items = ' '.join(str(x) for x in self.items)
        return f'({items})'


class _FormArgMode(Enum):
    REQUIRED = 'required'
    OPTIONAL = 'optional'
    REST = 'rest'


def form_node(cls):
    """A class decorator to finalize fully derived FormNode subclasses."""
    assert issubclass(cls, FormNode)
    res = attrs(init=False, slots=True)(cls)
    res._args = []
    res._required_args = 0
    res._rest_arg = None
    state = _FormArgMode.REQUIRED
    for field in fields(res):
        if 'arg_mode' in field.metadata:
            if state is _FormArgMode.REST:
                raise RuntimeError('rest argument must be last')
            if field.metadata['arg_mode'] is _FormArgMode.REQUIRED:
                if state is _FormArgMode.OPTIONAL:
                    raise RuntimeError('required arg after optional arg')
                res._args.append(field)
                res._required_args += 1
            elif field.metadata['arg_mode'] is _FormArgMode.OPTIONAL:
                state = _FormArgMode.OPTIONAL
                res._args.append(field)
            elif field.metadata['arg_mode'] is _FormArgMode.REST:
                state = _FormArgMode.REST
                res._rest_arg = field
            else:
                assert 0
    return res


def form_arg(arg_type):
    """Defines a required form argument of a given node type."""
    return attrib(metadata={
        'arg_type': arg_type,
        'arg_mode': _FormArgMode.REQUIRED,
    })


def form_optional_arg(arg_type):
    """Defines an optional form argument of a given node type.
    If not passed, it is set to None.  All optional arguments
    must come after all required arguments.
    """
    return attrib(metadata={
        'arg_type': arg_type,
        'arg_mode': _FormArgMode.OPTIONAL,
    })


def form_rest_arg(arg_type):
    """Defines a ``rest`` form argument.  All form arguments not consumed
    by required and optional arguments will be converted to the given node
    type and gathered into a tuple.  There can be at most one rest argument
    and it must be the last defined form argument.
    """
    return attrib(metadata={
        'arg_type': arg_type,
        'arg_mode': _FormArgMode.REST,
    })


@attrs(slots=True, init=False)
class FormNode(Node):
    """An abstract base class for form nodes.  Final subclasses need to
    set a ``symbol`` class attribute, define zero or more form arguments,
    and call the ``@form_node`` decorator on the class.
    """
    symbol_location = attrib(
            validator=optional(instance_of(TextLocationRange)), cmp=False)

    def __init__(self, value=NOTHING, location=None, symbol_location=None,
                 **kwargs):
        """Constructs a FormNode instance from a value and location (where
        value is a list node, or a plain list), or directly from argument
        values::

            AbcNode([Symbol('abc'), 123, 'def'], TextLocationRange(...))
            AbcNode(my_arg=123, my_other_arg='def', location=...)
        """
        if not hasattr(self, 'symbol'):
            raise RuntimeError('constructing abstract FormNode')
        if value is not NOTHING:
            if kwargs:
                raise TypeError(
                    'cannot construct FormNode from both a value and kwargs')
            value, self.location = _unwrap(value, location)
            if not isinstance(value, tuple):
                raise ConvertError(f'{self.location}: expected a list')
            if not value:
                raise ConvertError(f'{self.location}: empty form')
            symbol, self.symbol_location = _unwrap(value[0], symbol_location)
            if not isinstance(symbol, Symbol):
                raise ConvertError(
                    f'{location}: form must start with a symbol')
            if symbol != self.symbol:
                raise ConvertError(
                    f'{location}: expected form ({self.symbol})')
            if len(value) - 1 < self._required_args:
                raise ConvertError(
                        f'{location}: too few arguments to form {self.symbol}')
            for arg, val in zip(self._args, value[1:]):
                kwargs[arg.name] = val
            extra = value[len(self._args) + 1:]
            if self._rest_arg is not None:
                kwargs[self._rest_arg.name] = extra
            elif extra:
                raise ConvertError(
                    f'{self.location}: too many arguments '
                    f'to form {self.symbol}')
        else:
            self.location = location
            self.symbol_location = symbol_location
        was_missing = False
        for field in fields(type(self)):
            if 'arg_type' in field.metadata:
                arg_mode = field.metadata['arg_mode']
                arg_type = field.metadata['arg_type']
                if field.name in kwargs:
                    value = kwargs.pop(field.name)
                    if arg_mode is _FormArgMode.REQUIRED:
                        value = arg_type(value)
                    elif arg_mode is _FormArgMode.OPTIONAL:
                        if value is not None:
                            value = arg_type(value)
                    elif arg_mode is _FormArgMode.REST:
                        value = tuple(
                            arg_type(x)
                            for x in value
                        )
                    else:
                        assert 0
                elif arg_mode is _FormArgMode.REQUIRED:
                    raise TypeError(
                            f'{location}: no value for {field.name}')
                elif arg_mode is _FormArgMode.OPTIONAL:
                    value = None
                elif arg_mode is _FormArgMode.REST:
                    value = ()
                else:
                    assert 0
                if value is None:
                    was_missing = True
                elif was_missing and value != ():
                    raise TypeError(
                            'passing argument after a missing argument')
            elif field.name in ('location', 'symbol_location'):
                # already set before
                continue
            else:
                assert 0
            setattr(self, field.name, value)
        if kwargs:
            arg = kwargs.popitem()[0]
            raise TypeError(f'unknown field {arg}')
        validate(self)

    def to_list(self):
        """Converts a parsed form back to a tuple of S-expressions it was
        made from.
        """
        res = [SymbolNode(self.symbol, self.symbol_location)]
        for arg in self._args:
            val = getattr(self, arg.name)
            if val is not None:
                res.append(val)
        if self._rest_arg is not None:
            res += getattr(self, self._rest_arg.name)
        return tuple(res)

    def __str__(self):
        items = ' '.join(str(x) for x in self.to_list())
        return f'({items})'


class _AlternativesMeta(type):
    """A simple metaclass for AlternativesNode to make isinstance work.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'alternatives'):
            self.set_alternatives(self.alternatives)

    def __instancecheck__(self, instance):
        for alt in getattr(self, '_alternatives', []):
            if isinstance(instance, alt):
                return True
        return False


class AlternativesNode(metaclass=_AlternativesMeta):
    """A base for making node pseudo-classes that, when "created", match
    the passed value to one of a given list of node subclasses and call
    the constructor of the matching one, if any.

    If all involved node types are already defined on subclass creation,
    the list of supported node types can be set through the ``alternatives``
    class attribute::

        class MyAlternativesNode(AlternativesNode):
            alternatives = [
                MyNode,
                AnotherNode,
            ]

    If one of the node types isn't yet defined when a subclass is constructed,
    the node types can be set later through the ``set_alternatives`` class
    method::

        class MyAlternativesNode(AlternativesNode):
            pass

        class MyNode(...):
            ...

        MyAlternativesNode.set_alternatives([
            MyNode,
            AnotherNode,
        ])

    The alternatives specified must be mutually exclusive, as follows:

    - There must be at most one alternative for each atom type.
    - There must be at most one of the following:

      - A ListNode subtype.
      - Any number of FormNode subtypes, with distinct symbols.

    - If any AlternativeNode subclass is specified in alternatives, it's
      as if all alternatives of that class were specified directly in its
      place.
    """

    def __new__(cls, value, location=None):
        if not hasattr(cls, '_alternatives'):
            raise RuntimeError('AlternativesNode subclass not initialized')
        value, location = _unwrap(value, location)
        for atom_type in ATOM_TYPES:
            if isinstance(value, atom_type.value_type):
                if atom_type in cls._atom_types:
                    return cls._atom_types[atom_type](value, location)
                else:
                    raise ConvertError(
                            f'{location}: {atom_type.__name__} not allowed')
        assert isinstance(value, tuple)
        if cls._list_type is not None:
            return cls._list_type(value, location)
        if not value:
            raise ConvertError(f'{location}: empty form')
        symbol, symbol_location = _unwrap(value[0])
        if not isinstance(symbol, Symbol):
            raise ConvertError(
                f'{location}: form must start with a symbol')
        if symbol not in cls._form_types:
            available = ', '.join(str(sym) for sym in cls._form_types)
            raise ConvertError(f'{location}: unknown form {symbol}'
                               f' (available forms: {available})')
        return cls._form_types[symbol](value, location)

    @classmethod
    def set_alternatives(cls, alternatives):
        if hasattr(cls, '_alternatives'):
            raise RuntimeError('AlternativesNode subclass initialized twice')
        cls._atom_types = {}
        cls._list_type = None
        cls._form_types = {}
        cls._alternatives = []
        for alt in alternatives:
            if isinstance(alt, _AlternativesMeta):
                cls._alternatives += alt._alternatives
            else:
                cls._alternatives.append(alt)
        for alt in cls._alternatives:
            for atom_type in ATOM_TYPES:
                if issubclass(alt, atom_type):
                    if atom_type in cls._atom_types:
                        raise RuntimeError(
                                f'Two alternatives for {atom_type.__name__}')
                    cls._atom_types[atom_type] = alt
                    break
            else:
                if issubclass(alt, ListNode):
                    if cls._list_type is not None:
                        raise RuntimeError('Two alternatives for list')
                    cls._list_type = alt
                elif issubclass(alt, FormNode):
                    if alt.symbol in cls._form_types:
                        raise RuntimeError(
                            f'Two alternatives for form {alt.symbol}')
                    cls._form_types[alt.symbol] = alt
                else:
                    raise RuntimeError(f'unknown alternative type {alt}')
        if cls._list_type and cls._form_types:
            raise RuntimeError('cannot have both FormNodes and a ListNode')


class GenericNode(AlternativesNode):
    """A node pseudo-type representing any of the generic node types."""
    pass


@attrs(slots=True, init=False)
class GenericListNode(ListNode):
    """Represents a generic list S-expression -- items can be of any
    generic node type.
    """
    item_type = GenericNode


GenericNode.set_alternatives([
    GenericListNode,
    SymbolNode,
    NilNode,
    BoolNode,
    IntNode,
    WordNode,
    ArrayNode,
    StringNode,
])
