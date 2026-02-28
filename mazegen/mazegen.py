#!/usr/bin/env python

"""Maze generator and solver with curses.

This module provides an interactive terminal maze application that
supports two algorithms (DFS and PRIME), BFS solving, and animated
solution path display.

Typical usage:

    python a_maz_ing.py config.txt

The config file must define WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE
PERFCT, ALGO, SEED.
Engoy playing the maze.
"""


import curses
import math
import random
import time
from typing import Optional, List, Dict, Tuple


class Cell:
    """Represents a single cell in the maze grid.

    Attributes:
        walls: Dictionary indicating presence of walls on each side
               (keys: 'T', 'B', 'L', 'R' for top, bottom, left, right).
        limits: Dictionary indicating if cell is at maze boundaries
                (keys: 'T', 'B', 'L', 'R' for top, bottom, left, right).
        x: Column position of the cell.
        y: Row position of the cell.
        logo: Whether this cell is part of the logo pattern.
        visited: Whether this cell has been visited during maze generation.
    """

    def __init__(
            self, x: int,
            y: int,
            limits: Dict[str, bool]
            ) -> None:
        """Initialize a cell with position and boundary information.

        Args:
            x: Column position of the cell.
            y: Row position of the cell.
            limits: Dictionary indicating if cell is at maze boundaries
                   (keys: 'T', 'B', 'L', 'R' for top, bottom, left, right).
        """
        self.walls = {'T': True, 'B': True, 'L': True, 'R': True}
        self.limits = limits
        self.x = x
        self.y = y
        self.logo = False
        self.visited = False
        self.in_path = False
        self.solution = False

    def draw(
            self,
            stdscr: curses.window,
            cells: List[List["Cell"]],
            width: int,
            height: int,
            entry: Tuple[int, int],
            exit: Tuple[int, int],
            maze_color: Dict[str, int]
            ) -> None:
        """Draw the cell on the screen with appropriate walls and colors.

        Renders the cell as a 4x3 character block with walls represented by
        block characters. Colors differ for logo cells, entry, and exit.

        Args:
            stdscr: Curses window object for display.
            cells: 2D list of all cells in the maze.
            width: Total width of the maze in cells.
            height: Total height of the maze in cells.
            entry: Entry point coordinates (row, column).
            exit: Exit point coordinates (row, column).
        """

        nx = self.x * 4
        ny = self.y * 2

        stdscr.addstr(ny, nx, "█",
                      curses.color_pair(maze_color['Walls']))
        stdscr.addstr(ny, nx + 3, "█",
                      curses.color_pair(maze_color['Walls']))
        stdscr.addstr(ny + 2, nx, "█",
                      curses.color_pair(maze_color['Walls']))
        stdscr.addstr(ny + 2, nx + 3, "█",
                      curses.color_pair(maze_color['Walls']))

        if (self.y - 1 >= 0 and cells[self.y - 1][self.x].solution
                and self.solution and not self.walls['T']):
            stdscr.addstr(ny, nx + 1, "██",
                          curses.color_pair(maze_color['Solution']))
        elif self.walls['T'] and ((self.y - 1 >= 0 and
                                   cells[self.y - 1][self.x].walls['B'])
                                  or self.y == 0):
            stdscr.addstr(ny, nx + 1, "██",
                          curses.color_pair(maze_color['Walls']))
        elif self.limits['T']:
            stdscr.addstr(ny, nx + 1, "██",
                          curses.color_pair(maze_color['Walls']))
        else:
            stdscr.addstr(ny, nx + 1, "  ",
                          curses.color_pair(maze_color['Walls']))

        if (self.y + 1 < height and cells[self.y + 1][self.x].solution
                and self.solution and not self.walls['B']):
            stdscr.addstr(ny + 2, nx + 1, "██",
                          curses.color_pair(maze_color['Solution']))
        elif self.walls['B']:
            stdscr.addstr(ny + 2, nx + 1, "██",
                          curses.color_pair(maze_color['Walls']))
        elif self.limits['B']:
            stdscr.addstr(ny + 2, nx + 1, "██",
                          curses.color_pair(maze_color['Walls']))
        else:
            stdscr.addstr(ny + 2, nx + 1, "  ",
                          curses.color_pair(maze_color['Walls']))

        if (self.x - 1 >= 0 and cells[self.y][self.x - 1].solution
                and self.solution and not self.walls['L']):
            stdscr.addstr(ny + 1, nx, "█",
                          curses.color_pair(maze_color['Solution']))
        elif self.walls['L'] and ((self.x - 1 >= 0 and
                                   cells[self.y][self.x - 1].walls['R']) or
                                  self.x == 0):
            stdscr.addstr(ny + 1, nx, "█",
                          curses.color_pair(maze_color['Walls']))
        elif self.limits['L']:
            stdscr.addstr(ny + 1, nx, "█",
                          curses.color_pair(maze_color['Walls']))
        else:
            stdscr.addstr(ny + 1, nx, " ",
                          curses.color_pair(maze_color['Walls']))

        if (self.x + 1 < width and cells[self.y][self.x + 1].solution
                and self.solution and not self.walls['R']):
            stdscr.addstr(ny + 1, nx + 3, "█",
                          curses.color_pair(maze_color['Solution']))
        elif self.walls['R'] and ((self.x + 1 < width and
                                   cells[self.y][self.x + 1].walls['L']) or
                                  self.x == width - 1):
            stdscr.addstr(ny + 1, nx + 3, "█",
                          curses.color_pair(maze_color['Walls']))
        elif self.limits['R']:
            stdscr.addstr(ny + 1, nx + 3, "█",
                          curses.color_pair(maze_color['Walls']))
        else:
            stdscr.addstr(ny + 1, nx + 3, " ",
                          curses.color_pair(maze_color['Walls']))

        if self.logo:
            stdscr.addstr(ny + 1, nx + 1, "██",
                          curses.color_pair(maze_color['Logo']))
        elif self.x == entry[1] and self.y == entry[0]:
            stdscr.addstr(ny + 1, nx + 1, "██",
                          curses.color_pair(maze_color['Entry']))
        elif self.x == exit[1] and self.y == exit[0]:
            stdscr.addstr(ny + 1, nx + 1, "██",
                          curses.color_pair(maze_color['Exit']))
        elif self.solution:
            stdscr.addstr(ny + 1, nx + 1, "██",
                          curses.color_pair(maze_color['Solution']))
        else:
            stdscr.addstr(ny + 1, nx + 1, "  ",
                          curses.color_pair(maze_color['Walls']))


