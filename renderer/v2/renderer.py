# -*- coding: utf-8 -*-
"""
Renderer с системой состояний для управления несколькими экранами.

Состояния:
- 'main': Основное окно с картой (работает основной цикл)
- 'creatures_list': Список существ (пауза основного цикла)
- 'logs': Логи в полный экран (пауза основного цикла)
- 'experiment': Окно эксперимента (пауза основного цикла)
- Другие модальные окна...

Каждое состояние показывает только свои элементы и обрабатывает свои события.
"""

import pygame
from typing import Dict, Optional, Callable
from renderer.v2.gui_viewport import Viewport
from renderer.v2.gui_variablespanel import VariablesPanel
from renderer.v2.gui_selected_creature import SelectedCreaturePanel
from renderer.v2.gui_selected_creature_history import SelectedCreatureHistory
from service.logger.logger import logme


class Renderer:
    """
    Управляет отрисовкой симуляции с системой состояний.
    
    Одно состояние активно в любой момент времени.
    Каждое состояние определяет, какие виджеты отрисовываются и какие события обрабатываются.
    """
    
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
        pygame.display.set_caption("NNEvol (Khan RL Lab)")
        icon_surface = pygame.image.load('./docs/icon.png')
        pygame.display.set_icon(icon_surface)
        
        # Инициализация шрифта
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            # Fallback на системный шрифт если файл не найден
            self.font = pygame.font.Font(None, self.FONT_SIZE)
        
        # СИСТЕМА СОСТОЯНИЙ
        # Текущее активное состояние
        self.current_state = 'main'
        
        # Словарь состояний: {state_name: description}
        # Используется для валидации и отладки
        self.states = {
            'main': 'Основное окно с картой',
            'popup_simparams': 'Popup окно параметров симуляции (модальное)',
            'creatures_list': 'Список существ (модальное)',
            'logs': 'Логи в полный экран (модальное)',
            'experiment': 'Окно эксперимента (модальное)',
        }
        
        # Часы для управления FPS
        self.clock = pygame.time.Clock()
        
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        self.viewport = Viewport(world=self.world)
        self.variables_panel = VariablesPanel(world=self.world)
        self.selected_creature_panel = SelectedCreaturePanel(world=self.world)
        self.selected_creature_history = SelectedCreatureHistory(world=self.world)
        
        # ВЫБОР СУЩЕСТВА
        self.selected_creature_id = None
        
        
        # TODO: Добавить остальные виджеты
        # self.func_keys_panel = FunctionKeysPanel(app=self.app)
        # ... и т.д.

    # ============================================================================
    # УПРАВЛЕНИЕ СОСТОЯНИЯМИ
    # ============================================================================
    
    def set_state(self, state_name: str) -> bool:
        """
        Переключиться на новое состояние.
        
        Args:
            state_name: Название состояния (ключ из self.states)
            
        Returns:
            True если переключение успешно, False если состояние не найдено
        """
        if state_name not in self.states:
            print(f"⚠️ Неизвестное состояние: {state_name}")
            return False
        
        if self.current_state != state_name:
            print(f"State transition: {self.current_state} → {state_name}")
            self.current_state = state_name
            
            # Управление паузой: модальные окна ставят симуляцию на паузу
            if state_name != 'main':
                # Переход в модальное окно - пауза и очистка выбора
                self.app.is_running = False
                self.selected_creature_id = None  # Очищаем выбор при открытии popup
            else:
                self.app.is_running = True
            
            self._on_state_enter(state_name)
        
        return True
    
    def get_state(self) -> str:
        """Получить текущее состояние."""
        return self.current_state
    
    def is_main_state(self) -> bool:
        """Проверить, находимся ли в основном состоянии (работает игровой цикл)."""
        return self.current_state == 'main'
    
    def is_modal_state(self) -> bool:
        """Проверить, находимся ли в модальном окне (пауза игрового цикла)."""
        return self.current_state != 'main'
    
    def _on_state_enter(self, state_name: str) -> None:
        """
        Вызывается при входе в новое состояние.
        
        Пауза управляется в set_state(), здесь можно добавить 
        инициализацию для конкретного состояния (например, инициализировать данные окна).
        
        Args:
            state_name: Название нового состояния
        """
        # Примеры для будущего использования:
        # if state_name == 'creatures_list':
        #     self.creatures_popup.refresh_data()
        # elif state_name == 'experiment':
        #     self.experiment_modal.initialize()
        pass
    
    # ============================================================================
    # ОБРАБОТКА СОБЫТИЙ
    # ============================================================================

    def _handle_keyboard(self, event: pygame.event.Event) -> bool:
        """
        Обработка клавиатурных событий.
        
        События маршрутизируются в зависимости от текущего состояния.
        
        Args:
            event: pygame.event.Event клавиатурного события
            
        Returns:
            True если надо выходить из приложения
        """
        # ОСНОВНОЕ СОСТОЯНИЕ
        if self.current_state == 'main':
            return self._handle_keyboard_main(event)
        
        # POPUP ПАРАМЕТРОВ СИМУЛЯЦИИ
        elif self.current_state == 'popup_simparams':
            return self._handle_keyboard_popup_simparams(event)
        
        # СПИСОК СУЩЕСТВ
        elif self.current_state == 'creatures_list':
            return self._handle_keyboard_creatures_list(event)
        
        # ЛОГИ
        elif self.current_state == 'logs':
            return self._handle_keyboard_logs(event)
        
        # ЭКСПЕРИМЕНТ
        elif self.current_state == 'experiment':
            return self._handle_keyboard_experiment(event)
        
        return False
    
    def _handle_keyboard_main(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий в основном состоянии.
        
        Здесь обрабатываются события для всех постоянных виджетов:
        - Viewport (пан/зум)
        - VariablesPanel (редактирование переменных)
        - FunctionKeysPanel (функциональные клавиши)
        
        И глобальные команды:
        - Space: пауза/возобновление
        - A: вкл/выкл отрисовку
        - F1: открыть список существ
        - F12: открыть логи
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Функциональные клавиши - открытие модальных окон
        if event.key == pygame.K_F1:
            # Открыть список существ
            self.set_state('creatures_list')
            return False
        
        elif event.key == pygame.K_F9:
            # Открыть/закрыть параметры симуляции
            self.set_state('popup_simparams')
            return False
        
        elif event.key == pygame.K_F7:
            print("F7 F7 F7 F7 F7 F7 F7 F7 F7 F7 F7 F7 F7 F7 ")
            print(logme.get_creature_energy_history(1))

        
        elif event.key == pygame.K_F12:
            # Открыть логи
            self.set_state('logs')
            return False
        
        # TODO: Добавить обработку событий для постоянных виджетов
        # if self.variables_panel.handle_event(event):
        #     return False
        # if self.func_keys_panel.handle_event(event):
        #     return False
        # if self.viewport.handle_event(event):
        #     return False
        
        # Глобальные команды
        if event.key == pygame.K_SPACE:
            # Space: включить/выключить симуляцию
            self.app.toggle_run()
            return False
        
        elif event.key == pygame.K_a:
            # A: включить/выключить анимацию (отрисовку)
            self.app.toggle_animate()
            return False
        
        return False
    
    def _handle_keyboard_popup_simparams(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий в окне параметров симуляции.
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Закрытие по Escape или F9
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F9:
            self.set_state('main')
            return True
        
        # Обработка событий для VariablesPanel
        if self.variables_panel.handle_event(event):
            return True
        
        return False
    
    def _handle_keyboard_creatures_list(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий в окне списка существ.
        
        TODO: Будет реализовано при добавлении виджета CreaturesPopup
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Закрытие по Escape или F1
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1:
            self.set_state('main')
            return True
        elif event.key == pygame.K_F7:
            print("Тестовое событие F7 в окне списка существ")

        
        # TODO: Добавить обработку событий для CreaturesPopup
        # if self.creatures_popup.handle_event(event):
        #     return True
        
        return False
    
    def _handle_keyboard_logs(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий в окне логов.
        
        TODO: Будет реализовано при добавлении виджета LogsPopup
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Закрытие по Escape или F12
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F12:
            self.set_state('main')
            return True
        
        # TODO: Добавить обработку событий для LogsPopup
        # if self.logs_popup.handle_event(event):
        #     return True
        
        return False
    
    def _handle_keyboard_experiment(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий в окне эксперимента.
        
        TODO: Будет реализовано при добавлении виджета ExperimentModal
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        # Закрытие по Escape
        if event.key == pygame.K_ESCAPE:
            self.set_state('main')
            return True
        
        # TODO: Добавить обработку событий для ExperimentModal
        # if self.experiment_modal.handle_event(event):
        #     return True
        
        return False

    def _handle_mouse(self, event: pygame.event.Event) -> None:
        """
        Обработка событий мыши.
        
        События маршрутизируются в зависимости от текущего состояния.
        """
        # Мышь обрабатывается только в основном состоянии
        # (для viewport пан/зум и выбор существа)
        if self.current_state == 'main':
            # Левая кнопка мыши - выбор существа
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                creature_id = self.viewport.get_creature_at_position(event.pos)
                if creature_id is not None:
                    selected_creature = self.world.get_creature_by_id(creature_id)
                    self.selected_creature_id = creature_id
                    # print(f"✓ Creature selected: id={creature_id} age={selected_creature.age}, pos=({int(selected_creature.x)}, {int(selected_creature.y)}), energy={selected_creature.energy:.2f}")
                    # print(f"Energy history length: {len(logme.get_creature_energy_history(creature_id))}")
                else:
                    selected_creature = None
                    self.selected_creature_id = None
                    print("✗ No creature at this position")
            
            # Остальные события мыши (пан, зум)
            self.viewport.handle_event(event)

    def control_run(self) -> bool:
        """
        Основная функция обработки событий.
        Вызывается один раз за фрейм из application.py
        
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
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                self._handle_mouse(event)
        
        return False

    # ============================================================================
    # ОТРИСОВКА
    # ============================================================================

    def draw(self) -> None:
        """
        Отрисовка всех компонентов.
        
        Отрисовываемые элементы зависят от текущего состояния.
        Вызывается один раз за фрейм из application.py (если animate_flag == True)
        """
        # Очистка экрана
        # self.screen.fill(self.COLORS['background'])
        
        # Отрисовка в зависимости от состояния
        if self.current_state == 'main':
            self._draw_main()
        elif self.current_state == 'popup_simparams':
            self._draw_popup_simparams()
        elif self.current_state == 'creatures_list':
            self._draw_creatures_list()
        elif self.current_state == 'logs':
            self._draw_logs()
        elif self.current_state == 'experiment':
            self._draw_experiment()
        
        # Обновление дисплея
        pygame.display.flip()
    
    def _draw_main(self) -> None:
        """
        Отрисовка основного состояния.
        
        Элементы:
        - Viewport (карта мира)
        - VariablesPanel (панель переменных)
        - FunctionKeysPanel (функциональные клавиши)
        - SelectedCreaturePanel (информация о выбранном существе)
        - WorldStatsPanel (статистика мира)
        """
        # Отрисовка viewport (карта мира) с рамкой вокруг выбранного существа
        self.viewport.draw(self.screen, self.font, selected_creature_id=self.selected_creature_id)
        
        # Проверка, что существо с таким id существует в мире   
        if self.selected_creature_id is not None and self.world.get_creature_by_id(self.selected_creature_id) is None:
            self.selected_creature_id = None

        if self.selected_creature_id is not None:
            # Отрисовка панели информации о выбранном существе
            self.selected_creature_panel.draw(self.screen, self.selected_creature_id)

            # Отрисовка панели информации о выбранном существе
            self.selected_creature_history.draw(self.screen, self.selected_creature_id)
            # print("Рисуем историю энергии для существа id=" + str(self.selected_creature_id))
        
        # TODO: Добавить отрисовку виджетов
        # self.variables_panel.draw(self.screen)
        # self.func_keys_panel.draw(self.screen)
        # self.world_stats_panel.draw(self.screen)
    
    def _draw_popup_simparams(self) -> None:
        """
        Отрисовка окна параметров симуляции.
        
        Элементы:
        - VariablesPanel (панель редактирования переменных симуляции)
        """
        self.variables_panel.draw(self.screen)
    
    def _draw_creatures_list(self) -> None:
        """
        Отрисовка окна списка существ.
        
        Элементы:
        - CreaturesPopup (модальное окно со списком)
        """
        # TODO: self.creatures_popup.draw(self.screen)
    
    def _draw_logs(self) -> None:
        """
        Отрисовка окна логов в полный экран.
        
        Элементы:
        - LogsPopup (модальное окно с логами)
        """
        # TODO: self.logs_popup.draw(self.screen)
    
    def _draw_experiment(self) -> None:
        """
        Отрисовка окна эксперимента.
        
        Элементы:
        - ExperimentModal (модальное окно с экспериментом)
        """
        # TODO: self.experiment_modal.draw(self.screen)
