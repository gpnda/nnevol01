# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
from renderer import Renderer
import random

class Application():

	def __init__(self):
		self.quit_flag = False
		self.is_running = True

		# Параметры симуляции
		self.parameter1 = 10
		self.parameter2 = 0.5
		self.parameter3 = 55000
		self.parameter4 = 0.15
		self.parameter5 = 0.35

		# Генерация мира
		self.world = WorldGenerator.generate_world(
			width=100,
            height=50,
            wall_count=350, 
            food_count=300,
            creatures_count=30
        )
		self.renderer = Renderer(self.world, self)

		# Добавляем переменные в панель с callback функциями
		self.renderer.add_variable("parameter1", self.parameter1, min_val=0, max_val=100, on_change=self._on_parameter1_change )
		self.renderer.add_variable("parameter2", self.parameter2, float, 0.0, 100.0, on_change=self._on_parameter2_change )
		self.renderer.add_variable("parameter3", self.parameter3, min_val=-20, max_val=50, on_change=self._on_parameter3_change )
		self.renderer.add_variable("parameter4", self.parameter4, float, 0.0, 1.0, on_change=self._on_parameter4_change )
		self.renderer.add_variable("parameter5", self.parameter5, int, on_change=self._on_parameter5_change )
		

	def run(self):
		self.quit_flag = False # Флаг о том, что приложение надо закрыть
		self.is_running = True # Флаг о том что процесс симуляции запущен
		self.animate_flag = True # Флаг о том, что надо анимировать симуляцию

		while self.quit_flag == False:

			if self.is_running:
				self.world.update()
				self.world.update_map()
			
			if self.animate_flag:
				self.renderer.draw()
			
			#self.limit_fps()
			self.renderer.control_run()
		print("---===   Terminated   ===---")
























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
	
	def limit_fps(self):
		"""Ограничение FPS."""
		self.renderer.clock.tick(15)
	
	def _on_parameter1_change(self, value):
		"""Callback при изменении parameter1."""
		self.parameter1 = value
		print(f"parameter1 changed to: {self.parameter1}")
	
	def _on_parameter2_change(self, value):
		"""Callback при изменении parameter2."""
		self.parameter2 = value
		print(f"parameter2 changed to: {self.parameter2}")
	
	def _on_parameter3_change(self, value):
		"""Callback при изменении parameter3."""
		self.parameter3 = value
		print(f"parameter3 changed to: {value}")
	
	def _on_parameter4_change(self, value):
		"""Callback при изменении parameter4."""
		self.parameter4 = value
		print(f"parameter4 changed to: {value}")
	
	def _on_parameter5_change(self, value):
		"""Callback при изменении parameter5."""
		self.parameter5 = value
		print(f"parameter5 changed to: {value}")

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
	




