from binflakes.types import BinWord


def test_conflict():
    assert str(BinWord(12, 0x123)) == '#12x123'
