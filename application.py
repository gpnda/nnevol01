# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
# from renderer.v1.renderer import Renderer
# from renderer.mock.renderer import Renderer
# from renderer.v2.renderer import Renderer
from renderer.v3dto.renderer import Renderer
from simparams import sp
from service.logger.logger import logme
from service.performance_monitor.performance_monitor import PerformanceMonitor


class Application():

	def __init__(self):
		self.quit_flag = False
		self.is_running = True
		self.animate_flag = True
		self.is_logging = True
		self.performance_monitor = PerformanceMonitor()

		# Генерация мира
		self.world = WorldGenerator.generate_world(
			width=100,
            height=50,
            wall_count=350, 
            food_count=sp.food_amount,
            creatures_count=500
        )
		self.renderer = Renderer(self.world, self)
		
		
	def run(self):

		print("/ Fucking go! /")
		
		while self.quit_flag == False:

			if self.is_running:
				self.world.update()
				self.world.update_map()
				if self.is_logging:
					logme.write_stats(self.world.creatures)
					logme.write_population_size(len(self.world.creatures))
			
			if self.animate_flag:
				self.renderer.draw()

			
			
			#self.limit_fps()

			self.renderer.control_run()

			self.performance_monitor.tick(self.world.tick)

		print("/ Terminated. /")

	def terminate(self):
		self.quit_flag = True
		
	def toggle_run(self):
		"""Включить/выключить симуляцию (Space)."""
		if self.is_running:
			self.is_running = False
		else:
			self.is_running = True
	
	def toggle_animate(self):
		"""Включить/выключить анимацию (A)."""
		if self.animate_flag:
			self.animate_flag = False
		else:
			self.animate_flag = True

	def toggle_logging(self):
		"""Включить/выключить логгирование (L)."""
		if self.is_logging:
			self.is_logging = False
		else:
			self.is_logging = True
	
	def limit_fps(self):
		"""Ограничение FPS."""
		self.renderer.clock.tick(2)

	def saveWorld(self):
		"""Сохранить мир (F1)."""
		print("saveWorld - saving simulation state")
	
	def loadWorld(self):
		"""Загрузить мир (F2)."""
		print("loadWorld - loading simulation state")
	
	def resetWorld(self):
		"""Сбросить мир (F3)."""
		print("resetWorld - resetting simulation")
		self.is_running = False
	
	
	
	
	
	
	
	
	
	
	



	




