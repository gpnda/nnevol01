# V3DTO Widget Development - Code Examples

Практические примеры кода для разработки виджетов в Renderer v3dto.

---

## 1️⃣ Простой Информационный Виджет

**Пример:** Панель, которая просто отображает информацию (без взаимодействия)

```python
# -*- coding: utf-8 -*-
"""
SimpleInfoPanel - простая информационная панель.

Отображает текущее состояние симуляции:
- Номер тика
- Количество существ
- Количество еды
- Средний возраст популяции
"""

import pygame
from typing import TYPE_CHECKING
from renderer.v3dto.dto import RenderStateDTO

if TYPE_CHECKING:
    pass


class SimpleInfoPanel:
    """Простая информационная панель в левой части экрана."""
    
    # ========== КОНФИГУРАЦИЯ ==========
    WIDGET_X = 5
    WIDGET_Y = 505
    WIDTH = 200
    HEIGHT = 90
    
    FONT_SIZE = 12
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    COLORS = {
        'background': (20, 20, 20),
        'border': (100, 100, 100),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
    }
    
    BORDER_WIDTH = 2
    PADDING = 8
    LINE_HEIGHT = 16
    
    # ========== ИНИЦИАЛИЗАЦИЯ ==========
    def __init__(self):
        """Инициализация без параметров."""
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, 
                                self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    # ========== ОТРИСОВКА ==========
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """Отрисовка информационной панели."""
        # Очистить поверхность
        self.surface.fill(self.COLORS['background'])
        
        # Граница
        pygame.draw.rect(self.surface, self.COLORS['border'], 
                        self.surface.get_rect(), self.BORDER_WIDTH)
        
        # Заголовок
        title_text = self.font.render("Simulation Info", True, self.COLORS['label'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Получить данные из render_state
        tick = render_state.tick
        population = len(render_state.world.creatures)
        food_count = len(render_state.world.foods)
        
        # Вычислить средний возраст
        if population > 0:
            avg_age = sum(c.age for c in render_state.world.creatures) // population
        else:
            avg_age = 0
        
        # Отрисовать информацию
        y_offset = self.PADDING + self.LINE_HEIGHT + 5
        
        tick_text = self.font.render(f"Tick: {tick}", True, self.COLORS['text'])
        self.surface.blit(tick_text, (self.PADDING, y_offset))
        y_offset += self.LINE_HEIGHT
        
        pop_text = self.font.render(f"Pop: {population}", True, self.COLORS['text'])
        self.surface.blit(pop_text, (self.PADDING, y_offset))
        y_offset += self.LINE_HEIGHT
        
        food_text = self.font.render(f"Food: {food_count}", True, self.COLORS['text'])
        self.surface.blit(food_text, (self.PADDING, y_offset))
        y_offset += self.LINE_HEIGHT
        
        age_text = self.font.render(f"Avg Age: {avg_age}", True, self.COLORS['text'])
        self.surface.blit(age_text, (self.PADDING, y_offset))
        
        # Отобразить на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

---

## 2️⃣ Интерактивный Виджет с Callback

**Пример:** Панель с одной редактируемой переменной и callback уведомлением

```python
# -*- coding: utf-8 -*-
"""
EditableParameterPanel - интерактивная панель редактирования одного параметра.

Позволяет редактировать значение параметра в реальном времени с использованием
callback для уведомления родителя об изменениях.
"""

import pygame
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dto import RenderStateDTO


