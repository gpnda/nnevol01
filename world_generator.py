# -*- coding: utf-8 -*-

import random
from food import Food
from creature import Creature
from world import World

class WorldGenerator:
    @staticmethod
    def generate_world(width=20, height=20, wall_count=100, food_count=10, creatures_count=15):
        world = World(width, height)
        WorldGenerator.generate_walls(world, wall_count)
        WorldGenerator.save_walls_map(world)
        WorldGenerator.generate_food(world, food_count)
        WorldGenerator.generate_creatures(world, creatures_count)
        return world
    
    
    @staticmethod
    def generate_walls(world, wall_count):
        width = world.width
        height = world.height

		# Генерация стен
        for i in range(wall_count):
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            world.set_cell(x , y , 1)
        
        # Генерация стен у границ карты - горизонтальные верхняя и нижняя
        for i in range(width):
            world.set_cell(i , 0 , 1)
            world.set_cell(i , height-1 , 1)
		
        # Генерация стен у границ карты - вертикальные левая и правая
        for i in range(height):
            world.set_cell(0 , i , 1)
            world.set_cell(width-1, i , 1)
    
    @staticmethod
    def save_walls_map(world):
        # После генерации стен - мы должны сохранить карту стен, чтоб потом обновлять карту
        world.walls_map = world.map.copy()

    @staticmethod
    def generate_food(world, food_count):
        width = world.width
        height = world.height
        # Генерация еды
        for _ in range(food_count):
            while True:
                x, y = random.randint(0, width-1), random.randint(0, height-1)
                # Проверим, что пища создается на пустой ячейке
                if world.get_cell(x,y) == 0:
                    world.add_food(Food(x, y))
                    break
    
    @staticmethod
    def generate_creatures(world, creatures_count):
        width = world.width
        height = world.height
        # Генерация существ
        for _ in range(creatures_count):
            while True:
                x, y = random.randint(0, width-1), random.randint(0, height-1)
                # Проверим, что существо создается на пустой ячейке
                if world.get_cell(x,y) == 0:
                    world.add_creature(Creature(x, y))
                    break
		
