from rays import cast_ray
from player import Player
import math
import pygame



def is_close_to_grid(coord, cell_size, delta):
	# Calculate the distance from the coordinate to the previous grid line.
	remainder = coord % cell_size
	print(remainder)
	# Check if it's within delta of either the previous or next grid line.
	return remainder < delta or (cell_size - remainder) < delta

def is_vector_close_to_grid(point, cell_size, delta):
	# Check for both x and y coordinates.
	return is_close_to_grid(point.x, cell_size, delta) and is_close_to_grid(point.y, cell_size, delta)


def draw_view(player, grid, cell_size, max_distance, screen, width, height, path=None):
	"""
	Draws the 2D raycasted view for the player.

	:param player: Player object with pos (Vector2) and orientation (angle in radians).
	:param grid: 2D list representing the game world (1 = wall, 0 = empty space).
	:param cell_size: Size of each grid cell.
	:param max_distance: Maximum raycasting distance.
	:param screen: Pygame display surface.
	:param width: Screen width (number of rays).
	:param height: Screen height (for wall height scaling).
	"""

	angle_step = player.fov / width / 180 * math.pi
	begin_angle = player.orientation - player.fov / 2 / 180 * math.pi

	for i in range(width):
		begin_angle += angle_step
		direction = pygame.math.Vector2(math.cos(begin_angle), math.sin(begin_angle))

		# Cast the ray and get the intersection distance
		end_point = cast_ray(player.pos, direction, grid, cell_size, max_distance)
		distance = (end_point - player.pos).length()

		if distance > max_distance - 0.001:
			continue
		# Prevent fisheye effect by adjusting for angle distortion
		corrected_distance = math.fabs(distance * math.cos(begin_angle - player.orientation))

		# Calculate wall height (inverse of distance)
		if corrected_distance > 0:
			wall_height = min(height, int(height * cell_size / 2 / (corrected_distance + 0.0001)))  # Avoid division by zero
		else:
			wall_height = height

		# Draw vertical line (simple raycasting rendering)
		if not is_vector_close_to_grid(end_point, cell_size, 0.5):
			color = (0,0,0)
		else:
			color = (128,128,128)
		pygame.draw.line(screen, color, (i, height // 2 - wall_height // 2), (i, height // 2 + wall_height // 2))
		# pygame.display.flip()



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
		# print(player.pos)
		print(player.orientation)
		screen.fill((0, 0, 0))
		draw_view(player, grid, 60, 400, screen, 600, 600)
		pygame.display.flip()