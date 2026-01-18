# V3DTO Widget Development - Quick Reference

Краткая шпаргалка для разработки новых виджетов. Используйте вместе с V3DTO_WIDGET_DEVELOPMENT_MANUAL.md

---

## 🎯 В 30 Секунд

1. **Создать файл:** `renderer/v3dto/gui_myname.py`
2. **Структура:** constants → __init__() → draw()
3. **Данные:** Только из RenderStateDTO (никаких синглтонов!)
4. **Добавить в Renderer:** Инициализировать + вызвать в draw()

---

## 📝 Минимальный Шаблон

```python
# -*- coding: utf-8 -*-
"""MyWidget - краткое описание."""

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dto import RenderStateDTO

class MyWidget:
    # CONSTANTS
    WIDGET_X, WIDGET_Y = 10, 10
    WIDTH, HEIGHT = 200, 100
    FONT_SIZE = 14
    COLORS = {'background': (30,30,30), 'text': (200,200,200)}
    
    def __init__(self):
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        self.surface.fill(self.COLORS['background'])
        # ваш код отрисовки
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

---

## ✅ Чеклист Перед Коммитом

- [ ] `__init__()` БЕЗ параметров (кроме callback)
- [ ] Нет импортов `world`, `logger`, `debugger`, `simparams`
- [ ] Все параметры - class constants
- [ ] Шрифт с try-except fallback
- [ ] RenderStateDTO только в draw()
- [ ] Используется собственный surface
- [ ] Добавлено в Renderer.__init__()
- [ ] Вызвано в _draw_main() (или другом состоянии)
- [ ] Docstring описывает архитектуру v3dto

---

## 🔗 Где Что Находится

| Что | Где |
|-----|-----|
| Новый виджет | `renderer/v3dto/gui_*.py` |
| Инициализация | `Renderer.__init__()` |
| Отрисовка | `Renderer._draw_main()` и т.д. |
| Данные | `RenderStateDTO` |
| Цвета и размеры | class constants в начале класса |
| Обработка событий | `Renderer._handle_keyboard()` |

---

## 📊 Макет Экрана v3dto

```
(5,5) Viewport (1240x500)
     |_________|
     |         | VariablesPanel (700x420)
     |_________|__________|
                          |
(35,150) SelectedCreaturePanel (250x300)
     |
(4,505) SelectedCreatureHistory (1243x65)
```

---

## 🎨 Стандартные Цвета

```python
COLORS = {
    'background': (30, 30, 30),      # Тёмный
    'border': (150, 150, 150),       # Серый
    'text': (200, 200, 200),         # Светлый
    'highlight': (0, 255, 100),      # Зелёный
    'selected': (255, 255, 0),       # Жёлтый
}
```

---

## ❌ ЗАПРЕЩЕНО / ✅ ПРАВИЛЬНО

| Запрещено | Правильно |
|-----------|-----------|
| Импортировать `world` | Использовать `render_state.world` |
| Импортировать `logme` | Использовать `render_state.params` |
| Импортировать `debug` | Использовать `render_state.debug` |
| Менять состояние мира | Только отрисовка |
| `self.x = 10` в коде | `WIDGET_X = 10` constant |
| Рисовать прямо на screen | На surface, потом screen.blit() |

---

## 🔄 Данные в RenderStateDTO

```python
# Мир
render_state.world.creatures      # [CreatureDTO, ...]
render_state.world.foods          # [FoodDTO, ...]
render_state.world.map            # numpy array

# Параметры
render_state.params.mutation_probability
render_state.params.food_amount
# и так далее...

# Отладка
render_state.debug.raycast_dots   # для отладки
render_state.debug.visions        # видение существ

# Выбранное существо
render_state.selected_creature.creature   # CreatureDTO
render_state.selected_creature.history    # CreatureHistoryDTO

# Состояние приложения
render_state.current_state        # 'main', 'modal', etc.
render_state.tick                 # номер тика
render_state.fps                  # счётчик FPS
```

---

## 🚀 3 Простых Шага для Нового Виджета

### 1. Создать класс
```python
# renderer/v3dto/gui_mywidget.py
class MyWidget:
    WIDGET_X, WIDGET_Y = 10, 10
    WIDTH, HEIGHT = 200, 100
    # ... rest
```

### 2. Добавить в Renderer
```python
# renderer.py, в __init__():
self.my_widget = MyWidget()

# в _draw_main():
self.my_widget.draw(self.screen, render_state)
```

### 3. Готово! 🎉

---

## 📌 Интерактивные Виджеты

Если нужны события клавиатуры:

```python
def handle_keydown(self, event: pygame.event.Event) -> bool:
    if event.key == pygame.K_UP:
        self.selected_index -= 1
        return True
    return False

# В Renderer._handle_keyboard_main():
if self.my_widget.handle_keydown(event):
    return True
```

---

## 🐛 Отладка

```python
# Проверить, что данные приходят
print(f"Creature: {render_state.selected_creature}")
print(f"Population: {len(render_state.world.creatures)}")

# Проверить, что виджет инициализирован
print(f"Widget rect: {self.rect}")

# Убедиться, что нет синглтонов
import renderer.v3dto.gui_mywidget
# Должны быть только pygame, numpy, DTO
```

---

## 📖 Примеры Существующих Виджетов

**Простой (информационный):**
- `gui_selected_creature.py` — 202 строки, только отрисовка

**Средний (с камерой):**
- `gui_viewport.py` — 412 строк, обработка мышки, координаты

**Сложный (интерактивный):**
- `gui_variablespanel.py` — 352 строки, редактирование, callback

**Модальный (окно):**
- `gui_creatures_list.py` — 262 строки, навигация, скролл

---

**Читай полный Manual:** `V3DTO_WIDGET_DEVELOPMENT_MANUAL.md`
