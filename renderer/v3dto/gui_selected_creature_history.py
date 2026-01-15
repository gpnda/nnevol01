# -*- coding: utf-8 -*-
"""
SelectedCreatureHistory - v3dto версия.

Панель графика истории энергии выбранного существа.

Отображает:
- График энергии за последние 1200 тиков
- Минимальное и максимальное значение энергии
- Текущее значение энергии
- Маркеры событий (питание, размножение)

Если существо не выбрано, панель не отображается.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
from typing import List, Optional
from renderer.v3dto.dto import RenderStateDTO


class SelectedCreatureHistory:
    """
    Панель с графиком истории энергии выбранного существа.
    
    Отображается в нижней части экрана с фиксированными координатами.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает историю энергии из render_state.selected_creature.history.energy_history
    - Извлекает события из render_state.selected_creature.history.events
    - Полностью изолирована от сингльтонов
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
    MAX_HISTORY_POINTS = 1200  # Показываем последние 1200 тиков
    
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
    
    def __init__(self):
        """Инициализация панели."""
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифты для текста
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
            self.small_font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.SMALL_FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.small_font = pygame.font.Font(None, self.SMALL_FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """
        Отрисовка панели с графиком энергии выбранного существа.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о выбранном существе
        """
        # Если существо не выбрано, ничего не рисуем
        if render_state.selected_creature is None:
            return
        
        if render_state.selected_creature.history is None:
            return
        
        history_dto = render_state.selected_creature.history
        energy_history = history_dto.energy_history
        
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Заголовок
        title_text = self.font.render("Energy History", True, self.COLORS['highlight'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Если история пуста, выводим сообщение
        if not energy_history or len(energy_history) == 0:
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
            energy_history,
            history_dto.events,
            render_state.tick,
            graph_x,
            graph_y
        )
        
        # Статистика
        stats_y = graph_y + self.GRAPH_HEIGHT + 10
        
        min_text = self.small_font.render(f"Min: {min_energy:.2f}", True, self.COLORS['label'])
        self.surface.blit(min_text, (self.PADDING, stats_y))
        
        max_text = self.small_font.render(f"Max: {max_energy:.2f}", True, self.COLORS['label'])
        self.surface.blit(max_text, (self.PADDING, stats_y + 18))
        
        current_energy = render_state.selected_creature.creature.energy
        current_text = self.small_font.render(
            f"Current: {current_energy:.2f}",
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
            
            # Рисуем точку на конце (для лучшей видимости)
            pygame.draw.circle(self.surface, self.COLORS['highlight'], points[-1], 3)
    
    def _draw_events_on_graph(
        self,
        energy_history: List[float],
        events: Optional[List],
        current_tick: int,
        graph_x: int,
        graph_y: int
    ) -> None:
        """
        Отрисовывает маркеры событий на графике энергии.
        
        Логика:
        - Для каждого события вычисляем его позицию на X оси на основе tick_number
        - Событие должно быть в диапазоне истории: [current_tick - len(history) + 1, current_tick]
        - Отрисовываем маркер события цветом, соответствующим типу события
        
        Args:
            energy_history: История энергии (список значений)
            events: Список событий из CreatureHistoryDTO
            current_tick: Текущий номер тика в симуляции
            graph_x: X координата левого края графика
            graph_y: Y координата верхнего края графика
        """
        if not events:
            return
        
        # Вычисляем начальный тик для этой истории
        history_start_tick = current_tick - len(energy_history) + 1
        
        # Для каждого события вычисляем позицию на графике
        for event in events:
            # Проверяем, входит ли событие в видимый диапазон истории
            if event.tick < history_start_tick or event.tick > current_tick:
                continue  # Событие вне диапазона видимой истории
            
            # Вычисляем индекс в массиве energy_history
            history_index = event.tick - history_start_tick
            
            if history_index < 0 or history_index >= len(energy_history):
                continue
            
            # Вычисляем X координату маркера
            x = graph_x + history_index
            
            # Вычисляем Y координату на основе значения энергии в этот момент
            y = graph_y + self.GRAPH_HEIGHT - int(energy_history[history_index] * self.GRAPH_HEIGHT)
            
            # Получаем цвет маркера в зависимости от типа события
            event_color = self.EVENT_COLORS.get(event.event_type, self.EVENT_COLORS['default'])
            
            # Рисуем маркер события (полый кружок)
            pygame.draw.circle(
                self.surface,
                event_color,
                (int(x), int(y)),
                self.EVENT_MARKER_RADIUS,
                2  # Толщина линии (2 = полый кружок)
            )
