*This project has been created as part of the 42 curriculum by zhaouzan, abchahid*

# A-Maze-ing

## Description

A-Maze-ing is an interactive terminal maze generator and solver built in Python.
The program reads a configuration file, generates a random maze using either a
Depth-First Search (DFS) or Prim's algorithm, renders it live in the terminal with
`curses`, solves it with BFS, and writes the result to a hex-encoded output file.

Key features:
- Two generation algorithms: **DFS** (recursive backtracker) and **Prim's**
- **Perfect maze** mode — exactly one path between entry and exit
- **BFS** shortest-path solver
- A **"42" logo** pattern embedded in the centre of the maze
- **Hex-encoded** output file with solution directions (N / S / E / W)
- 6 built-in **colour schemes** — cycle them live with key `3`
- Reusable `mazegen` pip-installable package 

---

## Instructions

### Requirements

- Python **3.10 or later**
- No third-party runtime dependencies (`curses` is part of the standard library)
- `flake8` and `mypy` for linting (dev only)

### Installation

```bash
make install        # installs flake8 and mypy from requirements.txt
```

### Running

```bash
python3 a_maze_ing.py config.txt
# or
make run
```

### Debug mode

```bash
make debug
```

### Lint

```bash
make lint           # flake8 + mypy with standard flags
make lint-strict    # flake8 + mypy --strict
```

### Clean

```bash
make clean          # removes __pycache__, .mypy_cache, etc.
```

### Controls (inside the terminal UI)

| Key | Action                                |
|-----|---------------------------------------|
| `1` | Generate / re-generate the maze       |
| `2` | Show / hide the BFS solution path     |
| `3` | Cycle through 6 wall colour schemes   |
| `4` | Quit                                  |

---

## Configuration File Format

The configuration file uses one `KEY=VALUE` pair per line.
Lines starting with `#` are treated as comments and are ignored.
Keys and values **must not** contain spaces or tabs.

| Key           | Required | Description                                             | Example                   |
|---------------|----------|---------------------------------------------------------|---------------------------|
| `WIDTH`       | YES      | Number of columns (cells), must be > 0                  | `WIDTH=20`                |
| `HEIGHT`      | YES      | Number of rows (cells), must be > 0                     | `HEIGHT=15`               |
| `ENTRY`       | YES      | Entry cell as `x,y` (col, row), 0-indexed               | `ENTRY=0,0`               |
| `EXIT`        | YES      | Exit cell as `x,y` (col, row), 0-indexed                | `EXIT=19,14`              |
| `OUTPUT_FILE` | YES      | Output filename, must have `.txt` extension             | `OUTPUT_FILE=maze.txt`    |
| `PERFECT`     | YES      | `True` = one unique solution, `False` = multi-path      | `PERFECT=True`            |
| `ALGO`        | NO       | Generation algorithm: `DFS` or `PRIME` (default: `DFS`) | `ALGO=DFS`               |
| `SEED`        | NO       | Integer seed for reproducible mazes                     | `SEED=42`                 |

**Validation rules enforced by the parser:**
- `WIDTH` and `HEIGHT` must be positive integers greater than 0.
- `ENTRY` and `EXIT` must be within maze bounds and must not be the same cell.
- `PERFECT` must be exactly `True` or `False` (case-sensitive).
- `OUTPUT_FILE` must end with `.txt`.
- `SEED` is optional; any non-integer value is silently treated as no seed.
- Lines with more than one `=` sign or no `=` sign raise a `ValueError`.

**Minimum maze size for the "42" pattern:** `WIDTH >= 9` and `HEIGHT >= 7`.

Example `config.txt`:

```ini
# A-Maze-ing configuration
WIDTH=16
HEIGHT=16
ENTRY=0,0
EXIT=15,15
OUTPUT_FILE=output_maze.txt
PERFECT=False
ALGO=PRIME
SEED=42
```

---

## Output File Format

The maze is written row by row, one hex character per cell.
Each hex digit encodes which walls are **closed** using this bitmask:

| Bit     | Value | Direction      |
|---------|-------|----------------|
| 0 (LSB) | 1     | North (Top)    |
| 1       | 2     | East  (Right)  |
| 2       | 4     | South (Bottom) |
| 3       | 8     | West  (Left)   |

A closed wall sets the bit to `1`; open means `0`.

