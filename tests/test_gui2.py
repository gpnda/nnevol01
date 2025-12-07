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
        'accent_glow': (255, 100, 180, 100),
        'warning': (255, 100, 0),
        'error': (255, 50, 50),
        'success': (0, 255, 100),
        'disabled': (80, 100, 120),
        'overlay': (0, 0, 0, 180)  # Полупрозрачный оверлей
    }
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.elements = []
        self.popups = []  # Список активных popup-окон
        self.active_element = None
        self.font = None
        self.small_font = None
        self.title_font = None
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
            # Основной шрифт
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)
            self.title_font = pygame.font.Font(None, 32)
            
            # Симуляция пиксельного шрифта
            self.font.set_bold(True)
            self.small_font.set_bold(True)
            self.title_font.set_bold(True)
        except:
            # Запасной вариант
            self.font = pygame.font.SysFont('courier', 20, bold=True)
            self.small_font = pygame.font.SysFont('courier', 14, bold=True)
            self.title_font = pygame.font.SysFont('courier', 28, bold=True)
    
    # ========== ОСНОВНЫЕ МЕТОДЫ ДОБАВЛЕНИЯ ЭЛЕМЕНТОВ ==========
    
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
    
    # ========== МЕТОДЫ POPUP-ОКОН ==========
    
    def show_popup(self, title: str, message: str, 
                  buttons: Optional[List[Dict]] = None,
                  width: int = 400, height: int = 250,
                  popup_type: str = "info") -> str:
        """
        Отображение popup-окна
        
        Args:
            title: Заголовок окна
            message: Сообщение
            buttons: Список кнопок [{'text': 'OK', 'id': 'ok'}]
            width: Ширина окна
            height: Высота окна
            popup_type: Тип окна ('info', 'warning', 'error', 'confirm', 'custom')
            
        Returns:
            ID созданного popup-окна
        """
        # Создаем уникальный ID для popup
        popup_id = f"popup_{len(self.popups)}_{pygame.time.get_ticks()}"
        
        # Определяем тип окна и цвет заголовка
        if popup_type == "warning":
            title_color = self.COLORS['warning']
        elif popup_type == "error":
            title_color = self.COLORS['error']
        elif popup_type == "confirm":
            title_color = self.COLORS['accent']
        else:
            title_color = self.COLORS['text']
        
        # Стандартные кнопки если не указаны
        if buttons is None:
            if popup_type == "confirm":
                buttons = [
                    {'text': 'YES', 'id': 'yes', 'key': pygame.K_y},
                    {'text': 'NO', 'id': 'no', 'key': pygame.K_n}
                ]
            else:
                buttons = [{'text': 'OK', 'id': 'ok', 'key': pygame.K_RETURN}]
        
        # Центрируем окно на экране
        screen_width, screen_height = self.screen.get_size()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Создаем объект popup
        popup = {
            'id': popup_id,
            'title': title,
            'message': message,
            'buttons': buttons,
            'rect': pygame.Rect(x, y, width, height),
            'type': popup_type,
            'title_color': title_color,
            'created_at': pygame.time.get_ticks(),
            'button_elements': []  # Будут созданы при отрисовке
        }
        
        # Добавляем popup в список
        self.popups.append(popup)
        
        # Блокируем взаимодействие с элементами под popup
        for element in self.elements:
            element['enabled'] = False
        
        return popup_id
    
    def show_loading_popup(self, title: str = "Loading...", 
                          message: str = "Please wait",
                          width: int = 300, height: int = 150) -> str:
        """
        Отображение popup-окна с индикатором загрузки
        """
        popup_id = f"loading_{len(self.popups)}_{pygame.time.get_ticks()}"
        
        screen_width, screen_height = self.screen.get_size()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        popup = {
            'id': popup_id,
            'title': title,
            'message': message,
            'rect': pygame.Rect(x, y, width, height),
            'type': 'loading',
            'title_color': self.COLORS['text'],
            'created_at': pygame.time.get_ticks(),
            'progress': 0,  # Прогресс от 0 до 100
            'spinner_angle': 0
        }
        
        self.popups.append(popup)
        
        # Блокируем элементы
        for element in self.elements:
            element['enabled'] = False
            
        return popup_id
    
    def update_loading_popup(self, popup_id: str, progress: Optional[float] = None,
                            message: Optional[str] = None):
        """
        Обновление popup-окна загрузки
        """
        for popup in self.popups:
            if popup['id'] == popup_id and popup['type'] == 'loading':
                if progress is not None:
                    popup['progress'] = max(0, min(100, progress))
                if message is not None:
                    popup['message'] = message
                break
    
    def close_popup(self, popup_id: Optional[str] = None):
        """
        Закрытие popup-окна
        
        Args:
            popup_id: ID окна для закрытия. Если None - закрывает все окна.
        """
        if popup_id is None:
            # Закрываем все окна
            self.popups.clear()
            # Разблокируем элементы
            for element in self.elements:
                element['enabled'] = True
        else:
            # Закрываем конкретное окно
            self.popups = [p for p in self.popups if p['id'] != popup_id]
            
            # Если больше нет popup-окон, разблокируем элементы
            if not self.popups:
                for element in self.elements:
                    element['enabled'] = True
    
    def get_active_popup(self) -> Optional[Dict]:
        """Получение активного popup-окна (последнего в списке)"""
        if self.popups:
            return self.popups[-1]
        return None
    
    # ========== МЕТОДЫ ОТРИСОВКИ ==========
    
    def draw_grid(self):
        """Отрисовка сетки в ретро-стиле"""
        width, height = self.screen.get_size()
        
        # Создаем поверхность для сетки с альфа-каналом
        grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Вертикальные линии
        for x in range(0, width, self.grid_size):
            alpha = 20 if x % (self.grid_size * 5) == 0 else 10
            pygame.draw.line(grid_surface, (0, 100, 200, alpha), 
                           (x, 0), (x, height), 1)
        
        # Горизонтальные линии
        for y in range(0, height, self.grid_size):
            alpha = 20 if y % (self.grid_size * 5) == 0 else 10
            pygame.draw.line(grid_surface, (0, 100, 200, alpha), 
                           (0, y), (width, y), 1)
        
        # Рисуем сетку на экране
        self.screen.blit(grid_surface, (0, 0))
        
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
    
    def draw_popup(self, popup: Dict):
        """Отрисовка popup-окна"""
        rect = popup['rect']
        
        # Оверлей (затемнение фона)
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(self.COLORS['overlay'])
        self.screen.blit(overlay, (0, 0))
        
        # Основное окно
        self._draw_popup_window(rect)
        
        # Заголовок
        title_surf = self.title_font.render(popup['title'], True, popup['title_color'])
        title_rect = title_surf.get_rect(center=(rect.centerx, rect.y + 40))
        
        # Эффект свечения для заголовка
        glow_surf = self.title_font.render(popup['title'], True, 
                                         (*popup['title_color'][:3], 100))
        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            self.screen.blit(glow_surf, 
                           (title_rect.x + offset[0], title_rect.y + offset[1]))
        
        self.screen.blit(title_surf, title_rect)
        
        # Разделитель под заголовком
        pygame.draw.line(self.screen, popup['title_color'],
                        (rect.x + 20, rect.y + 70),
                        (rect.right - 20, rect.y + 70), 2)
        
        # Сообщение
        message_y = rect.y + 90
        max_width = rect.width - 40
        
        # Обработка переноса строк
        words = popup['message'].split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = self.font.render(test_line, True, self.COLORS['text'])
            
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Отображение строк
        for i, line in enumerate(lines):
            line_surf = self.font.render(line, True, self.COLORS['text'])
            line_rect = line_surf.get_rect(center=(rect.centerx, message_y + i * 30))
            self.screen.blit(line_surf, line_rect)
        
        # Отрисовка в зависимости от типа popup
        if popup['type'] == 'loading':
            self._draw_loading_indicator(popup)
        else:
            self._draw_popup_buttons(popup)
    
    def _draw_popup_window(self, rect: pygame.Rect):
        """Отрисовка окна popup"""
        # Основная панель с эффектом свечения
        self._draw_glow(rect.inflate(20, 20), (0, 150, 255, 50), 15)
        
        # Окно
        pygame.draw.rect(self.screen, self.COLORS['panel'], rect)
        pygame.draw.rect(self.screen, self.COLORS['border'], rect, 3)
        
        # Угловые акценты (более крупные для popup)
        corner_len = 12
        corners = [
            (rect.topleft, (rect.left + corner_len, rect.top), (rect.left, rect.top + corner_len)),
            (rect.topright, (rect.right - corner_len, rect.top), (rect.right, rect.top + corner_len)),
            (rect.bottomleft, (rect.left + corner_len, rect.bottom), (rect.left, rect.bottom - corner_len)),
            (rect.bottomright, (rect.right - corner_len, rect.bottom), (rect.right, rect.bottom - corner_len))
        ]
        
        for corner, horiz, vert in corners:
            pygame.draw.line(self.screen, self.COLORS['accent'], corner, horiz, 3)
            pygame.draw.line(self.screen, self.COLORS['accent'], corner, vert, 3)
        
        # Внутренняя рамка
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(self.screen, self.COLORS['panel_light'], inner_rect, 2)
    
    def _draw_loading_indicator(self, popup: Dict):
        """Отрисовка индикатора загрузки"""
        rect = popup['rect']
        center_x = rect.centerx
        center_y = rect.bottom - 60
        
        # Анимированный спиннер
        spinner_radius = 20
        popup['spinner_angle'] = (popup['spinner_angle'] + 5) % 360
        
        # Рисуем спиннер
        for i in range(8):
            angle = math.radians(popup['spinner_angle'] + i * 45)
            x = center_x + math.cos(angle) * spinner_radius
            y = center_y + math.sin(angle) * spinner_radius
            
            alpha = 255 - i * 30
            color = (*self.COLORS['accent'][:3], alpha)
            
            # Создаем поверхность для круга с альфа-каналом
            circle_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, color, (5, 5), 3)
            self.screen.blit(circle_surf, (x - 5, y - 5))
        
        # Прогресс-бар (если есть прогресс)
        if 'progress' in popup and popup['progress'] > 0:
            bar_width = rect.width - 80
            bar_rect = pygame.Rect(rect.x + 40, center_y + 30, bar_width, 8)
            
            # Фон прогресс-бара
            pygame.draw.rect(self.screen, self.COLORS['panel_light'], bar_rect)
            pygame.draw.rect(self.screen, self.COLORS['border'], bar_rect, 1)
            
            # Заполненная часть
            fill_width = int(bar_width * popup['progress'] / 100)
            fill_rect = pygame.Rect(rect.x + 40, center_y + 30, fill_width, 8)
            pygame.draw.rect(self.screen, self.COLORS['accent'], fill_rect)
            
            # Текст прогресса
            progress_text = self.small_font.render(f"{popup['progress']:.0f}%", 
                                                 True, self.COLORS['text'])
            self.screen.blit(progress_text, 
                           (rect.x + 40 + bar_width + 10, center_y + 25))
    
    def _draw_popup_buttons(self, popup: Dict):
        """Отрисовка кнопок popup-окна"""
        rect = popup['rect']
        buttons = popup['buttons']
        
        # Очищаем старые элементы кнопок
        popup['button_elements'] = []
        
        # Вычисляем позиции кнопок
        total_button_width = len(buttons) * 120 + (len(buttons) - 1) * 20
        start_x = rect.centerx - total_button_width // 2
        button_y = rect.bottom - 60
        
        for i, button_info in enumerate(buttons):
            button_rect = pygame.Rect(start_x + i * 140, button_y, 120, 40)
            
            # Сохраняем информацию о кнопке для обработки событий
            button_element = {
                'rect': button_rect,
                'text': button_info['text'],
                'id': button_info['id'],
                'hover': False
            }
            
            # Проверяем наведение мыши
            mouse_pos = pygame.mouse.get_pos()
            button_element['hover'] = button_rect.collidepoint(mouse_pos)
            
            # Отображаем кнопку
            self._draw_retro_button(button_rect, 
                                  button_element['hover'], 
                                  True)
            
            # Текст кнопки
            text_surf = self.font.render(button_info['text'], True, 
                                       self.COLORS['text'])
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)
            
            # Отображение горячей клавиши
            if 'key' in button_info:
                key_name = pygame.key.name(button_info['key']).upper()
                key_surf = self.small_font.render(f"({key_name})", True,
                                                self.COLORS['accent'])
                key_rect = key_surf.get_rect(midtop=(button_rect.centerx, 
                                                   button_rect.bottom + 5))
                self.screen.blit(key_surf, key_rect)
            
            popup['button_elements'].append(button_element)
    
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
    
    # ========== ОБРАБОТКА СОБЫТИЙ ==========
    
    def handle_popup_events(self, events: List[pygame.event.Event]) -> Optional[str]:
        """
        Обработка событий для popup-окон
        
        Returns:
            ID нажатой кнопки или None
        """
        if not self.popups:
            return None
            
        active_popup = self.get_active_popup()
        if not active_popup:
            return None
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Проверяем клик по кнопкам popup
                if active_popup['type'] != 'loading':
                    for button in active_popup.get('button_elements', []):
                        if button['rect'].collidepoint(event.pos):
                            # Закрываем popup и возвращаем ID кнопки
                            self.close_popup(active_popup['id'])
                            return button['id']
                
                # Закрытие по клику вне окна (только для информационных окон)
                if (active_popup['type'] in ['info', 'warning', 'error'] and 
                    not active_popup['rect'].collidepoint(event.pos)):
                    self.close_popup(active_popup['id'])
                    return 'outside'
            
            elif event.type == pygame.KEYDOWN:
                # Закрытие по Escape
                if event.key == pygame.K_ESCAPE:
                    # Для confirm окон не закрываем по Escape
                    if active_popup['type'] != 'confirm':
                        self.close_popup(active_popup['id'])
                        return 'escape'
                
                # Обработка горячих клавиш для кнопок
                if active_popup['type'] != 'loading':
                    for button_info in active_popup['buttons']:
                        if 'key' in button_info and event.key == button_info['key']:
                            self.close_popup(active_popup['id'])
                            return button_info['id']
        
        return None
    
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
    
    # ========== ОСНОВНЫЕ МЕТОДЫ ИНТЕРФЕЙСА ==========
    
    def handle_events(self, events: List[pygame.event.Event]) -> Optional[str]:
        """Обработка событий"""
        # Сначала обрабатываем события popup
        popup_result = self.handle_popup_events(events)
        
        # Если есть активный popup, не обрабатываем события основных элементов
        if self.popups:
            # Обновляем состояние наведения для кнопок popup
            active_popup = self.get_active_popup()
            if active_popup and active_popup['type'] != 'loading':
                mouse_pos = pygame.mouse.get_pos()
                for button in active_popup.get('button_elements', []):
                    button['hover'] = button['rect'].collidepoint(mouse_pos)
            return popup_result
        
        # Обработка событий для основных элементов
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
        return popup_result
    
    def update(self):
        """Обновление состояния popup-окон (анимации и т.д.)"""
        current_time = pygame.time.get_ticks()
        
        for popup in self.popups:
            if popup['type'] == 'loading':
                # Анимируем спиннер
                popup['spinner_angle'] = (popup['spinner_angle'] + 5) % 360
                
                # Автоматическое закрытие после 10 секунд (на всякий случай)
                if current_time - popup['created_at'] > 10000:
                    self.close_popup(popup['id'])
    
    def draw(self):
        """Отрисовка всех элементов GUI и popup-окон"""
        # Отрисовка сетки (опционально)
        if self.show_grid:
            self.draw_grid()
        
        # Отрисовка основных элементов
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
        
        # Отрисовка popup-окон поверх всего
        for popup in self.popups:
            self.draw_popup(popup)


