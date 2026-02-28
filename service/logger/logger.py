# -*- coding: utf-8 -*-
from collections import deque, defaultdict
from typing import Dict, Deque, List, Any, Tuple
import numpy as np

# Опишем структуру данных для ханения исторической информации о поколениях, смертях, 
# а также о возрастах размножения каждого существа
# эти данные позволят опредялять качественные характеристики отбора
INT32 = np.int32
FLOAT32 = np.float32
dtype_population_data = np.dtype([
    ('id', INT32),
    ('generation', INT32),
    ('age', INT32),
    ('reprod_ages', INT32, (3,))
])



class CreatureEvent:
    """Событие в истории существа (поедание, размножение и т.д.)"""
    
    def __init__(self, creature_id: int, tick_number: int, event_type: str, value: Any):
        self.creature_id = creature_id
        self.tick_number = tick_number
        self.event_type = event_type  # "EAT_FOOD", "CREATE_CHILD", и т.д.
        self.value = value
    
    def __repr__(self) -> str:
        return f"CreatureEvent(id={self.creature_id}, tick={self.tick_number}, type={self.event_type}, value={self.value})"


class Logger:
    
    _instance = None
    MAX_HISTORY = 1000  # Максимальное количество сохраняемых тиков
    MAX_POPULATION_HISTORY = 1500  # Максимальное количество сохраняемых значений численности популяции
    MAX_DEATH_STATS = 200  # Максимальное количество сохраняемых записей о смертях
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):

            self._enabled = True  # Флаг для включения/отключения логирования

            # Словарь для хранения истории энергии по ID существа
            # Ключ: ID существа, Значение: очередь значений энергии (float)
            self.energy_history: Dict[int, Deque[float]] = defaultdict(
                lambda: deque(maxlen=self.MAX_HISTORY)
            )
            
            # Словарь для хранения событий по ID существа
            # Ключ: ID существа, Значение: список событий (CreatureEvent)
            self.events_log: Dict[int, List[CreatureEvent]] = defaultdict(list)

            # История численности популяции (хранит только последние MAX_POPULATION_HISTORY значений)
            self.population_size: Deque[int] = deque(maxlen=self.MAX_POPULATION_HISTORY)

            # История смертей (хранит только последние MAX_DEATH_STATS записей)
            self.death_stats: Deque[Tuple] = deque(maxlen=self.MAX_DEATH_STATS)

            # Пометка об инициализации
            self._initialized = True
    









    def is_enabled(self) -> bool:
        """Проверить, включено ли логирование."""
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Включить/выключить логирование."""
        if self._enabled and not enabled:
            # При отключении очистить все данные
            self.clear_all()
        self._enabled = enabled

    def clear_all(self) -> None:
        """Очистить все собранные данные."""
        self.energy_history.clear()
        self.events_log.clear()
        self.population_size.clear()
        self.death_stats.clear()









    def write_stats(self, creatures: List[Any]) -> None:
        for cr in creatures:
            self.energy_history[cr.id].append(float(cr.energy))
        
        self._cleanup_dead_creatures_stats(creatures)

    def write_population_size(self, size: int) -> None:
        self.population_size.append(size)

    def write_death_stats(self, id: int, generation: int, age: int, reprod_ages: list) -> None:
        self.death_stats.append((id, generation, age, reprod_ages))
    
    def get_death_stats_as_ndarray(self):
        data_array = np.array(self.death_stats, dtype=dtype_population_data)
        return data_array
    
    def get_population_size_history_as_list(self) -> List[int]:
        return list(self.population_size)

    def _cleanup_dead_creatures_stats(self, alive_creatures: List[Any]) -> None:
        """
        Удаляет статистику об умерших существах.
        
        Из историй energy_history и events_log удаляются существа,
        которые больше не присутствуют в списке живых.
        
        Args:
            alive_creatures: Список живых существ
        """
        alive_ids = {cr.id for cr in alive_creatures}
        dead_ids = set(self.energy_history.keys()) - alive_ids
        
        for dead_id in dead_ids:
            self.energy_history.pop(dead_id, None)
            self.events_log.pop(dead_id, None)
        pass
        
    
    def get_creature_energy_history(self, creature_id: int) -> list:
        """
        Получить всю историю энергии одного существа по sID.
        
        Args:
            creature_id: ID существа.
        
        Returns:
            list: список значений энергии (float) для каждого тика.
        """
        return list(self.energy_history.get(creature_id, []))

    
    def log_event(self, creature_id: int, tick: int, event_type: str, value: Any) -> None:
        """
        Логировать событие для существа с текущим номером тика.
        
        Args:
            creature_id: ID существа.
            event_type: Тип события ("EAT_FOOD", "CREATE_CHILD", и т.д.).
            value: Значение события (например, количество энергии).
        
        Example:
            logger.log_event(creature_id=65, tick=100, event_type="EAT_FOOD", value=10)
        """
        event = CreatureEvent(creature_id, tick, event_type, value)
        self.events_log[creature_id].append(event)
    
    
    def get_creature_events(self, creature_id: int) -> List[CreatureEvent]:
        """
        Получить все события для существа.
        
        Args:
            creature_id: ID существа.
        
        Returns:
            List[CreatureEvent]: список всех событий существа.
        
        Example:
            events = logger.get_creature_events(65)
        """
        return self.events_log.get(creature_id, [])
    
    
    def get_creature_events_by_type(self, creature_id: int, event_type: str) -> List[CreatureEvent]:
        """
        Получить события определенного типа для существа.
        
        Args:
            creature_id: ID существа.
            event_type: Тип события для фильтрации.
        
        Returns:
            List[CreatureEvent]: список событий заданного типа.
        
        Example:
            food_events = logger.get_creature_events_by_type(65, "EAT_FOOD")
        """
        events = self.events_log.get(creature_id, [])
        return [e for e in events if e.event_type == event_type]
    
    
    def get_events_count(self, creature_id: int, event_type: str = None) -> int:
        """
        Получить количество событий для существа (опционально - по типу).
        
        Args:
            creature_id: ID существа.
            event_type: Тип события (опционально). Если None, считаются все события.
        
        Returns:
            int: количество событий.
        
        Example:
            total_events = logger.get_events_count(65)
            food_eaten = logger.get_events_count(65, "EAT_FOOD")
        """
        if event_type is None:
            return len(self.events_log.get(creature_id, []))
        return len(self.get_creature_events_by_type(creature_id, event_type))
    
    


logme = Logger()