After a blank line, the file contains three more lines:
1. Entry coordinates as `x,y`
2. Exit coordinates as `x,y`
3. BFS shortest path as a string of `N`, `S`, `E`, `W` characters

All lines end with `\n`.

Example:
```
9515391539551795151151153
...

0,0
15,15
SSSEEENNNSEEE...
```

---

## Algorithms

### DFS - Depth-First Search (Recursive Backtracker)

Starting from the entry cell, the algorithm picks a random unvisited neighbour,
removes the wall between them, and recurses. When it reaches a dead end it
backtracks. This produces mazes with **long, winding corridors** and a single
obvious main path.

**Why DFS?** Simple to implement, guarantees full connectivity (perfect maze),
produces visually interesting results with long corridors, and runs in O(n) time
and space (where n = number of cells). It is the classic choice for maze projects.

### Prim's Algorithm

Starting from the entry cell, the algorithm maintains a frontier set of reachable
but unvisited cells and picks one at random, connecting it to a randomly chosen
already-visited neighbour. This produces mazes with **many short branches** and a
more uniform, organic appearance.

**Why Prim's?** Added as a bonus to demonstrate how a different spanning-tree
algorithm produces a structurally different maze from the same grid, even with the
same seed. It also avoids deep recursion for large mazes.

Select the algorithm via `ALGO=DFS` or `ALGO=PRIME` in the config file.

---

## Colour Schemes

The maze supports **6 built-in colour schemes**, cycled live by pressing `3`.
Each scheme defines distinct colours for: walls, the "42" logo, the solution path,
the entry cell, and the exit cell.

| Scheme | Walls   | Logo  | Solution | Entry | Exit |
|--------|---------|-------|----------|-------|------|
| 1      | Blue    | Cyan  | Magenta  | Green | Red  |
| 2      | Cyan    | Blue  | Yellow   | Green | Red  |
| 3      | Green   | Blue  | Magenta  | Cyan  | Red  |
| 4      | Yellow  | Green | Cyan     | Green | Red  |
| 5      | Red     | Cyan  | Yellow   | Green | Red  |
| 6      | Magenta | Cyan  | Yellow   | Green | Red  |

### How colour schemes work

Colour schemes are defined in `a_maze_ing.py` as a dictionary. Each scheme maps
five roles (`Walls`, `Logo`, `Solution`, `Entry`, `Exit`) to a `curses` colour
pair index (1 through 6). The six pairs are initialised at startup:

```
Pair 1  Blue on Black
Pair 2  Cyan on Black
Pair 3  Green on Black
Pair 4  Yellow on Black
Pair 5  Red on Black
Pair 6  Magenta on Black
```

### Adding a custom colour scheme

**Step 1 — optionally define a new curses colour pair** (only needed if you want
a colour not already in pairs 1-6). Add a new `init_pair` call in `main()`:

```python
curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
```

**Step 2 — add an entry to `maze_colors`** in `main()`:

```python
maze_colors = {
    ...
    '7': {
        'Walls':    1,   # pair index used for wall characters
        'Logo':     7,   # pair index used for the "42" logo cells
        'Solution': 4,   # pair index used for the BFS solution path
        'Entry':    3,   # pair index used for the entry cell
        'Exit':     5,   # pair index used for the exit cell
    }
}
```

**Step 3 — extend the random range** in the `choice == ord('3')` branch:

```python
rndm = random.randint(1, 7)   # was randint(1, 6)
```

The `maze_color` dict is passed directly to `MazeGenerator` and forwarded to
every `Cell.draw()` call, so changes take effect immediately on the next redraw.

---

## Reusable Code - `mazegen` Package

The maze generation and solving logic is extracted into a standalone
pip-installable package called `mazegen`, located at the root of the repository.
It has **no dependency on `curses`** and can be imported in any Python project.

### What is reusable

- **`Cell` class** - a single maze cell with `.walls` (dict `T/B/L/R`), `.x`, `.y`, `.logo`, `.visited`
- **`MazeGenerator` class** - full generation and solving logic:
  - `dfs(stdscr, y, x)` - DFS maze generation with animated curses display
  - `prime(stdscr, y, x)` - Prim's maze generation with animated curses display
  - `bfs_solver(entry, exit)` - BFS solver returning `list[tuple[int,int]]` or `None`
  - `display(stdscr)` - renders current maze state to the terminal
  - `show_hide_solution_path(stdscr, path, show)` - toggles solution overlay

### Installing the package

