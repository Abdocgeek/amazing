#!/usr/bin/env python3
"""Maze generator standalone module.

This is a display-free version of the maze generator.
Same Cell and MazeGenerator classes as a_maze_ing.py but with
all curses, display, animation, and time dependencies removed.
Can be imported and used in any project without a terminal.

Typical usage:

    from mazegen import MazeGenerator
    import random

    random.seed(42)
    maze = MazeGenerator(
        height=15,
        width=20,
        entry=(0, 0),
        exit=(14, 19),
        perfect=True
    )
    maze.dfs(0, 0)
    path = maze.bfs_solver((0, 0), (14, 19))
    print(path)
"""

import math
import random
from typing import Dict, List, Optional, Tuple


class Cell:
    """Represents a single cell in the maze grid.

    Attributes:
        walls: Dictionary indicating presence of walls on each side
               (keys: 'T', 'B', 'L', 'R' for top, bottom, left, right).
        limits: Dictionary indicating if cell is at maze boundaries.
        x: Column position of the cell.
        y: Row position of the cell.
        logo: Whether this cell is part of the logo pattern.
        visited: Whether this cell has been visited during maze generation.
        in_path: Whether this cell is marked as part of a path.
        solution: Whether this cell is part of the solution path.
    """

    def __init__(
            self,
            x: int,
            y: int,
            limits: Dict[str, bool]
            ) -> None:
        """Initialize a cell with position and boundary information.

        Args:
            x: Column position of the cell.
            y: Row position of the cell.
            limits: Dictionary indicating if cell is at maze boundaries
                   (keys: 'T', 'B', 'L', 'R').
        """
        self.walls: Dict[str, bool] = {
            'T': True, 'B': True, 'L': True, 'R': True
        }
        self.limits: Dict[str, bool] = limits
        self.x: int = x
        self.y: int = y
        self.logo: bool = False
        self.visited: bool = False
        self.in_path: bool = False
        self.solution: bool = False


