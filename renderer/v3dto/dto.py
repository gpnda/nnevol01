# -*- coding: utf-8 -*-
"""
Data Transfer Objects (DTO) для Renderer v3dto.

DTO отделяют слой представления (Renderer) от доменной логики (World, Creature, Logger, Debugger).
Виджеты работают только с DTO и не знают о существовании world, logger и debugger синглтонов.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np


# ============================================================================
# DTO для существ
# ============================================================================

@dataclass
class CreatureDTO:
    """Data Transfer Object для отдельного существа.
    
    Содержит все поля существа, необходимые для отрисовки и отображения информации.
    """
    id: int
    x: float
    y: float
    angle: float
    energy: float
    age: int
    speed: float
    generation: int
    bite_effort: float
    vision_distance: float
    bite_range: float
    
    @classmethod
    def from_creature_id(cls, creature_id: int, creatures_list: list) -> 'CreatureDTO':
        """
        Фабрика для создания CreatureDTO из creature_id.
        
        Ищет существо в списке по ID и преобразует его в DTO.
        
        Args:
            creature_id: ID существа для поиска
            creatures_list: Список существ для поиска
        
        Returns:
            CreatureDTO: DTO найденного существа
        
        Raises:
            ValueError: Если существо с заданным ID не найдено
        """
        target_creature = None
        for creature in creatures_list:
            if creature.id == creature_id:
                target_creature = creature
                break
        
        if target_creature is None:
            raise ValueError(f"Creature with ID {creature_id} not found in creatures list")
        
        return cls(
            id=target_creature.id,
            x=target_creature.x,
            y=target_creature.y,
            angle=target_creature.angle,
            energy=target_creature.energy,
            age=target_creature.age,
            speed=target_creature.speed,
            generation=target_creature.generation,
            bite_effort=target_creature.bite_effort,
            vision_distance=target_creature.vision_distance,
            bite_range=target_creature.bite_range,
        )
    
    # Дополнительные вычисленные поля для UI
    @property
    def energy_percentage(self) -> float:
        """Энергия в процентах (0-100)."""
        return max(0, min(100, self.energy * 100))
    
    @property
    def age_days(self) -> int:
        """Возраст в условных днях (тики / 50)."""
        return self.age // 50 if self.age > 0 else 0


# ============================================================================
# DTO для мира
# ============================================================================

@dataclass
class FoodDTO:
    """Data Transfer Object для пищи."""
    x: float
    y: float
    energy: float


@dataclass
class WorldStateDTO:
    """Data Transfer Object для состояния мира.
    
    Содержит снимок состояния мира (map, creatures, foods) в момент времени.
    Используется для отрисовки viewport и других виджетов.
    """
    map: np.ndarray  # numpy array [height, width] с значениями: 0=пусто, 1=стена, 2=еда, 3=существо
    width: int
    height: int
    creatures: List[CreatureDTO]
    foods: List[FoodDTO]
    tick: int
    
    # Удобные методы для поиска
    def get_creature_by_id(self, creature_id: int) -> Optional[CreatureDTO]:
        """Найти существо по ID в текущем снимке."""
        for creature in self.creatures:
            if creature.id == creature_id:
                return creature
        return None
    
    def get_creature_at_position(self, x: int, y: int, radius: float = 1.0) -> Optional[int]:
        """Найти ID существа около позиции (x, y).
        
        Args:
            x, y: Координаты на карте
            radius: Радиус поиска
            
        Returns:
            ID существа или None
        """
        for creature in self.creatures:
            distance = ((creature.x - x) ** 2 + (creature.y - y) ** 2) ** 0.5
            if distance <= radius:
                return creature.id
        return None


# ============================================================================
# DTO для истории существа
# ============================================================================

@dataclass
class CreatureEventDTO:
    """Data Transfer Object для события в истории существа."""
    tick: int
    event_type: str  # "EAT_FOOD", "CREATE_CHILD", "COLLIDE_WALL", и т.д.
    value: Any


@dataclass
class CreatureHistoryDTO:
    """Data Transfer Object для истории существа.
    
    Содержит всю информацию о событиях и энергии существа за его жизнь.
    Используется для отрисовки графиков и истории SelectedCreatureHistory.
    """
    creature_id: int
    energy_history: List[float]  # История энергии [t=0, t=1, t=2, ...]
    events: List[CreatureEventDTO]  # Список событий с тиками
    
    @property
    def energy_min(self) -> float:
        """Минимальная энергия в истории."""
        return min(self.energy_history) if self.energy_history else 0.0
    
    @property
    def energy_max(self) -> float:
        """Максимальная энергия в истории."""
        return max(self.energy_history) if self.energy_history else 0.0
    
    @property
    def energy_current(self) -> float:
        """Текущая энергия (последнее значение в истории)."""
        return self.energy_history[-1] if self.energy_history else 0.0
    
    @property
    def lifespan(self) -> int:
        """Количество тиков жизни существа."""
        return len(self.energy_history)


# ============================================================================
# DTO для отладочной информации
# ============================================================================

@dataclass
class DebugDataDTO:
    """Data Transfer Object для отладочной информации.
    
    Содержит информацию из debugger синглтона для визуализации при отладке.
    """
    raycast_dots: Optional[np.ndarray] = None  # Точки raycasts для visualization
    all_visions: Optional[np.ndarray] = None   # Вся информация о виденном
    all_outs: Optional[np.ndarray] = None      # Выходы нейросетей
    
    def is_empty(self) -> bool:
        """Проверить, пусто ли множество отладочных данных."""
        return all(x is None for x in [self.raycast_dots, self.all_visions, self.all_outs])


# ============================================================================
# DTO для параметров симуляции
# ============================================================================

@dataclass
class SimulationParamsDTO:
    """Data Transfer Object для параметров симуляции.
    
    Содержит текущие значения всех параметров симуляции.
    Используется для отрисовки VariablesPanel.
    """
    # Мутация
    mutation_probability: float
    mutation_strength: float
    
    # Жизненный цикл
    creature_max_age: int
    
    # Еда
    food_amount: int
    food_energy_capacity: float
    food_energy_chunk: float
    
    # Размножение
    reproduction_ages: List[int]
    reproduction_offsprings: int
    
    # Энергия - затраты
    energy_cost_tick: float
    energy_cost_speed: float
    energy_cost_rotate: float
    energy_cost_bite: float
    
    # Энергия - получение
    energy_gain_from_food: float
    energy_gain_from_bite_cr: float
    
    # Энергия - потери
    energy_loss_bitten: float
    energy_loss_collision: float
    
    # Состояние симуляции
    is_running: bool
    is_animating: bool
    is_logging: bool
    
    # Мутации
    allow_mutations: int


# ============================================================================
# DTO для выбранного существа (полная информация для панели)
# ============================================================================

@dataclass
class SelectedCreaturePanelDTO:
    """Data Transfer Object для информации выбранного существа (полная версия для панели).
    
    Объединяет CreatureDTO и CreatureHistoryDTO для удобства отрисовки.
    """
    creature: CreatureDTO
    history: Optional[CreatureHistoryDTO] = None
    
    @property
    def is_valid(self) -> bool:
        """Проверить, валидны ли данные о существе."""
        return self.creature is not None


# ============================================================================
# DTO для состояния рендеринга
# ============================================================================

@dataclass
class RenderStateDTO:
    """Data Transfer Object для состояния рендеринга.
    
    Используется для передачи полного снимка состояния всем виджетам
    в методе Renderer.draw().
    
    ВАЖНО: experiment_dto НЕ находится здесь!
    Экспериментальные данные передаются отдельно в _draw_experiment().
    """
    # Основное состояние мира
    world: WorldStateDTO
    
    # Параметры симуляции
    params: SimulationParamsDTO
    
    # Отладочная информация
    debug: DebugDataDTO
    
    # Текущее выбранное существо и его история
    selected_creature: Optional[SelectedCreaturePanelDTO] = None
    
    # Текущее состояние рендеринга
    current_state: str = 'main'  # 'main', 'popup_simparams', 'creatures_list', и т.д.
    tick: int = 0
    fps: int = 0
    
    @property
    def population_count(self) -> int:
        """Количество живых существ."""
        return len(self.world.creatures)
    
    @property
    def food_count(self) -> int:
        """Количество пищи на карте."""
        return len(self.world.foods)
    
    @property
    def is_selected_alive(self) -> bool:
        """Проверить, живо ли выбранное существо."""
        if self.selected_creature is None:
            return False
        return self.selected_creature.creature in self.world.creatures