```bash
# From the pre-built wheel:
pip install mazegen-0.1.0-py3-none-any.whl

# Or from the source archive:
pip install mazegen.tar.gz
```

### Basic example

```python
import curses
import random
from mazegen.mazegen import MazeGenerator

def run(stdscr):
    random.seed(42)
    maze = MazeGenerator(
        height=15,
        width=20,
        entry=(0, 0),    # (row, col)
        exit=(14, 19),   # (row, col)
        perfect=True,
    )
    maze.dfs(stdscr, 0, 0)

    path = maze.bfs_solver((0, 0), (14, 19))
    if path:
        print(f"Solution: {len(path)} steps")

curses.wrapper(run)
```

### Custom parameters

```python
import random
random.seed(42)   # set before calling dfs/prime for reproducibility

maze = MazeGenerator(
    height=15,
    width=20,
    entry=(0, 0),
    exit=(14, 19),
    perfect=True,
    maze_color={          # optional - omit to use the default scheme
        'Walls': 1, 'Logo': 2, 'Solution': 6, 'Entry': 3, 'Exit': 5
    }
)
```

### Accessing the maze structure

```python
# maze.cells - list[list[Cell]], indexed as cells[row][col]
for row in maze.cells:
    for cell in row:
        # cell.walls: {'T': bool, 'B': bool, 'L': bool, 'R': bool}
        # True = wall present
        print(cell.x, cell.y, cell.walls)
```

### Accessing the solution

```python
path = maze.bfs_solver((0, 0), (14, 19))   # list[tuple[int,int]] or None
if path:
    print(f"{len(path)} steps: {path[0]} to {path[-1]}")
```

### Rebuilding the package from source

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install build
python -m build --no-isolation
# Outputs:
#   dist/mazegen-0.1.0-py3-none-any.whl
#   dist/mazegen-0.1.0.tar.gz
pip install dist/mazegen-0.1.0-py3-none-any.whl
```

The repository contains everything needed to rebuild:
- `mazegen/__init__.py` and `mazegen/mazegen.py` - full source
- `pyproject.toml` - build configuration

---

## Team and Project Management

### Team members and roles

| Login      | Role                                                                                          |
|------------|-----------------------------------------------------------------------------------------------|
| `zhaouzan` | Config file parser, BFS path solver , packaging, linting   |
| `abchahid` | DFS and Prim's algorithm implementation, imperfect maze logic, curses display rendering + animated display, hex output file       |

### Planning

**Initial plan:**
1. **Week 1** - Config parser, `Cell` and `MazeGenerator` classes, DFS algorithm
2. **Week 2** - Curses display, BFS solver, hex output file format
3. **Week 3** - Prim's algorithm, imperfect maze mode, "42" logo pattern
4. **Week 4** - Type annotations, mypy / flake8, mazegen package, README

**How it evolved:**
The mypy strict type-annotation phase took significantly longer than anticipated.
The main challenge was understanding that `Optional[Cell]` in the grid type caused
cascading union-attr errors throughout the file, and that `hexa_output.py` needed a
`TYPE_CHECKING` circular-import guard to pass strict mypy. The `mazegen` package
design also changed: the first plan was to import directly from `a_maze_ing.py`,
but `curses` at module level made that impossible without a live terminal, so the
generation logic was re-implemented as a standalone module.

### What worked well

- DFS and BFS were straightforward once the Cell/wall model was clear
- `curses` animation added real visual value with minimal extra code
- The modular split between `a_maze_ing.py`, `hexa_output.py`, and `mazegen`
  kept each file focused and testable in isolation

### What could be improved

- The recursive DFS hits Python's default recursion limit on very large mazes;
  an iterative version would be more robust
- The curses display does not handle terminal resize gracefully
- More generation algorithms (Kruskal's, Wilson's) could be added

### Tools used

- **Python 3.12** - main language
- **curses** - terminal UI (standard library)
- **mypy** - static type checking
- **flake8** - PEP 8 linting
- **setuptools / build** - pip packaging
- **poetry ** - used to Create the reusable package 

---

## Resources

### Maze generation references

- [Maze generation algorithms - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth: Maze algorithms - Walter D. Pullen](http://www.astrolog.org/labyrnth/algrithm.htm)
- [Jamis Buck - Mazes for Programmers (blog series)](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Prim's algorithm - Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [BFS (Breadth-First Search) - Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)

### Python references

- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
