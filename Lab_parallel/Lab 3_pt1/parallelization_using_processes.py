import multiprocessing
import os


# Define a function to calculate the sum of numbers in a given range.
# The result is written to a file to be collected later by the main process.
def calculate_sum(start, end, result_file):
    # Calculate the sum of numbers in the range [start, end].
    total = sum(range(start, end + 1))
    # Open a file in write mode to store the result.
    with open(result_file, 'w') as f:
        # Write the calculated sum to the file.
        f.write(str(total))


# Define the total number of integers to sum.
n = int(1e8)
# Define the number of processes to create.
num_processes = 4
# Calculate the range of numbers each process will handle.
step = n // num_processes

# Initialize a list to hold the created processes.
processes = []

# Create and start processes in a loop.
for i in range(num_processes):
    # Calculate the start and end range for each process.
    start_process = (i * step) + 1
    # Ensure the last process gets the remainder of the range.
    end_process = (i + 1) * step if i != num_processes - 1 else n
    # Define a unique result file for each process.
    result_file = f'result_{i}.txt'

    # Create a Process instance, targeting the calculate_sum function.
    process = multiprocessing.Process(target=calculate_sum, args=(start_process, end_process, result_file))
    # Append the created process to the processes list.
    processes.append(process)
    # Start the process's execution.
    process.start()

# Wait for all processes to finish.
for process in processes:
    process.join()

# Collect results from the result files and remove the files.
results = []
for i in range(num_processes):
    # Define the result file for the current index.
    result_file = f'result_{i}.txt'
    # Open the result file in read mode.
    with open(result_file, 'r') as f:
        # Read the result from the file, convert it to an integer, and append it to the results list.
        results.append(int(f.read().strip()))
    # Remove the result file to clean up.
    os.remove(result_file)

# Calculate the sum of the results from all processes.
print(sum(results))
# Indicate that all processes have finished.
print("All processes have finished")
