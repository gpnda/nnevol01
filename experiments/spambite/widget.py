# -*- coding: utf-8 -*-
"""
SpambiteExperiment Widget - v3dto версия.

Визуальный интерфейс для SpambiteExperiment.
Архитектура v3dto:
- НЕ имеет зависимостей от world, experiment, debugger
- Получает данные только через SpambiteExperimentDTO
- Полностью изолирована от singleton'ов и RenderStateDTO
- Может быть открыто и закрыто через state machine Renderer'а
"""

import pygame


class SpambiteExperimentWidget:
    """
    Виджет для визуализации SpambiteExperiment.
    
    Архитектура DTO:
    - Получает SpambiteExperimentDTO в методе draw()
    - Не имеет доступа к RenderStateDTO
    - Рисует карту мира 50x50, существо, пищу и статистику
    - Полностью изолирована от singleton'ов
    """
    
    # ============================================================================
    # Константы конфигурации
    # ============================================================================
    
    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 700
    POPUP_HEIGHT = 600
    
    # Параметры шрифта
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    # Размеры элементов
    TITLE_HEIGHT = 40
    CONTENT_PADDING = 20
    MAP_CELL_SIZE = 8  # Пиксели на клетку карты
    
    # Цвета в стиле BIOS
    COLORS = {
        'bg': (5, 41, 158),           # Синий фон
        'border': (170, 170, 170),    # Серая граница
        'title_bg': (0, 167, 225),    # Голубой заголовок
        'title_text': (0, 0, 0),      # Чёрный текст в заголовке
        'text': (170, 170, 170),      # Серый текст
        'label': (255, 255, 255),     # Белый для меток
        'value': (0, 255, 100),       # Зелёный для значений
        'map_bg': (10, 10, 30),       # Очень тёмный синий для карты
        'map_empty': (30, 30, 60),    # Тёмный синий для пустых клеток
        'map_wall': (100, 100, 100),  # Серый для стен
        'map_food': (0, 255, 0),      # Зелёный для пищи
        'map_creature': (255, 0, 0),  # Красный для существа
    }
    
    # ============================================================================
    # Инициализация
    # ============================================================================
    
    def __init__(self):
        """Инициализация виджета SpambiteExperiment."""
        # Инициализация шрифтов
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE + 4)
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font_small = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE - 2)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 4)
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_small = pygame.font.Font(None, self.FONT_SIZE - 2)
        
        # Позиция и размер окна
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        self._center_on_screen(1024, 768)  # По умолчанию, будет обновлено при draw
    
    # ============================================================================
    # Методы рисования
    # ============================================================================
    
    def draw(self, screen: pygame.Surface, experiment_dto) -> None:
        """
        Основной метод рисования виджета.
        
        Args:
            screen: pygame.Surface для рисования
            experiment_dto: SpambiteExperimentDTO с данными эксперимента
        """
        # Центрировать на экране
        self._center_on_screen(screen.get_width(), screen.get_height())
        
        # Проверить валидность DTO
        if experiment_dto is None:
            return
        
        # Рисовать окно
        self._draw_background(screen)
        self._draw_title(screen)
        self._draw_content(screen, experiment_dto)
        self._draw_border(screen)
    
    def _draw_background(self, screen: pygame.Surface) -> None:
        """Рисовать фон окна."""
        pygame.draw.rect(screen, self.COLORS['bg'], self.rect)
    
    def _draw_border(self, screen: pygame.Surface) -> None:
        """Рисовать границу окна."""
        pygame.draw.rect(screen, self.COLORS['border'], self.rect, 2)
    
    def _draw_title(self, screen: pygame.Surface) -> None:
        """Рисовать заголовок окна."""
        title_rect = pygame.Rect(
            self.rect.x, self.rect.y,
            self.rect.width, self.TITLE_HEIGHT
        )
        pygame.draw.rect(screen, self.COLORS['title_bg'], title_rect)
        
        title_text = self.font_title.render("SpambiteExperiment", True, self.COLORS['title_text'])
        title_x = self.rect.x + (self.rect.width - title_text.get_width()) // 2
        title_y = self.rect.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
    
    def _draw_content(self, screen: pygame.Surface, exp_dto: object) -> None:
        """
        Рисовать основное содержимое окна.
        
        Layout:
        ┌─────────────────────────────────────────┐
        │ Title (SpambiteExperiment)              │
        ├─────────────────────────────────────────┤
        │ Map 50x50 (left)    │ Stats (right)    │
        │ - World grid        │ - Iteration      │
        │ - Creature          │ - Successes      │
        │ - Food              │ - Failures       │
        │                     │ - Success rate   │
        ├─────────────────────────────────────────┤
        │ Press ESC to exit                       │
        └─────────────────────────────────────────┘
        
        Args:
            screen: pygame.Surface для рисования
            exp_dto: SpambiteExperimentDTO с данными эксперимента
        """
        content_y = self.rect.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        content_x = self.rect.x + self.CONTENT_PADDING
        
        # ===== Размеры карты =====
        map_width = 50 * self.MAP_CELL_SIZE  # 400 пиксели
        map_height = 50 * self.MAP_CELL_SIZE  # 400 пиксели
        
        # Рисовать карту (слева)
        map_rect = pygame.Rect(content_x, content_y, map_width, map_height)
        self._draw_map(screen, map_rect, exp_dto)
        
        # Рисовать статистику (справа)
        stats_x = content_x + map_width + self.CONTENT_PADDING
        self._draw_stats(screen, stats_x, content_y, exp_dto)
        
        # Рисовать помощь внизу
        help_text = self.font_small.render("Press ESC to exit", True, self.COLORS['value'])
        help_y = self.rect.y + self.rect.height - self.CONTENT_PADDING - help_text.get_height()
        screen.blit(help_text, (content_x, help_y))
    
    def _draw_map(self, screen: pygame.Surface, map_rect: pygame.Rect, exp_dto: object) -> None:
        """
        Рисовать карту мира 50x50.
        
        Показывает:
        - Стены (серый цвет)
        - Пусто (темный синий)
        - Пищу (зеленый)
        - Существо (красный)
        """
        # Фон карты
        pygame.draw.rect(screen, self.COLORS['map_bg'], map_rect)
        pygame.draw.rect(screen, self.COLORS['border'], map_rect, 1)
        
        # Если нет данных карты - выход
        if exp_dto.world_state is None:
            return
        
        # Рисовать сетку и объекты
        world_map = exp_dto.world_state.map
        
        for y in range(50):
            for x in range(50):
                # Позиция клетки на экране
                cell_x = map_rect.x + x * self.MAP_CELL_SIZE
                cell_y = map_rect.y + y * self.MAP_CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, self.MAP_CELL_SIZE, self.MAP_CELL_SIZE)
                
                # Получить тип клетки
                cell_value = world_map[y, x]
                
                # Рисовать в зависимости от типа
                if cell_value == 1:  # Стена
                    pygame.draw.rect(screen, self.COLORS['map_wall'], cell_rect)
                elif cell_value == 2:  # Пища
                    pygame.draw.rect(screen, self.COLORS['map_empty'], cell_rect)
                    pygame.draw.circle(screen, self.COLORS['map_food'], cell_rect.center, 2)
                elif cell_value == 3:  # Существо
                    pygame.draw.rect(screen, self.COLORS['map_empty'], cell_rect)
                    pygame.draw.rect(screen, self.COLORS['map_creature'], cell_rect, 1)
                else:  # Пусто
                    pygame.draw.rect(screen, self.COLORS['map_empty'], cell_rect)
    
    def _draw_stats(self, screen: pygame.Surface, start_x: int, start_y: int, exp_dto: object) -> None:
        """
        Рисовать статистику эксперимента справа.
        
        Показывает:
        - Текущая итерация / всего
        - Успехи / неудачи
        - Процент успеха
        - Фреймы в текущей итерации
        """
        y = start_y
        line_height = 25
        
        # Заголовок статистики
        stats_title = self.font.render("STATISTICS", True, self.COLORS['label'])
        screen.blit(stats_title, (start_x, y))
        y += line_height + 5
        
        # Разделитель
        pygame.draw.line(screen, self.COLORS['border'], 
                        (start_x, y), (start_x + 150, y), 1)
        y += 10
        
        # Итерация
        iter_text = f"Iteration:"
        iter_value = f"{exp_dto.current_iteration}/{exp_dto.total_iterations}"
        self._draw_stat_line(screen, start_x, y, iter_text, iter_value)
        y += line_height
        
        # Успехи
        succ_text = "Successes:"
        succ_value = f"{exp_dto.successes}"
        self._draw_stat_line(screen, start_x, y, succ_text, succ_value)
        y += line_height
        
        # Неудачи
        fail_text = "Failures:"
        fail_value = f"{exp_dto.failures}"
        self._draw_stat_line(screen, start_x, y, fail_text, fail_value)
        y += line_height
        
        # Процент успеха
        success_rate = exp_dto.success_rate
        rate_text = "Success Rate:"
        rate_value = f"{success_rate:.1f}%"
        self._draw_stat_line(screen, start_x, y, rate_text, rate_value)
        y += line_height + 5
        
        # Разделитель
        pygame.draw.line(screen, self.COLORS['border'], 
                        (start_x, y), (start_x + 150, y), 1)
        y += 10
        
        # Фреймы в итерации
        frames_text = f"Frames: {exp_dto.frames_in_iteration}/300"
        frames_surf = self.font_small.render(frames_text, True, self.COLORS['text'])
        screen.blit(frames_surf, (start_x, y))
        y += line_height
        
        # Progress bar для фреймов
        progress = exp_dto.iteration_progress  # 0.0 - 1.0
        bar_width = 150
        bar_height = 10
        bar_x = start_x
        bar_y = y
        
        # Фон прогресс-бара
        pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        # Заполненная часть
        filled_width = int(bar_width * progress)
        if filled_width > 0:
            pygame.draw.rect(screen, self.COLORS['value'], (bar_x, bar_y, filled_width, bar_height))
        # Граница
        pygame.draw.rect(screen, self.COLORS['border'], (bar_x, bar_y, bar_width, bar_height), 1)
    
    def _draw_stat_line(self, screen: pygame.Surface, x: int, y: int, 
                       label: str, value: str) -> None:
        """Рисовать одну строку статистики (метка: значение)."""
        label_surf = self.font.render(label, True, self.COLORS['label'])
        value_surf = self.font.render(value, True, self.COLORS['value'])
        
        screen.blit(label_surf, (x, y))
        screen.blit(value_surf, (x + 120, y))
    
    # ============================================================================
    # Утилиты
    # ============================================================================
    
    def _center_on_screen(self, screen_width: int, screen_height: int) -> None:
        """Центрировать окно на экране."""
        self.rect.x = (screen_width - self.POPUP_WIDTH) // 2
        self.rect.y = (screen_height - self.POPUP_HEIGHT) // 2
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий клавиатуры.
        
        Args:
            event: pygame.event.Event клавиатурного события
            
        Returns:
            True если событие обработано, False иначе
            
        Замечание: Закрытие окна (ESC/F2) обрабатывается в Renderer,
                  этот метод для внутренних событий виджета.
        """
        # TODO: Реализовать обработку событий если потребуется
        return False
