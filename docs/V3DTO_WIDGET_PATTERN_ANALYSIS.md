# Анализ Паттерна Создания Виджетов в v3dto Renderer

## Вывод: ДА, виджеты создаются по ОДИНАКОВОМУ ПРИНЦИПУ ✓

Все виджеты в v3dto следуют единому архитектурному паттерну с **общими чертами и соглашениями**.

---

## Общие Черты Всех Виджетов

### 1️⃣ **Структура Класса**

**Все виджеты имеют одинаковую структуру:**

```python
class WidgetName:
    # 1. Константы конфигурации (расположение, размеры, цвета)
    POSITION_X = ...
    POSITION_Y = ...
    WIDTH = ...
    HEIGHT = ...
    
    FONT_SIZE = ...
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    
    COLORS = {
        'key': (r, g, b),
        ...
    }
    
    # 2. Инициализация (__init__)
    def __init__(self, ...):
        # Создание pygame.Rect для геометрии
        self.rect = pygame.Rect(...)
        
        # Создание pygame.Surface для отрисовки
        self.surface = pygame.Surface((WIDTH, HEIGHT), ...)
        
        # Инициализация шрифтов
        self.font = pygame.font.Font(...)
    
    # 3. Метод отрисовки (draw)
    def draw(self, screen: pygame.Surface, ...) -> None:
        # Отрисовка на surface или screen
        ...
```

### 2️⃣ **Инициализация**

**Все виджеты:**
- ✓ НЕ требуют зависимостей от `world`, `app`, `logger`, `debugger`
- ✓ Имеют `__init__()` с минимальными параметрами (или без них)
- ✓ Создают `pygame.Rect()` для расположения на экране
- ✓ Создают `pygame.Surface()` для собственной отрисовки
- ✓ Инициализируют шрифты через try-except (безопасно)

**Примеры:**

| Виджет | __init__ параметры |
|--------|-------------------|
| `Viewport` | `()` — нет параметров |
| `SelectedCreaturePanel` | `()` — нет параметров |
| `SelectedCreatureHistory` | `()` — нет параметров |
| `VariablesPanel` | `(on_parameter_change: Callable)` — только callback |

### 3️⃣ **Конфигурация через Class Constants**

**Все виджеты определяют свои параметры как class-level константы:**

```python
# Viewport
VIEWPORT_X = 5
VIEWPORT_Y = 5
VIEWPORT_WIDTH = 1240
VIEWPORT_HEIGHT = 500
CAMERA_SCALE_MIN = 7.0
CAMERA_SCALE_MAX = 50.0

# SelectedCreaturePanel
POSITION_X = 35
POSITION_Y = 150
WIDTH = 250
HEIGHT = 300

# SelectedCreatureHistory
POSITION_X = 4
POSITION_Y = 505
WIDTH = 1243
HEIGHT = 65

# VariablesPanel
PANEL_X = 275
PANEL_Y = 35
PANEL_WIDTH = 700
PANEL_HEIGHT = 420
```

**Преимущества:**
- Легко менять расположение без изменения логики
- Все параметры в одном месте (удобство)
- Нет "магических чисел" в коде

### 4️⃣ **Цветовая Схема**

**Все виджеты определяют `COLORS` словарь:**

```python
COLORS = {
    'background': (r, g, b),
    'border': (r, g, b),
    'text': (r, g, b),
    'highlight': (r, g, b),
    'selected': (r, g, b),
    # ... специфичные для виджета цвета
}
```

**Все используют:**
- Одинаковый формат (RGB tuple)
- Одинаковые ключи где применимо (background, border, text)
- Именованные цвета вместо magic numbers

### 5️⃣ **Шрифты**

**Все виджеты следуют одному паттерну:**

```python
FONT_SIZE = 16
FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'

def __init__(self):
    try:
        self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
    except (FileNotFoundError, pygame.error):
        self.font = pygame.font.Font(None, self.FONT_SIZE)  # fallback
```

**Это обеспечивает:**
- Одинаковый стиль шрифта для всех
- Graceful fallback на системный шрифт
- Центральное управление (легко изменить FONT_PATH везде)

### 6️⃣ **Метод draw()**

**Все виджеты имеют `draw()` метод, но сигнатуры НЕМНОГО отличаются:**

```python
# Viewport (получает RenderStateDTO + font)
def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO', 
         font: pygame.font.Font = None) -> None:
    ...

# SelectedCreaturePanel (получает RenderStateDTO)
def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
    ...

# SelectedCreatureHistory (получает RenderStateDTO)
def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
    ...

# VariablesPanel (НЕ получает RenderStateDTO)
def draw(self, screen: pygame.Surface) -> None:
    ...
```

**Почему разные сигнатуры?**
- **Viewport** нужен `font` для отладочной информации
- **SelectedCreaturePanel, History** получают `RenderStateDTO` с данными
- **VariablesPanel** управляет своим состоянием (editing, selected_index) независимо

**✅ Но архитектурный принцип ОДИН:**
> *Данные передаются через DTO, НЕ прямые объекты world/logger*

### 7️⃣ **Отсутствие Зависимостей**

**Все виджеты:**
- ❌ НЕ импортируют `world`
- ❌ НЕ импортируют `logger` (singleton)
- ❌ НЕ импортируют `debugger` (singleton)
- ❌ НЕ импортируют `simparams` (singleton)
- ✅ Только читают данные из передаваемых параметров (DTO или callback)

