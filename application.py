# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
from renderer import Renderer
import random

class Application():

	def __init__(self):
		self.is_running = False
		self.world = WorldGenerator.generate_world(
			width=100,
            height=50,
            wall_count=350, 
            food_count=300,
            creatures_count=30
        )
		self.renderer = Renderer(self.world, self)

	def run(self):
		self.is_running = True
		while self.is_running:
			if self.renderer.isGotQuitEvent():
				self.is_running = False
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
	
	def toggle_run(self):
		if self.is_running:
			self.is_running = False
		else:
			self.is_running = True
	
	def limit_fps(self):
		"""Ограничение FPS."""
		self.renderer.clock.tick(15)

	



