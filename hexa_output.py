def create_output_file(file, cells, entry, exit, solution):
    total = 0
    hexa = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F']
    with open(file, "w") as file:
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

        file.write(f"\n{entry[1]},{entry[0]}\n")
        file.write(f"{exit[1]},{exit[0]}\n")

        x = entry[1]
        y = entry[0]
        for cell in solution:
            nx = cell[1]
            ny = cell[0]
            if nx - x > 0:
                file.write('E')
            elif nx - x < 0:
                file.write('W')
            elif ny - y > 0:
                file.write('S')
            elif ny - y < 0:
                file.write('N')
            x = nx
            y = ny
        file.write('\n')
