import pygame
import ctypes
import time
import math
from queue import PriorityQueue

# triples
WHITE = (255, 255, 255)
ORANGE = (255, 165 , 0)
BLUE = (0, 0, 250)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

WIDTH = 800
# returns "pygame.Surface" object
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('PathfindingVisualizer by Eduard Hermann')
image = pygame.image.load('icon.png')
pygame.display.set_icon(image)

class Node:

	def __init__(self, row, column, width, maxRows):
		self.row = row
		self.column = column
		self.width = width
		self.maxRows = maxRows
		self.x = column * width
		self.y = row * width
		self.color = WHITE
		self.neighbors = []

	def get_pos(self):
		return self.row, self.column

	def get_neighbors(self):
		return self.neighbors

	def get_color(self):
		return self.color

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == BLUE

	def reset(self):
		self.color = WHITE

	def make_open(self):
		self.color = GREEN

	def make_closed(self):
		self.color = RED

	def make_barrier(self):
		self.color = BLACK

	def make_start(self):
		self.color = ORANGE

	def make_end(self):
		self.color = BLUE

	def make_path(self):
		self.color = YELLOW

	def draw_itself(self, window):
		pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		# UP
		if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
			self.neighbors.append(grid[self.row - 1][self.column])
		# DOWN
		if self.row < self.maxRows - 1 and not grid[self.row + 1][self.column].is_barrier():
			self.neighbors.append(grid[self.row + 1][self.column])
		# LEFT
		if self.column > 0 and not grid[self.row][self.column - 1].is_barrier():
			self.neighbors.append(grid[self.row][self.column - 1])
		# RIGHT
		if self.column < self.maxRows - 1 and not grid[self.row][self.column + 1].is_barrier():
			self.neighbors.append(grid[self.row][self.column + 1])

# manhattan distance
def MDistance(pos1, pos2):
	x1, y1 = pos1
	x2, y2 = pos2
	return abs(x2 - x1) + abs(y2 - y1)

def make_grid(rows, width):
	grid = []
	node_width = width // rows
	for i in range(rows):
		grid.append([])
		for n in range(rows):
			node = Node(i, n, node_width, rows)
			grid[i].append(node)
	return grid

def clear_grid(grid, start, end):
	for row in grid:
		for node in row:
			if node.get_color() != start.get_color() and node.get_color() != end.get_color() and not node.is_barrier():
				node.reset()

def draw_grid(window, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(window, GRAY, (i * gap, 0), (i * gap, width))
	for i in range(rows):
		pygame.draw.line(window, GRAY, (0, i * gap), (width, i * gap))

def draw(window, grid, rows, width):
	window.fill(WHITE)
	for row in grid:
		for node in row:
			node.draw_itself(window)
	draw_grid(window, rows, width)
	pygame.display.update()

def get_clicked_pos(pos, rows, width):
	gap = width // rows
	x, y = pos

	row = y // gap
	column = x // gap

	return row, column

def compare(node, start, end):
	if node != start and node != end:
		return True
	return False

# backtracking through possible paths
def reconstruct_path(draw, came_from, start, end):
	end_temp = end
	path_count = 0
	while end in came_from:
		end = came_from[end]
		if compare(end, start, end_temp):
			end.make_path()
			path_count += 1
		draw()
	return path_count

# f_score(n) = g_score(n) + MDistance(n)
def AStar(draw, grid, start, end):
	count = 0
	queue = PriorityQueue()
	queue.put((0, count, start))
	g_score = {node: float("inf") for row in grid for node in row}
	g_score[start] = 0
	f_score = {node: float("inf") for row in grid for node in row}
	f_score[start] = MDistance(start.get_pos(), end.get_pos())

	container = {start}
	came_from = {}

	while not queue.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		# removes
		current = queue.get()[2]
		container.remove(current)

		if current == end:
			path_count = reconstruct_path(draw, came_from, start, end)
			return path_count, True
		else:
			if compare(current, start, end):
				current.make_closed()
			draw()

		for neighbor in current.get_neighbors():
			g_score_neighbor = g_score[current] + 1

			if g_score_neighbor < g_score[neighbor]:
				g_score[neighbor] = g_score_neighbor
				f_score[neighbor] = g_score_neighbor + MDistance(neighbor.get_pos(), end.get_pos())
				
				if neighbor not in container:
					count += 1
					queue.put((f_score[neighbor], count, neighbor))
					container.add(neighbor)
					came_from[neighbor] = current
					if compare(neighbor, start, end):
						neighbor.make_open()
	return 0, False

def Dijkstra(draw, grid, start, end):
	count = 0
	d_score = {node: float("inf") for row in grid for node in row}
	d_score[start] = 0
	v_score = {node: False for row in grid for node in row}
	queue = PriorityQueue()
	queue.put((d_score[start], count, start))

	came_from = {}

	while not queue.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = queue.get()[2]

		if current == end:
			path_count = reconstruct_path(draw, came_from, start, end)
			return path_count, True
		else:
			if compare(current, start, end):
				current.make_closed()
			draw()

		v_score[current] = True

		for neighbor in current.get_neighbors():
			if not v_score[neighbor]:
				neighbor_d_score = d_score[current] + 1

				if neighbor_d_score < d_score[neighbor]:
					count += 1
					d_score[neighbor] = neighbor_d_score
					queue.put((d_score[neighbor], count, neighbor))
					came_from[neighbor] = current
					if compare(neighbor, start, end):
						neighbor.make_open()
	return 0, False

def main(window, width):
	ROWS = 50
	GRID = make_grid(ROWS, width)

	start = None
	end = None

	run = True

	while run:
		draw(window, GRID, ROWS, width)
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				row, column = get_clicked_pos(pos, ROWS, width)
				spot = GRID[row][column]
				if not start and spot != end:
					start = spot
					spot.make_start()
				elif not end and spot != start:
					end = spot
					spot.make_end()
				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]:
				pos = pygame.mouse.get_pos()
				row, column = get_clicked_pos(pos, ROWS, width)
				spot = GRID[row][column]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if start is not None and end is not None:
					
					if event.key == pygame.K_a:
						for row in GRID:
							for node in row:
								node.update_neighbors(GRID)

						time_start = time.time()
						path_count, found = AStar(lambda: draw(window, GRID, ROWS, width), GRID, start, end)
						my_info = str(time.time() - time_start)[:6]
						ctypes.windll.user32.MessageBoxW(0, "Execution Time: " + my_info + " seconds\n" + "Path Found: " + str(found) + "\n" + "Path Length: " + str(path_count), "AStar Information Message", 64)

					elif event.key == pygame.K_d:
						for row in GRID:
							for node in row:
								node.update_neighbors(GRID)

						time_start = time.time()
						path_count, found = Dijkstra(lambda: draw(window, GRID, ROWS, width), GRID, start, end)
						my_info = str(time.time() - time_start)[:6]
						ctypes.windll.user32.MessageBoxW(0, "Execution Time: " + my_info + " seconds\n" + "Path Found: " + str(found) + "\n" + "Path Length: " + str(path_count), "Dijkstra Information Message", 64)

					elif event.key == pygame.K_c:
						start = None
						end = None
						GRID = make_grid(ROWS, width)

					elif event.key == pygame.K_v:
						clear_grid(GRID, start, end)
	pygame.quit()

main(WIN, WIDTH)
