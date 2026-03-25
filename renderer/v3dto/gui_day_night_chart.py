# -*- coding: utf-8 -*-
"""
DayNightChart - v3dto версия.

Панель с графиком истории освещенности (день/ночь).

Отображает:
- График значений освещенности за последние 300 тиков
- Минимальное и максимальное значение освещенности
- Текущее значение освещенности
- Визуальное разделение между днем и ночью (светлые/темные зоны)

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
import numpy as np
from typing import List, Optional
from renderer.v3dto.dto import RenderStateDTO


class DayNightChart:
    """
    Панель с графиком истории освещенности (день/ночь).
    
    Отображается с фиксированными координатами.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает история освещенности из render_state.world.day_light_ndarr
    - Полностью изолирована от сингльтонов
    """
    
    # Координаты и размеры
    POSITION_X = 930
    POSITION_Y = 9
    WIDTH = 310
    HEIGHT = 35
    
    # Параметры графика
    GRAPH_PADDING = 2
    GRAPH_HEIGHT = 25
    CUSTOM_RIGHT_PADDING = 0
    GRAPH_WIDTH = WIDTH - 2 * GRAPH_PADDING
    MAX_HISTORY_POINTS = 300  # Показываем последние 300 тиков (максимум на ndarray)
    NOW_MARK_INDEX = 150
    
    # Цвета
    COLORS = {
        'background': (0, 0, 0),
        'border': (60, 60, 60),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'highlight': (255, 200, 100),  # Оранжевый для дня/ночи
        'graph_background': (20, 20, 70),
        'graph_line': (255, 200, 100),  # Оранжевая линия освещенности
        'graph_grid': (40, 40, 40),
        'now_line': (120, 220, 255),
        'day_zone': (100, 100, 30),  # Темно-желтая зона для дневного света
        'night_zone': (30, 30, 50),  # Темно-синяя зона для ночи
    }
    
    # Размеры
    BORDER_WIDTH = 1
    PADDING = 3
    FONT_SIZE = 16
    
    def __init__(self):
        """Инициализация панели."""
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифт для текста
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """
        Отрисовка панели с графиком освещенности.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными об освещенности
        """
        # Очистка поверхности
        self.surface.fill((0, 0, 0, 0))
        
        # Получаем историю освещенности
        day_light_history = render_state.world.day_light_ndarr
        
        # Если история не существует или пуста, выводим сообщение
        if day_light_history is None or len(day_light_history) == 0:
            no_data_text = self.font.render("No daylight data", False, self.COLORS['label'])
            self.surface.blit(no_data_text, (self.PADDING, self.PADDING))
            screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
            return
        
        # Конвертируем в список если это ndarray
        if isinstance(day_light_history, np.ndarray):
            light_values = day_light_history.tolist()
        else:
            light_values = list(day_light_history)
        
        # Берем только последние MAX_HISTORY_POINTS значений
        if len(light_values) > self.MAX_HISTORY_POINTS:
            light_values = light_values[-self.MAX_HISTORY_POINTS:]
        
        # Вычисляем min/max
        min_light = min(light_values)
        max_light = max(light_values)
        current_light = light_values[-1] if light_values else 0.0
        
        # Если min и max одинаковые, устанавливаем диапазон
        if min_light == max_light:
            display_min = max(0.0, min_light - 0.1)
            display_max = max_light + 0.1
        else:
            display_min = min_light
            display_max = max_light
        
        light_range = display_max - display_min
        if light_range == 0:
            light_range = 1
        
        # Рисуем область графика
        graph_x = self.GRAPH_PADDING
        graph_y = self.PADDING
        
        # Тень графика
        pygame.draw.rect(
            self.surface,
            self.COLORS['background'],
            (graph_x+5, graph_y+5, self.GRAPH_WIDTH, self.GRAPH_HEIGHT),
            0
        )

        # Фон графика
        pygame.draw.rect(
            self.surface,
            self.COLORS['graph_background'],
            (graph_x, graph_y, self.GRAPH_WIDTH, self.GRAPH_HEIGHT),
            0
        )
        
        # Граница графика
        pygame.draw.rect(
            self.surface,
            self.COLORS['border'],
            (graph_x, graph_y, self.GRAPH_WIDTH, self.GRAPH_HEIGHT),
            self.BORDER_WIDTH
        )
        
        # Рисуем горизонтальную сетку (2 линии)
        grid_y_positions = [
            graph_y + self.GRAPH_HEIGHT * i // 2
            for i in range(3)
        ]
        for grid_y in grid_y_positions:
            pygame.draw.line(
                self.surface,
                self.COLORS['graph_grid'],
                (graph_x, grid_y),
                (graph_x + self.GRAPH_WIDTH, grid_y),
                1
            )

        # Вертикальная отсечка "Now" на 150-й позиции массива.
        # Для истории в 299/300 точек это центр графика (текущий момент).
        if len(light_values) > 1:
            now_index = min(self.NOW_MARK_INDEX, len(light_values) - 1)
            now_x = graph_x + (now_index / (len(light_values) - 1)) * self.GRAPH_WIDTH
            now_x_int = int(round(now_x))
            pygame.draw.line(
                self.surface,
                self.COLORS['now_line'],
                (now_x_int, graph_y),
                (now_x_int, graph_y + self.GRAPH_HEIGHT),
                1
            )
            light_percent = int(current_light * 100)
            value_text = f"{light_percent}%"
            now_surface = self.font.render(f"Now: {value_text}", False, self.COLORS['now_line'])
            now_text_x = min(self.WIDTH - 24, now_x_int + 2)
            self.surface.blit(now_surface, (now_text_x, graph_y + 7))
        
        # Преобразуем значения в координаты графика
        if len(light_values) > 1:
            points = []
            for i, light_value in enumerate(light_values):
                x = graph_x + (i / (len(light_values) - 1)) * self.GRAPH_WIDTH
                # Нормализуем значение на высоту графика (0 = вверху, 1 = внизу)
                normalized = (light_value - display_min) / light_range
                y = graph_y + self.GRAPH_HEIGHT - (normalized * self.GRAPH_HEIGHT)
                points.append((int(round(x)), int(round(y))))
            
            # Рисуем линию графика
            if len(points) > 1:
                pygame.draw.lines(self.surface, self.COLORS['graph_line'], False, points, 2)
            
            # Рисуем текущую точку (кружок в конце)
            if len(points) > 0:
                now_point = points[150]
                pygame.draw.circle(self.surface, self.COLORS['highlight'], now_point, 3)
        elif len(light_values) == 1:
            # Если одна точка, рисуем ее
            x = graph_x + self.GRAPH_WIDTH // 2
            normalized = (light_values[0] - display_min) / light_range
            y = graph_y + self.GRAPH_HEIGHT - (normalized * self.GRAPH_HEIGHT)
            pygame.draw.circle(self.surface, self.COLORS['highlight'], (int(x), int(y)), 3)
        
        # Выводим заголовок и текущее значение
        header_text = f"Daylight"
        
        
        title_surface = self.font.render(header_text, False, self.COLORS['highlight'])
        # value_surface = self.font.render(value_text, False, self.COLORS['label'])
        
        self.surface.blit(title_surface, (self.PADDING + 2, self.PADDING+7))
        # self.surface.blit(value_surface, (self.WIDTH - 50, self.PADDING+7))
        
        # Отрисовка финальной поверхности
        screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
