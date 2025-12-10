import pygame
import sys
from typing import Dict, Any, Callable, Optional, List, Tuple


class VariablesPanel:
    """Панель переменных в BIOS/Norton Commander стиле"""
    
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    MAX_VISIBLE_VARS = 15
    
    # Геометрия панели: позиция (левый верхний угол) и размеры
    # Все значения в пикселях, за исключением указанных иначе
    PANEL_X = 0           # Абсолютная X координата (левая граница)
    PANEL_Y = 0           # Абсолютная Y координата (верхняя граница)
    PANEL_WIDTH = 0       # 0 = весь экран, >0 = фиксированная ширина
    PANEL_HEIGHT = 0      # 0 = весь экран минус нижняя панель, >0 = фиксированная высота
    FUNC_KEYS_PANEL_HEIGHT = 80  # Высота нижней панели функциональных клавиш
    
    # Внутренние смещения элементов в панели
    PADDING_X = 10        # Отступ слева и справа
    PADDING_Y = 10        # Отступ сверху и снизу
    TITLE_Y_OFFSET = 10   # Y смещение заголовка от верхнего края панели
    TITLE_BOTTOM_OFFSET = 50  # Смещение первого элемента от верхнего края панели
    ITEM_VALUE_X = 50     # X смещение значения переменной
    HIGHLIGHT_X_OFFSET = 5   # Смещение выделения слева
    HIGHLIGHT_Y_OFFSET = 3   # Смещение выделения сверху
    HIGHLIGHT_WIDTH_OFFSET = 10  # Вычитается из ширины выделения
    HIGHLIGHT_HEIGHT_OFFSET = 4  # Вычитается из высоты выделения
    
    # Цвета панели переменных
    COLORS = {
        'panel_bg': (5, 41, 158),
        'text': (170, 170, 170),
        'highlight': (255, 255, 255),
        'selected': (0, 167, 225),
        'active': (0, 170, 0),
    }

    def __init__(self, screen: pygame.Surface, font_size: int = 24, line_height: int = 30):
        """Инициализация панели переменных"""
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.font_size = font_size
        self.line_height = line_height
        
        # Инициализация шрифтов
        self.font = pygame.font.Font(self.FONT_PATH, font_size)
        self.font_bold = pygame.font.Font(self.FONT_PATH, font_size)
        
        # Переменные приложения
        self.variables: Dict[str, Dict[str, Any]] = {}
        
        # Состояние панели
        self.selected_index = 0
        self.editing = False
        self.input_buffer = ""
        
        # Вычисление фактических размеров панели
        self._calculate_bounds()
    
    def _calculate_bounds(self) -> None:
        """Расчет границ и размеров панели на основе констант и размера экрана"""
        # Позиция
        self.x = self.PANEL_X
        self.y = self.PANEL_Y
        
        # Размеры
        if self.PANEL_WIDTH == 0:
            self.width = self.screen_width
        else:
            self.width = self.PANEL_WIDTH
            
        if self.PANEL_HEIGHT == 0:
            self.height = self.screen_height - self.FUNC_KEYS_PANEL_HEIGHT
        else:
            self.height = self.PANEL_HEIGHT
        
    def add_variable(self, name: str, value: Any, var_type: type = int, 
                     min_val: Optional[float] = None, max_val: Optional[float] = None,
                     readonly: bool = False) -> None:
        """Добавить переменную в панель"""
        self.variables[name] = {
            'value': value,
            'type': var_type,
            'min': min_val,
            'max': max_val,
            'readonly': readonly,
            'display_name': name
        }
    
    def get_variable(self, name: str) -> Any:
        """Получить значение переменной"""
        return self.variables[name]['value'] if name in self.variables else None
    
    def set_variable(self, name: str, value: Any) -> None:
        """Установить значение переменной с проверкой диапазона"""
        if name not in self.variables:
            return
            
        var_info = self.variables[name]
        
        try:
            # Преобразование типа
            if var_info['type'] == int:
                value = int(value)
            elif var_info['type'] == float:
                value = float(value)
            
            # Проверка диапазона
            if var_info['min'] is not None:
                value = max(value, var_info['min'])
            if var_info['max'] is not None:
                value = min(value, var_info['max'])
            
            var_info['value'] = value
        except (ValueError, TypeError):
            pass
    
    def _draw_variable_item(self, index: int, y_pos: int, var_name: str, var_info: Dict) -> None:
        """Отрисовка одной переменной"""
        # Выделение выбранной строки
        if index == self.selected_index:
            pygame.draw.rect(self.screen, self.COLORS['selected'],
                           (self.x + self.HIGHLIGHT_X_OFFSET, y_pos - self.HIGHLIGHT_Y_OFFSET, 
                            self.width - self.HIGHLIGHT_WIDTH_OFFSET, self.line_height - self.HIGHLIGHT_HEIGHT_OFFSET))
        
        # Имя переменной
        name_text = var_info.get('display_name', var_name)
        text_color = self.COLORS['highlight'] if index == self.selected_index else self.COLORS['text']
        name_surf = self.font.render(f"{name_text:<20}", False, text_color)
        self.screen.blit(name_surf, (self.x + self.PADDING_X, y_pos))
        
        # Значение переменной
        if index == self.selected_index and self.editing:
            value_text = self.input_buffer + "_"
            value_color = self.COLORS['active']
        else:
            value_text = str(var_info['value'])
            value_color = self.COLORS['text']
        
        value_surf = self.font.render(f"{value_text:>15}", False, value_color)
        self.screen.blit(value_surf, (self.x + self.ITEM_VALUE_X, y_pos))
    
    def draw(self) -> None:
        """Отрисовка панели с переменными"""
        # Фон панели
        pygame.draw.rect(self.screen, self.COLORS['panel_bg'],
                        (self.x, self.y, self.width, self.height))
        
        # Заголовок
        title_surf = self.font_bold.render("Settings", False, self.COLORS['highlight'])
        self.screen.blit(title_surf, (self.x + self.PADDING_X, self.y + self.TITLE_Y_OFFSET))
        
        # Список переменных
        var_list = list(self.variables.items())
        max_display = min(self.MAX_VISIBLE_VARS, len(var_list))
        
        for i in range(max_display):
            var_name, var_info = var_list[i]
            y_pos = self.y + self.TITLE_BOTTOM_OFFSET + i * self.line_height
            self._draw_variable_item(i, y_pos, var_name, var_info)


