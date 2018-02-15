import unittest

from binflakes.sexpr.string import escape_string


class TestString(unittest.TestCase):
    def test_escape(self):
        assert escape_string('abc') == '"abc"'
        assert escape_string('abc "def" ghi') == '"abc \\"def\\" ghi"'
        assert escape_string('abc \\ def') == '"abc \\\\ def"'
        assert (escape_string('abc \a\b\t\n\f\r\v\x1b def') ==
                '"abc \\a\\b\\t\\n\\f\\r\\x0b\\e def"')
        assert (escape_string('abc \x00\x7f\uffff\U0010ffff def') ==
                '"abc \\x00\\x7f\\uffff\\U10ffff def"')
