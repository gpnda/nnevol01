# -*- coding: utf-8 -*-
"""
Панель графика истории энергии выбранного существа.

Отображает:
- График энергии за последние 500 тиков
- Минимальное и максимальное значение энергии
- Текущее значение энергии

Если существо не выбрано, панель не отображается.
"""

import pygame
from typing import List, Tuple
from service.logger.logger import logme


class SelectedCreatureHistory:
    """
    Панель с графиком истории энергии выбранного существа.
    
    Отображается в правой части экрана с фиксированными координатами.
    """
    
    # Координаты и размеры
    POSITION_X = 4
    POSITION_Y = 505
    WIDTH = 1243
    HEIGHT = 65
    
    # Параметры графика
    GRAPH_PADDING = 2
    GRAPH_HEIGHT = 60
    GRAPH_WIDTH = WIDTH - 2 * GRAPH_PADDING
    MAX_HISTORY_POINTS = 1200  # Показываем последние 500 тиков
    
    # Цвета
    COLORS = {
        'background': (0, 0, 0),
        'border': (60, 60, 60),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'highlight': (0, 255, 100),
        'graph_background': (30, 30, 30),
        'graph_line': (0, 200, 100),
        'graph_grid': (60, 60, 60),
    }
    
    # Размеры
    BORDER_WIDTH = 2
    PADDING = 5
    LINE_HEIGHT = 25
    FONT_SIZE = 16
    SMALL_FONT_SIZE = 12
    
    # Цвета и параметры событий
    EVENT_MARKER_RADIUS = 4
    EVENT_COLORS = {
        'EAT_FOOD': (0, 255, 0),        # Зелёный - еда
        'CREATE_CHILD': (255, 165, 0),  # Оранжевый - потомки
        'default': (100, 100, 255),     # Синий - прочие события
    }
    
    def __init__(self, world):
        """Инициализация панели."""
        self.world = world
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифты для текста
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
            self.small_font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.SMALL_FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.small_font = pygame.font.Font(None, self.SMALL_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, selected_creature_id: int) -> None:
        """
        Отрисовка панели с графиком энергии выбранного существа.
        
        Args:
            screen: Pygame surface для отрисовки
            selected_creature_id: ID выбранного существа (или None)
        """
        # Если существо не выбрано, ничего не рисуем
        if selected_creature_id is None:
            return
        
        selected_creature = self.world.get_creature_by_id(selected_creature_id)
        if selected_creature is None:
            return
        
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Заголовок
        title_text = self.font.render("Energy History", True, self.COLORS['highlight'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # #################################################################################
        # ДОСТУП К ИНФОРМАЦИИ О СОБЫТИЯХ ИЗ ЛОГГЕРА
        # 
        # Логгер хранит историю событий каждого существа, включая:
        # - поедание пищи (EAT_FOOD)
        # - размножение/создание потомков (CREATE_CHILD)
        # - и другие события
        #
        # Способы получить информацию:
        #
        # 1. Получить все события существа:
        #    events = self.logger.get_creature_events(selected_creature_id)
        #    # events - список объектов CreatureEvent
        #
        # 2. Получить события определённого типа:
        #    food_events = self.logger.get_creature_events_by_type(selected_creature_id, "EAT_FOOD")
        #    children_events = self.logger.get_creature_events_by_type(selected_creature_id, "CREATE_CHILD")
        #
        # 3. Каждое событие содержит:
        #    - event.creature_id: ID существа
        #    - event.tick_number: номер тика симуляции
        #    - event.event_type: тип события (строка)
        #    - event.value: значение события (может быть число, ID, и т.д.)
        #
        # 4. Получить историю энергии (текущий способ в этой панели):
        #    energy_history = self.logger.get_creature_energy_history(selected_creature_id)
        #    # energy_history - список значений энергии по каждому тику
        #
        # 5. Получить количество событий определённого типа:
        #    count = self.logger.get_events_count(selected_creature_id, "EAT_FOOD")
        #
        # #################################################################################
        
        # Получаем историю энергии
        energy_history = logme.get_creature_energy_history(selected_creature_id)
        
        # Если история пуста, выводим сообщение
        if not energy_history:
            no_data_text = self.small_font.render("No history yet", True, self.COLORS['label'])
            self.surface.blit(no_data_text, (self.PADDING, self.PADDING + self.LINE_HEIGHT + 20))
            screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
            return
        
        # Берем только последние MAX_HISTORY_POINTS значений
        if len(energy_history) > self.MAX_HISTORY_POINTS:
            energy_history = energy_history[-self.MAX_HISTORY_POINTS:]
        
        # Определяем границы графика (0.0 до 1.0)
        min_display = 0.0
        max_display = 1.0
        
        # Вычисляем min/max из истории для статистики
        min_energy = min(energy_history)
        max_energy = max(energy_history)
        
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
            1
        )
        
        # Рисуем сетку (горизонтальные линии)
        self._draw_grid(graph_x, graph_y, min_display, max_display)
        
        # Рисуем линию графика
        if len(energy_history) > 1:
            self._draw_graph_line(
                energy_history, 
                graph_x, 
                graph_y, 
                min_display, 
                max_display
            )
        
        # Рисуем события на графике (маркеры)
        self._draw_events_on_graph(
            selected_creature_id,
            energy_history,
            graph_x,
            graph_y
        )
        
        # Статистика
        stats_y = graph_y + self.GRAPH_HEIGHT + 10
        
        min_text = self.small_font.render(f"Min: {min_energy:.2f}", True, self.COLORS['label'])
        self.surface.blit(min_text, (self.PADDING, stats_y))
        
        max_text = self.small_font.render(f"Max: {max_energy:.2f}", True, self.COLORS['label'])
        self.surface.blit(max_text, (self.PADDING, stats_y + 18))
        
        current_text = self.small_font.render(
            f"Current: {selected_creature.energy:.2f}", 
            True, 
            self.COLORS['highlight']
        )
        self.surface.blit(current_text, (self.PADDING, stats_y + 36))
        
        # Отрисовка на главный экран
        screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
    
    def _draw_grid(self, graph_x: int, graph_y: int, min_val: float, max_val: float) -> None:
        """
        Рисует сетку на фоне графика.
        
        Args:
            graph_x: X координата левого края графика
            graph_y: Y координата верхнего края графика
            min_val: Минимальное значение на оси Y
            max_val: Максимальное значение на оси Y
        """
        # Рисуем 4 горизонтальные линии сетки
        num_grid_lines = 4
        for i in range(1, num_grid_lines):
            y_ratio = i / num_grid_lines
            y_pos = graph_y + int(self.GRAPH_HEIGHT * y_ratio)
            
            pygame.draw.line(
                self.surface,
                self.COLORS['graph_grid'],
                (graph_x, y_pos),
                (graph_x + self.GRAPH_WIDTH, y_pos),
                1
            )
    
    def _draw_graph_line(
        self, 
        energy_history: List[float], 
        graph_x: int, 
        graph_y: int,
        min_val: float, 
        max_val: float
    ) -> None:
        """
        Рисует линию графика энергии.
        
        Args:
            energy_history: Список значений энергии
            graph_x: X координата левого края графика
            graph_y: Y координата верхнего края графика
            min_val: Минимальное значение на оси Y
            max_val: Максимальное значение на оси Y
        """
        if len(energy_history) < 2:
            return
        
        points = []
        
        for i, energy in enumerate(energy_history):
            # Пропускаем None значения
            if energy is None:
                continue
                
            try:
                # Используем значение энергии напрямую (уже в диапазоне [0, 1])
                energy_val = float(energy)
                
                # Ограничиваем значение в диапазон [0, 1]
                energy_val = max(0, min(1, energy_val))
                
                # Рассчитываем X координату (1 пиксел = 1 точка в истории)
                x = graph_x + i
                
                # Рассчитываем Y координату (инвертируем, так как Y растет вниз)
                y = graph_y + self.GRAPH_HEIGHT - int(energy_val * self.GRAPH_HEIGHT)
                
                points.append((int(x), int(y)))
            except (ValueError, TypeError):
                # Пропускаем некорректные значения
                continue
        
        # Рисуем линию
        if len(points) > 1:
            pygame.draw.lines(
                self.surface,
                self.COLORS['graph_line'],
                False,
                points,
                2
            )
            
            # Рисуем точки на концах (для лучшей видимости)
            pygame.draw.circle(self.surface, self.COLORS['highlight'], points[-1], 3)    
    def _draw_events_on_graph(
        self,
        creature_id: int,
        energy_history: List[float],
        graph_x: int,
        graph_y: int
    ) -> None:
        """
        Отрисовывает маркеры событий на графике энергии.
        
        Логика:
        - Получаем все события существа из глобального logme
        - Для каждого события вычисляем его позицию на X оси:
          - X_смещение = world.tick_number - event.tick_number
          - Если смещение в диапазоне [0, len(energy_history)), то событие видимо
        - Отрисовываем маркер события цветом, соответствующим типу события
        
        Args:
            creature_id: ID существа
            energy_history: История энергии (список значений)
            graph_x: X координата левого края графика
            graph_y: Y координата верхнего края графика
        """
        # Получаем все события существа
        events = logme.get_creature_events(creature_id)
        
        if not events:
            return
        
        # Получаем текущий номер тика в симуляции
        current_tick = self.world.tick_number if hasattr(self.world, 'tick_number') else 0
        
        # Вычисляем начальный тик для этой истории
        # (начало видимого окна на графике)
        history_start_tick = current_tick - len(energy_history) + 1
        
        # Для каждого события вычисляем позицию на графике
        for event in events:
            # Вычисляем смещение события от конца графика
            tick_offset = current_tick - event.tick_number
            
            # Проверяем, входит ли событие в видимый диапазон
            if tick_offset < 0 or tick_offset >= len(energy_history):
                continue  # Событие вне диапазона видимой истории
            
            # Вычисляем индекс в массиве energy_history
            # (от конца массива, так как это последние значения)
            history_index = len(energy_history) - 1 - tick_offset
            
            if history_index < 0 or history_index >= len(energy_history):
                continue
            
            # Вычисляем X координату маркера
            x = graph_x + history_index
            
            # Вычисляем Y координату (в верхней части графика для видимости)
            y = graph_y + 3
            
            # Получаем цвет маркера в зависимости от типа события
            event_color = self.EVENT_COLORS.get(event.event_type, self.EVENT_COLORS['default'])
            
            # Рисуем маркер события (кружок или крест)
            # Кружок для основных событий
            pygame.draw.circle(
                self.surface,
                event_color,
                (int(x), int(y)),
                self.EVENT_MARKER_RADIUS,
                2  # Толщина линии (2 = полый кружок)
            )