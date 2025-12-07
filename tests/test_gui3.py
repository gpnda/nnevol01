import pygame
import sys

# Инициализация PyGame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 16
BUTTON_HEIGHT = 24

# Цвета (биосовая палитра)
COLORS = {
    'bg': (0, 0, 0),          # черный фон
    'text': (170, 170, 170),  # светло-серый текст
    'selected': (0, 85, 0),   # зеленый выделенный
    'border': (85, 85, 85),   # серые рамки
    'highlight': (170, 170, 0), # желтый заголовок
    'button': (0, 85, 85),    # бирюзовые кнопки
    'input': (0, 42, 0)       # темно-зеленый ввод
}

class BIOSVariable:
    """Класс для переменной с настраиваемым значением"""
    def __init__(self, name, value, min_val=0, max_val=100):
        self.name = name
        self.value = value
        self.default = value
        self.min = min_val
        self.max = max_val
        self.editing = False
        self.input_buffer = ""
        
    def start_edit(self):
        self.editing = True
        self.input_buffer = str(self.value)
        
    def cancel_edit(self):
        self.editing = False
        self.input_buffer = ""
        
    def confirm_edit(self):
        try:
            new_val = int(self.input_buffer)
            if self.min <= new_val <= self.max:
                self.value = new_val
        except ValueError:
            pass
        self.editing = False
        self.input_buffer = ""
        
    def reset(self):
        self.value = self.default

class BIOSGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BIOS/Norton Commander Interface")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('couriernew', FONT_SIZE, bold=True)
        
        # Переменные для левой панели
        self.variables = [
            BIOSVariable("CPU Frequency", 3200, 800, 5000),
            BIOSVariable("Memory Speed", 2666, 1600, 4800),
            BIOSVariable("Voltage", 1.35, 1.0, 1.5),
            BIOSVariable("Fan Speed", 1200, 800, 3000),
            BIOSVariable("Boot Order", 1, 1, 5),
            BIOSVariable("Timeout", 10, 1, 60),
            BIOSVariable("SATA Mode", 1, 1, 3),
            BIOSVariable("Power Save", 1, 1, 3)
        ]
        
        # Текущий выбор
        self.selected_index = 0
        self.active_panel = 'left'  # 'left' или 'function_keys'
        
        # Функциональные клавиши
        self.function_keys = [
            ("F1", "Help"),
            ("F2", "Save"),
            ("F3", "Load"),
            ("F4", "Default"),
            ("F5", "Reset"),
            ("F6", "Test"),
            ("F7", "Backup"),
            ("F8", "Restore"),
            ("F9", "Info"),
            ("F10", "Exit")
        ]
        
        # Вспомогательный текст
        self.help_text = [
            "↑↓: Navigate    Enter: Edit/Confirm    Tab: Switch Panel",
            "Esc: Cancel    F1: Help    F10: Exit"
        ]
        
    def draw_text(self, text, x, y, color=COLORS['text'], bg_color=None):
        """Отрисовка текста с заданным цветом"""
        text_surface = self.font.render(text, True, color)
        if bg_color:
            bg_rect = pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
            pygame.draw.rect(self.screen, bg_color, bg_rect)
        self.screen.blit(text_surface, (x, y))
        return text_surface.get_width()
        
    def draw_panel(self, x, y, width, height, title):
        """Отрисовка панели с рамкой"""
        # Рамка
        pygame.draw.rect(self.screen, COLORS['border'], (x, y, width, height), 1)
        
        # Заголовок
        pygame.draw.rect(self.screen, COLORS['border'], (x, y-2, len(title)*FONT_SIZE//2 + 10, FONT_SIZE + 4))
        self.draw_text(title, x+5, y, COLORS['highlight'], COLORS['bg'])
        
        return pygame.Rect(x, y, width, height)
        
    def draw_variables_panel(self):
        """Отрисовка левой панели с переменными"""
        panel_rect = self.draw_panel(20, 50, 400, 400, " SYSTEM SETTINGS ")
        
        y_offset = 30
        for i, var in enumerate(self.variables):
            y = panel_rect.y + y_offset + i * 30
            
            # Фон для выделенного элемента
            if i == self.selected_index and self.active_panel == 'left':
                pygame.draw.rect(self.screen, COLORS['selected'], 
                               (panel_rect.x + 5, y, panel_rect.width - 10, 25))
            
            # Имя переменной
            self.draw_text(var.name.ljust(20), panel_rect.x + 10, y + 5)
            
            # Значение или поле ввода
            if var.editing:
                # Поле ввода
                input_bg = pygame.Rect(panel_rect.x + 210, y + 3, 100, 20)
                pygame.draw.rect(self.screen, COLORS['input'], input_bg)
                self.draw_text(var.input_buffer + "_", panel_rect.x + 215, y + 5, COLORS['text'])
            else:
                # Отображение значения
                value_text = f"[{var.value}]"
                self.draw_text(value_text, panel_rect.x + 215, y + 5, COLORS['highlight'])
            
            # Минимальное/максимальное значение
            range_text = f"({var.min}-{var.max})"
            self.draw_text(range_text, panel_rect.x + 320, y + 5, COLORS['border'])
            
    def draw_function_keys(self):
        """Отрисовка панели функциональных клавиш"""
        panel_rect = self.draw_panel(20, 470, SCREEN_WIDTH - 40, 100, " FUNCTION KEYS ")
        
        # Распределяем клавиши по рядам
        keys_per_row = 5
        for i, (key, label) in enumerate(self.function_keys):
            row = i // keys_per_row
            col = i % keys_per_row
            
            x = panel_rect.x + 20 + col * 150
            y = panel_rect.y + 30 + row * 30
            
            # Подсветка активной панели
            bg_color = None
            if self.active_panel == 'function_keys' and i == self.selected_index % len(self.function_keys):
                bg_color = COLORS['button']
                
            # Клавиша
            self.draw_text(key + ":", x, y, COLORS['highlight'], bg_color)
            # Описание
            self.draw_text(label, x + 40, y, COLORS['text'], bg_color)
            
    def draw_status_bar(self):
        """Отрисовка строки состояния"""
        pygame.draw.rect(self.screen, COLORS['border'], (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))
        
        # Текущая выбранная переменная
        if self.active_panel == 'left' and self.selected_index < len(self.variables):
            var = self.variables[self.selected_index]
            status = f"Selected: {var.name} = {var.value} (Range: {var.min}-{var.max})"
            self.draw_text(status, 10, SCREEN_HEIGHT - 25, COLORS['text'])
            
        # Подсказки
        hints = "TAB: Switch Panel | ENTER: Edit/Confirm | ESC: Cancel | F10: Exit"
        self.draw_text(hints, SCREEN_WIDTH - len(hints)*FONT_SIZE//2 - 10, SCREEN_HEIGHT - 25, COLORS['border'])
        
    def draw(self):
        """Отрисовка всего интерфейса"""
        self.screen.fill(COLORS['bg'])
        
        # Заголовок
        self.draw_text("BIOS SETUP UTILITY", SCREEN_WIDTH // 2 - 100, 10, COLORS['highlight'])
        self.draw_text("v2.0 (C) 1992-2024 Phoenix Technologies Ltd.", SCREEN_WIDTH // 2 - 150, 30, COLORS['border'])
        
        # Панели
        self.draw_variables_panel()
        self.draw_function_keys()
        self.draw_status_bar()
        
        pygame.display.flip()
        
    def handle_input(self):
        """Обработка ввода с клавиатуры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                current_var = self.variables[self.selected_index] if self.selected_index < len(self.variables) else None
                
                # Режим редактирования переменной
                if current_var and current_var.editing:
                    if event.key == pygame.K_RETURN:
                        current_var.confirm_edit()
                    elif event.key == pygame.K_ESCAPE:
                        current_var.cancel_edit()
                    elif event.key == pygame.K_BACKSPACE:
                        current_var.input_buffer = current_var.input_buffer[:-1]
                    elif event.unicode.isdigit() or event.unicode == '.':
                        current_var.input_buffer += event.unicode
                    return True
                    
                # Навигация по панелям
                if event.key == pygame.K_TAB:
                    self.active_panel = 'function_keys' if self.active_panel == 'left' else 'left'
                    self.selected_index = 0
                    
                # Управление в левой панели
                elif self.active_panel == 'left':
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.variables)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.variables)
                    elif event.key == pygame.K_RETURN:
                        if current_var:
                            current_var.start_edit()
                            
                # Управление в панели функциональных клавиш
                elif self.active_panel == 'function_keys':
                    if event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 5)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.function_keys) - 1, self.selected_index + 5)
                    elif event.key == pygame.K_LEFT:
                        self.selected_index = max(0, self.selected_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_index = min(len(self.function_keys) - 1, self.selected_index + 1)
                    elif event.key == pygame.K_RETURN:
                        self.execute_function_key(self.selected_index % len(self.function_keys))
                        
                # Функциональные клавиши (глобальные)
                if event.key == pygame.K_F1:
                    self.show_help()
                elif event.key == pygame.K_F4:
                    self.load_defaults()
                elif event.key == pygame.K_F5:
                    self.reset_settings()
                elif event.key == pygame.K_F10:
                    return False
                    
        return True
        
    def execute_function_key(self, index):
        """Выполнение действия функциональной клавиши"""
        key, label = self.function_keys[index]
        print(f"Pressed {key}: {label}")
        
        # Здесь можно добавить логику для каждой клавиши
        if key == "F2":
            self.save_settings()
        elif key == "F3":
            self.load_settings()
        elif key == "F10":
            pygame.quit()
            sys.exit()
            
    def save_settings(self):
        """Сохранение настроек"""
        print("Settings saved")
        
    def load_settings(self):
        """Загрузка настроек"""
        print("Settings loaded")
        
    def load_defaults(self):
        """Загрузка настроек по умолчанию"""
        for var in self.variables:
            var.reset()
        print("Defaults loaded")
        
    def reset_settings(self):
        """Сброс всех настроек"""
        self.selected_index = 0
        self.active_panel = 'left'
        print("Settings reset")
        
    def show_help(self):
        """Показать справку"""
        print("Help: Use arrow keys to navigate, Enter to edit, Tab to switch panels")
        
    def run(self):
        """Главный цикл"""
        running = True
        while running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = BIOSGUI()
    app.run()