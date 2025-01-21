import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import time

# Step 1: Graph Representation
def create_graph():
    city_graph = nx.Graph()
    city_graph.add_edges_from([
        (1, 2), (2, 3), (3, 4), (4, 5),
        (1, 6), (6, 7), (7, 5), (2, 7)
    ])
    return city_graph

# Step 2: Bi-directional BFS
def bidirectional_bfs(graph, start, goal):
    if start == goal:
        return [start]
    
    front_start = {start}
    front_goal = {goal}
    visited_start = {start: None}
    visited_goal = {goal: None}
    
    while front_start and front_goal:
        # Expand from the start side
        if front_start:
            new_front = set()
            for node in front_start:
                for neighbor in graph.neighbors(node):
                    if neighbor not in visited_start:
                        visited_start[neighbor] = node
                        new_front.add(neighbor)
                        if neighbor in visited_goal:
                            return construct_path(visited_start, visited_goal, neighbor)
            front_start = new_front
        
        # Expand from the goal side
        if front_goal:
            new_front = set()
            for node in front_goal:
                for neighbor in graph.neighbors(node):
                    if neighbor not in visited_goal:
                        visited_goal[neighbor] = node
                        new_front.add(neighbor)
                        if neighbor in visited_start:
                            return construct_path(visited_start, visited_goal, neighbor)
            front_goal = new_front
    
    return None

def construct_path(visited_start, visited_goal, meeting_point):
    path = []
    node = meeting_point
    while node is not None:
        path.append(node)
        node = visited_start[node]
    path.reverse()
    node = visited_goal[meeting_point]
    while node is not None:
        path.append(node)
        node = visited_goal[node]
    return path

# Step 3: Standard BFS and DFS
def bfs(graph, start, goal):
    queue = deque([start])
    visited = {start: None}
    
    while queue:
        node = queue.popleft()
        if node == goal:
            return construct_path_bfs_dfs(visited, goal)
        
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited[neighbor] = node
                queue.append(neighbor)
    return None

def dfs(graph, start, goal):
    stack = [start]
    visited = {start: None}
    
    while stack:
        node = stack.pop()
        if node == goal:
            return construct_path_bfs_dfs(visited, goal)
        
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited[neighbor] = node
                stack.append(neighbor)
    return None

def construct_path_bfs_dfs(visited, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = visited[node]
    return path[::-1]

# Step 4: Visualization
def visualize_search(graph, path, title):
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=700)
    if path:
        edges = [(path[i], path[i+1]) for i in range(len(path) - 1)]
        nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color='red', width=2)
    plt.title(title)
    plt.show()

# Step 5: Main Function to Compare Algorithms
def main():
    graph = create_graph()
    start, goal = 1, 5

    print("\nGraph Visualization:")
    nx.draw(graph, with_labels=True, node_color='lightblue', node_size=700)
    plt.show()

    # Bi-directional BFS
    start_time = time.time()
    bidirectional_path = bidirectional_bfs(graph, start, goal)
    print("Bi-directional BFS Path:", bidirectional_path)
    print("Time Taken:", time.time() - start_time)
    visualize_search(graph, bidirectional_path, "Bi-directional BFS")

    # BFS
    start_time = time.time()
    bfs_path = bfs(graph, start, goal)
    print("BFS Path:", bfs_path)
    print("Time Taken:", time.time() - start_time)
    visualize_search(graph, bfs_path, "BFS")

    # DFS
    start_time = time.time()
    dfs_path = dfs(graph, start, goal)
    print("DFS Path:", dfs_path)
    print("Time Taken:", time.time() - start_time)
    visualize_search(graph, dfs_path, "DFS")

if __name__ == "__main__": 
    main()