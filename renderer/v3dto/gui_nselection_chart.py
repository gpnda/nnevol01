# -*- coding: utf-8 -*-
"""
NSelectionChart - v3dto версия.

Гистограмма смертей по возрастам существ.

Отображает:
- Гистограмму распределения смертей по возрастам
- Минимальное и максимальное значение возраста
- Текущее количество смертей

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
import numpy as np
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class NSelectionChart:
    """
    Панель с гистограммой смертей по возрастам.
    
    Отображается в нижней части экрана с фиксированными координатами.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает статистику смертей из logger.get_death_stats_as_ndarray()
    - Полностью изолирована от сингльтонов
    """
    
    # Координаты и размеры (совпадают с PopulationChart, кроме ширины)
    POSITION_X = 810
    POSITION_Y = 505
    WIDTH = 400
    HEIGHT = 65
    
    # Параметры графика
    GRAPH_PADDING = 2
    GRAPH_HEIGHT = 57
    GRAPH_WIDTH = WIDTH - 2 * GRAPH_PADDING - 100
    
    # Цвета
    COLORS = {
        'background': (0, 0, 0),
        'border': (60, 60, 60),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'highlight': (100, 200, 255),
        'graph_background': (30, 30, 30),
        'graph_bar': (255, 100, 100),
        'graph_grid': (60, 60, 60),
    }
    
    # Размеры
    BORDER_WIDTH = 2
    PADDING = 5
    LINE_HEIGHT = 25
    FONT_SIZE = 16
    SMALL_FONT_SIZE = 12
    
    def filter_post_mortum_reprod_ages(data):
        # cut off reproduction ages older then death age
        for i in range(len(data)):
            death_age = data['age'][i]
            reprod_ages_list = data['reprod_ages'][i].tolist()
            filtered_reprod_ages = [age for age in reprod_ages_list if age < death_age]
            # pad with -1 to keep the shape
            while len(filtered_reprod_ages) < 3:
                filtered_reprod_ages.append(-1)
            data['reprod_ages'][i] = np.array(filtered_reprod_ages, dtype=np.int32)
        return data

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
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка панели с гистограммой смертей по возрастам.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о смертях
        """
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Получаем статистику смертей из логгера
        from service.logger.logger import logme
        death_data = logme.get_death_stats_as_ndarray()
        # death_data = death_data[-100:]  # Обрежем данные, нужны только последние 100 смертей, это как бы актуальный график
        
        # Если статистика пуста, выводим сообщение
        if death_data.size == 0:
            no_data_text = self.small_font.render("No deaths yet", True, self.COLORS['label'])
            self.surface.blit(no_data_text, (self.PADDING, self.PADDING + self.LINE_HEIGHT))
            screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
            return
        
        # Извлекаем возрасты из поля 'age' структурированного массива
        ages = death_data['age']
        
        # удалим возрасты размножения старше возраста смерти
        death_data = NSelectionChart.filter_post_mortum_reprod_ages(death_data)

        # извлекаем возрасты размножения
        reprod_ages = death_data['reprod_ages']
        
        if len(ages) == 0:
            no_data_text = self.small_font.render("No deaths yet", True, self.COLORS['label'])
            self.surface.blit(no_data_text, (self.PADDING, self.PADDING + self.LINE_HEIGHT))
            screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
            return
        
        # Вычисляем статистику
        min_age = int(np.min(ages))
        max_age = int(np.max(ages))
        total_deaths = len(ages)
        
        # Если min и max одинаковые, устанавливаем диапазон с запасом
        if min_age == max_age:
            age_range_start = max(0, min_age - 1)
            age_range_end = max_age + 1
        else:
            age_range_start = min_age
            age_range_end = max_age
        
        # Создаём гистограмму смертей
        bins = 50 # age_range_end - age_range_start + 1
        hist_deaths, bin_edges = np.histogram(ages, bins=bins, range=(age_range_start, age_range_end + 1))
        
        # Распаковываем возрасты размножения в плоский массив (фильтруя -1)
        reprod_ages_flat = []
        for reprod_ages_row in reprod_ages:
            for age in reprod_ages_row:
                if age >= 0:  # Пропускаем -1 (padding)
                    reprod_ages_flat.append(age)
        
        # Создаём гистограмму размножения с тем же масштабом и bins
        if len(reprod_ages_flat) > 0:
            hist_reprod, _ = np.histogram(reprod_ages_flat, bins=bins, range=(age_range_start, age_range_end + 1))
        else:
            hist_reprod = np.zeros_like(hist_deaths)
        
        # Нормализуем по максимуму из обеих гистограмм
        max_count = max(np.max(hist_deaths) if len(hist_deaths) > 0 else 1,
                       np.max(hist_reprod) if len(hist_reprod) > 0 else 1)
        if max_count == 0:
            max_count = 1
        
        # Рисуем область графика
        graph_x = self.GRAPH_PADDING
        graph_y = self.PADDING
        
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
                (graph_x + self.GRAPH_WIDTH, grid_y),
                1
            )
        
        # Рисуем столбцы гистограммы
        if len(hist_deaths) > 0:
            bar_width = self.GRAPH_WIDTH / len(hist_deaths)
            for i in range(len(hist_deaths)):
                # Координаты столбца
                bar_x = graph_x + i * bar_width
                bar_height_y = graph_y + self.GRAPH_HEIGHT
                
                # Рисуем столбец смертей (красный)
                if hist_deaths[i] > 0:
                    death_height = (hist_deaths[i] / max_count) * self.GRAPH_HEIGHT
                    pygame.draw.rect(
                        self.surface,
                        self.COLORS['graph_bar'],
                        (int(bar_x), int(bar_height_y - death_height), int(bar_width), int(death_height)),
                        0
                    )
                
                # Рисуем столбец размножения (зелёный) поверх красного
                if hist_reprod[i] > 0:
                    reprod_height = (hist_reprod[i] / max_count) * self.GRAPH_HEIGHT
                    pygame.draw.rect(
                        self.surface,
                        (100, 200, 100),  # Зелёный цвет для размножения
                        (int(bar_x), int(bar_height_y - reprod_height), int(bar_width), int(reprod_height)),
                        0
                    )
        
        # Выводим статистику справа от графика
        stats_x = graph_x + self.GRAPH_WIDTH + 10
        stats_y = graph_y + 5
        
        stats_text = [
            f"Min: {min_age}",
            f"Max: {max_age}",
            f"Deaths: {total_deaths}",
        ]
        
        for i, text in enumerate(stats_text):
            stat_surface = self.small_font.render(text, True, self.COLORS['label'])
            self.surface.blit(stat_surface, (stats_x, stats_y + i * 15))
        
        # Заголовок
        title_text = self.font.render("Death by Age", True, self.COLORS['highlight'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Отрисовка финальной поверхности
        screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
