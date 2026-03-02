#!/usr/bin/env python3
import curses
import random
from typing import List, Tuple


Point = Tuple[int, int]


class SnakeGame:
    def __init__(self, stdscr: "curses._CursesWindow") -> None:
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        self.min_height = 10
        self.min_width = 20
        self.snake: List[Point] = []
        self.direction: Point = (0, 1)
        self.food: Point = (0, 0)
        self.score = 0
        self.speed_ms = 110

    def reset(self) -> None:
        self.height, self.width = self.stdscr.getmaxyx()
        if self.height < self.min_height or self.width < self.min_width:
            raise ValueError("Terminal too small. Minimum size is 20x10.")

        center_y = self.height // 2
        center_x = self.width // 2
        self.snake = [
            (center_y, center_x),
            (center_y, center_x - 1),
            (center_y, center_x - 2),
        ]
        self.direction = (0, 1)
        self.score = 0
        self.food = self.spawn_food()

    def spawn_food(self) -> Point:
        while True:
            y = random.randint(1, self.height - 2)
            x = random.randint(1, self.width - 2)
            if (y, x) not in self.snake:
                return (y, x)

    def draw(self) -> None:
        self.stdscr.clear()
        self.stdscr.border()
        self.stdscr.addstr(0, 2, f" Score: {self.score} ")
        self.stdscr.addch(self.food[0], self.food[1], "*")

        head = self.snake[0]
        self.stdscr.addch(head[0], head[1], "@")
        for segment in self.snake[1:]:
            self.stdscr.addch(segment[0], segment[1], "o")

        self.stdscr.refresh()

    def set_direction(self, key: int) -> None:
        mapping = {
            curses.KEY_UP: (-1, 0),
            curses.KEY_DOWN: (1, 0),
            curses.KEY_LEFT: (0, -1),
            curses.KEY_RIGHT: (0, 1),
        }
        if key not in mapping:
            return

        next_direction = mapping[key]
        if (next_direction[0] == -self.direction[0] and next_direction[1] == -self.direction[1]):
            return
        self.direction = next_direction

    def tick(self) -> bool:
        head_y, head_x = self.snake[0]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)

        hit_wall = new_head[0] <= 0 or new_head[0] >= self.height - 1 or new_head[1] <= 0 or new_head[1] >= self.width - 1
        hit_self = new_head in self.snake
        if hit_wall or hit_self:
            return False

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        return True

    def game_over_screen(self) -> str:
        msg1 = "GAME OVER"
        msg2 = f"Final Score: {self.score}"
        msg3 = "Press R to restart or Q to quit"

        self.stdscr.nodelay(False)
        self.stdscr.clear()
        self.stdscr.border()

        center_y = self.height // 2
        self.stdscr.addstr(center_y - 1, max(1, (self.width - len(msg1)) // 2), msg1)
        self.stdscr.addstr(center_y, max(1, (self.width - len(msg2)) // 2), msg2)
        self.stdscr.addstr(center_y + 1, max(1, (self.width - len(msg3)) // 2), msg3)
        self.stdscr.refresh()

        while True:
            key = self.stdscr.getch()
            if key in (ord("r"), ord("R")):
                return "restart"
            if key in (ord("q"), ord("Q")):
                return "quit"

    def run(self) -> None:
        while True:
            self.reset()
            self.stdscr.nodelay(True)
            self.stdscr.timeout(self.speed_ms)

            while True:
                self.draw()
                key = self.stdscr.getch()
                if key in (ord("q"), ord("Q")):
                    return
                self.set_direction(key)
                if not self.tick():
                    break

            action = self.game_over_screen()
            if action == "quit":
                return


def main(stdscr: "curses._CursesWindow") -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        # Some terminals do not support cursor visibility changes.
        pass
    stdscr.keypad(True)

    game = SnakeGame(stdscr)
    try:
        game.run()
    except ValueError as err:
        stdscr.clear()
        stdscr.addstr(0, 0, str(err))
        stdscr.addstr(2, 0, "Resize the terminal and try again.")
        stdscr.addstr(4, 0, "Press any key to exit.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
