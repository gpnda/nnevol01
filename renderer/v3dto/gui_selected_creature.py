# -*- coding: utf-8 -*-
"""
SelectedCreaturePanel - v3dto версия.

Панель информации о выбранном существе.

Отображает:
- ID существа
- Возраст
- Текущую энергию
- Поколение
- Угол поворота
- Скорость
- Сенсорный ввод (видение) в виде цветных квадратов

Если существо не выбрано, панель не отображается.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, debugger, logger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
import numpy as np
from typing import Optional
from renderer.v3dto.dto import RenderStateDTO


class SelectedCreaturePanel:
    """
    Панель с информацией о выбранном существе.
    
    Отображается в левой части экрана с фиксированными координатами.
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Извлекает данные о существе из render_state.selected_creature
    - Извлекает видение из render_state.debug
    - Полностью изолирована от сингльтонов
    """
    
    # Координаты и размеры
    POSITION_X = 5
    POSITION_Y = 510
    WIDTH = 500
    HEIGHT = 60
    
    # Цвета
    COLORS = {
        'background': (5, 41, 158),
        'border': (150, 150, 150),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'highlight': (0, 255, 100),
    }
    
    # Размеры
    BORDER_WIDTH = 2
    PADDING = 5

    LINE_HEIGHT = 13
    FONT_SIZE = 16
    
    def __init__(self):
        """Инициализация панели."""
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифт для текста
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """
        Отрисовка панели с информацией о выбранном существе.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о выбранном существе
        """
        # Если существо не выбрано, ничего не рисуем
        if render_state.selected_creature is None:
            return
        
        selected_creature = render_state.selected_creature.creature
        
        # Очистка поверхности
        self.surface.fill(self.COLORS['background'])
        
        # Заголовок
        title_text = self.font.render(
            f"id: {selected_creature.id}",
            False,
            self.COLORS['highlight']
        )
        self.surface.blit(title_text, (self.PADDING, self.PADDING))


        # Хочу вывести энергию в виде прогресс-бара
        pygame.draw.rect(
                self.surface,
                self.COLORS['border'],
                (self.PADDING + 100, self.PADDING, 100, 12),
                self.BORDER_WIDTH
            )
        # Максимум энергии всегда = 1.0
        pygame.draw.rect(
            self.surface,
            self.COLORS['highlight'],
            (self.PADDING + 100 + self.BORDER_WIDTH,
             self.PADDING + self.BORDER_WIDTH,
             int((100 - 2 * self.BORDER_WIDTH) * min(selected_creature.energy, 1.0)),
             12 - 2 * self.BORDER_WIDTH)
        )
        
        # Информация о существе
        y_offset = self.PADDING + self.LINE_HEIGHT
        
        # Возраст
        age_label = self.font.render("Age:", False, self.COLORS['label'])
        self.surface.blit(age_label, (self.PADDING, y_offset))
        
        age_value = self.font.render(f"{selected_creature.age}", False, self.COLORS['text'])
        self.surface.blit(age_value, (self.PADDING + 100, y_offset))
        
        y_offset += self.LINE_HEIGHT
        
        # # Энергия
        # energy_label = self.font.render("Energy:", False, self.COLORS['label'])
        # self.surface.blit(energy_label, (self.PADDING, y_offset))
        
        # energy_value = self.font.render(
        #     f"{selected_creature.energy:.2f}",
        #     False,
        #     self.COLORS['text']
        # )
        # self.surface.blit(energy_value, (self.PADDING + 100, y_offset))
        
        # y_offset += self.LINE_HEIGHT
        
        # Поколение
        generation_label = self.font.render("Generation:", False, self.COLORS['label'])
        self.surface.blit(generation_label, (self.PADDING, y_offset))
        
        generation_value = self.font.render(
            f"{selected_creature.generation}",
            False,
            self.COLORS['text']
        )
        self.surface.blit(generation_value, (self.PADDING + 100, y_offset))
        
        y_offset += self.LINE_HEIGHT
        
        # Угол поворота
        # angle_label = self.font.render("Angle:", True, self.COLORS['label'])
        # self.surface.blit(angle_label, (self.PADDING, y_offset))
        
        # angle_value = self.font.render(
        #     f"{selected_creature.angle:.2f}°",
        #     True,
        #     self.COLORS['text']
        # )
        # self.surface.blit(angle_value, (self.PADDING + 100, y_offset))
        
        # y_offset += self.LINE_HEIGHT
        
        # Скорость
        # speed_label = self.font.render("Speed:", True, self.COLORS['label'])
        # self.surface.blit(speed_label, (self.PADDING, y_offset))
        
        # speed_value = self.font.render(
        #     f"{selected_creature.speed:.2f}",
        #     True,
        #     self.COLORS['text']
        # )
        # self.surface.blit(speed_value, (self.PADDING + 100, y_offset))

        # Количество потомков
        # Получим количество потомков из render_state CreatureEventDTO

        num_offspring = 0
        for event in render_state.selected_creature.history.events:
            if event.event_type == "CREATE_CHILD":
                num_offspring += event.value
        offspring_label = self.font.render(f"Offsprings:", False, self.COLORS['label'])
        self.surface.blit(offspring_label, (self.PADDING, y_offset))
        # Нарисуем потомков справа в виде кружков, по 10 штук в ряд
        for i in range(num_offspring):
            pygame.draw.circle(
                self.surface,
                (255, 165, 0),
                (self.PADDING + 100 + (i % 10) * 11 + 6, y_offset + 6 + (i // 10) * 5),
                4,
                2
            )
        
        # =====================================================================
        # Рисование видения (сенсорного ввода) выбранного существа
        # =====================================================================
        
        # Получаем видение из DebugDataDTO
        all_visions = render_state.debug.all_visions
        if all_visions is not None and render_state.selected_creature.creature.id is not None:
            # Индекс существа в массиве creatures
            creature_index = None
            for i, creature_dto in enumerate(render_state.world.creatures):
                if creature_dto.id == selected_creature.id:
                    creature_index = i
                    break
            
            if creature_index is not None and creature_index < len(all_visions):
                selected_creature_vision = all_visions[creature_index]
                
                # Преобразование в uint8 диапазон [0, 255]
                selected_creature_vision_int = (selected_creature_vision * 255).astype(np.uint8)
                selected_creature_vision_int_list = selected_creature_vision_int.tolist()
                
                # Преобразование в RGB кортежи
                # Видение состоит из 3 каналов по 15 сенсоров каждый
                rgb_tuples = list(zip(
                    selected_creature_vision_int_list[0:15],
                    selected_creature_vision_int_list[15:30],
                    selected_creature_vision_int_list[30:45]
                ))

                # Фон под видение и надпись
                pygame.draw.rect(
                    self.surface,
                    (0, 0, 0),
                    (225, 2, 215, 56)
                )
                # Граница видения
                pygame.draw.rect(
                    self.surface,
                    (50, 50, 50),
                    (231, 21, 202, 21),
                    2
                )
                vision_label = self.font.render("Vision:", False, self.COLORS['label'])
                self.surface.blit(vision_label, (233, 9))
                
                # Рисование видения в виде 15 цветных квадратов
                vision_block_y = self.HEIGHT - self.PADDING - 30
                square_size = 13
                for i, rgb in enumerate(rgb_tuples):
                    x = 235 + i * square_size
                    y = vision_block_y
                    pygame.draw.rect(self.surface, rgb, (x, y, square_size, square_size))
        
        # =====================================================================
        
        # Отрисовка на главный экран
        screen.blit(self.surface, (self.POSITION_X, self.POSITION_Y))
