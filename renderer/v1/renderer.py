# -*- coding: utf-8 -*-
"""
Главный класс для отрисовки симуляции эволюции.

Renderer управляет:
- Окном pygame
- Обработкой клавиатуры (Space для toggle_run, A для toggle_animate)
- Координацией отрисовки различных компонентов (Viewport и в будущем GUI компоненты)
"""

import pygame
from typing import Callable, Optional, Any
from renderer.v1.gui_viewport import Viewport
from renderer.v1.gui_variablespanel import VariablesPanel
from renderer.v1.gui_functionalkeys import FunctionKeysPanel
from renderer.v1.gui_creatures_popup import CreaturesPopup


class Renderer:
    """Управляет отрисовкой всей симуляции и обработкой событий."""
    
    # Параметры экрана
    SCREEN_WIDTH = 1250
    SCREEN_HEIGHT = 600
    
    # Цвета базовые
    COLORS = {
        'background': (0, 0, 0),
        'text': (200, 200, 200),
    }
    
    # Шрифт для отладочной информации
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'

    def __init__(self, world, app):
        """
        Инициализация Renderer.
        
        Args:
            world: Объект World с картой симуляции
            app: Объект Application для управления состоянием
        """
        self.world = world
        self.app = app
        
        # Инициализация PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Evolutionary Simulation")
        
        # Инициализация шрифта
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            # Fallback на системный шрифт если файл не найден
            self.font = pygame.font.Font(None, self.FONT_SIZE)
        
        # Инициализация компонентов визуализации
        self.viewport = Viewport(world=self.world)
        self.variables_panel = VariablesPanel(world=self.world)
        self.func_keys_panel = FunctionKeysPanel(app=self.app)
        self.creatures_popup = CreaturesPopup(world=self.world)
        
        # Часы для управления FPS
        self.clock = pygame.time.Clock()

    def _handle_keyboard(self, event: pygame.event.Event) -> bool:
        """
        Обработка клавиатурных событий.
        
        Args:
            event: pygame.event.Event клавиатурного события
            
        Returns:
            True если надо выходить из приложения
        """
        # Обработка popup окна (имеет приоритет)
        if self.creatures_popup.handle_event(event):
            return False
        
        # Сначала проверяем функциональные клавиши
        if self.func_keys_panel.handle_event(event):
            return False
        
        # Затем пытаемся обработать в VariablesPanel
        if self.variables_panel.handle_event(event):
            return False
        
        # Затем обработка глобальных команд Renderer
        if event.key == pygame.K_SPACE:
            # Space: включить/выключить симуляцию
            self.app.toggle_run()
        
        elif event.key == pygame.K_a:
            # A: включить/выключить анимацию (отрисовку)
            self.app.toggle_animate()
        
        
        return False

    def _handle_mouse(self, event: pygame.event.Event) -> None:
        """Обработка событий мыши."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.viewport.handle_mouse_down(event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.viewport.handle_mouse_up(event)
        
        elif event.type == pygame.MOUSEMOTION:
            self.viewport.handle_mouse_motion(event)

    def control_run(self) -> bool:
        """
        Основная функция обработки событий.
        
        Returns:
            True если надо выходить из приложения
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.app.terminate()
                return True
            
            elif event.type == pygame.KEYDOWN:
                if self._handle_keyboard(event):
                    return True
            
            # Обработка мыши
            self._handle_mouse(event)
        
        return False

    def draw(self) -> None:
        """Отрисовка всех компонентов."""
        # Очистка экрана
        self.screen.fill(self.COLORS['background'])
        
        # Отрисовка viewport карты
        self.viewport.draw(self.screen, self.font)
        
        # Отрисовка панели переменных
        self.variables_panel.draw(self.screen)
        
        # Отрисовка панели функциональных клавиш
        self.func_keys_panel.draw(self.screen)
        
        # Отрисовка popup окна со списком существ (в последнюю очередь, чтобы было сверху)
        self.creatures_popup.draw(self.screen)
        
        # Обновление дисплея
        pygame.display.flip()
        
        # Ограничение FPS (опционально раскомментировать)
        # self.clock.tick(60)

