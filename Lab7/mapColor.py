# Map Coloring Problem using Backtracking

# Function to check if coloring is safe
def is_safe(node, color, colors, graph):
    for neighbor in graph[node]:
        if colors[neighbor] == color:
            return False
    return True

# Backtracking function
def map_coloring(graph, colors, node, num_colors):
    if node == len(graph):  # All nodes colored
        return True
    
    for color in range(1, num_colors + 1):
        if is_safe(node, color, colors, graph):
            colors[node] = color
            if map_coloring(graph, colors, node + 1, num_colors):
                return True
            colors[node] = 0  # Backtrack

    return False

# Wrapper function
def solve_map_coloring(graph, num_colors):
    colors = [0] * len(graph)  # Initialize colors
    
    if not map_coloring(graph, colors, 0, num_colors):
        print("No solution exists")
        return None

    return colors

# Example Graph (Adjacency List Representation)
graph = {
    0: [1, 2, 3],
    1: [0, 2],
    2: [0, 1, 3],
    3: [0, 2]
}

num_colors = 3  # Number of colors available

# Solve the problem
solution = solve_map_coloring(graph, num_colors)

# Print solution
if solution:
    print("Coloring of the map:", solution)