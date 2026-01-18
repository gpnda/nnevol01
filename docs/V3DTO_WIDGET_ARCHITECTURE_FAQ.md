# V3DTO Widget Architecture - FAQ

Частые архитектурные вопросы и ответы при разработке виджетов.

---

## 🤔 Общие Вопросы об Архитектуре

### Q: Почему DTO вообще нужны?

**A:** DTO (Data Transfer Objects) решают главную проблему - слабая связанность слоев:

**ДО DTO (плохо):**
```python
class ViewportWidget:
    def __init__(self, world, logger, debugger):
        self.world = world      # Зависит от структуры мира
        self.logger = logger    # Зависит от logger'а
        self.debugger = debugger # Зависит от debugger'а
    
    def draw(self):
        # Если world изменится, это сломает viewport
        creatures = self.world.creatures  # Тесная связанность
```

**ПОСЛЕ DTO (хорошо):**
```python
class ViewportWidget:
    def draw(self, screen: pygame.Surface, render_state: RenderStateDTO):
        # Никаких зависимостей, только данные
        creatures = render_state.world.creatures  # Слабая связанность
```

**Преимущества:**
- ✅ Виджет работает с любым источником данных
- ✅ Легко писать тесты (мокируем только DTO)
- ✅ Легко менять внутреннюю структуру мира
- ✅ Явные контракты между слоями

---

### Q: Может ли виджет иметь параметры в `__init__()`?

**A:** Только в очень специфических случаях:

✅ **Допустимо:**
```python
def __init__(self, on_parameter_change: Callable[[str, Any], None]):
    self.on_parameter_change = on_parameter_change  # Callback, не зависимость!
```

✅ **Допустимо:**
```python
def __init__(self, param_name: str):
    self.param_name = param_name  # Простые данные, не синглтоны
```

❌ **Запрещено:**
```python
def __init__(self, world, logger):  # Синглтоны!
    self.world = world
    self.logger = logger
```

**Правило:** Только простые типы данных (str, float, int) или callback функции. Никогда синглтоны!

---

### Q: Что если виджету нужны данные, которых нет в RenderStateDTO?

**A:** Добавь их в RenderStateDTO или создай новый DTO.

```python
# renderer/v3dto/dto.py - добавь новое поле
@dataclass
class RenderStateDTO:
    # ... существующие поля ...
    my_custom_data: MyCustomDTO  # ← Новое поле

# renderer/v3dto/renderer.py - заполни его
def _prepare_render_state_dto(self) -> RenderStateDTO:
    # ... подготовить мой кастомный DTO ...
    my_custom_dto = self._prepare_my_custom_dto()
    
    return RenderStateDTO(
        # ... другие данные ...
        my_custom_data=my_custom_dto,
    )

# gui_mywidget.py - используй его
def draw(self, screen, render_state):
    data = render_state.my_custom_data  # ✅ Теперь доступно
```

**Важно:** Не добавляй синглтоны в DTO! Только трансформированные данные.

---

### Q: Может ли виджет модифицировать состояние мира?

**A:** **НЕТ!** Виджет - это только представление.

```python
# ❌ НИКОГДА ТАК:
def draw(self, screen, render_state):
    render_state.world.creatures[0].energy = 100  # Побочный эффект!

# ✅ ПРАВИЛЬНО:
def draw(self, screen, render_state):
    energy = render_state.world.creatures[0].energy
    # Используй для отрисовки, не для изменения
    text = self.font.render(f"Energy: {energy}", True, self.COLORS['text'])
    self.surface.blit(text, (0, 0))
```

**Правило:** Виджет читает, но никогда не пишет в состояние.

**Исключение:** Интерактивные виджеты вызывают callback:
```python
# ✅ ДОПУСТИМО - вызвать callback
self.on_parameter_change("mutation_probability", 0.5)
# Renderer обработает побочный эффект
```

---

## 🔧 Технические Вопросы

### Q: Можно ли использовать numpy в виджете?

**A:** Да, numpy часто нужен для работы с картой.

```python
# ✅ Допустимо
import numpy as np
from renderer.v3dto.dto import RenderStateDTO

def draw(self, screen, render_state):
    # Работа с картой мира
    map_array = render_state.world.map  # numpy array
    
    # Найти все стены
    walls = np.where(map_array == 1)
    
    # Использовать для отрисовки
    for x, y in zip(walls[0], walls[1]):
        # рисуем стену
        pass
```

**Правило:** Можешь импортировать `numpy`, `pygame`, DTO. Всё остальное - потребует обоснования.

---

