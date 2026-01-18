# V3DTO Widget Development - TL;DR (Executive Summary)

Предельно краткое резюме всех 5 документов в одном месте.

---

## 🎯 Главное (30 секунд)

**Три правила:**

1. ✅ **Виджет получает данные через RenderStateDTO** (НИКОГДА не импортируй world, logger, debugger)
2. ✅ **Инициализируй БЕЗ параметров** (или только callback)
3. ✅ **Определи всё как class constants** (WIDGET_X, WIDTH, COLORS и т.д.)

**Структура:**
```python
class MyWidget:
    WIDGET_X = 10      # Constants
    WIDTH = 200
    COLORS = {...}
    
    def __init__(self):                          # БЕЗ параметров
        self.rect = pygame.Rect(...)
        self.surface = pygame.Surface(...)
    
    def draw(self, screen, render_state):        # Только эти два параметра
        # рисуй на self.surface
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

---

## 📋 В 5 Шагов до Готового Виджета

### 1️⃣ Создай файл
```bash
renderer/v3dto/gui_mywidget.py
```

### 2️⃣ Скопируй структуру
```python
# -*- coding: utf-8 -*-
"""MyWidget - краткое описание. Архитектура v3dto: DTO, без синглтонов."""

import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .dto import RenderStateDTO

class MyWidget:
    WIDGET_X, WIDGET_Y = 10, 10
    WIDTH, HEIGHT = 200, 100
    COLORS = {'background': (30,30,30), 'text': (200,200,200)}
    
    def __init__(self):
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        try:
            self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', 14)
        except:
            self.font = pygame.font.Font(None, 14)
    
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        self.surface.fill(self.COLORS['background'])
        # ... твой код ...
        screen.blit(self.surface, (self.rect.x, self.rect.y))
```

### 3️⃣ Добавь в Renderer.__init__()
```python
self.my_widget = MyWidget()
```

### 4️⃣ Вызови в _draw_main()
```python
def _draw_main(self, render_state):
    self.my_widget.draw(self.screen, render_state)
```

### 5️⃣ Готово! ✅

---

## 🚀 Шпаргалка на Одной Странице

### Получить Данные
```python
render_state.world.creatures      # Список существ
render_state.world.foods          # Список еды
render_state.world.map            # Карта (numpy array)
render_state.params               # Параметры симуляции
render_state.tick                 # Номер тика
render_state.fps                  # Счётчик FPS
```

### Цвета (Стандарт)
```python
COLORS = {
    'background': (30, 30, 30),
    'border': (150, 150, 150),
    'text': (200, 200, 200),
    'highlight': (0, 255, 100),
    'selected': (255, 255, 0),
}
```

### Обработка Событий
```python
def handle_keydown(self, event: pygame.event.Event) -> bool:
    if event.key == pygame.K_RETURN:
        return True  # ← Обработано
    return False     # ← Не обработано

# В Renderer._handle_keyboard_main():
if self.my_widget.handle_keydown(event):
    return True
```

### Callback при Изменении
```python
# В __init__():
def __init__(self, on_change: Callable[[str, Any], None]):
    self.on_change = on_change

# Позже:
self.on_change("param_name", new_value)

# В Renderer.__init__():
self.panel = MyPanel(on_change=self._on_parameter_change)

# Обработчик:
def _on_parameter_change(self, param_name: str, value: Any):
    from simparams import sp
    setattr(sp, param_name, value)
```

---

## ❌ ЗАПРЕЩЕНО / ✅ ПРАВИЛЬНО

| ❌ Не Делай | ✅ Делай |
|---|---|
| `from world import world` | Используй `render_state.world` |
| `from service.logger import logme` | Используй `render_state.params` |
| `def __init__(self, world)` | `def __init__(self)` |
| `self.world.creatures[0].energy = 100` | Только читать, вызывать callback |
| `self.x = 10; self.y = 20` | `WIDGET_X = 10; WIDGET_Y = 20` |
| `screen.blit(text, (100, 100))` | Рисуй на surface, потом screen.blit() |
| `pygame.font.Font('./font.ttf')` | Используй try-except с fallback |

---

## 🎨 Макет Экрана

```
(5,5) Viewport (1240x500)
     |_________|
     |         | VariablesPanel (700x420, editable)
     |_________|__________|
                          |
(35,150) SelectedCreaturePanel (250x300)
     |
