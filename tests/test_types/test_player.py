import pytest
from game.types import Player

def test_player_opponent():
    assert Player.WHITE.opponent == Player.BLACK
    assert Player.BLACK.opponent == Player.WHITE

def test_player_value():
    assert Player.WHITE.value == "white"
    assert Player.BLACK.value == "black"

def test_player_equality():
    assert Player.WHITE == Player.WHITE
    assert Player.BLACK == Player.BLACK
    assert Player.WHITE != Player.BLACK 