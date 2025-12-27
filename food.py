# -*- coding: utf-8 -*-

class Food():
    def __init__(self, x, y, nutrition):
        self.x = x
        self.y = y
        self.nutrition = nutrition

    def decrement(self, sim_food_energy_chunk):
        self.nutrition -= sim_food_energy_chunk
        print("Food at (" + str(self.x) + "," + str(self.y) + ") decremented to " + str(self.nutrition))    
        

    
