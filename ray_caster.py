from rays import cast_ray, cast_horizontal_ray
from typing import Dict, Tuple
from player import Player
import math
import pygame


def is_close_to_grid(coord, cell_size, delta):
	# Calculate the distance from the coordinate to the previous grid line.
	remainder = coord % cell_size
	# Check if it's within delta of either the previous or next grid line.
	return remainder < delta or (cell_size - remainder) < delta


def is_vector_close_to_grid(point, cell_size, delta):
	# Check for both x and y coordinates.
	return is_close_to_grid(point.x, cell_size, delta) and is_close_to_grid(point.y, cell_size, delta)

def normalize_angle(angle):
	while angle > math.pi:
		angle -= 2 * math.pi
	while angle < -math.pi:
		angle += 2 * math.pi
	return angle


def draw_view(player, grid, cell_size, max_distance, screen, width, height, path:Dict[Tuple[int, int], Tuple[int, int, int]]=None, path_point_size = 10):
	"""
	Draws the 2D raycasted view for the player.

	First, walls are drawn using vertical rays as before.
	Then, the floor is drawn by iterating over horizontal screen rows (from the horizon down)
	and, for each row, computing a horizontal floor ray from leftmost to rightmost points.

	For a given floor row (y on screen):
		- The distance from the player is computed via similar triangles:
			row_distance = (cell_size * height) / (2 * (y - horizon))
		- The leftmost world point is calculated from an angle of (player.orientation - fov/2),
		  and the rightmost from (player.orientation + fov/2).
		- The floor ray from left_point to right_point is subdivided using cast_horizontal_ray.
		- Each segment is then mapped linearly to screen x coordinates.
	"""
	# --- FLOOR DRAWING (horizontal rays) ---
	horizon = height // 2
	# Left and right boundary angles (in radians) for the floor.
	left_angle = player.orientation - (player.fov / 2) / 180 * math.pi
	right_angle = player.orientation + (player.fov / 2) / 180 * math.pi

	# For each horizontal screen row from the horizon down...
	for y in range(horizon + 1, height):

		# Avoid division by zero; the further from the horizon, the farther the floor.
		if (y - horizon) == 0:
			continue
		# Compute floor distance using similar triangles.
		row_distance = (cell_size / 2 * height) / (2.0 * (y - horizon)) / math.cos(player.fov / 2 / 180 * math.pi)
		if row_distance > max_distance:
			continue
		# Compute world coordinates for the leftmost and rightmost points on this row.
		left_point = player.pos + pygame.math.Vector2(math.cos(left_angle), math.sin(left_angle)) * row_distance
		right_point = player.pos + pygame.math.Vector2(math.cos(right_angle), math.sin(right_angle)) * row_distance

		# Use cast_horizontal_ray to subdivide the floor ray from left_point to right_point.
		floor_segments = cast_horizontal_ray(
			left_point.x, left_point.y,
			right_point.x, right_point.y,
			cell_size,
			grid,
			path if path is not None else [],
			1,
			path_point_size
		)

		# The total horizontal vector and its length for mapping to screen space.
		total_vector = right_point - left_point
		total_length = total_vector.length()
		if total_length == 0:
			continue

		for seg in floor_segments:
			seg_start_x, seg_start_y, seg_end_x, seg_end_y, seg_color = seg

			# Create vectors for the segment endpoints.
			seg_start = pygame.math.Vector2(seg_start_x, seg_start_y)
			seg_end = pygame.math.Vector2(seg_end_x, seg_end_y)

			# Calculate the angles from the player to the segment endpoints.
			angle_start = math.atan2(seg_start.y - player.pos.y, seg_start.x - player.pos.x)
			angle_end = math.atan2(seg_end.y - player.pos.y, seg_end.x - player.pos.x)



			# Normalize angles relative to left_bound.
			t_start = (normalize_angle(angle_start - left_angle)) / (player.fov / 180 * math.pi)
			t_end = (normalize_angle(angle_end - left_angle)) / (player.fov / 180 * math.pi)

			# Clamp the values between 0 and 1.
			t_start = max(0.0, min(1.0, t_start))
			t_end = max(0.0, min(1.0, t_end))

			# Map to screen x coordinates.
			screen_x0 = int(t_start * width)
			screen_x1 = int(t_end * width)

			pygame.draw.line(screen, seg_color, (screen_x0, y), (screen_x1, y))


	# --- WALL DRAWING (vertical rays) ---
	angle_step = player.fov / width / 180 * math.pi
	current_angle = player.orientation - (player.fov / 2) / 180 * math.pi

	for i in range(width):
		current_angle += angle_step
		direction = pygame.math.Vector2(math.cos(current_angle), math.sin(current_angle))
		# Cast ray from player to wall.
		end_point = cast_ray(player.pos, direction, grid, cell_size, max_distance)
		distance = (end_point - player.pos).length()
		if distance > max_distance - 0.001:
			continue
		# Correct distance to avoid fisheye distortion.
		corrected_distance = abs(distance * math.cos(current_angle - player.orientation))
		if corrected_distance > 0:
			wall_height = min(height, int(height * cell_size / 2 / (corrected_distance + 0.0001)))
		else:
			wall_height = height
		# Determine wall color based on grid proximity.
		if not is_vector_close_to_grid(end_point, cell_size, 0.5):
			color = (0, 0, 0)
		else:
			color = (128, 128, 128)
		pygame.draw.line(screen, color, (i, height // 2 - wall_height // 2), (i, height // 2 + wall_height // 2))



if __name__ == "__main__":
	pygame.init()
	screen = pygame.display.set_mode((600, 600))
	player = Player(pygame.math.Vector2(200, 200), 10, 200)
	grid = []
	for i in range(10):
		grid.append([True] * 10)
	grid[0] = [False] * 10
	grid[-1] = [False] * 10
	for i in range(10):
		grid[i][0] = False
		grid[i][-1] = False
		print(grid[i])

	while True:
		player.orientation += 0.01
		if player.orientation > math.pi:
			player.orientation -= 2 * math.pi
		print(player.orientation)
		screen.fill((0, 0, 0))
		draw_view(player, grid, 60, 400, screen, 600, 600)
		pygame.display.flip()
