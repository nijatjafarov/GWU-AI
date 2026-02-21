import unittest
import tempfile
import os
from collections import defaultdict
from main import (parse_file, build_graph, 
                  revise, ac3, select_mrv, 
                  order_lcv, solve)

class TestGraphColoringSolver(unittest.TestCase):
    
    def setUp(self):
        self.test_files = []

    # Clean up any created test files after all tests are done
    def tearDown(self):
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def create_test_file(self, content):
        fd, path = tempfile.mkstemp(text=True)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        self.test_files.append(path)
        return path
    
    # Tests for parse_file function
    def test_parse_file_basic(self):
        content = """colors=3\n1,2\n2,3\n3,1"""
        path = self.create_test_file(content)
        vertices, edges, colors = parse_file(path)
        
        self.assertEqual(sorted(vertices), [1, 2, 3])
        self.assertEqual(set(edges), {(1, 2), (2, 3), (1, 3)})
        self.assertEqual(colors, 3)
    
    def test_parse_file_with_comments(self):
        content = """# This is a comment\ncolors=4\n# Another comment\n1,2\n2,3\n3,4\n4,1"""

        path = self.create_test_file(content)
        vertices, edges, colors = parse_file(path)
        
        self.assertEqual(sorted(vertices), [1, 2, 3, 4])
        self.assertEqual(set(edges), {(1, 2), (2, 3), (3, 4), (1, 4)})
        self.assertEqual(colors, 4)
    
    def test_parse_file_ignore_self_loops(self):
        content = """colors=2\n1,1\n1,2\n2,2"""

        path = self.create_test_file(content)
        vertices, edges, colors = parse_file(path)
        
        self.assertEqual(sorted(vertices), [1, 2])
        self.assertEqual(set(edges), {(1, 2)})
        self.assertEqual(colors, 2)
    
    def test_parse_file_duplicate_edges(self):
        content = """colors=3\n1,2\n2,1\n1,3"""

        path = self.create_test_file(content)
        vertices, edges, colors = parse_file(path)
        
        self.assertEqual(sorted(vertices), [1, 2, 3])
        self.assertEqual(set(edges), {(1, 2), (1, 3)})
        self.assertEqual(colors, 3)
    
    # Tests for build_graph function
    def test_build_graph_empty(self):
        edges = []
        graph = build_graph(edges)
        self.assertEqual(graph, defaultdict(set))
    
    def test_build_graph_basic(self):
        edges = [(1, 2), (2, 3), (1, 3)]
        graph = build_graph(edges)
        
        self.assertEqual(graph[1], {2, 3})
        self.assertEqual(graph[2], {1, 3})
        self.assertEqual(graph[3], {1, 2})
    
    def test_revise_no_revision(self):
        domains = {1: [0, 1, 2], 2: [0, 1, 2]}
        revised = revise(domains, 1, 2)
        
        self.assertFalse(revised)
        self.assertEqual(domains[1], [0, 1, 2])
    
    def test_revise_with_revision(self):
        domains = {1: [0, 1], 2: [0]}
        revised = revise(domains, 1, 2)
        
        self.assertTrue(revised)
        self.assertEqual(domains[1], [1])
    
    def test_revise_all_removed(self):
        domains = {1: [0], 2: [0]}
        revised = revise(domains, 1, 2)
        
        self.assertTrue(revised)
        self.assertEqual(domains[1], [])
    
    # Tests for ac3 function
    def test_ac3_consistent(self):
        domains = {1: [0, 1], 2: [0, 1], 3: [0, 1]}
        graph = {1: {2, 3}, 2: {1, 3}, 3: {1, 2}}
        
        result = ac3(domains, graph)
        self.assertTrue(result)
    
    def test_ac3_inconsistent(self):
        domains = {1: [0], 2: [0], 3: [1, 2]}
        graph = {1: {2, 3}, 2: {1, 3}, 3: {1, 2}}
        
        result = ac3(domains, graph)
        self.assertFalse(result)
    
    def test_ac3_reduces_domains(self):
        domains = {1: [0, 1], 2: [0], 3: [1]}
        graph = {1: {2, 3}, 2: {1}, 3: {1}}
        
        ac3(domains, graph)
        self.assertEqual(domains[1], [])
    
    # Tests for select_mrv function
    def test_select_mrv_basic(self):
        domains = {1: [0], 2: [0, 1], 3: [0, 1, 2]}
        assignment = {}
        graph = {1: {2}, 2: {1, 3}, 3: {2}}
        
        var = select_mrv(domains, assignment, graph)
        self.assertEqual(var, 1)
    
    def test_select_mrv_tie_break(self):
        domains = {1: [0, 1], 2: [0, 1], 3: [0, 1, 2]}
        assignment = {}
        graph = {1: {2, 3}, 2: {1}, 3: {1}}
        
        var = select_mrv(domains, assignment, graph)
        self.assertEqual(var, 1)
    
    def test_select_mrv_unassigned_only(self):
        domains = {1: [0], 2: [0, 1], 3: [0, 1, 2]}
        assignment = {1: 0}
        graph = {1: {2}, 2: {1, 3}, 3: {2}}
        
        var = select_mrv(domains, assignment, graph)
        self.assertEqual(var, 2)
    
    # Tests for order_lcv function
    def test_order_lcv_basic(self):
        domains = {1: [0, 1], 2: [0, 1], 3: [1]}
        graph = {1: {2, 3}, 2: {1}, 3: {1}}
        
        ordered = order_lcv(1, domains, graph)
        self.assertEqual(ordered, [0, 1])
    
    # Tests for solve function
    def test_solve_trivial(self):
        content = """colors=2\n1,2"""
        path = self.create_test_file(content)
        solution = solve(path)
        
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution), 2)
        self.assertNotEqual(solution[1], solution[2])
    
    def test_solve_2colorable_graph(self):
        content = """colors=2\n1,2\n2,3\n3,4\n4,1"""

        path = self.create_test_file(content)
        solution = solve(path)
        
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution), 4)
        self.assertNotEqual(solution[1], solution[2])
        self.assertNotEqual(solution[2], solution[3])
        self.assertNotEqual(solution[3], solution[4])
        self.assertNotEqual(solution[4], solution[1])
    
    def test_solve_3colorable_graph(self):
        content = """colors=3\n1,2\n2,3\n3,1\n3,4\n4,5\n5,3"""

        path = self.create_test_file(content)
        solution = solve(path)
        
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution), 5)
        for u, v in [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 3)]:
            self.assertNotEqual(solution[u], solution[v])
    
    def test_solve_unsolvable(self):
        content = """colors=2\n1,2\n2,3\n3,1"""

        path = self.create_test_file(content)
        solution = solve(path)
        
        self.assertIsNone(solution)
    
    def test_solve_complete_graph(self):
        content = """colors=4\n1,2\n1,3\n1,4\n2,3\n2,4\n3,4"""

        path = self.create_test_file(content)
        solution = solve(path)
        
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution), 4)
        colors = list(solution.values())
        self.assertEqual(len(set(colors)), 4)
    
    def test_solve_large_graph(self):
        content = """colors=3\n1,2\n1,3\n2,3\n2,4\n3,4\n4,5\n5,6\n6,4"""

        path = self.create_test_file(content)
        solution = solve(path)
        
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution), 6)
        
        edges = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5), (5, 6), (6, 4)]
        for u, v in edges:
            self.assertNotEqual(solution[u], solution[v],
                               f"Vertices {u} and {v} have same color {solution[u]}")
if __name__ == "__main__":
    unittest.main()