"""Unit tests for Snake game core logic."""

import curses
import random

import pytest

from snake_game import SnakeGame


class FakeWindow:
    """Minimal curses-like test double used by SnakeGame tests."""

    def __init__(self, height: int = 20, width: int = 40) -> None:
        self.height = height
        self.width = width
        self.keys = []

    def getmaxyx(self):
        return self.height, self.width

    def clear(self):
        return None

    def border(self):
        return None

    def addstr(self, _y, _x, _s):
        return None

    def addch(self, _y, _x, _ch):
        return None

    def refresh(self):
        return None

    def nodelay(self, _flag):
        return None

    def timeout(self, _millis):
        return None

    def keypad(self, _flag):
        return None

    def getch(self):
        if self.keys:
            return self.keys.pop(0)
        return -1


def create_game(height: int = 20, width: int = 40) -> SnakeGame:
    return SnakeGame(FakeWindow(height=height, width=width))


def test_reset_initializes_snake_and_food(monkeypatch: pytest.MonkeyPatch) -> None:
    game = create_game()
    monkeypatch.setattr(SnakeGame, "spawn_food", lambda _self: (1, 1))

    game.reset()

    assert len(game.snake) == 3
    assert game.snake[0] == (10, 20)
    assert game.direction == (0, 1)
    assert game.score == 0
    assert game.food == (1, 1)


def test_set_direction_ignores_reverse_direction() -> None:
    game = create_game()
    game.direction = (0, 1)

    game.set_direction(curses.KEY_LEFT)

    assert game.direction == (0, 1)


def test_tick_moves_without_growth() -> None:
    game = create_game()
    game.snake = [(5, 5), (5, 4), (5, 3)]
    game.direction = (0, 1)
    game.food = (1, 1)

    alive = game.tick()

    assert alive is True
    assert game.snake == [(5, 6), (5, 5), (5, 4)]
    assert game.score == 0


def test_tick_grows_and_increments_score(monkeypatch: pytest.MonkeyPatch) -> None:
    game = create_game()
    game.snake = [(5, 5), (5, 4), (5, 3)]
    game.direction = (0, 1)
    game.food = (5, 6)
    monkeypatch.setattr(SnakeGame, "spawn_food", lambda _self: (2, 2))

    alive = game.tick()

    assert alive is True
    assert game.snake == [(5, 6), (5, 5), (5, 4), (5, 3)]
    assert game.score == 1
    assert game.food == (2, 2)


def test_tick_allows_moving_into_previous_tail_cell() -> None:
    game = create_game()
    game.snake = [(3, 3), (3, 2), (4, 2), (4, 3)]
    game.direction = (1, 0)
    game.food = (10, 10)

    alive = game.tick()

    assert alive is True
    assert game.snake == [(4, 3), (3, 3), (3, 2), (4, 2)]


def test_tick_detects_wall_collision() -> None:
    game = create_game()
    game.snake = [(1, 5), (2, 5), (3, 5)]
    game.direction = (-1, 0)
    game.food = (10, 10)

    alive = game.tick()

    assert alive is False


def test_spawn_food_raises_when_board_is_full() -> None:
    game = create_game(height=4, width=4)
    game.height = 4
    game.width = 4
    game.snake = [(1, 1), (1, 2), (2, 1), (2, 2)]

    with pytest.raises(RuntimeError, match="No free cells"):
        game.spawn_food()


def test_tick_marks_win_when_board_becomes_full(monkeypatch: pytest.MonkeyPatch) -> None:
    game = create_game(height=4, width=4)
    game.height = 4
    game.width = 4
    game.snake = [(1, 1), (2, 1), (2, 2)]
    game.direction = (0, 1)
    game.food = (1, 2)

    def should_not_spawn(_self):
        raise AssertionError("spawn_food should not be called when board is full")

    monkeypatch.setattr(SnakeGame, "spawn_food", should_not_spawn)

    alive = game.tick()

    assert alive is False
    assert game.did_win is True
    assert game.score == 1


def test_spawn_food_skips_occupied_cells(monkeypatch: pytest.MonkeyPatch) -> None:
    game = create_game(height=6, width=6)
    game.height = 6
    game.width = 6
    game.snake = [(1, 1), (1, 2)]

    values = iter([1, 1, 2, 2])
    monkeypatch.setattr(random, "randint", lambda _a, _b: next(values))

    food = game.spawn_food()

    assert food == (2, 2)
