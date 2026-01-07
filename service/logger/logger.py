# -*- coding: utf-8 -*-
from collections import deque, defaultdict
from typing import Dict, Deque

class Logger:
    
    _instance = None
    MAX_HISTORY = 1000  # Максимальное количество сохраняемых тиков
    
    def __new__(cls, world=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, world=None):
        if not hasattr(self, '_initialized'):
            if world is None:
                raise ValueError("Logger requires world object on first initialization")
            self.creatures = world.creatures
            self.energy_history: Dict[int, Deque[float]] = defaultdict(
                lambda: deque(maxlen=self.MAX_HISTORY)
            )
            self._initialized = True



    def write_stats(self):
        for cr in self.creatures:
            self.energy_history[cr.id].append(float(cr.energy))
        
        self._cleanup_dead_creatures_stats()
                

    def _cleanup_dead_creatures_stats(self):
        alive_ids = {cr.id for cr in self.creatures}
        dead_ids = set(self.energy_history.keys()) - alive_ids # магиеская магия питона
        
        for dead_id in dead_ids:
            del self.energy_history[dead_id]
        
    
    def get_creature_energy_history(self, creature_id: int) -> list:
        """
        Получить всю историю энергии одного существа по sID.
        
        Args:
            creature_id: ID существа.
        
        Returns:
            list: список значений энергии (float) для каждого тика.
        """
        return list(self.energy_history.get(creature_id, []))

    
    