import pygame
import math
import numpy as np

WindowSize = WindowWidth, WindowHeight = (750, 950)
Blue = (0,0,255)
Green = (0,255,0)
BorderWidth = 2
LargeSpace = False


def gray(val, min, max):
	if val > max:
		val = max
	if val < min:
		val = min
	g = math.floor((val - min) / (max-min) * 255)
	return (g, g, g)
	
def extraInputPos(idx):
	Rows = [20, 3, 8]
	col = idx
	for row in range(len(Rows)):
		if col - Rows[row] < 0:
			return row, col
		col -= Rows[row]
		
	return len(Rows), col

class Display(object):

	def __init__(self, screen_width, screen_height, controller_lookup):
		pygame.init()
		pygame.font.init()
		self.font = pygame.font.SysFont('Times New Roman', 12)
		self.controller_lookup = controller_lookup
		self.screen_width = screen_width
		self.screen_height = screen_height
		
		self.window = window = pygame.display.set_mode(WindowSize)
		
	
	def update(self, inputs, state, outputs, q, reward, convs):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				raise Exception("Display window closed by user.")
	
		self.window.fill(Green)
		y = self.drawInputs(inputs)
		y = self.drawState(state, y)
		y = self.drawQ(q, y)
		y = self.drawOutputs(outputs, y)
		y = self.drawReward(reward, y)
		self.drawConvs(convs, 0)
		pygame.display.flip()
		
	def drawConvs(self, convs, y):
		if convs != None:
			for conv_batch in convs:
				y = self.drawConv(conv_batch[0], y)
				
		return y
				
	def drawConv(self, conv, base_y):
		width = len(conv[0])
		height = len(conv)
		size = int(300 / width)
		largest = min(np.amax(conv), 1)
		for x in range(width):
			for y in range(height):
				pixel = conv[y][x]
				
				pixel = (pixel[2]*256/largest, pixel[1]*256/largest, pixel[0]*256/largest)
				
				pixel = (
					int(min(max(pixel[0], 0), 255)),
					int(min(max(pixel[1], 0), 255)),
					int(min(max(pixel[2], 0), 255)),
				)
				self.window.fill(pixel, (350 + x*size, y*size+base_y, size, size))
				
		return base_y + height * size + 5
	
	def drawInputs(self, inputs):
		NumTiles = self.screen_width * self.screen_height
		TileSize = 15
		
		self.window.fill(Blue,
			(
				5-BorderWidth,
				5-BorderWidth,
				self.screen_width*TileSize + BorderWidth*2,
				self.screen_height*TileSize + BorderWidth*2,
			)
		)
		for tileX in range(self.screen_width):
			for tileY in range(self.screen_height):
				self.window.fill(
					gray(inputs[tileY*self.screen_width+tileX], -2, 2),
					(5+tileX*TileSize, 5+tileY*TileSize, TileSize, TileSize)
				)
				
		y = self.screen_height*TileSize+10
		
		maxRow = 0
		maxCol = 0
		for i in range(NumTiles, len(inputs)):
			row, col = extraInputPos(i-NumTiles)
			maxRow = max(row, maxRow)
			maxCol = max(col, maxCol)
		
		self.window.fill(Blue,
			(
				5-BorderWidth,
				y-BorderWidth,
				(maxCol+1)*TileSize + BorderWidth*2,
				(maxRow+1)*TileSize + BorderWidth*2,
			)
		)
		for i in range(NumTiles, len(inputs)):
			row, col = extraInputPos(i-NumTiles)
			self.window.fill(
				gray(inputs[i], 0, 1),
				(5 + col*TileSize, y + row*TileSize, TileSize, TileSize)
			)
			
		y += (maxRow+1)*TileSize
		if LargeSpace:
			y += 30
		else:
			y += 10
		
		if not LargeSpace:
			self.window.fill(Blue, (0, y-3, WindowWidth, 2))
			
		return y
	
	def drawState(self, state, y):
		for layer in state:
			y = self.drawLayer(layer.c[0], y)
			y = self.drawLayer(layer.h[0], y)
			y += 10
			if not LargeSpace:
				self.window.fill(Blue, (0, y-3, WindowWidth, 2))
			
		return y
		
	def drawLayer(self, layer, y):
		CellSize = 6
		CellsPerRow = 50
		rows = math.ceil(len(layer) / CellsPerRow)
		self.window.fill(Blue,
			(
				5-BorderWidth,
				y-BorderWidth,
				CellsPerRow*CellSize + BorderWidth*2,
				rows*CellSize + BorderWidth*2,
			)
		)
		for i in range(len(layer)):
			cellX = i % CellsPerRow
			cellY = i // CellsPerRow
			self.window.fill(
				gray(layer[i], -1, 1),
				(5+cellX*CellSize, y+cellY*CellSize, CellSize, CellSize)
			)
		
		y += (rows + 1) * CellSize
		
		if LargeSpace:
			y += 20
		
		return y
		
	def drawOutputs(self, outputs, y):
		positions = [
			(0, 1),
			(2, 1),
			(5, 2),
		]
		
		OutputSize = 15
		
		self.window.fill(Blue,
			(
				5-BorderWidth,
				y-BorderWidth,
				7*OutputSize+BorderWidth*2,
				3*OutputSize+BorderWidth*2,
			)
		)
		for i in range(len(outputs)):
			px,py = positions[i]
			px,py = px*OutputSize,py*OutputSize
			self.window.fill(
				gray(outputs[i], 0, 1),
				(5+px, y+py, OutputSize, OutputSize)
			)
			
		y += OutputSize * 3
		y += 5
		
		return y

	def drawQ(self, q, y):
		self.window.fill(Blue,
			(
				5-BorderWidth,
				y-BorderWidth,
				150,
				13*len(q)+BorderWidth*2,
			)
		)
		
		for i in range(len(q)):
			textsurface = self.font.render('{0}: {1}'.format(str(i), str(q[i])), True, (220, 220, 220))
			self.window.blit(textsurface, (5, y))
			y += 13
			
		y += 5
			
		return y
		
	def drawReward(self, reward, y):
		self.window.fill(Blue,
			(
				5-BorderWidth,
				y-BorderWidth,
				150,
				13+BorderWidth*2,
			)
		)
		
		textsurface = self.font.render('Reward: {0}'.format(reward), True, (220, 220, 220))
		self.window.blit(textsurface, (5, y))
		y += 18
		
		return y
	
	def close(self):
		pygame.display.quit()