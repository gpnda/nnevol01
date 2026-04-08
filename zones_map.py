# -*- coding: utf-8 -*-
"""Система зон (гнёзда и открытые области) для симуляции."""

import numpy as np
import random


class ZonesMap:
	"""
	Система зон определяет области гнёзд (indoor) и открытые области (outdoor).
	
	Загружается из CSV карты, где:
	- '9' = indoor zones (гнёзда)
	- '0' = outdoor zones (открытые)
	- '1' = walls (не используются для распределения пищи)
	
	Кэширует списки пикселей для быстрого случайного выбора.
	"""
	
	ZONE_INDOOR = 9
	ZONE_OUTDOOR = 0
	ZONE_WALL = 1
	
	def __init__(self, width: int, height: int):
		"""Инициализирует карту зон."""
		self.width = width
		self.height = height
		# Карта зон: 0=outdoor, 9=indoor, 1=walls
		self.zones_map = np.zeros((height, width), dtype='int')
		
		# Кэшированные списки пикселей для быстрого доступа
		self.indoor_pixels = []
		self.outdoor_pixels = []
	
	def generate_lefthalf_zone(self, walls_map: np.ndarray) -> None:
		"""
		Для случайной карты:
		- левая половина свободных клеток -> indoor (норки)
		- правая половина свободных клеток -> outdoor (снаружи)
		- стены остаются стенами
		"""
		if walls_map.shape != (self.height, self.width):
			raise ValueError(
				f"walls_map shape {walls_map.shape} != ({self.height}, {self.width})"
			)

		self.zones_map.fill(self.ZONE_WALL)
		split_x = self.width // 2

		for y in range(self.height):
			for x in range(self.width):
				if int(walls_map[y, x]) == self.ZONE_WALL:
					self.zones_map[y, x] = self.ZONE_WALL
				elif x < split_x:
					self.zones_map[y, x] = self.ZONE_INDOOR
				else:
					self.zones_map[y, x] = self.ZONE_OUTDOOR

		# Единая точка построения кэшей indoor/outdoor
		self._build_pixel_caches()
	
	def load_from_csv(self, raw_csv_data: list) -> None:
		"""
		Загружает информацию о зонах из сырых данных CSV.
		
		Args:
		    raw_csv_data: Список списков значений из CSV (до преобразования '9' в '0')
		                 Размеры должны совпадать с width и height
		"""
		if not raw_csv_data:
			raise ValueError("raw_csv_data is empty")
		
		height = len(raw_csv_data)
		if height != self.height:
			raise ValueError(f"CSV height {height} != zones_map height {self.height}")
		
		# Заполняем карту зон на основе CSV данных
		for y, row in enumerate(raw_csv_data):
			for x, cell_value in enumerate(row):
				if x >= self.width:
					break
				cell_int = int(cell_value)
				
				# Определяем тип зоны
				if cell_int == self.ZONE_INDOOR:
					self.zones_map[y, x] = self.ZONE_INDOOR
				elif cell_int == self.ZONE_WALL or cell_int == 1:
					self.zones_map[y, x] = self.ZONE_WALL
				else:
					# Всё остальное — outdoor
					self.zones_map[y, x] = self.ZONE_OUTDOOR
		
		# Предварительно вычисляем кэши пикселей
		self._build_pixel_caches()
	
	def _build_pixel_caches(self) -> None:
		"""
		Предварительно вычисляет списки indoor и outdoor пикселей
		для быстрого случайного выбора.
		"""
		self.indoor_pixels = []
		self.outdoor_pixels = []
		
		for y in range(self.height):
			for x in range(self.width):
				zone = self.zones_map[y, x]
				if zone == self.ZONE_INDOOR:
					self.indoor_pixels.append((x, y))
				elif zone == self.ZONE_OUTDOOR:
					self.outdoor_pixels.append((x, y))
		
		if not self.indoor_pixels:
			raise ValueError("No indoor pixels found in zones_map")
		if not self.outdoor_pixels:
			raise ValueError("No outdoor pixels found in zones_map")
	
	def get_random_indoor_pixel(self) -> tuple:
		"""
		Возвращает координаты (x, y) случайного пикселя внутри гнезда.
		
		Returns:
		    Tuple (x, y) с координатами случайного indoor пикселя
		"""
		if not self.indoor_pixels:
			raise RuntimeError("No indoor pixels available. Call load_from_csv() first.")
		return random.choice(self.indoor_pixels)
	
	def get_random_outdoor_pixel(self) -> tuple:
		"""
		Возвращает координаты (x, y) случайного пикселя вне гнезда.
		
		Returns:
		    Tuple (x, y) с координатами случайного outdoor пикселя
		"""
		if not self.outdoor_pixels:
			raise RuntimeError("No outdoor pixels available. Call load_from_csv() first.")
		return random.choice(self.outdoor_pixels)
	
	def is_indoor(self, x: float, y: float) -> bool:
		"""
		Проверяет, находится ли координата внутри гнезда.
		
		Args:
		    x: X-координата (может быть float)
		    y: Y-координата (может быть float)
		
		Returns:
		    True если координата в indoor зоне, иначе False
		"""
		ix = int(x)
		iy = int(y)
		
		# Граничные проверки
		if ix < 0 or ix >= self.width or iy < 0 or iy >= self.height:
			return False
		
		zone = self.zones_map[iy, ix]
		return zone == self.ZONE_INDOOR
