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
		self.performance_monitor = PerformanceMonitor(self)
		self.experiment_mode = False
		self.experiment = None

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

			if self.experiment_mode:
				self.experiment.update()
				self.renderer.draw()
				self.renderer.control_run()
			else:
				if self.is_running:
					self.world.update()
					self.world.update_map()
					if logme.is_enabled():
						logme.write_stats(self.world.creatures)
						logme.write_population_size(len(self.world.creatures))
					if self.animate_flag:
						self.renderer.draw()
						self.renderer.control_run()
					else:
						self.renderer.control_run()
				else:
					self.renderer.draw()
					self.renderer.control_run()
			
			#self.limit_fps()

			

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
	
	
	
	
	
	
	
	
	
	
	



	




