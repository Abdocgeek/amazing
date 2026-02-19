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
import sys
from typing import Optional, List, Dict, Tuple, Any
from hexa_output import create_output_file


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
                and self.solution):
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

        if self.walls['B']:
            stdscr.addstr(ny + 2, nx + 1, "██",
                          curses.color_pair(maze_color['Walls']))
        elif self.limits['B']:
            stdscr.addstr(ny + 2, nx + 1, "██",
                          curses.color_pair(maze_color['Walls']))
        else:
            stdscr.addstr(ny + 2, nx + 1, "  ",
                          curses.color_pair(maze_color['Walls']))

        if (self.x - 1 >= 0 and cells[self.y][self.x - 1].solution
                and self.solution):
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
                and self.solution):
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
            # if maze_color - 1 > 0:
            #     logo_color = maze_color - 1
            # else:
            #     logo_color = maze_color + 1
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


class Maze:
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
            perfect: bool
            ) -> None:
        """Initialize a maze with given dimensions.

        Args:
            height: Number of cells in vertical direction.
            width:  Number of cells in horizontal direction.
            entry:  Entry point.
            exit:   Exit point.
            perfect:True means the maze has one solution.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.visited_count = 0
        self.cells_count = width * height
        self.perfect_maze = perfect
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
        # [[None for x in range(width)] for y in range(height)]
        self.generate_maze()
        if width >= 7 and height >= 7:
            self.declare_logo()

    def generate_maze(self) -> None:
        """Generate the initial maze grid with all walls intact.

        Creates a grid of Cell objects with appropriate boundary information
        and marks the entry cell as visited.
        """
        x = 0
        y = 0
        # self.cells: list[list[Cell]] = []
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
            maze_color: Dict[str, int],
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
                self.display(stdscr, maze_color)
                time.sleep(0.01)
        else:
            for place in path:
                nx = place[1]
                ny = place[0]
                self.cells[ny][nx].solution = False
            self.display(stdscr, maze_color)

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

        # Check RIGHT - is there a wall blocking?
        if not self.cells[y][x].walls['R'] and x + 1 < self.width:
            neighbors.append((y, x + 1))

        # Check DOWN
        if not self.cells[y][x].walls['B'] and y + 1 < self.height:
            neighbors.append((y + 1, x))

        # Check LEFT
        if not self.cells[y][x].walls['L'] and x - 1 >= 0:
            neighbors.append((y, x - 1))

        # Check UP
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

    def dfs(
            self,
            stdscr: curses.window,
            y: int,
            x: int,
            maze_color: Dict[str, int]) -> None:
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
            self.display(stdscr, maze_color)
            time.sleep(0.01)

            if self.visited_count < self.cells_count:
                self.dfs(stdscr, ny, nx, maze_color)

    def prime(
            self,
            stdscr: curses.window,
            y: int,
            x: int,
            maze_color: Dict[str, int]) -> None:
        """Generate a maze using prime algo

        Args:
            stdscr: Curses window object for display.
            y: Starting row position.
            x: Starting column position.
            maze_color: Color mapping dict.

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
                self.display(stdscr, maze_color)
                x = nx
                y = ny
                time.sleep(0.01)
            else:
                return

    def make_it_imperfect(
            self,
            stdscr: curses.window,
            maze_color: Dict[str, int]) -> None:
        """Remove extra walls to create an imperfect maze (multiple paths).

        Args:
            stdscr: Curses window object for display.
            maze_color: Color mapping dict.
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

                    self.display(stdscr, maze_color)
                # if (x == self.width - 1 and not self.cells[y][x - 1].logo
                #     and self.cells[y][x].walls['T']
                #     and (self.cells[y][x - 1].walls['T']
                #          or self.cells[y - 1][x - 1].walls['R'])):
                #     self.cells[y][x].walls['T'] = False
                #     self.cells[y - 1][x].walls['B'] = False
                #     self.display(stdscr, w_color)
                # time.sleep(0.1)

    def display(
            self,
            stdscr: curses.window,
            maze_color: Dict[str, int]) -> None:
        """Display the current state of the maze.

        Clears the screen and redraws all cells in the maze with their
        current wall configuration and colors.

        Args:
            stdscr: Curses window object for display.
            maze_color: Color mapping world.
        """
        # stdscr.clear()
        for row in self.cells:
            for cell in row:
                cell.draw(
                        stdscr,
                        self.cells,
                        self.width,
                        self.entry,
                        self.exit,
                        maze_color
                        )

        stdscr.refresh()


def parse_config(filename: str) -> Dict[str, Any]:
    """ Parse your config file

    Args:
        filename: name of the configfile

    Returns:
        Dictionary with parsed configuration values.

    Raises:
        ValueError: If required keys are missing or values are invalid.
        TypeError: If entry and exit are the same point.
    """
    config = {}

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Invalid line: {line}")
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    required = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "ALGO",
        "SEED"
    ]

    for key in required:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")
    width = int(config["WIDTH"])
    height = int(config["HEIGHT"])
    entry_x, entry_y = map(int, config["ENTRY"].split(","))
    exit_x, exit_y = map(int, config["EXIT"].split(","))
    perfect = config["PERFECT"].lower() == "true"
    output_file = config["OUTPUT_FILE"]
    algo = config["ALGO"]
    seed = int(config["SEED"])
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive greater then 0.")
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ValueError("ENTRY out of bounds")
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ValueError("EXIT out of bounds")
    if algo not in ['DFS', 'PRIME']:
        raise ValueError("choose one algo between DFS or PRIME.")
    if entry_x == exit_x and entry_y == exit_y:
        raise TypeError(
            "Entry and Exit must be separated or make the maze abit bigger")
    # if not isinstance(seed, int):
    #     raise(ValueError("oiahsoiajs"))
    # try:
    # except Exception:
    #     raise ValueError("Make sure seed is a number.")
    return {
        "width": width,
        "height": height,
        "entry": (entry_y, entry_x),
        "exit": (exit_y, exit_x),
        "output_file": output_file,
        "perfect": perfect,
        "algo": algo,
        "seed": seed
    }


def main(stdscr: curses.window) -> None:
    """Main function to initialize and run the maze generation.
    Initializes curses color pairs, creates a maze instance, displays it,
    and runs the depth-first search algorithm to generate the maze paths.
    Waits for user input before exiting.
    Args:
        stdscr: Curses window object provided by curses.wrapper.
    """
    file = sys.argv
    conf = parse_config(file[1])
    entry = conf["entry"]
    exit_point = conf["exit"]
    height = conf["height"]
    width = conf["width"]
    perfect = conf["perfect"]
    algo = conf["algo"]
    seed = conf["seed"]
    output_file = conf["output_file"]

    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    maze_colors = {'1': {'Walls': 1, 'Logo': 2, 'Solution': 6,
                         'Entry': 3, 'Exit': 5},
                   '2': {'Walls': 2, 'Logo': 1, 'Solution': 4,
                         'Entry': 3, 'Exit': 5},
                   '3': {'Walls': 3, 'Logo': 1, 'Solution': 6,
                         'Entry': 2, 'Exit': 5},
                   '4': {'Walls': 4, 'Logo': 3, 'Solution': 2,
                         'Entry': 3, 'Exit': 5},
                   '5': {'Walls': 5, 'Logo': 2, 'Solution': 4,
                         'Entry': 3, 'Exit': 5},
                   '6': {'Walls': 6, 'Logo': 2, 'Solution': 4,
                         'Entry': 3, 'Exit': 5}}
    maze = None
    maze_color = maze_colors['1']
    solution = None
    show_solution = True
    stdscr.clear()
    maze = Maze(height, width, entry, exit_point, perfect)
    maze.display(stdscr, maze_color)
    while True:
        stdscr.addstr(height * 2 + 2, 0, "===========A_MAZ_ING========")
        stdscr.addstr(height * 2 + 3, 0, "1. Generate/Re-generate a new maze")
        stdscr.addstr(height * 2 + 4, 0, "2. Show/Hide solution")
        stdscr.addstr(height * 2 + 5, 0, "3. Change maze's colors")
        stdscr.addstr(height * 2 + 6, 0, "4. Quit")
        stdscr.refresh()

        try:
            choice = stdscr.getch()
            if choice == ord('1'):
                # stdscr.clear()
                if seed:
                    random.seed(seed)
                if (algo == "DFS"):
                    maze = Maze(
                            height,
                            width,
                            entry,
                            exit_point,
                            perfect)
                    maze.dfs(stdscr, entry[0], entry[1], maze_color)
                elif (algo == "PRIME"):
                    maze = Maze(
                            height,
                            width,
                            entry,
                            exit_point,
                            perfect)
                    maze.prime(stdscr, entry[0], entry[1], maze_color)
                if not perfect:
                    maze.make_it_imperfect(stdscr, maze_color)

                # maze.display(stdscr, d_color)
                # choice = stdscr.getch()

            elif choice == ord('2'):
                solution = maze.bfs_solver(entry, exit_point)
                if solution:
                    maze.show_hide_solution_path(stdscr, solution, maze_color,
                                                 show_solution)
                    show_solution = not show_solution
                # choice = stdscr.getch()

            elif choice == ord('3'):
                rndm = random.randint(1, 6)
                maze_color = maze_colors[str(rndm)]
                maze.display(stdscr, maze_color)
                # choice = stdscr.getch()

            elif choice == ord('4'):
                break
            solution = maze.bfs_solver(entry, exit_point)
            create_output_file(output_file, maze.cells, entry,
                               exit_point, solution)
        except Exception as e:
            stdscr.refresh()
            stdscr.clear()
            print(f"They said somthing wrong.{str(e)}")


if __name__ == "__main__":
    try:
        if (len(sys.argv) > 1):
            file = sys.argv
            conf = parse_config(file[len(file) - 1])
            curses.wrapper(main)
        else:
            print("Error: Config file is missing!")
    except KeyboardInterrupt:
        print("\nExited-_^.")
    except FileNotFoundError as e:
        print(f"Error they said : {str(e)}")
    except ValueError as e:
        print(f'Error they said : {str(e)}')
    except curses.error as e:
        print(f"Error they said hello : {str(e)}")
