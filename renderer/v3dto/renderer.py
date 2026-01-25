# -*- coding: utf-8 -*-
"""
Renderer v3dto - версия с изоляцией данных через DTO.

Архитектура:
- Renderer получает world, app, debugger, logger
- Но НЕ пробрасывает их виджетам
- Вместо этого преобразует данные в DTO
- Виджеты работают только с DTO и полностью от них отделены

Это позволяет:
✓ Полностью тестировать виджеты
✓ Менять источник данных без изменения виджетов
✓ Явные контракты между слоями
✓ Слабая связанность
"""

import pygame
from typing import Dict, Optional, Callable
import numpy as np

from renderer.v3dto.gui_viewport import Viewport
from renderer.v3dto.gui_variablespanel import VariablesPanel
from renderer.v3dto.gui_selected_creature import SelectedCreaturePanel
from renderer.v3dto.gui_selected_creature_history import SelectedCreatureHistory
from renderer.v3dto.gui_pop_chart import PopulationChart
from renderer.v3dto.gui_nselection_chart import NSelectionChart
from renderer.v3dto.gui_creatures_list import CreaturesListModal
from renderer.v3dto.gui_experiment import ExperimentModal

from renderer.v3dto.dto import (
    CreatureDTO, WorldStateDTO, FoodDTO, CreatureEventDTO,
    CreatureHistoryDTO, DebugDataDTO, SimulationParamsDTO,
    SelectedCreaturePanelDTO, RenderStateDTO
)

from service.logger.logger import logme
from service.debugger.debugger import debug


