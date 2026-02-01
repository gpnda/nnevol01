# -*- coding: utf-8 -*-
"""
Dummy Experiment - простой базовый эксперимент для тестирования системы.

Назначение:
- Наблюдение за одним существом
- Сбор статистики поведения
- Проверка механизмов vision, bite, movement
"""

from experiments.base import ExperimentBase


class DummyExperiment(ExperimentBase):
    """
    Базовый dummy эксперимент.
    
    Логика:
    - Выбирается одно существо для наблюдения
    - Остальные существа также продолжают жить (параллельно)
    - Ведётся статистика по выбранному существу
    - Во время эксперимента симуляция работает в обычном режиме
    """
    
    def __init__(self, experiment_type: str, experimental_creature_id: int):
        """
        Инициализация dummy эксперимента.
        
        Args:
            experiment_type: Тип эксперимента (должен быть "dummy")
            experimental_creature_id: ID существа для наблюдения
        """
        self.experiment_type = experiment_type
        self.creature_id = experimental_creature_id
        self.is_running = False
        self.tick_counter = 0
        self.start_energy = None
        self.max_energy = None
        self.min_energy = None
        
        print(f"[EXPERIMENT] Dummy experiment initialized")
        print(f"  Type: {experiment_type}")
        print(f"  Target creature: {experimental_creature_id}")
    
    def start(self) -> None:
        """Запустить эксперимент."""
        self.is_running = True
        self.tick_counter = 0
        print(f"[EXPERIMENT] Starting dummy experiment on creature {self.creature_id}")
    
    def stop(self) -> None:
        """Остановить эксперимент."""
        self.is_running = False
        print(f"[EXPERIMENT] Stopping dummy experiment")
        self._print_stats()
    
    def update(self) -> None:
        """
        Основной метод обновления эксперимента.
        
        Вызывается каждый фрейм из application.run() если experiment_mode == True.
        Здесь должна быть логика сбора статистики и мониторинга.
        """
        if not self.is_running:
            return
        
        self.tick_counter += 1
        
        # Каждые 100 тиков выводим отладочную информацию
        if self.tick_counter % 100 == 0:
            print(f"[EXPERIMENT] Tick {self.tick_counter}: monitoring creature {self.creature_id}")
    
    def _print_stats(self) -> None:
        """Вывести статистику эксперимента."""
        print(f"[EXPERIMENT] Dummy experiment stats:")
        print(f"  Total ticks: {self.tick_counter}")
        print(f"  Target creature: {self.creature_id}")
        print(f"  Status: {'COMPLETED' if self.tick_counter > 0 else 'NOT STARTED'}")
