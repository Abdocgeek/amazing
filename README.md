*This project has been created as part of the 42 curriculum by zhaouzan and abchahid*

# A-Maze-ing

## Description

A-Maze-ing is an interactive terminal maze generator and solver built in Python.
The program takes a configuration file, generates a random maze using either a
depth-first search (DFS) or Prim's algorithm, displays it in the terminal with
curses, and writes the result to a hex-encoded output file.

Key features:
- Two generation algorithms: DFS (recursive backtracker) and Prim's
- Perfect maze mode (exactly one path between entry and exit)
- Animated generation and solution path display
- BFS-based shortest path solver
- A "42" logo pattern embedded in the centre of the maze
- Hex-encoded output file with solution directions (N/S/E/W)
- Reusable `mazegen` pip package with no curses dependency

---

## Instructions

### Requirements

- Python 3.10 or later
- No third-party runtime dependencies (curses is part of the standard library)
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

| Key | Action                          |
|-----|---------------------------------|
| `1` | Generate / re-generate the maze |
| `2` | Show / hide the solution path   |
| `3` | Cycle maze wall colours         |
| `4` | Quit                            |

---

## Configuration file format

The configuration file uses one `KEY=VALUE` pair per line.
Lines starting with `#` are comments and are ignored.

| Key           | Description                              | Example                   |
|---------------|------------------------------------------|---------------------------|
| `WIDTH`       | Number of columns (cells)                | `WIDTH=20`                |
| `HEIGHT`      | Number of rows (cells)                   | `HEIGHT=15`               |
| `ENTRY`       | Entry cell as `x,y` (col, row)           | `ENTRY=0,0`               |
| `EXIT`        | Exit cell as `x,y` (col, row)            | `EXIT=19,14`              |
| `OUTPUT_FILE` | Path of the hex output file              | `OUTPUT_FILE=maze.txt`    |
| `PERFECT`     | `True` = one solution, `False` = multi   | `PERFECT=True`            |
| `ALGO`        | Generation algorithm: `DFS` or `PRIME`   | `ALGO=DFS`                |
| `SEED`        | Integer seed for reproducibility         | `SEED=42`                 |

Example `config.txt`:

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
ALGO=DFS
SEED=42
```

---

## Output file format

The maze is written row by row, one hex character per cell.
Each hex digit encodes which walls are **closed** using this bitmask:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1       | East  |
| 2       | South |
| 3       | West  |

A closed wall sets the bit to `1`; open means `0`.

After a blank line, the file contains three more lines:
1. Entry coordinates as `x,y`
2. Exit coordinates as `x,y`
3. Shortest path as a string of `N`, `S`, `E`, `W` characters

All lines end with `\n`.

Example:
```
9515391539551795151151153
...

1,1
19,14
SWSESWSESSSEENNEESE...
```

---

## Algorithms

### Chosen algorithms: DFS and Prim's

The project implements **two** generation algorithms selectable via `ALGO=DFS`
or `ALGO=PRIME` in the config file.

#### DFS — Depth-First Search (Recursive Backtracker)

The default algorithm. Starting from the entry cell, the algorithm picks a random
unvisited neighbour, removes the wall between them, and recurses. When it reaches
a dead end it backtracks. This produces mazes with **long, winding corridors** and
a single obvious solution path.

**Why DFS?** It is simple to implement, guarantees full connectivity (perfect maze),
produces visually interesting results with long corridors, and runs in O(n) time and
space (where n = number of cells). It is the classic choice for beginner maze projects.

#### Prim's Algorithm

An alternative. Starting from the entry cell, it maintains a frontier set of reachable
but unvisited cells and picks one at random at each step, connecting it to a randomly
chosen already-visited neighbour. This produces mazes with **many short branches**
and a more uniform appearance than DFS.

**Why Prim's?** It was added as a bonus to demonstrate how a different spanning-tree
algorithm produces a structurally different maze from the same grid, even with the
same seed.

---

## Reusable code — `mazegen` package

The maze generation and solving logic is extracted into a standalone pip-installable
package called `mazegen`, located at the root of the repository. It has **no dependency
on curses** and can be imported in any Python project.

### What is reusable

- `Cell` class — a single maze cell with `.walls` (dict `T/B/L/R`), `.x`, `.y`
- `MazeGenerator` class — full generation and solving logic:
  - `generate()` — builds the maze (DFS or Prim's)
  - `solve()` — BFS solver returning `list[tuple[int,int]]` or `None`
  - `to_string()` — ASCII art representation
  - `to_hex()` — hex-encoded rows (same bitmask as the output file)
  - `save(path)` — writes the output file format

### Installing the package

```bash
pip install mazegen-1.0.0-py3-none-any.whl
# or from source:
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### Basic example

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=10, height=10)
gen.generate()
print(gen.to_string())

