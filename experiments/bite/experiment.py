# -*- coding: utf-8 -*-
"""
Bite Experiment - проверка правильности кусания в различных сценариях.

Стадии:
0. Пища впритык (должен кусать)
1. Пища не видна (не должен кусать)
2. Пища далеко по центру (не должен кусать)
3. Пища близко, но вне досягаемости (не должен кусать)
4. Пища чуть правее (не должен кусать)
5. Пища чуть левее (не должен кусать)
6. Резюме результатов (финальная стадия)
"""

import random
import math
from experiments.base.staged_experiment_base import StagedExperimentBase
from experiments.bite.dto import BiteExperimentDTO
from world import World

class BiteExperiment(StagedExperimentBase):
    """Эксперимент проверки кусания."""

    def __init__(self, target_creature_id: int, world: World):
        super().__init__(target_creature_id, world)

        # Инициализация переменных специфичные для BiteExperiment
        self.random_value = 0.0
    
    def _get_total_stages(self) -> int:
        return 7  # 6 тестовых стадий + 1 финальная
    
    def _stage_0(self):
        """Стадия 0: Пища впритык (залито красным)."""
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
        
    def _stage_1(self):
        """Стадия 1: Пища не видна."""
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_2(self):
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_3(self):
        """Стадия 3: Пища близко, но вне досягаемости."""
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_4(self):
        """Стадия 4: Пища чуть правее."""
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_5(self):
        """Стадия 5: Пища чуть левее."""
        
        # Заглушка для проверки успеха
        success = random.random() > 0.1
    
    def _stage_6(self):
        """Стадия 6: Резюме (финальная стадия)."""
        # Ничего не делаем, просто завершаем
        pass
    
    def get_experiment_dto(self):
        """Вернуть DTO для виджета."""
        #summary = self.stats.get_summary()
        return BiteExperimentDTO(
            creature_id=self.target_creature.id,
            is_running=self.is_running,
            current_stage=self.current_stage,
            stage_run_counter=self.stage_run_counter,
            random_value=self.random_value
        )
