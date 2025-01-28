from collections import deque

def bidirectional_bfs(graph, start, goal):
    if start == goal:
        return [start]

    forward_queue = deque([start])
    backward_queue = deque([goal])
    forward_visited = {start}
    backward_visited = {goal}
    forward_parent = {start: None}
    backward_parent = {goal: None}

    def get_path(node, forward_parent, backward_parent):
        path = []
        while node is not None:
            path.append(node)
            node = forward_parent[node]
        path = path[::-1]  
        node = backward_parent[path[-1]]
        while node is not None:
            path.append(node)
            node = backward_parent[node]
        return path

    while forward_queue and backward_queue:

        forward_current = forward_queue.popleft()
        for neighbor, weight in graph[forward_current]:
            if neighbor not in forward_visited:
                forward_visited.add(neighbor)
                forward_parent[neighbor] = forward_current
                forward_queue.append(neighbor)

                if neighbor in backward_visited:  
                    print("Order of visited nodes (forward):", forward_visited)
                    print("Order of visited nodes (backward):", backward_visited)
                    return get_path(neighbor, forward_parent, backward_parent)

        backward_current = backward_queue.popleft()
        for neighbor, weight in graph[backward_current]:
            if neighbor not in backward_visited:
                backward_visited.add(neighbor)
                backward_parent[neighbor] = backward_current
                backward_queue.append(neighbor)

                if neighbor in forward_visited:  
                    print("Order of visited nodes (forward):", forward_visited)
                    print("Order of visited nodes (backward):", backward_visited)
                    return get_path(neighbor, forward_parent, backward_parent)

    print("Order of visited nodes (forward):", forward_visited)
    print("Order of visited nodes (backward):", backward_visited)
    return None  
graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('A', 1), ('D', 2), ('E', 6)],
    'C': [('A', 4), ('F', 3)],
    'D': [('B', 2)],
    'E': [('B', 6), ('F', 2)],
    'F': [('C', 3), ('E', 2)]
}

start_node = 'A'
goal_node = 'F'
shortest_path = bidirectional_bfs(graph, start_node, goal_node)
if shortest_path:
    print("Shortest path:", shortest_path)
else:
    print("No path found.")
