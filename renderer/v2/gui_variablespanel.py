# -*- coding: utf-8 -*-
"""
Панель переменных в стиле BIOS/Norton Commander для отображения и редактирования параметров.
Адаптирован для Renderer v2 (система состояний).
"""

import pygame
from typing import Dict, Any, Optional, List, Callable
from simparams import sp
from creature import Creature


class VariablesPanel:
    """Панель переменных для отображения и редактирования состояния симуляции."""
    
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
    
    def __init__(self, world):
        """
        Инициализация панели переменных.
        
        Args:
            world: Объект World для обновления пищи и т.д.
        """
        # TODO: Надо бы вынести из виджета gui_variablespanel.py зависимость от world и app 
        # - без этого связанность будет меньше и код чище. 
        # Сейчас мог бы это сделать, но не хочу отвлекаться.
        self.world = world
        
        # Геометрия
        self.rect = pygame.Rect(self.PANEL_X, self.PANEL_Y, 
                                self.PANEL_WIDTH, self.PANEL_HEIGHT)
        
        # Шрифт
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
        
        # Переменные приложения: {name: {value, type, min, max, callback}}
        self.variables: Dict[str, Dict[str, Any]] = {}
        
        # Состояние редактирования
        self.selected_index = 0
        self.editing = False
        self.input_buffer = ""

        # Добавляем переменные в панель с callback функциями
        self.add_variable("mutation_probability", 		sp.mutation_probability, 		float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_mutation_probability_change )
        self.add_variable("mutation_strength", 		    sp.mutation_strength, 			float, 	min_val=0.0, 	max_val=100.0, 	on_change=self._on_mutation_strength_change )
        self.add_variable("creature_max_age", 			sp.creature_max_age, 			int, 	min_val=1, 		max_val=100000, on_change=self._on_creature_max_age_change )
        self.add_variable("food_amount", 				sp.food_amount, 				int, 	min_val=1, 		max_val=100000, on_change=self._on_food_amount_change )
        self.add_variable("food_energy_capacity", 		sp.food_energy_capacity, 		float, 	min_val=0.0, 	max_val=50.0, 	on_change=self._on_food_energy_capacity_change )
        self.add_variable("food_energy_chunk", 		    sp.food_energy_chunk, 			float, 	min_val=0.0, 	max_val=50.0, 	on_change=self._on_food_energy_chunk_change )
        self.add_variable("reproduction_ages", 		    sp.reproduction_ages, 			str, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_reproduction_ages_change )
        self.add_variable("reproduction_offsprings", 	sp.reproduction_offsprings, 	int, 	min_val=1, 		max_val=100, 	on_change=self._on_reproduction_offsprings_change )
        self.add_variable("energy_cost_tick", 			sp.energy_cost_tick, 			float, 	min_val=0.0, 	max_val=100.0, 	on_change=self._on_energy_cost_tick_change )
        self.add_variable("energy_cost_speed", 		    sp.energy_cost_speed, 			float, 	min_val=0.0, 	max_val=100.0, 	on_change=self._on_energy_cost_speed_change )
        self.add_variable("energy_cost_rotate", 		sp.energy_cost_rotate, 			float, 	min_val=-20.0, 	max_val=50.0, 	on_change=self._on_energy_cost_rotate_change )
        self.add_variable("energy_cost_bite", 			sp.energy_cost_bite, 			float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_cost_bite_change )
        self.add_variable("energy_gain_from_food", 	    sp.energy_gain_from_food, 		float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_gain_from_food_change )
        self.add_variable("energy_gain_from_bite_cr", 	sp.energy_gain_from_bite_cr, 	float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_gain_from_bite_cr_change )
        self.add_variable("energy_loss_bitten", 		sp.energy_loss_bitten, 			float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_loss_bitten_change )
        self.add_variable("energy_loss_collision", 	    sp.energy_loss_collision, 		float, 	min_val=0.0, 	max_val=1.0, 	on_change=self._on_energy_loss_collision_change )
    
    def add_variable(self, name: str, value: Any, var_type: type = int,
                     min_val: Optional[float] = None, 
                     max_val: Optional[float] = None,
                     on_change: Optional[Callable[[Any], None]] = None) -> None:
        """
        Добавить переменную в панель.
        
        Args:
            name: Имя переменной (отображается в панели)
            value: Начальное значение
            var_type: Тип переменной (int, float, str)
            min_val: Минимальное значение (опционально)
            max_val: Максимальное значение (опционально)
            on_change: Callback функция вызываемая при изменении значения (опционально)
                       Получает на вход новое значение: on_change(new_value)
        """
        self.variables[name] = {
            'value': value,
            'type': var_type,
            'min': min_val,
            'max': max_val,
            'on_change': on_change,
        }
    
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
                value = value
            
            var_info['value'] = value
            
            # Вызываем callback если значение изменилось
            if value != old_value and var_info['on_change'] is not None:
                var_info['on_change'](value)
        
        except (ValueError, TypeError):
            pass
    
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
            # Пробел - добавляем в buffer и закрываем редактирование
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
            self.input_buffer = str(var_info['value'])
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
                if len(str(var_info['value'])) <= 10:
                    value_text = str(var_info['value'])
                else:
                    value_text = str(var_info['value'])[0:8] + ".."
                value_color = text_color
            
            value_surf = self.font.render(f"{value_text:>10}", False, value_color)
            screen.blit(value_surf, (self.rect.x + self.ITEM_VALUE_X, y_offset))
            
            y_offset += self.LINE_HEIGHT

    # ============================================================================
    # CALLBACKS для изменения параметров
    # ============================================================================
    
    def _on_mutation_probability_change(self, value):
        """Callback при изменении mutation_probability."""
        sp.mutation_probability = value
        print(f"mutation_probability changed to: {sp.mutation_probability}")

    def _on_mutation_strength_change(self, value):
        """Callback при изменении mutation_strength."""
        sp.mutation_strength = value
        print(f"mutation_strength changed to: {sp.mutation_strength}")

    def _on_creature_max_age_change(self, value):
        """Callback при изменении creature_max_age."""
        sp.creature_max_age = value
        print(f"creature_max_age changed to: {sp.creature_max_age}")

    def _on_food_amount_change(self, value):
        """Callback при изменении food_amount."""
        sp.food_amount = value
        print(f"food_amount changed to: {sp.food_amount}")

    def _on_food_energy_capacity_change(self, value):
        """Callback при изменении food_energy_capacity."""
        sp.food_energy_capacity = value
        self.world.change_food_capacity() # Обновляем текущую еду в мире
        print(f"food_energy_capacity changed to: {sp.food_energy_capacity}")

    def _on_food_energy_chunk_change(self, value):
        """Callback при изменении food_energy_chunk."""
        sp.food_energy_chunk = value
        print(f"food_energy_chunk changed to: {sp.food_energy_chunk}")

    def _on_reproduction_ages_change(self, value):
        """Callback при изменении reproduction_ages.
        sp.reproduction_ages = [100, 200, 300, 500]
        """
        print("Callback при изменении reproduction_ages...")
        try:
            # remove square brackets if present
            if value.startswith('[') and value.endswith(']'):
                value = value[1:-1]
            ages = [int(x.strip()) for x in value.split(",")]
            sp.reproduction_ages = ages
            print(f"reproduction_ages changed to: {sp.reproduction_ages}")

            # Обновляем возрасты рождения у всех существ
            for cr in self.world.creatures:
                cr.birth_ages = Creature.diceRandomAges(sp.reproduction_ages)
                print("diceRandomAges!!!!!!!!!!!!!!!")
            
        except Exception as e:
            print(f"Ошибка разбора reproduction_ages: {e}")

    def _on_reproduction_offsprings_change(self, value):
        """Callback при изменении reproduction_offsprings."""
        sp.reproduction_offsprings = value
        print(f"reproduction_offsprings changed to: {sp.reproduction_offsprings}")

    def _on_energy_cost_tick_change(self, value):
        """Callback при изменении energy_cost_tick."""
        sp.energy_cost_tick = value
        print(f"energy_cost_tick changed to: {sp.energy_cost_tick}")

    def _on_energy_cost_speed_change(self, value):
        """Callback при изменении energy_cost_speed."""
        sp.energy_cost_speed = value
        print(f"energy_cost_speed changed to: {sp.energy_cost_speed}")

    def _on_energy_cost_rotate_change(self, value):
        """Callback при изменении energy_cost_rotate."""
        sp.energy_cost_rotate = value
        print(f"energy_cost_rotate changed to: {sp.energy_cost_rotate}")

    def _on_energy_cost_bite_change(self, value):
        """Callback при изменении energy_cost_bite."""
        sp.energy_cost_bite = value
        print(f"energy_cost_bite changed to: {sp.energy_cost_bite}")

    def _on_energy_gain_from_food_change(self, value):
        """Callback при изменении energy_gain_from_food."""
        sp.energy_gain_from_food = value
        print(f"energy_gain_from_food changed to: {sp.energy_gain_from_food}")

    def _on_energy_gain_from_bite_cr_change(self, value):
        """Callback при изменении energy_gain_from_bite_cr."""
        sp.energy_gain_from_bite_cr = value
        print(f"energy_gain_from_bite_cr changed to: {sp.energy_gain_from_bite_cr}")

    def _on_energy_loss_bitten_change(self, value):
        """Callback при изменении energy_loss_bitten."""
        sp.energy_loss_bitten = value
        print(f"energy_loss_bitten changed to: {sp.energy_loss_bitten}")

    def _on_energy_loss_collision_change(self, value):
        """Callback при изменении energy_loss_collision."""
        sp.energy_loss_collision = value
        print(f"energy_loss_collision changed to: {sp.energy_loss_collision}")
