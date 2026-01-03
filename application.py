# -*- coding: utf-8 -*-

from world_generator import WorldGenerator
from renderer import Renderer
import random
from simparams import sp

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
		self.renderer.add_variable("mutation_probability", 		sp.mutation_probability, 		float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_mutation_probability_change )
		self.renderer.add_variable("mutation_strength", 		sp.mutation_strength, 			float, 	min_val=0.0, 	max_val=100.0, 	on_change=self._on_mutation_strength_change )
		self.renderer.add_variable("creature_max_age", 			sp.creature_max_age, 			int, 	min_val=1, 		max_val=100000, on_change=self._on_creature_max_age_change )
		self.renderer.add_variable("food_amount", 				sp.food_amount, 				int, 	min_val=1, 		max_val=100000, on_change=self._on_food_amount_change )
		self.renderer.add_variable("food_energy_capacity", 		sp.food_energy_capacity, 		float, 	min_val=0.0, 	max_val=50.0, 	on_change=self._on_food_energy_capacity_change )
		self.renderer.add_variable("food_energy_chunk", 		sp.food_energy_chunk, 			float, 	min_val=0.0, 	max_val=50.0, 	on_change=self._on_food_energy_chunk_change )
		self.renderer.add_variable("reproduction_ages", 		sp.reproduction_ages, 			str, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_reproduction_ages_change )
		self.renderer.add_variable("reproduction_offsprings", 	sp.reproduction_offsprings, 	int, 	min_val=1, 		max_val=100, 	on_change=self._on_reproduction_offsprings_change )
		self.renderer.add_variable("energy_cost_tick", 			sp.energy_cost_tick, 			float, 	min_val=0.0, 	max_val=100.0, 	on_change=self._on_energy_cost_tick_change )
		self.renderer.add_variable("energy_cost_move", 			sp.energy_cost_move, 			float, 	min_val=0.0, 	max_val=100.0, 	on_change=self._on_energy_cost_move_change )
		self.renderer.add_variable("energy_cost_rotate", 		sp.energy_cost_rotate, 			float, 	min_val=-20.0, 	max_val=50.0, 	on_change=self._on_energy_cost_rotate_change )
		self.renderer.add_variable("energy_cost_bite", 			sp.energy_cost_bite, 			float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_cost_bite_change )
		self.renderer.add_variable("energy_gain_from_food", 	sp.energy_gain_from_food, 		float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_gain_from_food_change )
		self.renderer.add_variable("energy_gain_from_bite_cr", 	sp.energy_gain_from_bite_cr, 	float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_gain_from_bite_cr_change )
		self.renderer.add_variable("energy_loss_bitten", 		sp.energy_loss_bitten, 			float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_loss_bitten_change )
		self.renderer.add_variable("energy_loss_collision", 	sp.energy_loss_collision, 		float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_loss_collision_change )
		
		# Добавление функциональных клавиш
		self.renderer.add_function_key("F3", "SimParams", self.simparams_print)

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
	
	
	
	
	
	
	
	
	
	
	
	def _on_mutation_probability_change(self, value):
		"""Callback при изменении mutation_probability."""
		sp.mutation_probability = value
		print(f"mutation_probability changed to: {sp.mutation_probability}")

	def _on_mutation_strength_change(self, value):
		"""Callback при изменении mutation_strength."""
		sp.mutation_strength = value
		print(f"mutation_strength changed to: {sp.mutation_strength}")
	
	def _on_creature_max_age_change(self, value):
		"""Callback при изменении creature_max_age."""
		sp.creature_max_age = value
		print(f"creature_max_age changed to: {sp.creature_max_age}")
	
	def _on_food_amount_change(self, value):
		"""Callback при изменении food_amount."""
		sp.food_amount = value
		print(f"food_amount changed to: {sp.food_amount}")
	
	def _on_food_energy_capacity_change(self, value):
		"""Callback при изменении food_energy_capacity."""
		sp.food_energy_capacity = value
		self.world.change_food_capacity() # Обновляем текущую еду в мире
		print(f"food_energy_capacity changed to: {sp.food_energy_capacity}")
	
	def _on_food_energy_chunk_change(self, value):
		"""Callback при изменении food_energy_chunk."""
		sp.food_energy_chunk = value
		print(f"food_energy_chunk changed to: {sp.food_energy_chunk}")
	
	def _on_reproduction_ages_change(self, value):
		"""Callback при изменении reproduction_ages.
		sp.reproduction_ages = [100, 200, 300, 500]
		"""
		print("Callback при изменении reproduction_ages...")
		try:
			# remove square brackets if present
			if value.startswith('[') and value.endswith(']'):
				value = value[1:-1]
			ages = [int(x.strip()) for x in value.split(",")]
			sp.reproduction_ages = ages
			print(f"reproduction_ages changed to: {sp.reproduction_ages}")
		except Exception as e:
			print(f"Ошибка разбора reproduction_ages: {e}")
	
	def _on_reproduction_offsprings_change(self, value):
		"""Callback при изменении reproduction_offsprings."""
		sp.reproduction_offsprings = value
		print(f"reproduction_offsprings changed to: {sp.reproduction_offsprings}")
	
	def _on_energy_cost_tick_change(self, value):
		"""Callback при изменении energy_cost_tick."""
		sp.energy_cost_tick = value
		print(f"energy_cost_tick changed to: {sp.energy_cost_tick}")
	
	def _on_energy_cost_move_change(self, value):
		"""Callback при изменении energy_cost_move."""
		sp.energy_cost_move = value
		print(f"energy_cost_move changed to: {sp.energy_cost_move}")
	
	def _on_energy_cost_rotate_change(self, value):
		"""Callback при изменении energy_cost_rotate."""
		sp.energy_cost_rotate = value
		print(f"energy_cost_rotate changed to: {sp.energy_cost_rotate}")
	
	def _on_energy_cost_bite_change(self, value):
		"""Callback при изменении energy_cost_bite."""
		sp.energy_cost_bite = value
		print(f"energy_cost_bite changed to: {sp.energy_cost_bite}")
	
	def _on_energy_gain_from_food_change(self, value):
		"""Callback при изменении energy_gain_from_food."""
		sp.energy_gain_from_food = value
		print(f"energy_gain_from_food changed to: {sp.energy_gain_from_food}")
	
	def _on_energy_gain_from_bite_cr_change(self, value):
		"""Callback при изменении energy_gain_from_bite_cr."""
		sp.energy_gain_from_bite_cr = value
		print(f"energy_gain_from_bite_cr changed to: {sp.energy_gain_from_bite_cr}")
	
	def _on_energy_loss_bitten_change(self, value):
		"""Callback при изменении energy_loss_bitten."""
		sp.energy_loss_bitten = value
		print(f"energy_loss_bitten changed to: {sp.energy_loss_bitten}")
	
	def _on_energy_loss_collision_change(self, value):
		"""Callback при изменении energy_loss_collision."""
		sp.energy_loss_collision = value
		print(f"energy_loss_collision changed to: {sp.energy_loss_collision}")
	



	def simparams_print(self):
		"""Вывод всех параметров симуляции в консоль."""
		print("=== SimParams ===")
		print(f"mutation_probability: {sp.mutation_probability}")
		print(f"mutation_strength: {sp.mutation_strength}")
		print(f"creature_max_age: {sp.creature_max_age}")
		print(f"food_amount: {sp.food_amount}")
		print(f"food_energy_capacity: {sp.food_energy_capacity}")
		print(f"food_energy_chunk: {sp.food_energy_chunk}")
		print(f"reproduction_ages: {sp.reproduction_ages} type: {type(sp.reproduction_ages)}")
		print(f"reproduction_offsprings: {sp.reproduction_offsprings}")
		print(f"energy_cost_tick: {sp.energy_cost_tick}")
		print(f"energy_cost_move: {sp.energy_cost_move}")
		print(f"energy_cost_rotate: {sp.energy_cost_rotate}")
		print(f"energy_cost_bite: {sp.energy_cost_bite}")
		print(f"energy_gain_from_food: {sp.energy_gain_from_food}")
		print(f"energy_gain_from_bite_cr: {sp.energy_gain_from_bite_cr}")
		print(f"energy_loss_bitten: {sp.energy_loss_bitten}")
		print(f"energy_loss_collision: {sp.energy_loss_collision}")



	




