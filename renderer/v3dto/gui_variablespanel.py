# -*- coding: utf-8 -*-
"""
Панель переменных в стиле BIOS/Norton Commander для отображения и редактирования параметров.
Адаптирован для Renderer v3dto (DTO архитектура с callback паттерном).
"""

import pygame
from typing import Dict, Any, Optional, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dto import RenderStateDTO


class VariablesPanel:
    """Панель переменных для отображения и редактирования состояния симуляции.
    
    Архитектура:
    - Виджет НЕ имеет доступа к world или SimParams
    - Виджет НЕ импортирует singleton зависимости
    - Вместо этого вызывает callback при изменении параметра
    - Renderer обрабатывает побочные эффекты (изменение SimParams, обновление мира и т.д.)
    """
    
    # Геометрия панели на экране
    PANEL_X = 275
    PANEL_Y = 35
    PANEL_WIDTH = 700
    PANEL_HEIGHT = 420
    
    # Параметры отображения
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    LINE_HEIGHT = 20
    
    TITLE_Y_OFFSET = 10
    TITLE_BOTTOM_OFFSET = 40
    ITEM_VALUE_X = 150
    PADDING_X = 5
    PADDING_Y = 5
    
    # Цвета
    COLORS = {
        'bg': (5, 41, 158),
        'text': (170, 170, 170),
        'highlight': (255, 255, 255),
        'selected': (0, 167, 225),
    }
    
    def __init__(self, on_parameter_change: Callable[[str, Any], None]):
        """
        Инициализация панели переменных.
        
        Args:
            on_parameter_change: Callback функция вызываемая при изменении параметра
                                Сигнатура: on_parameter_change(param_name: str, value: Any)
        """
        self.on_parameter_change = on_parameter_change
        
        # Геометрия
        self.rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, 
                                self.PANEL_WIDTH, self.PANEL_HEIGHT)
        
        # Шрифт
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
        
        # Переменные приложения: {name: {value, type, min, max}}
        # Обратите внимание: на есть 'on_change' callback - они больше не нужны!
        self.variables: Dict[str, Dict[str, Any]] = {}
        
        # Состояние редактирования
        self.selected_index = 0
        self.editing = False
        self.input_buffer = ""

        # Добавляем переменные в панель
        # Значения берутся из RenderStateDTO во время draw()
        self.add_variable("mutation_probability",        float, min_val=0.0,     max_val=1.0)
        self.add_variable("mutation_strength",           float, min_val=0.0,     max_val=100.0)
        self.add_variable("creature_max_age",            int,   min_val=1,       max_val=100000)
        self.add_variable("food_amount",                 int,   min_val=1,       max_val=100000)
        self.add_variable("food_energy_capacity",        float, min_val=0.0,     max_val=50.0)
        self.add_variable("food_energy_chunk",           float, min_val=0.0,     max_val=50.0)
        self.add_variable("reproduction_ages",           str,   min_val=0.0,     max_val=1.0)
        self.add_variable("reproduction_offsprings",     int,   min_val=1,       max_val=100)
        self.add_variable("energy_cost_tick",            float, min_val=0.0,     max_val=100.0)
        self.add_variable("energy_cost_speed",           float, min_val=0.0,     max_val=100.0)
        self.add_variable("energy_cost_rotate",          float, min_val=-20.0,   max_val=50.0)
        self.add_variable("energy_cost_bite",            float, min_val=0.0,     max_val=1.0)
        self.add_variable("energy_gain_from_food",       float, min_val=0.0,     max_val=1.0)
        self.add_variable("energy_gain_from_bite_cr",    float, min_val=0.0,     max_val=1.0)
        self.add_variable("energy_loss_bitten",          float, min_val=0.0,     max_val=1.0)
        self.add_variable("energy_loss_collision",       float, min_val=0.0,     max_val=1.0)
        self.add_variable("allow_mutations",               int,  min_val=0,      max_val=1)
    
    def add_variable(self, name: str, var_type: type = int,
                     min_val: Optional[float] = None, 
                     max_val: Optional[float] = None) -> None:
        """
        Добавить переменную в панель.
        
        Args:
            name: Имя переменной (отображается в панели)
            var_type: Тип переменной (int, float, str)
            min_val: Минимальное значение (опционально)
            max_val: Максимальное значение (опционально)
        """
        self.variables[name] = {
            'value': None,  # Значение устанавливается из RenderStateDTO
            'type': var_type,
            'min': min_val,
            'max': max_val,
        }
    
    def update_from_render_state(self, render_state: 'RenderStateDTO') -> None:
        """
        Обновить текущие значения переменных из RenderStateDTO.
        
        Args:
            render_state: RenderStateDTO со всеми параметрами
        """
        params_dto = render_state.params
        
        # Обновляем значения из DTO
        self.variables['mutation_probability']['value'] = params_dto.mutation_probability
        self.variables['mutation_strength']['value'] = params_dto.mutation_strength
        self.variables['creature_max_age']['value'] = params_dto.creature_max_age
        self.variables['food_amount']['value'] = params_dto.food_amount
        self.variables['food_energy_capacity']['value'] = params_dto.food_energy_capacity
        self.variables['food_energy_chunk']['value'] = params_dto.food_energy_chunk
        self.variables['reproduction_ages']['value'] = str(params_dto.reproduction_ages)
        self.variables['reproduction_offsprings']['value'] = params_dto.reproduction_offsprings
        self.variables['energy_cost_tick']['value'] = params_dto.energy_cost_tick
        self.variables['energy_cost_speed']['value'] = params_dto.energy_cost_speed
        self.variables['energy_cost_rotate']['value'] = params_dto.energy_cost_rotate
        self.variables['energy_cost_bite']['value'] = params_dto.energy_cost_bite
        self.variables['energy_gain_from_food']['value'] = params_dto.energy_gain_from_food
        self.variables['energy_gain_from_bite_cr']['value'] = params_dto.energy_gain_from_bite_cr
        self.variables['energy_loss_bitten']['value'] = params_dto.energy_loss_bitten
        self.variables['energy_loss_collision']['value'] = params_dto.energy_loss_collision
        self.variables['allow_mutations']['value'] = params_dto.allow_mutations
    
    def get_variable(self, name: str) -> Any:
        """Получить значение переменной."""
        if name not in self.variables:
            return None
        return self.variables[name]['value']
    
    def set_variable(self, name: str, value: Any) -> None:
        """
        Установить значение переменной с проверкой типа и диапазона.
        Вызовет callback если значение изменилось.
        
        Args:
            name: Имя переменной
            value: Новое значение
        """
        if name not in self.variables:
            return
        
        var_info = self.variables[name]
        old_value = var_info['value']
        
        try:
            # Преобразование типа
            if var_info['type'] == int:
                value = int(value)
                # Проверка диапазона
                if var_info['min'] is not None:
                    value = max(value, var_info['min'])
                if var_info['max'] is not None:
                    value = min(value, var_info['max'])
            elif var_info['type'] == float:
                value = float(value)
                # Проверка диапазона
                if var_info['min'] is not None:
                    value = max(value, var_info['min'])
                if var_info['max'] is not None:
                    value = min(value, var_info['max'])
            elif var_info['type'] == str:
                value = str(value)
            
            var_info['value'] = value
            
            # Вызываем callback если значение изменилось
            if value != old_value:
                self.on_parameter_change(name, value)
                print(f"Parameter changed: {name} = {value}")
        
        except (ValueError, TypeError) as e:
            print(f"Error setting {name}: {e}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий клавиатуры.
        
        Args:
            event: pygame.event.Event клавиатурного события
            
        Returns:
            True если событие обработано
        """
        if event.type != pygame.KEYDOWN:
            return False
        
        var_list = list(self.variables.items())
        
        if self.editing:
            return self._handle_editing(event, var_list)
        else:
            return self._handle_navigation(event, var_list)
    
    def _handle_editing(self, event: pygame.event.Event, var_list: List) -> bool:
        """Обработка событий в режиме редактирования."""
        if event.key == pygame.K_RETURN:
            self._finish_editing(var_list)
            return True
        
        elif event.key == pygame.K_ESCAPE:
            self.editing = False
            self.input_buffer = ""
            return True
        
        elif event.key == pygame.K_BACKSPACE:
            self.input_buffer = self.input_buffer[:-1]
            return True
        
        elif event.key in self._get_digit_keys():
            digit = event.key - pygame.K_0
            self.input_buffer += str(digit)
            return True
        
        elif event.key == pygame.K_MINUS and not self.input_buffer:
            self.input_buffer = "-"
            return True
        
        elif event.key == pygame.K_PERIOD:
            if "." not in self.input_buffer:
                self.input_buffer += "."
            return True
        
        elif event.key == pygame.K_COMMA:
            self.input_buffer += ","
            return True
        
        elif event.key == pygame.K_LEFTBRACKET:
            self.input_buffer += "["
            return True
        
        elif event.key == pygame.K_RIGHTBRACKET:
            self.input_buffer += "]"
            return True
        
        elif event.key == pygame.K_SPACE:
            self.input_buffer += " "
            return True
        
        return False
    
    @staticmethod
    def _get_digit_keys() -> tuple:
        """Возвращает кортеж кодов цифровых клавиш."""
        return (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9)
    
    def _handle_navigation(self, event: pygame.event.Event, var_list: List) -> bool:
        """Обработка событий в режиме навигации."""
        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            return True
        
        elif event.key == pygame.K_DOWN:
            max_index = len(var_list) - 1
            self.selected_index = min(max_index, self.selected_index + 1)
            return True
        
        elif event.key == pygame.K_RETURN:
            return self._activate_selected(var_list)
        
        return False
    
    def _activate_selected(self, var_list: List) -> bool:
        """Активирует выбранный элемент для редактирования."""
        if var_list and self.selected_index < len(var_list):
            var_name, var_info = var_list[self.selected_index]
            self.editing = True
            self.input_buffer = str(var_info['value']) if var_info['value'] is not None else ""
            return True
        
        return False
    
    def _finish_editing(self, var_list: List) -> None:
        """Завершение редактирования и сохранение значения."""
        if var_list and self.selected_index < len(var_list):
            var_name, var_info = var_list[self.selected_index]
            if self.input_buffer:
                self.set_variable(var_name, self.input_buffer)
        
        self.editing = False
        self.input_buffer = ""
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовка панели переменных на экран.
        
        Args:
            screen: pygame.Surface главного экрана для отрисовки
        """
        # Фон панели
        pygame.draw.rect(screen, self.COLORS['bg'], self.rect)
        pygame.draw.rect(screen, self.COLORS['highlight'], self.rect, 2)
        
        # Заголовок
        title_surf = self.font.render("VARS", False, self.COLORS['highlight'])
        screen.blit(title_surf, (self.rect.x + self.PADDING_X, 
                                 self.rect.y + self.TITLE_Y_OFFSET))
        
        # Переменные
        var_list = list(self.variables.items())
        y_offset = self.rect.y + self.TITLE_BOTTOM_OFFSET
        
        for idx, (var_name, var_info) in enumerate(var_list):
            # Выделение выбранной строки
            if idx == self.selected_index:
                pygame.draw.rect(screen, self.COLORS['selected'],
                               (self.rect.x + 3, y_offset - 2, 
                                self.rect.width - 6, self.LINE_HEIGHT))
            
            # Имя переменной
            name_text = f"{var_name:<15}"
            text_color = self.COLORS['highlight'] if idx == self.selected_index else self.COLORS['text']
            name_surf = self.font.render(name_text, False, text_color)
            screen.blit(name_surf, (self.rect.x + self.PADDING_X, y_offset))
            
            # Значение переменной
            if idx == self.selected_index and self.editing:
                # В режиме редактирования показываем input_buffer с курсором
                value_text = self.input_buffer + "_"
                value_color = (255, 255, 0)  # Жёлтый для редактируемого
            else:
                value_display = var_info['value'] if var_info['value'] is not None else "N/A"
                if len(str(value_display)) <= 10:
                    value_text = str(value_display)
                else:
                    value_text = str(value_display)[0:8] + ".."
                value_color = text_color
            
            value_surf = self.font.render(f"{value_text:>10}", False, value_color)
            screen.blit(value_surf, (self.rect.x + self.ITEM_VALUE_X, y_offset))
            
            y_offset += self.LINE_HEIGHT
