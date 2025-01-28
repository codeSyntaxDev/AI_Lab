import numpy as np
import matplotlib.pyplot as plt
import random

def generate_heuristic_grid(rows, cols, peak=(5, 5), scale=5):
    x = np.arange(rows)
    y = np.arange(cols)
    X, Y = np.meshgrid(x, y)

    # Gaussian function: creates a "mountain" shape
    heuristic_grid = np.exp(-((X - peak[0])**2 + (Y - peak[1])**2) / (2 * scale**2))
    heuristic_grid = 1 - heuristic_grid  # Invert to find minimum
    return heuristic_grid

def hill_climbing(grid, start):
    rows, cols = grid.shape
    current = start
    path = [current]

    while True:
        x, y = current
        neighbors = []

        # Get valid neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                neighbors.append((nx, ny))

        # Evaluate heuristic for neighbors
        neighbors = [(grid[nx, ny], (nx, ny)) for nx, ny in neighbors]

        if not neighbors:
            # No valid moves, end search
            break

        # Find the neighbor with the lowest heuristic value
        neighbors.sort()  # Sort by heuristic
        best_heuristic, best_neighbor = neighbors[0]

        if grid[x, y] <= best_heuristic:
            # Stop if no improvement
            break

        current = best_neighbor
        path.append(current)

    return path, current

def random_restart_hill_climbing(grid, max_restarts):
    rows, cols = grid.shape
    best_path = None
    best_position = None
    best_value = float('inf')  # Initialize with a high value
    all_paths = []

    for restart in range(max_restarts):
        # Start from a random position
        start = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        path, final_position = hill_climbing(grid, start)
        final_value = grid[final_position]

        all_paths.append((path, final_position, final_value))

        # Update the best solution found so far
        if final_value < best_value:
            best_value = final_value
            best_position = final_position
            best_path = path

        print(f"Restart {restart + 1}: Start={start}, End={final_position}, Value={final_value:.2f}")

    return best_path, best_position, best_value, all_paths

def plot_heuristic_grid(grid, best_path, all_paths, start, goal):
    plt.figure(figsize=(10, 10))
    plt.imshow(grid, cmap='viridis', origin='lower')
    
    # Plot all paths
    for path, _, _ in all_paths:
        path = np.array(path)
        plt.plot(path[:, 1], path[:, 0], color='gray', alpha=0.3, linestyle='--', label='Other Paths' if 'Other Paths' not in plt.gca().get_legend_handles_labels()[1] else "")

    # Highlight the best path
    if best_path:
        best_path = np.array(best_path)
        plt.plot(best_path[:, 1], best_path[:, 0], color='red', label='Best Path')

    plt.scatter(goal[1], goal[0], color='blue', s=100, label='Goal')
    plt.colorbar(label="Heuristic Value")
    plt.legend()
    plt.title("Random Restart Hill Climbing on Heuristic Grid")
    plt.show()

# Parameters
rows, cols = 10, 10
goal = (5, 5)  # Peak of the heuristic function
scale = 2  # Controls the width of the "mountain"
max_restarts = 5  # Number of random restarts

# Generate heuristic grid
heuristic_grid = generate_heuristic_grid(rows, cols, peak=goal, scale=scale)

# Print heuristic grid
print("Heuristic Grid:")
print(np.round(heuristic_grid, 2))

# Solve using Random Restart Hill Climbing
best_path, best_position, best_value, all_paths = random_restart_hill_climbing(heuristic_grid, max_restarts)

# Results
print("\nBest Path Found:", best_path)
print("Best Final Position:", best_position)
print("Best Heuristic Value:", best_value)

# Plot the grid and paths
plot_heuristic_grid(heuristic_grid, best_path, all_paths, start=None, goal=goal)