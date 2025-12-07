# -*- coding: utf-8 -*-

import pygame
from debugger import debug

class Renderer:
    
    def __init__(self, world, app):
        self.world = world
        self.app = app
        
        pygame.init()
        self.screen = pygame.display.set_mode((1250, 600))
        self.font = pygame.font.SysFont('Arial', 12)
        self.clock = pygame.time.Clock()
        
        # Настройки viewport для карты
        self.map_viewport = pygame.Rect(200, 50, 800, 500)  # Позиция и размеры viewport
        
        # Создаем отдельную поверхность для viewport
        self.viewport_surface = pygame.Surface((self.map_viewport.width, self.map_viewport.height))
        
        # Параметры камеры для перемещения и масштабирования
        self.camera_offset = pygame.Vector2(0, -6.0)  # Смещение карты
        self.camera_scale = 8.0  # Масштаб карты
        self.min_scale = 7.0  # Минимальный масштаб
        self.max_scale = 50.0  # Максимальный масштаб
        
        # Переменные для перемещения карты
        self.is_dragging = False
        self.drag_start_pos = pygame.Vector2(0, 0)
        self.drag_start_offset = pygame.Vector2(0, 0)
    
    def screen_to_map_pos(self, screen_pos):
        """Преобразует координаты экрана в координаты карты с учетом viewport и камеры"""
        if not self.map_viewport.collidepoint(screen_pos):
            return None
        
        # Координаты относительно viewport
        viewport_pos = (
            screen_pos[0] - self.map_viewport.x,
            screen_pos[1] - self.map_viewport.y
        )
        
        # Координаты на карте с учетом масштаба и смещения
        map_x = (viewport_pos[0] / self.camera_scale) + self.camera_offset.x
        map_y = (viewport_pos[1] / self.camera_scale) + self.camera_offset.y
        
        return pygame.Vector2(map_x, map_y)
    
    def map_to_viewport_pos(self, map_pos):
        """Преобразует координаты карты в координаты относительно поверхности viewport"""
        # Координаты относительно карты с учетом масштаба и смещения
        viewport_x = (map_pos.x - self.camera_offset.x) * self.camera_scale
        viewport_y = (map_pos.y - self.camera_offset.y) * self.camera_scale
        
        return pygame.Vector2(viewport_x, viewport_y)
    
    def get_visible_cells_range(self):
        """Возвращает диапазон видимых клеток с учётом камеры"""
        # Вычисляем какие клетки видны в viewport
        min_x = int(self.camera_offset.x)
        min_y = int(self.camera_offset.y)
        max_x = int(self.camera_offset.x + self.map_viewport.width / self.camera_scale) + 1
        max_y = int(self.camera_offset.y + self.map_viewport.height / self.camera_scale) + 1
        
        # Ограничиваем диапазон размерами мира
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(self.world.width, max_x)
        max_y = min(self.world.height, max_y)
        
        return min_x, max_x, min_y, max_y
    
    def handle_mouse_events(self, event):
        """Обрабатывает события мыши для перемещения и масштабирования карты"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                if self.map_viewport.collidepoint(event.pos):
                    self.is_dragging = True
                    self.drag_start_pos = pygame.Vector2(event.pos)
                    self.drag_start_offset = self.camera_offset.copy()
                    
            elif event.button == 4:  # Колесико вверх (zoom in)
                if self.map_viewport.collidepoint(event.pos):
                    self.zoom_at_point(event.pos, 1.2)
                    
            elif event.button == 5:  # Колесико вниз (zoom out)
                if self.map_viewport.collidepoint(event.pos):
                    self.zoom_at_point(event.pos, 0.8)
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Левая кнопка мыши
                self.is_dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Вычисляем смещение в координатах карты
                delta_x = (self.drag_start_pos.x - event.pos[0]) / self.camera_scale
                delta_y = (self.drag_start_pos.y - event.pos[1]) / self.camera_scale
                
                # Обновляем смещение камеры
                self.camera_offset.x = self.drag_start_offset.x + delta_x
                self.camera_offset.y = self.drag_start_offset.y + delta_y
    
    def zoom_at_point(self, screen_point, zoom_factor):
        """Масштабирует карту относительно точки на экране"""
        # Получаем позицию точки в координатах карты до масштабирования
        map_pos_before = self.screen_to_map_pos(screen_point)
        if map_pos_before is None:
            return
        
        # Применяем масштабирование
        new_scale = self.camera_scale * zoom_factor
        self.camera_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        # Получаем позицию точки в координатах карты после масштабирования
        map_pos_after = self.screen_to_map_pos(screen_point)
        if map_pos_after is None:
            return
        
        # Корректируем смещение камеры, чтобы точка осталась на месте
        delta = map_pos_after - map_pos_before
        self.camera_offset -= delta
    
    def draw_map(self):
        """Основной метод отрисовки карты и raycast точек"""
        # Заливаем экран черным
        self.screen.fill((0, 0, 0))
        
        # Заливаем поверхность viewport серым цветом (фон)
        self.viewport_surface.fill((10, 10, 10))
        
        # Вычисляем диапазон видимых клеток для оптимизации отрисовки
        min_x, max_x, min_y, max_y = self.get_visible_cells_range()
        
        # Отрисовка видимых клеток карты на поверхности viewport
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                cell_value = self.world.get_cell(x, y)
                if cell_value == 0:
                    continue
                
                # Преобразуем координаты карты в координаты относительно viewport
                viewport_pos = self.map_to_viewport_pos(pygame.Vector2(x, y))
                
                # Вычисляем размер клетки с учётом масштаба
                cell_size = max(1, int(self.camera_scale))
                
                # Создаём прямоугольник для клетки
                rect = pygame.Rect(
                    int(viewport_pos.x),
                    int(viewport_pos.y),
                    cell_size,
                    cell_size
                )
                
                # Проверяем, находится ли прямоугольник хотя бы частично в пределах viewport
                if (rect.right > 0 and rect.left < self.map_viewport.width and
                    rect.bottom > 0 and rect.top < self.map_viewport.height):
                    
                    # Выбираем цвет в зависимости от типа клетки
                    if cell_value == 1:
                        color = (50, 50, 50)
                        pygame.draw.rect(self.viewport_surface, color, rect, 0)
                    elif cell_value == 2:
                        color = (255, 50, 50)
                        pygame.draw.rect(self.viewport_surface, color, rect, 0)
                    elif cell_value == 3:
                        color = (50, 50, 255)
                        pygame.draw.rect(self.viewport_surface, color, rect, 0)
        
        # Отрисовка raycast_dots на поверхности viewport (всегда 1 пиксель независимо от зума)
        raycast_dots = debug.get("raycast_dots")
        for dot in raycast_dots:
            # Преобразуем координаты карты в координаты относительно viewport
            viewport_pos = self.map_to_viewport_pos(pygame.Vector2(dot[0], dot[1]))
            
            # Проверяем, находится ли точка внутри границ viewport
            if (0 <= viewport_pos.x < self.map_viewport.width and 
                0 <= viewport_pos.y < self.map_viewport.height):
                
                # Всегда рисуем точку размером 1 пиксель
                self.viewport_surface.set_at(
                    (int(viewport_pos.x), int(viewport_pos.y)), 
                    (100, 100, 100)
                )
        
        # Выводим поверхность viewport на экран
        self.screen.blit(self.viewport_surface, (self.map_viewport.x, self.map_viewport.y))
        
        # Рисуем рамку вокруг viewport
        pygame.draw.rect(self.screen, (100, 100, 100), self.map_viewport, 2)
        
        # Отображаем информацию о камере и видимых клетках
        info_text = [
            f"Scale: {self.camera_scale:.2f}",
            f"Offset: ({self.camera_offset.x:.1f}, {self.camera_offset.y:.1f})",
            f"Visible cells: {max_x-min_x}x{max_y-min_y}"
        ]
        
        y_offset = self.map_viewport.y - 25
        for i, text in enumerate(info_text):
            info_surface = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(info_surface, (self.map_viewport.x, y_offset))
            y_offset += 15
        
        # Обновляем экран
        pygame.display.flip()
    
    def control_run(self):
        """Обрабатывает события"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.app.terminate()
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Space key pressed!")
                    self.app.toggle_run()
                elif event.key == pygame.K_a:
                    print("A key pressed!")
                    self.app.toggle_animate()
                elif event.key == pygame.K_r:
                    print("R key pressed - resetting view")
                    # Сброс камеры
                    self.camera_offset = pygame.Vector2(0, 0)
                    self.camera_scale = 1.0
            
            # Обработка событий мыши для управления картой
            self.handle_mouse_events(event)
        
        return False