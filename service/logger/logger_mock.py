# -*- coding: utf-8 -*-
"""
Mock Logger for testing and development purposes.
Provides the same interface as the real Logger but does nothing.
"""
from typing import List, Any
import numpy as np


class CreatureEvent:
    """Mock событие в истории существа (пустышка)"""
    
    def __init__(self, creature_id: int, tick_number: int, event_type: str, value: Any):
        self.creature_id = creature_id
        self.tick_number = tick_number
        self.event_type = event_type
        self.value = value
    
    def __repr__(self) -> str:
        return f"CreatureEvent(id={self.creature_id}, tick={self.tick_number}, type={self.event_type}, value={self.value})"


class Logger:
    """
    Mock-версия Logger. Предоставляет тот же интерфейс, но не выполняет реальных операций.
    Используется для тестирования или отключения логирования.
    """
    
    _instance = None
    MAX_HISTORY = 1000
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        
        if not hasattr(self, '_initialized'):
            self._initialized = True
    
    def write_stats(self, creatures: List[Any]) -> None:
        """Mock: записывает статистику (ничего не делает)"""
        pass
    
    def write_population_size(self, size: int) -> None:
        """Mock: записывает размер популяции (ничего не делает)"""
        pass
    
    def write_death_stats(self, id: int, generation: int, age: int, reprod_ages: list) -> None:
        """Mock: записывает статистику смертей (ничего не делает)"""
        pass
    
    def get_death_stats_as_ndarray(self):
        """Mock: возвращает пустой массив статистики смертей"""
        dtype_population_data = np.dtype([
            ('id', np.int32),
            ('generation', np.int32),
            ('age', np.int32),
            ('reprod_ages', np.int32, (3,))
        ])
        return np.array([], dtype=dtype_population_data)
    
    def get_population_size_history_as_list(self) -> List[int]:
        return []

    def get_creature_energy_history(self, creature_id: int) -> list:
        """Mock: возвращает пустую историю энергии"""
        return []
    
    def log_event(self, creature_id: int, tick: int, event_type: str, value: Any) -> None:
        """Mock: логирует событие (ничего не делает)"""
        pass
    
    def get_creature_events(self, creature_id: int) -> List[CreatureEvent]:
        """Mock: возвращает пустой список событий"""
        return []
    
    def get_creature_events_by_type(self, creature_id: int, event_type: str) -> List[CreatureEvent]:
        """Mock: возвращает пустой список событий по типу"""
        return []
    
    def get_events_count(self, creature_id: int, event_type: str = None) -> int:
        """Mock: возвращает 0 событий"""
        return 0


# Синглтон mock logger (аналог logme из оригинального logger.py)
logme = Logger()
