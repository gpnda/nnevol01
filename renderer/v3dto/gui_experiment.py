# -*- coding: utf-8 -*-
"""
ExperimentModal - v3dto версия.

Модальное окно экспериментов.
Начальная версия: отображает информацию о выбранном существе.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
- Может быть открыто и закрыто через state machine Renderer'а
"""

import pygame
from typing import TYPE_CHECKING, Callable, Optional, Any

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class ExperimentModal:
    """
    Модальное окно для экспериментов.
    
    Начальная версия отображает информацию о выбранном существе (ID).
    
    Архитектура DTO:
    - Получает RenderStateDTO в методе draw()
    - Получает selected_creature_id из reset(selected_creature_id)
    - Полностью изолирована от синглтонов
    - Использует callback паттерн для управления экспериментами (как VariablesPanel)
    
    Callbacks:
    - on_start_experiment(duration): Запустить эксперимент
    - on_stop_experiment(): Остановить эксперимент
    """
    
    # Геометрия окна (центрировано на экране)
    POPUP_WIDTH = 500
    POPUP_HEIGHT = 300
    
    # Параметры отображения
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    TITLE_HEIGHT = 30
    CONTENT_PADDING = 20
    LINE_HEIGHT = 25
    
    # Цвета в стиле BIOS
    COLORS = {
        'bg': (5, 41, 158),           # Синий фон
        'border': (170, 170, 170),    # Серая граница
        'title_bg': (0, 167, 225),    # Голубой заголовок
        'title_text': (0, 0, 0),      # Чёрный текст в заголовке
        'text': (170, 170, 170),      # Серый текст
        'label': (255, 255, 255),     # Белый для меток
        'value': (0, 255, 100),       # Зелёный для значений
    }
    
    def __init__(self, 
                 on_start_experiment: Optional[Callable[[int], None]] = None,
                 on_stop_experiment: Optional[Callable[[], None]] = None):
        """
        Инициализация модального окна экспериментов.
        
        Args:
            on_start_experiment: Callback для запуска эксперимента (duration_ticks)
            on_stop_experiment: Callback для остановки эксперимента
        """
        # Callbacks для управления экспериментом
        self.on_start_experiment = on_start_experiment or (lambda x: None)
        self.on_stop_experiment = on_stop_experiment or (lambda: None)
        
        # Инициализация шрифтов
        try:
            self.font_title = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE + 2)
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
            self.font_small = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE - 2)
        except (FileNotFoundError, pygame.error):
            self.font_title = pygame.font.Font(None, self.FONT_SIZE + 2)
            self.font = pygame.font.Font(None, self.FONT_SIZE)
            self.font_small = pygame.font.Font(None, self.FONT_SIZE - 2)
        
        # Позиция и размер окна (будут вычислены при первом draw)
        self.selected_creature_id = None
        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, self.POPUP_WIDTH, self.POPUP_HEIGHT)
        
        # Состояние эксперимента (для отображения)
        self.experiment_running = False
        self.default_duration = 500
    
    def reset(self, selected_creature_id: int) -> None:
        """Сбросить состояние (вызывается при открытии модала)."""
        self.selected_creature_id = selected_creature_id
        self.experiment_running = False
        return
    
    def start_experiment(self, duration: int = 500) -> None:
        """
        Запустить эксперимент через callback.
        
        Args:
            duration: Количество тиков для эксперимента
        """
        self.on_start_experiment(duration)
        self.experiment_running = True
    
    def stop_experiment(self) -> None:
        """Остановить эксперимент через callback."""
        self.on_stop_experiment()
        self.experiment_running = False
    
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """
        Обработка клавиш в окне эксперимента.
        
        Args:
            event: Pygame event KEYDOWN
        
        Returns:
            True если событие обработано, False иначе
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # S - Start experiment
        if event.key == pygame.K_s:
            self.start_experiment(self.default_duration)
            print(f"[ExperimentModal] Эксперимент запущен на {self.default_duration} тиков")
            return True
        
        # X - Stop experiment
        elif event.key == pygame.K_x:
            if self.experiment_running:
                self.stop_experiment()
                print("[ExperimentModal] Эксперимент остановлен")
            return True
        
        return False
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка модального окна экспериментов.
        
        Args:
            screen: Pygame surface для отрисовки
            render_state: RenderStateDTO с данными о выбранном существе
        """
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
            "Experiment Window", 
            True, 
            self.COLORS['title_text']
        )
        title_x = self.x + self.CONTENT_PADDING
        title_y = self.y + (self.TITLE_HEIGHT - title_text.get_height()) // 2
        screen.blit(title_text, (title_x, title_y))
        
        # Контент окна
        content_y = self.y + self.TITLE_HEIGHT + self.CONTENT_PADDING
        content_x = self.x + self.CONTENT_PADDING
        
        if self.selected_creature_id is None:
            # Нет выбранного существа
            msg = self.font.render("No creature selected", True, self.COLORS['text'])
            screen.blit(msg, (content_x, content_y))
        else:
            # Отрисовка информации о выбранном существе
            lines = [
                f"Selected Creature ID:",
                f"  {self.selected_creature_id}",
                f"",
                f"Experiment Status: {'RUNNING' if self.experiment_running else 'IDLE'}",
            ]
            
            # Добавить информацию о тиках если эксперимент активен
            if render_state.experiment_result is not None:
                exp = render_state.experiment_result
                lines.extend([
                    f"Progress: {exp.current_tick} / {exp.total_ticks} ticks ({exp.progress_percent:.1f}%)",
                    f"Energy: {exp.current_energy:.2f}",
                ])
            else:
                lines.append(f"Duration: {self.default_duration} ticks")
            
            lines.extend([
                f"",
                f"Controls:",
                f"  S - Start experiment",
                f"  X - Stop experiment",
            ])
            
            for line in lines:
                if line.startswith("  "):
                    # Значение - зелёный цвет
                    text_surface = self.font.render(line, True, self.COLORS['value'])
                elif line.startswith("Experiment Status"):
                    # Статус - разные цвета в зависимости от состояния
                    color = self.COLORS['value'] if self.experiment_running else self.COLORS['text']
                    text_surface = self.font.render(line, True, color)
                else:
                    # Метка - белый цвет
                    text_surface = self.font.render(line, True, self.COLORS['label'])
                
                screen.blit(text_surface, (content_x, content_y))
                content_y += self.LINE_HEIGHT
        
        # Отрисовка подсказки внизу
        help_text = "F2 or ESC: close"
        help_surface = self.font_small.render(help_text, True, self.COLORS['text'])
        help_x = self.x + (self.POPUP_WIDTH - help_surface.get_width()) // 2
        help_y = self.y + self.POPUP_HEIGHT - self.CONTENT_PADDING - help_surface.get_height()
        screen.blit(help_surface, (help_x, help_y))
