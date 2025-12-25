# -*- coding: utf-8 -*-

class Food():
    def __init__(self, x, y, nutrition):
        self.x = x
        self.y = y
        self.nutrition = nutrition

    def decrement(self):
        self.nutrition -= 0.6
        print("Food at (" + str(self.x) + "," + str(self.y) + ") decremented to " + str(self.nutrition))    
        

    