class Renderer:
    """
    Renderer v3dto с изоляцией данных через DTO.
    
    Основные отличия от v2:
    1. Все данные для виджетов передаются через DTO
    2. Виджеты не получают прямой доступ к world, logger, debugger
    3. Renderer отвечает за преобразование данных в DTO
    4. Полная изоляция Presentation от Domain Logic
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
        pygame.display.set_caption("NNEvol (Khan RL Lab) - v3dto")
        try:
            icon_surface = pygame.image.load('./docs/icon.png')
            pygame.display.set_icon(icon_surface)
        except:
            pass  # Иконка опциональна
        
        # Инициализация шрифта
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
        
        # СИСТЕМА СОСТОЯНИЙ
        self.current_state = 'main'
        self.states = {
            'main': 'Основное окно с картой',
            'popup_simparams': 'Popup окно параметров симуляции (модальное)',
            'creatures_list': 'Список существ (модальное)',
            'logs': 'Логи в полный экран (модальное)',
            'experiment': 'Окно эксперимента (модальное)',
        }
        
        # Часы для управления FPS
        self.clock = pygame.time.Clock()
        
        # ВИДЖЕТЫ
        self.viewport = Viewport()
        self.variables_panel = VariablesPanel(on_parameter_change=self._on_parameter_change)
        self.selected_creature_panel = SelectedCreaturePanel()
        self.selected_creature_history = SelectedCreatureHistory()
        self.pop_chart = PopulationChart()
        self.nselection_chart = NSelectionChart()
        self.creatures_list_modal = CreaturesListModal()
        self.experiment_modal = ExperimentModal()
        
        # ВЫБОР СУЩЕСТВА (только ID, данные передаются через DTO)
        self.selected_creature_id: Optional[int] = None
        
        # FPS счетчик для отладки
        self.frame_count = 0
        self.fps = 0

    # ============================================================================
    # УПРАВЛЕНИЕ СОСТОЯНИЯМИ
    # ============================================================================
    
    def set_state(self, state_name: str) -> bool:
        """Переключиться на новое состояние."""
        if state_name not in self.states:
            print(f"⚠️ Неизвестное состояние: {state_name}")
            return False
        
        if self.current_state != state_name:
            print(f"State transition: {self.current_state} → {state_name}")
            self.current_state = state_name
            
            # Управление паузой: модальные окна ставят симуляцию на паузу
            if state_name != 'main':
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
        """Проверить, находимся ли в основном состоянии."""
        return self.current_state == 'main'
    
    def is_modal_state(self) -> bool:
        """Проверить, находимся ли в модальном окне."""
        return self.current_state != 'main'
    
    def _on_state_enter(self, state_name: str) -> None:
        """Вызывается при входе в новое состояние."""
        if state_name == 'creatures_list':
            # Сбрасываем навигацию при открытии списка существ
            self.creatures_list_modal.reset()
        elif state_name == 'experiment':
            # Сбрасываем состояние при открытии окна экспериментов
            self.experiment_modal.reset()
    
    # ============================================================================
    # ОБРАБОТЧИК ИЗМЕНЕНИЙ ПАРАМЕТРОВ
    # ============================================================================
    
    def _select_creature_by_tab(self) -> None:
        """
        Переключиться на существо со следующим по убыванию ID при нажатии TAB.
        
        Логика:
        - Если ничего не выбрано: выбрать существо с максимальным ID
        - Если что-то выбрано: выбрать существо с ID, на 1 меньше текущего
        - Если достигли минимального ID, циклимся на максимальный
        """
        if not self.world.creatures:
            self.selected_creature_id = None
            return
        
        # Получаем все ID существ и сортируем в порядке убывания
        all_ids = sorted([c.id for c in self.world.creatures], reverse=True)
        
        if self.selected_creature_id is None:
            # Если ничего не выбрано, выбираем существо с максимальным ID
            self.selected_creature_id = all_ids[0]
            print(f"✓ Creature selected (TAB): id={self.selected_creature_id} (max)")
        else:
            # Найти текущее существо в отсортированном списке
            if self.selected_creature_id in all_ids:
                current_index = all_ids.index(self.selected_creature_id)
                # Переходим на следующее (которое имеет меньший ID)
                next_index = (current_index + 1) % len(all_ids)
                self.selected_creature_id = all_ids[next_index]
                is_cycled = next_index == 0
                if is_cycled:
                    print(f"✓ Creature selected (TAB): id={self.selected_creature_id} (min, cycled to max)")
                else:
                    print(f"✓ Creature selected (TAB): id={self.selected_creature_id}")
            else:
                # Если текущее существо больше не существует, выбираем максимальное
                self.selected_creature_id = all_ids[0]
                print(f"✓ Creature selected (TAB): id={self.selected_creature_id} (previous dead, reset to max)")
    
    def _select_creature_by_shift_tab(self) -> None:
        """
        Переключиться на существо со следующим по возрастанию ID при нажатии Shift+TAB.
        
        Логика:
        - Если ничего не выбрано: выбрать существо с минимальным ID
        - Если что-то выбрано: выбрать существо с ID, на 1 больше текущего
        - Если достигли максимального ID, циклимся на минимальный
        """
        if not self.world.creatures:
            self.selected_creature_id = None
            return
        
        # Получаем все ID существ и сортируем в порядке возрастания
        all_ids = sorted([c.id for c in self.world.creatures])
        
        if self.selected_creature_id is None:
            # Если ничего не выбрано, выбираем существо с минимальным ID
            self.selected_creature_id = all_ids[0]
            print(f"✓ Creature selected (Shift+TAB): id={self.selected_creature_id} (min)")
        else:
            # Найти текущее существо в отсортированном списке
            if self.selected_creature_id in all_ids:
                current_index = all_ids.index(self.selected_creature_id)
                # Переходим на следующее (которое имеет больший ID)
                next_index = (current_index + 1) % len(all_ids)
                self.selected_creature_id = all_ids[next_index]
                is_cycled = next_index == 0
                if is_cycled:
                    print(f"✓ Creature selected (Shift+TAB): id={self.selected_creature_id} (max, cycled to min)")
                else:
                    print(f"✓ Creature selected (Shift+TAB): id={self.selected_creature_id}")
            else:
                # Если текущее существо больше не существует, выбираем минимальное
                self.selected_creature_id = all_ids[0]
                print(f"✓ Creature selected (Shift+TAB): id={self.selected_creature_id} (previous dead, reset to min)")
    
    def _select_creature_reset(self) -> None:
        """
        Сбросить выбор существа (нажата ESCAPE).
        """
        if self.selected_creature_id is not None:
            print(f"✓ Creature selection reset (ESCAPE)")
            self.selected_creature_id = None
        return

    
    
    
    def _on_parameter_change(self, param_name: str, value: any) -> None:
        """
        Callback для обработки изменений параметров из VariablesPanel.
        
        Args:
            param_name: Имя параметра (e.g. "mutation_probability")
            value: Новое значение параметра
        """
        from simparams import sp
        
        # Устанавливаем значение в SimParams
        if hasattr(sp, param_name):
            setattr(sp, param_name, value)
            print(f"✓ Parameter updated: {param_name} = {getattr(sp, param_name)}")
            
            # Обработка побочных эффектов
            if param_name == "food_amount":
                # Если количество еды изменилось, обновляем мир
                if hasattr(self.world, 'change_food_capacity'):
                    self.world.change_food_capacity()
                    print(f"✓ World food capacity updated")
            
            elif param_name == "reproduction_ages":
                # Если возрасты размножения изменились, обновляем у всех существ
                from creature import Creature
                for creature in self.world.creatures:
                    creature.birth_ages = Creature.diceRandomAges(sp.reproduction_ages)
                print(f"✓ All creatures reproduction ages updated")
        else:
            print(f"✗ Unknown parameter: {param_name}")

    # ============================================================================
    # DTO FACTORY МЕТОДЫ
    # ============================================================================
    
    def _prepare_creature_dto(self, creature) -> CreatureDTO:
        """Преобразовать объект Creature в CreatureDTO."""
        return CreatureDTO(
            id=creature.id,
            x=creature.x,
            y=creature.y,
            angle=creature.angle,
            energy=creature.energy,
            age=creature.age,
            speed=creature.speed,
            generation=creature.generation,
            bite_effort=creature.bite_effort,
            vision_distance=creature.vision_distance,
            bite_range=creature.bite_range,
        )
    
    def _prepare_food_dto(self, food) -> FoodDTO:
        """Преобразовать объект Food в FoodDTO."""
        return FoodDTO(
            x=food.x,
            y=food.y,
            energy=food.nutrition,
        )
    
    def _prepare_world_dto(self) -> WorldStateDTO:
        """Собрать снимок world в WorldStateDTO.
        
        ВАЖНО: Это преобразование должно быть быстрым, т.к. вызывается каждый фрейм!
        """
        creatures_dto = [self._prepare_creature_dto(c) for c in self.world.creatures]
        foods_dto = [self._prepare_food_dto(f) for f in self.world.foods]
        
        return WorldStateDTO(
            map=self.world.map,
            width=self.world.width,
            height=self.world.height,
            creatures=creatures_dto,
            foods=foods_dto,
            tick=self.world.tick,
        )
    
    def _prepare_debug_dto(self) -> DebugDataDTO:
        """Собрать отладочные данные из debugger синглтона в DebugDataDTO."""
        return DebugDataDTO(
            raycast_dots=debug.get("raycast_dots"),
            all_visions=debug.get("all_visions"),
            all_outs=debug.get("all_outs"),
        )
    
    def _prepare_simulation_params_dto(self) -> SimulationParamsDTO:
        """Собрать параметры симуляции в SimulationParamsDTO."""
        from simparams import sp
        
        return SimulationParamsDTO(
            mutation_probability=sp.mutation_probability,
            mutation_strength=sp.mutation_strength,
            creature_max_age=sp.creature_max_age,
            food_amount=sp.food_amount,
            food_energy_capacity=sp.food_energy_capacity,
            food_energy_chunk=sp.food_energy_chunk,
            reproduction_ages=sp.reproduction_ages,
            reproduction_offsprings=sp.reproduction_offsprings,
            energy_cost_tick=sp.energy_cost_tick,
            energy_cost_speed=sp.energy_cost_speed,
            energy_cost_rotate=sp.energy_cost_rotate,
            energy_cost_bite=sp.energy_cost_bite,
            energy_gain_from_food=sp.energy_gain_from_food,
            energy_gain_from_bite_cr=sp.energy_gain_from_bite_cr,
            energy_loss_bitten=sp.energy_loss_bitten,
            energy_loss_collision=sp.energy_loss_collision,
            is_running=self.app.is_running,
            is_animating=self.app.animate_flag,
            is_logging=self.app.is_logging,
            allow_mutations=sp.allow_mutations,
        )
    
    def _prepare_creature_history_dto(self, creature_id: int) -> Optional[CreatureHistoryDTO]:
        """Собрать историю существа из logger в CreatureHistoryDTO."""
        energy_history = logme.get_creature_energy_history(creature_id)
        creature_events = logme.get_creature_events(creature_id)
        
        # Преобразуем события в DTO
        events_dto = [
            CreatureEventDTO(
                tick=event.tick_number,
                event_type=event.event_type,
                value=event.value,
            )
            for event in creature_events
        ]
        
        return CreatureHistoryDTO(
            creature_id=creature_id,
            energy_history=energy_history,
            events=events_dto,
        )
    
    def _prepare_selected_creature_dto(self, world_dto: WorldStateDTO) -> Optional[SelectedCreaturePanelDTO]:
        """Собрать DTO для выбранного существа."""
        if self.selected_creature_id is None:
            return None
        
        creature_dto = world_dto.get_creature_by_id(self.selected_creature_id)
        if creature_dto is None:
            return None
        
        history_dto = self._prepare_creature_history_dto(self.selected_creature_id)
        
        return SelectedCreaturePanelDTO(
            creature=creature_dto,
            history=history_dto,
        )
    
    def _prepare_render_state_dto(self) -> RenderStateDTO:
        """Собрать ПОЛНЫЙ снимок состояния для всех виджетов в RenderStateDTO.
        
        Это главный метод, который собирает все DTO для передачи в виджеты.
        """
        world_dto = self._prepare_world_dto()
        params_dto = self._prepare_simulation_params_dto()
        debug_dto = self._prepare_debug_dto()
        selected_creature_dto = self._prepare_selected_creature_dto(world_dto)
        
        return RenderStateDTO(
            world=world_dto,
            params=params_dto,
            debug=debug_dto,
            selected_creature=selected_creature_dto,
            current_state=self.current_state,
            tick=self.world.tick,
            fps=self.fps,
        )

    # ============================================================================
    # ОБРАБОТКА СОБЫТИЙ
    # ============================================================================

    def _handle_keyboard(self, event: pygame.event.Event) -> bool:
        """Обработка клавиатурных событий."""
        if self.current_state == 'main':
            return self._handle_keyboard_main(event)
        elif self.current_state == 'popup_simparams':
            return self._handle_keyboard_popup_simparams(event)
        elif self.current_state == 'creatures_list':
            return self._handle_keyboard_creatures_list(event)
        elif self.current_state == 'logs':
            return self._handle_keyboard_logs(event)
        elif self.current_state == 'experiment':
            return self._handle_keyboard_experiment(event)
        
        return False
    
    def _handle_keyboard_main(self, event: pygame.event.Event) -> bool:
        """Обработка событий в основном состоянии."""
        if event.type != pygame.KEYDOWN:
            return False
        
        # Функциональные клавиши - открытие модальных окон
        if event.key == pygame.K_F1:
            self.set_state('creatures_list')
            print(logme.get_death_stats_as_ndarray())
            return False
        elif event.key == pygame.K_F2:
            self.set_state('experiment')
            return False
        elif event.key == pygame.K_F9:
            self.set_state('popup_simparams')
            return False
        elif event.key == pygame.K_F12:
            self.set_state('logs')
            return False
        
        # Глобальные команды
        if event.key == pygame.K_SPACE:
            self.app.toggle_run()
            return False
        elif event.key == pygame.K_a:
            self.app.toggle_animate()
            return False
        elif event.key == pygame.K_TAB:
            # Проверяем, нажата ли клавиша Shift
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_SHIFT:
                # Shift+TAB: переключаться между существами по ID (от min к max)
                self._select_creature_by_shift_tab()
            else:
                # TAB: переключаться между существами по ID (от max к min)
                self._select_creature_by_tab()
            return False
        elif event.key == pygame.K_ESCAPE:
            self._select_creature_reset()
        
        return False
    
    def _handle_keyboard_popup_simparams(self, event: pygame.event.Event) -> bool:
        """Обработка событий в окне параметров симуляции."""
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F9:
            self.set_state('main')
            return True
        
        # Делегируем обработку событий VariablesPanel
        if self.variables_panel.handle_event(event):
            return True
        
        return False
    
    def _handle_keyboard_creatures_list(self, event: pygame.event.Event) -> bool:
        """Обработка событий в окне списка существ."""
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1:
            self.set_state('main')
            return True
        
        # Навигация в списке существ
        creatures_count = len(self.world.creatures)
        
        if event.key == pygame.K_UP:
            self.creatures_list_modal.move_selection_up(creatures_count)
            return True
        
        elif event.key == pygame.K_DOWN:
            self.creatures_list_modal.move_selection_down(creatures_count)
            return True
        
        elif event.key == pygame.K_HOME:
            self.creatures_list_modal.move_selection_home()
            return True
        
        elif event.key == pygame.K_END:
            self.creatures_list_modal.move_selection_end(creatures_count)
            return True
        
        return False
    
    def _handle_keyboard_logs(self, event: pygame.event.Event) -> bool:
        """Обработка событий в окне логов."""
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F12:
            self.set_state('main')
            return True
        
        return False
    
    def _handle_keyboard_experiment(self, event: pygame.event.Event) -> bool:
        """Обработка событий в окне эксперимента."""
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F2:
            self.set_state('main')
            return True
        
        return False

    def _handle_mouse(self, event: pygame.event.Event, world_dto: WorldStateDTO) -> None:
        """Обработка событий мыши."""
        if self.current_state == 'main':
            # Сначала обрабатываем событие в viewport (пан, зум)
            self.viewport.handle_event(event)
            
            # Левая кнопка мыши - выбор существа
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                creature_id = self.viewport.get_creature_at_position(event.pos, world_dto)
                
                if creature_id is not None:
                    self.selected_creature_id = creature_id
                    print(f"✓ Creature selected: id={creature_id}")
                else:
                    self.selected_creature_id = None
                    print("✗ No creature at this position")

    def control_run(self) -> bool:
        """Основная функция обработки событий.
        
        Вызывается один раз за фрейм из application.py
        
        Returns:
            True если надо выходить из приложения
        """
        # Подготовим DTO для mouse handler (может потребоваться)
        world_dto = self._prepare_world_dto()
        
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
                self._handle_mouse(event, world_dto)
        
        return False

    # ============================================================================
    # ОТРИСОВКА
    # ============================================================================

    def draw(self) -> None:
        """Отрисовка всех компонентов.
        
        Главный метод рисования, вызывается один раз за фрейм из application.py.
        
        Здесь происходит:
        1. Подготовка RenderStateDTO со всеми данными
        2. Отрисовка в зависимости от текущего состояния
        3. Обновление дисплея
        """
        # Очистка экрана
        self.screen.fill(self.COLORS['background'])
        
        # Подготовка полного снимка состояния для виджетов
        render_state = self._prepare_render_state_dto()
        
        # Отрисовка в зависимости от состояния
        if self.current_state == 'main':
            self._draw_main(render_state)
        elif self.current_state == 'popup_simparams':
            self._draw_popup_simparams(render_state)
        elif self.current_state == 'creatures_list':
            self._draw_creatures_list(render_state)
        elif self.current_state == 'logs':
            self._draw_logs(render_state)
        elif self.current_state == 'experiment':
            self._draw_experiment(render_state)
        
        # Обновление дисплея
        pygame.display.flip()
        
        # Обновление FPS
        self.frame_count += 1
        if self.frame_count >= 30:
            self.fps = int(self.clock.get_fps())
            self.frame_count = 0
        
        self.clock.tick(60)  # 60 FPS max
    
    def _draw_main(self, render_state: RenderStateDTO) -> None:
        """Отрисовка основного состояния.
        
        Элементы:
        - Viewport (карта мира)
        - SelectedCreaturePanel (информация о выбранном существе)
        - SelectedCreatureHistory (история энергии)
        - PopulationChart (график размера популяции)
        - NSelectionChart (гистограмма смертей по возрастам)
        """
        # Отрисовка viewport
        self.viewport.draw(self.screen, render_state, self.font)

        # Отрисовка графика популяции
        self.pop_chart.draw(self.screen, render_state)
        
        # Отрисовка гистограммы смертей по возрастам
        self.nselection_chart.draw(self.screen, render_state)
        
        # Отрисовка панели выбранного существа
        self.selected_creature_panel.draw(self.screen, render_state)
        
        # Отрисовка истории энергии
        self.selected_creature_history.draw(self.screen, render_state)
        
        
    
    def _draw_popup_simparams(self, render_state: RenderStateDTO) -> None:
        """Отрисовка окна параметров симуляции."""
        # Обновляем значения панели из RenderStateDTO
        self.variables_panel.update_from_render_state(render_state)
        
        # Отрисовка переменной панели
        self.variables_panel.draw(self.screen)
    
    def _draw_creatures_list(self, render_state: RenderStateDTO) -> None:
        """Отрисовка окна списка существ."""
        self.creatures_list_modal.draw(self.screen, render_state)
    
    def _draw_logs(self, render_state: RenderStateDTO) -> None:
        """Отрисовка окна логов в полный экран."""
        # TODO: self.logs_popup.draw(self.screen, render_state)
        self._draw_debug_info(render_state)
    
    def _draw_experiment(self, render_state: RenderStateDTO) -> None:
        """Отрисовка окна эксперимента."""
        self.experiment_modal.draw(self.screen, render_state)
    
    def _draw_debug_info(self, render_state: RenderStateDTO) -> None:
        """Вспомогательный метод для отрисовки отладочной информации."""
        info_lines = [
            f"v3dto Architecture Test",
            f"State: {render_state.current_state}",
            f"Population: {render_state.population_count}",
            f"Food: {render_state.food_count}",
            f"Tick: {render_state.tick}",
            f"FPS: {render_state.fps}",
            f"Selected: {self.selected_creature_id}",
            f"",
            f"DTO Structure:",
            f"  WorldStateDTO: {len(render_state.world.creatures)} creatures",
            f"  DebugDataDTO: empty={render_state.debug.is_empty()}",
            f"  SimulationParamsDTO: loaded",
            f"  SelectedCreaturePanelDTO: {render_state.selected_creature is not None}",
        ]
        
        for i, line in enumerate(info_lines):
            text_surface = self.font.render(line, True, self.COLORS['text'])
            self.screen.blit(text_surface, (10, 10 + i * 20))
