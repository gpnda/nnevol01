# -*- coding: utf-8 -*-
"""
SpambiteExperiment DTO - передача данных для виджета.

Data Transfer Object для SpambiteExperiment.
Содержит все данные, необходимые для отрисовки виджета.
Полностью изолирована от singleton'ов (world, logger, debugger).
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from renderer.v3dto.dto import WorldStateDTO, CreatureDTO


@dataclass
class SpambiteExperimentDTO:
    """
    Data Transfer Object для SpambiteExperiment.
    
    Передает все необходимые данные из experiment в widget.
    Widget получает этот DTO через render_state.experiment_dto.
    """
    
    # Состояние мира эксперимента
    world_state: Optional[WorldStateDTO]
    
    # Данные целевого существа
    creature_dto: Optional[CreatureDTO]
    
    # Позиции пищи (список кортежей (x, y))
    food_positions: List[Tuple[float, float]]
    
    # Статистика итераций
    current_iteration: int  # 1-20
    total_iterations: int   # обычно 20
    
    # Счет успехов и неудач
    successes: int
    failures: int
    
    # Текущее состояние в итерации
    frames_in_iteration: int
    
    # Опциональная отладочная информация
    debug_message: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Процент успеха (0-100)."""
        total = self.successes + self.failures
        return (self.successes / total * 100) if total > 0 else 0.0
    
    @property
    def iteration_progress(self) -> float:
        """Прогресс текущей итерации (0-1)."""
        return self.frames_in_iteration / 300.0  # MAX_FRAMES_PER_ITERATION = 300
