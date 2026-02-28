#!/usr/bin/env python

"""Maze generator and solver with curses.

This module provides an interactive terminal maze application that
supports two algorithms (DFS and PRIME), BFS solving, and animated
solution path display.

Typical usage:

    python a_maz_ing.py config.txt

The config file must define WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE
PERFCT, ALGO, SEED.
Enjoy playing the maze.
"""


import curses
import random
import sys
from hexa_output import create_output_file
from mazegen.mazegen import MazeGenerator
from parse_config_file import parse_config


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
    maze = MazeGenerator(height, width, entry, exit_point, perfect, maze_color)
    exit_x = exit_point[1]
    exit_y = exit_point[0]
    entry_x = entry[1]
    entry_y = entry[0]
    if maze.cells[exit_y][exit_x].logo:
        raise ValueError("Exit have the same coordinates!")
    if maze.cells[entry_y][entry_x].logo:
        raise ValueError("Ba3ad entry mn logo please!")

    stdscr.addstr(height * 2 + 2, 0, "===========A_MAZ_ING========")
    stdscr.addstr(height * 2 + 3, 0, "1. Re-generate a new maze")
    stdscr.addstr(height * 2 + 4, 0, "2. Show/Hide solution")
    stdscr.addstr(height * 2 + 5, 0, "3. Change maze's colors")
    stdscr.addstr(height * 2 + 6, 0, "4. Quit")
    stdscr.refresh()

    if seed is not None:
        random.seed(seed)
    if (algo == "DFS"):
        maze.dfs(stdscr, entry[0], entry[1])
    elif (algo == "PRIME"):
        maze.prime(stdscr, entry[0], entry[1])

    solution = maze.bfs_solver(entry, exit_point)
    create_output_file(output_file, maze.cells, entry, exit_point, solution)

    while True:
        stdscr.addstr(height * 2 + 2, 0, "===========A_MAZ_ING========")
        stdscr.addstr(height * 2 + 3, 0, "1. Re-generate a new maze")
        stdscr.addstr(height * 2 + 4, 0, "2. Show/Hide solution")
        stdscr.addstr(height * 2 + 5, 0, "3. Change maze's colors")
        stdscr.addstr(height * 2 + 6, 0, "4. Quit")
        stdscr.refresh()

        try:
            choice = stdscr.getch()
            if choice == ord('1'):
                if seed is not None:
                    random.seed(seed)
                maze = MazeGenerator(height, width, entry, exit_point,
                                     perfect, maze_color)
                if (algo == "DFS"):
                    maze.dfs(stdscr, entry[0], entry[1])
                elif (algo == "PRIME"):
                    maze.prime(stdscr, entry[0], entry[1])

            elif choice == ord('2'):
                solution = maze.bfs_solver(entry, exit_point)
                if solution:
                    maze.show_hide_solution_path(stdscr, solution,
                                                 show_solution)
                    show_solution = not show_solution

            elif choice == ord('3'):
                rndm = random.randint(1, 6)
                maze_color = maze_colors[str(rndm)]
                maze.maze_color = maze_color
                maze.display(stdscr)

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
        print(f"Error: {str(e)}")
    except ValueError as e:
        print(f'Error: {str(e)}')
    except curses.error:
        print("Error: Screen size is not enough!")
    except Exception as e:
        print(e)
