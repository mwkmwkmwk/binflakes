from attr import attrs, attrib
from attr.validators import instance_of


@attrs(slots=True, frozen=True)
class Symbol:
    """Represents an S-expression symbol."""
    name = attrib(validator=instance_of(str))

    def __str__(self):
        return self.name
