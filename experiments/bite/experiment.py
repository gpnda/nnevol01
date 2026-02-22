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
???. Две пищи - слева и справа, посередине щель (не должен кусать)
6. Резюме результатов (финальная стадия)
"""

import random
import math
import numpy as np
from experiments.base.staged_experiment_base import StagedExperimentBase
from experiments.bite.dto import BiteExperimentDTO
from experiments.toolbox import ScenarioBuilder, VisionSimulator, StatsCollector
from world import World
from experiments.base.dto import ExperimentWorldStateDTO

class BiteExperiment(StagedExperimentBase):
    """Эксперимент проверки кусания."""

    def __init__(self, target_creature_id: int, world: World):
        super().__init__(target_creature_id, world)

        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Инициализация сборщика статистики
        self.stats = StatsCollector()
        
        # Переменные для хранения текущего состояния (для передачи в DTO)
        self.current_vision_input = None  # vision array [45]
        self.current_nn_outputs = None  # (angle_delta, speed_delta, bite_output)
        self.current_raycast_dots = None  # координаты raycast точек
        
        # Переменная для отладки (удалить позже)
        self.random_value = 0.0

    
    def _get_total_stages(self) -> int:
        return 7  # 6 тестовых стадий + 1 финальная
    
    def _stage_0(self):
        """Стадия 0: Пища впритык (экзаменуемое существо должно кусать еду рядом).
        
        Процедура прогона:
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (6, 25) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        7. Очистить мир для следующего прогона
        """
        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 1

        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        

        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        creature_y = 25.5 + y_offset
        
        # Разместить существо перед едой
        creature = ScenarioBuilder.place_creature(
            self.test_world, 
            x=5.7, 
            y=creature_y, 
            angle=0.0
        )
        
        # Разместить еду прямо перед существом (смотрящим вправо)
        ScenarioBuilder.place_food(self.test_world, x=6, y=25)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(creature, vision)
        
        # Сохранить текущее состояние для DTO (для визуализации в виджете)
        self.current_vision_input = vision
        self.current_nn_outputs = (float(angle_delta), float(speed_delta), float(bite_output))
        self.current_raycast_dots = raycast_dots
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output > 0.5
        
        # Записать результат в статистику
        self.stats.add_run(
            stage=0,
            success=success,
            bite_output=float(bite_output),
            vision_sum=float(np.sum(vision)),
            angle_delta=float(angle_delta),
            speed_delta=float(speed_delta)
        )

        
    
        
    def _stage_1(self):
        """Стадия 1: Пища не видна (не должен кусать)

        Процедура прогона:
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (6, 25) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        7. Очистить мир для следующего прогона
        """
        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 20

        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Разместить существо
        creature = ScenarioBuilder.place_creature(
            self.test_world, 
            x=5.7, 
            y=25.5, 
            angle=0.0
        )
        
        # Разместить 20 стен в случных местах карты, но не других стенах и не на существе
        for _ in range(20):
            while True:
                wall_x = random.randint(0, self.test_world.width - 1)
                wall_y = random.randint(0, self.test_world.height - 1)
                if self.test_world.map[wall_y, wall_x] == 0 and not (creature.x - 1 <= wall_x <= creature.x + 1 and creature.y - 1 <= wall_y <= creature.y + 1):
                    ScenarioBuilder.place_wall(self.test_world, x=wall_x, y=wall_y)
                    break
        # Разместить 15 неуправляемых существ в случных местах карты, но не других стенах и не на других существах
        for _ in range(15):
            while True:
                creature_x = random.uniform(0, self.test_world.width)
                creature_y = random.uniform(0, self.test_world.height)
                if self.test_world.map[int(creature_y), int(creature_x)] == 0 and not (creature.x - 1 <= creature_x <= creature.x + 1 and creature.y - 1 <= creature_y <= creature.y + 1):
                    ScenarioBuilder.place_creature(self.test_world, x=creature_x, y=creature_y, angle=random.uniform(0, 360))
                    break
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(creature, vision)
        
        # Сохранить текущее состояние для DTO (для визуализации в виджете)
        self.current_vision_input = vision
        self.current_nn_outputs = (float(angle_delta), float(speed_delta), float(bite_output))
        self.current_raycast_dots = raycast_dots
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output > 0.5
        
        # Записать результат в статистику
        self.stats.add_run(
            stage=1,
            success=success,
            bite_output=float(bite_output),
            vision_sum=float(np.sum(vision)),
            angle_delta=float(angle_delta),
            speed_delta=float(speed_delta)
        )
    
    def _stage_2(self):
        """Стадия 2: Пища далеко по центру (не должен кусать)"""
        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 1
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_3(self):
        """Стадия 3: Пища близко, но вне досягаемости (не должен кусать)"""

        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 5
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_4(self):
        """Стадия 4: Пища чуть правее (не должен кусать)"""

        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 100
        
        
        # Заглушка для проверки успеха
        self.random_value = random.random()  # для демонстрации изменения состояния
        success = self.random_value > 0.1
    
    def _stage_5(self):
        """Стадия 5: Пища чуть правее (не должен кусать)"""

        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 5
        
        
        # Заглушка для проверки успеха
        success = random.random() > 0.1
    
    def _stage_6(self):
        """Стадия 6: Резюме (финальная стадия)."""
        # Инициализация количества прогонов для этой стадии.
        # тупое место для инициализации, но так у нас не будет отдельного метода для инициализации стадии
        # Обязательно нужно задавать эту переменную в каждой стадии, иначе она перейдет с предыдущей стадии! 
        self.num_runs_this_stage = 1

        # Выводим резюме результатов
        self._print_summary()
    
    def get_experiment_dto(self):
        """Вернуть DTO для виджета с полной изоляцией через DTO."""
        summary = self.stats.get_summary()
        return BiteExperimentDTO(
            creature_id=self.target_creature.id,
            is_running=self.is_running,
            current_stage=self.current_stage,
            stage_run_counter=self.stage_run_counter,
            num_runs_this_stage=self.num_runs_this_stage,
            world=self._prepare_world_state_dto(),
            vision_input=self.current_vision_input,
            nn_outputs=self.current_nn_outputs,
            raycast_dots=self.current_raycast_dots,
            summary=summary
        )
    
    def _prepare_world_state_dto(self):
        """Подготовить DTO для виджета. Возвращает тестового мира."""
        return ExperimentWorldStateDTO(
            map=self.test_world.map,
            width=self.test_world.width,
            height=self.test_world.height
        )

    def _print_summary(self):
        """Вывести резюме результатов эксперимента в консоль."""
        summary = self.stats.get_summary()
        print(f"\n[BITE EXPERIMENT] Summary for creature {self.target_creature.id}")
        
        for stage in sorted([k for k in summary.keys() if isinstance(k, int)])[:6]:  # первые 6 стадий
            stage_stats = summary[stage]
            print(f"  Stage {stage}: "
                  f"Total={stage_stats['total']}, "
                  f"Success={stage_stats['success']}, "
                  f"Fail={stage_stats['fail']}, "
                  f"Rate={stage_stats['success_rate']*100:.1f}%")
        
        if 'overall' in summary:
            overall = summary['overall']
            print(f"  OVERALL: "
                  f"Total={overall['total_runs']}, "
                  f"Success={overall['total_success']}, "
                  f"Rate={overall['overall_success_rate']*100:.1f}%")
