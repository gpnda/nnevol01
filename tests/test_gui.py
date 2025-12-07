import pygame
import pygame.gfxdraw
import math
from typing import Dict, List, Tuple, Optional, Callable, Any

class RetroTechGUI:
    """Графический интерфейс в стиле ретро-техно"""
    
    # Цветовая палитра в стиле ретро-техно
    COLORS = {
        'background': (5, 5, 15),
        'panel': (10, 15, 30),
        'panel_light': (20, 30, 50),
        'border': (0, 200, 255),
        'border_glow': (0, 150, 255, 100),
        'text': (0, 255, 200),
        'text_glow': (100, 255, 230),
        'accent': (255, 0, 150),
        'accent_glow': (255, 100, 180),
        'warning': (255, 100, 0),
        'disabled': (80, 100, 120)
    }
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.elements = []
        self.active_element = None
        self.font = None
        self.small_font = None
        self.last_mouse_pos = (0, 0)
        self.grid_size = 20
        self.show_grid = False
        
        # Инициализация шрифтов
        self._init_fonts()
        
        # Регистр клавиш для комбинаций
        self.key_modifiers = {
            'ctrl': False,
            'shift': False,
            'alt': False
        }
        
        # Комбинации клавиш
        self.key_combinations = {}
        
    def _init_fonts(self):
        """Инициализация шрифтов в ретро-стиле"""
        try:
            # Попробуем загрузить пиксельный шрифт
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)
            # Симуляция пиксельного шрифта через растровый эффект
            self.font.set_bold(True)
            self.small_font.set_bold(True)
        except:
            # Запасной вариант
            self.font = pygame.font.SysFont('courier', 20, bold=True)
            self.small_font = pygame.font.SysFont('courier', 14, bold=True)
    
    def add_element(self, element_type: str, **kwargs) -> Dict:
        """Добавление нового элемента GUI"""
        element = {
            'type': element_type,
            'id': kwargs.get('id', f'elem_{len(self.elements)}'),
            'rect': pygame.Rect(kwargs['x'], kwargs['y'], 
                              kwargs.get('width', 200), 
                              kwargs.get('height', 40)),
            'label': kwargs.get('label', ''),
            'value': kwargs.get('value', 0),
            'min': kwargs.get('min', 0),
            'max': kwargs.get('max', 100),
            'step': kwargs.get('step', 1),
            'options': kwargs.get('options', []),
            'callback': kwargs.get('callback', None),
            'enabled': kwargs.get('enabled', True),
            'visible': kwargs.get('visible', True),
            'key_combo': kwargs.get('key_combo', None),  # (modifier, key)
            'hover': False,
            'dragging': False,
            'style': kwargs.get('style', {})
        }
        
        if element['key_combo']:
            self.key_combinations[element['key_combo']] = element['id']
            
        self.elements.append(element)
        return element
    
    def draw_grid(self):
        """Отрисовка сетки в ретро-стиле"""
        width, height = self.screen.get_size()
        
        # Вертикальные линии
        for x in range(0, width, self.grid_size):
            alpha = 20 if x % (self.grid_size * 5) == 0 else 10
            pygame.draw.line(self.screen, (0, 100, 200, alpha), 
                           (x, 0), (x, height), 1)
        
        # Горизонтальные линии
        for y in range(0, height, self.grid_size):
            alpha = 20 if y % (self.grid_size * 5) == 0 else 10
            pygame.draw.line(self.screen, (0, 100, 200, alpha), 
                           (0, y), (width, y), 1)
        
        # Угловые маркеры
        corners = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        for corner in corners:
            pygame.draw.line(self.screen, self.COLORS['border'], 
                           corner, (corner[0] + 10, corner[1]), 2)
            pygame.draw.line(self.screen, self.COLORS['border'], 
                           corner, (corner[0], corner[1] + 10), 2)
    
    def draw_slider(self, element: Dict):
        """Отрисовка слайдера"""
        if not element['visible']:
            return
            
        rect = element['rect']
        value = element['value']
        min_val = element['min']
        max_val = element['max']
        
        # Основная панель
        self._draw_panel(rect, element['hover'], element['enabled'])
        
        # Вычисление позиции ползунка
        slider_width = 20
        range_val = max_val - min_val
        pos_x = rect.x + 10 + (rect.width - 20 - slider_width) * (value - min_val) / range_val
        
        # Трек слайдера
        track_rect = pygame.Rect(rect.x + 10, rect.y + rect.height//2 - 2, 
                               rect.width - 20, 4)
        pygame.draw.rect(self.screen, self.COLORS['border'], track_rect)
        
        # Ползунок
        slider_rect = pygame.Rect(pos_x, rect.y + rect.height//2 - 10, 
                                slider_width, 20)
        
        # Эффект свечения при наведении
        if element['hover'] or element['dragging']:
            self._draw_glow(slider_rect, self.COLORS['accent_glow'], 10)
        
        # Рисуем ползунок с градиентом
        self._draw_retro_button(slider_rect, element['hover'] or element['dragging'], 
                              element['enabled'], is_slider=True)
        
        # Значение
        value_text = self.small_font.render(f"{value:.1f}", True, 
                                          self.COLORS['text'])
        self.screen.blit(value_text, (rect.x + rect.width + 10, rect.y + 10))
        
        # Метка
        if element['label']:
            label = self.font.render(element['label'], True, 
                                   self.COLORS['text'] if element['enabled'] 
                                   else self.COLORS['disabled'])
            self.screen.blit(label, (rect.x, rect.y - 25))
    
    def draw_button(self, element: Dict):
        """Отрисовка кнопки"""
        if not element['visible']:
            return
            
        rect = element['rect']
        
        # Эффект свечения при наведении
        if element['hover']:
            self._draw_glow(rect.inflate(10, 10), 
                          self.COLORS['border_glow'], 15)
        
        # Рисуем кнопку
        self._draw_retro_button(rect, element['hover'], element['enabled'])
        
        # Текст кнопки
        text = self.font.render(element['label'], True, 
                              self.COLORS['text'] if element['enabled'] 
                              else self.COLORS['disabled'])
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
        
        # Отображение сочетания клавиш
        if element['key_combo']:
            mod, key = element['key_combo']
            key_text = self._get_key_combo_text(mod, key)
            key_surf = self.small_font.render(key_text, True, 
                                            self.COLORS['accent'])
            self.screen.blit(key_surf, (rect.right + 10, rect.centery - 8))
    
    def draw_toggle(self, element: Dict):
        """Отрисовка переключателя"""
        if not element['visible']:
            return
            
        rect = element['rect']
        is_on = bool(element['value'])
        
        # Основная панель
        self._draw_panel(rect, element['hover'], element['enabled'])
        
        # Переключатель
        toggle_rect = pygame.Rect(rect.x + 5, rect.y + 5, 
                                rect.height - 10, rect.height - 10)
        
        if is_on:
            # Включенное состояние
            pygame.draw.rect(self.screen, self.COLORS['accent'], toggle_rect)
            pygame.draw.rect(self.screen, self.COLORS['text'], toggle_rect, 2)
            
            # Эффект свечения
            if element['hover']:
                self._draw_glow(toggle_rect, self.COLORS['accent_glow'], 10)
        else:
            # Выключенное состояние
            pygame.draw.rect(self.screen, self.COLORS['panel_light'], toggle_rect)
            pygame.draw.rect(self.screen, self.COLORS['border'], toggle_rect, 2)
        
        # Метка
        if element['label']:
            label = self.font.render(element['label'], True, 
                                   self.COLORS['text'] if element['enabled'] 
                                   else self.COLORS['disabled'])
            self.screen.blit(label, (rect.x + rect.height + 10, 
                                   rect.y + rect.height//2 - 10))
    
    def draw_dropdown(self, element: Dict):
        """Отрисовка выпадающего списка"""
        if not element['visible']:
            return
            
        rect = element['rect']
        options = element['options']
        selected = element['value']
        
        # Основная панель
        self._draw_panel(rect, element['hover'], element['enabled'])
        
        # Текущее значение
        if 0 <= selected < len(options):
            text = self.font.render(options[selected], True, 
                                  self.COLORS['text'])
            self.screen.blit(text, (rect.x + 10, rect.y + rect.height//2 - 10))
        
        # Стрелка
        arrow_points = [
            (rect.right - 20, rect.centery - 5),
            (rect.right - 10, rect.centery - 5),
            (rect.right - 15, rect.centery + 5)
        ]
        pygame.draw.polygon(self.screen, self.COLORS['border'], arrow_points)
        
        # Метка
        if element['label']:
            label = self.font.render(element['label'], True, 
                                   self.COLORS['text'] if element['enabled'] 
                                   else self.COLORS['disabled'])
            self.screen.blit(label, (rect.x, rect.y - 25))
    
    def _draw_panel(self, rect: pygame.Rect, hover: bool, enabled: bool):
        """Отрисовка панели элемента"""
        # Основной прямоугольник
        color = self.COLORS['panel_light'] if hover else self.COLORS['panel']
        if not enabled:
            color = tuple(c // 2 for c in color)
        
        pygame.draw.rect(self.screen, color, rect)
        
        # Рамка с эффектом неона
        border_color = self.COLORS['border'] if enabled else self.COLORS['disabled']
        pygame.draw.rect(self.screen, border_color, rect, 2)
        
        # Угловые акценты
        corner_len = 8
        # Левый верхний
        pygame.draw.line(self.screen, border_color, 
                        rect.topleft, (rect.left + corner_len, rect.top), 2)
        pygame.draw.line(self.screen, border_color, 
                        rect.topleft, (rect.left, rect.top + corner_len), 2)
        # Правый верхний
        pygame.draw.line(self.screen, border_color, 
                        rect.topright, (rect.right - corner_len, rect.top), 2)
        pygame.draw.line(self.screen, border_color, 
                        rect.topright, (rect.right, rect.top + corner_len), 2)
        # Левый нижний
        pygame.draw.line(self.screen, border_color, 
                        rect.bottomleft, (rect.left + corner_len, rect.bottom), 2)
        pygame.draw.line(self.screen, border_color, 
                        rect.bottomleft, (rect.left, rect.bottom - corner_len), 2)
        # Правый нижний
        pygame.draw.line(self.screen, border_color, 
                        rect.bottomright, (rect.right - corner_len, rect.bottom), 2)
        pygame.draw.line(self.screen, border_color, 
                        rect.bottomright, (rect.right, rect.bottom - corner_len), 2)
    
    def _draw_retro_button(self, rect: pygame.Rect, hover: bool, 
                          enabled: bool, is_slider: bool = False):
        """Отрисовка кнопки в ретро-стиле"""
        if not enabled:
            color = self.COLORS['disabled']
        elif hover:
            color = self.COLORS['accent']
        else:
            color = self.COLORS['border']
        
        # Основная форма
        pygame.draw.rect(self.screen, color, rect)
        
        # Внутренняя рамка
        inner_color = (min(color[0] + 50, 255), 
                      min(color[1] + 50, 255), 
                      min(color[2] + 50, 255))
        pygame.draw.rect(self.screen, inner_color, rect.inflate(-4, -4), 2)
        
        # Эффект 3D для кнопок (не для слайдеров)
        if not is_slider:
            # Верхняя и левая грани (свет)
            pygame.draw.line(self.screen, inner_color, 
                           rect.topleft, rect.topright, 2)
            pygame.draw.line(self.screen, inner_color, 
                           rect.topleft, rect.bottomleft, 2)
            # Нижняя и правая грани (тень)
            shadow_color = tuple(max(c - 50, 0) for c in color)
            pygame.draw.line(self.screen, shadow_color, 
                           rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, shadow_color, 
                           rect.topright, rect.bottomright, 2)
    
    def _draw_glow(self, rect: pygame.Rect, color: Tuple, intensity: int):
        """Отрисовка эффекта свечения"""
        # Проверяем, есть ли альфа-канал в цвете
        if len(color) == 4:
            r, g, b, base_alpha = color
        else:
            r, g, b = color
            base_alpha = 255
        
        for i in range(intensity, 0, -1):
            alpha = base_alpha // intensity * i
            glow_rect = rect.inflate(i * 2, i * 2)
            
            # Создаем поверхность для свечения
            glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (r, g, b, alpha), 
                           (0, 0, *glow_rect.size), border_radius=5)
            
            self.screen.blit(glow_surf, glow_rect)
    
    def _get_key_combo_text(self, modifier: str, key: int) -> str:
        """Преобразование комбинации клавиш в текст"""
        mod_text = ""
        if 'ctrl' in modifier:
            mod_text += "Ctrl+"
        if 'shift' in modifier:
            mod_text += "Shift+"
        if 'alt' in modifier:
            mod_text += "Alt+"
        
        key_text = pygame.key.name(key).upper()
        return mod_text + key_text
    
    def handle_events(self, events: List[pygame.event.Event]):
        """Обработка событий"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        # Обновление состояния наведения
        for element in self.elements:
            if not element['visible'] or not element['enabled']:
                element['hover'] = False
                continue
                
            element['hover'] = element['rect'].collidepoint(mouse_pos)
            
            # Если элемент активен и мышь перемещается при зажатой кнопке
            if element['dragging'] and mouse_pressed[0]:
                self._handle_drag(element, mouse_pos)
        
        # Обработка событий
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event)
            elif event.type == pygame.KEYUP:
                self._handle_key_up(event)
        
        self.last_mouse_pos = mouse_pos
    
    def _handle_mouse_down(self, event: pygame.event.Event):
        """Обработка нажатия мыши"""
        for element in self.elements:
            if not element['visible'] or not element['enabled']:
                continue
                
            if element['rect'].collidepoint(event.pos):
                self.active_element = element['id']
                
                if element['type'] == 'slider':
                    element['dragging'] = True
                    self._update_slider_value(element, event.pos[0])
                elif element['type'] == 'button':
                    if element['callback']:
                        element['callback'](element)
                elif element['type'] == 'toggle':
                    element['value'] = not element['value']
                    if element['callback']:
                        element['callback'](element)
                elif element['type'] == 'dropdown':
                    # Здесь можно реализовать раскрытие списка
                    pass
                
                break
    
    def _handle_mouse_up(self, event: pygame.event.Event):
        """Обработка отпускания мыши"""
        for element in self.elements:
            if element['type'] == 'slider':
                element['dragging'] = False
        self.active_element = None
    
    def _handle_drag(self, element: Dict, mouse_pos: Tuple[int, int]):
        """Обработка перетаскивания"""
        if element['type'] == 'slider':
            self._update_slider_value(element, mouse_pos[0])
    
    def _update_slider_value(self, element: Dict, mouse_x: int):
        """Обновление значения слайдера"""
        rect = element['rect']
        slider_width = 20
        usable_width = rect.width - 20 - slider_width
        
        # Вычисляем новое значение
        relative_x = max(0, min(usable_width, mouse_x - rect.x - 10 - slider_width/2))
        value_range = element['max'] - element['min']
        new_value = element['min'] + (relative_x / usable_width) * value_range
        
        # Применяем шаг
        step = element['step']
        if step > 0:
            new_value = round(new_value / step) * step
        
        # Обновляем значение
        element['value'] = max(element['min'], min(element['max'], new_value))
        
        # Вызываем callback
        if element['callback']:
            element['callback'](element)
    
    def _handle_key_down(self, event: pygame.event.Event):
        """Обработка нажатия клавиш"""
        # Обновление модификаторов
        self.key_modifiers['ctrl'] = event.mod & pygame.KMOD_CTRL
        self.key_modifiers['shift'] = event.mod & pygame.KMOD_SHIFT
        self.key_modifiers['alt'] = event.mod & pygame.KMOD_ALT
        
        # Проверка комбинаций клавиш
        current_mods = []
        if self.key_modifiers['ctrl']:
            current_mods.append('ctrl')
        if self.key_modifiers['shift']:
            current_mods.append('shift')
        if self.key_modifiers['alt']:
            current_mods.append('alt')
        
        mod_key = ('+'.join(current_mods), event.key)
        
        if mod_key in self.key_combinations:
            element_id = self.key_combinations[mod_key]
            for element in self.elements:
                if element['id'] == element_id and element['enabled'] and element['visible']:
                    if element['type'] == 'button' and element['callback']:
                        element['callback'](element)
                    elif element['type'] == 'toggle':
                        element['value'] = not element['value']
                        if element['callback']:
                            element['callback'](element)
                    break
    
    def _handle_key_up(self, event: pygame.event.Event):
        """Обработка отпускания клавиш"""
        # Сброс модификаторов при отпускании специальных клавиш
        if event.key in [pygame.K_LCTRL, pygame.K_RCTRL]:
            self.key_modifiers['ctrl'] = False
        elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
            self.key_modifiers['shift'] = False
        elif event.key in [pygame.K_LALT, pygame.K_RALT]:
            self.key_modifiers['alt'] = False
    
    def draw(self):
        """Отрисовка всех элементов GUI"""
        # Отрисовка сетки (опционально)
        if self.show_grid:
            self.draw_grid()
        
        # Отрисовка элементов по типам
        for element in self.elements:
            if not element['visible']:
                continue
                
            if element['type'] == 'slider':
                self.draw_slider(element)
            elif element['type'] == 'button':
                self.draw_button(element)
            elif element['type'] == 'toggle':
                self.draw_toggle(element)
            elif element['type'] == 'dropdown':
                self.draw_dropdown(element)
    
    def get_element(self, element_id: str) -> Optional[Dict]:
        """Получение элемента по ID"""
        for element in self.elements:
            if element['id'] == element_id:
                return element
        return None
    
    def update_element(self, element_id: str, **kwargs):
        """Обновление параметров элемента"""
        element = self.get_element(element_id)
        if element:
            for key, value in kwargs.items():
                if key in element:
                    element[key] = value
    
    def remove_element(self, element_id: str):
        """Удаление элемента"""
        self.elements = [e for e in self.elements if e['id'] != element_id]
        
        # Удаление из комбинаций клавиш
        to_remove = []
        for combo, eid in self.key_combinations.items():
            if eid == element_id:
                to_remove.append(combo)
        for combo in to_remove:
            del self.key_combinations[combo]


# Пример использования
def example_usage():
    """Пример использования GUI модуля"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Retro Tech GUI Demo")
    clock = pygame.time.Clock()
    
    # Создание GUI
    gui = RetroTechGUI(screen)
    gui.show_grid = True
    
    # Callback функции
    def slider_changed(element):
        print(f"Slider '{element['id']}' changed to: {element['value']}")
    
    def button_clicked(element):
        print(f"Button '{element['label']}' clicked!")
    
    def toggle_changed(element):
        state = "ON" if element['value'] else "OFF"
        print(f"Toggle '{element['label']}' switched {state}")
    
    # Добавление элементов
    gui.add_element(
        'slider',
        id='volume',
        x=100, y=100,
        width=300, height=30,
        label='Volume',
        min=0, max=100, value=50, step=1,
        callback=slider_changed,
        key_combo=('ctrl', pygame.K_v)  # Ctrl+V для управления
    )
    
    gui.add_element(
        'slider',
        id='brightness',
        x=100, y=150,
        width=300, height=30,
        label='Brightness',
        min=0, max=100, value=75, step=5,
        callback=slider_changed
    )
    
    gui.add_element(
        'button',
        id='apply_btn',
        x=100, y=220,
        width=150, height=40,
        label='APPLY',
        callback=button_clicked,
        key_combo=('ctrl+shift', pygame.K_a)  # Ctrl+Shift+A
    )
    
    gui.add_element(
        'toggle',
        id='power',
        x=100, y=280,
        width=200, height=40,
        label='Power',
        value=True,
        callback=toggle_changed,
        key_combo=('ctrl', pygame.K_p)  # Ctrl+P
    )
    
    gui.add_element(
        'toggle',
        id='wifi',
        x=100, y=330,
        width=200, height=40,
        label='Wi-Fi',
        value=False,
        callback=toggle_changed
    )
    
    gui.add_element(
        'dropdown',
        id='resolution',
        x=100, y=380,
        width=200, height=40,
        label='Resolution',
        options=['1920x1080', '1600x900', '1366x768', '1280x720'],
        value=0
    )
    
    # Главный цикл
    running = True
    while running:
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g and event.mod & pygame.KMOD_CTRL:
                    gui.show_grid = not gui.show_grid
        
        # Обновление GUI
        gui.handle_events(events)
        
        # Отрисовка
        screen.fill(gui.COLORS['background'])
        gui.draw()
        
        # Отображение подсказки
        hint = gui.font.render("Use Ctrl+V, Ctrl+P, Ctrl+Shift+A for shortcuts", 
                             True, gui.COLORS['text_glow'])
        screen.blit(hint, (100, 500))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    example_usage()