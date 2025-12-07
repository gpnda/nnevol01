import pygame
import sys
from typing import Dict, Any, Callable, Optional, List, Tuple

class BIOSStyleGUI:
    def __init__(self, screen: pygame.Surface, font_size: int = 24):
        """
        Инициализация GUI в стиле BIOS/Norton Commander
        
        Args:
            screen: Surface PyGame для отрисовки
            font_size: Размер шрифта
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Шрифт в стиле терминала
        #self.font = pygame.font.SysFont('couriernew', font_size)
        #self.font_bold = pygame.font.SysFont('couriernew', font_size, bold=True)
        self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', font_size)
        self.font_bold = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', font_size)
        
        # Цвета BIOS-стиля
        self.COLORS = {
            'bg': (0, 0, 0),           # Черный фон
            'text': (170, 170, 170),   # Серый текст
            'highlight': (255, 255, 255), # Белый выделение
            'selected': (0, 85, 0),    # Темно-зеленый выбранный
            'active': (0, 170, 0),     # Зеленый активный
            'panel_bg': (0, 0, 85),    # Темно-синий фон панели
            'border': (85, 85, 85),    # Серый бордюр
            'func_keys': (170, 170, 0),# Желтый для функциональных клавиш
        }
        
        # Переменные приложения (имя: [значение, тип, min, max])
        self.variables: Dict[str, Dict[str, Any]] = {}
        
        # Функциональные клавиши (key: [описание, callback])
        self.function_keys: Dict[str, Tuple[str, Callable]] = {}
        
        # Состояние GUI
        self.selected_index = 0  # Выбранная строка в панели переменных
        self.editing = False     # Режим редактирования значения
        self.input_buffer = ""   # Буфер ввода для редактирования
        self.active_panel = "variables"  # Активная панель: "variables" или "func_keys"
        
        # Области отрисовки
        self.panel_width = self.width // 2 - 50
        self.panel_height = self.height - 100
        self.panel_x = 20
        self.panel_y = 20
        
        # Функциональные клавиши внизу
        self.func_keys_y = self.height - 60
        
    def add_variable(self, name: str, value: Any, var_type: type = int, 
                     min_val: Optional[float] = None, max_val: Optional[float] = None,
                     readonly: bool = False):
        """
        Добавить переменную в левую панель
        
        Args:
            name: Имя переменной
            value: Начальное значение
            var_type: Тип переменной (int, float, str)
            min_val: Минимальное значение (для чисел)
            max_val: Максимальное значение (для чисел)
            readonly: Только для чтения
        """
        self.variables[name] = {
            'value': value,
            'type': var_type,
            'min': min_val,
            'max': max_val,
            'readonly': readonly,
            'display_name': name
        }
    
    def add_function_key(self, key: str, description: str, callback: Callable):
        """
        Добавить функциональную клавишу
        
        Args:
            key: Обозначение клавиши (F1, F2, ...)
            description: Описание функции
            callback: Функция-обработчик
        """
        self.function_keys[key] = (description, callback)
    
    def get_variable(self, name: str) -> Any:
        """Получить значение переменной"""
        return self.variables[name]['value'] if name in self.variables else None
    
    def set_variable(self, name: str, value: Any):
        """Установить значение переменной с проверкой диапазона"""
        if name in self.variables:
            var_info = self.variables[name]
            
            # Проверка типа и диапазона
            try:
                if var_info['type'] == int:
                    value = int(value)
                elif var_info['type'] == float:
                    value = float(value)
                
                if var_info['min'] is not None and value < var_info['min']:
                    value = var_info['min']
                if var_info['max'] is not None and value > var_info['max']:
                    value = var_info['max']
                
                var_info['value'] = value
            except (ValueError, TypeError):
                pass  # Сохраняем старое значение при ошибке
    
    def draw_panel(self):
        """Отрисовка левой панели с переменными"""
        # Фон панели
        pygame.draw.rect(self.screen, self.COLORS['panel_bg'],
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height))
        
        # Заголовок панели
        title = "НАСТРОЙКИ"
        title_surf = self.font_bold.render(title, False, self.COLORS['highlight'])
        self.screen.blit(title_surf, (self.panel_x + 10, self.panel_y + 10))
        
        # Список переменных
        var_list = list(self.variables.items())
        max_display = min(15, len(var_list))  # Максимум 15 строк на экране
        
        for i in range(max_display):
            if i >= len(var_list):
                break
                
            var_name, var_info = var_list[i]
            y_pos = self.panel_y + 50 + i * 30
            
            # Выделение выбранной строки
            if i == self.selected_index and self.active_panel == "variables":
                pygame.draw.rect(self.screen, self.COLORS['selected'],
                               (self.panel_x + 5, y_pos - 3, self.panel_width - 10, 26))
            
            # Имя переменной
            name_text = var_info.get('display_name', var_name)
            name_surf = self.font.render(f"{name_text:<20}", False, 
                                        self.COLORS['highlight'] if i == self.selected_index 
                                        else self.COLORS['text'])
            self.screen.blit(name_surf, (self.panel_x + 10, y_pos))
            
            # Значение переменной
            value_color = self.COLORS['active'] if (i == self.selected_index and self.editing) else self.COLORS['text']
            value_text = str(var_info['value'])
            
            # Если редактируем эту переменную, показываем буфер ввода
            if i == self.selected_index and self.editing:
                value_text = self.input_buffer + "_"
            
            value_surf = self.font.render(f"{value_text:>15}", False, value_color)
            self.screen.blit(value_surf, (self.panel_x + 250, y_pos))
    
    def draw_function_keys(self):
        """Отрисовка панели функциональных клавиш"""
        # Линия разделения
        pygame.draw.line(self.screen, self.COLORS['border'],
                        (20, self.func_keys_y - 20),
                        (self.width - 20, self.func_keys_y - 20), 2)
        
        # Функциональные клавиши
        keys_per_row = 4
        key_width = self.width // keys_per_row
        
        for idx, (key, (desc, _)) in enumerate(self.function_keys.items()):
            if idx >= 8:  # Ограничим 8 клавишами
                break
                
            row = idx // keys_per_row
            col = idx % keys_per_row
            
            x_pos = 20 + col * key_width
            y_pos = self.func_keys_y + row * 30
            
            # Отображение клавиши
            key_text = f"{key}: {desc}"
            color = self.COLORS['func_keys'] if self.active_panel == "func_keys" and idx == self.selected_index else self.COLORS['text']
            key_surf = self.font.render(key_text, False, color)
            self.screen.blit(key_surf, (x_pos, y_pos))
    
    def draw(self):
        """Основной метод отрисовки GUI"""
        # Очистка экрана
        self.screen.fill(self.COLORS['bg'])
        
        # Отрисовка панелей
        self.draw_panel()
        self.draw_function_keys()
        
        # Инструкция
        help_text = "TAB: переключить панель | ENTER: выбрать/подтвердить | ESC: отмена"
        help_surf = self.font.render(help_text, False, self.COLORS['text'])
        self.screen.blit(help_surf, (20, self.height - 30))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий ввода
        
        Returns:
            True если событие обработано GUI, False если нужно передать дальше
        """
        if event.type == pygame.KEYDOWN:
            var_list = list(self.variables.items())
            
            if self.editing:
                # Режим редактирования значения
                return self._handle_editing(event, var_list)
            else:
                # Обычный режим навигации
                return self._handle_navigation(event, var_list)
        
        return False
    
    def _handle_editing(self, event: pygame.event.Event, var_list: List) -> bool:
        """Обработка событий в режиме редактирования"""
        if event.key == pygame.K_RETURN:
            # Подтверждение ввода
            self._finish_editing(var_list)
            return True
            
        elif event.key == pygame.K_ESCAPE:
            # Отмена редактирования
            self.editing = False
            self.input_buffer = ""
            return True
            
        elif event.key == pygame.K_BACKSPACE:
            # Удаление символа
            self.input_buffer = self.input_buffer[:-1]
            return True
            
        elif event.key in (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                          pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
            # Ввод цифр
            digit = event.key - pygame.K_0
            self.input_buffer += str(digit)
            return True
            
        elif event.key == pygame.K_MINUS and not self.input_buffer:
            # Минус для отрицательных чисел
            self.input_buffer = "-"
            return True
            
        elif event.key == pygame.K_PERIOD and float in [v['type'] for v in self.variables.values()]:
            # Точка для дробных чисел
            if "." not in self.input_buffer:
                self.input_buffer += "."
            return True
        
        return False
    
    def _handle_navigation(self, event: pygame.event.Event, var_list: List) -> bool:
        """Обработка событий в режиме навигации"""
        if event.key == pygame.K_TAB:
            # Переключение между панелями
            self.active_panel = "func_keys" if self.active_panel == "variables" else "variables"
            self.selected_index = 0
            return True
            
        elif event.key == pygame.K_UP:
            # Перемещение вверх
            max_index = len(var_list) - 1 if self.active_panel == "variables" else min(7, len(self.function_keys) - 1)
            self.selected_index = max(0, self.selected_index - 1)
            return True
            
        elif event.key == pygame.K_DOWN:
            # Перемещение вниз
            max_index = len(var_list) - 1 if self.active_panel == "variables" else min(7, len(self.function_keys) - 1)
            self.selected_index = min(max_index, self.selected_index + 1)
            return True
            
        elif event.key == pygame.K_RETURN:
            # Активация выбранного элемента
            if self.active_panel == "variables" and var_list:
                var_name, var_info = var_list[self.selected_index]
                if not var_info['readonly']:
                    # Начало редактирования
                    self.editing = True
                    self.input_buffer = str(var_info['value'])
                    return True
            elif self.active_panel == "func_keys":
                # Вызов callback функции
                func_keys_list = list(self.function_keys.items())
                if self.selected_index < len(func_keys_list):
                    key, (desc, callback) = func_keys_list[self.selected_index]
                    callback()
                    return True
        
        return False
    
    def _finish_editing(self, var_list: List):
        """Завершение редактирования и сохранение значения"""
        if var_list and self.selected_index < len(var_list):
            var_name, var_info = var_list[self.selected_index]
            
            if self.input_buffer:  # Если что-то введено
                self.set_variable(var_name, self.input_buffer)
            
            self.editing = False
            self.input_buffer = ""
    
    def update(self):
        """Обновление состояния GUI (пустой метод для совместимости)"""
        pass
    
    def run(self):
        """Запуск основного цикла GUI (для тестирования)"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    self.handle_event(event)
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)


# Пример использования
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("BIOS/Norton Commander Style GUI")
    
    # Создание GUI
    gui = BIOSStyleGUI(screen)
    
    # Добавление переменных
    gui.add_variable("Speed", 50, min_val=0, max_val=100)
    gui.add_variable("Power", 75.5, float, 0.0, 100.0)
    gui.add_variable("Temperature", 25, min_val=-20, max_val=50)
    gui.add_variable("State", "Активно", str)
    gui.add_variable("Mode", 1, min_val=1, max_val=5)
    gui.add_variable("Timeout", 30, min_val=1, max_val=300)
    
    # Пример функции для callback
    def save_settings():
        print("Сохранение настроек...")
        for name, info in gui.variables.items():
            print(f"{name}: {info['value']}")
    
    def reset_settings():
        print("Reset settings")
        gui.set_variable("speed", 50)
        gui.set_variable("power", 75.5)
        gui.set_variable("temperature", 25)
    
    def exit_app():
        pygame.quit()
        sys.exit()
    
    # Добавление функциональных клавиш
    gui.add_function_key("F1", "Save", save_settings)
    gui.add_function_key("F2", "Load", lambda: print("Загрузка..."))
    gui.add_function_key("F3", "Reset", reset_settings)
    gui.add_function_key("F4", "Exit", exit_app)
    gui.add_function_key("F5", "Test", lambda: print("Тестовая функция"))
    
    # Запуск основного цикла
    gui.run()