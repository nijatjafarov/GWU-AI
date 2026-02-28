# Dependencies
from collections import defaultdict, deque
import copy

# Get vertices, edges, and number of colors from the input file
def parse_file(path):
    edges = set()
    vertices = set()
    colors = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("colors"):
                colors = int(line.split("=")[1])
            else:
                a, b = map(int, line.split(","))
                if a != b:
                    edges.add(tuple(sorted((a, b))))
                vertices.update([a, b])
    return list(vertices), list(edges), colors


# Build an adjacency list
def build_graph(edges):
    g = defaultdict(set)
    for u, v in edges:
        g[u].add(v)
        g[v].add(u)
    return g

# Check if the value of xi is consistent with xj
def revise(domains, xi, xj):
    revised = False
    for x in set(domains[xi]):
        if all(x == y for y in domains[xj]):
            domains[xi].remove(x)
            revised = True
    return revised

# Arc Consistency Algorithm (AC-3)
def ac3(domains, graph):
    queue = deque([(x, y) for x in graph for y in graph[x]])

    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            for xk in graph[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

# Minimum Remaining Values
def select_mrv(domains, assignment, graph):
    unassigned = [v for v in domains if v not in assignment]
    return min(unassigned, key=lambda v: (len(domains[v]), -len(graph[v])))

# Least Constraining Value
def order_lcv(var, domains, graph):
    def conflicts(val):
        return sum(val in domains[n] for n in graph[var])
    return sorted(domains[var], key=conflicts)


def backtrack(assignment, domains, graph):
    if len(assignment) == len(domains):
        return assignment

    var = select_mrv(domains, assignment, graph)

    for value in order_lcv(var, domains, graph):
        local_domains = copy.deepcopy(domains)
        assignment[var] = value
        local_domains[var] = [value]

        if ac3(local_domains, graph):
            result = backtrack(assignment, local_domains, graph)
            if result:
                return result

        assignment.pop(var)

    return None

# Main function to solve CSP
def solve(path):
    vertices, edges, k = parse_file(path)
    graph = build_graph(edges)
    domains = {v: list(range(k)) for v in vertices}

    ac3(domains, graph)
    return backtrack({}, domains, graph)


if __name__ == "__main__":
    solution = solve("test3.txt")

    if solution is None:
        print("No solution found.")
    else:
        print("="*40)
        print("Solution")
        print("="*40)

        for k, v in sorted(solution.items()):
            print(f"Vertex {k}: Color {v}")
