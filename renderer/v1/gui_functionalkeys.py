# -*- coding: utf-8 -*-
"""
Панель функциональных клавиш в стиле BIOS/Norton Commander.
"""

import pygame
from typing import Dict, Tuple, Callable


class FunctionKeysPanel:
    """Панель функциональных клавиш для управления приложением."""
    
    # Геометрия панели на экране (явные значения)
    PANEL_X = 5
    PANEL_Y = 545
    PANEL_WIDTH = 220
    PANEL_HEIGHT = 50
    
    # Параметры отображения
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    # Внутренние смещения
    PADDING_X = 10
    PADDING_Y = 8
    ROW_HEIGHT = 20
    KEYS_PER_ROW = 3  # Сколько клавиш в строке
    
    # Цвета
    COLORS = {
        'bg': (5, 41, 158),
        'text': (170, 170, 170),
        'highlight': (255, 255, 255),
        'func_key': (170, 170, 0),
        'border': (5, 41, 158),
    }
    
    def __init__(self, app):
        """Инициализация панели функциональных клавиш."""

        self.app = app

        # Геометрия
        self.rect = pygame.Rect(self.PANEL_X, self.PANEL_Y,
                                self.PANEL_WIDTH, self.PANEL_HEIGHT)
        
        # Шрифт
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
        
        # Функциональные клавиши: {key: (description, callback)}
        self.function_keys: Dict[str, Tuple[str, Callable]] = {}

        # Добавление функциональных клавиш
        #self.func_keys_panel.add_function_key("F1", "Save", self.app.saveWorld)
        self.add_function_key("F2", "Load", self.app.loadWorld)
        self.add_function_key("F3", "Reset", self.app.resetWorld)
        self.add_function_key("F4", "Exit", self.app.terminate)
        
        self.add_function_key("F3", "SimParams", self.app.world.simparams_print)
    
    def add_function_key(self, key: str, description: str, 
                        callback: Callable) -> None:
        """
        Добавить функциональную клавишу.
        
        Args:
            key: Название клавиши (например "F1", "F2")
            description: Описание функции (выводится в панели)
            callback: Функция вызываемая при нажатии клавиши
        """
        self.function_keys[key] = (description, callback)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий клавиатуры.
        
        Args:
            event: pygame.event.Event клавиатурного события
            
        Returns:
            True если событие обработано
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Маппинг клавиш F1-F12 к кодам pygame
        key_map = {
            pygame.K_F1: "F1",
            pygame.K_F2: "F2",
            pygame.K_F3: "F3",
            pygame.K_F4: "F4",
            pygame.K_F5: "F5",
            pygame.K_F6: "F6",
            pygame.K_F7: "F7",
            pygame.K_F8: "F8",
            pygame.K_F9: "F9",
            pygame.K_F10: "F10",
            pygame.K_F11: "F11",
            pygame.K_F12: "F12",
        }
        
        # Проверяем нажата ли функциональная клавиша
        key_name = key_map.get(event.key)
        if key_name and key_name in self.function_keys:
            description, callback = self.function_keys[key_name]
            callback()
            return True
        
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовка панели функциональных клавиш на экран.
        
        Args:
            screen: pygame.Surface главного экрана
        """
        
        # Фон панели
        pygame.draw.rect(screen, self.COLORS['bg'], self.rect)
        pygame.draw.rect(screen, self.COLORS['highlight'], self.rect, 2)
        
        # Отрисовка функциональных клавиш
        func_keys_list = list(self.function_keys.items())
        y_offset = self.rect.y + self.PADDING_Y
        col_count = 0
        
        for idx, (key, (description, _)) in enumerate(func_keys_list):
            # Вычисляем позицию с учетом количества колонок
            row = idx // self.KEYS_PER_ROW
            col = idx % self.KEYS_PER_ROW
            
            x_offset = self.rect.x + self.PADDING_X + col * (self.rect.width // self.KEYS_PER_ROW)
            y_pos = y_offset + row * self.ROW_HEIGHT
            
            # # Проверяем выходит ли за границы панели
            # if y_pos + self.ROW_HEIGHT > self.rect.y + self.rect.height:
            #     break
            
            # Текст: "F1: Description"
            text = f"{key}: {description}"
            text_surf = self.font.render(text, False, self.COLORS['func_key'])
            screen.blit(text_surf, (x_offset, y_pos))
