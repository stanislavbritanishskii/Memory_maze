import math
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