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
    PANEL_HEIGHT = 470
    
    # Параметры отображения
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    LINE_HEIGHT = 20
    
    TITLE_Y_OFFSET = 10
    TITLE_BOTTOM_OFFSET = 40
    ITEM_VALUE_X = 150
    PADDING_X = 5
    PADDING_Y = 5
    COMMENT_BOX_HEIGHT = 58
    COMMENT_BOX_MARGIN = 8
    COMMENT_MAX_LINES = 2

    # Двухколоночный layout
    COLUMN_SIZE = 17          # Максимум строк в одной колонке
    COLUMN_WIDTH = PANEL_WIDTH // 2  # 350px на колонку
    
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
        self.add_variable("mutation_probability",             float, min_val=0.0,     max_val=1.0,      comment="Probability of mutating each weight")
        self.add_variable("mutation_strength",                float, min_val=0.0,     max_val=100.0,    comment="Mutation strength applied to each weight")
        self.add_variable("creature_max_age",                 int,   min_val=1,       max_val=100000,   comment="Maximum creature age, in ticks")
        self.add_variable("food_amount",                      int,   min_val=1,       max_val=100000,   comment="Amount of food on the map")
        self.add_variable("food_energy_capacity",             float, min_val=0.0,     max_val=50.0,     comment="Available energy capacity of untouched food")
        self.add_variable("food_energy_chunk",                float, min_val=0.0,     max_val=50.0,     comment="Amount bitten off from food in a single bite")
        self.add_variable("food_max_age",                     int,   min_val=1,       max_val=100000,   comment="Maximum food age, in ticks")
        self.add_variable("food_proportion_indoor_outdoor",   float, min_val=0.0,     max_val=1.0,      comment="Ratio of food placed inside versus outside burrows")
        self.add_variable("reproduction_ages",                str,   min_val=0.0,     max_val=1.0,      comment="Ages at which reproduction occurs, for example: [350, 400, 450] *brackets are required*")
        self.add_variable("reproduction_offsprings",          int,   min_val=1,       max_val=100,      comment="Number of offspring produced during each reproduction")
        self.add_variable("energy_cost_tick",                 float, min_val=0.0,     max_val=100.0,    comment="Base energy cost of surviving one tick")
        self.add_variable("energy_cost_speed",                float, min_val=0.0,     max_val=100.0,    comment="Energy cost of movement speed")
        self.add_variable("energy_cost_rotate",               float, min_val=-20.0,   max_val=50.0,     comment="Energy cost of rotation")
        self.add_variable("energy_cost_bite",                 float, min_val=0.0,     max_val=1.0,      comment="Energy cost of a bite")
        self.add_variable("energy_gain_from_food",            float, min_val=0.0,     max_val=1.0,      comment="Energy gained from food")
        self.add_variable("energy_gain_from_bite_cr",         float, min_val=0.0,     max_val=1.0,      comment="[unused] Energy gained from biting another creature")
        self.add_variable("energy_loss_bitten",               float, min_val=0.0,     max_val=1.0,      comment="[unused] Energy lost when a creature is bitten")
        self.add_variable("energy_loss_collision",            float, min_val=0.0,     max_val=1.0,      comment="Penalty for colliding with a wall (currently deducted from energy)")
        self.add_variable("allow_mutations",                  int,   min_val=0,       max_val=1,        comment="Mutations are enabled (1) or disabled (0). This param also switches off automatically near population size borders")
        self.add_variable("zones_penalty_mode",               int,   min_val=0,       max_val=2,        comment="Zone penalty mode (0 = none, 1 = penalty for being inside a burrow, 2 = penalty for being outside)")
        self.add_variable("zones_penalty",                    float, min_val=0.0,     max_val=1.0,      comment="Penalty amount for staying in a zone. Applied to creature.health")
        self.add_variable("zones_penalty_probability",        float, min_val=0.0,     max_val=1.0,      comment="Probability of receiving a zone penalty (for example, 0.02 means a 2 percent chance each tick)")
    
    def add_variable(self, name: str, var_type: type = int,
                     min_val: Optional[float] = None, 
                     max_val: Optional[float] = None, 
                     comment: Optional[str] = None) -> None:
        """
        Добавить переменную в панель.
        
        Args:
            name: Имя переменной (отображается в панели)
            var_type: Тип переменной (int, float, str)
            min_val: Минимальное значение (опционально)
            max_val: Максимальное значение (опционально)
            comment: Комментарий к переменной (опционально)
        """
        self.variables[name] = {
            'value': None,  # Значение устанавливается из RenderStateDTO
            'type': var_type,
            'min': min_val,
            'max': max_val,
            'comment': comment,
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
        self.variables['food_max_age']['value'] = params_dto.food_max_age
        self.variables['food_proportion_indoor_outdoor']['value'] = params_dto.food_proportion_indoor_outdoor
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
        self.variables['zones_penalty_mode']['value'] = params_dto.zones_penalty_mode
        self.variables['zones_penalty']['value'] = params_dto.zones_penalty
        self.variables['zones_penalty_probability']['value'] = params_dto.zones_penalty_probability
    
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
        total = len(var_list)
        col, row = divmod(self.selected_index, self.COLUMN_SIZE)

        if event.key == pygame.K_UP:
            if row > 0:
                self.selected_index -= 1
            return True

        elif event.key == pygame.K_DOWN:
            next_index = self.selected_index + 1
            # Не переходить в следующую колонку и не выходить за конец списка
            if next_index < total and (next_index % self.COLUMN_SIZE) != 0:
                self.selected_index = next_index
            return True

        elif event.key == pygame.K_LEFT:
            if col > 0:
                new_index = (col - 1) * self.COLUMN_SIZE + row
                self.selected_index = min(new_index, total - 1)
            else:
                # Если мы на первой колонке - переходим на самый первый параметр
                self.selected_index = 0
            return True

        elif event.key == pygame.K_RIGHT:
            new_index = (col + 1) * self.COLUMN_SIZE + row
            if new_index < total:
                self.selected_index = new_index
            else:
                # Если в следующей колонке нет строки, переходим на последнюю строку
                self.selected_index = total - 1
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

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Разбивает текст на строки, которые помещаются по ширине."""
        if not text:
            return []

        words = text.split()
        if not words:
            return [text]

        lines = []
        current_line = words[0]

        for word in words[1:]:
            candidate = f"{current_line} {word}"
            if self.font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines
    
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
        title_surf = self.font.render("SIMULATION PARAMETERS", False, self.COLORS['highlight'])
        screen.blit(title_surf, (self.rect.x + self.PADDING_X, 
                                 self.rect.y + self.TITLE_Y_OFFSET))
        
        # Вертикальный разделитель между колонками
        divider_x = self.rect.x + self.COLUMN_WIDTH
        pygame.draw.line(screen, self.COLORS['highlight'],
                         (divider_x, self.rect.y + self.TITLE_BOTTOM_OFFSET - 5),
                         (divider_x, self.rect.y + self.PANEL_HEIGHT - 5))

        # Переменные
        var_list = list(self.variables.items())

        for idx, (var_name, var_info) in enumerate(var_list):
            col, row = divmod(idx, self.COLUMN_SIZE)
            x_base = self.rect.x + col * self.COLUMN_WIDTH
            y = self.rect.y + self.TITLE_BOTTOM_OFFSET + row * self.LINE_HEIGHT

            # Выделение выбранной строки
            if idx == self.selected_index:
                pygame.draw.rect(screen, self.COLORS['selected'],
                                 (x_base + 3, y - 2, self.COLUMN_WIDTH - 6, self.LINE_HEIGHT))

            # Имя переменной
            name_text = f"{var_name:<25}"
            text_color = self.COLORS['highlight'] if idx == self.selected_index else self.COLORS['text']
            name_surf = self.font.render(name_text, False, text_color)
            screen.blit(name_surf, (x_base + self.PADDING_X, y))

            # Значение переменной
            if idx == self.selected_index and self.editing:
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
            screen.blit(value_surf, (x_base + self.ITEM_VALUE_X, y))

        # Комментарий к выбранному параметру в нижней части панели
        if var_list and self.selected_index < len(var_list):
            selected_name, selected_info = var_list[self.selected_index]
            comment_rect = pygame.Rect(
                self.rect.x + self.COMMENT_BOX_MARGIN,
                self.rect.bottom - self.COMMENT_BOX_HEIGHT - self.COMMENT_BOX_MARGIN,
                self.rect.width - self.COMMENT_BOX_MARGIN * 2,
                self.COMMENT_BOX_HEIGHT,
            )
            pygame.draw.rect(screen, self.COLORS['bg'], comment_rect)
            pygame.draw.rect(screen, self.COLORS['highlight'], comment_rect, 1)

            min_value = selected_info.get('min')
            max_value = selected_info.get('max')
            min_text = min_value if min_value is not None else "-"
            max_text = max_value if max_value is not None else "-"
            header_text = f"HINT: {selected_name}  min:{min_text} max:{max_text}"
            header_surf = self.font.render(header_text, False, self.COLORS['highlight'])
            screen.blit(header_surf, (comment_rect.x + self.PADDING_X, comment_rect.y + 4))

            comment_text = selected_info.get('comment') or "No description available for the selected parameter"
            wrapped_lines = self._wrap_text(comment_text, comment_rect.width - self.PADDING_X * 2)

            for line_idx, line in enumerate(wrapped_lines[:self.COMMENT_MAX_LINES]):
                line_y = comment_rect.y + 22 + line_idx * self.LINE_HEIGHT
                line_surf = self.font.render(line, False, self.COLORS['text'])
                screen.blit(line_surf, (comment_rect.x + self.PADDING_X, line_y))
