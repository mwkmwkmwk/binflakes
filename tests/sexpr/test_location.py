from binflakes.sexpr.location import TextLocationSingle, TextLocationRange


class TestLocation:
    def test_single(self):
        a = TextLocationSingle('abc.binflake', 13, 4)
        assert a.filename == 'abc.binflake'
        assert a.line == 13
        assert a.column == 4
        assert str(a) == 'abc.binflake:13:4'

    def test_range(self):
        a = TextLocationRange('abc.binflake', 13, 4, 14, 2)
        b = TextLocationRange('abc.binflake', 13, 4, 13, 8)
        assert a.filename == b.filename == 'abc.binflake'
        assert a.start_line == 13
        assert a.start_column == 4
        assert a.end_line == 14
        assert a.end_column == 2
        assert b.start_line == 13
        assert b.start_column == 4
        assert b.end_line == 13
        assert b.end_column == 8
        assert str(a) == 'abc.binflake:13:4-14:2'
        assert str(b) == 'abc.binflake:13:4-8'
        sa = TextLocationSingle('abc.binflake', 13, 4)
        sb = TextLocationSingle('abc.binflake', 14, 3)
        assert sa - sb == a
