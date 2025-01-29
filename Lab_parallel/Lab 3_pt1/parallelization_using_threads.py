import threading
import time


# Define a function to calculate the sum of numbers in a given range.
# The results of the sum are appended to a shared list.
def calculate_sum_for_threads(start: int = 1,
                              end: int = 1000,
                              results_list: list = []):
    result = 0
    for i in range(start, end + 1):
        result += i
    # Append the computed sum to the shared list.
    results_list.append(result)


# Record the start time of the program execution.
start_time = time.time()

# Define the total number of integers to sum.
n = int(1e8)
# Define the number of threads to create.
num_threads = 4
# Calculate the range of numbers each thread will process.
step = n // 4

# Initialize a list to hold the created threads.
threads = []
# Initialize a list to store the results from each thread.
results = []

# Create and start threads in a loop.
for i in range(num_threads):
    # Calculate the start and end range for each thread.
    start_thread = (i * step) + 1
    end_thread = (i + 1) * step
    # Create a Thread instance, targeting the calculate_sum_for_threads function.
    thread = threading.Thread(target=calculate_sum_for_threads,
                              args=(start_thread,
                                    end_thread,
                                    results))
    # Append the created thread to the threads list.
    threads.append(thread)
    # Start the thread's execution.
    thread.start()

# Wait for all threads to finish.
for thread in threads:
    thread.join()

# Print the sum of the results from all threads.
print(sum(results))
# Record the end time of the program execution.
end_time = time.time()

# Print the total execution time.
print(f"All threads have finished, the execution time is {end_time - start_time}")
