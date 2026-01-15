# V3DTO Widget Pattern - Quick Reference Checklist

## ✅ Требования для Правильного Виджета v3dto

### Инициализация (`__init__`)

```python
class YourWidget:
    # ✅ Должно быть:
    WIDGET_X = 10
    WIDGET_Y = 10
    WIDTH = 200
    HEIGHT = 100
    
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    COLORS = {
        'background': (20, 20, 20),
        'border': (100, 100, 100),
        'text': (200, 200, 200),
    }
    
    def __init__(self, ...):  # ✅ Минимум параметров
        # ✅ Создать Rect
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, 
                                self.WIDTH, self.HEIGHT)
        
        # ✅ Создать Surface
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # ✅ Инициализировать шрифт с fallback
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
```

### Отрисовка (`draw`)

```python
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """✅ Правильная сигнатура (или без render_state для исключений)."""
        
        # ✅ Очистить surface
        self.surface.fill(self.COLORS['background'])
        
        # ✅ Использовать данные из render_state (не из world!)
        # ХОРОШО:
        creature = render_state.selected_creature
        # ПЛОХО:
        # creature = self.world.creatures[0]  ← ❌ FORBIDDEN
        
        # ✅ Отрисовать на self.surface
        self.surface.blit(text_surf, (10, 10))
        
        # ✅ Отрисовать border
        pygame.draw.rect(self.surface, self.COLORS['border'], 
                        self.surface.get_rect(), 2)
        
        # ✅ Блит на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

### Изоляция от Singletons

```python
# ✅ ХОРОШИЕ импорты:
import pygame
from typing import Optional
from renderer.v3dto.dto import RenderStateDTO

# ❌ ЗАПРЕЩЁННЫЕ импорты:
# from world import World               ❌
# from logger import logme              ❌
# from debugger import debug            ❌
# from simparams import sp              ❌
# from application import Application   ❌
```

---

## 📊 Сравнение Четырёх Виджетов

### 1. Viewport

| Аспект | Значение |
|--------|----------|
| **__init__ параметры** | ✅ Нет |
| **Surface** | ✅ Да (основной рендер) |
| **draw() сигнатура** | `draw(screen, render_state, font)` |
| **Extra methods** | ✅ screen_to_map, handle_mouse_* |
| **State management** | ✅ camera_offset, camera_scale, is_dragging |
| **Особенность** | Получает font в draw() для debug text |

**Инициализация:**
```python
self.viewport = Viewport()  # Ноль параметров
```

**Вызов:**
```python
self.viewport.draw(self.screen, render_state, self.font)
```

---

### 2. SelectedCreaturePanel

| Аспект | Значение |
|--------|----------|
| **__init__ параметры** | ✅ Нет |
| **Surface** | ✅ Да (с SRCALPHA) |
| **draw() сигнатура** | `draw(screen, render_state)` |
| **Extra methods** | ❌ Нет (простой рендер) |
| **State management** | ❌ Нет (stateless) |
| **Особенность** | Простой вывод информации |

**Инициализация:**
```python
self.selected_creature_panel = SelectedCreaturePanel()
```

**Вызов:**
```python
self.selected_creature_panel.draw(self.screen, render_state)
```

---

### 3. SelectedCreatureHistory

| Аспект | Значение |
|--------|----------|
| **__init__ параметры** | ✅ Нет |
| **Surface** | ✅ Да (с SRCALPHA) |
| **draw() сигнатура** | `draw(screen, render_state)` |
| **Extra methods** | ✅ _draw_graph_line, _draw_event_markers |
| **State management** | ❌ Нет (все данные из render_state) |
| **Особенность** | Отрисовка графиков и событий |

**Инициализация:**
```python
self.selected_creature_history = SelectedCreatureHistory()
```

**Вызов:**
```python
self.selected_creature_history.draw(self.screen, render_state)
```

---

### 4. VariablesPanel

| Аспект | Значение |
|--------|----------|
| **__init__ параметры** | ✅ on_parameter_change callback |
| **Surface** | ❌ Нет (рисует прямо на screen) |
| **draw() сигнатура** | `draw(screen)` ← ИСКЛЮЧЕНИЕ |
| **Extra methods** | ✅ add_variable, handle_keydown |
| **State management** | ✅ editing, selected_index, input_buffer, variables |
| **Особенность** | Двусторонняя коммуникация (callback) |

**Инициализация:**
```python
self.variables_panel = VariablesPanel(on_parameter_change=self._on_parameter_change)
```

**Вызов:**
```python
self.variables_panel.draw(self.screen)  # Без render_state!
```

**Callback в Renderer:**
```python
def _on_parameter_change(self, param_name: str, value: Any):
    """Обработка изменений из VariablesPanel."""
    setattr(sp, param_name, value)
