class SimParams:
    """Параметры симуляции - все магические числа собраны в одном месте"""
    
    _instance = None
    
    def __init__(self):
        # === Параметры нейронной сети ===
        # Вероятность мутации каждого веса (из creature.py reprodCreature())
        self.mutation_probability = 0.1
        # Сила мутации - насколько сильно изменяются веса (из creature.py reprodCreature())
        self.mutation_strength = 0.5
        
        # === Параметры существа ===
        # Максимальный возраст существа в тиках (из creature.py update())
        self.creature_max_age = 250
        # Расстояние видения существа в ячейках (из creature.py __init__)
        # self.creature_vision_distance = 20
        # Диапазон укуса существа (из creature.py __init__)
        # self.creature_bite_range = 0.5
        
        # === Параметры еды ===
        # Количество еды при инициализации (из world_generator.py)
        self.food_amount = 10
        # Энергия одного куска пищи (из food.py - nutrition параметр)
        self.food_energy_capacity = 1.0
        # Энергия, получаемая существом за укус еды (из world.py creature_bite)
        self.food_energy_chunk = 0.5
        
        # === Параметры размножения ===
        # Возраст в диапазонах, при котором существо может размножаться (из creature.py birth_ages)
        # Примерно: 90-110, 190-210, 290-310, 490-510
        self.reproduction_ages = [100, 200, 300, 500]
        # Количество потомков при одном размножении (из creature.py reprodCreature())
        self.reproduction_offsprings = 3
        
        # === Затраты энергии ===
        # Затрата энергии за просто существование (из creature.py update())
        self.energy_cost_tick = 0.01
        # Затрата энергии на движение (интегрирована в общую)
        self.energy_cost_move = 0.0  # не найдено явно, встроено в базовую затрату
        # Затрата энергии на поворот (интегрирована в общую)
        self.energy_cost_rotate = 0.0  # не найдено явно, встроено в базовую затрату
        # Затрата энергии при столкновении со стеной (из world.py update())
        self.energy_cost_bite = 0.01  # при столкновении со стеной
        
        # === Приобретение энергии ===
        # Энергия, получаемая при укусе еды (из world.py creature_bite)
        self.energy_gain_from_food = 0.5
        # Энергия, получаемая при укусе другого существа (закомментировано)
        self.energy_gain_from_bite_cr = 0.1
        # Энергия, теряемая при укусе (закомментировано)
        self.energy_loss_bitten = 0.3
        # Энергия, теряемая при столкновении (из world.py update())
        self.energy_loss_collision = 0.01

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    

# Глобальный инстанс
sp = SimParams()


# Использование:
# ============================================================
# from simparams import sp
#
# # Получение значения параметра
# mutation_prob = sp.mutation_probability
#
# # Изменение значения параметра
# sp.mutation_probability = 0.15
# sp.energy_cost_tick = 0.02
#
# # Использование в коде:
# class Creature:
#     def mutate(self):
#         self.nn.mutate(sp.mutation_probability, sp.mutation_strength)
#
#     def update(self):
#         self.energy -= sp.energy_cost_tick
#         self.age += 1
#         if self.age > sp.creature_max_age:
#             self.energy = -100.0
# ============================================================