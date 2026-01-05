# -*- coding: utf-8 -*-
"""
Popup окно со списком существ в стиле BIOS/Norton Commander.
Отображает информацию о всех существах в симуляции.
"""

import pygame
from typing import Optional


class CreaturesPopup:
    """Popup окно для отображения списка всех существ с их параметрами."""
    
    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 500
    POPUP_HEIGHT = 400
    
    # Параметры отображения
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 30
    HEADER_HEIGHT = 25
    ROW_HEIGHT = 18
    PADDING_X = 10
    PADDING_Y = 8
    
    # Максимум строк в окне (для скролла)
    MAX_VISIBLE_ROWS = 16
    
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
    
    def __init__(self, world):
        """
        Инициализация popup окна.
        
        Args:
            world: Объект World для доступа к списку существ
        """
        self.world = world
        self.visible = False
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
        
        # Получаем размер экрана для центрирования
        self.screen_width = pygame.display.get_surface().get_width()
        self.screen_height = pygame.display.get_surface().get_height()
        
        # Позиция popup (центр экрана)
        self.x = (self.screen_width - self.POPUP_WIDTH) // 2
        self.y = (self.screen_height - self.POPUP_HEIGHT) // 2
        
        self.rect = pygame.Rect(self.x, self.y, self.POPUP_WIDTH, self.POPUP_HEIGHT)
    
    def toggle(self) -> None:
        """Переключить видимость popup."""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
            self.selected_index = 0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий клавиатуры для popup.
        
        Args:
            event: pygame.event.Event
            
        Returns:
            True если событие обработано
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # F1: открыть/закрыть popup существ (обрабатываем независимо от видимости)
        if event.key == pygame.K_F1:
            self.toggle()
            return True
        
        # Остальные события обрабатываются только если popup видим
        if not self.visible:
            return False
        
        creatures_count = len(self.world.creatures)
        if creatures_count == 0:
            # Закрыть popup если нет существ
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            return False
        
        max_scroll = max(0, creatures_count - self.MAX_VISIBLE_ROWS)
        
        if event.key == pygame.K_UP:
            # Движение вверх по списку
            if self.selected_index > 0:
                self.selected_index -= 1
                # Автоскролл
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
            return True
        
        elif event.key == pygame.K_DOWN:
            # Движение вниз по списку
            if self.selected_index < creatures_count - 1:
                self.selected_index += 1
                # Автоскролл
                if self.selected_index >= self.scroll_offset + self.MAX_VISIBLE_ROWS:
                    self.scroll_offset = self.selected_index - self.MAX_VISIBLE_ROWS + 1
            return True
        
        elif event.key == pygame.K_HOME:
            # В начало списка
            self.selected_index = 0
            self.scroll_offset = 0
            return True
        
        elif event.key == pygame.K_END:
            # В конец списка
            self.selected_index = creatures_count - 1
            self.scroll_offset = max_scroll
            return True
        
        elif event.key == pygame.K_ESCAPE:
            # Закрыть popup
            self.visible = False
            return True
        
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовка popup окна.
        
        Args:
            screen: pygame.Surface для отрисовки
        """
        if not self.visible:
            return
        
        # Отрисовка фона popup
        pygame.draw.rect(screen, self.COLORS['bg'], self.rect)
        pygame.draw.rect(screen, self.COLORS['border'], self.rect, 2)
        
        # Отрисовка заголовка
        title_rect = pygame.Rect(self.x, self.y, self.POPUP_WIDTH, self.TITLE_HEIGHT)
        pygame.draw.rect(screen, self.COLORS['title_bg'], title_rect)
        
        title_text = self.font_title.render(
            f"Creatures: {len(self.world.creatures)}", 
            True, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.PADDING_X
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Отрисовка заголовков столбцов
        header_y = self.y + self.TITLE_HEIGHT
        header_rect = pygame.Rect(self.x, header_y, self.POPUP_WIDTH, self.HEADER_HEIGHT)
        pygame.draw.line(screen, self.COLORS['border'], 
                        (self.x, header_y + self.HEADER_HEIGHT),
                        (self.x + self.POPUP_WIDTH, header_y + self.HEADER_HEIGHT), 1)
        
        headers = [
            ("ID", 30),
            ("Age", 40),
            ("X", 40),
            ("Y", 40),
            ("Energy", 60),
            ("Speed", 50),
        ]
        
        col_x = self.x + self.PADDING_X
        for header, width in headers:
            text = self.font.render(header, True, self.COLORS['header'])
            screen.blit(text, (col_x, header_y + 5))
            col_x += width
        
        # Отрисовка строк с существами
        row_y = header_y + self.HEADER_HEIGHT
        creatures = self.world.creatures[self.scroll_offset:self.scroll_offset + self.MAX_VISIBLE_ROWS]
        
        for idx, creature in enumerate(creatures):
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
                (str(actual_idx), 30),
                (str(creature.age), 40),
                (f"{creature.x:.1f}", 40),
                (f"{creature.y:.1f}", 40),
                (f"{creature.energy:.1f}", 60),
                (f"{creature.speed:.2f}", 50),
            ]
            
            col_x = self.x + self.PADDING_X
            for value, width in creature_data:
                text = self.font.render(value, True, text_color)
                screen.blit(text, (col_x, row_y + 2))
                col_x += width
            
            row_y += self.ROW_HEIGHT
        
        # Сообщение если нет существ
        if len(self.world.creatures) == 0:
            msg = self.font.render("No creatures", True, self.COLORS['text'])
            msg_x = self.x + (self.POPUP_WIDTH - msg.get_width()) // 2
            msg_y = self.y + self.TITLE_HEIGHT + (self.POPUP_HEIGHT - self.TITLE_HEIGHT - msg.get_height()) // 2
            screen.blit(msg, (msg_x, msg_y))
        
        # Отрисовка подсказки внизу
        help_text = "Use arrows to scroll, Home/End to jump, F1 or ESC to close"
        help_surface = self.font_small.render(help_text, True, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.PADDING_Y - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
