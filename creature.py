# -*- coding: utf-8 -*-
#from nn.nn_torch_rnn import NeuralNetwork
from nn.my_handmade_ff import NeuralNetwork
import copy
import random
from simparams import sp
from service.logger.logger import logme


class Creature():
    _id_counter = 0
    
    def __init__(self, x: float, y: float):
        # назначаем уникальный ID
        Creature._id_counter += 1
        self.id = Creature._id_counter
        self.generation = 0

        self.x = x
        self.y = y
        self.energy = 1.0
        self.age = 0
        self.speed = 1
        self.angle = random.random()*3.14
        self.bite_effort = 0.0
        self.vision_distance = 20
        self.bite_range = 0.5
        self.nn = NeuralNetwork()
        self.birth_ages = Creature.diceRandomAges(sp.reproduction_ages) # Рандомные возрасты для рождения потомства


    @staticmethod
    def diceRandomAges(reproduction_ages):
        ages = []
        for age in reproduction_ages:
            variation = random.randint(-10, 10)
            ages.append(age + variation)
        return ages
    
    def reprodCreature(self):
        cr_babies = []
        # print ("начало цикла по рождению детей")
        for j in range(0, sp.reproduction_offsprings):
            # print ("Процесс рождения существа. 1 Погнали")
            # c = copy.deepcopy(self)
            # print ("Процесс рождения существа. 2")
            # c.mutate(app.gM_probability, app.gM_strength)
            # print ("Процесс рождения существа. 3")
            # c.uid = uuid.uuid4()
            # print ("Процесс рождения существа. 4")
            # c.generation = self.generation + 1
            # print ("Процесс рождения существа. 5")
            c = Creature(self.x, self.y)
            c.generation = self.generation + 1
            print ("Рождение существа поколения №" + str(c.generation))
            c.nn = NeuralNetwork.copy(self.nn)
            c.nn.mutate(sp.mutation_probability, sp.mutation_strength)
            # c.isSelected = False
            # print ("Процесс рождения существа. 6")
            cr_babies.append(c)
            # print ("Процесс рождения существа. 7. Родили уфф..")
        return cr_babies
    
    
    def update(self):

        # Существо тратит энергию на просто существование в мире
        self.energy -= sp.energy_cost_tick

        # Существо тратит энергию на перемещение, пропорционально скорости
        self.energy -= abs(self.speed) * sp.energy_cost_speed

        # Существо тратит энергию на поворот, пропорционально углу поворота
        self.energy -= abs(self.angle) * sp.energy_cost_rotate
        
        # Существо тратит энергию на укус, пропорционально силе укуса
        self.energy -= abs(self.bite_effort) * sp.energy_cost_bite


        # Существо стареет
        self.age += 1
        if self.age > sp.creature_max_age:
            self.energy = -100.0


        # Существо тратит энергию на бег в зависимости от скорости
        # Существо тратит энергию на поворот, в зависимости от резкого поворота
        # Существо тратит энергию на поворот, в зависимости от резкого поворота

    
    def gain_energy(self, amount: float):
        self.energy += amount
        if self.energy > 1.0:
            self.energy = 1.0




# 
# 
# 
# ЧТО НАРЕКОМЕНДОВАЛ DEEPSEEK
# 
# 
#   def update(self, world: World):
#         """Полный цикл обновления существа."""
#         # 1. Обновляем физиологию
#         self._update_physiology()
        
#         # 2. Если существо живо - действуем
#         if self.is_alive and self.energy > 0:
#             # 3. Получаем информацию о мире
#             vision = self.get_creature_vision(world)
            
#             # 4. Принимаем решение
#             action = self.pass_vision_to_neural_network(vision)
            
#             # 5. Выполняем действие
#             self.execute_output_as_creature_decisions(action, world)
# 
# 
# 
# 
# 
# 
#     def get_creature_vision(self, world: World) -> VisionData:
#         """Собирает информацию о мире вокруг существа."""
#         vision_data = VisionData()
        
#         # Сканируем область вокруг
#         for dx in range(-self.vision_range, self.vision_range + 1):
#             for dy in range(-self.vision_range, self.vision_range + 1):
#                 if dx == 0 and dy == 0:
#                     continue
                    
#                 world_x, world_y = self.x + dx, self.y + dy
#                 if world.is_valid_position(world_x, world_y):
#                     cell_value = world.get_cell(world_x, world_y)
#                     distance = max(abs(dx), abs(dy))
                    
#                     vision_data.add_cell(dx, dy, cell_value, distance)
        
#         return vision_data
    
#     def pass_vision_to_neural_network(self, vision: VisionData) -> Action:
#         """Обрабатывает визуальную информацию через ИИ."""
#         # Преобразуем vision в входные данные для нейросети
#         network_input = self._vision_to_network_input(vision)
        
#         # Получаем решение от мозга
#         network_output = self.brain.process(network_input)
        
#         # Интерпретируем выход нейросети как действие
#         return self._network_output_to_action(network_output)
    
#     def execute_output_as_creature_decisions(self, action: Action, world: World):
#         """Выполняет выбранное действие в мире."""
#         if action.type == ActionType.MOVE:
#             world.move_creature_by(self, action.dx, action.dy)
#         elif action.type == ActionType.EAT:
#             self.try_eat_at(world, self.x + action.dx, self.y + action.dy)
#         elif action.type == ActionType.REST:
#             self.rest()
    
#     def _update_physiology(self):
#         """Обновляет внутреннее состояние (энергия, здоровье)."""
#         self.energy -= 0.1
#         if self.energy <= 0:
#             self.health -= 1
#             self.energy = 0
    
#     @property
#     def is_alive(self) -> bool:
#         return self.health > 0