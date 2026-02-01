# -*- coding: utf-8 -*-
"""
Dummy Experiment Widget - v3dto версия.

Визуальный интерфейс для dummy эксперимента.
Архитектура v3dto:
- НЕ имеет зависимостей от world, experiment, debugger, RenderStateDTO
- Получает данные только через DummyExperimentDTO
- Полностью изолирована от singleton'ов
- Может быть открыто и закрыто через state machine Renderer'а
"""

import pygame


class DummyExperimentWidget:
    """
    Виджет для визуализации dummy эксперимента.
    
    Архитектура DTO:
    - Получает DummyExperimentDTO в методе draw()
    - Не имеет доступа к RenderStateDTO
    - Полностью изолирована от singleton'ов
    """
    
    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 600
    POPUP_HEIGHT = 400
    
    # Параметры отображения
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 40
    CONTENT_PADDING = 20
    LINE_HEIGHT = 30
    
    # Цвета в стиле BIOS
    COLORS = {
        'bg': (5, 41, 158),           # Синий фон
        'border': (170, 170, 170),    # Серая граница
        'title_bg': (0, 167, 225),    # Голубой заголовок
        'title_text': (0, 0, 0),      # Чёрный текст в заголовке
        'text': (170, 170, 170),      # Серый текст
        'label': (255, 255, 255),     # Белый для меток
        'value': (0, 255, 100),       # Зелёный для значений
    }
    
    def __init__(self):
        """Инициализация виджета dummy эксперимента."""
        # Инициализация шрифтов
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE + 4)
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font_small = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE - 2)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 4)
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_small = pygame.font.Font(None, self.FONT_SIZE - 2)
        
        # Позиция и размер окна (будут вычислены при первом draw)
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)
    
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
        if event.type != pygame.KEYDOWN:
            return False
        
        # Здесь можно добавить внутренние команды эксперимента
        # Пока ничего не обрабатываем
        return False
    
    def draw(self, screen: pygame.Surface, experiment_dto) -> None:
        """
        Отрисовка виджета dummy эксперимента.
        
        Args:
            screen: Pygame surface для отрисовки
            experiment_dto: DummyExperimentDTO с данными эксперимента
        """
        # Проверить валидность DTO
        if experiment_dto is None:
            return
        
        # Вычисляем позицию окна (центр экрана)
        screen_width, screen_height = screen.get_size()
        self.x = (screen_width - self.POPUP_WIDTH) // 2
        self.y = (screen_height - self.POPUP_HEIGHT) // 2
        self.rect = pygame.Rect(self.x, self.y, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        
        # Отрисовка фона окна
        pygame.draw.rect(screen, self.COLORS['bg'], self.rect)
        pygame.draw.rect(screen, self.COLORS['border'], self.rect, 2)
        
        # Отрисовка заголовка
        title_rect = pygame.Rect(self.x, self.y, self.POPUP_WIDTH, self.TITLE_HEIGHT)
        pygame.draw.rect(screen, self.COLORS['title_bg'], title_rect)
        
        title_text = self.font_title.render(
            "Dummy Experiment", 
            True, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.CONTENT_PADDING
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Контент окна
        content_y = self.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        content_x = self.x + self.CONTENT_PADDING
        
        # Отрисовка информации об эксперименте из experiment_dto
        creature_id = experiment_dto.creature_id if hasattr(experiment_dto, 'creature_id') else 'unknown'
        
        lines = [
            f"Experiment Type:",
            f"  DUMMY",
            f"",
            f"Target Creature:",
            f"  ID: {creature_id}",
            f"",
            f"Status:",
            f"  RUNNING",
        ]
        
        for line in lines:
            if line.startswith("  "):
                # Значение - зелёный цвет
                text_surface = self.font.render(line, True, self.COLORS['value'])
            elif line == "":
                # Пустая строка - пропускаем
                text_surface = None
            else:
                # Метка - белый цвет
                text_surface = self.font.render(line, True, self.COLORS['label'])
            
            if text_surface is not None:
                screen.blit(text_surface, (content_x, content_y))
            content_y += self.LINE_HEIGHT
        
        # Отрисовка подсказки внизу
        help_text = "ESC or F2: close experiment"
        help_surface = self.font_small.render(help_text, True, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.CONTENT_PADDING - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
