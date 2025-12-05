# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
from renderer import Renderer
import random

class Application():

	def __init__(self):
		self.isRunning = False
		self.world = WorldGenerator.generate_world(
			width=100,
            height=50,
            wall_count=350, 
            food_count=300,
            creatures_count=30
        )
		self.renderer = Renderer(self.world, cell_size=12)

	def run(self):
		self.isRunning = True
		while self.isRunning:
			if self.renderer.isGotQuitEvent():
				self.isRunning = False
			self.world.update()
			self.world.update_map()
			self.renderer.draw()
			#self.limit_fps()
		self.terminate()

	def terminate(self):
		quitFlag = self.renderer.terminate()
		if quitFlag:
			print("Terminated normally")
		else:
			print("Terminated with errors: " + str(quitFlag))

	def saveWorld(self):
		print("saveWorld dummy")

	def loadWorld(self):
		print("loadWorld dummy")
	
	def limit_fps(self):
		"""Ограничение FPS."""
		self.renderer.clock.tick(15)

	



