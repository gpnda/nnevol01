# -*- coding: utf-8 -*-
from simparams import sp

class Food():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.nutrition = sp.food_energy_capacity
        self.food_age = 0
    

    def decrement(self):
        self.nutrition -= sp.food_energy_chunk
        # print("Food at (" + str(self.x) + "," + str(self.y) + ") decremented to " + str(self.nutrition))
        
