# -*- coding: utf-8 -*-
#from nn.nn_torch_rnn import NeuralNetwork
from nn.my_handmade_ff import NeuralNetwork
import copy
import random
from simparams import sp


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
        self.health = 1.0
        self.age = 0
        self.speed = 1
        self.angle = random.random()*3.14
        self.bite_effort = 0.0
        self.vision_distance = 20
        self.bite_range = 0.5
        self.nn = NeuralNetwork()
        self.birth_ages = Creature.diceRandomAges(sp.reproduction_ages) # Рандомные возрасты для рождения потомства
        # Дополнительные входы сетки, которые не зависят от зрения, а зависят от других факторов, таких как голод, боль и т.д.
        self.input_hurting = 0.0
        self.input_starving = 0.9
        self.input_wayblocked = 0.0
        self.input_bite_success = 0.0


    @staticmethod
    def string_to_list(input_string):
        """
        Преобразует строку в список целых чисел методом split.
        Обрабатывает случаи с отсутствующими/частичными скобками.

        Метод нужен, потому что возраста размножения в simparams хранятся в виде строки
        А хранятся в виде строки они, чтобы не создавтаь отдельный тип данных для списков.
        
        """
        
        # Убираем пробелы в начале и конце
        input_string = input_string.strip()

        # Если строка пустая или состоит только из пробелов
        if not input_string or input_string == "":
            return []
        
        # Убираем квадратные скобки если они есть
        # Мы удаляем их только если они на соответствующих позициях
        if input_string.startswith('['):
            input_string = input_string[1:]
        if input_string.endswith(']'):
            input_string = input_string[:-1]
        
        # Убираем пробелы после удаления скобок
        input_string = input_string.strip()
        
        # Если после очистки строка пустая
        if not input_string:
            return []
        
        # Разделяем по запятой
        parts = input_string.split(',')
        result = []
        
        # Преобразуем каждый элемент в целое число
        for part in parts:
            part = part.strip()  # Убираем пробелы вокруг
            if part:  # Пропускаем пустые строки
                try:
                    result.append(int(part))
                except ValueError:
                    # Если элемент нельзя преобразовать в целое число
                    # Можно либо пропустить, либо обработать иначе
                    # Здесь просто пропускаем некорректные значения
                    continue
        
        return result


    @staticmethod
    def diceRandomAges(reproduction_ages):
        # print(str(reproduction_ages) + " - Тип данных: " + str(type(reproduction_ages)))
        if type(reproduction_ages) is list:
            reproduction_ages_list = reproduction_ages
        else:
            reproduction_ages_list = Creature.string_to_list(reproduction_ages)
        ages = []
        for age in reproduction_ages_list:
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
            # print ("Рождение существа поколения №" + str(c.generation))
            c.nn = NeuralNetwork.copy(self.nn)
            if sp.allow_mutations == 1:
                c.nn.mutate(sp.mutation_probability, sp.mutation_strength)
                # print("##################  c.nn.mutate  ##################")
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

        # Здоровье существо меняется в зависимости от сытости (энергии)
        self.health = self.gain_health(self.health, self.energy)


        # Существо стареет
        self.age += 1
        if self.age > sp.creature_max_age:
            self.health = -100.0


        # Существо тратит энергию на бег в зависимости от скорости
        # Существо тратит энергию на поворот, в зависимости от резкого поворота
        # Существо тратит энергию на поворот, в зависимости от резкого поворота

    
    def gain_energy(self, amount: float):
        self.energy += amount
        if self.energy > 1.0:
            self.energy = 1.0

    def gain_health(self, health, energy):
        # Чем выше энергия, тем больше здоровье восстанавливается
        # вообще тут должа быть функция, которая бы моделировала восстановление или падение здоровья в зависимости от сытости и голода
        # TODO: Параметры этой функции, хорошо было бы вынести в simparams.
        # TODO: Вся эта функция кривенькая, и вызов ее тоже какойто странный, как будто в бессознательном состоянии писал. Переделать бы.
        if energy > 0.5:
            health += (energy - 0.5) * 0.1
            if health > 1.0:
                health = 1.0
            
            # Сигнал голода для нейросети, нормированный от 0 до 1. При достаточной энергии голода нет, сигнал равен нулю.
            self.input_starving = 0.0
            return health # Восстанавливаем здоровье при достаточной энергии
        else:
            health -= (0.5 - energy) * 0.02  # Теряем здоровье при низкой энергии
            
            # Сигнал голода для нейросети, нормированный от 0 до 1. При недостаточной энергии сигнал голода увеличивается.
            self.input_starving = (0.5 - energy) * 2.0  # TODO Кривовато. Возможны отрицательные значения. Вся эта функция кривенькая.
            return health
    

    def hurt(self, damage: float):
        # НЕДОДЕЛАНО!!!!!!!!!!!!!!!!!!!!!!!
        self.health -= damage
        if self.health < 0.0:
            self.health = 0.0
        return