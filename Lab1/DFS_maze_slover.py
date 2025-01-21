# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def create_graph(maze):
    """
    Convert a maze into a graph where each walkable cell is a node,
    and edges connect adjacent walkable cells.

    Args:
        maze (numpy.ndarray): 2D array representing the maze 
                               (1 = walkable path, 0 = wall)

    Returns:
        networkx.Graph: Graph representation of the maze
    """
    G = nx.Graph()
    rows, cols = maze.shape

    for r in range(rows):
        for c in range(cols):
            if maze[r, c] == 1:  # Ensure only walkable cells are nodes
                if r > 0 and maze[r-1, c] == 1:  # Up
                    G.add_edge((r, c), (r-1, c))
                if r < rows - 1 and maze[r+1, c] == 1:  # Down
                    G.add_edge((r, c), (r+1, c))
                if c > 0 and maze[r, c-1] == 1:  # Left
                    G.add_edge((r, c), (r, c-1))
                if c < cols - 1 and maze[r, c+1] == 1:  # Right
                    G.add_edge((r, c), (r, c+1))

    return G

def dfs_all_paths_iterative(G, start, end, maze):
    """
    Perform Depth-First Search (DFS) iteratively to find a valid path from start to end.

    Args:
        G (networkx.Graph): Graph representing the maze
        start (tuple): Starting node coordinates
        end (tuple): Target/ending node coordinates
        maze (numpy.ndarray): 2D array representing the maze (used for walkability validation)

    Returns:
        tuple: Contains the path found and number of nodes explored
    """
    stack = [(start, [start])]  # Stack to store (current_node, path_so_far)
    nodes_explored = 0
    visited = set()

    while stack:
        current, path = stack.pop()
        nodes_explored += 1

        if current in visited:
            continue
        visited.add(current)

        if current == end:
            return path, nodes_explored

        for neighbor in G.neighbors(current):
            # Ensure the neighbor is a walkable cell
            if maze[neighbor[0], neighbor[1]] == 1 and neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))

    return None, nodes_explored

def visualize_maze_with_cursor_no_animation(maze, path):
    """
    Visualize the maze and the movement along the path step-by-step.

    Args:
        maze (numpy.ndarray): 2D array representing the maze
        path (list): List of coordinates showing the path from start to end
    """
    rows, cols = maze.shape
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(maze, cmap='binary')  # Binary colormap (0 = black, 1 = white)
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=1)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    start, end = path[0], path[-1]
    ax.add_patch(plt.Rectangle((start[1] - 0.5, start[0] - 0.5), 1, 1, color='green', label='Start'))
    ax.add_patch(plt.Rectangle((end[1] - 0.5, end[0] - 0.5), 1, 1, color='red', label='End'))

    cursor, = ax.plot([], [], 'bo', markersize=10, label='Cursor')
    trail, = ax.plot([], [], 'cyan', linewidth=2, alpha=0.7, label='Trail')
    plt.legend()
    plt.ion()

    for i in range(len(path)):
        x = [p[0] for p in path[:i + 1]]
        y = [p[1] for p in path[:i + 1]]
        cursor.set_data(y[-1:], x[-1:])
        trail.set_data(y, x)
        plt.draw()
        plt.pause(0.3)

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    # Define the maze as a 2D numpy array
    maze = np.array([
        [1, 0, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1],
        [0, 0, 1, 1, 1],
        [1, 1, 1, 0, 1]
    ])

    # Define the start and end points
    start = (0, 0)
    end = (2, 4)

    # Create the graph representation of the maze
    G = create_graph(maze)

    # Perform DFS to find the path
    dfs_path, dfs_nodes_explored = dfs_all_paths_iterative(G, start, end, maze)

    # Check if a valid path was found and visualize
    if dfs_path:
        print("DFS Path:", dfs_path)
        print("DFS Nodes Explored:", dfs_nodes_explored)
        visualize_maze_with_cursor_no_animation(maze, dfs_path)
    else:
        print("No path found!")
