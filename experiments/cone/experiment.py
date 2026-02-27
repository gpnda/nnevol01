# -*- coding: utf-8 -*-
"""
Cone Experiment - проверка достижения цели в различных координатах.

Стадии:
Стадий не планируется.
"""

import random
import math
import numpy as np
from experiments.base.staged_experiment_base import StagedExperimentBase
from experiments.bite.dto import BiteExperimentDTO
from experiments.toolbox import ScenarioBuilder, VisionSimulator, StatsCollector
from world import World
from experiments.base.dto import ExperimentWorldStateDTO, ExperimentCreatureStateDTO

class ConeExperiment(StagedExperimentBase):
    """Эксперимент проверки кусания."""

    def __init__(self, target_creature_id: int, world: World):
        super().__init__(target_creature_id, world)

        self.plan = [
            {
            "stage_method": self._stage_0,
            "stage_name": "CONE CONE CONE",
            "num_runs": 100,
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

        # Разместим еду в начальной позиции
        ScenarioBuilder.place_food(self.test_world, x=self.current_food_x, y=self.current_food_y)
        
        # Размещаем существо
        self.inspecting_creature.x = 2.5
        self.inspecting_creature.y = 12.5
        self.inspecting_creature.angle = 0.0
        
    







########################################################################################
###      ######     ##   ####   #        ##############################################
##    ###   #    ##   #     ##  ##   ###################################################
##    #######   ####  #   #  #  ##      ##################       ### ###################
##    ####  #    ##   #   ##    ##   #################     #    # ######################
###       #####     ###   ###    #        ####          #      ##  #####################
#######################################                           # ####################
################################                #                 #    #################
###########################                              #     #    ### ################
#######      ######                                              # #    ################
#######   #  #                                                       # #################
#######      ####                                      #         #      # ##############
######################                     #                  #     #   ################
###############################                                     ##  ################
#####################################                  #            ####################
################################################              #    # ###################
########################################################        # ######################
############################################################    ### ####################
########################################################################################
########################################################################################

    def _stage_0(self):
        """Стадия 0: CONE CONE CONE
        
        Процедура прогона:
        0. Создать пустой новый мир
        1. Разместить существо в (5.7, 25.5 ± 0.3), смотрящее вправо (angle=0)
        2. Последовательно размещать пищу в разных точках карты
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
            if (int(bitex) < 0 or int(bitex) > self.test_world_width-1):
                return False
            if (int(bitey) < 0 or int(bitey) > self.test_world_height-1):
                return False

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
        

        # print("step: ", self.current_stage, self.stage_run_counter, "pos:", round(self.inspecting_creature.x, 2), round(self.inspecting_creature.y, 2), "angle:", round(self.inspecting_creature.angle, 2), "bite:", round(bite_output, 2))


        # Сохранить текущее состояние существа для DTO (для визуализации в виджете)
        self.current_creature_state = ExperimentCreatureStateDTO(
            x=self.inspecting_creature.x,
            y=self.inspecting_creature.y,
            angle=self.inspecting_creature.angle,
            vision_input=vision,
            nn_outputs=(float(out_angle), float(out_speed), float(bite_output)),
            raycast_dots=raycast_dots
        )

        if self.stage_run_counter == 10:
            self.stage_run_counter = 0
            self.finish_run(success=False)

        
        
        








    def finish_run(self, success: bool):
        print(" ##########################  FINISH RUN ###########################")
        # Создаём пустой тестовый мир 50x50 для экспериментов
        self.test_world = ScenarioBuilder.create_test_world(self.test_world_width, self.test_world_height)
        
        # Переходим к следующей позиции пищи (п.2 в процедуре прогона: Последовательно размещать пищу в разных точках карты)
        self.current_food_x += 1
        if self.current_food_x >= self.test_world_width:
            self.current_food_x = 0
            self.current_food_y += 1
            if self.current_food_y >= self.test_world_height:
                print("All food positions tested.")
                return

        # Разместим еду в начальной позиции
        ScenarioBuilder.place_food(self.test_world, x=self.current_food_x, y=self.current_food_y)
        
        # Разместим существо обратно в начальную позицию
        self.inspecting_creature.x = 2.5
        self.inspecting_creature.y = 12.5
        self.inspecting_creature.angle = 0.0
        
        # Сохраняем результат прогона в статистику
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
