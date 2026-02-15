# -*- coding: utf-8 -*-
"""
StagedExperimentBase - базовый класс для многостадийных экспериментов.

Архитектура:
- Каждая стадия = отдельный метод _stage_N()
- State machine переключает стадии через self.current_stage
- Каждая стадия выполняет серию прогонов
- Финальная стадия = резюме результатов
"""

from abc import ABC, abstractmethod
from experiments.base import ExperimentBase
from world import World

class StagedExperimentBase(ExperimentBase, ABC):
    """
    Базовый класс для стадийных экспериментов.
    
    Наследники должны определить:
    - _stage_0(), _stage_1(), ..., _stage_N(): логика каждой стадии
    - _get_total_stages(): общее количество стадий
    """
    
    def __init__(self, target_creature_id: int, world: World):
        super().__init__()
        
        # Захватываем данные из основного мира
        self.original_world = world
        
        self.target_creature = None
        for creature in world.creatures:
            if creature.id == target_creature_id:
                self.target_creature = creature
                break
        
        if self.target_creature is None:
            raise ValueError(f"Creature {target_creature_id} not found")
        
        
        # State machine
        self.current_stage = 0
        self.num_runs_this_stage = 0  # для контроля количества прогонов в каждой стадии
        self.stage_run_counter = 0  # счетчик прогонов внутри стадии

        
        self.is_running = False
    
    @abstractmethod
    def _get_total_stages(self) -> int:
        """Вернуть общее количество стадий (включая финальную)."""
        pass
    
    @abstractmethod
    def _stage_0(self):
        """Логика стадии 0."""
        pass
    
    def start(self):
        """Запустить эксперимент."""
        self.is_running = True
        self.current_stage = 0
        self.stage_run_counter = 0
        print(f"[STAGED EXPERIMENT] Started")
    
    def stop(self):
        """Остановить эксперимент."""
        self.is_running = False
        print(f"[STAGED EXPERIMENT] Stopped")
        self._print_summary()
    
    def update(self):
        """Основной цикл обновления."""
        if not self.is_running:
            return
        
        # State machine: вызвать метод текущей стадии
        # С проверкой, что стадия существует (вдруг не имплементирована)
        stage_method = getattr(self, f'_stage_{self.current_stage}', None)
        if stage_method is None:
            print(f"[ERROR] Stage {self.current_stage} not implemented")
            self.stop()
            return
        
        # выполнить логику стадии
        stage_method()

        # увеличить счетчик прогонов внутри стадии и перейти к следующей стадии, если достигнут лимит
        self.stage_run_counter_increment()
        
    
    def stage_run_counter_increment(self):
        """Увеличить счетчик прогонов внутри стадии и перейти к следующей стадии, если достигнут лимит."""
        self.stage_run_counter += 1
        
        if self.stage_run_counter >= self.num_runs_this_stage:
            # Переход к следующей стадии
            self.stage_run_counter = 0   # сбросить счетчик для следующей стадии
            self.current_stage += 1      # перейти к следующей стадии
        
            # Если все стадии завершены, то
            if self.current_stage >= self._get_total_stages():
                self.stop()

    def _print_summary(self):
        """Вывести резюме результатов."""
        print(f"[STAGED EXPERIMENT] Summary for creature {self.target_creature.id}")
        # Здесь можно вывести какие-то общие результаты, например, финальную энергию, 
        # количество съеденной пищи, количество укусов и так далее, в зависимости от логики эксперимента

    
