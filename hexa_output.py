"""Hexadecimal maze output module.

Exports the maze structure and solution path to a file using a hex encoding.
Each cell maps to one hex character via the bitmask: T=1, R=2, B=4, L=8.
"""
from typing import TYPE_CHECKING, Iterable, Optional, Sequence, Tuple

if TYPE_CHECKING:
    from a_maze_ing import Cell


def create_output_file(
        file: str,
        cells: Sequence[Sequence["Cell"]],
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        solution: Optional[Iterable[Tuple[int, int]]]
        ) -> None:
    """Export the maze structure and solution path to a file.

    The maze grid is encoded using a hexadecimal representation where each
    cell is represented by a single hex digit corresponding to its wall
    configuration using the following bitmask:

        Top    = 1
        Right  = 2
        Bottom = 4
        Left   = 8

    After the grid, the file contains:
        - Entry coordinates (x,y)
        - Exit coordinates (x,y)
        - Solution path directions as characters:
          'N', 'S', 'E', 'W'

    Args:
        file_path: Path to the output file.
        cells: 2D grid of Cell objects representing the maze.
        entry: Entry position as (row, column).
        exit_point: Exit position as (row, column).
        solution: Ordered iterable of (row, column) positions forming
            the solution path. If None, no path is written.

    Returns:
        None
    """
    total = 0
    hexa = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F']
    with open(file, "w") as f:
        for row in cells:
            for cell in row:
                total = 0
                if cell.walls['T']:
                    total += 1
                if cell.walls['R']:
                    total += 2
                if cell.walls['B']:
                    total += 4
                if cell.walls['L']:
                    total += 8
                f.write(hexa[total])
            f.write('\n')

        f.write(f"\n{entry[1]},{entry[0]}\n")
        f.write(f"{exit[1]},{exit[0]}\n")

        if solution is not None:
            x = entry[1]
            y = entry[0]
            for cel in solution:
                nx = cel[1]
                ny = cel[0]
                if nx - x > 0:
                    f.write('E')
                elif nx - x < 0:
                    f.write('W')
                elif ny - y > 0:
                    f.write('S')
                elif ny - y < 0:
                    f.write('N')
                x = nx
                y = ny
            f.write('\n')
