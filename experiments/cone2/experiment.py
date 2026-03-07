# -*- coding: utf-8 -*-
"""
Cone2 Experiment - проверка достижения цели в различных координатах.

Стадии:
Стадий не планируется.
"""

import math
import numpy as np
from experiments.base.staged_experiment_base import StagedExperimentBase
from experiments.toolbox import ScenarioBuilder, VisionSimulator, StatsCollector
from world import World
from experiments.base.dto import ExperimentWorldStateDTO, ExperimentCreatureStateDTO
from experiments.cone2.dto import Cone2ExperimentDTO


MAX_TICKS_TO_ACHIVE_GOAL = 50  # Максимальное количество тиков, за которые существо должно достичь цели (куснуть пищу)

class Cone2Experiment(StagedExperimentBase):
    """Эксперимент с конусом - собираю его заново"""

    def __init__(self, target_creature_id: int, world: World):
        super().__init__(target_creature_id, world)


        self.plan = [
            {
            "stage_method": self._stage_0,
            "stage_name": "CONE2 CONE2 CONE2",
            "num_runs": 1000,
            "result_threshold": 0.9,
            }
            ]
        
        # Создаем экспериментальное существо с нейронной сеткой, скопированной из target_creature
        self.inspecting_creature = ScenarioBuilder.copy_creature(
            world.get_creature_by_id(target_creature_id)
        )

        # Инициализация сборщика статистики
        self.stats_collector = StatsCollector()

        # Переменные для хранения текущего состояния существа (для передачи в DTO)
        self.current_creature_state = None  # ExperimentCreatureStateDTO

        # параметры экспериментального мира
        self.test_world_width = 27
        self.test_world_height = 27

        # Создаём пустой тестовый мир 27x27 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(self.test_world_width, self.test_world_height)
        
        # Переменные для хранения текущей позиции пищи
        self.current_food_x = 0
        self.current_food_y = 0

        # Разместим еду
        ScenarioBuilder.place_food(self.test_world, x=self.current_food_x, y=self.current_food_y)
        
        # Размещаем существо
        self.inspecting_creature.x = 2.5
        self.inspecting_creature.y = 12.5
        self.inspecting_creature.angle = 0.0


        # Переменные для хранения текущей позиции пищи
        # Один run - это серия тиков, за которые существо должно куснуть пищу.
        # В каждый run - мы перемещаем пищу на 1 клетку вперед.
        # Так что нам нужно хранить текущую позицию пищи, чтобы знать, куда ее переместить в начале каждого run.
        # так что обнуляем именно в конструкторе а не в начале каждого run.
        self.current_food_x = 0
        self.current_food_y = 0

    
    def _stage_0(self):
        """Стадия 0: CONE CONE CONE
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Разместить пищу в точке (self.current_food_x, self.current_food_y)
        3. Запустить рабочий цикл, пока не будет достигнуто 
            - либо успешный укус пищи, 
            - либо выход за пределы карты 
            - или пищи нет в поле зрения на протяжении 10 тиков.
                    3.1. Получить vision через raycast
                    3.2. Вычислить выходы нейросети
                    3.3. Переместить существо примерно также как в основной симуляции
        6. Записать в статистику
        
        """
        
        # Получить vision для существа (raycast) + raycast_dots для визуализации
        vision, raycast_dots = VisionSimulator.get_creature_vision(self.test_world, self.inspecting_creature)

        # Вычислить выходы нейросети (out_angle, out_speed, bite)
        out_angle, out_speed, bite_output = VisionSimulator.simulate_nn_output(self.inspecting_creature, vision)

        ang, spd, newx, newy = World.apply_outs( # По моей задумке - это должен быть статичный метод класса World
				creature_x = self.inspecting_creature.x,
				creature_y = self.inspecting_creature.y,
				creature_angle = self.inspecting_creature.angle,
				creature_speed = self.inspecting_creature.speed,
				out_angle = out_angle,  # выход нейросети для angle
				out_speed = out_speed,  # выход нейросети для speed
				)
        self.inspecting_creature.angle = ang
        self.inspecting_creature.speed = spd
		# newx=newx #     просто демонстрирую, что этот метод возвращает и новые координаты тоже
		# newy=newy #      и что дальше будет использоваться эта четверка уже расчитанных переменных
        
        # Проверим, чтосущество не выползло за пределы карты
        if newx < 0 or newx >= self.test_world_width or newy < 0 or newy >= self.test_world_height:
            self.finish_run(success=False)
            return

        # Существо осталось в пределах карты, обновляем его позицию
        self.inspecting_creature.x = newx
        self.inspecting_creature.y = newy

        # Стен на карте не будет, поэтому и правил столкновения со стенами не будет писать
        # ...

        # Проверим другие условия SUCCESS/FAIL, например, кусает ли существо пищу (bite > 0.5) и пища в поле зрения
        # Проверить, кусает ли существо (bite > 0.5)
        if bite_output > 0.5:
            # Проверить, что на куснутом участке - еда. Это значит SUCCESS
            bitex = self.inspecting_creature.x + self.inspecting_creature.bite_range*math.cos(self.inspecting_creature.angle)
            bitey = self.inspecting_creature.y + self.inspecting_creature.bite_range*math.sin(self.inspecting_creature.angle)
            
            # Проверим выход за пределы карты > app.world.dimx-1 mappointer
            if (int(bitex) < 0 or int(bitex) > self.test_world_width-1) or (int(bitey) < 0 or int(bitey) > self.test_world_height-1):
                # Если существо куснуло за пределы карты, то просто не считаем это укусом, иначе будет Out of index
                pass
            else:
                # # Проверим на попытку укусить себя
                #               ДА ПОФИГ, СУЩЕСТВО ТО МОЖЕТ СТОЯТЬ НА ПИЩЕ В ОДНОЙ КЛЕТКЕ, ТАК ЧТО ПУСТЬ КУСАЕТ
                # if (int(bitex) == int(self.x) and int(bitey) == int(self.y)):
                # 	return False
                
                # получим информацию о том, что находится в клетке, которую существо кусает
                biteplace =  self.test_world.get_cell(int(bitex), int(bitey))

                if biteplace == 2:
                    # Существу повезло, оно укусило пищу.
                    self.finish_run(success=True)
                    return
        
        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(out_angle), float(out_speed), float(bite_output)),
            raycast_dots=raycast_dots
        )

        # Прервать run, если за XXX тиков не удалось ее куснуть. 
        # Если не прервать таким образом и не вернуть счетчик к нулю, то 
        # эксперимент завершиться по достижению количества, указанного в плане.
        if self.stage_run_counter == MAX_TICKS_TO_ACHIVE_GOAL:
            self.stage_run_counter = 0
            self.finish_run(success=False)


        # увеличить счетчик прогонов внутри стадии и перейти к следующей стадии, если достигнут лимит
        self.stage_run_counter_increment()





    def finish_run(self, success: bool):
        print(" ##########################  FINISH RUN ###########################")
        print("###   self.stage_run_counter", self.stage_run_counter)
        print("###   self.current_food_x", self.current_food_x)
        print("###   self.current_food_y", self.current_food_y)
        
        self.stage_run_counter = 0 # обнуляем счетчик
        print("###   NOW NEW VALUE self.stage_run_counter", self.stage_run_counter)
        
        # Сохраняем результат прогона в статистику
        self.stats_collector.add_run(
            stage=self.current_stage,
            success=success,
            point_x=self.current_food_x,
            point_y=self.current_food_y,
        )

        # Создаём пустой тестовый мир 27x27 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(self.test_world_width, self.test_world_height)
        
        # Переходим к следующей позиции пищи (п.2 в процедуре прогона: Последовательно размещать пищу в разных точках карты)
        self.current_food_x += 1
        if self.current_food_x >= self.test_world_width:
            self.current_food_x = 0
            self.current_food_y += 1
            if self.current_food_y >= self.test_world_height:
                print("All food positions tested.")
                self.stop()
                return
        
        print(f"Next food position: ({self.current_food_x}, {self.current_food_y})")
        # Разместим еду
        ScenarioBuilder.place_food(self.test_world, x=self.current_food_x, y=self.current_food_y)
        
        # Размещаем существо
        self.inspecting_creature.x = 2.5
        self.inspecting_creature.y = 12.5
        self.inspecting_creature.angle = 0.0
    
    



    def get_experiment_dto(self):
        """Вернуть DTO для виджета с полной изоляцией через DTO."""
        # summary = self.stats.get_summary()
        return Cone2ExperimentDTO(
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