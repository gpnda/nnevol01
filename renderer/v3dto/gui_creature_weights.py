# -*- coding: utf-8 -*-
"""
CreatureWeightsWidget - v3dto версия.

Виджет для отображения весов нейросети выбранного существа.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, debugger, logger, creature objects
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class CreatureWeightsWidget:
    """
    Виджет для отображения весов нейросети существа.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает данные о существе из render_state.selected_creature
    - Полностью изолирована от сингльтонов
    
    TODO: В будущем нужно добавить отображение реальных весов из nn (neural network).
          Для этого потребуется:
          - Добавить веса в CreatureDTO (через creatures_list_state.detail_creature_id)
          Пока это просто placeholder-заглушка.
    """
    
    # Координаты и размеры
    WIDGET_X = 370
    WIDGET_Y = 58
    WIDTH = 750
    HEIGHT = 475
    
    # Цвета
    COLORS = {
        'background': (20, 20, 30),
        'border': (100, 150, 200),
        'text': (200, 200, 200),
        'title': (0, 200, 255),
        'placeholder': (150, 150, 150),
    }
    
    # Размеры
    BORDER_WIDTH = 0
    PADDING = 10
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    def __init__(self):
        """Инициализация виджета без зависимостей."""
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифт для текста
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка виджета с весами существа.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о выбранном существе в creatures_list
        """
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Рисуем границу
        # pygame.draw.rect(
        #     self.surface,
        #     self.COLORS['border'],
        #     (0, 0, self.WIDTH - 1, self.HEIGHT - 1),
        #     self.BORDER_WIDTH
        # )
        
        # Заголовок
        title_text = self.font.render("Creature Weights", True, self.COLORS['title'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Получаем информацию о выбранном существе из creatures_list_state
        if render_state.creatures_list_state is None:
            # Никакое существо не выбрано в creatures_list
            placeholder_text = self.font.render(
                "No creature selected in list",
                True,
                self.COLORS['placeholder']
            )
            self.surface.blit(
                placeholder_text,
                (self.PADDING, self.PADDING + 30)
            )
        else:
            # Получаем ID выбранного существа
            creature_id = render_state.creatures_list_state.detail_creature_id
            
            # Ищем существо по ID в world DTO
            creature_dto = render_state.world.get_creature_by_id(creature_id)
            
            if creature_dto is None:
                # Существо не найдено (может быть погибло)
                placeholder_text = self.font.render(
                    f"Creature #{creature_id} not found",
                    True,
                    self.COLORS['placeholder']
                )
                self.surface.blit(
                    placeholder_text,
                    (self.PADDING, self.PADDING + 30)
                )
            else:
                # Отображаем информацию о существе
                creature_id_text = self.font.render(
                    f"Creature #{creature_id}",
                    True,
                    self.COLORS['text']
                )
                self.surface.blit(
                    creature_id_text,
                    (self.PADDING, self.PADDING + 30)
                )
                
                # Информация о существе
                info_lines = [
                    f"Age: {creature_dto.age}",
                    f"Energy: {creature_dto.energy:.1f}",
                    f"Health: {creature_dto.health:.1f}",
                    f"Generation: {creature_dto.generation}",
                ]
                
                y_offset = self.PADDING + 60
                for line in info_lines:
                    line_text = self.font.render(line, True, self.COLORS['placeholder'])
                    self.surface.blit(line_text, (self.PADDING, y_offset))
                    y_offset += 20
                
                # Placeholder для весов
                placeholder_text = self.font.render(
                    "[Neural Network Weights - TODO]",
                    True,
                    self.COLORS['placeholder']
                )
                self.surface.blit(
                    placeholder_text,
                    (self.PADDING, y_offset + 10)
                )
        
        # Отобразить на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
