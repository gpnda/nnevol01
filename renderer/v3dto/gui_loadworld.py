# -*- coding: utf-8 -*-
"""
PopupLoadWorldModal - v3dto версия.

Модальное окно загрузки мира.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
- Может быть открыто и закрыто через state machine Renderer'а
"""


import pygame
from typing import Any, Callable, Dict, List, Optional
from renderer.v3dto.dto import RenderStateDTO


class PopupLoadWorldModal:
    """
    Модальное окно для загрузки мира.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Полностью изолирована от сингльтонов
    """

    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 830
    POPUP_HEIGHT = 500
    
    # Параметры отображения
    FONT_SIZE = 16
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
        'selected': (0, 167, 225),    # Голубой для выделения
    }


    def __init__(self, on_do_loadworld: Optional[Callable[[str], None]] = None):
        """Инициализация модального окна загрузки мира.
            
            Args:
            on_do_loadworld: Callback при подтверждении загрузки мира
                            Сигнатура: on_do_loadworld(save_file_name: str)
        """

        # Callback функция
        self.on_do_loadworld = on_do_loadworld

        # Список слотов сохранения мира. Будет заполнен через renderer._on_state_enter()
        self.save_slots = []

        # Флаг для отслеживания момента закрытия окна после загрузки мира
        self.just_loaded = False  # ← Добавляем флаг

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
        
        # Состояние для навигации по таблице
        self.selected_slot = 0  # Глобальный индекс выбранного слота
        self.slots_list = []  # Кэш списка слотов для навигации
        self.current_page = 0  # Текущая страница (начинается с 0)
        
        # Ширина столбцов (в пикселях)
        self.col_widths = {
            'id': 30,
            'name': 240,
            'modified_at': 130,
            'creatures_count': 90,
            'max_generation': 80,
            'map_size': 80,
        }
    
    @property
    def rows_per_page(self) -> int:
        """Количество строк, которые поместятся на одну страницу."""
        available_height = (
            self.POPUP_HEIGHT 
            - self.TITLE_HEIGHT 
            - self.CONTENT_PADDING * 3  # вверху, внизу и перед help
            - self.LINE_HEIGHT  # для help_text
        )
        return max(1, available_height // self.LINE_HEIGHT)
    
    @property
    def total_pages(self) -> int:
        """Общее количество страниц."""
        if len(self.slots_list) == 0:
            return 1
        return (len(self.slots_list) + self.rows_per_page - 1) // self.rows_per_page


    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовка модального окна загрузки мира с таблицей слотов
        
        Args:
            screen: Pygame surface для отрисовки
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
            "LOAD", 
            False, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.CONTENT_PADDING
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Стартовая позиция для таблицы
        table_y = self.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        table_x = self.x + self.CONTENT_PADDING
        
        # Получаем список слотов из переданного списка (или пустой список если нет)
        self.slots_list = self.save_slots
        
        # Отрисовка заголовка таблицы
        self._draw_table_header(screen, table_x, table_y)
        table_y += self.LINE_HEIGHT
        
        # Вычисляем диапазон слотов для текущей страницы
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.slots_list))
        
        # Отрисовка строк таблицы (только для текущей страницы)
        for global_slot_id in range(start_idx, end_idx):
            slot_info = self.slots_list[global_slot_id]
            
            # Определяем цвет строки (выбранная или нет)
            row_bg_color = self.COLORS['selected'] if global_slot_id == self.selected_slot else None
            
            # Отрисовка строки таблицы
            self._draw_table_row(
                screen, 
                table_x, 
                table_y, 
                global_slot_id, 
                slot_info,
                is_selected=(global_slot_id == self.selected_slot),
                row_bg_color=row_bg_color
            )
            table_y += self.LINE_HEIGHT
        
        # Отрисовка подсказки внизу
        help_text = "UP/DOWN: navigate | LEFT/RIGHT: pages | ENTER: load | ESC: close"
        help_surface = self.font.render(help_text, False, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.CONTENT_PADDING - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
        
        # Отрисовка информации о странице
        page_text = f"Page {self.current_page + 1}/{self.total_pages}"
        page_surface = self.font.render(page_text, False, self.COLORS['text'])
        page_x = self.x + self.CONTENT_PADDING
        page_y = self.y + self.POPUP_HEIGHT - self.CONTENT_PADDING - page_surface.get_height()
        screen.blit(page_surface, (page_x, page_y))
    
    def _draw_table_header(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Отрисовка заголовока таблицы с разделителями столбцов."""
        col_y = y
        col_x = x
        
        headers = ['ID', 'Name', 'Modified At', 'Creatures', 'Max Gen', 'Map Size']
        widths = [
            self.col_widths['id'],
            self.col_widths['name'],
            self.col_widths['modified_at'],
            self.col_widths['creatures_count'],
            self.col_widths['max_generation'],
            self.col_widths['map_size'],
        ]
        
        for header, width in zip(headers, widths):
            header_text = self.font.render(header, False, self.COLORS['label'])
            screen.blit(header_text, (col_x, col_y))
            col_x += width + 10
        
    
    def _draw_table_row(
        self, 
        screen: pygame.Surface, 
        x: int, 
        y: int, 
        slot_id: int, 
        slot_info: dict,
        is_selected: bool = False,
        row_bg_color: Optional[tuple] = None,
    ) -> None:
        """
        Отрисовка одной строки таблицы.
        
        Args:
            screen: Pygame surface
            x, y: Позиция строки
            slot_id: ID слота
            slot_info: Информация о слоте (dict)
            is_selected: Выбрана ли эта строка
            row_bg_color: Цвет фона строки
        """
        # Отрисовка фона выбранной строки
        if is_selected and row_bg_color:
            row_rect = pygame.Rect(
                x - 5, 
                y - 5, 
                sum(self.col_widths.values()) + len(self.col_widths) * 10, 
                self.LINE_HEIGHT
            )
            pygame.draw.rect(screen, row_bg_color, row_rect)
        
        col_x = x
        
        # Форматируем значения для таблицы
        id_str = str(slot_id)
        name_str = str(slot_info.get('name', 'Unknown'))[:35]
        modified_at_str = str(slot_info.get('modified_at', 'N/A'))
        creatures_val = slot_info.get('creatures_count')
        creatures_str = str(creatures_val) if creatures_val is not None else 'N/A'
        generation_val = slot_info.get('max_generation')
        generation_str = str(generation_val) if generation_val is not None else 'N/A'
        map_size_str = str(slot_info.get('map_size', 'N/A'))
        
        values = [id_str, name_str, modified_at_str, creatures_str, generation_str, map_size_str]
        widths = [
            self.col_widths['id'],
            self.col_widths['name'],
            self.col_widths['modified_at'],
            self.col_widths['creatures_count'],
            self.col_widths['max_generation'],
            self.col_widths['map_size'],
        ]
        
        # Отрисовка каждого столбца
        text_color = self.COLORS['label'] if is_selected else self.COLORS['text']
        for value, width in zip(values, widths):
            value_text = self.font.render(value, False, text_color)
            screen.blit(value_text, (col_x, y))
            col_x += width + 10  # +10 для отступа между столбцами
    
    def move_selection_up(self) -> None:
        """Переместить выбор вверх по таблице."""
        if self.selected_slot > 0:
            self.selected_slot -= 1
            self._ensure_selection_visible()
    
    def move_selection_down(self) -> None:
        """Переместить выбор вниз по таблице."""
        if self.selected_slot < len(self.slots_list) - 1:
            self.selected_slot += 1
            self._ensure_selection_visible()
    
    def move_page_left(self) -> None:
        """Перейти на предыдущую страницу."""
        if self.current_page > 0:
            self.current_page -= 1
            # Выбираем первый слот новой страницы
            self.selected_slot = self.current_page * self.rows_per_page
    
    def move_page_right(self) -> None:
        """Перейти на следующую страницу."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            # Выбираем первый слот новой страницы
            self.selected_slot = self.current_page * self.rows_per_page
    
    def _ensure_selection_visible(self) -> None:
        """Убедиться, что выбранный слот видим на текущей странице."""
        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        
        # Если выбранный слот вне видимого диапазона, переместить на нужную страницу
        if self.selected_slot < start_idx:
            self.current_page = self.selected_slot // self.rows_per_page
        elif self.selected_slot >= end_idx:
            self.current_page = self.selected_slot // self.rows_per_page
    
    def reset(self) -> None:
        """Сбросить выбор на первый слот первой страницы."""
        self.selected_slot = 0
        self.current_page = 0

    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий для модального окна загрузки мира.
        
        Args:
            event: Pygame событие для обработки
            
        Returns:
            True если событие было обработано
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_UP:
            self.move_selection_up()
            return True
        
        elif event.key == pygame.K_DOWN:
            self.move_selection_down()
            return True
        
        elif event.key == pygame.K_LEFT:
            self.move_page_left()
            return True
        
        elif event.key == pygame.K_RIGHT:
            self.move_page_right()
            return True
        
        elif event.key == pygame.K_RETURN:
            # Вызываем callback с полным stem файла сохранения
            if self.on_do_loadworld is not None and 0 <= self.selected_slot < len(self.slots_list):
                selected_slot_info = self.slots_list[self.selected_slot]
                save_file_name = selected_slot_info.get('filename', '')
                self.on_do_loadworld(save_file_name)
                self.just_loaded = True  # Устанавливаем флаг, что мир был загружен
            return True
        
        return False
    
    def should_close(self) -> bool:
        if self.just_loaded:
            self.just_loaded = False
            return True
        return False