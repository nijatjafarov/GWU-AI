import numpy as np
import heapq
import time

# Author: Nijat Jafarov
# Reading the matrix from the input file
try:
    maze = np.loadtxt("p1_maze_nopath_large_file.txt", dtype=int)
except Exception as e:
    print("Error loading maze:", e)
    exit(1)

#Author: Soltan Hasanov
# Heuristic - Manhattan distance
def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
    # return abs(a[0] - b[0])

# Author: Soltan Hasanov
def is_valid_point(maze, point):
    rows, cols = maze.shape
    y, x = point
    return 0 <= y < rows and 0 <= x < cols and maze[y, x] == 0

# Author: Nijat Jafarov
def get_neighbors(maze, node):
    rows, cols = maze.shape
    y, x = node

    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    for dy, dx in directions:
        ny, nx = y + dy, x + dx
        if 0 <= ny < rows and 0 <= nx < cols and maze[ny, nx] == 0:
            yield (ny, nx)

# Author: Soltan Hasanov
def astar_search(maze, start, end, dist):
    
    # Priority queue
    pq = [(dist(start, end), 0, start)]
    visited = {start: (0, None)}
    nodes_expanded = 0

    while pq:
        f, g, current = heapq.heappop(pq)

        if current == end:
            return reconstruct_path(visited, current), g, nodes_expanded

        if g > visited[current][0]:
            continue

        nodes_expanded += 1

        for neighbor in get_neighbors(maze, current):
            new_g = g + 1

            if neighbor not in visited or new_g < visited[neighbor][0]:
                visited[neighbor] = (new_g, current)
                new_f = new_g + dist(neighbor, end)
                heapq.heappush(pq, (new_f, new_g, neighbor))

    return None, None, nodes_expanded


# Author: Soltan Hasanov
# Algorithm
def search(maze, start, end, dist):
    if not is_valid_point(maze, start) or not is_valid_point(maze, end):
        return None, None, None

    return astar_search(maze, start, end, dist)


# Author: Nijat Jafarov
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current][1]
        path.append(current)
    return list(reversed(path[:-1]))

# Inputs
inputs = [
    # ((1,1), (1104, 0)),
    ((1, 34), (99, 1))
]

ITERATIONS = 100

# Author: Nijat Jafarov
def run_search(maze, start, end, heuristic):
    t0 = time.perf_counter()
    path, cost, nodes = search(maze, start, end, heuristic)
    t1 = time.perf_counter()

    return path, cost, nodes, (t1 - t0)

def benchmark_search(maze, start, end, heuristic, iterations):

    total_time = 0
    final_path = None
    final_cost = None
    final_nodes = None

    for _ in range(iterations):
        path, cost, nodes, elapsed = run_search(maze, start, end, heuristic)

        total_time += elapsed

        if path is not None:
            final_path = path
            final_cost = cost
            final_nodes = nodes

    avg_time = total_time / iterations

    return final_path, final_cost, final_nodes, avg_time


def print_results(title, path, cost, nodes, avg_time, iterations):

    print(f"\n{title}")

    if path:
        print("Distance:", cost, "| Nodes expanded:", nodes)
        print("Path summary:", path[:5], "...", path[-5:])
    else:
        print("Path not found.")

    print(f"Average execution time over {iterations} runs: {avg_time:.6f} sec")


def main():
    zero_heuristic = lambda a, b: 0

    for i, (start, end) in enumerate(inputs, start=1):

        print("========================================")
        print(f"Test {i}")
        print("Start:", start, "End:", end)

        informed = benchmark_search(maze, start, end, dist, ITERATIONS)

        uninformed = benchmark_search(maze, start, end, zero_heuristic, ITERATIONS)

        print_results("Informed search (A*):", *informed, ITERATIONS)

        print_results("Uninformed search (Zero Heuristic):", *uninformed, ITERATIONS)

main()