(4,505) SelectedCreatureHistory (1243x65)
```

Свободное место: помещай новые виджеты так чтобы не перекрывали существующие.

---

## 📚 Документы и Для Чего

| Документ | Когда читать | Время |
|----------|--------------|-------|
| **V3DTO_WIDGET_DEVELOPMENT_MANUAL.md** | В первый раз, полное понимание | 30 мин |
| **V3DTO_WIDGET_QUICK_REFERENCE.md** | Краткое напоминание, шпаргалка | 5 мин |
| **V3DTO_WIDGET_CODE_EXAMPLES.md** | Примеры кода похожих виджетов | 10 мин |
| **V3DTO_WIDGET_ARCHITECTURE_FAQ.md** | Вопросы об архитектуре | 10 мин |
| **V3DTO_WIDGET_PRECOMMIT_CHECKLIST.md** | Перед коммитом, финальная проверка | 10 мин |
| **V3DTO_WIDGET_DEVELOPMENT_DOCUMENTATION_INDEX.md** | Навигация по всей документации | 5 мин |

---

## ✅ Финальный Чек-Лист

Перед `git commit`:

```
☐ Виджет в renderer/v3dto/gui_*.py
☐ Нет импортов world, logger, debugger, simparams
☐ __init__() БЕЗ параметров (или только callback)
☐ Все параметры как class constants
☐ Шрифт с try-except fallback
☐ draw() получает (screen, render_state)
☐ Результат рисуется на self.surface, потом screen.blit()
☐ Добавлено в Renderer.__init__()
☐ Вызвано в Renderer._draw_main()
☐ Отображается на экране
☐ Не пересекается с другими виджетами
☐ События обрабатываются корректно
☐ Нет побочных эффектов
☐ Код соответствует стилю других виджетов
☐ Docstring описывает архитектуру v3dto
```

Если всё ☐ — готово! ✅

---

## 🤔 Если Что-то Не Работает

1. **Виджет не отображается?**
   - Проверь `__init__()` инициализирован ли в Renderer
   - Проверь `draw()` вызывается ли в `_draw_main()`
   - Проверь позицию (WIDGET_X, WIDGET_Y) в пределах экрана

2. **События не обрабатываются?**
   - Проверь `handle_keydown()` возвращает bool
   - Проверь обработчик вызывается ли в Renderer._handle_*()
   - Проверь возвращается ли True при обработке

3. **Импорт world/logger не работает?**
   - ❌ НИКОГДА не импортируй их в виджет!
   - ✅ Используй `render_state.world`, `render_state.params`

4. **Что если данные отсутствуют в RenderStateDTO?**
   - Добавь DTO в `renderer/v3dto/dto.py`
   - Заполни DTO в `Renderer._prepare_render_state_dto()`
   - Используй в draw()

---

## 📞 Быстрые Ответы

**Q: Где создавать?**  
A: `renderer/v3dto/gui_*.py`

**Q: Какой импортировать?**  
A: Только pygame, numpy, DTO. БЕЗ синглтонов.

**Q: `__init__()` параметры?**  
A: Только простые типы (str, float, int) и Callable callback.

**Q: Откуда данные?**  
A: Только из `RenderStateDTO` в методе `draw()`.

**Q: Как сообщить об изменении?**  
A: Вызвать callback: `self.on_change("param", value)`.

**Q: Обработка мышки?**  
A: Метод `handle_mousebuttondown()` возвращающий bool.

**Q: Цвета какие?**  
A: COLORS = {...} в class constants.

**Q: Шрифт может не существовать?**  
A: Да, используй try-except с fallback на системный.

---

## 🎯 Философия v3dto

**Главная идея:** Слабая связанность через DTO.

```
Renderer (singleton coordinator)
    ├─ Читает: world, logger, debugger, simparams
    ├─ Преобразует в: DTO (data only)
    └─ Передаёт: RenderStateDTO виджетам
        ├─ Widget1 (чистый UI, нет синглтонов)
        ├─ Widget2 (чистый UI, нет синглтонов)
        └─ Widget3 (чистый UI, нет синглтонов)
```

**Это позволяет:**
- ✅ Тестировать виджеты отдельно (мокируем DTO)
- ✅ Менять источник данных (world, logger)
- ✅ Переиспользовать виджеты в других местах
- ✅ Явные контракты между слоями
- ✅ Легко читаемый и поддерживаемый код

---

## 🚀 Начинай Сейчас!

1. Открой **V3DTO_WIDGET_QUICK_REFERENCE.md**
2. Скопируй **минимальный шаблон**
3. Адаптируй под своё
4. Следуй **V3DTO_WIDGET_PRECOMMIT_CHECKLIST.md**
5. Готово! 🎉

---

**Версия:** 1.0  
**Дата:** 2026-01-18  
**Всё что тебе нужно знать о v3dto виджетах в одном файле!**
