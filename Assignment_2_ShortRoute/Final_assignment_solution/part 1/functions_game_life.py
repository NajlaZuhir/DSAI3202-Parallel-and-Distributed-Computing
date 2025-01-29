# functions_game_life.py

from mpi4py import MPI
import numpy as np  

def update_Grid_GameofLife(local_grid, top_ghost_row, bottom_ghost_row):

    """
        Purpose: Updating local grid according to the rules of Game of Life,
        using the provided top and bottom ghost rows to create an extended grid.

        Parameters (numpy.ndarray):
        - local_grid: local grid to be updated.
        - top_ghost_row: ghost row above the local grid.
        - bottom_ghost_row : ghost row below the local grid.

        Returns:
        - None: The function modifies the `local_grid` array in place (o(1)).

    """

    # Extended grid includes the local grid plus the top and bottom ghost rows
    extended_grid = np.vstack([top_ghost_row, local_grid, bottom_ghost_row])
    n_rows, n_cols = extended_grid.shape

    # Function to count neighbors for extended grid with ghost rows
    def count_neighbors(r, c):
        nei = 0
        for i in range(max(0, r - 1), min(r + 2, n_rows)):
            for j in range(max(0, c - 1), min(c + 2, n_cols)):
                if i == r and j == c:
                    continue
                # checking for live cells
                if extended_grid[i][j] in [1, 3]:
                    nei += 1
        return nei

    # Apply Game of Life rules
    for r in range(1, n_rows - 1):  # Exclude ghost rows in iteration
        for c in range(n_cols):
            nei_alive = count_neighbors(r, c)
            if extended_grid[r][c] == 1 and nei_alive in [2, 3]:
                local_grid[r - 1][c] = 3  # Alive to Alive
            elif extended_grid[r][c] == 0 and nei_alive == 3:
                local_grid[r - 1][c] = 2  # Dead to Alive

    # apply the temporary state transitions
    for r in range(local_grid.shape[0]):
        for c in range(local_grid.shape[1]):
            if local_grid[r][c] == 3:
                local_grid[r][c] = 1  # Remain alive
            elif local_grid[r][c] == 2:
                local_grid[r][c] = 1  # Become alive
            else:
                local_grid[r][c] = 0  # Become dead or remain dead



def exchange_ghost_rows(local_grid, grid_cols, rank, size, comm): 

    """
        Purpose: Exchange ghost rows between neighboring processes in a distributed grid.

        Parameters:
        - local_grid (numpy.ndarray): The local grid of the current process.
        - grid_cols (int): The number of columns in the grid.
        - rank (int): The rank of the current process.
        - size (int): The total number of MPI processes.
        - comm (MPI.Comm): The MPI communicator object.

        Returns:
        - tuple: A tuple containing the top ghost row and the bottom ghost row.

    """

    top_ghost_row = np.empty(grid_cols, dtype=int)
    bottom_ghost_row = np.empty(grid_cols, dtype=int)

    reqs = []

    # Send and receive bottom row
    if rank < size - 1:
        reqs.append(comm.Isend(local_grid[-1], dest=rank + 1))
        reqs.append(comm.Irecv(bottom_ghost_row, source=rank + 1))
    # Send and receive top row
    if rank > 0:
        reqs.append(comm.Isend(local_grid[0], dest=rank - 1))
        reqs.append(comm.Irecv(top_ghost_row, source=rank - 1))

    MPI.Request.Waitall(reqs)

    if rank == 0:
        top_ghost_row[:] = 0  # incase dead cells beyond the top edge
    if rank == size - 1:
        bottom_ghost_row[:] = 0  # incase dead cells beyond the bottom edge

    return top_ghost_row, bottom_ghost_row
