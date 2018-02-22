from attr import attrs, attrib
from attr.validators import instance_of


@attrs(slots=True)
class TextLocationSingle:
    """Represents a single (filename, line, column) location in the input."""

    filename = attrib(validator=instance_of(str))
    line = attrib(validator=instance_of(int))
    column = attrib(validator=instance_of(int))

    def __str__(self):
        return f'{self.filename}:{self.line}:{self.column}'

    def __sub__(self, other):
        """Returns a TextLocationRange corresponding to the range starting
        from the first single location (included) until the second single
        location (excluded).
        """
        assert self.filename == other.filename
        assert (self.line, self.column) <= (other.line, other.column)
        return TextLocationRange(
            self.filename, self.line, self.column,
            other.line, other.column - 1,
        )


@attrs(slots=True)
class TextLocationRange:
    """Represents a range of locations in one input file, with both endpoints
    included.
    """
    filename = attrib(validator=instance_of(str))
    start_line = attrib(validator=instance_of(int))
    start_column = attrib(validator=instance_of(int))
    end_line = attrib(validator=instance_of(int))
    end_column = attrib(validator=instance_of(int))

    def __str__(self):
        if self.start_line == self.end_line:
            return (f'{self.filename}:{self.start_line}:'
                    f'{self.start_column}-{self.end_column}')
        else:
            return (f'{self.filename}:{self.start_line}:{self.start_column}-'
                    f'{self.end_line}:{self.end_column}')