path = gen.solve()
print("Solution:", path)
```

### Custom parameters

```python
gen = MazeGenerator(
    width=20, height=15,
    entry=(0, 0),        # (row, col)
    exit=(14, 19),       # (row, col)
    seed=42,             # reproducible output
    algorithm='PRIME',   # 'DFS' (default) or 'PRIME'
    perfect=True,        # False = extra walls removed
)
gen.generate()
```

### Accessing the maze structure

```python
# gen.cells — list[list[Cell]], indexed as cells[row][col]
for row in gen.cells:
    for cell in row:
        # cell.walls: {'T': bool, 'B': bool, 'L': bool, 'R': bool}
        # True = wall present
        print(cell.x, cell.y, cell.walls)
```

### Accessing the solution

```python
path = gen.solve()   # list[tuple[int, int]] or None
if path:
    print(f"{len(path)} steps: {path[0]} → {path[-1]}")
```

### Building the package from source

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install build
python -m build --no-isolation
# Output:
#   dist/mazegen-1.0.0-py3-none-any.whl
#   dist/mazegen-1.0.0.tar.gz
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

The repository contains everything needed to rebuild:
- `mazegen/__init__.py` — the full source
- `pyproject.toml` — build configuration

---

## Team and project management

### Team members and roles

| Login | Role |
|-------|------|
| `zhaouzan` | parsing the config file — architecture,path (BFS) with display, packaging, linting |
| `abchahid`| upgrading algorithms dfs and PRIME also upgrading the path, solving the display |

### Planning

**Initial plan:**
1. Week 1 — Config parser, Cell and MazeGenerator classes, DFS algorithm
2. Week 2 — Curses display, BFS solver, output file format
3. Week 3 — Prim's algorithm, imperfect maze, "42" logo
4. Week 4 — Type annotations, mypy/flake8, mazegen package, README

**How it evolved:**
The type annotation phase (mypy strict) took significantly longer than anticipated.
The main challenge was understanding that `Optional[Cell]` in the grid type caused
cascade union-attr errors throughout the file, and that the hexa_output module
needed a circular-import guard (`TYPE_CHECKING`) to be compatible with strict mypy.
The mazegen package design also changed: the first plan was to import directly from
`a_maze_ing.py`, but curses at module level made that impossible without a terminal —
so the generation logic was re-implemented as a standalone module.

### What worked well

- DFS and BFS were straightforward to implement once the Cell/wall model was clear
- curses animation added real visual value with minimal extra code
- The modular split between `a_maze_ing.py`, `hexa_output.py`, and `mazegen` kept
  each file focused and testable in isolation

### What could be improved

- The recursive DFS hits Python's default recursion limit on very large mazes;
  an iterative version would be more robust
- The curses display does not handle terminal resize gracefully
- More generation algorithms (Kruskal's, Wilson's) could be added

### Tools used

- **Python 3.12** — main language
- **curses** — terminal UI (standard library)
- **mypy** — static type checking
- **flake8** — PEP 8 linting
- **setuptools / build** — pip packaging
- **Claude (Anthropic)** — used as an AI assistant (see Resources section)

---

## Resources

### Maze generation references

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Think Labyrinth: Maze algorithms — Walter D. Pullen](http://www.astrolog.org/labyrnth/algrithm.htm)
- [Jamis Buck — Mazes for Programmers (blog series)](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Prim's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [BFS (Breadth-First Search) — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)

### Python references

- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)

### AI usage

**Tool used:** Claude (Anthropic)

**Tasks where AI was used:**

| Part of the project | How AI was used |
|---------------------|-----------------|
| Type annotations | Diagnosing mypy strict errors; explaining why `Optional[Cell]` in the grid type caused union-attr cascade errors; fixing `List[int, int]` → `List[Tuple[int,int]]` |
| hexa_output.py | Identifying the `File` typing import error; fixing the `with open(file) as file` shadowing bug; adding `TYPE_CHECKING` guard for circular import |
| mazegen package | Explaining why `a_maze_ing.py` cannot be imported at package level (curses at module scope); designing the standalone module structure |
| README structure | Checking which sections the subject required; drafting the mazegen documentation section |
| pyproject.toml | Generating the correct `[tool.setuptools.packages.find]` config for a single-module package |