### Q: Как обрабатывать события (клавиатура, мышь)?

**A:** Создай методы `handle_*()`, вызови их из Renderer.

```python
# gui_mywidget.py
class MyWidget:
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        """
        Обработка события клавиатуры.
        
        Returns:
            True если виджет обработал событие
            False если событие "прошло дальше"
        """
        if event.key == pygame.K_RETURN:
            self._do_something()
            return True  # ← Событие обработано
        return False     # ← Событие не обработано
    
    def handle_mousebuttondown(self, event: pygame.event.Event) -> bool:
        """Обработка клика мыши."""
        if self.rect.collidepoint(event.pos):
            self._on_clicked()
            return True
        return False

# renderer/v3dto/renderer.py
def _handle_keyboard_main(self, event: pygame.event.Event) -> bool:
    """Обработка клавиатуры в основном состоянии."""
    if self.my_widget.handle_keydown(event):
        return True  # ← Виджет обработал, не обрабатываем дальше
    
    # ... обработка других виджетов ...
    return False
```

**Правило:** Возвращай `True` если обработал, `False` если нет.

---

### Q: Как хранить состояние виджета (например, редактируемое значение)?

**A:** В обычных атрибутах экземпляра, обновляй в `draw()` и `handle_*()`.

```python
class EditablePanel:
    def __init__(self):
        # ... геометрия ...
        self.is_editing = False      # Состояние
        self.input_buffer = ""       # Состояние
        self.selected_index = 0      # Состояние
    
    def draw(self, screen, render_state):
        # Использовать состояние для отрисовки
        if self.is_editing:
            bg_color = self.COLORS['highlight']
        else:
            bg_color = self.COLORS['background']
    
    def handle_keydown(self, event):
        # Обновлять состояние при событиях
        if event.key == pygame.K_RETURN:
            self.is_editing = not self.is_editing
            return True
        return False
```

**Правило:** Состояние виджета - это его атрибуты. Обновляй их в обработчиках событий.

---

### Q: Может ли один виджет зависеть от другого?

**A:** Лучше избегать. Используй `RenderStateDTO` как промежуточное звено.

```python
# ❌ Плохо - прямая зависимость
class PanelA:
    def __init__(self, panel_b):
        self.panel_b = panel_b  # Зависит от PanelB

# ✅ Хорошо - зависимость через DTO
class PanelA:
    def draw(self, screen, render_state):
        # render_state содержит данные для обеих панелей
        # Обе панели используют одни и те же данные
        pass

class PanelB:
    def draw(self, screen, render_state):
        # Того же самого DTO
        pass

# Renderer координирует обе панели
class Renderer:
    def _draw_main(self, render_state):
        self.panel_a.draw(screen, render_state)
        self.panel_b.draw(screen, render_state)
```

**Правило:** Виджеты не знают друг о друге. Renderer координирует их через общий DTO.

---

## 📊 Организационные Вопросы

### Q: Где должны быть виджеты в проекте?

**A:** Строгая структура:

```
renderer/
├── v3dto/                          # ← Версия 3 (текущая)
│   ├── __init__.py
│   ├── renderer.py                 # Main coordinator
│   ├── dto.py                      # DTO definitions
│   ├── gui_viewport.py             # Viewport widget
│   ├── gui_selected_creature.py    # Info panel widget
│   ├── gui_variablespanel.py       # Interactive widget
│   ├── gui_pop_chart.py            # Chart widget
│   ├── gui_creatures_list.py       # Modal widget
│   └── gui_*.py                    # Новые виджеты сюда
├── v2/                             # ← Старая версия (deprecated)
├── v1/                             # ← Очень старая версия
└── mock/                           # ← Для тестов
```

**Правило:** Все новые виджеты в `renderer/v3dto/gui_*.py`.

---

### Q: Как должен быть организован один файл виджета?

**A:** Единая структура для всех:

```python
# -*- coding: utf-8 -*-
"""
WidgetName - краткое описание.

Что показывает:
- Пункт 1
- Пункт 2

АРХИТЕКТУРА v3dto:
- НЕ имеет зависимостей от world, logger, debugger
- Получает данные только через RenderStateDTO
- Полностью изолирована от singleton'ов
"""

# ИМПОРТЫ (только стандартные + pygame + DTO)
import pygame
import numpy as np  # если нужно
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .dto import RenderStateDTO

# КЛАСС ВИДЖЕТА
class MyWidget:
    """Описание класса."""
    
    # ========== КОНФИГУРАЦИЯ ==========
    # Constants для параметров
    
    # ========== ИНИЦИАЛИЗАЦИЯ ==========
    def __init__(self, ...):
        # Инициализировать состояние и геометрию
        
    # ========== ОТРИСОВКА ==========
    def draw(self, ...):
        # Отрисовать виджет
    
    # ========== ОБРАБОТКА СОБЫТИЙ (если нужно) ==========
    def handle_keydown(self, ...):
        # Обработать клавиатуру
    
    def handle_mousebuttondown(self, ...):
        # Обработать мышь
```

