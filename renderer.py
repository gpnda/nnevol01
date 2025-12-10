# -*- coding: utf-8 -*-

import pygame
from debugger import debug
from gui import BIOSStyleGUI


class Renderer:
    # Константы конфигурации
    SCREEN_WIDTH = 1250
    SCREEN_HEIGHT = 600
    FONT_SIZE = 16
    GUI_FONT_SIZE = 24
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    # Viewport карты
    MAP_VIEWPORT_RECT = pygame.Rect(210, 5, 700, 500)
    
    # Параметры GUI
    GUI_WIDTH = 200
    GUI_HEIGHT = 600
    GUI_X = 5
    GUI_Y = 5
    GUI_LINE_HEIGHT = 20
    
    # Параметры камеры (по умолчанию)
    CAMERA_OFFSET_DEFAULT = pygame.Vector2(0, -6.0)
    CAMERA_SCALE_DEFAULT = 8.0
    CAMERA_SCALE_MIN = 7.0
    CAMERA_SCALE_MAX = 50.0
    
    # Цвета
    COLORS = {
        'background': (0, 0, 0),
        'viewport_bg': (10, 10, 10),
        'wall': (50, 50, 50),
        'food': (219, 80, 74),
        'creature': (50, 50, 255),
        'raycast_dot': (100, 100, 100),
        'viewport_border': (5, 41, 158),
        'text': (200, 200, 200),
    }

    def __init__(self, world, app):
        self.world = world
        self.app = app
        
        # Инициализация PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        self.clock = pygame.time.Clock()
        
        # Инициализация viewport
        self._init_viewport()
        
        # Инициализация GUI
        self._init_gui()

    def _init_viewport(self) -> None:
        """Инициализация viewport для карты"""
        self.map_viewport = self.MAP_VIEWPORT_RECT.copy()
        self.viewport_surface = pygame.Surface((self.map_viewport.width, self.map_viewport.height))
        
        # Параметры камеры
        self.camera_offset = self.CAMERA_OFFSET_DEFAULT.copy()
        self.camera_scale = self.CAMERA_SCALE_DEFAULT
        
        # Переменные для перемещения карты
        self.is_dragging = False
        self.drag_start_pos = pygame.Vector2(0, 0)
        self.drag_start_offset = pygame.Vector2(0, 0)

    def _init_gui(self) -> None:
        """Инициализация GUI с переменными"""
        self.gui_surface = pygame.Surface((self.GUI_WIDTH, self.GUI_HEIGHT))
        self.gui = BIOSStyleGUI(self.gui_surface, self.GUI_FONT_SIZE, self.GUI_LINE_HEIGHT)
        
        # Добавление переменных для отображения
        self.gui.add_variable("Speed", 50, min_val=0, max_val=100)
        self.gui.add_variable("Power", 75.5, float, 0.0, 100.0)
        self.gui.add_variable("Temperature", 25, min_val=-20, max_val=50)
        self.gui.add_variable("State", "Активно", str)
        self.gui.add_variable("Mode", 1, min_val=1, max_val=5)
        self.gui.add_variable("Timeout", 30, min_val=1, max_val=300)

        self.gui.add_function_key("F1", "Save", lambda: print("save_settings..."))
        self.gui.add_function_key("F2", "Load", lambda: print("Загрузка..."))
        self.gui.add_function_key("F3", "Reset", lambda: print("reset_settings..."))
        self.gui.add_function_key("F4", "Exit", lambda: print("exit app..."))
        self.gui.add_function_key("F5", "Test", lambda: print("Тестовая функция"))
    
    def screen_to_map_pos(self, screen_pos: tuple) -> pygame.Vector2:
        """Преобразует координаты экрана в координаты карты с учетом viewport и камеры"""
        if not self.map_viewport.collidepoint(screen_pos):
            return None
        
        viewport_pos = (
            screen_pos[0] - self.map_viewport.x,
            screen_pos[1] - self.map_viewport.y
        )
        
        map_x = (viewport_pos[0] / self.camera_scale) + self.camera_offset.x
        map_y = (viewport_pos[1] / self.camera_scale) + self.camera_offset.y
        
        return pygame.Vector2(map_x, map_y)
    
    def map_to_viewport_pos(self, map_pos: pygame.Vector2) -> pygame.Vector2:
        """Преобразует координаты карты в координаты относительно поверхности viewport"""
        viewport_x = (map_pos.x - self.camera_offset.x) * self.camera_scale
        viewport_y = (map_pos.y - self.camera_offset.y) * self.camera_scale
        
        return pygame.Vector2(viewport_x, viewport_y)
    
    def get_visible_cells_range(self) -> tuple:
        """Возвращает диапазон видимых клеток (min_x, max_x, min_y, max_y)"""
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
    
    def handle_mouse_events(self, event: pygame.event.Event) -> None:
        """Обрабатывает события мыши для перемещения и масштабирования карты"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self._handle_mouse_motion(event)

    def _handle_mouse_button_down(self, event: pygame.event.Event) -> None:
        """Обработка нажатия кнопки мыши"""
        if not self.map_viewport.collidepoint(event.pos):
            return
            
        if event.button == 1:  # Левая кнопка мыши
            self.is_dragging = True
            self.drag_start_pos = pygame.Vector2(event.pos)
            self.drag_start_offset = self.camera_offset.copy()
        elif event.button == 4:  # Колесико вверх (zoom in)
            self.zoom_at_point(event.pos, 1.2)
        elif event.button == 5:  # Колесико вниз (zoom out)
            self.zoom_at_point(event.pos, 0.8)

    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Обработка движения мыши"""
        delta_x = (self.drag_start_pos.x - event.pos[0]) / self.camera_scale
        delta_y = (self.drag_start_pos.y - event.pos[1]) / self.camera_scale
        
        self.camera_offset.x = self.drag_start_offset.x + delta_x
        self.camera_offset.y = self.drag_start_offset.y + delta_y
    
    def zoom_at_point(self, screen_point: tuple, zoom_factor: float) -> None:
        """Масштабирует карту относительно точки на экране"""
        map_pos_before = self.screen_to_map_pos(screen_point)
        if map_pos_before is None:
            return
        
        # Применяем масштабирование с ограничениями
        new_scale = self.camera_scale * zoom_factor
        self.camera_scale = max(self.CAMERA_SCALE_MIN, min(self.CAMERA_SCALE_MAX, new_scale))
        
        # Корректируем смещение камеры, чтобы точка осталась на месте
        map_pos_after = self.screen_to_map_pos(screen_point)
        if map_pos_after is None:
            return
        
        delta = map_pos_after - map_pos_before
        self.camera_offset -= delta
    
    def _draw_cells(self, min_x: int, max_x: int, min_y: int, max_y: int) -> None:
        """Отрисовка видимых клеток карты"""
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                cell_value = self.world.get_cell(x, y)
                if cell_value == 0:
                    continue
                
                viewport_pos = self.map_to_viewport_pos(pygame.Vector2(x, y))
                cell_size = max(1, int(self.camera_scale))
                
                rect = pygame.Rect(
                    int(viewport_pos.x),
                    int(viewport_pos.y),
                    cell_size,
                    cell_size
                )
                
                # Проверяем видимость и отрисовываем
                if self._is_rect_visible(rect):
                    color = self._get_cell_color(cell_value)
                    pygame.draw.rect(self.viewport_surface, color, rect, 0)

    def _is_rect_visible(self, rect: pygame.Rect) -> bool:
        """Проверяет, видна ли область в viewport"""
        return (rect.right > 0 and rect.left < self.map_viewport.width and
                rect.bottom > 0 and rect.top < self.map_viewport.height)

    def _get_cell_color(self, cell_value: int) -> tuple:
        """Возвращает цвет для типа клетки"""
        color_map = {
            1: self.COLORS['wall'],
            2: self.COLORS['food'],
            3: self.COLORS['creature'],
        }
        return color_map.get(cell_value, (0, 0, 0))

    def _draw_raycast_dots(self) -> None:
        """Отрисовка точек raycasting"""
        raycast_dots = debug.get("raycast_dots")
        if raycast_dots is None:
            return
            
        for dot in raycast_dots:
            viewport_pos = self.map_to_viewport_pos(pygame.Vector2(dot[0], dot[1]))
            
            if (0 <= viewport_pos.x < self.map_viewport.width and 
                0 <= viewport_pos.y < self.map_viewport.height):
                self.viewport_surface.set_at(
                    (int(viewport_pos.x), int(viewport_pos.y)), 
                    self.COLORS['raycast_dot']
                )

    def _draw_viewport_info(self, min_x: int, max_x: int, min_y: int, max_y: int) -> None:
        """Отрисовка информации о камере и видимых клетках"""
        info_text = [
            f"Scale: {self.camera_scale:.2f}",
            f"Offset: ({self.camera_offset.x:.1f}, {self.camera_offset.y:.1f})",
            f"Visible cells: {max_x-min_x}x{max_y-min_y}"
        ]
        
        y_offset = self.map_viewport.y + 10
        x_offset = self.map_viewport.x + 5
        for text in info_text:
            info_surface = self.font.render(text, True, self.COLORS['text'])
            self.screen.blit(info_surface, (x_offset, y_offset))
            y_offset += 15
    
    def draw_map(self) -> None:
        """Основной метод отрисовки карты"""
        self.viewport_surface.fill(self.COLORS['viewport_bg'])
        
        min_x, max_x, min_y, max_y = self.get_visible_cells_range()
        
        self._draw_cells(min_x, max_x, min_y, max_y)
        self._draw_raycast_dots()
        
        self.screen.blit(self.viewport_surface, (self.map_viewport.x, self.map_viewport.y))
        pygame.draw.rect(self.screen, self.COLORS['viewport_border'], self.map_viewport, 2)
        
        self._draw_viewport_info(min_x, max_x, min_y, max_y)
        
    
    def draw_gui(self) -> None:
        """Отрисовка GUI"""
        self.gui.draw()
        self.screen.blit(self.gui_surface, (self.GUI_X, self.GUI_Y))
    
    def draw(self) -> None:
        """Основной метод отрисовки всего"""
        self.screen.fill(self.COLORS['background'])
        self.draw_gui()
        self.draw_map()
        pygame.display.flip()
    
    def _handle_keyboard_events(self, event: pygame.event.Event) -> bool:
        """Обработка клавиатурных событий, возвращает True если нужно выйти"""
        if event.key == pygame.K_SPACE:
            self.app.toggle_run()
        elif event.key == pygame.K_a:
            self.app.toggle_animate()
        elif event.key == pygame.K_r:
            self._reset_camera()
        else:
            self.gui.handle_event(event)
        return False

    def _reset_camera(self) -> None:
        """Сброс параметров камеры"""
        self.camera_offset = self.CAMERA_OFFSET_DEFAULT.copy()
        self.camera_scale = self.CAMERA_SCALE_DEFAULT
    
    def control_run(self) -> bool:
        """Обрабатывает события, возвращает True если нужно выйти"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.app.terminate()
                return True
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard_events(event)
            
            self.handle_mouse_events(event)
        
        return False