from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

def bidirectional_bfs(graph, start, goal):
    if start == goal:
        return [start], 0

    forward_queue = deque([start])
    backward_queue = deque([goal])

    forward_visited = {start: None}
    backward_visited = {goal: None}

    forward_order = []
    backward_order = []

    def build_path():
        path = []
        node = meeting_node
        while node is not None:
            path.append(node)
            node = forward_visited[node]
        path = path[::-1]  

        node = backward_visited[meeting_node]
        while node is not None:
            path.append(node)
            node = backward_visited[node]

        return path

    meeting_node = None
    while forward_queue and backward_queue:
        # Forward BFS
        if forward_queue:
            current = forward_queue.popleft()
            forward_order.append(current)
            for neighbor, weight in graph[current]:
                if neighbor not in forward_visited:
                    forward_visited[neighbor] = current
                    forward_queue.append(neighbor)
                    if neighbor in backward_visited:  
                        meeting_node = neighbor
                        return build_path(), len(build_path()) - 1

        # Backward BFS
        if backward_queue:
            current = backward_queue.popleft()
            backward_order.append(current)
            for neighbor, weight in graph[current]:
                if neighbor not in backward_visited:
                    backward_visited[neighbor] = current
                    backward_queue.append(neighbor)
                    if neighbor in forward_visited: 
                        meeting_node = neighbor
                        return build_path(), len(build_path()) - 1

    return None, None

def visualize_graph(graph, path):
    G = nx.Graph()
    
    for node, neighbors in graph.items():
        for neighbor, weight in neighbors:
            G.add_edge(node, neighbor, weight=weight)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=500, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=2)
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color="orange", node_size=600)

    plt.title("Graph Visualization with Shortest Path")
    plt.show()

def input_graph():
    graph = {}
    print("Enter the weighted graph as adjacency list (e.g., A:B,2;C,3 means A is connected to B with weight 2 and to C with weight 3). Type 'done' when finished:")
    while True:
        line = input("Enter node and its neighbors: ").strip()
        if line.lower() == 'done':
            break
        node, neighbors = line.split(":")
        graph[node.strip()] = [(neighbor.split(",")[0].strip(), int(neighbor.split(",")[1].strip())) for neighbor in neighbors.split(";")]
    return graph

print("Input the graph:")
graph = input_graph()

start_node = input("Enter the start node: ").strip()
goal_node = input("Enter the goal node: ").strip()

path, cost = bidirectional_bfs(graph, start_node, goal_node)

if path:
    print("Shortest Path:", path)
    print("Cost (number of edges):", cost)
else:
    print("No path found.")

visualize_graph(graph, path)