class MazeGenerator:
    """A maze generator with DFS and PRIME algorithms and a BFS solver.

    Display-free version — no curses dependency.
    The maze structure is accessible via the cells attribute
    after calling dfs() or prime().

    Attributes:
        width: Number of cells in horizontal direction.
        height: Number of cells in vertical direction.
        entry: Entry point as (row, column) tuple.
        exit: Exit point as (row, column) tuple.
        visited_count: Number of cells visited during generation.
        cells_count: Total number of cells in the maze.
        cells: 2D list of Cell objects representing the maze grid.

    Example:
        >>> import random
        >>> random.seed(42)
        >>> maze = MazeGenerator(
        ...     height=10, width=10,
        ...     entry=(0, 0), exit=(9, 9),
        ...     perfect=True
        ... )
        >>> maze.dfs(0, 0)
        >>> path = maze.bfs_solver((0, 0), (9, 9))
        >>> print(path)
    """

    def __init__(
            self,
            height: int,
            width: int,
            entry: Tuple[int, int],
            exit: Tuple[int, int],
            perfect: bool
            ) -> None:
        """Initialize a maze with given dimensions.

        Args:
            height: Number of cells in vertical direction.
            width:  Number of cells in horizontal direction.
            entry:  Entry point as (row, column) tuple.
            exit:   Exit point as (row, column) tuple.
            perfect: True means exactly one solution path.
        """
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit
        self.visited_count: int = 0
        self.cells_count: int = width * height
        self.perfect_maze: bool = perfect
        self.cells: List[List[Cell]] = [
            [
                Cell(
                    x, y,
                    {
                        'T': (y == 0),
                        'B': (y == height - 1),
                        'L': (x == 0),
                        'R': (x == width - 1),
                    }
                )
                for x in range(width)
            ]
            for y in range(height)
        ]
        self.generate_maze()
        if width >= 7 and height >= 7:
            self.declare_logo()

    def generate_maze(self) -> None:
        """Initialize the maze grid and mark the entry cell as visited."""
        for y in range(self.height):
            for x in range(self.width):
                limits = {
                    'T': (y == 0),
                    'B': (y == self.height - 1),
                    'L': (x == 0),
                    'R': (x == self.width - 1)
                }
                self.cells[y][x] = Cell(x, y, limits)
        self.cells[self.entry[0]][self.entry[1]].visited = True
        self.visited_count += 1

    def declare_logo(self) -> None:
        """Mark specific cells in the center as the 42 logo pattern."""
        center_width = math.floor(self.width / 2)
        center_height = math.floor(self.height / 2)
        x = center_width - 3
        y = center_height - 2

        self.cells[y][x].logo = True
        self.cells[y + 1][x].logo = True
        self.cells[y + 2][x].logo = True
        self.cells[y + 2][x + 1].logo = True
        self.cells[y + 2][x + 2].logo = True
        self.cells[y + 3][x + 2].logo = True
        self.cells[y + 4][x + 2].logo = True
        self.cells[y + 4][x + 4].logo = True
        self.cells[y + 4][x + 5].logo = True
        self.cells[y + 4][x + 6].logo = True
        self.cells[y + 3][x + 4].logo = True
        self.cells[y + 2][x + 4].logo = True
        self.cells[y + 2][x + 5].logo = True
        self.cells[y + 2][x + 6].logo = True
        self.cells[y + 1][x + 6].logo = True
        self.cells[y][x + 6].logo = True
        self.cells[y][x + 5].logo = True
        self.cells[y][x + 4].logo = True

    def dfs(self, y: int, x: int) -> None:
        """Generate maze paths using depth-first search algorithm.

        Recursively visits unvisited neighboring cells, removing walls
        between them. Avoids logo cells.

        Args:
            y: Current row position.
            x: Current column position.
        """
        choices = []
        if (x + 1 < self.width and not self.cells[y][x + 1].visited
                and not self.cells[y][x + 1].logo):
            choices.append((y, x + 1))
        if (y + 1 < self.height and not self.cells[y + 1][x].visited
                and not self.cells[y + 1][x].logo):
            choices.append((y + 1, x))
        if (y - 1 >= 0 and not self.cells[y - 1][x].visited
                and not self.cells[y - 1][x].logo):
            choices.append((y - 1, x))
        if (x - 1 >= 0 and not self.cells[y][x - 1].visited
                and not self.cells[y][x - 1].logo):
            choices.append((y, x - 1))
        if not choices:
            return

        random.shuffle(choices)

        for i in range(len(choices)):
            ny, nx = choices[i]
            if self.cells[ny][nx].visited:
                continue
            if ny - y > 0:
                self.cells[ny][nx].walls["T"] = False
                self.cells[y][x].walls["B"] = False
            if nx - x > 0:
                self.cells[ny][nx].walls["L"] = False
                self.cells[y][x].walls["R"] = False
            if nx - x < 0:
                self.cells[ny][nx].walls["R"] = False
                self.cells[y][x].walls["L"] = False
            if ny - y < 0:
                self.cells[ny][nx].walls["B"] = False
                self.cells[y][x].walls["T"] = False

            self.cells[ny][nx].visited = True
            self.visited_count += 1

            if self.visited_count < self.cells_count:
                self.dfs(ny, nx)

    def prime(self, y: int, x: int) -> None:
        """Generate a maze using Prim's algorithm.

        Builds the maze by randomly selecting frontier cells and
        connecting them to the already visited region.

        Args:
            y: Starting row position.
            x: Starting column position.
        """
        choices: set = set()
        while self.visited_count < self.cells_count:
            if (x + 1 < self.width and not self.cells[y][x + 1].visited
                    and not self.cells[y][x + 1].logo):
                choices.add((y, x + 1))
            if (y + 1 < self.height and not self.cells[y + 1][x].visited
                    and not self.cells[y + 1][x].logo):
                choices.add((y + 1, x))
            if (y - 1 >= 0 and not self.cells[y - 1][x].visited
                    and not self.cells[y - 1][x].logo):
                choices.add((y - 1, x))
            if (x - 1 >= 0 and not self.cells[y][x - 1].visited
                    and not self.cells[y][x - 1].logo):
                choices.add((y, x - 1))

            if choices:
                selection = random.choice(list(choices))
                ny, nx = selection
                choices.remove(selection)

                if ny - 1 >= 0 and self.cells[ny - 1][nx].visited:
                    self.cells[ny][nx].walls["T"] = False
                    self.cells[ny - 1][nx].walls["B"] = False
                elif nx - 1 >= 0 and self.cells[ny][nx - 1].visited:
                    self.cells[ny][nx].walls["L"] = False
                    self.cells[ny][nx - 1].walls["R"] = False
                elif nx + 1 < self.width and self.cells[ny][nx + 1].visited:
                    self.cells[ny][nx].walls["R"] = False
                    self.cells[ny][nx + 1].walls["L"] = False
                elif ny + 1 < self.height and self.cells[ny + 1][nx].visited:
                    self.cells[ny][nx].walls["B"] = False
                    self.cells[ny + 1][nx].walls["T"] = False

                self.cells[ny][nx].visited = True
                self.visited_count += 1
                x = nx
                y = ny
            else:
                return

    def make_it_imperfect(self) -> None:
        """Remove extra walls to create an imperfect maze (multiple paths)."""
        for y in range(self.height):
            for x in range(self.width):
                if (x + 1 < self.width and x - 1 >= 0
                    and y + 1 < self.height and y - 1 >= 0
                    and not self.cells[y][x].logo
                    and not self.cells[y][x + 1].logo
                    and not self.cells[y][x - 1].logo
                    and not self.cells[y + 1][x].logo
                        and not self.cells[y - 1][x].logo):
                    if (self.cells[y][x].walls['T']
                        and ((self.cells[y][x + 1].walls['T']
                              or self.cells[y - 1][x + 1].walls['L'])
                        and (self.cells[y][x - 1].walls['T']
                             or self.cells[y - 1][x - 1].walls['R']))):
                        self.cells[y][x].walls['T'] = False
                        self.cells[y - 1][x].walls['B'] = False

                    if (self.cells[y][x].walls['L']
                        and ((self.cells[y + 1][x].walls['L']
                              or self.cells[y + 1][x - 1].walls['T'])
                        and (self.cells[y - 1][x].walls['L']
                             or self.cells[y - 1][x - 1].walls['B']))):
                        self.cells[y][x].walls['L'] = False
                        self.cells[y][x - 1].walls['R'] = False

    def get_neighbors(
            self,
            y: int,
            x: int
            ) -> List[Tuple[int, int]]:
        """Get walkable neighbors (no walls blocking).

        Args:
            y: Row of current cell.
            x: Column of current cell.

        Returns:
            List of (row, col) tuples for reachable neighbors.
        """
        neighbors = []
        if not self.cells[y][x].walls['R'] and x + 1 < self.width:
            neighbors.append((y, x + 1))
        if not self.cells[y][x].walls['B'] and y + 1 < self.height:
            neighbors.append((y + 1, x))
        if not self.cells[y][x].walls['L'] and x - 1 >= 0:
            neighbors.append((y, x - 1))
        if not self.cells[y][x].walls['T'] and y - 1 >= 0:
            neighbors.append((y - 1, x))
        return neighbors

    def bfs_solver(
            self,
            entry: Tuple[int, int],
            end: Tuple[int, int]
            ) -> Optional[List[Tuple[int, int]]]:
        """Solve the maze using BFS and return the shortest path.

        Args:
            entry: Start position as (row, column).
            end: End position as (row, column).

        Returns:
            List of (row, col) coordinates forming the shortest path,
            or None if no path exists.
        """
        for row in self.cells:
            for cell in row:
                cell.visited = False
        child: List[Tuple[int, int]] = [entry]
        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            entry: None
        }
        self.cells[entry[0]][entry[1]].visited = True

        while child:
            curr = child.pop(0)
            cy, cx = curr
            if curr == end:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = end
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path
            neighbors = self.get_neighbors(cy, cx)
            for ny, nx in neighbors:
                if not self.cells[ny][nx].visited:
                    self.cells[ny][nx].visited = True
                    parent[(ny, nx)] = curr
                    child.append((ny, nx))
        return None
