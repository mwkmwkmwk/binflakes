from io import StringIO

ESCAPE_TO_CHAR = {
    'a': '\a',
    'b': '\b',
    't': '\t',
    'n': '\n',
    'f': '\f',
    'r': '\r',
    'e': '\x1b',
    '\\': '\\',
    '"': '"',
}

CHAR_TO_ESCAPE = {v: k for k, v in ESCAPE_TO_CHAR.items()}


def escape_string(value):
    """Converts a string to its S-expression representation, adding quotes
    and escaping funny characters.
    """
    res = StringIO()
    res.write('"')
    for c in value:
        if c in CHAR_TO_ESCAPE:
            res.write(f'\\{CHAR_TO_ESCAPE[c]}')
        elif c.isprintable():
            res.write(c)
        elif ord(c) < 0x100:
            res.write(f'\\x{ord(c):02x}')
        elif ord(c) < 0x10000:
            res.write(f'\\u{ord(c):04x}')
        else:
            res.write(f'\\U{ord(c):06x}')
    res.write('"')
    return res.getvalue()
