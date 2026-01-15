# -*- coding: utf-8 -*-
"""
CreaturesListModal - v3dto версия.

Модальное окно со списком всех существ в стиле BIOS/Norton Commander.
Отображает информацию о всех существах в симуляции.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
- Поддерживает навигацию: стрелки вверх/вниз, Home/End
- Может быть открыто и закрыто через state machine Renderer'а
"""

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class CreaturesListModal:
    """
    Модальное окно для отображения списка всех существ.
    
    Отображает в таблице:
    - ID существа
    - Возраст
    - Координаты (X, Y)
    - Текущую энергию
    - Скорость
    - Поколение
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает список существ из render_state.world.creatures
    - Полностью изолирована от сингльтонов
    - Управление навигацией внутри метода draw()
    """
    
    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 600
    POPUP_HEIGHT = 450
    
    # Параметры отображения
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 30
    HEADER_HEIGHT = 25
    ROW_HEIGHT = 18
    PADDING_X = 10
    PADDING_Y = 8
    
    # Максимум строк в окне (для скролла)
    MAX_VISIBLE_ROWS = 18
    
    # Цвета в стиле BIOS
    COLORS = {
        'bg': (5, 41, 158),           # Синий фон
        'border': (170, 170, 170),    # Серая граница
        'title_bg': (0, 167, 225),    # Голубой заголовок
        'title_text': (0, 0, 0),      # Чёрный текст в заголовке
        'text': (170, 170, 170),      # Серый текст
        'header': (255, 255, 255),    # Белый для заголовков столбцов
        'selected': (0, 167, 225),    # Голубой для выделения
        'selected_text': (0, 0, 0),   # Чёрный текст при выделении
    }
    
    def __init__(self):
        """Инициализация модального окна списка существ."""
        self.scroll_offset = 0
        self.selected_index = 0
        
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
    
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий клавиатуры для навигации в списке.
        
        Вызывается только когда рендерер находится в состоянии 'creatures_list'.
        
        Args:
            event: pygame.event.Event (KEYDOWN)
            
        Returns:
            True если событие обработано, False если нет
        """
        # Должно быть переданно через Renderer, поэтому мы не знаем количество существ здесь
        # Это обработается в Renderer._handle_creatures_list_keyboard()
        return False
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка модального окна со списком существ.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о существах
        """
        creatures = render_state.world.creatures
        creatures_count = len(creatures)
        
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
            f"Creatures: {creatures_count}", 
            True, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.PADDING_X
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Отрисовка заголовков столбцов
        header_y = self.y + self.TITLE_HEIGHT
        pygame.draw.line(
            screen, 
            self.COLORS['border'], 
            (self.x, header_y + self.HEADER_HEIGHT),
            (self.x + self.POPUP_WIDTH, header_y + self.HEADER_HEIGHT), 
            1
        )
        
        # Определение столбцов: (название, ширина)
        headers = [
            ("ID", 35),
            ("Age", 40),
            ("X", 45),
            ("Y", 45),
            ("Energy", 65),
            ("Speed", 55),
            ("Gen", 40),
        ]
        
        col_x = self.x + self.PADDING_X
        for header, width in headers:
            text = self.font.render(header, True, self.COLORS['header'])
            screen.blit(text, (col_x, header_y + 5))
            col_x += width
        
        # Отрисовка строк с существами
        if creatures_count == 0:
            # Сообщение если нет существ
            msg = self.font.render("No creatures", True, self.COLORS['text'])
            msg_x = self.x + (self.POPUP_WIDTH - msg.get_width()) // 2
            msg_y = self.y + self.TITLE_HEIGHT + self.HEADER_HEIGHT + 50
            screen.blit(msg, (msg_x, msg_y))
        else:
            row_y = header_y + self.HEADER_HEIGHT
            visible_creatures = creatures[self.scroll_offset:self.scroll_offset + self.MAX_VISIBLE_ROWS]
            
            for idx, creature in enumerate(visible_creatures):
                actual_idx = self.scroll_offset + idx
                is_selected = (actual_idx == self.selected_index)
                
                # Фон строки
                if is_selected:
                    row_rect = pygame.Rect(self.x + 1, row_y, self.POPUP_WIDTH - 2, self.ROW_HEIGHT)
                    pygame.draw.rect(screen, self.COLORS['selected'], row_rect)
                    text_color = self.COLORS['selected_text']
                else:
                    text_color = self.COLORS['text']
                
                # Данные существа
                creature_data = [
                    (str(actual_idx), 35),
                    (str(creature.age), 40),
                    (f"{creature.x:.1f}", 45),
                    (f"{creature.y:.1f}", 45),
                    (f"{creature.energy:.1f}", 65),
                    (f"{creature.speed:.2f}", 55),
                    (str(creature.generation), 40),
                ]
                
                col_x = self.x + self.PADDING_X
                for value, width in creature_data:
                    text = self.font.render(value, True, text_color)
                    screen.blit(text, (col_x, row_y + 2))
                    col_x += width
                
                row_y += self.ROW_HEIGHT
        
        # Отрисовка подсказки внизу
        help_text = "Arrows: scroll | Home/End: jump | ESC: close"
        help_surface = self.font_small.render(help_text, True, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.PADDING_Y - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
    
    # ========================================================================
    # НАВИГАЦИЯ (вызывается из Renderer._handle_creatures_list_keyboard())
    # ========================================================================
    
    def move_selection_up(self, creatures_count: int) -> None:
        """Переместить выделение на одну строку вверх."""
        if creatures_count == 0:
            return
        if self.selected_index > 0:
            self.selected_index -= 1
            # Автоскролл
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
    
    def move_selection_down(self, creatures_count: int) -> None:
        """Переместить выделение на одну строку вниз."""
        if creatures_count == 0:
            return
        if self.selected_index < creatures_count - 1:
            self.selected_index += 1
            # Автоскролл
            if self.selected_index >= self.scroll_offset + self.MAX_VISIBLE_ROWS:
                self.scroll_offset = self.selected_index - self.MAX_VISIBLE_ROWS + 1
    
    def move_selection_home(self) -> None:
        """Переместить выделение в начало списка."""
        self.selected_index = 0
        self.scroll_offset = 0
    
    def move_selection_end(self, creatures_count: int) -> None:
        """Переместить выделение в конец списка."""
        if creatures_count == 0:
            return
        self.selected_index = creatures_count - 1
        self.scroll_offset = max(0, creatures_count - self.MAX_VISIBLE_ROWS)
    
    def reset(self) -> None:
        """Сбросить состояние навигации (вызывается при открытии модала)."""
        self.scroll_offset = 0
        self.selected_index = 0
    
    def get_selected_creature_id(self, creatures_count: int) -> int:
        """Получить ID выбранного существа."""
        if creatures_count > 0 and self.selected_index < creatures_count:
            return self.selected_index
        return -1
