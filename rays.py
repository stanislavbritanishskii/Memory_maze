import math
from typing import Dict, Tuple
import pygame

def cast_ray(start, direction, grid, CELL_SIZE, max_distance):
	"""
	Casts a ray from start in the given direction until it hits an obstacle cell or reaches max_distance.
	Uses the DDA (Digital Differential Analyzer) algorithm for grid traversal.
	- start: pygame.math.Vector2, starting position.
	- direction: pygame.math.Vector2, normalized direction vector.
	- grid: 2D list representing the maze grid.
	- CELL_SIZE: Size of each cell.
	- max_distance: Maximum distance the ray can travel.
	Returns the endpoint of the ray.
	"""
	# Ensure the direction is normalized
	if direction.length() == 0:
		return start
	direction = direction.normalize()

	cell_x = int(start.x // CELL_SIZE)
	cell_y = int(start.y // CELL_SIZE)

	# Determine step direction and initial boundary distances
	if direction.x > 0:
		step_x = 1
		next_boundary_x = (cell_x + 1) * CELL_SIZE
	else:
		step_x = -1
		next_boundary_x = cell_x * CELL_SIZE
	if direction.y > 0:
		step_y = 1
		next_boundary_y = (cell_y + 1) * CELL_SIZE
	else:
		step_y = -1
		next_boundary_y = cell_y * CELL_SIZE

	# Calculate tMax and tDelta for x and y directions
	if direction.x != 0:
		tMaxX = (next_boundary_x - start.x) / direction.x
		tDeltaX = CELL_SIZE / abs(direction.x)
	else:
		tMaxX = float('inf')
		tDeltaX = float('inf')
	if direction.y != 0:
		tMaxY = (next_boundary_y - start.y) / direction.y
		tDeltaY = CELL_SIZE / abs(direction.y)
	else:
		tMaxY = float('inf')
		tDeltaY = float('inf')
	t = 0.0
	# Traverse the grid
	while t < max_distance:
		# Check if we are out of bounds
		if cell_x < 0 or cell_x >= len(grid[0]) or cell_y < 0 or cell_y >= len(grid):
			break
		# If not the starting cell and the current cell is an obstacle, stop
		if t > 0 and not grid[cell_y][cell_x]:
			break
		# Step to next cell
		if tMaxX < tMaxY:
			t = tMaxX
			cell_x += step_x
			tMaxX += tDeltaX
		else:
			t = tMaxY
			cell_y += step_y
			tMaxY += tDeltaY

	end_point = start + direction * min(t, max_distance)
	return end_point


import math


def cast_horizontal_ray(start_x, start_y, end_x, end_y, cell_size, grid, path:Dict[Tuple[int, int], Tuple[int, int, int]], delta, path_delta=0):
	"""
	Casts a horizontal ray on the floor from (start_x, start_y) to (end_x, end_y).
	Returns a list of segments, each segment is:
		[x_start, y_start, x_end, y_end, (r, g, b)]

	Colors:
		- White (255,255,255): normal segments.
		- Grey (128,128,128): segments where every point is closer than delta to a grid line.
		- Red (255,0,0): segments where every point is within delta of the center of the cell
		  (i.e. inside a circle of radius delta centered in the cell) and that cell is in the given path.

	Parameters:
		start_x, start_y: Starting coordinates.
		end_x, end_y: Ending coordinates.
		cell_size: The size of each cell.
		grid: 2D grid (not used for geometry, but kept for consistency).
		path: List of [cell_x, cell_y] indicating cells that, if hit near center, make the segment red.
		delta: The threshold distance for grid boundaries or cell centers.
	"""
	segments = []

	dx = end_x - start_x
	dy = end_y - start_y
	# Parameter t goes from 0 to 1 along the ray.
	t_breaks = set([0.0, 1.0])

	# Helper: Given a coordinate range, add t where x(t) equals k*cell_size ± delta.
	x_min = min(start_x, end_x)
	x_max = max(start_x, end_x)
	k_min = int(math.floor(x_min / cell_size)) - 1
	k_max = int(math.floor(x_max / cell_size)) + 1
	for k in range(k_min, k_max + 1):
		# x = k*cell_size + delta
		if dx != 0:
			t_val = (k * cell_size + delta - start_x) / dx
			if 0.0 <= t_val <= 1.0:
				t_breaks.add(t_val)
		# x = k*cell_size - delta
		if dx != 0:
			t_val = (k * cell_size - delta - start_x) / dx
			if 0.0 <= t_val <= 1.0:
				t_breaks.add(t_val)

	# Similarly for y: y = m*cell_size ± delta.
	y_min = min(start_y, end_y)
	y_max = max(start_y, end_y)
	m_min = int(math.floor(y_min / cell_size)) - 1
	m_max = int(math.floor(y_max / cell_size)) + 1
	for m in range(m_min, m_max + 1):
		if dy != 0:
			t_val = (m * cell_size + delta - start_y) / dy
			if 0.0 <= t_val <= 1.0:
				t_breaks.add(t_val)
		if dy != 0:
			t_val = (m * cell_size - delta - start_y) / dy
			if 0.0 <= t_val <= 1.0:
				t_breaks.add(t_val)

	# For red segments: for each cell in path, compute intersection of the ray with the circle
	# centered at the cell's center (with radius delta).
	for cell in path.keys():
		cell_y, cell_x = cell
		center_x = cell_x * cell_size + cell_size / 2.0
		center_y = cell_y * cell_size + cell_size / 2.0
		# Solve (start_x + t*dx - center_x)^2 + (start_y + t*dy - center_y)^2 = delta^2
		A = dx * dx + dy * dy
		B = 2 * (dx * (start_x - center_x) + dy * (start_y - center_y))
		C = (start_x - center_x) ** 2 + (start_y - center_y) ** 2 - path_delta * path_delta
		if A == 0:
			continue
		discriminant = B * B - 4 * A * C
		if discriminant < 0:
			continue
		sqrt_disc = math.sqrt(discriminant)
		t1 = (-B - sqrt_disc) / (2 * A)
		t2 = (-B + sqrt_disc) / (2 * A)
		for t_val in (t1, t2):
			if 0.0 <= t_val <= 1.0:
				t_breaks.add(t_val)

	# Sort all t breakpoints.
	t_breaks = sorted(t_breaks)

	# Function to classify a point along the ray.
	def classify_point(t):
		y = start_x + t * dx
		x = start_y + t * dy
		# Determine which cell we're in.
		cell_x = int(x // cell_size)
		cell_y = int(y // cell_size)
		# Red test: if the point is within delta of the cell center AND the cell is in path.
		center_x = cell_x * cell_size + cell_size / 2.0
		center_y = cell_y * cell_size + cell_size / 2.0
		if math.hypot(x - center_x, y - center_y) < path_delta:
			if path.get((cell_x, cell_y)) is not None:
				return path[(cell_x, cell_y)]
			# if [cell_x, cell_y] in path:
			# 	return "red"
		# Grey test: if the point is within delta of any grid line.
		# For vertical grid lines:
		mod_x = x - cell_x * cell_size
		dist_x = min(mod_x, cell_size - mod_x)
		# For horizontal grid lines:
		mod_y = y - cell_y * cell_size
		dist_y = min(mod_y, cell_size - mod_y)
		if dist_x < delta or dist_y < delta:
			return (128,128,128)
		return (255,255,255)

	# Now, iterate over each consecutive interval in t.
	for i in range(len(t_breaks) - 1):
		t0 = t_breaks[i]
		t1 = t_breaks[i + 1]
		# Sample a midpoint; because our breakpoints are chosen to be the only transitions,
		# the property is constant over [t0, t1].
		t_mid = (t0 + t1) / 2.0
		color = classify_point(t_mid)
		# if prop == "red":
		# 	color = (255, 0, 0)
		# elif prop == "grey":
		# 	color = (128, 128, 128)
		# else:
		# 	color = (255, 255, 255)

		seg_start_x = start_x + t0 * dx
		seg_start_y = start_y + t0 * dy
		seg_end_x = start_x + t1 * dx
		seg_end_y = start_y + t1 * dy
		segments.append([seg_start_x, seg_start_y, seg_end_x, seg_end_y, color])

	return segments


def draw_polygon_from_rays(player, grid, cell_size, max_distance, screen, angle_step=1):
	"""
	Casts rays from the player's position in all directions, collects the endpoints,
	and creates a "hole" in an opaque black overlay using the polygon defined by these endpoints.
	The polygon area will be fully transparent, while the rest of the screen appears black.
	- player: The Player object.
	- grid: The maze grid.
	- cell_size: Size of each grid cell.
	- max_distance: Maximum distance for rays (in pixels).
	- screen: The Pygame surface to draw on.
	- angle_step: Angle step in degrees between consecutive rays.
	"""
	endpoints = []
	for angle in range(0, 360, angle_step):
		rad = math.radians(angle)
		direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
		end_point = cast_ray(player.pos, direction, grid, cell_size, max_distance)
		endpoints.append((int(end_point.x), int(end_point.y)))
	# Create an overlay surface with per-pixel alpha
	overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
	# Fill the overlay completely with opaque black
	overlay.fill((0, 0, 0, 255))
	# Draw the polygon with a fully transparent color to "cut out" the area
	pygame.draw.polygon(overlay, (0, 0, 0, 0), endpoints)
	# Blit the overlay onto the screen; the polygon area will be transparent, revealing what's underneath
	screen.blit(overlay, (0, 0))