**Пример:** `SelectedCreaturePanel` НЕ импортирует ничего из доменной логики:

```python
import pygame
import numpy as np
from typing import Optional
from renderer.v3dto.dto import RenderStateDTO  # Только DTO!

class SelectedCreaturePanel:
    # ... полностью изолирован
```

### 8️⃣ **Surface для Отрисовки**

**Все виджеты создают собственный `pygame.Surface`:**

```python
# Viewport
self.surface = pygame.Surface((self.rect.width, self.rect.height))

# SelectedCreaturePanel
self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

# SelectedCreatureHistory
self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

# VariablesPanel
# Рисует прямо на screen (исключение, но логично для панели переменных)
```

**Зачем surface?**
- Изоляция отрисовки каждого виджета
- Возможность использовать alpha blending (`pygame.SRCALPHA`)
- Легко тестировать отдельно

---

## Сравнительная Таблица

| Характеристика | Viewport | SelectedCreaturePanel | SelectedCreatureHistory | VariablesPanel |
|---|---|---|---|---|
| **Требует параметров в __init__** | ❌ Нет | ❌ Нет | ❌ Нет | ✅ callback |
| **Имеет COLORS dict** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Имеет FONT_SIZE + FONT_PATH** | ✅ Да* | ✅ Да | ✅ Да | ✅ Да |
| **Имеет POSITION/WIDTH/HEIGHT** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Создает pygame.Surface** | ✅ Да | ✅ Да | ✅ Да | ❌ Нет |
| **Имеет draw() метод** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Импортирует DTO** | ✅ Да | ✅ Да | ✅ Да | ❌ Нет |
| **Независим от world** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Использует try-except для шрифта** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |

*Viewport получает font как параметр в draw()

---

## Как Это Работает в Renderer

```python
class Renderer:
    def __init__(self, world, app):
        # 1. Инициализация виджетов БЕЗ параметров
        self.viewport = Viewport()
        self.variables_panel = VariablesPanel(on_parameter_change=self._on_parameter_change)
        self.selected_creature_panel = SelectedCreaturePanel()
        self.selected_creature_history = SelectedCreatureHistory()
    
    def draw(self):
        # 2. Подготовка DTO
        render_state = self._prepare_render_state_dto()
        
        # 3. Вызов draw() каждого виджета с одинаковым контрактом
        self.viewport.draw(self.screen, render_state, self.font)
        self.selected_creature_panel.draw(self.screen, render_state)
        self.selected_creature_history.draw(self.screen, render_state)
        self.variables_panel.draw(self.screen)  # Исключение
    
    def _on_parameter_change(self, param_name: str, value: Any):
        # 4. Обработка обратного вызова из VariablesPanel
        setattr(sp, param_name, value)
```

**Архитектурные преимущества:**
- ✅ Слабая связанность между Renderer и виджетами
- ✅ Виджеты легко тестировать отдельно (нужны только DTO)
- ✅ Виджеты можно переиспользовать в других контекстах
- ✅ Изменение источника данных не требует изменения виджетов

---

## Рекомендация для Новых Виджетов

Если вы создаёте новый виджет, следуйте этому шаблону:

```python
# -*- coding: utf-8 -*-
"""
Описание виджета.
Архитектура v3dto: получает данные через DTO, не импортирует singletons.
"""

import pygame
from typing import Optional, TYPE_CHECKING
from renderer.v3dto.dto import RenderStateDTO  # Или другие нужные DTO

if TYPE_CHECKING:
    # Type hints для IDE
    pass

class MyNewWidget:
    """Описание."""
    
    # 1. Константы конфигурации
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
    
    def __init__(self):
        """2. Инициализация без параметров (или минимум)."""
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, 
                                self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except (FileNotFoundError, pygame.error):
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
        """3. Метод отрисовки с DTO параметром."""
        # Отрисовка на self.surface
        self.surface.fill(self.COLORS['background'])
        
        # Использование данных из render_state
        # ...
        
        # Блит на главный экран
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

---

## Итоговые Выводы

| Вопрос | Ответ |
|--------|-------|
| **Все виджеты создаются по одинаковому принципу?** | ✅ **ДА** |
| **Есть ли общие черты?** | ✅ **ДА, много** |
| **Есть ли исключения?** | ⚠️ **Частично (VariablesPanel)** |
| **Это хорошая архитектура?** | ✅ **ДА, очень хорошая** |
| **Почему?** | Полная изоляция, слабая связанность, тестируемость |

### Общие Черты (Consensus Pattern):

1. **Инициализация** — Без зависимостей или только callback
2. **Конфигурация** — Class constants (POSITION, SIZE, COLORS, FONT)
3. **Отрисовка** — `draw()` метод с данными в виде DTO
4. **Шрифты** — Безопасная инициализация с fallback
5. **Цвета** — Словарь COLORS с именованными ключами
6. **Изоляция** — НЕ импортирует singletons (world, logger, debugger, simparams)
7. **Surface** — Собственная pygame.Surface для отрисовки (где применимо)

### Вариации (Зачем они):

- **VariablesPanel** вызывает callback вместо DTO (управляет своим состоянием)
- **Viewport** получает font в draw() (для debug info)
- Некоторые используют `pygame.SRCALPHA`, другие нет (зависит от прозрачности)

**Это допустимые вариации, но ядро архитектуры — ОДНО.**
