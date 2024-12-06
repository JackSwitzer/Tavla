import pytest
from game.types import Point, Player

class TestPoint:
    def test_empty_point(self):
        point = Point()
        assert point.count == 0
        assert point.color is None
        assert point.is_empty
        assert not point.is_blot

    def test_white_point(self):
        point = Point(2)
        assert point.count == 2
        assert point.color == Player.WHITE
        assert not point.is_empty
        assert not point.is_blot

    def test_black_point(self):
        point = Point(-3)
        assert point.count == -3
        assert point.color == Player.BLACK
        assert not point.is_empty
        assert not point.is_blot

    def test_blot(self):
        white_blot = Point(1)
        black_blot = Point(-1)
        assert white_blot.is_blot
        assert black_blot.is_blot

    def test_invalid_count(self):
        with pytest.raises(ValueError):
            Point(16)  # Max is 15
        with pytest.raises(ValueError):
            Point(-16) 