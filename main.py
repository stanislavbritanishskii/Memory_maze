import pygame
import sys
import math
from maze_functions import *
from rays import *
from player import *
from collections import deque
from ray_caster import draw_view

WINDOW_SIZE = 1000
WINDOW_TITLE = "Memory Maze"
FPS = 60

# Global configuration variables (modifiable in the start screen)
config_grid_size = 5
config_time_to_start = 1.0  # in seconds
config_show_best_route = True
config_view_distance = 5
path_taken_color=(255, 0,0)
best_path_color = (0,0,255)
end_point_color = (0,255,0)
start_point_color = (255,0,0)


# These will be updated when simulation starts
GRID_SIZE = config_grid_size
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
PLAYER_SPEED = CELL_SIZE * 5  # pixels per second
PATH_SIZE = CELL_SIZE /6
THREE_D = True

def draw_grid(grid, screen, furthest: pygame.math.Vector2 = None, start: pygame.math.Vector2 = None):
	"""
	Draws the grid on the provided Pygame screen.
	- grid: A square 2D list of booleans.
	  True  => black cell (obstacle)
	  False => white cell (free)
	- screen: The Pygame surface to draw on.
	"""
	n = len(grid)
	cell_size = WINDOW_SIZE // n
	for row in range(n):
		for col in range(n):
			color = (0, 0, 0) if not grid[row][col] else (255, 255, 255)
			if furthest is not None and furthest.x == row and furthest.y == col:
				color = (0, 255, 0)
			if start is not None and start.x == col and start.y == row:
				color = (255, 0, 0)
			rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
			pygame.draw.rect(screen, color, rect)
			pygame.draw.rect(screen, (128, 128, 128), rect, 1)


def draw_path(path, screen, color=(0, 0, 255)):
	for p in path.keys():
		pygame.draw.circle(screen, path[p],
			(p[1] * CELL_SIZE + CELL_SIZE / 2, p[0] * CELL_SIZE + CELL_SIZE / 2),
			PATH_SIZE)


def start_simulation(grid_size):
	global GRID_SIZE, CELL_SIZE, PLAYER_SPEED
	GRID_SIZE = grid_size
	CELL_SIZE = WINDOW_SIZE // GRID_SIZE
	PLAYER_SPEED = CELL_SIZE * 7
	grid = generate_maze(GRID_SIZE, GRID_SIZE, 15)

	player_start = None
	for row in range(GRID_SIZE):
		for col in range(GRID_SIZE):
			if grid[row][col]:  # white cell is free
				player_start = pygame.math.Vector2((col + 0.5) * CELL_SIZE, (row + 0.5) * CELL_SIZE)
				break
		if player_start:
			break
	if player_start is None:
		player_start = pygame.math.Vector2(WINDOW_SIZE / 2, WINDOW_SIZE / 2)
	furthest, path = bfs_furthest(int(player_start.y / CELL_SIZE), int(player_start.x / CELL_SIZE), grid, best_path_color)

	player_radius = CELL_SIZE * 0.3
	player = Player(player_start, player_radius, PLAYER_SPEED)
	player_start_cell = player_start / CELL_SIZE
	player_start_cell.x = int(player_start_cell.x)
	player_start_cell.y = int(player_start_cell.y)
	path_taken = {(int(player_start_cell.y), int(player_start_cell.x)): path_taken_color,
				  (int(furthest.x), int(furthest.y)): end_point_color}
	return grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED


