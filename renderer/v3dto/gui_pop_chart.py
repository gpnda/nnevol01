# -*- coding: utf-8 -*-
"""
PopulationChart - v3dto версия.

Панель графика размера популяции.

Отображает:
- График численности популяции за последние 1200 тиков
- Минимальное и максимальное значение численности
- Текущее значение численности

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
from typing import List, Optional
from renderer.v3dto.dto import RenderStateDTO


class PopulationChart:
    """
    Панель с графиком численности популяции.
    
    Отображается в нижней части экрана с фиксированными координатами.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает историю популяции из logger.population_size
    - Полностью изолирована от сингльтонов
    """
    
    # Координаты и размеры (совпадают с SelectedCreatureHistory)
    POSITION_X = 4
    POSITION_Y = 505
    WIDTH = 790
    HEIGHT = 65
    
    # Параметры графика
    GRAPH_PADDING = 2
    GRAPH_HEIGHT = 57
    CUSTOM_RIGHT_PADDING = 30
    GRAPH_WIDTH = WIDTH - 2 * GRAPH_PADDING - CUSTOM_RIGHT_PADDING
    MAX_HISTORY_POINTS = 1200  # Показываем последние 1200 тиков
    
    # Цвета
    COLORS = {
        'background': (0, 0, 0),
        'border': (60, 60, 60),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'highlight': (100, 200, 255),
        'graph_background': (30, 30, 30),
        'graph_line': (100, 150, 255),
        'graph_grid': (60, 60, 60),
    }
    
    # Размеры
    BORDER_WIDTH = 2
    PADDING = 5
    LINE_HEIGHT = 25
    FONT_SIZE = 16
    SMALL_FONT_SIZE = 12
    
    def __init__(self):
        """Инициализация панели."""
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.surface.fill(self.COLORS['background'])
        
        # Шрифты для текста
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
            self.small_font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.SMALL_FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.small_font = pygame.font.Font(None, self.SMALL_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """
        Отрисовка панели с графиком численности популяции.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о популяции
        """
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])  # ПОТОМ ОБРАТНО НА background #########################
        
        
        
        # Получаем историю популяции из logger
        from service.logger.logger import logme
        population_history = list(logme.population_size)
        
        # Если история пуста, выводим сообщение
        if not population_history or len(population_history) == 0:
            no_data_text = self.small_font.render("No data yet", True, self.COLORS['label'])
            self.surface.blit(no_data_text, (self.PADDING, self.PADDING + self.LINE_HEIGHT + 20))
            screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
            return
        
        # Берем только последние MAX_HISTORY_POINTS значений
        if len(population_history) > self.MAX_HISTORY_POINTS:
            population_history = population_history[-self.MAX_HISTORY_POINTS:]
        
        # Вычисляем min/max
        min_pop = min(population_history)
        max_pop = max(population_history)
        current_pop = population_history[-1] if population_history else 0
        
        # Если min и max одинаковые, устанавливаем диапазон с небольшим запасом
        if min_pop == max_pop:
            display_min = max(0, min_pop - 1)
            display_max = max_pop + 1
        else:
            display_min = min_pop
            display_max = max_pop
        
        pop_range = display_max - display_min
        if pop_range == 0:
            pop_range = 1
        
        # Рисуем область графика
        graph_x = self.GRAPH_PADDING
        graph_y = self.PADDING
        
        # Фон графика
        pygame.draw.rect(
            self.surface,
            self.COLORS['graph_background'],
            (graph_x, graph_y, self.GRAPH_WIDTH + self.CUSTOM_RIGHT_PADDING, self.GRAPH_HEIGHT),
            0
        )
        
        # Граница графика
        pygame.draw.rect(
            self.surface,
            self.COLORS['border'],
            (graph_x, graph_y, self.GRAPH_WIDTH + self.CUSTOM_RIGHT_PADDING, self.GRAPH_HEIGHT),
            self.BORDER_WIDTH
        )
        
        # Рисуем горизонтальную сетку (3 линии)
        grid_y_positions = [
            graph_y + self.GRAPH_HEIGHT * i // 3
            for i in range(4)
        ]
        for grid_y in grid_y_positions:
            pygame.draw.line(
                self.surface,
                self.COLORS['graph_grid'],
                (graph_x, grid_y),
                (graph_x + self.GRAPH_WIDTH + self.CUSTOM_RIGHT_PADDING, grid_y),
                1
            )
        
        # Преобразуем значения в координаты графика
        if len(population_history) > 1:
            points = []
            for i, pop_value in enumerate(population_history):
                x = graph_x + (i / (len(population_history) - 1)) * self.GRAPH_WIDTH
                # Нормализуем значение на высоту графика
                normalized = (pop_value - display_min) / pop_range
                y = graph_y + self.GRAPH_HEIGHT - (normalized * self.GRAPH_HEIGHT)
                points.append((int(round(x)), int(round(y))))
            
            # Рисуем линию графика
            if len(points) > 1:
                pygame.draw.lines(self.surface, self.COLORS['graph_line'], False, points, 2)

            
            # Рисуем текущую точку (кружок в конце)
            if len(points) > 0:
                last_point = points[-1]
                pygame.draw.circle(self.surface, self.COLORS['highlight'], last_point, 4)
        
        # Выводим статистику справа от графика
        stats_x = graph_x + 10
        stats_y = graph_y + 5
        
        stats_text = [
            f"Min: {min_pop}",
            f"Max: {max_pop}",
            f"Now: {current_pop}",
        ]
        
        for i, text in enumerate(stats_text):
            stat_surface = self.small_font.render(text, True, self.COLORS['label'])
            self.surface.blit(stat_surface, (stats_x, stats_y + i * 15))
        
        # Выводим общее количество тиков
        # tick_count = len(population_history)
        # tick_text = self.small_font.render(f"Ticks: {tick_count}", True, self.COLORS['text'])
        # self.surface.blit(tick_text, (self.PADDING, self.POSITION_Y + self.HEIGHT - 20))
        # Заголовок
        title_text = self.font.render("Population Size", True, self.COLORS['highlight'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        # Отрисовка финальной поверхности
        screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
