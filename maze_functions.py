import random
import pygame


def generate_maze(width, height, round_walk: 20):
	"""
	Generates a maze in-place on the given grid using DFS-based recursive backtracking.

	The grid is assumed to be a 2D list of booleans with all cells initially True (empty).
	After running this function, passages are marked as True and walls as False.

	Note: For a proper maze, grid dimensions should be odd numbers.
	"""

	grid = [[False] * width for _ in range(height)]
	# for i in range(1, height - 1):
	# 	for j in range(1, width - 1):
	# 		grid[i][j] = True
	# return grid
	# Choose a starting cell; typically (1,1) works for grids at least 3x3.
	start_i, start_j = 1, 1
	grid[start_i][start_j] = True

	# Use a stack for DFS: each element is a tuple (i, j)
	stack = [(start_i, start_j)]

	# Define movement directions: up, down, left, right.
	# We move two cells at a time because the cell in-between will be removed (carved out) as a passage.
	directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

	while stack:
		current_i, current_j = stack[-1]
		neighbors = []

		# Check all four directions for potential neighbors
		for di, dj in directions:
			ni, nj = current_i + di, current_j + dj
			# Ensure neighbor is within bounds and not yet carved (still a wall)
			if 0 <= ni < height - 1 and 0 <= nj < width - 1 and (
					grid[ni][nj] == False or not random.randint(0, round_walk)):
				neighbors.append((di, dj))

		if neighbors:
			# Randomly choose one of the valid directions
			di, dj = random.choice(neighbors)
			ni, nj = current_i + di, current_j + dj

			# Remove the wall between the current cell and the chosen neighbor.
			# The cell in between is at (current_i + di//2, current_j + dj//2).
			wall_i = current_i + di // 2
			wall_j = current_j + dj // 2
			grid[wall_i][wall_j] = True

			# Mark the neighbor as a passage.
			grid[ni][nj] = True

			# Move to the neighbor cell.
			stack.append((ni, nj))
		else:
			# Backtrack if there are no unvisited neighbors.
			stack.pop()

	grid[0] = [False] * width
	grid[height - 1] = [False] * height
	for i in range(width):
		grid[i][height - 1] = False
		grid[i][0] = False
	return grid


from collections import deque

from collections import deque
import pygame


def bfs_furthest(x, y, grid, path_color=(0,0,0)):
	"""
	Finds and returns the furthest cell reachable from the starting cell (x, y) using BFS,
	along with the shortest path from (x, y) to that furthest cell.

	Parameters:
		x (int): The starting row index.
		y (int): The starting column index.
		grid (list[list[bool]]): A 2D grid where accessible cells are True and walls are False.
			(Note: Updated grid definition to match the code logic.)

	Returns:
		tuple: A tuple (furthest_cell, path) where:
			- furthest_cell is a pygame.math.Vector2 containing the coordinates of the furthest cell.
			- path is a list of (row, column) tuples representing the shortest path from (x, y)
			  to the furthest cell (including both endpoints).
		Returns None if the starting cell is not accessible.
	"""
	# Check if the starting cell is accessible (True). If not, return None.
	if not grid[x][y]:
		return None

	visited = set()
	visited.add((x, y))

	# Dictionary for path reconstruction: maps each cell to its predecessor.
	prev = {}
	prev[(x, y)] = None

	# Initialize the queue with (row, column, distance)
	q = deque()
	q.append((x, y, 0))

	# Track the furthest cell and its distance
	furthest_cell = (x, y)
	max_distance = 0

	# Define movements: up, down, left, right.
	directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

	while q:
		cx, cy, dist = q.popleft()

		# Update furthest cell if a larger distance is found.
		if dist > max_distance:
			max_distance = dist
			furthest_cell = (cx, cy)

		# Explore all four neighbors.
		for dx, dy in directions:
			nx, ny = cx + dx, cy + dy
			# Check if within grid bounds.
			if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
				# Continue only if the cell is accessible and not visited.
				if (nx, ny) not in visited and grid[nx][ny]:
					visited.add((nx, ny))
					prev[(nx, ny)] = (cx, cy)
					q.append((nx, ny, dist + 1))

	# Reconstruct the shortest path from (x, y) to the furthest cell.
	path = {}
	cell = furthest_cell
	while cell is not None:
		path[cell] = path_color
		cell = prev[cell]
	# path.reverse()

	return pygame.math.Vector2(furthest_cell[0], furthest_cell[1]), path
