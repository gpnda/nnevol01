# -*- coding: utf-8 -*-


import sys
from world_generator import WorldGenerator
from renderer.v3dto.renderer import Renderer
from simparams import sp
from service.logger.logger import logme
from service.performance_monitor.performance_monitor import PerformanceMonitor
from service.world_persistence.world_persistence import world_persistence


class Application():

	def __init__(self):
		self.quit_flag = False
		self.is_running = True
		self.animate_flag = True
		self.performance_monitor = PerformanceMonitor(self)
		self.experiment_mode = False
		self.experiment = None

		if len(sys.argv) == 3 and sys.argv[1] == '-csvmap':
			# Загрузка мира из CSV
			self.world = WorldGenerator.generate_world_fromCSV(
				file_path=sys.argv[2],
				random_wall_count=350, 
				food_count=sp.food_amount,
				creatures_count=500,
				border_walls=True,
			)
		else:
			# Генерация мира стандартным способом
			self.world = WorldGenerator.generate_world(
				width=100,
				height=50,
				wall_count=350, 
				food_count=sp.food_amount,
				creatures_count=500,
				border_walls=True,
			)
		

		self.renderer = Renderer(self.world, self)
		
		
	def run(self):

		print("/ Fucking go! /")
		
		while self.quit_flag == False:

			if self.experiment_mode:
				self.experiment.update()
				self.renderer.draw(self.experiment.get_experiment_dto())
				self.renderer.control_run()
			else:
				if self.is_running:
					self.world.update()
					self.world.update_map()
					if logme.is_enabled():
						logme.write_stats(self.world.creatures)
						logme.write_population_size(len(self.world.creatures))
					if self.animate_flag:
						self.renderer.draw(self.renderer._prepare_render_state_dto())
						self.renderer.control_run()
					else:
						self.renderer.control_run()
				else:
					self.renderer.draw(self.renderer._prepare_render_state_dto())
					self.renderer.control_run()
			

			

			self.performance_monitor.tick(self.world.tick)

		print("/ Terminated. /")

	def init_experiment(self, experiment_type: str, experimental_creature_id: int = None):
		"""
		Инициализировать эксперимент.
		
		Args:
			experiment_type: Тип эксперимента ('spambite', 'dummy', и т.д.)
			experimental_creature_id: ID существа для тестирования
		
		Процесс:
		1. Инициализировать эксперимент, передав тип, ID и объет world для доступа к данным мира
		3. Запустить эксперимент
		"""
		print(f"APPLICATION LEVEL: Initializing experiment: {experiment_type} on creature ID {experimental_creature_id}")
		from experiments import EXPERIMENTS
		
		# Инициализировать эксперимент с типом, ID и списком существ
		experiment_registry = EXPERIMENTS[experiment_type]
		experiment_class = experiment_registry['experiment_class']
		
		self.experiment = experiment_class(experimental_creature_id, self.world)
		self.world.get_creature_by_id(experimental_creature_id).nn.print_nn_parameters() # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
		self.experiment_mode = True
		self.is_running = False  # Остановить основную симуляцию
		
		# Запускаем эксперимент
		self.experiment.start()
		print(f"Experiment initialized and started")
		

	def start_experiment(self):
		pass
	
	def stop_experiment(self):
		pass
	
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

	def animation_off(self):
		"""Выключить анимацию"""
		self.animate_flag = False
	
	def animation_on(self):
		"""Включить анимацию"""
		self.animate_flag = True


	def save_world(self, save_file_name: str):
		"""Сохранить мир в слот.
		
		Args:
			save_file_name: Имя файла для сохранения
		"""
		world_persistence.save_world(self.world, save_file_name)
	
	def load_world(self, save_file_name: str):
		"""Загрузить мир из слота.
		
		Args:
			save_file_name: Имя файла для загрузки
		"""
		if world_persistence.load_world(self.world, save_file_name):
			self.is_running = False  # Остановить симуляцию на время загрузки

	def load_creatures(self, save_file_name: str):
		"""Загрузить из слота только существ и добавить в текущий мир.
		
		Args:
			save_file_name: Имя файла для загрузки
		"""
		if world_persistence.load_creatures_only(self.world, save_file_name):
			self.is_running = False  # Сохраняем поведение модального окна: после операции остаемся на паузе
	
	def reset_world(self):
		"""Сбросить мир."""
		print("✓ reset_world() called")
		# TODO: Реализовать сброс мира к его исходному состоянию
		self.is_running = False
	
	
	
	
	
	
	
	
	
	
	



	




