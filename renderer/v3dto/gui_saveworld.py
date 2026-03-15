# -*- coding: utf-8 -*-
"""
PopupSaveWorldModal - v3dto версия.

Модальное окно сохранения мира.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
- Может быть открыто и закрыто через state machine Renderer'а
"""


import pygame
from typing import Callable, Optional
from renderer.v3dto.dto import RenderStateDTO


class PopupSaveWorldModal:
    """
    Модальное окно для сохранения мира.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Полностью изолирована от сингльтонов
    """

    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 830
    POPUP_HEIGHT = 300
    
    # Параметры отображения
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 30
    CONTENT_PADDING = 20
    LINE_HEIGHT = 25
    INPUT_FIELD_HEIGHT = 32
    INPUT_FIELD_WIDTH = 600
    MAX_FILENAME_LENGTH = 50

    # Цвета в стиле BIOS
    COLORS = {
        'bg': (5, 41, 158),           # Синий фон
        'border': (170, 170, 170),    # Серая граница
        'title_bg': (0, 167, 225),    # Голубой заголовок
        'title_text': (0, 0, 0),      # Чёрный текст в заголовке
        'text': (170, 170, 170),      # Серый текст
        'label': (255, 255, 255),     # Белый для меток
        'value': (0, 255, 100),       # Зелёный для значений
        'selected': (0, 167, 225),    # Голубой для выделения
        'input_bg': (0, 0, 0),        # Чёрный фон для поля ввода
        'input_border': (0, 255, 100),# Зелёная граница поля ввода
        'cursor': (0, 255, 100),      # Зелёный курсор
    }


    def __init__(self, on_do_saveworld: Optional[Callable[[str], None]] = None):
        """Инициализация модального окна сохранения мира.
            
            Args:
            on_do_saveworld: Callback при подтверждении сохранения мира
                            Сигнатура: on_do_saveworld(save_file_name: str)
        """

        # Callback функция
        self.on_do_saveworld = on_do_saveworld

        # Инициализация шрифтов
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE + 2)
            self.font_biginput = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE + 4)
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font_small = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE - 2)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 2)
            self.font_biginput = pygame.font.Font(None, self.FONT_SIZE + 4)
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_small = pygame.font.Font(None, self.FONT_SIZE - 2)
        

        # Позиция и размер окна (будут вычислены при первом draw)
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        
        # Поле ввода имени файла
        self.file_name = ""
        

    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка модального окна сохранения мира
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными для отображения
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
            "SAVE", 
            False, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.CONTENT_PADDING
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Отрисовка содержимого окна
        content_start_y = self.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        
        # Метка "Filename:"
        label_text = self.font.render("Filename:", False, self.COLORS['label'])
        screen.blit(label_text, (self.x + self.CONTENT_PADDING, content_start_y))
        
        # Поле ввода имени файла
        input_y = content_start_y + self.LINE_HEIGHT
        input_rect = pygame.Rect(
            self.x + self.CONTENT_PADDING,
            input_y,
            self.INPUT_FIELD_WIDTH,
            self.INPUT_FIELD_HEIGHT
        )
        
        # Отрисовка фона и границы поля ввода
        pygame.draw.rect(screen, self.COLORS['input_bg'], input_rect)
        pygame.draw.rect(screen, self.COLORS['input_border'], input_rect, 2)
        
        # Отрисовка текста в поле ввода
        display_text = self.file_name
        if len(display_text) > 40:  # Обрезаем если слишком длинный
            display_text = "..." + display_text[-37:]
        
        text_surface = self.font_biginput.render(display_text, False, self.COLORS['value'])
        text_x = input_rect.x + 5
        text_y = input_rect.y + (input_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # Отрисовка курсора (подчеркивание)
        cursor_x = text_x + text_surface.get_width()
        cursor_y = text_y + text_surface.get_height()
        cursor_width = 8
        pygame.draw.line(screen, self.COLORS['cursor'], 
                       (cursor_x, cursor_y), 
                       (cursor_x + cursor_width, cursor_y), 2)
        
        # Инструкции
        instructions = [
            "Enter - Save  |  Esc - Cancel",
            "A-Z, 0-9, _ , -  allowed",
            "Do not include file extension, will be added automatically",
            "If file exists, random slug will be added.",
        ]
        
        instr_y = input_y + self.INPUT_FIELD_HEIGHT + self.CONTENT_PADDING
        for i, instr in enumerate(instructions):
            instr_text = self.font.render(instr, False, self.COLORS['text'])
            screen.blit(instr_text, (self.x + self.CONTENT_PADDING, instr_y + i * 20))
        
    
    
    def reset(self) -> None:
        """Сбросить поле ввода."""
        self.file_name = ""
    
    
    
    def _is_valid_char(self, key_code: int, unicode_char: str) -> bool:
        """
        Проверка, является ли символ валидным для имени файла.
        Разрешены: A-Z, a-z, 0-9, _, -
        
        Args:
            key_code: pygame key code
            unicode_char: unicode символ (если доступен)
        
        Returns:
            True если символ валидный
        """
        # Проверяем ASCII коды
        # 48-57: 0-9
        # 65-90: A-Z
        # 97-122: a-z
        # 45: -
        # 95: _
        
        if unicode_char:
            char_code = ord(unicode_char)
            if (48 <= char_code <= 57 or    # 0-9
                65 <= char_code <= 90 or    # A-Z
                97 <= char_code <= 122 or   # a-z
                char_code == 45 or          # -
                char_code == 95):           # _
                return True
        
        return False
    
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий для модального окна сохранения мира.
        
        Args:
            event: Pygame событие для обработки
            
        Returns:
            True если событие было обработано
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Обработка Enter - сохранение
        if event.key == pygame.K_RETURN:
            if self.file_name.strip():  # Сохраняем только если имя не пусто
                if self.on_do_saveworld is not None:
                    self.on_do_saveworld(self.file_name)
            return True
        
        # Обработка Escape - отмена (окно закроет родитель)
        elif event.key == pygame.K_ESCAPE:
            self.reset()
            return False  # Сигнал родителю закрыть окно
        
        # Обработка Backspace - удаление последнего символа
        elif event.key == pygame.K_BACKSPACE:
            if self.file_name:
                self.file_name = self.file_name[:-1]
            return True
        
        # Обработка обычных символов (A-Z, 0-9, _, -)
        else:
            # Используем event.unicode для получения символа
            if event.unicode and self._is_valid_char(event.key, event.unicode):
                if len(self.file_name) < self.MAX_FILENAME_LENGTH:
                    self.file_name += event.unicode
                return True
        
        return False