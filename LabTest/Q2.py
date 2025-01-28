import random

PARAMETER_RANGES = {
    "M": (20, 100),  
    "T": (10, 40),  
    "L": (20, 100),  
    "F": (10, 20)  
}

def calculate_strength(params):
    M, T, L, F = params
    return (M * 0.8) + (T * 1.5) + (L * 0.2) + (F * 0.5)

def generate_individual():
    return [
        random.uniform(PARAMETER_RANGES["M"][0], PARAMETER_RANGES["M"][1]),
        random.uniform(PARAMETER_RANGES["T"][0], PARAMETER_RANGES["T"][1]),
        random.uniform(PARAMETER_RANGES["L"][0], PARAMETER_RANGES["L"][1]),
        random.uniform(PARAMETER_RANGES["F"][0], PARAMETER_RANGES["F"][1]),
    ]

def generate_population(size):
    return [generate_individual() for _ in range(size)]

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2


def mutate(individual, mutation_rate=0.1):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            param_key = list(PARAMETER_RANGES.keys())[i]
            individual[i] = random.uniform(PARAMETER_RANGES[param_key][0], PARAMETER_RANGES[param_key][1])

def tournament_selection(population, scores, k=3):
    selected = random.sample(list(zip(population, scores)), k)
    selected.sort(key=lambda x: x[1], reverse=True)
    return selected[0][0]


def genetic_algorithm(population_size, generations, mutation_rate=0.1):
    population = generate_population(population_size)

    for generation in range(generations):
        scores = [calculate_strength(ind) for ind in population]
        next_generation = []

        while len(next_generation) < population_size:
       
            parent1 = tournament_selection(population, scores)
            parent2 = tournament_selection(population, scores)

            child1, child2 = crossover(parent1, parent2)

            mutate(child1, mutation_rate)
            mutate(child2, mutation_rate)

            next_generation.append(child1)
            next_generation.append(child2)

        population = next_generation[:population_size]

        best_score = max(scores)
        best_individual = population[scores.index(best_score)]
        print(f"Generation {generation + 1}: Best Strength = {best_score}, Params = {best_individual}")

    scores = [calculate_strength(ind) for ind in population]
    best_index = scores.index(max(scores))
    return population[best_index], max(scores)

best_individual, best_strength = genetic_algorithm(population_size=50, generations=100, mutation_rate=0.1)
print(f"\nOptimal Rope Parameters: {best_individual}")
print(f"Maximum Rope Strength: {best_strength}")