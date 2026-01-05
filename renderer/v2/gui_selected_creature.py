# -*- coding: utf-8 -*-
"""
Панель информации о выбранном существе.

Отображает:
- Возраст существа
- Текущую энергию
- Другую релевантную информацию

Если существо не выбрано, панель не отображается.
"""

import pygame
from typing import Optional
from creature import Creature


class SelectedCreaturePanel:
    """
    Панель с информацией о выбранном существе.
    
    Отображается в левой части экрана с фиксированными координатами.
    """
    
    # Координаты и размеры
    POSITION_X = 35
    POSITION_Y = 150
    WIDTH = 250
    HEIGHT = 300
    
    # Цвета
    COLORS = {
        'background': (30, 30, 30),
        'border': (150, 150, 150),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'highlight': (0, 255, 100),
    }
    
    # Размеры
    BORDER_WIDTH = 2
    PADDING = 15
    LINE_HEIGHT = 25
    FONT_SIZE = 14
    
    def __init__(self):
        """Инициализация панели."""
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT))
        
        # Шрифт для текста
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, selected_creature: Optional[Creature]) -> None:
        """
        Отрисовка панели с информацией о выбранном существе.
        
        Args:
            screen: Pygame surface для отрисовки
            selected_creature: Выбранное существо (или None)
        """
        # Если существо не выбрано, ничего не рисуем
        if selected_creature is None:
            return
        
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Рисование границы
        pygame.draw.rect(
            self.surface,
            self.COLORS['border'],
            (0, 0, self.WIDTH, self.HEIGHT),
            self.BORDER_WIDTH
        )
        
        # Заголовок
        title_text = self.font.render("Selected Creature", True, self.COLORS['highlight'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Информация о существе
        y_offset = self.PADDING + self.LINE_HEIGHT + 10
        
        # Возраст
        age_label = self.font.render("Age:", True, self.COLORS['label'])
        self.surface.blit(age_label, (self.PADDING, y_offset))
        
        age_value = self.font.render(f"{selected_creature.age}", True, self.COLORS['text'])
        self.surface.blit(age_value, (self.PADDING + 100, y_offset))
        
        y_offset += self.LINE_HEIGHT
        
        # Энергия
        energy_label = self.font.render("Energy:", True, self.COLORS['label'])
        self.surface.blit(energy_label, (self.PADDING, y_offset))
        
        energy_value = self.font.render(f"{selected_creature.energy:.2f}", True, self.COLORS['text'])
        self.surface.blit(energy_value, (self.PADDING + 100, y_offset))
        
        y_offset += self.LINE_HEIGHT
        
        # Позиция
        position_label = self.font.render("Position:", True, self.COLORS['label'])
        self.surface.blit(position_label, (self.PADDING, y_offset))
        
        position_value = self.font.render(
            f"({int(selected_creature.x)}, {int(selected_creature.y)})",
            True,
            self.COLORS['text']
        )
        self.surface.blit(position_value, (self.PADDING + 100, y_offset))
        
        y_offset += self.LINE_HEIGHT
        
        # Угол поворота
        angle_label = self.font.render("Angle:", True, self.COLORS['label'])
        self.surface.blit(angle_label, (self.PADDING, y_offset))
        
        angle_value = self.font.render(f"{selected_creature.angle:.2f}°", True, self.COLORS['text'])
        self.surface.blit(angle_value, (self.PADDING + 100, y_offset))
        
        y_offset += self.LINE_HEIGHT
        
        # Скорость
        speed_label = self.font.render("Speed:", True, self.COLORS['label'])
        self.surface.blit(speed_label, (self.PADDING, y_offset))
        
        speed_value = self.font.render(f"{selected_creature.speed:.2f}", True, self.COLORS['text'])
        self.surface.blit(speed_value, (self.PADDING + 100, y_offset))
        
        # Отрисовка на главный экран
        screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
