# -*- coding: utf-8 -*-
"""
Viewport для v3dto - ПРИМЕР как переписать виджет для DTO архитектуры.

Это показывает как превратить старый Viewport (v2) в новый (v3dto)
с полной изоляцией от world и debugger синглтона.

КЛЮЧЕВЫЕ ИЗМЕНЕНИЯ:
1. ❌ Удалили: `from service.debugger.debugger import debug`
2. ❌ Удалили: параметр `world` из __init__
3. ✅ Добавили: параметр `render_state: RenderStateDTO` в draw()
4. ✅ Все данные берем из render_state вместо self.world и debug синглтона

STATUS: ПРИМЕР (не полный, показывает архитектуру)
TODO: Скопировать логику из renderer/v2/gui_viewport.py
"""

import pygame
from typing import Optional
import numpy as np

# ✅ ТОЛЬКО DTO импорты, БЕЗ domain логики!
from renderer.v3dto.dto import RenderStateDTO, WorldStateDTO, CreatureDTO, FoodDTO


class Viewport:
    """
    Viewport для v3dto - визуализация карты мира.
    
    Ключевая архитектурная разница от v2:
    - ❌ НЕ зависит от world объекта
    - ❌ НЕ зависит от debug синглтона
    - ✅ Работает только с RenderStateDTO
    - ✅ Полностью тестируем с mock DTO
    """
    
    # Расположение viewport на экране (пиксели)
    VIEWPORT_X = 5
    VIEWPORT_Y = 5
    VIEWPORT_WIDTH = 1240
    VIEWPORT_HEIGHT = 500
    
    # Параметры камеры по умолчанию
    CAMERA_OFFSET_DEFAULT = pygame.Vector2(0, -6.0)
    CAMERA_SCALE_DEFAULT = 8.0
    CAMERA_SCALE_MIN = 7.0
    CAMERA_SCALE_MAX = 50.0
    
    # Цвета для отрисовки
    COLORS = {
        'bg': (10, 10, 10),
        'border': (5, 41, 158),
        'wall': (50, 50, 50),
        'food': (219, 80, 74),
        'creature': (50, 50, 255),
        'creature_selected': (0, 255, 0),
        'raycast_dot': (100, 100, 100),
        'text': (200, 200, 200),
    }
    
    def __init__(self):
        """
        Инициализация viewport.
        
        ✅ БЕЗ параметров!
        ✅ БЕЗ зависимости от world!
        
        КЛЮЧЕВОЕ ОТЛИЧИЕ от v2:
        - v2: def __init__(self, world=None): self.world = world
        - v3dto: def __init__(self): pass (только UI параметры)
        """
        # Геометрия viewport на экране
        self.rect = pygame.Rect(self.VIEWPORT_X, self.VIEWPORT_Y, 
                                self.VIEWPORT_WIDTH, self.VIEWPORT_HEIGHT)
        
        # Поверхность для отрисовки карты
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        
        # Параметры камеры
        self.camera_offset = self.CAMERA_OFFSET_DEFAULT.copy()
        self.camera_scale = self.CAMERA_SCALE_DEFAULT
        
        # Состояние перетаскивания карты
        self.is_dragging = False
        self.drag_start_pos = pygame.Vector2(0, 0)
        self.drag_start_offset = pygame.Vector2(0, 0)
        
        # Шрифт для отладочной информации
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', 14)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, 14)

    # ============================================================================
    # ПРЕОБРАЗОВАНИЯ КООРДИНАТ
    # ============================================================================
    
    def screen_to_map(self, screen_pos: tuple) -> Optional[pygame.Vector2]:
        """
        Преобразует координаты экрана в координаты карты.
        
        Returns:
            pygame.Vector2 с координатами на карте или None если не в viewport
        """
        if not self.rect.collidepoint(screen_pos):
            return None
        
        # Координаты относительно viewport
        viewport_x = screen_pos[0] - self.rect.x
        viewport_y = screen_pos[1] - self.rect.y
        
        # Преобразование в координаты карты
        map_x = (viewport_x / self.camera_scale) + self.camera_offset.x
        map_y = (viewport_y / self.camera_scale) + self.camera_offset.y
        
        return pygame.Vector2(map_x, map_y)
    
    def map_to_viewport(self, map_pos: pygame.Vector2) -> pygame.Vector2:
        """
        Преобразует координаты карты в координаты относительно viewport поверхности.
        """
        viewport_x = (map_pos.x - self.camera_offset.x) * self.camera_scale
        viewport_y = (map_pos.y - self.camera_offset.y) * self.camera_scale
        
        return pygame.Vector2(viewport_x, viewport_y)
    
    def get_visible_range(self, world_dto: WorldStateDTO) -> tuple:
        """
        Возвращает диапазон видимых клеток карты.
        
        Args:
            world_dto: WorldStateDTO для получения размеров мира
        
        Returns:
            (min_x, max_x, min_y, max_y) - границы видимой области на карте
        """
        min_x = max(0, int(self.camera_offset.x))
        max_x = min(world_dto.width, int(self.camera_offset.x + self.rect.width / self.camera_scale))
        
        min_y = max(0, int(self.camera_offset.y))
        max_y = min(world_dto.height, int(self.camera_offset.y + self.rect.height / self.camera_scale))
        
        return (min_x, max_x, min_y, max_y)

    # ============================================================================
    # ОБРАБОТКА СОБЫТИЙ
    # ============================================================================
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий мыши (пан, зум).
        
        Returns:
            True если событие обработано
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка - пан
                self.is_dragging = True
                self.drag_start_pos = pygame.Vector2(event.pos)
                self.drag_start_offset = self.camera_offset.copy()
                return True
            elif event.button == 4:  # Колесо вверх - приближение
                self._handle_zoom(event.pos, 1.1)
                return True
            elif event.button == 5:  # Колесо вниз - отдаление
                self._handle_zoom(event.pos, 0.9)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Отпуск левой кнопки
                self.is_dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Вычисляем смещение
                delta = pygame.Vector2(event.pos) - self.drag_start_pos
                
                # Преобразуем пиксели в координаты карты
                offset_delta = delta / self.camera_scale
                
                # Применяем смещение к камере
                self.camera_offset = self.drag_start_offset - offset_delta
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R - сброс камеры
                self.camera_offset = self.CAMERA_OFFSET_DEFAULT.copy()
                self.camera_scale = self.CAMERA_SCALE_DEFAULT
                return True
        
        return False
    
    def _handle_zoom(self, mouse_pos: tuple, zoom_factor: float) -> None:
        """Обработка масштабирования (зум)."""
        # Ограничиваем масштаб
        new_scale = self.camera_scale * zoom_factor
        new_scale = max(self.CAMERA_SCALE_MIN, min(self.CAMERA_SCALE_MAX, new_scale))
        
        if new_scale == self.camera_scale:
            return  # Масштаб не изменился
        
        # Сохраняем точку под мышкой неподвижной
        # Точка на карте до масштабирования
        old_map_pos = self.screen_to_map(mouse_pos)
        
        # Меняем масштаб
        self.camera_scale = new_scale
        
        # Точка на карте после масштабирования
        new_map_pos = self.screen_to_map(mouse_pos)
        
        # Двигаем камеру так, чтобы точка осталась на месте
        if old_map_pos and new_map_pos:
            delta = old_map_pos - new_map_pos
            self.camera_offset += delta

    # ============================================================================
    # ОТРИСОВКА ГЛАВНЫЙ МЕТОД
    # ============================================================================
    
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """
        Отрисовка viewport с данными из RenderStateDTO.
        
        ✅ ГЛАВНОЕ ОТЛИЧИЕ от v2:
        - v2: def draw(self, screen, font, selected_creature_id=None)
              # использует self.world и debug синглтон
        - v3dto: def draw(self, screen, render_state)
                 # использует ТОЛЬКО render_state параметр
        
        Args:
            screen: pygame.Surface для отрисовки
            render_state: RenderStateDTO со всеми данными (world, debug, params, и т.д.)
        """
        # Получаем данные из RenderStateDTO
        world_dto = render_state.world
        debug_dto = render_state.debug
        selected_creature_id = render_state.selected_creature.creature.id if render_state.selected_creature else None
        
        # Очистка viewport поверхности
        self.surface.fill(self.COLORS['bg'])
        
        # Получаем видимый диапазон карты
        min_x, max_x, min_y, max_y = self.get_visible_range(world_dto)
        
        # ============================================================
        # 1. Отрисовка клеток (стены, пищу, существ)
        # ============================================================
        self._draw_cells(world_dto, min_x, max_x, min_y, max_y, selected_creature_id)
        
        # ============================================================
        # 2. Отрисовка raycasts для отладки (из DebugDataDTO)
        # ============================================================
        if debug_dto.raycast_dots is not None:
            self._draw_raycasts(debug_dto.raycast_dots)
        
        # ============================================================
        # 3. Отрисовка рамки вокруг выбранного существа
        # ============================================================
        if selected_creature_id is not None:
            selected_creature = world_dto.get_creature_by_id(selected_creature_id)
            if selected_creature:
                self._draw_selection_frame(selected_creature)
        
        # ============================================================
        # 4. Блит viewport на экран
        # ============================================================
        screen.blit(self.surface, self.rect)
        
        # Рамка вокруг viewport
        pygame.draw.rect(screen, self.COLORS['border'], self.rect, 2)
        
        # ============================================================
        # 5. Отладочная информация
        # ============================================================
        self._draw_debug_info(screen, world_dto, render_state.tick)

    def _draw_cells(self, world_dto: WorldStateDTO, min_x: int, max_x: int, 
                    min_y: int, max_y: int, selected_creature_id: Optional[int]) -> None:
        """
        Отрисовка клеток карты (стены, пищу, существ).
        
        ✅ Используем WorldStateDTO вместо self.world
        """
        CELL_SIZE = self.camera_scale
        
        # ✅ Используем world_dto.map вместо self.world.map
        map_data = world_dto.map
        
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                cell_value = int(map_data[y, x])
                
                if cell_value == 0:  # Пусто
                    continue
                
                # Преобразуем координаты карты в viewport координаты
                viewport_pos = self.map_to_viewport(pygame.Vector2(x, y))
                rect = pygame.Rect(viewport_pos.x, viewport_pos.y, CELL_SIZE, CELL_SIZE)
                
                if cell_value == 1:  # Стена
                    pygame.draw.rect(self.surface, self.COLORS['wall'], rect)
                
                elif cell_value == 2:  # Пища
                    pygame.draw.circle(self.surface, self.COLORS['food'], 
                                     (int(rect.centerx), int(rect.centery)), 
                                     max(2, int(CELL_SIZE / 3)))
                
                elif cell_value == 3:  # Существо
                    pygame.draw.rect(self.surface, self.COLORS['creature'], rect)
    
    def _draw_raycasts(self, raycast_dots: np.ndarray) -> None:
        """
        Отрисовка raycast точек для отладки.
        
        ✅ Используем raycast_dots из DebugDataDTO вместо debug синглтона
        """
        if raycast_dots is None or len(raycast_dots) == 0:
            return
        
        for dot in raycast_dots:
            if len(dot) >= 2:
                x, y = dot[0], dot[1]
                viewport_pos = self.map_to_viewport(pygame.Vector2(x, y))
                
                pygame.draw.circle(self.surface, self.COLORS['raycast_dot'],
                                 (int(viewport_pos.x), int(viewport_pos.y)), 2)
    
    def _draw_selection_frame(self, creature_dto: CreatureDTO) -> None:
        """Отрисовка рамки вокруг выбранного существа."""
        viewport_pos = self.map_to_viewport(pygame.Vector2(creature_dto.x, creature_dto.y))
        
        # Рамка с некоторым отступом
        frame_size = self.camera_scale * 1.5
        rect = pygame.Rect(
            viewport_pos.x - frame_size/2,
            viewport_pos.y - frame_size/2,
            frame_size,
            frame_size
        )
        
        pygame.draw.rect(self.surface, self.COLORS['creature_selected'], rect, 2)
    
    def _draw_debug_info(self, screen: pygame.Surface, world_dto: WorldStateDTO, tick: int) -> None:
        """Отрисовка отладочной информации."""
        info = [
            f"Scale: {self.camera_scale:.1f}",
            f"Offset: ({self.camera_offset.x:.1f}, {self.camera_offset.y:.1f})",
            f"Visible: {int(self.rect.width / self.camera_scale)} x {int(self.rect.height / self.camera_scale)}",
            f"Population: {len(world_dto.creatures)}",
            f"Food: {len(world_dto.foods)}",
            f"Tick: {tick}",
        ]
        
        for i, text in enumerate(info):
            surface = self.font.render(text, True, self.COLORS['text'])
            screen.blit(surface, (self.rect.right + 10, self.rect.y + i * 20))

    # ============================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ============================================================================
    
    def get_creature_at_position(self, screen_pos: tuple, render_state: RenderStateDTO) -> Optional[int]:
        """
        Найти ID существа в позиции экрана.
        
        ✅ Используем WorldStateDTO вместо self.world
        
        Args:
            screen_pos: (x, y) координаты экрана
            render_state: RenderStateDTO
            
        Returns:
            ID существа или None
        """
        map_pos = self.screen_to_map(screen_pos)
        if map_pos is None:
            return None
        
        # ✅ Используем метод из WorldStateDTO
        return render_state.world.get_creature_at_position(
            int(map_pos.x), int(map_pos.y), radius=1.0
        )