def draw_start_screen(screen, font):
	# Create a semi-transparent overlay
	overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
	overlay.set_alpha(200)
	overlay.fill((0, 0, 0))
	screen.blit(overlay, (0, 0))

	text_lines = [
		"START SCREEN - CONFIGURATION",
		"Adjust the following parameters:",
		"Grid Size: {} (UP/DOWN keys)".format(config_grid_size),
		"Time to Start (seconds): {:.2f} (RIGHT/LEFT keys)".format(config_time_to_start),
		"View Distance (tiles): {:.0f} (-/= keys)".format(config_view_distance),
		"Show Best Route: {} (Press B to toggle)".format("[X]" if config_show_best_route else "[ ]"),
		"3D mode: {} (Press D to toggle)".format("[X]" if THREE_D else "[ ]"),
		"Press ENTER to start simulation"
	]

	for i, line in enumerate(text_lines):
		text_surface = font.render(line, True, (255, 255, 255))
		screen.blit(text_surface,
		            (WINDOW_SIZE // 2 - text_surface.get_width() // 2, 100 + i * 40))


def draw_end_screen(screen, font, best_length, taken_length, percent_diff):
	# Create a semi-transparent overlay
	overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
	overlay.set_alpha(200)
	overlay.fill((0, 0, 0))
	screen.blit(overlay, (0, 0))

	text_lines = [
		"LEVEL COMPLETE!",
		"Best Path Length: {}".format(best_length),
		"Your Path Length: {}".format(taken_length),
		"Extra Steps: {:.2f}%".format(percent_diff),
		"Press ENTER to return to Start Screen"
	]

	for i, line in enumerate(text_lines):
		text_surface = font.render(line, True, (255, 255, 255))
		screen.blit(text_surface,
		            (WINDOW_SIZE // 2 - text_surface.get_width() // 2, 100 + i * 40))


def set_window_size():
	global WINDOW_SIZE
	temp_screen = pygame.display.set_mode((100, 100), pygame.RESIZABLE)
	pygame.display.set_caption("Temporary Window")  # Helps in getting title bar height
	temp_screen.fill((0, 0, 0))
	pygame.display.update()

	# Get the real window height including title bar
	window_rect = temp_screen.get_rect()
	pygame.event.pump()  # Process events to update the window
	title_bar_height = window_rect.top

	# Adjust square size to fit within the available screen space
	WINDOW_SIZE -= title_bar_height

	# Close temp window
	pygame.display.quit()

def main():
	global config_grid_size, config_time_to_start, config_show_best_route, PLAYER_SPEED, config_view_distance, WINDOW_SIZE, THREE_D, PATH_SIZE
	pygame.init()

	set_window_size()

	screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
	pygame.display.set_caption(WINDOW_TITLE)
	pygame.mouse.set_visible(False)
	clock = pygame.time.Clock()
	font = pygame.font.SysFont(None, 30)

	# State variables
	in_start_screen = True  # Configuration mode active initially
	active = False         # Simulation is active after countdown
	end_screen = False     # End screen is active upon reaching furthest cell
	elapsed_time = 0.0     # Elapsed simulation time (after countdown)
	simulation_start_time = 0

	# Generate initial maze using default configuration
	grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED = start_simulation(config_grid_size)

	while True:
		dt = clock.tick(FPS) / 1000.0

		# Event processing
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN and  event.key == pygame.K_ESCAPE:
				pygame.quit()
			if in_start_screen:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						config_grid_size += 2
						grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED = start_simulation(config_grid_size)
						PLAYER_SPEED = CELL_SIZE * 5
						PATH_SIZE = CELL_SIZE / 4
					elif event.key == pygame.K_DOWN:
						if config_grid_size > 5:
							config_grid_size -= 2
							grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED = start_simulation(config_grid_size)
							PLAYER_SPEED = CELL_SIZE * 5
							PATH_SIZE = CELL_SIZE / 4
					elif event.key == pygame.K_RIGHT:
						config_time_to_start += 1.0
					elif event.key == pygame.K_MINUS:
						if config_view_distance > 1:
							config_view_distance -= 1.0
					elif event.key == pygame.K_EQUALS:
						config_view_distance += 1.0
					elif event.key == pygame.K_LEFT:
						if config_time_to_start > 1.0:
							config_time_to_start -= 1.0
					elif event.key == pygame.K_b:
						config_show_best_route = not config_show_best_route
					elif event.key == pygame.K_d:
						THREE_D = not THREE_D
					elif event.key == pygame.K_RETURN:
						# End configuration mode and begin simulation (countdown starts)
						grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED = start_simulation(config_grid_size)
						in_start_screen = False
						active = False
						end_screen = False
						simulation_start_time = pygame.time.get_ticks()
						elapsed_time = 0.0

			else:
				# If in end screen, allow pressing ENTER to return to configuration
				if end_screen:
					if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
						in_start_screen = True
						end_screen = False
						simulation_start_time = pygame.time.get_ticks()
						elapsed_time = 0.0
						grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED = start_simulation(config_grid_size)

				else:
					# Simulation mode (non-end screen) event processing
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_r:
							# Restart simulation and go back to configuration
							in_start_screen = True
							active = False
							simulation_start_time = pygame.time.get_ticks()
							elapsed_time = 0.0
							grid, player, furthest, player_start_cell, path, path_taken, PLAYER_SPEED = start_simulation(config_grid_size)
						elif event.key == pygame.K_ESCAPE:
							pygame.quit()
					elif event.type == pygame.MOUSEMOTION and active:
						# event.rel gives the relative movement (dx, dy)
						dx, dy = event.rel
						if dx < 0:
							player.orientation -= 0.03
						if dx > 0:
							player.orientation += 0.03
						pygame.mouse.set_pos(WINDOW_SIZE // 2, WINDOW_SIZE // 2)

		# In configuration mode, freeze countdown by resetting simulation_start_time
		if in_start_screen:
			simulation_start_time = pygame.time.get_ticks()

		# Update simulation if not in start screen and not in end screen
		if not in_start_screen and not end_screen:
			# Countdown phase (simulation not yet active)
			if not active and pygame.time.get_ticks() - simulation_start_time > config_time_to_start * 1000:
				active = True
				elapsed_time = 0.0

			# Simulation active: process movement and update player's path
			if active:
				keys = pygame.key.get_pressed()
				movement = pygame.math.Vector2(0, 0)
				if keys[pygame.K_w] or keys[pygame.K_UP]:
					movement.y -= 1
				if keys[pygame.K_s] or keys[pygame.K_DOWN]:
					movement.y += 1

				if keys[pygame.K_e]:
					player.orientation += 0.1
				if keys[pygame.K_q]:
					player.orientation -= 0.1
				player.normalize_orientation()
				print(player.orientation)
				if keys[pygame.K_a] or keys[pygame.K_LEFT]:
					movement.x -= 1
				if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
					movement.x += 1
				if THREE_D:
					player.move_3d(movement, grid, CELL_SIZE, dt)
				else:
					player.move(movement, grid, CELL_SIZE, dt)

				# Update path taken if the player moves to a new cell
				current_cell = (int(player.pos.y / CELL_SIZE), int(player.pos.x / CELL_SIZE))
				if current_cell not in path_taken.keys():
					path_taken[current_cell] = path_taken_color

				# Check if the player has reached the furthest cell
				if (int(player.pos.y / CELL_SIZE) == int(furthest.x) and
				    int(player.pos.x / CELL_SIZE) == int(furthest.y)):
					player.pos.y = furthest.x * CELL_SIZE + CELL_SIZE / 2
					player.pos.x = furthest.y * CELL_SIZE + CELL_SIZE / 2
					end_screen = True
					active = False

			# Update elapsed simulation time (only when simulation is active)
			if active:
				elapsed_time += dt

		# Drawing section

		if not THREE_D:
			screen.fill((0, 0, 0))
		else:
			screen.fill((255, 255, 255))
		if not active or active and not THREE_D:
			draw_grid(grid, screen, furthest, player_start_cell)

		# Always draw the best and taken paths on the map
		if config_show_best_route and not active or end_screen:
			draw_path(path, screen)
		if not active or active and not THREE_D:
			draw_path(path_taken, screen, (128, 0, 0))

		if in_start_screen:
			# Draw the configuration overlay (start screen)
			draw_start_screen(screen, font)
		elif end_screen:
			# Compute statistics for the end screen
			best_length = len(path)
			taken_length = len(path_taken)
			percent_diff = ((taken_length - best_length) / best_length) * 100 if best_length != 0 else 0.0
			# Draw the end screen overlay
			draw_end_screen(screen, font, best_length, taken_length, percent_diff)
		else:
			# Simulation mode (after countdown)
			if not active:
				# Countdown phase: show remaining time
				remaining = config_time_to_start - (pygame.time.get_ticks() - simulation_start_time) / 1000.0
				countdown_text = font.render("Time to start: {:.2f} s".format(remaining), True, (128, 128, 128))
				screen.blit(countdown_text, (10, 10))
			else:
				if THREE_D:
					draw_view(player, grid, CELL_SIZE, config_view_distance * CELL_SIZE, screen, WINDOW_SIZE, WINDOW_SIZE, path_taken, PATH_SIZE)
				else:
					draw_polygon_from_rays(player, grid, CELL_SIZE, config_view_distance * CELL_SIZE, screen, 1)
					# Simulation active: show elapsed time and other info
				time_text = font.render("Elapsed Time: {:.2f} s".format(elapsed_time), True, (128, 128, 128))
				best_path_length_text = font.render("Best Path Length: {:.2f}".format(len(path)), True, (128, 128, 128))
				path_taken_text = font.render("Path Taken Length: {:.2f}".format(len(path_taken)), True, (128, 128, 128))
				screen.blit(time_text, (10, 10))
				screen.blit(best_path_length_text, (10, 30))
				screen.blit(path_taken_text, (10, 50))

		if not THREE_D:
			player.draw(screen)
		pygame.display.flip()


if __name__ == '__main__':
	main()
