# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
from renderer import Renderer
import random

class Application():

	def __init__(self):
		self.quit_flag = False
		self.is_running = True

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
		self.renderer.add_variable("sim_mutation_probability", self.world.sim_mutation_probability, float, 0.0, 1.0, on_change=self._on_sim_mutation_probability_change )
		self.renderer.add_variable("sim_mutation_strength", self.world.sim_mutation_strength, float, 0.0, 100.0, on_change=self._on_sim_mutation_strength_change )

		self.renderer.add_variable("sim_creature_max_age", self.world.sim_creature_max_age, int, 0, 50000, on_change=self._on_sim_creature_max_age_change )
		self.renderer.add_variable("sim_food_amount", self.world.sim_food_amount, int, 0, 50000, on_change=self._on_sim_food_amount_change )
		self.renderer.add_variable("sim_food_energy_capacity", self.world.sim_food_energy_capacity, float, 0.0, 100.0, on_change=self._on_sim_food_energy_capacity_change )
		self.renderer.add_variable("sim_food_energy_chunk", self.world.sim_food_energy_chunk, float, 0.0, 100.0, on_change=self._on_sim_food_energy_chunk_change )

		self.renderer.add_variable("sim_reproduction_ages", self.world.parameter2, float, 0.0, 100.0, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_reproduction_offsprings", self.world.sim_reproduction_offsprings, int, 1, 20, on_change=self._on_sim_reproduction_offsprings_change )

		self.renderer.add_variable("sim_energy_cost_tick", self.world.parameter2, float, 0.0, 100.0, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_energy_cost_move", self.world.parameter2, float, 0.0, 100.0, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_energy_cost_rotate", self.world.parameter3, min_val=-20, max_val=50, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_energy_cost_bite", self.world.parameter4, float, 0.0, 1.0, on_change=self._on_parameter4_change )
		self.renderer.add_variable("sim_energy_gain_from_food", self.world.parameter5, int, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_energy_gain_from_bite_cr", self.world.parameter5, int, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_energy_loss_bitten", self.world.parameter5, int, on_change=self._on_parameter5_change )
		self.renderer.add_variable("sim_energy_loss_collision", self.world.parameter5, int, on_change=self._on_parameter5_change )
		

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
	



	
	def _on_sim_mutation_probability_change(self, value):
		"""Callback при изменении sim_mutation_probability."""
		self.world.sim_mutation_probability = value
		print(f"sim_mutation_probability changed to: {self.world.sim_mutation_probability}")
	
	def _on_sim_mutation_strength_change(self, value):
		"""Callback при изменении sim_mutation_strength."""
		self.world.sim_mutation_strength = value
		print(f"sim_mutation_strength changed to: {self.world.sim_mutation_strength}")
	
	def _on_sim_creature_max_age_change(self, value):
		"""Callback при изменении sim_creature_max_age."""
		self.world.sim_creature_max_age = value
		print(f"sim_creature_max_age changed to: {self.world.sim_creature_max_age}")
	
	def _on_sim_food_amount_change(self, value):
		"""Callback при изменении sim_food_amount."""
		self.world.sim_food_amount = value
		print(f"sim_food_amount changed to: {self.world.sim_food_amount}")

	def _on_sim_food_energy_capacity_change(self, value):
		"""Callback при изменении sim_food_energy_capacity."""
		self.world.sim_food_energy_capacity = value
		print(f"sim_food_energy_capacity changed to: {self.world.sim_food_energy_capacity}")

	def _on_sim_food_energy_chunk_change(self, value):
		"""Callback при изменении sim_food_energy_chunk."""
		self.world.sim_food_energy_chunk = value
		print(f"sim_food_energy_chunk changed to: {self.world.sim_food_energy_chunk}")

	def _on_sim_reproduction_offsprings_change(self, value):
		"""Callback при изменении sim_reproduction_offsprings."""
		self.world.sim_reproduction_offsprings = value
		print(f"sim_reproduction_offsprings changed to: {self.world.sim_reproduction_offsprings}")

	def _on_parameter4_change(self, value):
		"""Callback при изменении parameter4."""
		self.world.parameter4 = value
		print(f"parameter4 changed to: {self.world.parameter4}")
	
	def _on_parameter5_change(self, value):
		"""Callback при изменении parameter5."""
		self.world.parameter5 = value
		print(f"parameter5 changed to: {self.world.parameter5}")












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
	




