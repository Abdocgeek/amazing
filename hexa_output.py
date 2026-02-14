def create_output_file(cells, entry, exit):
    total = 0
    hexa = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F']
    with open("output_maze.txt", "w") as file:
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
                file.write(hexa[total])
            file.write('\n')

        file.write(f"\n{entry[0]},{entry[1]}\n")
        file.write(f"{exit[0]},{exit[1]}")
