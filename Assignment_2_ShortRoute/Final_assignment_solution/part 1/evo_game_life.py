import os
import time
import random

def random_board(rows, cols):
    return [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]

def gameOfLife(board):
    n_rows, n_cols = len(board), len(board[0])

    def countNeighbors(r, c):
        nei = 0
        for i in range(r - 1, r + 2):
            for j in range(c - 1, c + 2):
                if ((i == r and j == c) or i < 0 or j < 0 or i == n_rows or j == n_cols):
                    continue
                if board[i][j] in [1, 3]:
                    nei += 1
        return nei

    for r in range(n_rows):
        for c in range(n_cols):
            nei_alive = countNeighbors(r, c)
            if board[r][c] == 1 and nei_alive in [2, 3]:
                board[r][c] = 3  # Alive to Alive
            elif board[r][c] == 0 and nei_alive == 3:
                board[r][c] = 2  # Dead to Alive

    for r in range(n_rows):
        for c in range(n_cols):
            if board[r][c] == 3:
                board[r][c] = 1  # Remain alive
            elif board[r][c] == 2:
                board[r][c] = 1  # Become alive
            else:
                board[r][c] = 0  # Become dead or remain dead

    return board

def print_board(board):
    for row in board:
        print(' '.join(map(str, row)))
    print()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main(rows, cols):
    my_board = random_board(rows, cols)

    while True:
        print_board(my_board)
        time.sleep(1)  # Adjust the speed of updates as needed
        clear_screen()
        my_board = gameOfLife(my_board)

if __name__ == "__main__":
    rows = 20
    cols = 20
    main(rows, cols)
