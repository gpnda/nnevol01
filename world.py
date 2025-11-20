# -*- coding: utf-8 -*-

from creature import Creature
import random
import math
from debugger import debug


class World():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.map = [[0 for _ in range(width)] for _ in range(height)]
		self.walls_map = []
		self.creatures = []
		self.foods = []

	
	def update_map(self):
		"""Обновляет карту для отображения (рендерер использует эту)"""
		# 1. Копируем стены
		self.map = [row[:] for row in self.walls_map]
		
		# 2. Добавляем еду
		for food in self.foods:
			self.set_cell(food.x, food.y, 2)  # FOOD
		
		# 3. Добавляем существ
		for creature in self.creatures:
			self.set_cell(int(creature.x), int(creature.y), 3)  # CREATURE

	def get_cell(self, x, y):
		return self.map[y][x]

	def set_cell(self, x, y, value):
		self.map[y][x] = value
		return True

	def add_food(self, food):
		self.foods.append(food)

	def add_creature(self, creature):
		self.creatures.append(creature)


	def update(self):
		# 1. Восприятие (параллельно)
		# Подготавливаем данные для быстрой функции
		current_map = self.map
		creatures_pos = []
		for creature in self.creatures:
			creatures_pos.append([
				creature.x, 
				creature.y, 
				creature.angle,
				creature.vision_distance
				])
		# запускаем быструю функцию
		all_visions, raycast_dots = self.fast_get_all_visions(current_map, creatures_pos)
		debug.set("raycast_dots", raycast_dots)
		
		
		# 2. Мышление (параллельно)  
		# Подготавливаем данные для быстрой функции
		creatures_nns = []
		for creature in self.creatures:
			creatures_nns.append(creature.nn) # Здесь не creature.nn надо, а функцию, возвращающую веса, например creature.get_brain_wights(). Ну, ок, пока не важно.
		# запускаем быструю функцию
		all_outs = self.fast_get_all_outs(all_visions, creatures_nns)
		# all_outs[] = [angle_delta, speed_delta, bite]


		# 3. Перемещаем существ, согласно выходам нейросетей
		for index, creature in enumerate(self.creatures):
			creature.angle = creature.angle + all_outs[index][0]
			creature.speed = creature.speed + all_outs[index][1]
			if creature.speed < -0.5:
				creature.speed = -0.5
			if creature.speed > 0.5:
				creature.speed = 0.5
			newx = creature.x + creature.speed*math.cos(creature.angle)
			newy = creature.y + creature.speed*math.sin(creature.angle)


			# Правила, по которым может перемещаться существо

			is_ok_to_go = True
			# Проверим выход за пределы карты
			if (int(newx) < 0 or int(newx) > self.width-1):
				is_ok_to_go = False
			if (int(newy) < 0 or int(newy) > self.height-1):
				is_ok_to_go = False
			
			# Проверим, что в новой клетке не стена. На стену нельзя переходить.
			if self.get_cell(int(newx),int(newy)) == 1:
				is_ok_to_go = False
			
			if is_ok_to_go:
				creature.x = newx
				creature.y = newy

			
	











	
	@staticmethod
	def fast_get_all_visions(map, creatures_pos):
		step = 0.9 # шаг перемещения взгляда (для raycast - дистанция на котороую двигаем вперед указатель)
		resolution = 15 # разрешение взгляда - по сути сколько лучше отправит raycast?
		angleofview = 1.04719 # это примерно 60 градусов
		anglestep = 1.04719 / resolution
		raycast_dots = []
		all_visions = []

		for index, cr in enumerate(creatures_pos):
			vision = []
			visionRed = []
			visionGreen = []
			visionBlue = []
			
			for a in range(resolution):
				adelta = -1*angleofview/2 + a*anglestep
				d = 0
				cur_vision = 0
				while d < cr[3]:
					d += step
					x = cr[0] + d*math.cos(cr[2]+adelta)
					y = cr[1] + d*math.sin(cr[2]+adelta)
					if int(x) == int(cr[0]) and int(y) == int(cr[1]):
						continue # Если смотрит на свое тело, то пропустим эту итерацию
					if True: #index == 0
						raycast_dots.append([x , y])
					dot = 0


					ix = int(x)
					iy = int(y)
					mw = len(map[0])
					mh = len(map)
					if ix < 0 or ix >= mw or iy < 0 or iy >= mh:
						# за пределами карты → чёрный
						vision.append(0)
						visionRed.append(0)
						visionGreen.append(0)
						visionBlue.append(0)
						break
					else:
						dot = map[iy][ix]
					
					# Если взгляд во что-то уперся, то Сохраняем цвет точки и Прерываем raycast
					if dot > 0:
						cur_vision = dot
						# Сюда надо вставлять опреденений цветов и разложение на каналы.
						dotColor = []
						if dot == 1:
							dotColor = [100,100,100]
						elif dot == 2:
							dotColor = [255,0,0]
						elif dot == 3:
							dotColor = [0,0,255]
						else:
							dotColor = [0,0,0]
					
						# Сюда вставляем искажение цвета, в зависимости от дистанции
						# Условие нужно, потому что иногда d улетает больше чем self.viewdistance, 
						# тогда цвет станет больше 255
						# if d < self.viewdistance:
						#     dotColor = Creature.__fadeColors(dotColor , d/self.viewdistance )


						vision.append(cur_vision)
						# тут переменная dotColor содержит RGB Представление цвета
						visionRed.append(dotColor[0])
						visionGreen.append(dotColor[1])
						visionBlue.append(dotColor[2])
						break

				else:
					# В этой ветке обслуживаем ситуацию, когда Raycast достиг 
					# максимальной дистанции взгляда и ничего не увидел
					vision.append(0)
					visionRed.append(0)
					visionGreen.append(0)
					visionBlue.append(0)
				
			# Превратим массив элементами карты в массив с цветами
			visionRGB = visionRed + visionGreen + visionBlue
			visionResult = visionRGB
			# print("visionRed: " + str(visionRed))
			# print("visionGreen: " + str(visionGreen))
			# print("visionBlue: " + str(visionBlue))

			all_visions.append(visionResult)
			
		# print("Длина массива all_visions: " + str(len(all_visions)))
		# for index,v in enumerate(all_visions):
		# 	print("Длина " + str(index) + " массива vision: " + str(len(v)))
		return all_visions, raycast_dots
	



















	@staticmethod
	def fast_get_all_outs(all_visions, creatures_nns):
		# Это заглушка для
		all_outs = [] # all_outs[] = [angle_delta, speed_delta, bite]

		for index,out in enumerate(creatures_nns):
			angle_delta = 0.0
			speed_delta = 0.3
			bite = 0.0
			
			if (all_visions[index][7] > 250) and (all_visions[index][22] < 50) and (all_visions[index][37] < 50):
				angle_delta = 0.01*(random.random()-0.5)
			else:
				angle_delta = 1*(random.random()-0.5)
			all_outs.append([
				angle_delta, 
				speed_delta, 
				bite
				])
					
		return all_outs