class MazeGenerator:
    """A maze generator search algorithm with visualization.

    Attributes:
        width: Number of cells in horizontal direction.
        height: Number of cells in vertical direction.
        entry: Entry point as (row, column) tuple.
        exit: Exit point as (row, column) tuple.
        visited_count: Number of cells visited during generation.
        cells_count: Total number of cells in the maze.
        cells: 2D list of Cell objects representing the maze grid.

        """

    def __init__(
            self,
            height: int,
            width: int,
            entry: Tuple[int, int],
            exit: Tuple[int, int],
            perfect: bool,
            maze_color: Dict[str, int] = None
            ) -> None:
        """Initialize a maze with given dimensions.

        Args:
            height: Number of cells in vertical direction.
            width:  Number of cells in horizontal direction.
            entry:  Entry point.
            exit:   Exit point.
            perfect: True means the maze has one solution.
            maze_color: Dict containing the colors needed for drawing the maze
                        Example : {'Walls': 1, 'Logo': 2, 'Solution': 6,
                               'Entry': 3, 'Exit': 5}
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.visited_count = 0
        self.perfect = perfect
        self.cells_count = width * height
        if maze_color is None:
            self.maze_color = {'Walls': 1, 'Logo': 2, 'Solution': 6,
                               'Entry': 3, 'Exit': 5}
        else:
            self.maze_color = maze_color
        self.cells: List[List[Cell]] = [
                [
                    Cell(
                        x,
                        y,
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
        if width >= 9 and height >= 7:
            self.declare_logo()
        else:
            raise ValueError("Maze width and height isnt enough"
                             "to show 42 logo")

    def generate_maze(self) -> None:
        """Generate the initial maze grid with all walls intact.

        Creates a grid of Cell objects with appropriate boundary information
        and marks the entry cell as visited.
        """
        x = 0
        y = 0
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

    def show_hide_solution_path(
            self,
            stdscr: curses.window,
            path: List[Tuple[int, int]],
            show: bool
            ) -> None:
        """ Make in the path available in the map curses
        Args:
            stdscr: the master of the map
            path: array has address of the solution
            path_color: color of the path.
            show: boolean variable to hide the solution
        """
        if show:
            for place in path:
                nx = place[1]
                ny = place[0]
                self.cells[ny][nx].solution = True
                self.display(stdscr)
                time.sleep(0.01)
        else:
            for place in path:
                nx = place[1]
                ny = place[0]
                self.cells[ny][nx].solution = False
            self.display(stdscr)

    def bfs_solver(
            self,
            entry: Tuple[int, int],
            end: Tuple[int, int]
            ) -> Optional[List[Tuple[int, int]]]:
        """Solve maze using BFS.
        Args:
            start: Start position (row, column).
            end: End position (row, column).

        Returns:
            List of coordinates forming the path, or None.
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
            y, x = curr
            if curr == end:
                path: List[Tuple[int, int]] = []
                node: Optional[Tuple[int, int]] = end
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()

                return path
            neighbors = self.get_neighbors(y, x)

            for ny, nx in neighbors:
                if not self.cells[ny][nx].visited:
                    self.cells[ny][nx].visited = True
                    parent[(ny, nx)] = curr
                    child.append((ny, nx))
        return None

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

    def declare_logo(self) -> None:
        """Mark specific 42 in the center of the maze as logo cells.

        Creates a 42 pattern in the center of the maze by marking specific
        cells. These cells will be excluded from the maze generation algorithm.
        """
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

    def dfs_algo(
            self,
            stdscr: curses.window,
            y: int,
            x: int) -> None:
        """Generate maze paths using depth-first search algorithm.

        Recursively visits unvisited neighboring cells, removing walls between
        them to create maze passages. The algorithm avoids logo cells and
        visualizes the generation process.

        Args:
            stdscr: Curses window object for display.
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
            stdscr.refresh()
            self.display(stdscr)
            time.sleep(0.01)

            if self.visited_count < self.cells_count:
                self.dfs_algo(stdscr, ny, nx)

    def dfs(
        self,
        stdscr: curses.window,
        y: int,
            x: int) -> None:

        """Generate maze paths using depth-first search algorithm.

        Recursively visits unvisited neighboring cells, removing walls between
        them to create maze passages. The algorithm avoids logo cells and
        visualizes the generation process.

        Args:
            stdscr: Curses window object for display.
            y: Current row position.
            x: Current column position.
        """

        self.dfs_algo(stdscr, y, x)
        if not self.perfect:
            self.make_it_imperfect(stdscr)

    def prime(
            self,
            stdscr: curses.window,
            y: int,
            x: int) -> None:
        """Generate a maze using prime algo

        Args:
            stdscr: Curses window object for display.
            y: Starting row position.
            x: Starting column position.

        """
        choices = set()
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
                stdscr.refresh()
                self.display(stdscr)
                x = nx
                y = ny
                time.sleep(0.01)
            else:
                break
        if not self.perfect:
            self.make_it_imperfect(stdscr)

    def make_it_imperfect(
            self,
            stdscr: curses.window) -> None:
        """Remove extra walls to create an imperfect maze (multiple paths).

        Args:
            stdscr: Curses window object for display.
        """
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

                    self.display(stdscr)

    def display(
            self,
            stdscr: curses.window) -> None:
        """Display the current state of the maze.

        Clears the screen and redraws all cells in the maze with their
        current wall configuration and colors.

        Args:
            stdscr: Curses window object for display.
        """

        for row in self.cells:
            for cell in row:
                cell.draw(
                        stdscr,
                        self.cells,
                        self.width,
                        self.height,
                        self.entry,
                        self.exit,
                        self.maze_color
                        )

        stdscr.refresh()