class FunctionKeysPanel:
    """Панель функциональных клавиш в BIOS/Norton Commander стиле"""
    
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    MAX_FUNC_KEYS = 8
    FUNC_KEYS_PER_ROW = 1
    
    # Геометрия панели: позиция и размеры
    PANEL_X = 0           # Абсолютная X координата
    PANEL_Y = 300           # 0 = автоматически (экран_высота - PANEL_HEIGHT)
    PANEL_WIDTH = 0       # 0 = весь экран, >0 = фиксированная ширина
    PANEL_HEIGHT = 80     # Высота панели функциональных клавиш
    
    # Внутренние смещения элементов в панели
    PADDING_X = 20        # Отступ элементов слева
    PADDING_Y = 10        # Отступ элементов сверху
    ROW_HEIGHT = 30       # Высота строки с функциональными клавишами
    SEPARATOR_HEIGHT = 20  # Высота линии разделения выше панели
    SEPARATOR_WIDTH = 2   # Толщина линии разделения
    
    # Цвета панели функциональных клавиш
    COLORS = {
        'text': (170, 170, 170),
        'func_keys': (170, 170, 0),
        'border': (255, 85, 85),
    }

    def __init__(self, screen: pygame.Surface, font_size: int = 24):
        """Инициализация панели функциональных клавиш"""
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.font_size = font_size
        
        # Инициализация шрифтов
        self.font = pygame.font.Font(self.FONT_PATH, font_size)
        
        # Функциональные клавиши
        self.function_keys: Dict[str, Tuple[str, Callable]] = {}
        
        # Состояние панели
        self.selected_index = 0
        
        # Вычисление фактических размеров панели
        self._calculate_bounds()
    
    def _calculate_bounds(self) -> None:
        """Расчет границ и размеров панели на основе констант и размера экрана"""
        # Позиция
        self.x = self.PANEL_X
        if self.PANEL_Y == 0:
            self.y = self.screen_height - self.PANEL_HEIGHT
        else:
            self.y = self.PANEL_Y
        
        # Размеры
        if self.PANEL_WIDTH == 0:
            self.width = self.screen_width
        else:
            self.width = self.PANEL_WIDTH
        self.height = self.PANEL_HEIGHT
        
    def add_function_key(self, key: str, description: str, callback: Callable) -> None:
        """Добавить функциональную клавишу"""
        self.function_keys[key] = (description, callback)
    
    def draw(self, selected_index: int = 0) -> None:
        """Отрисовка панели функциональных клавиш"""
        # Линия разделения
        separator_y = self.y - self.SEPARATOR_HEIGHT
        pygame.draw.line(self.screen, self.COLORS['border'],
                        (self.x, separator_y),
                        (self.x + self.width, separator_y), 
                        self.SEPARATOR_WIDTH)
        
        # Функциональные клавиши
        for idx, (key, (desc, _)) in enumerate(self.function_keys.items()):
            if idx >= self.MAX_FUNC_KEYS:
                break
            
            row = idx // self.FUNC_KEYS_PER_ROW
            col = idx % self.FUNC_KEYS_PER_ROW
            
            x_pos = self.x + self.PADDING_X + col * (self.width // self.FUNC_KEYS_PER_ROW)
            y_pos = self.y + self.PADDING_Y + row * self.ROW_HEIGHT
            
            key_text = f"{key}: {desc}"
            color = self.COLORS['func_keys'] if idx == selected_index else self.COLORS['text']
            key_surf = self.font.render(key_text, False, color)
            self.screen.blit(key_surf, (x_pos, y_pos))


class BIOSStyleGUI:
    """Комбинированный GUI: переменные и функциональные клавиши"""

    def __init__(self, screen: pygame.Surface, font_size: int = 24, line_height: int = 30):
        """Инициализация GUI"""
        self.screen = screen
        
        # Создание компонентов
        self.variables_panel = VariablesPanel(screen, font_size, line_height)
        self.func_keys_panel = FunctionKeysPanel(screen, font_size)
        
        # Состояние GUI
        self.active_panel = "variables"
        
    def add_variable(self, name: str, value: Any, var_type: type = int, 
                     min_val: Optional[float] = None, max_val: Optional[float] = None,
                     readonly: bool = False) -> None:
        """Добавить переменную в панель"""
        self.variables_panel.add_variable(name, value, var_type, min_val, max_val, readonly)
    
    def add_function_key(self, key: str, description: str, callback: Callable) -> None:
        """Добавить функциональную клавишу"""
        self.func_keys_panel.add_function_key(key, description, callback)
    
    def get_variable(self, name: str) -> Any:
        """Получить значение переменной"""
        return self.variables_panel.get_variable(name)
    
    def set_variable(self, name: str, value: Any) -> None:
        """Установить значение переменной"""
        self.variables_panel.set_variable(name, value)
    
    def draw(self) -> None:
        """Основной метод отрисовки GUI"""
        self.variables_panel.draw()
        self.func_keys_panel.draw(self.variables_panel.selected_index if self.active_panel == "func_keys" else 0)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий ввода"""
        if event.type != pygame.KEYDOWN:
            return False
        
        var_list = list(self.variables_panel.variables.items())
        
        if self.variables_panel.editing:
            return self._handle_editing(event, var_list)
        else:
            return self._handle_navigation(event, var_list)
    
    def _handle_editing(self, event: pygame.event.Event, var_list: List) -> bool:
        """Обработка событий в режиме редактирования"""
        if event.key == pygame.K_RETURN:
            self._finish_editing(var_list)
            return True
        elif event.key == pygame.K_ESCAPE:
            self.variables_panel.editing = False
            self.variables_panel.input_buffer = ""
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.variables_panel.input_buffer = self.variables_panel.input_buffer[:-1]
            return True
        elif event.key in self._get_digit_keys():
            digit = event.key - pygame.K_0
            self.variables_panel.input_buffer += str(digit)
            return True
        elif event.key == pygame.K_MINUS and not self.variables_panel.input_buffer:
            self.variables_panel.input_buffer = "-"
            return True
        elif event.key == pygame.K_PERIOD:
            if "." not in self.variables_panel.input_buffer:
                self.variables_panel.input_buffer += "."
            return True
        
        return False
    
    @staticmethod
    def _get_digit_keys() -> tuple:
        """Возвращает кортеж кодов цифровых клавиш"""
        return (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9)
    
    def _handle_navigation(self, event: pygame.event.Event, var_list: List) -> bool:
        """Обработка событий в режиме навигации"""
        if event.key == pygame.K_TAB:
            self.active_panel = "func_keys" if self.active_panel == "variables" else "variables"
            return True
        
        elif event.key == pygame.K_UP:
            if self.active_panel == "variables":
                self.variables_panel.selected_index = max(0, self.variables_panel.selected_index - 1)
            else:
                self.variables_panel.selected_index = max(0, self.variables_panel.selected_index - 1)
            return True
        
        elif event.key == pygame.K_DOWN:
            max_index_vars = len(var_list) - 1
            max_index_func = min(FunctionKeysPanel.MAX_FUNC_KEYS - 1, len(self.func_keys_panel.function_keys) - 1)
            if self.active_panel == "variables":
                self.variables_panel.selected_index = min(max_index_vars, self.variables_panel.selected_index + 1)
            else:
                self.variables_panel.selected_index = min(max_index_func, self.variables_panel.selected_index + 1)
            return True
        
        elif event.key == pygame.K_RETURN:
            return self._activate_selected(var_list)
        
        return False
    
    def _activate_selected(self, var_list: List) -> bool:
        """Активирует выбранный элемент"""
        if self.active_panel == "variables":
            if var_list and self.variables_panel.selected_index < len(var_list):
                var_name, var_info = var_list[self.variables_panel.selected_index]
                if not var_info['readonly']:
                    self.variables_panel.editing = True
                    self.variables_panel.input_buffer = str(var_info['value'])
                    return True
        
        elif self.active_panel == "func_keys":
            func_keys_list = list(self.func_keys_panel.function_keys.items())
            if self.variables_panel.selected_index < len(func_keys_list):
                key, (desc, callback) = func_keys_list[self.variables_panel.selected_index]
                callback()
                return True
        
        return False
    
    def _finish_editing(self, var_list: List) -> None:
        """Завершение редактирования и сохранение значения"""
        if var_list and self.variables_panel.selected_index < len(var_list):
            var_name, var_info = var_list[self.variables_panel.selected_index]
            if self.variables_panel.input_buffer:
                self.variables_panel.set_variable(var_name, self.variables_panel.input_buffer)
        
        self.variables_panel.editing = False
        self.variables_panel.input_buffer = ""
    
    def run(self) -> None:
        """Запуск основного цикла GUI (для тестирования)"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                self.handle_event(event)
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)


