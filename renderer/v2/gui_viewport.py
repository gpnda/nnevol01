# -*- coding: utf-8 -*-
"""
Viewport для отрисовки карты мира с поддержкой панорамирования и масштабирования.
Адаптирован для Renderer v2 (система состояний).
"""

import pygame
from service.debugger.debugger import debug


class Viewport:
    """Управляет просмотром и отрисовкой карты с камерой."""
    
    # Расположение viewport на экране (пиксели)
    # Расширено на всю ширину для v2 архитектуры
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
        'raycast_dot': (100, 100, 100),
        'text': (200, 200, 200),
    }
    
    def __init__(self, world=None):
        """
        Инициализация viewport.
        
        Args:
            world: Объект мира с методами get_cell(x, y)
        """
        self.world = world
        
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
    
    def screen_to_map(self, screen_pos: tuple) -> pygame.Vector2 | None:
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
        
        Returns:
            pygame.Vector2 с экранными координатами
        """
        viewport_x = (map_pos.x - self.camera_offset.x) * self.camera_scale
        viewport_y = (map_pos.y - self.camera_offset.y) * self.camera_scale
        
        return pygame.Vector2(viewport_x, viewport_y)
    
    def get_visible_range(self) -> tuple:
        """
        Возвращает диапазон видимых клеток карты.
        
        Returns:
            (min_x, max_x, min_y, max_y) - границы видимой области на карте
        """
        min_x = int(self.camera_offset.x)
        min_y = int(self.camera_offset.y)
        max_x = int(self.camera_offset.x + self.rect.width / self.camera_scale) + 1
        max_y = int(self.camera_offset.y + self.rect.height / self.camera_scale) + 1
        
        # Ограничиваем размерами мира
        if self.world:
            min_x = max(0, min_x)
            min_y = max(0, min_y)
            max_x = min(self.world.width, max_x)
            max_y = min(self.world.height, max_y)
        
        return min_x, max_x, min_y, max_y
    
    def get_creature_at_position(self, screen_pos: tuple) -> any:
        """
        Получить существо в точке клика.
        
        Args:
            screen_pos: (x, y) координаты на экране
            
        Returns:
            Целочисленное значение creature.id если существо найдено, иначе None
        """
        map_pos = self.screen_to_map(screen_pos)
        if map_pos is None:
            return None
        
        x, y = int(map_pos.x), int(map_pos.y)
        
        # Проверяем есть ли существо в этой клетке
        if self.world:
            for creature in self.world.creatures:
                # Сравниваем с учётом того, что координаты могут быть float
                if int(creature.x) == x and int(creature.y) == y:
                    return creature.id
        
        return None
    
    def handle_mouse_down(self, event: pygame.event.Event) -> None:
        """Обработка нажатия кнопки мыши."""
        if not self.rect.collidepoint(event.pos):
            return
        
        if event.button == 1:  # Левая кнопка - перетаскивание
            self.is_dragging = True
            self.drag_start_pos = pygame.Vector2(event.pos)
            self.drag_start_offset = self.camera_offset.copy()
        
        elif event.button == 4:  # Колесико вверх - приближение
            self.zoom_at_point(event.pos, 1.2)
        
        elif event.button == 5:  # Колесико вниз - отдаление
            self.zoom_at_point(event.pos, 0.8)
    
    def handle_mouse_up(self, event: pygame.event.Event) -> None:
        """Обработка отпускания кнопки мыши."""
        if event.button == 1:
            self.is_dragging = False
    
    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Обработка движения мыши при перетаскивании."""
        if not self.is_dragging:
            return
        
        delta_x = (self.drag_start_pos.x - event.pos[0]) / self.camera_scale
        delta_y = (self.drag_start_pos.y - event.pos[1]) / self.camera_scale
        
        self.camera_offset.x = self.drag_start_offset.x + delta_x
        self.camera_offset.y = self.drag_start_offset.y + delta_y
    
    def zoom_at_point(self, screen_pos: tuple, zoom_factor: float) -> None:
        """
        Масштабирует карту относительно точки на экране.
        
        Args:
            screen_pos: (x, y) координаты точки на экране
            zoom_factor: коэффициент масштабирования (>1 приближение, <1 отдаление)
        """
        map_pos_before = self.screen_to_map(screen_pos)
        if map_pos_before is None:
            return
        
        # Применяем масштабирование с ограничениями
        new_scale = self.camera_scale * zoom_factor
        self.camera_scale = max(self.CAMERA_SCALE_MIN, 
                                min(self.CAMERA_SCALE_MAX, new_scale))
        
        # Корректируем смещение камеры, чтобы точка осталась на месте
        map_pos_after = self.screen_to_map(screen_pos)
        if map_pos_after is None:
            return
        
        delta = map_pos_after - map_pos_before
        self.camera_offset -= delta
    
    def reset_camera(self) -> None:
        """Сброс камеры к параметрам по умолчанию."""
        self.camera_offset = self.CAMERA_OFFSET_DEFAULT.copy()
        self.camera_scale = self.CAMERA_SCALE_DEFAULT
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий мыши для viewport.
        
        Args:
            event: pygame.event.Event
            
        Returns:
            True если событие обработано
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event)
            return False
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(event)
            return False
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
            return False
        
        return False
    
    def _draw_cells(self) -> None:
        """Отрисовка видимых клеток карты."""
        if not self.world:
            return
        
        min_x, max_x, min_y, max_y = self.get_visible_range()
        
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                cell_value = self.world.get_cell(x, y)
                if cell_value == 0:
                    continue
                
                map_pos = pygame.Vector2(x, y)
                viewport_pos = self.map_to_viewport(map_pos)
                cell_size = max(1, int(self.camera_scale))
                
                rect = pygame.Rect(int(viewport_pos.x), int(viewport_pos.y), 
                                   cell_size, cell_size)
                
                # Проверяем видимость
                if not self._is_visible(rect):
                    continue
                
                color = self._get_cell_color(cell_value)
                pygame.draw.rect(self.surface, color, rect, 0)
    
    def _is_visible(self, rect: pygame.Rect) -> bool:
        """Проверяет, видна ли область в viewport."""
        return (rect.right > 0 and rect.left < self.rect.width and
                rect.bottom > 0 and rect.top < self.rect.height)
    
    def _get_cell_color(self, cell_value: int) -> tuple:
        """Возвращает цвет для типа клетки."""
        color_map = {
            1: self.COLORS['wall'],
            2: self.COLORS['food'],
            3: self.COLORS['creature'],
        }
        return color_map.get(cell_value, (0, 0, 0))
    
    def _draw_raycast_dots(self) -> None:
        """Отрисовка точек raycasting для отладки."""
        raycast_dots = debug.get("raycast_dots")
        if raycast_dots is None:
            return
        
        for dot in raycast_dots:
            viewport_pos = self.map_to_viewport(pygame.Vector2(dot[0], dot[1]))
            
            if (0 <= viewport_pos.x < self.rect.width and
                0 <= viewport_pos.y < self.rect.height):
                self.surface.set_at(
                    (int(viewport_pos.x), int(viewport_pos.y)),
                    self.COLORS['raycast_dot']
                )
    
    def _draw_selected_creature_box(self, creature) -> None:
        """
        Отрисовка рамки и точки выбранного существа.
        
        Рисует:
        1. Рамку вокруг клетки (целочисленные координаты)
        2. Маленький квадрат 3x3 пикселя в точных координатах существа (float)
        
        Это показывает разницу между целочисленными и вещественными координатами.
        
        Args:
            creature: Объект Creature с атрибутами x, y (float)
        """
        if creature is None:
            return
        
        # ===== РАМКА ВОКРУГ ЦЕЛОЧИСЛЕННОЙ КЛЕТКИ =====
        # Преобразуем целочисленные координаты клетки
        int_x, int_y = int(creature.x), int(creature.y)
        int_pos = pygame.Vector2(int_x, int_y)
        int_viewport_pos = self.map_to_viewport(int_pos)
        
        # Проверяем видимость рамки
        if 0 <= int_viewport_pos.x < self.rect.width and 0 <= int_viewport_pos.y < self.rect.height:
            box_size = int(self.camera_scale) + 12
            box_rect = pygame.Rect(
                int(int_viewport_pos.x - 6),
                int(int_viewport_pos.y - 6),
                box_size,
                box_size
            )
            # Рисуем белую рамку толщиной 1 пиксель вокруг клетки
            # Размер угла - 1/4 от стороны квадрата
            corner_length = box_rect.width // 4

            # Левый верхний угол
            pygame.draw.line(self.surface, (255, 255, 255), 
                            (box_rect.left, box_rect.top), 
                            (box_rect.left + corner_length, box_rect.top), 3)
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.left, box_rect.top),
                            (box_rect.left, box_rect.top + corner_length), 3)

            # Правый верхний угол
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.right - corner_length, box_rect.top),
                            (box_rect.right, box_rect.top), 3)
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.right, box_rect.top),
                            (box_rect.right, box_rect.top + corner_length), 3)

            # Левый нижний угол
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.left, box_rect.bottom - corner_length),
                            (box_rect.left, box_rect.bottom), 3)
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.left, box_rect.bottom),
                            (box_rect.left + corner_length, box_rect.bottom), 3)

            # Правый нижний угол
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.right, box_rect.bottom - corner_length),
                            (box_rect.right, box_rect.bottom), 3)
            pygame.draw.line(self.surface, (255, 255, 255),
                            (box_rect.right - corner_length, box_rect.bottom),
                            (box_rect.right, box_rect.bottom), 3)
        
        # ===== КВАДРАТ 3x3 В ТОЧНЫХ КООРДИНАТАХ =====
        # Преобразуем точные координаты существа (float)
        creature_pos = pygame.Vector2(creature.x, creature.y)
        viewport_pos = self.map_to_viewport(creature_pos)
        
        # Проверяем видимость квадрата
        if 0 <= viewport_pos.x < self.rect.width and 0 <= viewport_pos.y < self.rect.height:
            # Рисуем маленький квадрат 3x3 пикселя в точных координатах
            # Центруем квадрат вокруг точки существа
            marker_rect = pygame.Rect(
                int(viewport_pos.x) - 1,
                int(viewport_pos.y) - 1,
                3,
                3
            )
            # Рисуем жёлтый квадрат (заполненный)
            pygame.draw.rect(self.surface, (255, 255, 0), marker_rect)
    
    def _draw_debug_info(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Отрисовка отладочной информации (камера, видимые клетки)."""
        min_x, max_x, min_y, max_y = self.get_visible_range()
        
        info_lines = [
            f"Scale: {self.camera_scale:.2f}",
            f"Offset: ({self.camera_offset.x:.1f}, {self.camera_offset.y:.1f})",
            f"Visible: {max_x - min_x}x{max_y - min_y}",
        ]
        
        y_offset = 5
        for line in info_lines:
            text_surf = font.render(line, True, self.COLORS['text'])
            surface.blit(text_surf, (self.rect.x + 5, self.rect.y + y_offset))
            y_offset += 15
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font = None, selected_creature_id=None) -> None:
        """
        Отрисовка viewport на экран.
        
        Args:
            screen: pygame.Surface главного экрана
            font: pygame.font.Font для отрисовки текста (опционально)
            selected_creature_id: id выбранного существа (опционально)
        """
        # Очистка поверхности viewport
        self.surface.fill(self.COLORS['bg'])
        
        # Отрисовка клеток карты
        self._draw_cells()
        
        # Отрисовка raycast точек для отладки
        self._draw_raycast_dots()
        
        # Отрисовка рамки вокруг выбранного существа
        if selected_creature_id is not None:
            selected_creature = self.world.get_creature_by_id(selected_creature_id)
            if selected_creature is not None:
                self._draw_selected_creature_box(selected_creature)
        
            
        
        # Рисуем viewport на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
        pygame.draw.rect(screen, self.COLORS['border'], self.rect, 2)
        
        # Отрисовка отладочной информации если передан шрифт
        if font:
            self._draw_debug_info(screen, font)
