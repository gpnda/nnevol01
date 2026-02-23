# -*- coding: utf-8 -*-
"""
ExperListModal - v3dto версия.

Модальное окно экспер..
Начальная версия: отображает информацию о выбранном существе.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
- Может быть открыто и закрыто через state machine Renderer'а
"""

import pygame
from typing import TYPE_CHECKING, Callable, Any, Optional

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class ExperListModal:
    """
    Модальное окно для экспер..
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
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
    
    def __init__(self, on_experiment_choose: Optional[Callable[[int], None]] = None):
        """Инициализация модального окна экспер..
            - Загружает список экспер.. из реестра

            Args:
            on_experiment_choose: Callback при выборе эксперимента
                                Сигнатура: on_experiment_choose(experiment_id: int)
        """

        # Callback функция
        self.on_experiment_choose = on_experiment_choose

        
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
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)


        
    
    def reset(self, selected_creature_id: int) -> None:
        """Сбросить состояние (вызывается при открытии модала)."""
        self.selected_creature_id = selected_creature_id
        return
    

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий клавиатуры (выбор эксперимента по цифрам 0-9).
        
        Args:
            event: pygame.event.Event клавиатурного события
            
        Returns:
            True если событие обработано
        """
        if event.type != pygame.KEYDOWN:
            return False
    
        # Обработка цифр 0-9 для выбора эксперимента
        if pygame.K_0 <= event.key <= pygame.K_9:
            if self.selected_creature_id is not None:
                experiment_id = event.key - pygame.K_0
                self.on_experiment_choose(experiment_id)
                return True
            
        
        return False
    

    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка модального окна экспер..
        
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
            "Choose Exper.ment", 
            True, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.CONTENT_PADDING
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Контент окна
        content_y = self.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        content_x = self.x + self.CONTENT_PADDING
        
        # Получаем список экспер.. из RenderStateDTO
        exper_list = render_state.exper_list

        # Получить id выбранного существа для отображения
        self.selected_creature_id = render_state.selected_creature.creature.id if render_state.selected_creature else None

        # Отрисовка списка экспериментов
        for id, (exper_key, exper_info) in enumerate(exper_list.items()):
            exper_text = f"{id}: {exper_info['name']} - {exper_info['description']}"
            text_surface = self.font.render(exper_text, True, self.COLORS['label'])
            screen.blit(text_surface, (content_x, content_y))
            content_y += self.LINE_HEIGHT
        
        
        # Отрисовка подсказки внизу
        help_text = "F2 or ESC: close"
        help_surface = self.font_small.render(help_text, True, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.CONTENT_PADDING - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