**Правило:** Всегда одна и та же структура, один класс на файл.

---

### Q: Что если нужна сложная логика отрисовки?

**A:** Раздели на вспомогательные методы:

```python
class ComplexWidget:
    def draw(self, screen, render_state):
        self.surface.fill(self.COLORS['background'])
        
        # Разделить на методы
        self._draw_border()
        self._draw_title()
        self._draw_content(render_state)
        self._draw_footer()
        
        screen.blit(self.surface, (self.rect.x, self.rect.y))
    
    def _draw_border(self):
        """Отрисовка границы."""
        pygame.draw.rect(self.surface, self.COLORS['border'], 
                        self.surface.get_rect(), self.BORDER_WIDTH)
    
    def _draw_title(self):
        """Отрисовка заголовка."""
        title = self.font.render("My Widget", True, self.COLORS['label'])
        self.surface.blit(title, (self.PADDING, self.PADDING))
    
    def _draw_content(self, render_state):
        """Отрисовка содержимого (использует RenderStateDTO)."""
        # ... сложная логика ...
        pass
    
    def _draw_footer(self):
        """Отрисовка футера."""
        # ... код ...
        pass
```

**Правило:** Большой `draw()` можно разбить на `_draw_*()` методы.

---

## 🔍 Отладка

### Q: Как отладить, почему виджет не отображается?

**A:** Проверь эту цепочку:

1. **Инициализирован ли виджет в Renderer?**
   ```python
   # renderer.py, __init__()
   self.my_widget = MyWidget()  # ✅ Должно быть
   ```

2. **Вызывается ли draw() в нужном состоянии?**
   ```python
   def _draw_main(self, render_state):
       self.my_widget.draw(self.screen, render_state)  # ✅ Должно быть
   ```

3. **Правильная ли позиция на экране?**
   ```python
   WIDGET_X = 100
   WIDGET_Y = 100
   # Убедись, что (100, 100) внутри экрана (0-1250, 0-600)
   ```

4. **Заполняется ли surface?**
   ```python
   def draw(self, screen, render_state):
       self.surface.fill(self.COLORS['background'])  # ✅ Должно быть
       # ...
       screen.blit(self.surface, (self.rect.x, self.rect.y))  # ✅ Blит
   ```

5. **Может ли быть скрыт другим виджетом?**
   Если рисуешь в том же месте что другой виджет, один перепишет другой.

---

### Q: Как отладить события клавиатуры?

**A:** Добавь логирование:

```python
def handle_keydown(self, event: pygame.event.Event) -> bool:
    print(f"MyWidget got key: {event.key}")  # ← Отладочный вывод
    
    if event.key == pygame.K_RETURN:
        print("✓ Return pressed in MyWidget")
        return True
    
    print("✗ Event not handled by MyWidget")
    return False
```

И в Renderer:

```python
def _handle_keyboard_main(self, event):
    print(f"Main state got key: {event.key}")  # ← Отладочный вывод
    
    if self.my_widget.handle_keydown(event):
        print("✓ MyWidget handled the event")
        return True
    
    print("✗ Event not handled by any widget")
    return False
```

---

### Q: Как проверить данные в RenderStateDTO?

**A:** Просто выведи:

```python
def draw(self, screen, render_state):
    # Отладочный вывод
    print(f"Population: {len(render_state.world.creatures)}")
    print(f"Tick: {render_state.tick}")
    print(f"Mutation prob: {render_state.params.mutation_probability}")
    
    # ... остальной код ...
```

Но не забудь удалить debug принты перед коммитом!

---

## 📝 Резюме

| Вопрос | Ответ |
|--------|-------|
| Нужны ли DTO? | Да, для слабой связанности |
| `__init__()` может иметь параметры? | Только простые типы и callback'и |
| Может ли виджет менять мир? | Нет, только вызывать callback |
| Где хранить состояние? | В атрибутах экземпляра |
| Какой импортировать? | Только pygame, numpy, DTO |
| Где создавать виджеты? | `renderer/v3dto/gui_*.py` |
| Как передавать события? | `handle_*()` методы + возвращать bool |
| Как получать данные? | Только из RenderStateDTO |

