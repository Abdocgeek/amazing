import curses
import math
import random
import time


class Maze:
    def __init__(self, height, width, entry, exit, perfect):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.visited_count = 0
        self.cells_count = width * height
        self.perfect_maze = perfect
        self.cells = [[0 for x in range(width)] for y in range(height)]
        self.generate_maze()
        self.declare_logo()

    def generate_maze(self):
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

    def declare_logo(self):
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

    def dfs(self, stdscr, y, x):
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
            if self.perfect_maze:
                self.cells[ny][nx].visited = True
                self.visited_count += 1
            else:
                if random.random() < 0.8:
                    self.cells[ny][nx].visited = True
                    self.visited_count += 1
            self.display(stdscr)
            time.sleep(0.1)

            if self.visited_count < self.cells_count:
                self.dfs(stdscr, ny, nx)

    def display(self, stdscr):
        stdscr.clear()
        for row in self.cells:
            for cell in row:
                cell.draw(stdscr, self.cells, self.width, self.height,
                          self.entry, self.exit)
        stdscr.refresh()


class Cell:
    def __init__(self, x, y, limits):
        self.walls = {'T': True, 'B': True, 'L': True, 'R': True}
        self.limits = limits
        self.x = x
        self.y = y
        self.logo = False
        self.visited = False

    def draw(self, stdscr, cells, width, height, entry, exit):

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


def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    # random.seed(42)
    entry = (12, 1)
    # exit = (14, 12)
    exit = (12, 14)
    perfect = True
    maze = Maze(13, 15, entry, exit, perfect)
    maze.display(stdscr)
    maze.dfs(stdscr, entry[0], entry[1])

    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)
