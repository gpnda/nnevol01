# -*- coding: utf-8 -*-
"""
CreatureWeightsWidget - v3dto версия.

Виджет для отображения весов нейросети выбранного существа.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, debugger, logger, creature objects
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
import numpy as np
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class CreatureWeightsWidget:
    """
    Виджет для отображения весов нейросети существа.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает данные о существе из render_state.selected_creature
    - Полностью изолирована от сингльтонов
    """
    
    # Координаты и размеры
    WIDGET_X = 370
    WIDGET_Y = 58
    WIDTH = 750
    HEIGHT = 475
    
    # Цвета
    COLORS = {
        'background': (20, 20, 30),
        'border': (100, 150, 200),
        'text': (200, 200, 200),
        'title': (0, 200, 255),
        'placeholder': (150, 150, 150),
    }
    
    # Размеры
    BORDER_WIDTH = 0
    PADDING = 10
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    # Размеры для отрисовки весов
    MATRIX_CELL_SIZE = 2  # размер одного пиксела матрицы
    VECTOR_CELL_HEIGHT = 3  # высота вектора в пикселях
    
    def __init__(self):
        """Инициализация виджета без зависимостей."""
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифт для текста
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def _value_to_color(self, value: float) -> Tuple[int, int, int]:
        """
        Преобразует значение веса в RGB цвет.
        
        -1 → синий (0, 0, 255)
         0 → серый (128, 128, 128)
        +1 → красный (255, 0, 0)
        
        Args:
            value: float значение в диапазоне примерно [-1, +1]
            
        Returns:
            Tuple (R, G, B) где каждый компонент 0-255
        """
        # Зажимаем значение в диапазон [-1, +1]
        clamped = np.clip(float(value), -1.0, 1.0)
        
        if clamped < 0:
            # Интерполяция от серого к синему
            t = -clamped  # t в диапазоне [0, 1]
            r = int(128 * (1 - t))
            g = int(128 * (1 - t))
            b = int(128 + 127 * t)
        else:
            # Интерполяция от серого к красному
            t = clamped  # t в диапазоне [0, 1]
            r = int(128 + 127 * t)
            g = int(128 * (1 - t))
            b = int(128 * (1 - t))
        
        return (r, g, b)
    
    def _draw_matrix(self, surface: pygame.Surface, matrix: np.ndarray,
                     x: int, y: int, max_width: int, max_height: int,
                     label: str) -> int:
        """
        Отрисовывает матрицу весов как 2D сетку цветных квадратиков.
        
        Args:
            surface: pygame Surface для отрисовки
            matrix: numpy array с весами (rows x cols)
            x, y: начальные координаты
            max_width, max_height: максимальный размер для размещения
            label: название параметра (w1_x, w2, и т.д.)
            
        Returns:
            int: высота, занятая блоком (для расчета следующей позиции y)
        """
        rows, cols = matrix.shape
        
        # Рассчитываем размер каждого квадратика, чтобы влезть в max_width
        cell_size = max(1, min(max_width // cols, self.MATRIX_CELL_SIZE))
        
        # Если матрица слишком большая, масштабируем
        if cols * cell_size > max_width:
            cell_size = max(1, max_width // cols)
        
        matrix_width = cols * cell_size
        matrix_height = rows * cell_size
        
        # Рисуем матрицу
        for row in range(rows):
            for col in range(cols):
                value = matrix[row, col]
                color = self._value_to_color(value)
                
                rect = pygame.Rect(
                    x + col * cell_size,
                    y + 20 + row * cell_size,  # +20 для заголовка
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(surface, color, rect)
                
        
        # Рисуем label
        label_str = f"{label} {matrix.shape[0]}×{matrix.shape[1]}"
        label_text = self.font.render(label_str, True, self.COLORS['text'])
        surface.blit(label_text, (x, y))
        
        # Возвращаем высоту блока (label + матрица + отступ)
        return matrix_height + 25
    
    def _draw_vector(self, surface: pygame.Surface, vector: np.ndarray,
                    x: int, y: int, max_width: int, label: str) -> int:
        """
        Отрисовывает вектор весов как горизонтальную полоску.
        
        Args:
            surface: pygame Surface для отрисовки
            vector: numpy array с весами (n,)
            x, y: начальные координаты
            max_width: максимальная ширина
            label: название параметра (b1, b2, и т.д.)
            
        Returns:
            int: высота, занятая блоком (для расчета следующей позиции y)
        """
        n = len(vector)
        cell_width = max(1, max_width // n)
        
        # Если вектор большой, масштабируем
        if n * cell_width > max_width:
            cell_width = max(1, max_width // n)
        
        # Рисуем вектор как полоску
        for i in range(n):
            value = vector[i]
            color = self._value_to_color(value)
            
            rect = pygame.Rect(
                x + i * cell_width,
                y + 20,  # +20 для заголовка
                cell_width,
                self.VECTOR_CELL_HEIGHT
            )
            pygame.draw.rect(surface, color, rect)
        
        # Рисуем label
        label_str = f"{label} {len(vector)}"
        label_text = self.font.render(label_str, True, self.COLORS['text'])
        surface.blit(label_text, (x, y))
        
        # Возвращаем высоту блока
        return self.VECTOR_CELL_HEIGHT + 25
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка виджета с весами существа.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о выбранном существе в creatures_list
        """
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Заголовок
        title_text = self.font.render("Neural Network Weights", True, self.COLORS['title'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Получаем информацию о выбранном существе из creatures_list_state
        if render_state.creatures_list_state is None:
            # Никакое существо не выбрано в creatures_list
            placeholder_text = self.font.render(
                "No creature selected in list",
                True,
                self.COLORS['placeholder']
            )
            self.surface.blit(
                placeholder_text,
                (self.PADDING, self.PADDING + 30)
            )
        else:
            # Получаем ID выбранного существа
            creature_id = render_state.creatures_list_state.detail_creature_id
            
            # Проверяем что creature_id не None
            if creature_id is None:
                placeholder_text = self.font.render(
                    "No creature selected in list",
                    True,
                    self.COLORS['placeholder']
                )
                self.surface.blit(
                    placeholder_text,
                    (self.PADDING, self.PADDING + 30)
                )
            else:
                # Ищем существо по ID в world DTO
                creature_dto = render_state.world.get_creature_by_id(creature_id)
                
                if creature_dto is None:
                    # Существо не найдено (может быть погибло)
                    placeholder_text = self.font.render(
                        f"Creature #{creature_id} not found",
                        True,
                        self.COLORS['placeholder']
                    )
                    self.surface.blit(
                        placeholder_text,
                        (self.PADDING, self.PADDING + 30)
                    )
                else:
                    # Отображаем информацию о существе
                    creature_id_text = self.font.render(
                        f"Creature #{creature_id}",
                        True,
                        self.COLORS['text']
                    )
                    self.surface.blit(
                        creature_id_text,
                        (self.PADDING, self.PADDING + 30)
                    )
                    
                    # Информация о существе
                    info_lines = [
                        f"Age: {creature_dto.age}",
                        f"Energy: {creature_dto.energy:.1f}",
                        f"Health: {creature_dto.health:.1f}",
                        f"Generation: {creature_dto.generation}",
                    ]
                    
                    y_offset = self.PADDING + 60
                    for line in info_lines:
                        line_text = self.font.render(line, True, self.COLORS['placeholder'])
                        self.surface.blit(line_text, (self.PADDING, y_offset))
                        y_offset += 20
                    
                    # Отображение параметров нейросети
                    if render_state.creatures_list_state.nn_parameters:
                        nn_params = render_state.creatures_list_state.nn_parameters
                        
                        # Заголовок
                        nn_title_text = self.font.render(
                            "Neural Network Parameters:",
                            True,
                            self.COLORS['text']
                        )
                        self.surface.blit(nn_title_text, (self.PADDING, y_offset + 10))
                        
                        y_offset += 35
                        
                        # Организуем сетку: 2 колонки для компактности
                        left_x = self.PADDING
                        right_x = self.PADDING + self.WIDTH // 2
                        max_col_width = self.WIDTH // 2 - 2 * self.PADDING
                        max_col_height = 120  # максимальная высота блока
                        
                        left_y = y_offset
                        right_y = y_offset
                        
                        params_list = list(nn_params.items())
                        
                        # Распределяем параметры по колонкам
                        for idx, (param_name, param_info) in enumerate(params_list):
                            data = param_info['data']
                            kind = param_info['kind']
                            
                            # Определяем в какую колонку идти
                            if idx % 2 == 0:
                                # Левая колонка
                                x, y = left_x, left_y
                            else:
                                # Правая колонка
                                x, y = right_x, right_y
                            
                            # Рисуем параметр
                            if kind == 'matrix':
                                height = self._draw_matrix(
                                    self.surface, data, x, y,
                                    max_col_width, max_col_height, param_name
                                )
                            else:  # vector
                                height = self._draw_vector(
                                    self.surface, data, x, y,
                                    max_col_width, param_name
                                )
                            
                            # Обновляем y для следующего параметра в той же колонке
                            if idx % 2 == 0:
                                left_y += height + self.PADDING
                            else:
                                right_y += height + self.PADDING
                    else:
                        placeholder_text = self.font.render(
                            "[No NN parameters available]",
                            True,
                            self.COLORS['placeholder']
                        )
                        self.surface.blit(
                            placeholder_text,
                            (self.PADDING, y_offset + 20)
                        )
        
        # Отобразить на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
