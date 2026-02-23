# -*- coding: utf-8 -*-

from creature import Creature
#from nn.nn_torch_rnn import NeuralNetwork
from nn.my_handmade_ff import NeuralNetwork
import random
import math
import numpy as np
from numba import jit
from simparams import sp

from service.logger.logger import logme
from service.debugger.debugger import debug



class World():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.map = np.zeros((height, width), dtype='int')
		self.walls_map = np.zeros((height, width), dtype='int')
		self.creatures = []
		self.foods = []
		self.tick = 0


		


	
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

	def get_creature_by_id(self, creature_id):
		for creature in self.creatures:
			if creature.id == creature_id:
				return creature
		return None

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
		debug.set("raycast_dots", raycast_dots) # Тут все `numpy.float32`

		debug.set("all_visions", all_visions) # Тут все `numpy.float32`
		
		
		# 2. Мышление (параллельно)  
		# Подготавливаем данные для быстрой функции 
		# эта функция склеивает все сетки в векторизованные массивы: l1_weights, l2_weights, l1_bias, l2_bias)
		creatures_nns = NeuralNetwork.prepare_calc(self.creatures)
		# , но на выход она выдает обычный python кортеж (или если не получится, то список), 
		# содержащий эти самые numpy ndarray: l1_weights, l2_weights, l1_bias, l2_bias ...
		
		# запускаем быструю функцию
		all_outs = NeuralNetwork.make_all_decisions(all_visions, creatures_nns)
		# all_outs[] is a numpy ndarray [angle_delta, speed_delta, bite]

		debug.set("all_outs", all_outs) # Тут все `numpy.float32`

		# 3. Перемещаем существ, согласно выходам нейросетей
		for index, creature in enumerate(self.creatures):


			ang, spd, newx, newy = World.apply_outs( # По моей задумке - это должен быть статичный метод класса World
				creature_x = creature.x,
				creature_y = creature.y,
				creature_angle = creature.angle,
				creature_speed = creature.speed,
				out_angle = all_outs[index][0],  # выход нейросети для angle
				out_speed = all_outs[index][1],  # выход нейросети для speed
				)
			creature.angle = ang
			creature.speed = spd
			# newx=newx #     просто демонстрирую, что этот метод возвращает и новые координаты тоже
			# newy=newy #      и что дальше будет использоваться эта четверка уже расчитанных переменных
			

			# is_ok_to_go Проверяем/применяем правила, по которым существо может или не может перемещаться
			is_ok_to_go = True
			# За пределы карты проверим выход
			if int(newx) < 0 or int(newx) > self.width-1 or int(newy) < 0 or int(newy) > self.height-1:
				is_ok_to_go = False
			
			# Проверим, что в новой клетке не стена. На стену нельзя переходить.
			if self.get_cell(int(newx),int(newy)) == 1:
				# Существо столкнулось со стеной
				is_ok_to_go = False
				creature.energy -= sp.energy_loss_collision     # штраф за столкновение со стеной
				
			# Меняем или не меняем координаты на новые
			if is_ok_to_go:
				creature.x = newx
				creature.y = newy
			
			# Если существо куснуло - проверить что оно куснуло.
			creature.bite_effort = float(all_outs[index][2])
			if creature.bite_effort > 0.5:
				self.creature_bite(creature)


			creature.update()
			
			

			# Контроль размера популяции
			# По идее в будущем волны изобилия можно двигать, подстраивая их под себя, чтобы не тянуть время
			# Например, если популяция вымирает - сдвинуть волну изобилия до точки когда начинается рост изобилия.
			# И наоборот, если популяиця слишком расплодилась, то можно сдвинуть волну изобилия до точки, 
			# когда начинается скудный сезон - пищи становится все меньше.
			# Для этого надо ввести переменную "slide_to_rise", "slide_to_descent"
			# И тогда пока slide_to_rise==True, не надо повторно сдвигать изобилие на рост, потому что этот флаг
			# говорит о том, что изобилие уже сдвинули, и пока оно не 
			# станет slide_to_descent - сигмоиду не надо никуда сдвигать.
			#
			# С другой стороны, можно не париться, пусть скудный сезон продолжается столько сколько потребуется, 
			# Потому что мы Остановили мутации на 50 существах, и запретили смерть на 10 существах.
			# И теперь мы можем не переживать о вымирании. Точно также и про перенаселение.
			#
			# Но пока я не делаю сезоны и волны изобилия. Пока я должен сделать именно: 
			# 1. Предотвратить вымирание популяции
			# 2. Предотвратить перенаселенность мира
			# Для этого в классе Worldя напишу приватный метод control_population()
			# Внутри него должны быть методы которые в штатном режиме реализуют смерть и рождение
			# А в крайние отрезки - запрещает смерть или запрещает размножение.

		self.control_population()

		self.proceed_food()

		self.tick += 1

		# TODO: Надо ли это вынести в Application???
		# Регулировка количества пищи в мире
		if self.tick % 50 == 0:
			self.regulate_food()

		# print("POPULATION: " + str(len(self.creatures)))
		# print("tick: " + str(self.tick) + "   | cr[0].age:"+ str(self.creatures[0].age) + " cr[0].energy:" + str(self.creatures[0].energy) + "   | cr[0].birth_ages: " + str(self.creatures[0].birth_ages) )

			
	def regulate_food(self):
		# добавление или уничтожение пищи из массива world.foods[] в соответствии с  sim_food_amount
		if (sp.food_amount > len(self.foods)):
			# добавим недостающее количество пищи
			add_amount = sp.food_amount - len(self.foods)
			from world_generator import WorldGenerator
			WorldGenerator.generate_food(self, add_amount)
		else:
			# пищи слишком много, удалим часть
			self.foods = self.foods[0:sp.food_amount]
		
		# # Рандомизировать положение пищи.
		# for f in self.foods:
		#     f.setPositionRandom(self)




	def control_population(self):

		# Включить/Выключить мутации
		if len(self.creatures) <= 50 or len(self.creatures) >= 900:
			sp.allow_mutations = 0
		else:
			sp.allow_mutations = 1

		# if len(self.creatures)>=20:  #TODO не стал разбираться, но с этим условием - появляются существа с отрицательной энергией.
		self.death()
		
		if len(self.creatures)<950:
			self.reprod()

	def proceed_food(self):
		# Цикл обработки пищи
		self.foods = [food for food in self.foods if food.nutrition >= 0]

	def change_food_capacity(self):
		# Изменение параметра еды в зависимости от текущей популяции
		for f in self.foods:
			f.nutrition = sp.food_energy_capacity

	def death(self):
		"""
		Удаляет всех существ с энергией меньше 0, если после удаления останется 
		не менее 10 существ с положительной энергией
		"""
		
		# Считаем количество существ с энергией > 0
		positive_energy_count = sum(1 for creature in self.creatures if creature.energy > 0)
		
		# Если существ с энергией > 0 меньше 10 шт, то не фильтруем
		if positive_energy_count < 10:
			# Именно тут надо поднять всем энергию, потому что существ в популяции может быть 11, 
			# но по факту все они уже мертвы (с отрицательной энергией)
			for cr in self.creatures:
				if cr.energy <= 0:
					cr.energy = 1.0
					cr.age = random.randint(0, 100)
			return
		
		# Здесь надо как-то сохранить статистику по умершим существам
		# Пока кот так в лоб TODO потом надо както оптимизировтаь этот код
		for cr in self.creatures:
			if cr.energy < 0:
				logme.write_death_stats(
					id=cr.id,
					generation=cr.generation,
					age=cr.age,
					reprod_ages=cr.birth_ages
				)

		# Иначе удаляем существ с энергией < 0
		self.creatures = [creature for creature in self.creatures if creature.energy >= 0]
	
		

	def reprod(self):
		# Цикл размножения
		baby_creatures = []
		for i in filter(lambda c:c.age in c.birth_ages, self.creatures):
			i_children = i.reprodCreature()
			baby_creatures += i_children
			# print("Существо с ID " + str(i.id) + " родило " + str(len(i_children)) + " детей.")
			logme.log_event(creature_id=i.id, tick=self.tick, event_type="CREATE_CHILD", value=len(i_children))
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
			logme.log_event(creature_id=cr.id, tick=self.tick, event_type="EAT_FOOD", value=1)
			# Существу повезло, оно укусило пищу. Увеличить энергию существа.
			cr.gain_energy(sp.energy_gain_from_food)
			
			# # Уменьшить энергию у пищи.
			bitten_food = self.bitten_food( int(bitex), int(bitey) )

			bitten_food.decrement()


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
		

	def bitten_food(self, x, y):
		for food in self.foods:
			if food.x == x and food.y == y:
				return food
		return None







	@staticmethod
	@jit(nopython=True, fastmath=True)
	def fast_get_all_visions(map, creatures_pos):
		step = 0.9 # шаг перемещения взгляда (для raycast - дистанция на котороую двигаем вперед указатель)
		resolution = 15 # разрешение взгляда - по сути сколько лучше отправит raycast?
		angleofview = 1.04719 # это примерно 60 градусов
		anglestep = 1.04719 / resolution
		distance_of_view = creatures_pos[0,3]
		dots_in_ray = int(distance_of_view/step)
		n_creatures = creatures_pos.shape[0] # Выясним сколько существ в массиве creatures_pos
		
		max_raycast_dots = n_creatures * resolution * dots_in_ray + 1000  # 1000 - это запас на случай переполнения
		raycast_dots = np.zeros((max_raycast_dots, 2), dtype='float') # тут хранятся просто точки, и двойка тут означает просто X,Y
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
		# Обрезаем массив до реального размера (удаляем неиспользованные нули в конце)
		raycast_dots = raycast_dots[:raycast_dots_idx]
		# 18 000 против 166 000. Конечно надо обрезку делать
		# print("raycast_dots_idx: " + str(raycast_dots_idx) + "   | raycast_dots len: " + str(len(raycast_dots)))
		return all_visions / 255.0, raycast_dots


	def simparams_print(self):
		"""Вывод всех параметров симуляции в консоль."""
		print("=== SimParams ===")
		print(f"mutation_probability: {sp.mutation_probability}")
		print(f"mutation_strength: {sp.mutation_strength}")
		print(f"creature_max_age: {sp.creature_max_age}")
		print(f"food_amount: {sp.food_amount}")
		print(f"food_energy_capacity: {sp.food_energy_capacity}")
		print(f"food_energy_chunk: {sp.food_energy_chunk}")
		print(f"reproduction_ages: {sp.reproduction_ages} type: {type(sp.reproduction_ages)}")
		print(f"reproduction_offsprings: {sp.reproduction_offsprings}")
		print(f"energy_cost_tick: {sp.energy_cost_tick}")
		print(f"energy_cost_speed: {sp.energy_cost_speed}")
		print(f"energy_cost_rotate: {sp.energy_cost_rotate}")
		print(f"energy_cost_bite: {sp.energy_cost_bite}")
		print(f"energy_gain_from_food: {sp.energy_gain_from_food}")
		print(f"energy_gain_from_bite_cr: {sp.energy_gain_from_bite_cr}")
		print(f"energy_loss_bitten: {sp.energy_loss_bitten}")
		print(f"energy_loss_collision: {sp.energy_loss_collision}")
	
	@staticmethod
	def apply_outs(creature_x, creature_y, creature_angle, creature_speed, out_angle, out_speed):
		
		# Расчитываем новые координаты, куда существо хочет перейти
		new_angle = creature_angle + (float(out_angle)-0.5)
		# print(f"{all_outs[index][0]:.8f}")
		# Нормализуем угол в диапазон [0, 2π)
		new_angle = new_angle % (2 * math.pi)
		# Если угол отрицательный, добавляем 2π чтобы получить положительное значение
		# @TODO Вообще это интересный вопрос - этот разрыв в управлении углом существа (2π) - создает ли это помехи в процессе отбора?
		if new_angle < 0:
			new_angle += 2 * math.pi

		new_speed = creature_speed + (float(out_speed) - 0.5)
		if new_speed < -0.5:
			new_speed = -0.5
		if new_speed > 0.5:
			new_speed = 0.5
		newx = creature_x + new_speed*math.cos(new_angle)
		newy = creature_y + new_speed*math.sin(new_angle)

		return new_angle, new_speed, newx, newy


	