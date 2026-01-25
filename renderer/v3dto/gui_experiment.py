# -*- coding: utf-8 -*-
"""
ExperimentModal - v3dto версия.

Модальное окно экспериментов.
Начальная версия: отображает информацию о выбранном существе.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
- Может быть открыто и закрыто через state machine Renderer'а
"""

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class ExperimentModal:
    """
    Модальное окно для экспериментов.
    
    Начальная версия отображает информацию о выбранном существе (ID).
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Получает selected_creature_id из reset(selected_creature_id)
    - Полностью изолирована от сингльтонов
    """
    
    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 500
    POPUP_HEIGHT = 300
    
    # Параметры отображения
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 30
    CONTENT_PADDING = 20
    LINE_HEIGHT = 25
    
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
        """Инициализация модального окна экспериментов."""
        # Инициализация шрифтов
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE + 2)
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font_small = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE - 2)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 2)
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_small = pygame.font.Font(None, self.FONT_SIZE - 2)
        
        # Позиция и размер окна (будут вычислены при первом draw)
        self.selected_creature_id = None
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)
    
    def reset(self, selected_creature_id: int) -> None:
        """Сбросить состояние (вызывается при открытии модала)."""
        self.selected_creature_id = selected_creature_id
        return
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка модального окна экспериментов.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о выбранном существе
        """
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
            "Experiment Window", 
            True, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.CONTENT_PADDING
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Контент окна
        content_y = self.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        content_x = self.x + self.CONTENT_PADDING
        
        if self.selected_creature_id is None:
            # Нет выбранного существа
            msg = self.font.render("No creature selected", True, self.COLORS['text'])
            screen.blit(msg, (content_x, content_y))
        else:
            # Отрисовка информации о выбранном существе
            lines = [
                f"Selected Creature ID:",
                f"  {self.selected_creature_id}",
                f"",
                f"More features coming soon...",
            ]
            
            for line in lines:
                if line.startswith("  "):
                    # Значение - зелёный цвет
                    text_surface = self.font.render(line, True, self.COLORS['value'])
                else:
                    # Метка - белый цвет
                    text_surface = self.font.render(line, True, self.COLORS['label'])
                
                screen.blit(text_surface, (content_x, content_y))
                content_y += self.LINE_HEIGHT
        
        # Отрисовка подсказки внизу
        help_text = "F2 or ESC: close"
        help_surface = self.font_small.render(help_text, True, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.CONTENT_PADDING - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
