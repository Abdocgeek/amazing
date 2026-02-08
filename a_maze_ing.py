import curses
import math
import random
import time


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

    def __init__(self, height, width, entry, exit) -> None:
        """Initialize a maze with given dimensions.

        Args:
            height: Number of cells in vertical direction.
            width: Number of cells in horizontal direction.
            entry: Entry point.
            exit: Exit point.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.visited_count = 0
        self.cells_count = width * height
        self.cells = [[0 for x in range(width)] for y in range(height)]
        self.generate_maze()
        self.declare_logo()

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

    def dfs(self, stdscr, y, x) -> None:
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
            self.display(stdscr)
            time.sleep(0.1)

            if self.visited_count < self.cells_count:
                self.dfs(stdscr, ny, nx)

    def display(self, stdscr) -> None:
        """Display the current state of the maze.

        Clears the screen and redraws all cells in the maze with their
        current wall configuration and colors.

        Args:
            stdscr: Curses window object for display.
        """
        stdscr.clear()
        for row in self.cells:
            for cell in row:
                cell.draw(stdscr, self.cells, self.width, self.height,
                          self.entry, self.exit)
        stdscr.refresh()


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

    def __init__(self, x, y, limits) -> None:
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

    def draw(self, stdscr, cells, width, height, entry, exit) -> None:
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

        stdscr.addstr(ny, nx, "█", curses.color_pair(1))
        stdscr.addstr(ny, nx + 3, "█", curses.color_pair(1))
        stdscr.addstr(ny + 2, nx, "█", curses.color_pair(1))
        stdscr.addstr(ny + 2, nx + 3, "█", curses.color_pair(1))

        if self.walls['T'] and ((self.y - 1 >= 0 and
                                cells[self.y - 1][self.x].walls['B']) or
                                self.y == 0):
            stdscr.addstr(ny, nx + 1, "██", curses.color_pair(1))
        elif self.limits['T']:
            stdscr.addstr(ny, nx + 1, "██", curses.color_pair(1))
        else:
            stdscr.addstr(ny, nx + 1, "  ", curses.color_pair(1))

        if self.walls['B']:
            stdscr.addstr(ny + 2, nx + 1, "██", curses.color_pair(1))
        elif self.limits['B']:
            stdscr.addstr(ny + 2, nx + 1, "██", curses.color_pair(1))
        else:
            stdscr.addstr(ny + 2, nx + 1, "  ", curses.color_pair(1))

        if self.walls['L'] and ((self.x - 1 >= 0 and
                                cells[self.y][self.x - 1].walls['R']) or
                                self.x == 0):
            stdscr.addstr(ny + 1, nx, "█", curses.color_pair(1))
        elif self.limits['L']:
            stdscr.addstr(ny + 1, nx, "█", curses.color_pair(1))
        else:
            stdscr.addstr(ny + 1, nx, " ", curses.color_pair(1))

        if self.walls['R'] and ((self.x + 1 < width and
                                cells[self.y][self.x + 1].walls['L']) or
                                self.x == width - 1):
            stdscr.addstr(ny + 1, nx + 3, "█", curses.color_pair(1))
        elif self.limits['R']:
            stdscr.addstr(ny + 1, nx + 3, "█", curses.color_pair(1))
        else:
            stdscr.addstr(ny + 1, nx + 3, " ", curses.color_pair(1))

        if self.logo:
            stdscr.addstr(ny + 1, nx + 1, "██", curses.color_pair(2))
        elif self.x == entry[1] and self.y == entry[0]:
            stdscr.addstr(ny + 1, nx + 1, "██", curses.color_pair(3))
        elif self.x == exit[1] and self.y == exit[0]:
            stdscr.addstr(ny + 1, nx + 1, "██", curses.color_pair(4))
        else:
            stdscr.addstr(ny + 1, nx + 1, "  ", curses.color_pair(1))


def main(stdscr) -> None:
    """Main function to initialize and run the maze generation.

    Initializes curses color pairs, creates a maze instance, displays it,
    and runs the depth-first search algorithm to generate the maze paths.
    Waits for user input before exiting.

    Args:
        stdscr: Curses window object provided by curses.wrapper.
    """
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    # random.seed(42)
    entry = (12, 1)
    # exit = (14, 12)
    exit = (12, 14)
    maze = Maze(13, 15, entry, exit)
    maze.display(stdscr)
    maze.dfs(stdscr, entry[0], entry[1])

    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
