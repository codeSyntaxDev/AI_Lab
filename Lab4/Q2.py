import numpy as np
import matplotlib.pyplot as plt

def rastrigin(x):
    A = 10
    return A * len(x) + np.sum(x**2 - A * np.cos(2 * np.pi * x))

def initialize_population(pop_size, n_dim, lower_bound, upper_bound):
    population = np.random.uniform(lower_bound, upper_bound, (pop_size, n_dim))
    return population

def fitness(population):
    return np.apply_along_axis(rastrigin, 1, population)

def selection(population, fitness_vals, num_parents):
    parents = []
    for _ in range(num_parents):
        idx1, idx2 = np.random.choice(len(population), size=2, replace=False)
        if fitness_vals[idx1] < fitness_vals[idx2]:
            parents.append(population[idx1])
        else:
            parents.append(population[idx2])
    return np.array(parents)

def crossover(parents, crossover_rate):
    num_parents = len(parents)
    offspring = []
    for i in range(0, num_parents, 2):
        if np.random.rand() < crossover_rate:
            crossover_point = np.random.randint(1, parents.shape[1])
            offspring1 = np.hstack((parents[i, :crossover_point], parents[i+1, crossover_point:]))
            offspring2 = np.hstack((parents[i+1, :crossover_point], parents[i, crossover_point:]))
            offspring.append(offspring1)
            offspring.append(offspring2)
        else:
            offspring.append(parents[i])
            offspring.append(parents[i+1])
    return np.array(offspring)

def mutation(offspring, mutation_rate, lower_bound, upper_bound):
    for i in range(len(offspring)):
        if np.random.rand() < mutation_rate:
            mutation_point = np.random.randint(offspring.shape[1])
            mutation_value = np.random.normal(0, 0.1)
            offspring[i, mutation_point] += mutation_value
            offspring[i, mutation_point] = np.clip(offspring[i, mutation_point], lower_bound, upper_bound)
    return offspring

def genetic_algorithm(pop_size, n_dim, lower_bound, upper_bound, generations, crossover_rate, mutation_rate, num_parents):
    population = initialize_population(pop_size, n_dim, lower_bound, upper_bound)
    best_solution = None
    best_fitness = float('inf')
    
    for generation in range(generations):
        fitness_vals = fitness(population)
        min_fitness_idx = np.argmin(fitness_vals)
        if fitness_vals[min_fitness_idx] < best_fitness:
            best_fitness = fitness_vals[min_fitness_idx]
            best_solution = population[min_fitness_idx]
        
        parents = selection(population, fitness_vals, num_parents)
        offspring = crossover(parents, crossover_rate)
        offspring = mutation(offspring, mutation_rate, lower_bound, upper_bound)
        
        population = np.vstack((parents, offspring))[:pop_size]
        
        if generation % 50 == 0:
            print(f"Generation {generation}, Best Fitness: {best_fitness}")
    
    return best_solution, best_fitness

pop_size = 50
n_dim = 2
lower_bound = -5.12
upper_bound = 5.12
generations = 500
crossover_rate = 0.8
mutation_rate = 0.1
num_parents = 20

best_solution, best_fitness = genetic_algorithm(pop_size, n_dim, lower_bound, upper_bound, generations, crossover_rate, mutation_rate, num_parents)

print(f"Best Solution: {best_solution}")
print(f"Best Fitness: {best_fitness}")

x = np.linspace(lower_bound, upper_bound, 400)
y = np.linspace(lower_bound, upper_bound, 400)
X, Y = np.meshgrid(x, y)

Z = np.zeros(X.shape)
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        Z[i, j] = rastrigin(np.array([X[i, j], Y[i, j]]))  # Pass a NumPy array here

plt.figure(figsize=(10, 8))
plt.contourf(X, Y, Z, 50, cmap='viridis')
plt.colorbar(label="Fitness (Rastrigin Function Value)")
plt.scatter(best_solution[0], best_solution[1], color='red', label='Best Solution')
plt.title("Genetic Algorithm Optimization on Rastrigin Function")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.show()