import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import networkx as nx
from DFS_maze_slover import DFS_iterative

def create_graph(maze):
    """
    Convert a maze into a graph where each walkable cell is a node,
    and edges connect adjacent walkable cells.
    """
    G = nx.Graph()
    rows, cols = maze.shape

    for r in range(rows):
        for c in range(cols):
            if maze[r, c] == 1:  # Walkable path
                # Add edges to adjacent walkable cells
                if r > 0 and maze[r-1, c] == 1:  # Up
                    G.add_edge((r, c), (r-1, c))
                if r < rows - 1 and maze[r+1, c] == 1:  # Down
                    G.add_edge((r, c), (r+1, c))
                if c > 0 and maze[r, c-1] == 1:  # Left
                    G.add_edge((r, c), (r, c-1))
                if c < cols - 1 and maze[r, c+1] == 1:  # Right
                    G.add_edge((r, c), (r, c+1))

    return G

def bfs_shortest_path(G, start, end):
    """
    Perform BFS on the graph to find the shortest path from start to end.
    Returns the path and the number of nodes explored.
    """
    queue = deque([start])
    visited = {start: None}  # Track visited nodes and their parents
    nodes_explored = 0

    while queue:
        current = queue.popleft()
        nodes_explored += 1

        if current == end:
            # Reconstruct path from start to end
            path = []
            while current is not None:
                path.append(current)
                current = visited[current]
            return path[::-1], nodes_explored  # Return reversed path and nodes explored

        for neighbor in G.neighbors(current):
            if neighbor not in visited:
                visited[neighbor] = current
                queue.append(neighbor)

    return None, nodes_explored  # No path found

def visualize_maze_with_cursor_no_animation(maze, path):
    """
    Visualize the maze and the movement along the BFS path step-by-step.
    """
    rows, cols = maze.shape
    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw maze grid
    ax.imshow(maze, cmap='binary')
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='blue', linestyle='-', linewidth=1)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Highlight the start and end points
    start, end = path[0], path[-1]
    ax.add_patch(plt.Rectangle((start[1] - 0.5, start[0] - 0.5), 1, 1, color='green', label='Start'))
    ax.add_patch(plt.Rectangle((end[1] - 0.5, end[0] - 0.5), 1, 1, color='red', label='End'))

    # Cursor and trail setup
    cursor, = ax.plot([], [], 'bo', markersize=10, label='Cursor')
    trail, = ax.plot([], [], 'cyan', linewidth=2, alpha=0.7, label='Trail')
    plt.legend()
    plt.ion()  # Enable interactive mode

    # Animate path step-by-step
    for i in range(len(path)):
        x = [p[0] for p in path[:i + 1]]
        y = [p[1] for p in path[:i + 1]]

        cursor.set_data(y[-1:], x[-1:])  # Update cursor position
        trail.set_data(y, x)  # Update trail

        plt.draw()
        plt.pause(0.3)  # Pause to create animation effect

    plt.ioff()  # Disable interactive mode
    plt.show()

def compare_bfs_and_dfs(maze, start, end):
    # Create graph
    G = create_graph(maze)

    # BFS
    bfs_path, bfs_nodes_explored = bfs_shortest_path(G, start, end)
    # Display Results
    print("=== BFS Results ===")
    print(f"Path: {bfs_path}")
    print(f"Nodes Explored: {bfs_nodes_explored}")

    # DFS
    dfs_path, dfs_nodes_explored = DFS_iterative(G, start, end, maze)
    print("\n=== DFS Results ===")
    print(f"Path: {dfs_path}")
    print(f"Nodes Explored: {dfs_nodes_explored}")

if __name__ == "__main__":
    # Define a maze (0 = wall, 1 = path)
    maze = np.array([
        [1, 0, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1],
        [0, 0, 1, 1, 1],
        [1, 1, 1, 0, 1]
    ])
    
    start = (0, 0)
    end = (2, 4)    # Ending cell

    # Create graph from the maze
    G = create_graph(maze)

    # Find shortest path using BFS
    bfs_path, bfs_nodes_explored = bfs_shortest_path(G, start, end)

    if bfs_path:
        print("BFS Path:", bfs_path)
        print("BFS Nodes Explored:", bfs_nodes_explored)

        # Visualize the maze with cursor movement
        visualize_maze_with_cursor_no_animation(maze, bfs_path)
    else:
        print("No path found!")
    compare_bfs_and_dfs(maze, start, end)
