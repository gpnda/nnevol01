# -*- coding: utf-8 -*-

import csv
import random
import numpy as np
from food import Food
from creature import Creature
from world import World

class WorldGenerator:
    @staticmethod
    def generate_world(width=20, height=20, wall_count=100, food_count=10, creatures_count=15, border_walls=True):
        world = World(width, height)
        WorldGenerator.generate_walls(world, wall_count, border_walls)
        WorldGenerator.save_walls_map(world)
        world.zones_map.generate_lefthalf_zone(world.walls_map)
        WorldGenerator.generate_food(world, food_count)
        WorldGenerator.generate_creatures(world, creatures_count)
        return world
    
    @staticmethod
    def generate_world_fromCSV(file_path, random_wall_count=100, food_count=10, creatures_count=15, border_walls=True):
        print("Initialisig World from CSV file")

        # Сначала читаем CSV в обычный список, чтобы узнать размеры карты.
        csv_rows = []
        with open(file_path, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='\"')
            for row in csvreader:
                if not row:
                    continue
                csv_rows.append([int(x.strip()) for x in row if x.strip() != ''])

        if not csv_rows:
            raise ValueError(f"CSV map is empty: {file_path}")

        width = len(csv_rows[0])
        height = len(csv_rows)
        if any(len(row) != width for row in csv_rows):
            raise ValueError(f"CSV map rows have different lengths: {file_path}")

        world = World(width, height)
        
        # 1. Загружаем информацию о зонах из оригинальных CSV данных (до преобразования '9' в '0')
        world.zones_map.load_from_csv(csv_rows)
        
        # 2. Устанавливаем карту мира, заменяя '9' на '0'
        map_array = np.array(csv_rows, dtype='int')
        map_array[map_array == 9] = 0  # Заменяем гнёзда на открытое пространство в основной карте
        world.map = map_array
        
        WorldGenerator.generate_walls(world, random_wall_count, border_walls)
        WorldGenerator.save_walls_map(world)
        WorldGenerator.generate_food(world, food_count)
        WorldGenerator.generate_creatures(world, creatures_count)
        return world
    
    
    @staticmethod
    def generate_walls(world, wall_count, border_walls):
        width = world.width
        height = world.height

		# Генерация стен
        for i in range(wall_count):
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            world.set_cell(x , y , 1)
        
        if border_walls:
            # Генерация стен у границ карты - горизонтальные верхняя и нижняя
            for i in range(width):
                world.set_cell(i , 0 , 1)
                world.set_cell(i , height-1 , 1)
		
        if border_walls:
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
		
