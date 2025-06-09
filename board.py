GRID_SIZE = 10

def create_board():
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def can_place_ship(board, row, col, length, orientation):
    if row < 0 or col < 0 or row >= GRID_SIZE or col >= GRID_SIZE:
        return False
    if orientation == "H":
        if col + length > GRID_SIZE:
            return False
        for i in range(length):
            if board[row][col + i] != 0:
                return False
    else:
        if row + length > GRID_SIZE:
            return False
        for i in range(length):
            if board[row + i][col] != 0:
                return False
    return True

def place_ship(board, row, col, length, orientation):
    if orientation == "H":
        for i in range(length):
            board[row][col + i] = 1
    else:
        for i in range(length):
            board[row + i][col] = 1

def get_ship_cells(row, col, length, orientation):
    if orientation == "H":
        return [(row, col + i) for i in range(length)]
    else:
        return [(row + i, col) for i in range(length)]

def remove_ship(board, ship_cells):
    for r, c in ship_cells:
        board[r][c] = 0

def check_victory(board):
    for row in board:
        if 1 in row:
            return False
    return True
