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
    POPUP_WIDTH = 1000
    POPUP_HEIGHT = 550
    
    # Параметры отображения
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 30
    HEADER_HEIGHT = 25
    ROW_WIDTH = 175
    ROW_HEIGHT = 18
    PADDING_X = 10
    PADDING_Y = 8
    
    # Максимум строк в окне (для скролла)
    MAX_VISIBLE_ROWS = 23
    
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
        self.selected_index = 0  # Индекс выбранного существа в списке (НЕ creature.id !!!)
        
        # detail_creature_id: ID выбранного существа для отрисовки в других виджетах
        # Это значение записывается в CreaturesListDTO в renderer._prepare_creatures_list_dto()
        # и затем передается всем виджету CreatureWeightsWidget (gui_creature_weights.py) через RenderStateDTO
        self.detail_creature_id = None
        
        # Инициализация шрифтов
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font_small = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 2)
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_small = pygame.font.Font(None, self.FONT_SIZE)
        
        # Позиция и размер окна (будут вычислены при первом draw)
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)
    
    def handle_event(self, event: pygame.event.Event, render_state: 'RenderStateDTO') -> bool:
        """Обработка событий клавиатуры. Возвращает True если окно нужно закрыть."""
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1:
            return True  # Сигнал закрыть окно
        
        if event.key == pygame.K_UP:
            self.move_selection_up(render_state)
        elif event.key == pygame.K_DOWN:
            self.move_selection_down(render_state)
        elif event.key == pygame.K_HOME:
            self.move_selection_home(render_state)
        elif event.key == pygame.K_END:
            self.move_selection_end(render_state)
        
        return False  # Окно остается открытым
    
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
            False, 
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
            ("Gen", 40),
            ("Energy", 65),
            ("Health", 65),
        ]
        
        col_x = self.x + self.PADDING_X
        for header, width in headers:
            text = self.font.render(header, False, self.COLORS['header'])
            screen.blit(text, (col_x, header_y + 5))
            col_x += width
        
        # Отрисовка строк с существами
        if creatures_count == 0:
            # Сообщение если нет существ
            msg = self.font.render("No creatures", False, self.COLORS['text'])
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
                    row_rect = pygame.Rect(self.x + 1, row_y, self.ROW_WIDTH, self.ROW_HEIGHT)
                    pygame.draw.rect(screen, self.COLORS['selected'], row_rect)
                    text_color = self.COLORS['selected_text']
                else:
                    text_color = self.COLORS['text']
                
                # Данные существа
                creature_data = [
                    (str(creature.id), 35),
                    (str(creature.age), 40),
                    (str(creature.generation), 40),
                    (f"{creature.energy:.1f}", 65),
                    (f"{creature.health:.1f}", 65),
                ]
                
                col_x = self.x + self.PADDING_X
                for value, width in creature_data:
                    text = self.font.render(value, False, text_color)
                    screen.blit(text, (col_x, row_y + 2))
                    col_x += width
                
                row_y += self.ROW_HEIGHT
        
        # Отрисуем правую панель с информацией о выбранном существе
        # detail_creature_id = creatures[self.selected_index].id if self.selected_index < len(creatures) else "—"
        # Нет, будем рисовать правую панель в виде отдельного виджета

        # Отрисовка подсказки внизу
        help_text = "Arrows: scroll | Home/End: jump | ESC: close"
        help_surface = self.font_small.render(help_text, False, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.PADDING_Y - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
    
    # ========================================================================
    # НАВИГАЦИЯ (вызывается из Renderer._handle_creatures_list_keyboard())
    # ========================================================================
    
    def move_selection_up(self, render_state: 'RenderStateDTO') -> None:
        """Переместить выделение на одну строку вверх."""
        if len(render_state.world.creatures) == 0:
            return
        if self.selected_index > 0:
            self.selected_index -= 1
            # Автоскролл
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
        self.detail_creature_id = render_state.world.creatures[self.selected_index].id if self.selected_index < len(render_state.world.creatures) else None
    
    def move_selection_down(self, render_state: 'RenderStateDTO') -> None:
        """Переместить выделение на одну строку вниз."""
        if len(render_state.world.creatures) == 0:
            return
        if self.selected_index < len(render_state.world.creatures) - 1:
            self.selected_index += 1
            # Автоскролл
            if self.selected_index >= self.scroll_offset + self.MAX_VISIBLE_ROWS:
                self.scroll_offset = self.selected_index - self.MAX_VISIBLE_ROWS + 1
        self.detail_creature_id = render_state.world.creatures[self.selected_index].id if self.selected_index < len(render_state.world.creatures) else None
    
    def move_selection_home(self, render_state: 'RenderStateDTO') -> None:
        """Переместить выделение в начало списка."""
        self.selected_index = 0
        self.scroll_offset = 0
        self.detail_creature_id = render_state.world.creatures[self.selected_index].id if self.selected_index < len(render_state.world.creatures) else None
    
    def move_selection_end(self, render_state: 'RenderStateDTO') -> None:
        """Переместить выделение в конец списка."""
        if len(render_state.world.creatures) == 0:
            return
        self.selected_index = len(render_state.world.creatures) - 1
        self.scroll_offset = max(0, len(render_state.world.creatures) - self.MAX_VISIBLE_ROWS)
        self.detail_creature_id = render_state.world.creatures[self.selected_index].id if self.selected_index < len(render_state.world.creatures) else None
    
    def reset(self) -> None:
        """Сбросить состояние навигации (вызывается при открытии модала)."""
        self.scroll_offset = 0
        self.selected_index = 0
        self.detail_creature_id = None
    
    def get_selected_creature_id(self, render_state: 'RenderStateDTO') -> int:
        """Получить ID выбранного существа."""
        creatures_count = len(render_state.world.creatures)
        if creatures_count > 0 and self.selected_index < creatures_count:
            return render_state.world.creatures[self.selected_index].id if self.selected_index < len(render_state.world.creatures) else -1
        return -1
