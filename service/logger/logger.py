# -*- coding: utf-8 -*-
from collections import deque, defaultdict
from typing import Dict, Deque, List, Any

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
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.energy_history: Dict[int, Deque[float]] = defaultdict(
                lambda: deque(maxlen=self.MAX_HISTORY)
            )
            
            # Словарь для хранения событий по ID существа
            # Ключ: ID существа, Значение: список событий (CreatureEvent)
            self.events_log: Dict[int, List[CreatureEvent]] = defaultdict(list)

            self._initialized = True
            


    def write_stats(self, creatures: List[Any]) -> None:
        for cr in creatures:
            self.energy_history[cr.id].append(float(cr.energy))
        
        self._cleanup_dead_creatures_stats()
                

    def _cleanup_dead_creatures_stats(self):
        # alive_ids = {cr.id for cr in self.creatures}
        # dead_ids = set(self.energy_history.keys()) - alive_ids # магиеская магия питона
        
        # for dead_id in dead_ids:
        #     del self.energy_history[dead_id]
        #     if dead_id in self.events_log:
        #         del self.events_log[dead_id]
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