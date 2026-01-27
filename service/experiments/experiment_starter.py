# -*- coding: utf-8 -*-
"""
ExperimentStarter - управление экспериментами.

Запускает и контролирует эксперименты, изолированные от основной симуляции.
Вызывается из Application в режиме experiment_mode.
"""

from typing import Optional
from copy import deepcopy
from service.logger.logger import logme


class ExperimentStarter:
    """Управление одним экспериментом за раз."""
    
    def __init__(self):
        """Инициализация."""
        self.active_experiment: Optional['Experiment'] = None
        self.is_running = False
    
    def start_experiment(self, world) -> None:
        """
        Запустить эксперимент.
        
        Args:
            world: World объект для копирования состояния
        """
        if self.active_experiment is not None:
            print("[ExperimentStarter] Error: эксперимент уже запущен!")
            return
        
        try:
            # Создать копию мира для эксперимента
            world_copy = deepcopy(world)
            
            # Создать объект эксперимента
            self.active_experiment = Experiment(world_copy)
            self.is_running = True
            
            print(f"[ExperimentStarter] Эксперимент запущен")
            print(f"  Существ: {len(world_copy.creatures)}")
            print(f"  Еды: {len(world_copy.foods)}")
            
        except Exception as e:
            print(f"[ExperimentStarter] Error: {e}")
            self.active_experiment = None
            self.is_running = False
    
    def update(self) -> None:
        """
        Обновить активный эксперимент на один тик.
        
        Вызывается из Application.run() когда experiment_mode=True.
        """
        if self.active_experiment is None:
            return
        
        # Один тик эксперимента
        self.active_experiment.world.update()
        self.active_experiment.world.update_map()
        self.active_experiment.tick_count += 1
        
        # Проверка завершения эксперимента
        should_continue = self._check_experiment_status()
        
        if not should_continue:
            self._finish_experiment()
    
    def stop_experiment(self) -> None:
        """Остановить текущий эксперимент."""
        if self.active_experiment is None:
            return
        
        print(f"[ExperimentStarter] Эксперимент остановлен")
        print(f"  Тиков: {self.active_experiment.tick_count}")
        print(f"  Выживших существ: {len(self.active_experiment.world.creatures)}")
        
        self.active_experiment = None
        self.is_running = False
    
    def is_active(self) -> bool:
        """Есть ли активный эксперимент."""
        return self.active_experiment is not None and self.is_running
    
    def _check_experiment_status(self) -> bool:
        """
        Проверить статус эксперимента.
        
        Returns:
            True если нужно продолжать, False если завершить
        """
        if self.active_experiment is None:
            return False
        
        # Условия завершения
        # 1. Все существа мертвы
        if len(self.active_experiment.world.creatures) == 0:
            print("[ExperimentStarter] Эксперимент завершен: все существа мертвы")
            return False
        
        # 2. Максимальное время (если нужно)
        max_ticks = 10000  # TODO: сделать конфигурируемым
        if self.active_experiment.tick_count >= max_ticks:
            print(f"[ExperimentStarter] Эксперимент завершен: достигнут лимит {max_ticks} тиков")
            return False
        
        return True
    
    def _finish_experiment(self) -> None:
        """Завершить эксперимент и собрать результаты."""
        if self.active_experiment is None:
            return
        
        exp = self.active_experiment
        
        print(f"\n[ExperimentStarter] === Итоги эксперимента ===")
        print(f"  Длительность: {exp.tick_count} тиков")
        print(f"  Выживших существ: {len(exp.world.creatures)}")
        print(f"  Пищи на карте: {len(exp.world.foods)}")
        
        # Сбор статистики (если нужно)
        if len(exp.world.creatures) > 0:
            avg_energy = sum(c.energy for c in exp.world.creatures) / len(exp.world.creatures)
            print(f"  Средняя энергия выживших: {avg_energy:.2f}")
        
        print("=" * 40 + "\n")
        
        self.active_experiment = None
        self.is_running = False
    
    def get_experiment_state(self) -> Optional[dict]:
        """
        Получить текущее состояние эксперимента (для UI).
        
        Returns:
            Словарь с информацией или None
        """
        if self.active_experiment is None:
            return None
        
        exp = self.active_experiment
        
        return {
            'tick_count': exp.tick_count,
            'creatures_count': len(exp.world.creatures),
            'foods_count': len(exp.world.foods),
            'world_map': exp.world.map,
            'world': exp.world
        }


class Experiment:
    """Один запущенный эксперимент."""
    
    def __init__(self, world_copy):
        """
        Инициализировать эксперимент.
        
        Args:
            world_copy: Копия мира для изолированного эксперимента
        """
        self.world = world_copy
        self.tick_count = 0
        
        # Метрики (для будущей аналитики)
        self.max_creatures_count = len(world_copy.creatures)
        self.start_population = len(world_copy.creatures)
