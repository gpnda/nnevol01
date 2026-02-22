# -*- coding: utf-8 -*-
"""
Toolbox для экспериментов - набор утилит для создания контролируемых сценариев.

Содержит:
- StatsCollector: универсальный сборщик статистики по прогонам с поддержкой произвольных метрик

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
======================

1. Базовое использование - собрать статистику к успеху/неудаче:
    stats = StatsCollector()
    stats.add_run(stage=1, success=True, metric1=0.85, metric2=10)
    stats.add_run(stage=1, success=False, metric1=0.42, metric2=5)
    summary = stats.get_summary()

2. С произвольными метриками:
    stats = StatsCollector()
    stats.add_run(
        stage=1,
        success=True,
        bite_accuracy=0.85,
        energy_consumed=15,
        vision_quality=0.92,
        reaction_time=50,
    )
    
3. Анализ конкретной метрики:
    energy_stats = stats.get_metric_stats(stage=1, metric_name='energy_consumed')
    print(f"Avg energy: {energy_stats['avg']:.2f}, max: {energy_stats['max']}")
    # Output: Avg energy: 15.50, max: 28

4. Узнать все доступные метрики:
    all_metrics = stats.get_all_metrics_names()
    print(f"Available: {all_metrics}")
    # Output: Available: {'bite_accuracy', 'energy_consumed', 'vision_quality', 'reaction_time'}

5. Сравнение метрик между стадиями:
    stage1_metric = stats.get_metric_stats(stage=1, metric_name='reaction_time')
    stage2_metric = stats.get_metric_stats(stage=2, metric_name='reaction_time')
    print(f"Stage 1: {stage1_metric['avg']:.0f}±{stage1_metric['std']:.0f}, Stage 2: {stage2_metric['avg']:.0f}±{stage2_metric['std']:.0f}")
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from world import World
from world_generator import WorldGenerator
from creature import Creature
from food import Food
from nn.my_handmade_ff import NeuralNetwork



class ScenarioBuilder:
    """Построитель контролируемых сценариев для экспериментов."""
    
    @staticmethod
    def create_test_world(width: int = 10, height: int = 10) -> World:
        """Создать пустой тестовый мир с правильной инициализацией."""
        # Используем WorldGenerator с нулевыми параметрами для правильной инициализации walls_map
        world = WorldGenerator.generate_world(width, height, wall_count=0, food_count=0, creatures_count=0)
        return world
    
    @staticmethod
    def copy_creature(creature: Creature) -> Creature:
        """Создать новое чистое существо. Скопировать к него нейронную сеть, используя собственный метод нейронной сети"""
        new_creature = Creature(x=1, y=1)  # позиция будет переопределена при размещении
        new_creature.nn = NeuralNetwork.copy(creature.nn)  # используем метод копирования из класса NeuralNetwork
        return new_creature

    
    @staticmethod
    def place_food(world: World, x: int, y: int) -> Food:
        """Разместить еду в заданной позиции."""
        food = Food(x, y)
        world.add_food(food)
        return food
    
    @staticmethod
    def place_wall(world: World, x: int, y: int):
        """Разместить стену."""
        world.set_cell(x, y, 1)
        world.walls_map[y, x] = 1 #TODO Это сомнительная история... Хорошо бы от этого избавиться.
    
    # @staticmethod
    # def clear_world(world: World):
    #     """Очистить мир (удалить всех существ и еду)."""
    #     print(f"Before clear: creatures={len(world.creatures)}, foods={len(world.foods)}")
    #     print(f"Before clear: map unique values={np.unique(world.map)}")
        
    #     world.creatures.clear()
    #     world.foods.clear()
        
    #     print(f"After lists clear: creatures={len(world.creatures)}, foods={len(world.foods)}")
        
    #     world.map.fill(0)
    #     world.update_map()
    #     print(f"After map.fill(0): map unique values={np.unique(world.map)}")
        
        # world.update_map()
        # print(f"After update_map: map unique values={np.unique(world.map)}")
        # print(f"walls_map unique values={np.unique(world.walls_map)}")
        # print("---")


class VisionSimulator:
    """Симулятор зрения для быстрого тестирования."""
    
    @staticmethod
    def get_creature_vision(world: World, creature: Creature) -> Tuple[np.ndarray, np.ndarray]:
        """
        Получить vision массив и raycast_dots для одного существа.
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (vision array [45], raycast_dots для визуализации)
        """
        world.update_map()  # обновить карту перед raycast
        creatures_pos = np.array([[creature.x, creature.y, creature.angle, creature.vision_distance]], dtype='float')
        all_visions, raycast_dots = World.fast_get_all_visions(world.map, creatures_pos)
        return all_visions[0], raycast_dots  # возвращаем vision и raycast_dots первого существа
    
    @staticmethod
    def simulate_nn_output(creature: Creature, vision: np.ndarray) -> Tuple[float, float, float]:
        """
        Симулировать выход NN для заданного vision, используя fast_calc_all_outs.
        Гарантирует идентичность расчетов с основной симуляцией.
        
        Returns:
            (angle_delta, speed_delta, bite): выходы нейросети
        """
        # Подготовить веса NN для fast_calc_all_outs
        creatures_nns = NeuralNetwork.prepare_calc([creature])
        
        # Обернуть vision в правильную форму: [1, 45]
        all_inputs = vision.reshape(1, -1).astype(np.float32)
        
        # Вызвать fast_calc_all_outs через make_all_decisions (тот же путь, что в основной симуляции)
        outputs = NeuralNetwork.make_all_decisions(all_inputs, creatures_nns)
        
        return float(outputs[0, 0]), float(outputs[0, 1]), float(outputs[0, 2])




class StatsCollector:
    """
    Гибкий сборщик статистики для многостадийных экспериментов.
    
    Поддерживает произвольные метрики через **kwargs.
    Структура: [{stage, success, metrics: {название: значение}}, ...]
    """
    
    def __init__(self):
        self.runs: List[Dict[str, Any]] = []
    
    def add_run(self, stage: int, success: bool, **metrics):
        """
        Добавить результат прогона с произвольными метриками.
        
        Args:
            stage: Номер стадии эксперимента
            success: Успешно ли пройден тест
            **metrics: Произвольные метрики (bite=0.85, energy=10, vision_quality=0.9, ...)
        
        Примеры:
            stats.add_run(stage=1, success=True, bite=0.85)
            stats.add_run(stage=2, success=False, bite=0.42, energy=5, reaction_time=100)
        """
        self.runs.append({
            'stage': stage,
            'success': success,
            'metrics': metrics,
        })
    
    def get_stage_stats(self, stage: int) -> dict:
        """
        Получить базовую статистику по стадии.
        
        Returns:
            {total, success, fail, success_rate}
        """
        stage_runs = [r for r in self.runs if r['stage'] == stage]
        total = len(stage_runs)
        success_count = sum(1 for r in stage_runs if r['success'])
        
        return {
            'total': total,
            'success': success_count,
            'fail': total - success_count,
            'success_rate': success_count / total if total > 0 else 0.0,
        }
    
    def get_metric_stats(self, stage: int, metric_name: str) -> dict:
        """
        Получить подробную статистику для любой метрики.
        
        Args:
            stage: Номер стадии
            metric_name: Название метрики ('bite', 'energy_consumed', 'vision_quality', и т.д.)
        
        Returns:
            {avg, max, min, std, count}
        
        Пример:
            energy_stats = stats.get_metric_stats(stage=1, metric_name='energy_consumed')
            print(f"Avg: {energy_stats['avg']:.2f}, Std: {energy_stats['std']:.2f}")
        """
        stage_runs = [r for r in self.runs if r['stage'] == stage]
        values = [r['metrics'].get(metric_name) for r in stage_runs 
                  if metric_name in r['metrics']]
        
        if not values:
            return {'avg': 0.0, 'max': 0.0, 'min': 0.0, 'std': 0.0, 'count': 0}
        
        values_array = np.array(values)
        return {
            'avg': float(np.mean(values_array)),
            'max': float(np.max(values_array)),
            'min': float(np.min(values_array)),
            'std': float(np.std(values_array)),
            'count': len(values),
        }
    
    def get_all_metrics_names(self) -> set:
        """
        Получить все известные метрики из всех прогонов.
        
        Returns:
            Set названий метрик
        
        Пример:
            all_metrics = stats.get_all_metrics_names()
            print(f"Available: {all_metrics}")
            # Output: Available: {'bite', 'energy_consumed', 'vision_quality'}
        """
        all_names = set()
        for run in self.runs:
            all_names.update(run['metrics'].keys())
        return all_names
    
    def get_summary(self) -> dict:
        """
        Получить полную сводку по всем стадиям.
        
        Returns:
            {1: stage_stats, 2: stage_stats, ..., 'overall': overall_stats}
        """
        stages = set(r['stage'] for r in self.runs)
        summary = {}
        for stage in sorted(stages):
            summary[stage] = self.get_stage_stats(stage)
        
        total_runs = len(self.runs)
        total_success = sum(1 for r in self.runs if r['success'])
        
        summary['overall'] = {
            'total_runs': total_runs,
            'total_success': total_success,
            'overall_success_rate': total_success / total_runs if total_runs > 0 else 0.0,
        }
        
        return summary

