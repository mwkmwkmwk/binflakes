import re

from attr import attrs, attrib


@attrs(slots=True, frozen=True)
class Symbol:
    """Represents an S-expression symbol."""
    name = attrib()

    NAME_PATTERN = re.compile(
            r'[a-zA-Z*+=<>!?/$%_][0-9a-zA-Z*+=<>!?/$%_-]*|-')

    @name.validator
    def _validate_name(self, attribute, value):
        if not isinstance(value, str):
            raise TypeError('symbol name must be a string')
        if not self.NAME_PATTERN.fullmatch(value):
            raise ValueError(f'symbol name {value} is not valid')

    def __str__(self):
        return self.name