```

---

## 🎯 Общие Черты (Consensus)

| Черта | Все 4 виджета |
|-------|-------|
| **Константы конфигурации** | ✅ POSITION_X/Y, WIDTH, HEIGHT |
| **COLORS словарь** | ✅ Все определяют |
| **FONT_SIZE + FONT_PATH** | ✅ Все определяют |
| **try-except для шрифта** | ✅ Все используют graceful fallback |
| **__init__() независим** | ✅ Ноль глобальных зависимостей |
| **draw() метод** | ✅ Все имеют |
| **pygame.Rect** | ✅ Все создают |
| **Не импортирует singletons** | ✅ Все чистые |
| **Использует DTO** | ✅ Все (кроме VariablesPanel) |

---

## 🔴 Вариации (Допустимо Различаться)

| Вариация | Причина |
|----------|---------|
| **draw() сигнатура** | Разные потребности в данных |
| **VariablesPanel без DTO** | Управляет собственным состоянием (editing, input) |
| **Viewport с callback для mouse** | Требует обработки событий |
| **Surface vs прямой рендер** | SRCALPHA нужен только для прозрачности |
| **__init__ параметры** | VariablesPanel нужен callback для двусторонней связи |

---

## 📋 Чек-Лист для Нового Виджета

При создании нового виджета убедитесь:

### Структура
- [ ] Класс имеет `__init__(self)` без зависимостей
- [ ] Класс имеет `draw(screen, render_state)` метод
- [ ] Класс определяет `COLORS = {...}` словарь
- [ ] Класс определяет `POSITION_X, POSITION_Y, WIDTH, HEIGHT`
- [ ] Класс определяет `FONT_SIZE, FONT_PATH`

### Инициализация
- [ ] Создан `self.rect = pygame.Rect(...)`
- [ ] Создана `self.surface = pygame.Surface(...)`
- [ ] Инициализирован `self.font` с try-except

### Отрисовка
- [ ] Метод `draw()` получает `screen` и `render_state`
- [ ] Данные берутся из `render_state`, не из `world`
- [ ] Отрисовка происходит на `self.surface`
- [ ] Surface блитится на главный `screen`

### Чистота Кода
- [ ] Нет импорта `world`
- [ ] Нет импорта `logger`
- [ ] Нет импорта `debugger`
- [ ] Нет импорта `simparams`
- [ ] Только импорты pygame и DTO

### Опционально
- [ ] Extra методы для внутренней логики (e.g., `_format_data()`)
- [ ] State management если нужно (e.g., `selected_index`)
- [ ] Callback для двусторонней связи если нужно

---

## 🚀 Шаблон для Копирования

```python
# -*- coding: utf-8 -*-
"""
MyNewWidget - v3dto версия.

Описание виджета и его функционала.

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger, simparams
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO


class MyNewWidget:
    """Описание виджета."""
    
    # Координаты и размеры
    WIDGET_X = 10
    WIDGET_Y = 10
    WIDTH = 200
    HEIGHT = 100
    
    # Шрифт
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    # Цвета
    COLORS = {
        'background': (20, 20, 20),
        'border': (100, 100, 100),
        'text': (200, 200, 200),
        'highlight': (255, 255, 255),
    }
    
    # Параметры отображения
    BORDER_WIDTH = 2
    PADDING = 10
    LINE_HEIGHT = 20
    
    def __init__(self):
        """Инициализация виджета (без параметров)."""
        # Геометрия
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y,
                                self.WIDTH, self.HEIGHT)
        
        # Поверхность для отрисовки
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Шрифт
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """
        Отрисовка виджета на экран.
        
        Args:
            screen: Pygame surface главного экрана
            render_state: RenderStateDTO с данными симуляции
        """
        # Очистить surface
        self.surface.fill(self.COLORS['background'])
        
        # Отрисовать border
        pygame.draw.rect(self.surface, self.COLORS['border'],
                        self.surface.get_rect(), self.BORDER_WIDTH)
        
        # Извлечь данные из render_state
        # creature = render_state.selected_creature  ← так правильно
        # world = render_state.world  ← так правильно
        
        # Отрисовать текст
        text_surf = self.font.render("My Widget", False, self.COLORS['text'])
        self.surface.blit(text_surf, (self.PADDING, self.PADDING))
        
        # Блит на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

---

## 🎓 Вывод

> **Все виджеты в v3dto следуют единому паттерну:**
>
> 1. **Конфигурация** → Constants (POSITION, SIZE, COLORS, FONT)
> 2. **Инициализация** → __init__() с Rect, Surface, Font
> 3. **Отрисовка** → draw() получает DTO, рисует на surface
> 4. **Изоляция** → Ноль зависимостей от singletons
>
> **Вариации допустимы, но ядро архитектуры — ОДНО.**
