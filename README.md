# Simple Terminal Snake Game

A terminal-based Snake game written in Python using `curses`.

## Features

- Arrow key movement
- Live score display
- Wall and self-collision detection
- Restart option after game over
- Win condition when the board is fully filled

## Requirements

- Python 3.8+
- `curses` (built-in on macOS/Linux)
- On Windows, install dependency from `requirements.txt`
- `pytest` for running tests

## Run

```bash
python snake_game.py
```

## Test

```bash
pytest -q
```

## Controls

- `↑` move up
- `↓` move down
- `←` move left
- `→` move right
- `Q` quit game
- On game over:
  - `R` restart
  - `Q` quit
