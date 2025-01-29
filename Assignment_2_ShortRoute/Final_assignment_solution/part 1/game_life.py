# game_life.py

from mpi4py import MPI
import numpy as np
from functions_game_life import update_Grid_GameofLife, exchange_ghost_rows 

# 1. Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# 2. Define the grid
grid_rows = 20
grid_cols = 20

# Number of rows per process
rows_per_process = grid_rows // size
remaining_rows = grid_rows % size
if rank < remaining_rows:
    start_row = (rows_per_process + 1) * rank
    local_grid_rows = rows_per_process + 1
else:
    start_row = (rows_per_process + 1) * remaining_rows + rows_per_process * (rank - remaining_rows)
    local_grid_rows = rows_per_process

# 3. Initialize local grid (strip) for each process
local_grid = np.random.randint(2, size=(local_grid_rows, grid_cols))

# Number of steps to simulate
num_steps = 10  

# 5. Simulation loop
for step in range(num_steps):

    # Exchange ghost rows with neighboring processes
    top_ghost_row, bottom_ghost_row = exchange_ghost_rows(local_grid, grid_cols, rank, size, comm)  # Pass comm

    # Update the local grid with the new state
    update_Grid_GameofLife(local_grid, top_ghost_row, bottom_ghost_row)

    # Gather the updated grids on the root process
    if rank == 0:
        # container to receive the updated grids from all processes
        full_grid = np.empty((grid_rows, grid_cols), dtype=int)

        # This particularly for large grid size since the console has limitation of number of charcters check shape of grid 
        print(full_grid.shape) 
    else:
        full_grid = None

    # Gather all local grids into the full_grid array on the root process
    comm.Gather(local_grid, full_grid, root=0)

    # 6. Visualization on the root process
    if rank == 0:
        print(f"Step {step}:")
        for row in full_grid:
            print(' '.join(str(cell) for cell in row))
        print("\n" + "="*40 + "\n")
        
