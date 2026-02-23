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
from experiments.base.dto import ExperimentWorldStateDTO, ExperimentCreatureStateDTO

class BiteExperiment(StagedExperimentBase):
    """Эксперимент проверки кусания."""

    def __init__(self, target_creature_id: int, world: World):
        super().__init__(target_creature_id, world)

        self.plan = [
            {
            "stage_method": self._stage_0, # нулевая стадия - базовая проверка кусания, 10 прогонов для стабильной статистики
            "stage_name": "Do bite: Food Nearby at front",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.9,
            }, 
            {
            "stage_method": self._stage_1, # первая стадия - проверка, что существо не кусает, когда пища закрыта стеной, 20 прогонов для стабильной статистики
            "stage_name": "Don't bite: can't see any food",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.75,
            },
            {
            "stage_method": self._stage_2, # вторая стадия - проверка, что существо не кусает, когда пища далеко по центру, 20 прогонов для стабильной статистики
            "stage_name": "Don't bite: Food at front but far",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.9,
            },
            {
            "stage_method": self._stage_3, # третья стадия - проверка, что существо не кусает, когда пища близко, но вне досягаемости, 20 прогонов для стабильной статистики
            "stage_name": "Don't bite: Food still out of reach",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.7,
            },
            {
            "stage_method": self._stage_4, # четвертая стадия - проверка, что существо не кусает, когда пища чуть правее, 20 прогонов для стабильной статистики
            "stage_name": "Don't bite: Food at right side",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.6,
            },
            {
            "stage_method": self._stage_5, # пятая стадия - проверка, что существо не кусает, когда пища чуть левее, 20 прогонов для стабильной статистики
            "stage_name": "Don't bite: Food at left side",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.6,
            },
            {
            "stage_method": self._stage_6, # шестая стадия - есть пища слева и справа, посередине щель, существо должно понять что кусать нельзя, 20 прогонов для стабильной статистики
            "stage_name": "Don't bite: Gap in the middle",  # для отображения в виджете
            "num_runs": 30,
            "result_threshold": 0.0,
            },
            ]

        # Создаём пустой тестовый мир 50x50 для экспериментов. ХОТЯ МИРЫ СОЗДАЮТСЯ В ОТДЕЛЬНЫХ СТАДИЯХ СВОИ
        # self.test_world = ScenarioBuilder.create_test_world(50, 50)

        # Создаем экспериментальное существо с нейронной сеткой, скопированной из target_creature
        self.inspecting_creature = ScenarioBuilder.copy_creature(
            world.get_creature_by_id(target_creature_id)
        )

        # Инициализация сборщика статистики
        self.stats_collector = StatsCollector()
        
        # Переменные для хранения текущего состояния существа (для передачи в DTO)
        self.current_creature_state = None  # ExperimentCreatureStateDTO
        
        # Переменная для отладки (по сути - чтоб заглушки работали, просто поищи по файлу - увидишь)
        self.random_value = 0.0
    
    
    
    def _stage_0(self):
        """Стадия 0: Пища впритык (экзаменуемое существо должно кусать еду рядом).
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (6, 25) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
        # self.inspecting_creature.nn.print_nn_parameters()

        # Разместим еду в (6, 25) - прямо перед существом
        ScenarioBuilder.place_food(self.test_world, x=6, y=25)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output > 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )





























    def _stage_1(self):
        """Стадия 1: Пища не видна (не должен кусать)

        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (6, 25) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        self.inspecting_creature.nn.print_nn_parameters()   # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.

        
        
        # Разместить 100 стен в случных местах карты, но не других стенах и не на инспектируемом существе
        for _ in range(100):
            while True:
                wall_x = random.randint(0, self.test_world.width - 1)
                wall_y = random.randint(0, self.test_world.height - 1)
                if self.test_world.map[wall_y, wall_x] == 0 and not (self.inspecting_creature.x - 1 <= wall_x <= self.inspecting_creature.x + 1 and self.inspecting_creature.y - 1 <= wall_y <= self.inspecting_creature.y + 1):
                    ScenarioBuilder.place_wall(self.test_world, x=wall_x, y=wall_y)
                    break
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output < 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )
    
    def _stage_2(self):
        """Стадия 2: Пища далеко по центру (не должен кусать)
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (17, 25) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
        # self.inspecting_creature.nn.print_nn_parameters()

        # Разместим еду в (17, 25) - прямо перед существом
        ScenarioBuilder.place_food(self.test_world, x=17, y=25)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output < 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )
    














    
    
    def _stage_3(self):
        """Стадия 3: Пища близко, но вне досягаемости (не должен кусать)
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (8, 25) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
        # self.inspecting_creature.nn.print_nn_parameters()

        # Разместим еду в (8, 25) - прямо перед существом
        ScenarioBuilder.place_food(self.test_world, x=8, y=25)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output < 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )
    












    
    def _stage_4(self):
        """Стадия 4: Пища чуть правее (не должен кусать)
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (7, 26) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
        # self.inspecting_creature.nn.print_nn_parameters()

        # Разместим еду в (7, 26) - прямо перед существом
        ScenarioBuilder.place_food(self.test_world, x=7, y=26)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output < 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )
    




















    
    def _stage_5(self):
        """Стадия 5: Пища чуть левее (не должен кусать)
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (7, 24) - прямо перед существом
        3. Получить vision через raycast
        4. Вычислить выходы нейросети
        5. Проверить: bite_output > 0.5 = успех
        6. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
        # self.inspecting_creature.nn.print_nn_parameters()

        # Разместим еду в (7, 24) - прямо перед существом
        ScenarioBuilder.place_food(self.test_world, x=7, y=24)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output < 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )
    
















    
    def _stage_6(self):
        """Стадия 6: шестая стадия - есть пища слева и справа, посередине щель, существо должно понять что кусать нельзя, 20 прогонов для стабильной статистики.
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить еду в (7, 24) - слева перед существом
        3. Разместить еду в (7, 26) - справа перед существом
        4. Получить vision через raycast
        5. Вычислить выходы нейросети
        6. Проверить: bite_output > 0.5 = успех
        7. Записать в статистику
        
        """
        
        # Очистить мир для прогона
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(50, 50)
        
        # Размещаем существо
        self.inspecting_creature.x = 5.7
        # Генерировать случайное смещение Y: ±0.3
        y_offset = random.uniform(-0.3, 0.3)
        self.inspecting_creature.y = 25.5 + y_offset
        self.inspecting_creature.angle = 0.0

        # отладочный вывод весов, чтобы проверить что сетка копируется и передается успешно в эксперимент. Принты пока оставлю, потом уберу так или иначе.
        # self.inspecting_creature.nn.print_nn_parameters()

        # Разместим еду в (7, 24) - слева перед существом
        ScenarioBuilder.place_food(self.test_world, x=7, y=24)
        # Разместим еду в (7, 26) - справа перед существом
        ScenarioBuilder.place_food(self.test_world, x=7, y=26)
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)
        
        # Вычислить выходы нейросети (angle_delta, speed_delta, bite)
        angle_delta, speed_delta, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(angle_delta), float(speed_delta), float(bite_output)),
            raycast_dots=raycast_dots
        )
        
        # Проверить, кусает ли существо (bite > 0.5)
        success = bite_output < 0.5
        
        # Записать результат в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success
        )
    
















    
    def get_experiment_dto(self):
        """Вернуть DTO для виджета с полной изоляцией через DTO."""
        # summary = self.stats.get_summary()
        return BiteExperimentDTO(
            creature_id=self.target_creature.id,
            is_running=self.is_running,
            current_stage=self.current_stage,
            stage_run_counter=self.stage_run_counter,
            world=ExperimentWorldStateDTO(
                    map=self.test_world.map,
                    width=self.test_world.width,
                    height=self.test_world.height
                ),
            creature_state=self.current_creature_state,
            plan=self.plan,
            stats=self.stats_collector.get_all_stages_stats(),
        )
    
    def _get_total_stages(self) -> int:
        return len(self.plan)

    def _print_summary(self):
        """Вывести резюме результатов эксперимента в консоль."""
        pass
        # summary = self.stats.get_summary()
        # print(f"\n[BITE EXPERIMENT] Summary for creature {self.target_creature.id}")
        
        # for stage in sorted([k for k in summary.keys() if isinstance(k, int)])[:6]:  # первые 6 стадий
        #     stage_stats = summary[stage]
        #     print(f"  Stage {stage}: "
        #           f"Total={stage_stats['total']}, "
        #           f"Success={stage_stats['success']}, "
        #           f"Fail={stage_stats['fail']}, "
        #           f"Rate={stage_stats['success_rate']*100:.1f}%")
        
        # if 'overall' in summary:
        #     overall = summary['overall']
        #     print(f"  OVERALL: "
        #           f"Total={overall['total_runs']}, "
        #           f"Success={overall['total_success']}, "
        #           f"Rate={overall['overall_success_rate']*100:.1f}%")
