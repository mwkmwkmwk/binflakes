import pytest

from binflakes.sexpr.string import escape_string


class TestString:
    @pytest.mark.parametrize(('orig', 'escaped'), [
        ('abc', '"abc"'),
        ('abc "def" ghi', '"abc \\"def\\" ghi"'),
        ('abc \\ def', '"abc \\\\ def"'),
        ('abc \a\b\t\n\f\r\v\x1b def', '"abc \\a\\b\\t\\n\\f\\r\\x0b\\e def"'),
        ('abc \x00\x7f\uffff\U0010ffff def',
         '"abc \\x00\\x7f\\uffff\\U10ffff def"'),
    ])
    def test_escape(self, orig, escaped):
        assert escape_string(orig) == escaped