# Пример использования popup-окон
def popup_example():
    """Пример использования popup-окон"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 600))
    pygame.display.set_caption("Retro Tech GUI - Popup Demo")
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































    
    # Callback функции для кнопок
    def show_info_popup(element):
        gui.show_popup(
            title="Information",
            message="This is an information popup with some important details about the current operation.",
            popup_type="info"
        )
    
    def show_warning_popup(element):
        gui.show_popup(
            title="Warning!",
            message="This is a warning message. Something might not work as expected.",
            popup_type="warning"
        )
    
    def show_error_popup(element):
        gui.show_popup(
            title="Error Detected",
            message="A critical error has occurred. Please check your configuration and try again.",
            popup_type="error"
        )
    
    def show_confirm_popup(element):
        result = gui.show_popup(
            title="Confirmation Required",
            message="Are you sure you want to delete this item? This action cannot be undone.",
            popup_type="confirm"
        )
        print(f"Popup opened with ID: {result}")
    
    def show_custom_popup(element):
        gui.show_popup(
            title="Custom Dialog",
            message="This is a custom popup with multiple buttons.",
            buttons=[
                {'text': 'SAVE', 'id': 'save', 'key': pygame.K_s},
                {'text': 'CANCEL', 'id': 'cancel', 'key': pygame.K_c},
                {'text': 'HELP', 'id': 'help', 'key': pygame.K_h}
            ],
            popup_type="custom"
        )
    
    def show_loading_popup(element):
        popup_id = gui.show_loading_popup(
            title="Processing",
            message="Please wait while we process your request..."
        )
        
        # Имитация процесса загрузки
        def update_loading():
            for i in range(1, 101):
                gui.update_loading_popup(popup_id, progress=i)
                pygame.display.flip()
                pygame.time.delay(50)  # Небольшая задержка для имитации
            gui.close_popup(popup_id)
        
        # В реальном приложении это делалось бы в отдельном потоке
        # Для демо просто вызовем сразу
        update_loading()
    
    # Добавление элементов управления
    buttons_y = 100
    button_spacing = 70
    
    gui.add_element(
        'button',
        id='btn_info',
        x=100, y=buttons_y,
        width=200, height=40,
        label='Show Info Popup',
        callback=show_info_popup
    )
    
    gui.add_element(
        'button',
        id='btn_warning',
        x=100, y=buttons_y + button_spacing,
        width=200, height=40,
        label='Show Warning',
        callback=show_warning_popup
    )
    
    gui.add_element(
        'button',
        id='btn_error',
        x=100, y=buttons_y + button_spacing * 2,
        width=200, height=40,
        label='Show Error',
        callback=show_error_popup
    )
    
    gui.add_element(
        'button',
        id='btn_confirm',
        x=100, y=buttons_y + button_spacing * 3,
        width=200, height=40,
        label='Show Confirmation',
        callback=show_confirm_popup
    )
    
    gui.add_element(
        'button',
        id='btn_custom',
        x=350, y=buttons_y,
        width=200, height=40,
        label='Custom Buttons',
        callback=show_custom_popup
    )
    
    gui.add_element(
        'button',
        id='btn_loading',
        x=350, y=buttons_y + button_spacing,
        width=200, height=40,
        label='Show Loading',
        callback=show_loading_popup
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
        
        # Обработка событий GUI
        popup_result = gui.handle_events(events)
        if popup_result:
            print(f"Popup button clicked: {popup_result}")
        
        # Обновление состояния (для анимаций)
        gui.update()
        
        # Отрисовка
        screen.fill(gui.COLORS['background'])
        gui.draw()
        
        # Отображение инструкций
        instructions = [
            "Click buttons to open different popup windows",
            "Press ESC to close popups or exit",
            "Try hotkeys: Y/N in confirm, S/C/H in custom"
        ]
        
        for i, text in enumerate(instructions):
            hint = gui.small_font.render(text, True, gui.COLORS['text_glow'])
            screen.blit(hint, (50, 500 + i * 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    popup_example()