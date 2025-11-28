# -*- coding: utf-8 -*-

from creature import Creature
#from nn.nn_torch_rnn import NeuralNetwork
from nn.my_handmade_ff import NeuralNetwork
import random
import math
import numpy as np
from numba import jit

from debugger import debug



class World():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.map = np.zeros((height, width), dtype='int')
		self.walls_map = np.zeros((height, width), dtype='int')
		self.creatures = []
		self.foods = []

	
	def update_map(self):
		"""Обновляет карту для отображения (рендерер использует эту)"""
		# 1. Копируем стены
		self.map = self.walls_map.copy()
		
		# 2. Добавляем еду
		for food in self.foods:
			self.set_cell(food.x, food.y, 2)  # FOOD
		
		# 3. Добавляем существ
		for creature in self.creatures:
			self.set_cell(int(creature.x), int(creature.y), 3)  # CREATURE

	def get_cell(self, x, y):
		return self.map[y, x]

	def set_cell(self, x, y, value):
		self.map[y, x] = value
		return True

	def add_food(self, food):
		self.foods.append(food)

	def add_creature(self, creature):
		self.creatures.append(creature)


	def update(self):
		# 1. Восприятие (параллельно)
		# Подготавливаем данные для быстрой функции
		current_map = self.map
		creatures_pos = np.zeros((len(self.creatures),4), dtype='float')
		for index, creature in enumerate(self.creatures):
			creatures_pos[index] = np.array([creature.x, 
				creature.y, 
				creature.angle,
				creature.vision_distance]
				)
		# запускаем быструю функцию
		all_visions, raycast_dots = self.fast_get_all_visions(current_map, creatures_pos)
		all_visions_normalized = self.normalize_vision(all_visions)
		debug.set("raycast_dots", raycast_dots)
		
		
		# 2. Мышление (параллельно)  
		# Подготавливаем данные для быстрой функции
		creatures_nns = []
		for creature in self.creatures:
			creatures_nns.append(creature.nn.flatten_network())
		# запускаем быструю функцию
		print(creatures_nns)
		all_outs = NeuralNetwork.fast_calc_all_outs(all_visions_normalized, np.array(creatures_nns))
		# all_outs[] = [angle_delta, speed_delta, bite]


		# 3. Перемещаем существ, согласно выходам нейросетей
		for index, creature in enumerate(self.creatures):

			# Расчитываем новые координаты, куда существо хочет перейти
			creature.angle = creature.angle + (all_outs[index][0]-0.5)
			# print(f"{all_outs[index][0]:.8f}")
			# Нормализуем угол в диапазон [0, 2π)
			creature.angle = creature.angle % (2 * math.pi)
			# Если угол отрицательный, добавляем 2π чтобы получить положительное значение
			if creature.angle < 0:
				creature.angle += 2 * math.pi

			creature.speed = creature.speed + (all_outs[index][1] - 0.5)
			if creature.speed < -0.5:
				creature.speed = -0.5
			if creature.speed > 0.5:
				creature.speed = 0.5
			newx = creature.x + creature.speed*math.cos(creature.angle)
			newy = creature.y + creature.speed*math.sin(creature.angle)


			# is_ok_to_go Проверяем/применяем правила, по которым существо может или не может перемещаться
			is_ok_to_go = True
			# За пределы карты проверим выход
			if (int(newx) < 0 or int(newx) > self.width-1):
				is_ok_to_go = False
			if (int(newy) < 0 or int(newy) > self.height-1):
				is_ok_to_go = False
			
			# Проверим, что в новой клетке не стена. На стену нельзя переходить.
			if self.get_cell(int(newx),int(newy)) == 1:
				# Существо столкнулось со стеной
				is_ok_to_go = False
				creature.energy -= 0.01
				
			# Меняем или не меняем координаты на новые
			if is_ok_to_go:
				creature.x = newx
				creature.y = newy
			
			# Если существо куснуло - проверить что оно куснуло.
			if all_outs[index][2] > 0.5:
				self.creature_bite(creature)


			# Существо стареет
			creature.age += 1
			# Существо тратит энергию на просто существование в мире
			creature.energy -= 0.01
			# Существо тратит энергию на бег в зависимости от скорости
			# Существо тратит энергию на поворот, в зависимости от резкого поворота
			# Существо тратит энергию на поворот, в зависимости от резкого поворота

		
		if self.is_population_big_enough():
			self.remove_dead_creatures()

		if self.is_population_not_overcrowd():
			self.reprod()
			




	def is_population_big_enough(self):
		# если существ менее 50, то всем существам задать энергию = 1.0
		if len(self.creatures)<50:
			for cr in self.creatures:
				cr.energy = 1.0
			return False
		else:
			return True

	def is_population_not_overcrowd(self):
		if len(self.creatures)>100:
			return False
		else:
			return True

	def reprod(self):
		# Цикл размножения
		baby_creatures = []
		for i in filter(lambda c:c.age in c.birth_ages, self.creatures):
			baby_creatures += i.reprodCreature()
			# # Чтобы не было байби-бума, проверим что максимальное количество существ пока не достигнуто
			# if((len(self.creatures)+len(baby_creatures)) > self.gN_creatures):
			#     print("Существ слишком много, не будем добавлять еще детей " + str(len(self.creatures) +len(baby_creatures)))
			#     break
		self.creatures += baby_creatures

	def creature_bite(self, cr):
		bitex = cr.x + cr.bite_range*math.cos(cr.angle)
		bitey = cr.y + cr.bite_range*math.sin(cr.angle)
		
		# Проверим выход за пределы карты > app.world.dimx-1 mappointer
		if (int(bitex) < 0 or int(bitex) > self.width-1):
			return False
		if (int(bitey) < 0 or int(bitey) > self.height-1):
			return False

		# # Проверим на попытку укусить себя
		#               ДА ПОФИГ, СУЩЕСТВО ТО МОЖЕТ СТОЯТЬ НА ПИЩЕ В ОДНОЙ КЛЕТКЕ, ТАК ЧТО ПУСТЬ КУСАЕТ
		# if (int(bitex) == int(self.x) and int(bitey) == int(self.y)):
		# 	return False
		
		# получим информацию о том, что находится в клетке, которую существо кусает
		biteplace =  self.get_cell(int(bitex), int(bitey))
		if biteplace == 2:
			# Существу повезло, оно укусило пищу. Увеличить энергию существа.
			# print("Существу повезло, оно укусило пищу. Увеличить энергию существа.")
			cr.energy += 0.5
			if cr.energy > 1.0:
				cr.energy = 1.0
			
			# # Уменьшить энергию у пищи.
			# app.world.food_arr["X"+str(int(bitex))+"Y"+str(int(bitey))].foodAviable -= 0.35
			# # Если еда съедена полностью, сотрем ее с карты.
			# if ( app.world.food_arr["X"+str(int(bitex))+"Y"+str(int(bitey))].foodAviable < 0) :
			# 	app.world.delete_food(int(bitex), int(bitey))
			# # Вернем True как сигнал того, что мы поели
			# return True
		# elif biteplace == 3:
		# 	# print ("Существо укусило другое существо")
		# 	# Запишем в лог
		# 	if self.isSelected:
		# 		print('Selected Creature BITE_CREATURE')
		# 	self.history.append(['BITE_CREATURE',self._age])
		# 	# Существу повезло, оно укусило ДРУГОЕ СУЩЕСТВО
		# 	# Увеличить энергию существа.
		# 	self._energy += 0.1
		# 	if self._energy > self.MaxEnergy:
		# 		self._energy = self.MaxEnergy
		# 	# Уменьшить энергию у ДРУГОГО СУЩЕСТВА
		# 	# Надо найти жертву в массиве существ, которое находится по координатам (bitex, bitey)
		# 	# Цикл по всем существам

		# 	biten = app.world.getCreatureByCords(app, bitex, bitey) # куснутое существо
		# 	biten._energy -= 0.3
		# 	# Если у жертвы кончилась энергия
		# 	if biten._energy<0:
		# 		# Подотрем карту под жертвой
		# 		app.world.map[int(biten.y)][int(biten.x)] = biten.standingon


			# Вернем True как сигнал того, что мы поели
			return True

		

		# # Столкновение с едой
		# self._energy += self.app.gFood_bonus # Нихера непонятно, откуда тут известно значение self.app, но как видно - оно известно. я проверил
		# # print ("self.app.gFood_bonus = "+str(self.app.gFood_bonus))
		# if self._energy > self.MaxEnergy:
		#     self._energy = self.MaxEnergy
		# # print ("Существо покушало: " + str(self._energy))
		# self.x = newx
		# self.y = newy
		# # Еда съедена. Сотрем ее с карты
		# mappointer[int(self.y)][int(self.x)] = 0
		# # Залогируем что поели
		# # self.log("Ням-ням-ням. Поело. Энергия возросла на 0.5")
		# self.history.append(['BITE',self._age])
		# pass

		# Если укусили воздух - возвращаем false
		return False
		


	def remove_dead_creatures(self):
		"""Удаляет всех существ с энергией меньше 0"""
		self.creatures = [creature for creature in self.creatures 
							if creature.energy >= 0]
	
	@staticmethod
	@jit(nopython=True)
	def fast_get_all_visions(map, creatures_pos):
	    step = 0.9 # шаг перемещения взгляда (для raycast - дистанция на котороую двигаем вперед указатель)
	    resolution = 15 # разрешение взгляда - по сути сколько лучше отправит raycast?
	    angleofview = 1.04719 # это примерно 60 градусов
	    anglestep = 1.04719 / resolution
	    distance_of_view = creatures_pos[0,3]
	    dots_in_ray = int(distance_of_view/step)
	    n_creatures = creatures_pos.shape[0] # Выясним сколько существ в массиве creatures_pos
	    
	    raycast_dots = np.zeros((n_creatures*resolution*dots_in_ray, 2), dtype='float') # тут хранятся просто точки, и двойка тут означает просто X,Y
	    raycast_dots_idx=0
	    all_visions = np.zeros((n_creatures, resolution*3), dtype='int') # ВСЕГДА ОДИНАКОВЫЙ РАЗМЕР. 15 пикселов для 5 существ
	    
	    for index, cr in enumerate(creatures_pos):
	        visionRed = np.zeros(15, dtype='int')
	        visionGreen = np.zeros(15, dtype='int')
	        visionBlue = np.zeros(15, dtype='int')
	        vision_idx = 0

	        for a in range(resolution):
	            adelta = -1*angleofview/2 + a*anglestep # угол текущего луча
	            d = 0 # длина текущего луча, которую постепенно увеличиваем
	            cur_vision = 0
	            while d < cr[3]:
	                d += step
	                x = cr[0] + d*math.cos(cr[2]+adelta)
	                y = cr[1] + d*math.sin(cr[2]+adelta)
	                if int(x) == int(cr[0]) and int(y) == int(cr[1]):
	                    continue # Если смотрит на свое тело, то пропустим эту итерацию
	                if True: #index == 0
	                    # сохраним точку в массив точек
	                    raycast_dots[raycast_dots_idx] = np.array([x,y])
	                    raycast_dots_idx+=1
	                
	                dot = 0
	                ix = int(x)
	                iy = int(y)
	                mw = map.shape[1]
	                mh = map.shape[0]
	                if ix < 0 or ix >= mw or iy < 0 or iy >= mh:
	                    # за пределами карты → чёрный
	                    visionRed[vision_idx] = 0
	                    visionGreen[vision_idx] = 0
	                    visionBlue[vision_idx] = 0
	                    vision_idx += 1
	                    break
	                else:
	                    dot = map[iy,ix]

	                # Если взгляд во что-то уперся, то Сохраняем цвет точки и Прерываем raycast
	                if dot > 0:
	                    cur_vision = dot
	                    # Сюда надо вставлять опреденений цветов и разложение на каналы.
	                    dotColor = np.zeros(3, dtype='int')
	                    if dot == 1:
	                        dotColor = np.array([100,100,100])
	                    elif dot == 2:
	                        dotColor = np.array([255,0,0])
	                    elif dot == 3:
	                        dotColor = np.array([0,0,255])
	                    else:
	                        dotColor = np.array([0,0,0])

	                    # Сюда вставляем искажение цвета, в зависимости от дистанции
	                    # Условие нужно, потому что иногда d улетает больше чем self.viewdistance, 
	                    # тогда цвет станет больше 255
	                    # if d < self.viewdistance:
	                    #     dotColor = Creature.__fadeColors(dotColor , d/self.viewdistance )


	                    # тут переменная dotColor содержит RGB Представление цвета
	                    visionRed[vision_idx] = dotColor[0]
	                    visionGreen[vision_idx] = dotColor[1]
	                    visionBlue[vision_idx] = dotColor[2]
	                    vision_idx += 1
	                    break
	            else:
	                # В этой ветке обслуживаем ситуацию, когда Raycast достиг 
	                # максимальной дистанции взгляда и ничего не увидел
	                visionRed[vision_idx] = 0
	                visionGreen[vision_idx] = 0
	                visionBlue[vision_idx] = 0
	                vision_idx += 1

	        # Превратим массив элементами карты в массив с цветами
	        # далее - ручная конкатенация трех массивов в один
	        visionRGB = np.empty(resolution*3, dtype='int')
	        # Копирую вручную (JIT это любит!)
	        visionRGB[0:15] = visionRed
	        visionRGB[15:30] = visionGreen
	        visionRGB[30:45] = visionBlue
	        # print("visionRed: " + str(visionRed))
	        # print("visionGreen: " + str(visionGreen))
	        # print("visionBlue: " + str(visionBlue))

	        all_visions[index] = visionRGB
	        
	    # print("Длина массива all_visions: " + str(len(all_visions)))
	    # for index,v in enumerate(all_visions):
	    #   print("Длина " + str(index) + " массива vision: " + str(len(v)))
	    return all_visions, raycast_dots
	

	@staticmethod
	def normalize_vision(all_visions):
		"""
		Нормирует массив видения из диапазона 0-255 в диапазон 0.0-1.0
		all_visions: список массивов видения существ (каждый массив из 45 элементов 0...255)
		возвращает: список нормированных массивов (0.0...1.0)
		"""
		normalized_visions = []
		
		for vision in all_visions:
			normalized_vision = [pixel / 255.0 for pixel in vision]
			normalized_visions.append(normalized_vision)
		
		return normalized_visions