class EditableParameterPanel:
    """Панель для редактирования одного параметра."""
    
    # ========== КОНФИГУРАЦИЯ ==========
    WIDGET_X = 5
    WIDGET_Y = 35
    WIDTH = 260
    HEIGHT = 80
    
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    COLORS = {
        'background': (30, 30, 30),
        'border': (150, 150, 150),
        'text': (200, 200, 200),
        'label': (100, 150, 200),
        'input_bg': (50, 50, 50),
        'input_text': (255, 255, 255),
        'input_focus': (0, 200, 100),
    }
    
    BORDER_WIDTH = 2
    PADDING = 10
    LINE_HEIGHT = 25
    INPUT_HEIGHT = 25
    
    # ========== ИНИЦИАЛИЗАЦИЯ ==========
    def __init__(self, param_name: str, initial_value: float,
                 on_change: Callable[[str, float], None]):
        """
        Инициализация панели.
        
        Args:
            param_name: Имя параметра (e.g., "mutation_probability")
            initial_value: Начальное значение
            on_change: Callback функция (param_name, value)
        """
        self.param_name = param_name
        self.value = initial_value
        self.on_change = on_change
        
        # Состояние редактирования
        self.is_editing = False
        self.input_buffer = str(initial_value)
        
        # Геометрия
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, 
                                self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Rect для поля ввода
        self.input_rect = pygame.Rect(
            self.PADDING,
            self.PADDING + self.LINE_HEIGHT,
            self.WIDTH - 2 * self.PADDING,
            self.INPUT_HEIGHT
        )
        
        # Шрифт
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    # ========== ОТРИСОВКА ==========
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка панели (БЕЗ render_state, так как управляет своим состоянием)."""
        # Очистить поверхность
        self.surface.fill(self.COLORS['background'])
        
        # Граница
        pygame.draw.rect(self.surface, self.COLORS['border'], 
                        self.surface.get_rect(), self.BORDER_WIDTH)
        
        # Заголовок (имя параметра)
        title_text = self.font.render(self.param_name, True, self.COLORS['label'])
        self.surface.blit(title_text, (self.PADDING, self.PADDING))
        
        # Поле ввода
        input_color = self.COLORS['input_focus'] if self.is_editing else self.COLORS['border']
        pygame.draw.rect(self.surface, self.COLORS['input_bg'], 
                        self.input_rect, 0)  # Заливка
        pygame.draw.rect(self.surface, input_color, 
                        self.input_rect, 2)  # Граница
        
        # Текст в поле ввода
        display_text = self.input_buffer if self.is_editing else str(self.value)
        value_text = self.font.render(display_text, True, self.COLORS['input_text'])
        self.surface.blit(value_text, (self.input_rect.x + 5, self.input_rect.y + 3))
        
        # Отобразить на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
    
    # ========== ОБРАБОТКА СОБЫТИЙ ==========
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """Обработка клавиатуры для редактирования значения."""
        if not self.is_editing:
            # Если не редактируем, начать редактирование на любой цифре
            if event.unicode.isdigit() or event.unicode == '.':
                self.is_editing = True
                self.input_buffer = event.unicode
                return True
            elif event.key == pygame.K_RETURN:
                # Начать редактирование по Enter
                self.is_editing = True
                self.input_buffer = str(self.value)
                return True
        else:
            # Если редактируем
            if event.key == pygame.K_RETURN:
                # Завершить редактирование
                try:
                    new_value = float(self.input_buffer)
                    self.value = new_value
                    self.on_change(self.param_name, new_value)
                    self.is_editing = False
                    return True
                except ValueError:
                    # Некорректное значение, отменить
                    self.is_editing = False
                    self.input_buffer = str(self.value)
                    return True
            
            elif event.key == pygame.K_ESCAPE:
                # Отменить редактирование
                self.is_editing = False
                self.input_buffer = str(self.value)
                return True
            
            elif event.key == pygame.K_BACKSPACE:
                # Удалить последний символ
                self.input_buffer = self.input_buffer[:-1]
                return True
            
            elif event.unicode.isdigit() or event.unicode == '.':
                # Добавить символ
                self.input_buffer += event.unicode
                return True
        
        return False
    
    def handle_mousebuttondown(self, event: pygame.event.Event) -> bool:
        """Обработка клика мыши."""
        # Получить позицию мыши относительно widget'а
        relative_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
        
        if self.input_rect.collidepoint(relative_pos):
            # Клик на поле ввода
            if not self.is_editing:
                self.is_editing = True
                self.input_buffer = str(self.value)
            return True
        
        return False
```

---

## 3️⃣ Виджет с Обработкой Мышки

**Пример:** Кнопка, которая реагирует на клик

```python
# -*- coding: utf-8 -*-
"""
ButtonWidget - кнопка с callback на клик.
"""

import pygame
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .dto import RenderStateDTO


class ButtonWidget:
    """Простая кнопка на экране."""
    
    # ========== КОНФИГУРАЦИЯ ==========
    WIDGET_X = 10
    WIDGET_Y = 10
    WIDTH = 120
    HEIGHT = 40
    
    FONT_SIZE = 16
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    COLORS = {
        'background': (30, 30, 30),
        'background_hover': (50, 50, 50),
        'background_pressed': (80, 80, 80),
        'border': (150, 150, 150),
        'border_hover': (200, 200, 200),
        'text': (200, 200, 200),
        'text_hover': (255, 255, 255),
    }
    
    BORDER_WIDTH = 2
    # ========== ИНИЦИАЛИЗАЦИЯ ==========
    def __init__(self, label: str, on_click: Callable[[], None]):
        """
        Инициализация кнопки.
        
        Args:
            label: Текст на кнопке
            on_click: Callback функция при клике
        """
        self.label = label
        self.on_click = on_click
        
        # Состояние
        self.is_hovered = False
        self.is_pressed = False
        
        # Геометрия
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, 
                                self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифт
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    # ========== ОТРИСОВКА ==========
    def draw(self, screen: pygame.Surface, mouse_pos: Optional[tuple] = None) -> None:
        """
        Отрисовка кнопки.
        
        Args:
            screen: Главный экран
            mouse_pos: Позиция мыши (для эффекта hover)
        """
        # Определить состояние (hovered/normal)
        self.is_hovered = False
        if mouse_pos:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Выбрать цвет фона
        if self.is_pressed:
            bg_color = self.COLORS['background_pressed']
            border_color = self.COLORS['border_hover']
        elif self.is_hovered:
            bg_color = self.COLORS['background_hover']
            border_color = self.COLORS['border_hover']
        else:
            bg_color = self.COLORS['background']
            border_color = self.COLORS['border']
        
        # Выбрать цвет текста
        text_color = self.COLORS['text_hover'] if self.is_hovered else self.COLORS['text']
        
        # Очистить поверхность и нарисовать фон
        self.surface.fill(bg_color)
        pygame.draw.rect(self.surface, border_color, 
                        self.surface.get_rect(), self.BORDER_WIDTH)
        
        # Отрисовать текст в центре
        text = self.font.render(self.label, True, text_color)
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
        self.surface.blit(text, text_rect)
        
        # Отобразить на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
    
    # ========== ОБРАБОТКА СОБЫТИЙ ==========
    def handle_mousebuttondown(self, event: pygame.event.Event) -> bool:
        """Обработка клика мыши."""
        if self.rect.collidepoint(event.pos):
            self.is_pressed = True
            return True
        return False
    
    def handle_mousebuttonup(self, event: pygame.event.Event) -> bool:
        """Обработка отпускания мыши."""
        if self.is_pressed and self.rect.collidepoint(event.pos):
            # Вызвать callback при отпускании ВНУТРИ кнопки
            self.on_click()
            self.is_pressed = False
            return True
        
        self.is_pressed = False
        return False
```

---

## 4️⃣ Использование в Renderer

### Добавление простого виджета

```python
# renderer/v3dto/renderer.py

from renderer.v3dto.gui_simpleinfopanel import SimpleInfoPanel

class Renderer:
    def __init__(self, world, app):
        # ... существующий код ...
        
        # ✅ Инициализировать БЕЗ параметров
        self.info_panel = SimpleInfoPanel()
    
    def _draw_main(self, render_state: RenderStateDTO) -> None:
        """Отрисовка основного состояния."""
        # ... другие виджеты ...
        
        # ✅ Вызвать с RenderStateDTO
        self.info_panel.draw(self.screen, render_state)
```

### Добавление интерактивного виджета с callback

```python
from renderer.v3dto.gui_editableparameterpanel import EditableParameterPanel

class Renderer:
    def __init__(self, world, app):
        # ... существующий код ...
        
        # ✅ Передать callback в инициализацию
        self.edit_panel = EditableParameterPanel(
            param_name="mutation_probability",
            initial_value=0.1,
            on_change=self._on_parameter_change
        )
    
    def _on_parameter_change(self, param_name: str, value: float) -> None:
        """Обработчик изменения параметра."""
        from simparams import sp
        setattr(sp, param_name, value)
        print(f"✓ {param_name} changed to {value}")
    
    def _draw_popup_simparams(self, render_state: RenderStateDTO) -> None:
        """Отрисовка popup окна."""
        # ✅ Вызвать БЕЗ RenderStateDTO (виджет управляет своим состоянием)
        self.edit_panel.draw(self.screen)
    
    def _handle_keyboard_popup_simparams(self, event: pygame.event.Event) -> bool:
        """Обработка клавиатуры в popup."""
        if self.edit_panel.handle_keydown(event):
            return True
        return False
```

### Добавление виджета с кнопкой

```python
from renderer.v3dto.gui_buttonwidget import ButtonWidget

class Renderer:
    def __init__(self, world, app):
        # ... существующий код ...
        
        # ✅ Передать callback на клик
        self.button = ButtonWidget(
            label="Pause",
            on_click=self._on_pause_clicked
        )
    
    def _on_pause_clicked(self) -> None:
        """Обработчик клика на кнопку."""
        self.app.toggle_run()
        print("✓ Simulation paused/resumed")
    
    def _draw_main(self, render_state: RenderStateDTO) -> None:
        """Отрисовка основного состояния."""
        # ... другие виджеты ...
        
        # ✅ Передать позицию мыши для эффекта hover
        import pygame
        self.button.draw(self.screen, pygame.mouse.get_pos())
    
    def _handle_mouse_buttondown_main(self, event: pygame.event.Event) -> bool:
        """Обработка мышки в основном состоянии."""
        if self.button.handle_mousebuttondown(event):
            return True
        return False
    
    def _handle_mouse_buttonup_main(self, event: pygame.event.Event) -> bool:
        """Обработка отпускания мышки."""
        if self.button.handle_mousebuttonup(event):
            return True
        return False
```

---

## ⚡ Быстрые Ответы

### Как получить текущее число существ?
```python
population = len(render_state.world.creatures)
```

### Как получить все параметры симуляции?
```python
params = render_state.params
mutation_prob = params.mutation_probability
food_amount = params.food_amount
```

### Как вызвать callback при изменении?
```python
def __init__(self, on_change: Callable[[str, Any], None]):
    self.on_change = on_change

# Позже:
self.on_change("param_name", new_value)
```

### Как обработать событие мышки?
```python
def handle_mousebuttondown(self, event: pygame.event.Event) -> bool:
    if self.rect.collidepoint(event.pos):
        return True  # Виджет обработал событие
    return False      # Виджет не обработал
```

### Как проверить, редактируется ли поле?
```python
if self.rect.collidepoint(mouse_relative_pos):
    # Клик внутри widget'а
    pass
```

---

## 📚 Дополнительные Материалы

- `V3DTO_WIDGET_DEVELOPMENT_MANUAL.md` — Полный Manual
- `V3DTO_WIDGET_QUICK_REFERENCE.md` — Краткая шпаргалка
- `gui_selected_creature.py` — Реальный пример простого виджета
- `gui_variablespanel.py` — Реальный пример интерактивного виджета