# Демонстрация использования
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("BIOS/Norton Commander Style GUI")
    
    gui = BIOSStyleGUI(screen)
    
    # Добавление переменных
    gui.add_variable("Speed", 50, min_val=0, max_val=100)
    gui.add_variable("Power", 75.5, float, 0.0, 100.0)
    gui.add_variable("Temperature", 25, min_val=-20, max_val=50)
    gui.add_variable("State", "Активно", str)
    gui.add_variable("Mode", 1, min_val=1, max_val=5)
    gui.add_variable("Timeout", 30, min_val=1, max_val=300)
    
    # Callback функции
    def save_settings():
        print("Сохранение настроек...")
        for name, info in gui.variables_panel.variables.items():
            print(f"{name}: {info['value']}")
    
    def reset_settings():
        print("Сброс настроек")
        gui.set_variable("Speed", 50)
        gui.set_variable("Power", 75.5)
        gui.set_variable("Temperature", 25)
    
    def exit_app():
        pygame.quit()
        sys.exit()
    
    # Добавление функциональных клавиш
    gui.add_function_key("F1", "Save", save_settings)
    gui.add_function_key("F2", "Load", lambda: print("Загрузка..."))
    gui.add_function_key("F3", "Reset", reset_settings)
    gui.add_function_key("F4", "Exit", exit_app)
    gui.add_function_key("F5", "Test", lambda: print("Тестовая функция"))
    
    gui.run()