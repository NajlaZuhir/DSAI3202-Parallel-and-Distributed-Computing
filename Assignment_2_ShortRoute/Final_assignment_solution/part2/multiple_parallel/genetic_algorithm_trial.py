import numpy as np
import pandas as pd
import time
from genetic_algorithms_functions import calculate_fitness, \
    select_in_tournament, order_crossover, mutate, \
    generate_unique_population
from celery_app import calculate_fitness_async

# Load the distance matrix
distance_matrix = pd.read_csv('city_distances.csv').to_numpy()

# Parameters
num_nodes = distance_matrix.shape[0]
population_size = 10000
num_tournaments = 4  # Number of tournaments to run
mutation_rate = 0.1
num_generations = 200
infeasible_penalty = 1e6  # Penalty for infeasible routes
stagnation_limit = 5  # Number of generations without improvement before regeneration


# Generate initial population: each individual is a route starting at node 0
np.random.seed(42)  # For reproducibility
population = generate_unique_population(population_size, num_nodes)

# Initialize variables for tracking stagnation
best_calculate_fitness = int(1e6)
stagnation_counter = 0

start_time =  time.time()
# Main GA loop
def chunked_routes(routes, chunk_size=20):
    for i in range(0, len(routes), chunk_size):
        yield routes[i:i + chunk_size]

for generation in range(num_generations):
    async_results = []
    for route_chunk in chunked_routes(population, 100):  # Adjust chunk size as needed

        route_chunk = [[int(node) for node in route] for route in route_chunk]
        async_results.append(calculate_fitness_async.delay(route_chunk))

    # Gather and process results
    calculate_fitness_values = np.concatenate([result.get() for result in async_results])

    current_best_calculate_fitness = np.min(calculate_fitness_values)
    if current_best_calculate_fitness < best_calculate_fitness:
        best_calculate_fitness = current_best_calculate_fitness
        stagnation_counter = 0
    else:
        stagnation_counter += 1

    # Regenerate population if stagnation limit is reached, keeping the best individual
    if stagnation_counter >= stagnation_limit:
        print(f"Regenerating population at generation {generation} due to stagnation")
        best_individual = population[np.argmin(calculate_fitness_values)]
        population = generate_unique_population(population_size - 1, num_nodes)
        population.append(best_individual)
        stagnation_counter = 0
        continue  # Skip the rest of the loop for this generation

    # Selection, crossover, and mutation
    selected = select_in_tournament(population,
                                    calculate_fitness_values)
    offspring = []
    for i in range(0, len(selected), 2):
        parent1, parent2 = selected[i], selected[i + 1]
        route1 = order_crossover(parent1[1:], parent2[1:])
        offspring.append([0] + route1)
    mutated_offspring = [mutate(route, mutation_rate) for route in offspring]

    # Replacement: Replace the individuals that lost in the tournaments with the new offspring
    for i, idx in enumerate(np.argsort(calculate_fitness_values)[::-1][:len(mutated_offspring)]):
        population[idx] = mutated_offspring[i]

    # Ensure population uniqueness
    unique_population = set(tuple(ind) for ind in population)
    while len(unique_population) < population_size:
        individual = [0] + list(np.random.permutation(np.arange(1, num_nodes)))
        unique_population.add(tuple(individual))
    population = [list(individual) for individual in unique_population]

    # Print best calculate_fitness
    print(f"Generation {generation}: Best calculate_fitness = {current_best_calculate_fitness}")

# Update calculate_fitness_values for the final population
calculate_fitness_values = np.array([calculate_fitness(route, distance_matrix) for route in population])

# Output the best solution
end_time = time.time()
best_idx = np.argmin(calculate_fitness_values)
best_solution = population[best_idx]
print("Best Solution:", best_solution)
print("Total Distance:", calculate_fitness(best_solution, distance_matrix))
print(f"Execution time: {end_time - start_time} seconds")
