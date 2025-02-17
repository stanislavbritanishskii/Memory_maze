import math
import pygame
def circle_rect_collision(circle_pos, radius, rect):
	"""
	Checks for collision between a circle (with center circle_pos and radius) and a rectangle.
	Uses the standard method: find the closest point on the rectangle to the circle's center,
	then determine if that point is within the circle.
	"""
	closest_x = max(rect.left, min(circle_pos.x, rect.right))
	closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
	distance_sq = (circle_pos.x - closest_x) ** 2 + (circle_pos.y - closest_y) ** 2
	return distance_sq < radius ** 2


def circle_collides(pos, radius, grid, CELL_SIZE):
	"""
	Checks if a circle with center pos and radius collides with any black cell (obstacle) in the grid.
	It limits the check to grid cells that are within the circle's bounding box.
	"""
	n = len(grid)
	left_idx = max(0, int((pos.x - radius) // CELL_SIZE))
	right_idx = min(n - 1, int((pos.x + radius) // CELL_SIZE))
	top_idx = max(0, int((pos.y - radius) // CELL_SIZE))
	bottom_idx = min(n - 1, int((pos.y + radius) // CELL_SIZE))

	for row in range(top_idx, bottom_idx + 1):
		for col in range(left_idx, right_idx + 1):
			if not grid[row][col]:  # True represents a black cell (obstacle)
				rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
				if circle_rect_collision(pos, radius, rect):
					return True
	return False

class Player:
	def __init__(self, pos, radius, speed, color=(255, 0, 0)):
		"""
		Initializes the player.
		- pos: A pygame.math.Vector2 for the player's position.
		- radius: The radius of the player's circle.
		- speed: The movement speed in pixels per second.
		- color: The player's color.
		"""
		self.pos = pos
		self.orientation = 0
		self.fov = 90
		self.radius = radius
		self.speed = speed
		self.color = color

	def normalize_orientation(self):
		while self.orientation > math.pi:
			self.orientation -= 2 * math.pi
		while self.orientation < -math.pi:
			self.orientation += 2 * math.pi

	def move(self, movement, grid, CELL_SIZE, dt):
		"""
		Attempts to move the player using separate axis collision checking.
		- movement: A pygame.math.Vector2 representing the desired movement (already scaled by dt).
		- grid: The game grid.
		- CELL_SIZE: The size of each grid cell.
		"""

		if movement.length() != 0:
			movement = movement.normalize() * self.speed * dt
		# Move in x direction
		new_pos = self.pos.copy()
		new_pos.x += movement.x
		if not circle_collides(new_pos, self.radius, grid, CELL_SIZE):
			self.pos.x = new_pos.x
		# Move in y direction
		new_pos = self.pos.copy()
		new_pos.y += movement.y
		if not circle_collides(new_pos, self.radius, grid, CELL_SIZE):
			self.pos.y = new_pos.y

	def move_3d(self, movement, grid, CELL_SIZE, dt):
		"""
		Attempts to move the player considering orientation.
		- movement: A pygame.math.Vector2 representing the desired movement (already scaled by dt).
		- grid: The game grid.
		- CELL_SIZE: The size of each grid cell.
		"""

		if movement.length() != 0:
			movement = movement.normalize() * self.speed * dt
			self.normalize_orientation()
			angle_rad = self.orientation + math.pi / 2
			if angle_rad > math.pi:
				angle_rad -= 2 * math.pi
			if angle_rad < -math.pi:
				angle_rad += 2 * math.pi

			rotated_movement = pygame.math.Vector2(
				movement.x * math.cos(angle_rad) - movement.y * math.sin(angle_rad),
				movement.x * math.sin(angle_rad) + movement.y * math.cos(angle_rad)
			)
		else:
			rotated_movement = pygame.math.Vector2()


		# Move in x direction
		new_pos = self.pos.copy()
		new_pos.x += rotated_movement.x
		if not circle_collides(new_pos, self.radius, grid, CELL_SIZE):
			self.pos.x = new_pos.x
		# Move in y direction
		new_pos = self.pos.copy()
		new_pos.y += rotated_movement.y
		if not circle_collides(new_pos, self.radius, grid, CELL_SIZE):
			self.pos.y = new_pos.y



	def draw(self, screen):
		"""
		Draws the player as a circle on the provided screen.
		"""
		pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))
