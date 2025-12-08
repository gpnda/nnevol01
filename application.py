# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
from renderer import Renderer
import random

class Application():

	def __init__(self):
		self.quit_flag = False
		self.is_running = True
		self.world = WorldGenerator.generate_world(
			width=100,
            height=50,
            wall_count=350, 
            food_count=300,
            creatures_count=30
        )
		self.renderer = Renderer(self.world, self)

	def run(self):
		self.quit_flag = False # Флаг о том, что приложение надо закрыть
		self.is_running = True # Флаг о том что процесс симуляции запущен
		self.animate_flag = True # Флаг о том, что надо анимировать симуляцию

		while self.quit_flag == False:

			if self.is_running:
				self.world.update()
				self.world.update_map()
			
			if self.animate_flag:
				self.renderer.draw_map()
			
			#self.limit_fps()
			self.renderer.control_run()
		print("---===   Terminated   ===---")

	def terminate(self):
		self.quit_flag = True
		
	def saveWorld(self):
		print("saveWorld dummy")

	def loadWorld(self):
		print("loadWorld dummy")
	
	def toggle_run(self):
		if self.is_running:
			self.is_running = False
		else:
			self.is_running = True
	
	def toggle_animate(self):
		if self.animate_flag:
			self.animate_flag = False
		else:
			self.animate_flag = True
	
	def limit_fps(self):
		"""Ограничение FPS."""
		self.renderer.clock.tick(15)

	



