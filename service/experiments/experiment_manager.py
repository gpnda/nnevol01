# -*- coding: utf-8 -*-
"""
ExperimentManager - управление изолированными экспериментами.

Логика:
- Запускается когда пользователь переходит в режим эксперимента
- Берет снимок мира/существа
- Проводит эксперимент в изоляции
- Собирает метрики
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from copy import deepcopy
import math


# ============================================================================
# DTO для результатов эксперимента
# ============================================================================

@dataclass
class ExperimentMetricsDTO:
    """Метрики одного момента времени в эксперименте."""
    tick: int
    energy: float
    position: tuple                # (x, y)
    angle: float
    speed: float
    events: List[str] = field(default_factory=list)


@dataclass
class ExperimentResultDTO:
    """
    DTO для передачи результатов эксперимента в UI через RenderStateDTO.
    
    Это только данные, управление происходит через callbacks в Renderer.
    """
    status: str                                # "running", "completed", "stopped"
    current_tick: int
    total_ticks: int
    is_alive: bool
    
    # Текущее состояние
    current_energy: float
    current_position: tuple
    
    # История
    energy_history: List[float] = field(default_factory=list)
    position_history: List[tuple] = field(default_factory=list)
    metrics_history: List[ExperimentMetricsDTO] = field(default_factory=list)
    
    # Итоги
    total_energy_consumed: float = 0.0
    total_distance_traveled: float = 0.0
    events_count: Dict[str, int] = field(default_factory=dict)
    
    @property
    def progress_percent(self) -> float:
        """Прогресс в процентах (0-100)."""
        if self.total_ticks <= 0:
            return 0.0
        return (self.current_tick / self.total_ticks) * 100.0


# ============================================================================
# Внутренние классы для управления экспериментом
# ============================================================================

class ExperimentState:
    """Состояние одного запущенного эксперимента."""
    
    def __init__(self, world_snapshot, duration_ticks: int):
        """
        Инициализировать эксперимент.
        
        Args:
            world_snapshot: Снимок мира для эксперимента (deepcopy)
            duration_ticks: Максимальное количество тиков
        """
        self.world_snapshot = world_snapshot
        self.duration_ticks = duration_ticks
        
        self.current_tick = 0
        self.is_alive = True
        
        # История метрик
        self.energy_history: List[float] = []
        self.position_history: List[tuple] = []
        self.metrics_history: List[ExperimentMetricsDTO] = []
        
        # События
        self.events: Dict[str, int] = {}
        
        # Стартовое состояние
        self.start_energy = sum(cr.energy for cr in world_snapshot.creatures)
        self.last_world_state = None
    
    def tick(self) -> bool:
        """
        Один тик эксперимента.
        
        Returns:
            True если нужно продолжать, False если эксперимент должен завершиться
        """
        self.current_tick += 1
        
        # Проверка: закончилось ли время
        if self.current_tick >= self.duration_ticks:
            self.is_alive = False
            return False
        
        # Проверка: есть ли еще существа
        if len(self.world_snapshot.creatures) == 0:
            self.is_alive = False
            return False
        
        # Обновить мир в эксперименте
        self._update_snapshot()
        
        # Собрать метрики
        self._collect_metrics()
        
        return True
    
    def _update_snapshot(self):
        """Обновить снимок мира (запустить одну итерацию)."""
        # Обновить мир
        self.world_snapshot.update()
        self.world_snapshot.update_map()
        
        # Сохранить предыдущее состояние
        self.last_world_state = self.world_snapshot
    
    def _collect_metrics(self):
        """Собрать метрики текущего состояния."""
        if len(self.world_snapshot.creatures) == 0:
            self.is_alive = False
            return
        
        # Суммировать энергию по всем существам
        total_energy = sum(cr.energy for cr in self.world_snapshot.creatures)
        avg_position = self._calculate_avg_position()
        
        self.energy_history.append(total_energy)
        self.position_history.append(avg_position)
    
    def _calculate_avg_position(self) -> tuple:
        """Вычислить среднюю позицию всех существ."""
        if not self.world_snapshot.creatures:
            return (0, 0)
        
        avg_x = sum(cr.x for cr in self.world_snapshot.creatures) / len(self.world_snapshot.creatures)
        avg_y = sum(cr.y for cr in self.world_snapshot.creatures) / len(self.world_snapshot.creatures)
        return (avg_x, avg_y)
    
    def get_total_distance(self) -> float:
        """Общее пройденное расстояние (по средней позиции)."""
        total = 0.0
        for i in range(1, len(self.position_history)):
            p1, p2 = self.position_history[i-1], self.position_history[i]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            total += math.sqrt(dx*dx + dy*dy)
        return total


# ============================================================================
# ExperimentManager - главный класс
# ============================================================================

class ExperimentManager:
    """
    Менеджер экспериментов.
    
    Логика:
    1. start_experiment() - запустить эксперимент на копии мира
    2. update() - один тик эксперимента (вызывается из Application.run())
    3. stop_experiment() - остановить и вернуть результаты
    4. get_current_result() - получить текущий результат в виде DTO
    """
    
    def __init__(self):
        """Инициализировать менеджер экспериментов."""
        self.active_experiment: Optional[ExperimentState] = None
        self.duration_ticks: int = 500
    
    def start_experiment(self, world, duration_ticks: int = 500) -> bool:
        """
        Запустить новый эксперимент.
        
        Args:
            world: Объект World для эксперимента (будет скопирован)
            duration_ticks: Длительность эксперимента в тиках
        
        Returns:
            True если успешно запущен, False если ошибка
        """
        if self.active_experiment is not None:
            print("[ExperimentManager] Error: эксперимент уже запущен!")
            return False
        
        try:
            # Создать глубокую копию мира
            world_copy = deepcopy(world)
            
            # Создать объект эксперимента
            self.active_experiment = ExperimentState(world_copy, duration_ticks)
            self.duration_ticks = duration_ticks
            
            print(f"[ExperimentManager] Запущен эксперимент")
            print(f"  Длительность: {duration_ticks} тиков")
            print(f"  Существ: {len(world_copy.creatures)}")
            print(f"  Стартовая общая энергия: {self.active_experiment.start_energy:.2f}")
            
            return True
        
        except Exception as e:
            print(f"[ExperimentManager] Error при создании копии мира: {e}")
            self.active_experiment = None
            return False
    
    def update(self) -> Optional[ExperimentResultDTO]:
        """
        Обновить активный эксперимент на один тик.
        
        Вызывается из Application.run() когда experiment_mode = True.
        
        Returns:
            ExperimentResultDTO с текущим состоянием, или None если нет активного
        """
        if self.active_experiment is None:
            return None
        
        # Один тик эксперимента
        should_continue = self.active_experiment.tick()
        
        # Получить текущий результат
        result = self._prepare_result_dto()
        
        # Если эксперимент завершился, очистить
        if not should_continue:
            print(f"[ExperimentManager] Эксперимент завершен!")
            print(f"  Финальная энергия: {result.current_energy:.2f}")
            print(f"  Пройденная дистанция: {result.total_distance_traveled:.2f}")
            self.active_experiment = None
        
        return result
    
    def stop_experiment(self) -> Optional[ExperimentResultDTO]:
        """
        Остановить активный эксперимент (пользователь нажал stop).
        
        Returns:
            Финальный результат, или None если не было активного
        """
        if self.active_experiment is None:
            return None
        
        result = self._prepare_result_dto()
        result.status = "stopped"
        
        print(f"[ExperimentManager] Эксперимент остановлен пользователем!")
        self.active_experiment = None
        
        return result
    
    def get_current_result(self) -> Optional[ExperimentResultDTO]:
        """
        Получить текущий результат (для UI без обновления).
        
        Returns:
            ExperimentResultDTO или None
        """
        if self.active_experiment is None:
            return None
        
        return self._prepare_result_dto()
    
    def is_active(self) -> bool:
        """Есть ли активный эксперимент."""
        return self.active_experiment is not None
    
    def _prepare_result_dto(self) -> ExperimentResultDTO:
        """Преобразовать внутреннее состояние в DTO."""
        exp = self.active_experiment
        
        if not exp.world_snapshot.creatures:
            current_energy = 0.0
            current_position = (0, 0)
        else:
            current_energy = sum(cr.energy for cr in exp.world_snapshot.creatures)
            current_position = self._calculate_avg_position()
        
        status = "running"
        if not exp.is_alive:
            status = "completed"
        
        return ExperimentResultDTO(
            status=status,
            current_tick=exp.current_tick,
            total_ticks=exp.duration_ticks,
            is_alive=exp.is_alive,
            
            # Текущее состояние
            current_energy=current_energy,
            current_position=current_position,
            
            # История
            energy_history=exp.energy_history[:],
            position_history=exp.position_history[:],
            metrics_history=exp.metrics_history[:],
            
            # Итоги
            total_energy_consumed=exp.start_energy - current_energy,
            total_distance_traveled=exp.get_total_distance(),
            events_count=exp.events.copy()
        )
    
    def _calculate_avg_position(self) -> tuple:
        """Вычислить среднюю позицию всех существ в активном эксперименте."""
        if not self.active_experiment or not self.active_experiment.world_snapshot.creatures:
            return (0, 0)
        
        creatures = self.active_experiment.world_snapshot.creatures
        avg_x = sum(cr.x for cr in creatures) / len(creatures)
        avg_y = sum(cr.y for cr in creatures) / len(creatures)
        return (avg_x, avg_y)
