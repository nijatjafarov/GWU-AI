import unittest
import numpy as np
from io import StringIO
import sys
from unittest.mock import patch
import heapq

from main import (
    dist, is_valid_point, get_neighbors, 
    astar_search, search, main
)

class TestMazePathfinder(unittest.TestCase):
    
    def setUp(self):
        # Create a simple test maze
        self.maze = np.loadtxt("p1_maze_nopath_large_file.txt", dtype=int)
        
        # Test start and end points
        self.start = (1, 1)
        self.end = (2, 4)
        
    def test_dist_manhattan(self):
        # Same point
        self.assertEqual(dist((0, 0), (0, 0)), 0)
        
        # Adjacent points
        self.assertEqual(dist((0, 0), (0, 1)), 1)
        self.assertEqual(dist((0, 0), (1, 0)), 1)
        
        # Diagonal points
        self.assertEqual(dist((0, 0), (1, 1)), 2)
        
        # Far apart points
        self.assertEqual(dist((0, 0), (5, 5)), 10)
        self.assertEqual(dist((2, 3), (5, 7)), 7)
        
    def test_is_valid_point(self):
        # Valid points
        self.assertTrue(is_valid_point(self.maze, (1, 1)))
        self.assertTrue(is_valid_point(self.maze, (1, 8)))
        
        # Invalid points (out of bounds)
        self.assertFalse(is_valid_point(self.maze, (-1, 0)))
        self.assertFalse(is_valid_point(self.maze, (0, -1)))
        self.assertFalse(is_valid_point(self.maze, (90, 0)))
        self.assertFalse(is_valid_point(self.maze, (105, 5)))
        
        # Invalid points (walls)
        self.assertFalse(is_valid_point(self.maze, (0, 3)))  # Wall at (0,3)
        self.assertFalse(is_valid_point(self.maze, (5, 0)))  # Wall at (5,0)
        
    def test_get_neighbors(self):
        # Center point with valid neighbors
        neighbors = list(get_neighbors(self.maze, (2, 2)))
        expected_neighbors = [(1, 2), (2, 1), (2, 3)]
        self.assertEqual(sorted(neighbors), sorted(expected_neighbors))
        
    def test_astar_search_path_exists(self):
        path, cost, nodes_expanded = astar_search(
            self.maze, (1, 34), (15, 47), dist
        )
        
        self.assertIsNotNone(path)
        self.assertEqual(cost, 27)
        self.assertGreater(nodes_expanded, 0)
        
        # Verify path is valid
        for i in range(len(path) - 1):
            current = path[i]
            next_point = path[i + 1]
            # Check if points are adjacent
            self.assertEqual(dist(current, next_point), 1)
            # Check if points are valid
            self.assertTrue(is_valid_point(self.maze, current))
            self.assertTrue(is_valid_point(self.maze, next_point))
            
    def test_astar_search_no_path(self):
        path, cost, nodes_expanded = astar_search(
            self.maze, (0, 0), (2, 2), dist
        )
        
        self.assertIsNone(path)
        self.assertIsNone(cost)
        self.assertGreaterEqual(nodes_expanded, 0)
        
    def test_astar_search_same_start_end(self):
        path, cost, nodes_expanded = astar_search(
            self.maze, (0, 0), (0, 0), dist
        )
        
        self.assertEqual(path, [(0, 0)])
        self.assertEqual(cost, 0)
        self.assertEqual(nodes_expanded, 0)
        
    def test_search_invalid_points(self):
        # Invalid start
        path, cost, nodes_expanded = search(
            self.maze, (-1, 0), (0, 0), dist
        )
        self.assertIsNone(path)
        self.assertIsNone(cost)
        self.assertIsNone(nodes_expanded)
        
        # Invalid end
        path, cost, nodes_expanded = search(
            self.maze, (0, 0), (5, 5), dist
        )
        self.assertIsNone(path)
        self.assertIsNone(cost)
        self.assertIsNone(nodes_expanded)
        
        # Start on wall
        path, cost, nodes_expanded = search(
            self.maze, (0, 3), (0, 0), dist
        )
        self.assertIsNone(path)
        self.assertIsNone(cost)
        self.assertIsNone(nodes_expanded)
        
    def test_search_zero_heuristic(self):
        zero_heuristic = lambda a, b: 0
        path, cost, nodes_expanded = search(
            self.maze, (1, 1), (1, 7), zero_heuristic
        )
        
        self.assertIsNotNone(path)
        self.assertEqual(cost, 6)
        self.assertGreater(nodes_expanded, 0)
        
    def test_heuristic_comparison(self):
        # Run informed search
        _, _, informed_expanded = search(
            self.maze, (1, 2), (3, 39), dist
        )
        
        # Run uninformed search
        zero_heuristic = lambda a, b: 0
        _, _, uninformed_expanded = search(
            self.maze, (1, 2), (3, 39), zero_heuristic
        )
        
        # Informed search should expand fewer or equal nodes
        self.assertLessEqual(informed_expanded, uninformed_expanded)
        
    @patch('numpy.loadtxt')
    def test_main_with_valid_maze(self, mock_loadtxt):
        # Mock the maze loading
        mock_loadtxt.return_value = self.maze
        
        # Capture print output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Check if output contains expected strings
        self.assertIn("Test 1", output)
        self.assertIn("Informed search (A*):", output)
        self.assertIn("Uninformed search (Zero Heuristic):", output)
        
    def test_astar_search_optimal_path(self):
        
        path, cost, _ = astar_search(self.maze, (1, 1), (1, 8), dist)
        
        self.assertEqual(cost, 7)
        
        # Path should not go through walls
        for point in path:
            self.assertEqual(self.maze[point], 0)
            
    def test_astar_search_priority_queue_order(self):
        maze = np.zeros((3, 3), dtype=int)
        start = (0, 0)
        end = (2, 2)
        
        # Mock heapq.heappush to verify order
        original_heappush = heapq.heappush
        pushed_items = []
        
        def mock_heappush(pq, item):
            pushed_items.append(item)
            original_heappush(pq, item)
        
        heapq.heappush = mock_heappush
        
        try:
            astar_search(maze, start, end, dist)
            
            # Verify first item has correct format
            first_item = pushed_items[0]
            self.assertEqual(len(first_item), 3)
            self.assertIsInstance(first_item[0], (int, float))  # f score
            self.assertIsInstance(first_item[1], int)  # g score
            self.assertIsInstance(first_item[2], tuple)  # point
        finally:
            heapq.heappush = original_heappush

if __name__ == '__main__':
    unittest.main()