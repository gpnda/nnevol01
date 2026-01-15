# 🚀 CreaturesListModal - Быстрый старт

## Что это?

Переносимый компонент из v1 в v3dto архитектуру - модальное окно со списком существ в стиле BIOS.

## Файлы

| Файл | Назначение |
|------|-----------|
| `renderer/v3dto/gui_creatures_list.py` | 🆕 Новый v3dto виджет |
| `docs/CREATURES_LIST_MIGRATION.md` | Полная миграционная документация |
| `docs/CREATURES_LIST_EXAMPLES.md` | Примеры использования и тестирования |
| `renderer/v1/gui_creatures_popup.py` | 📦 Старая версия (сохранена для справки) |

## Интеграция в Renderer (3 шага)

### 1️⃣ Импорт + инициализация
```python
# renderer/v3dto/renderer.py

from renderer.v3dto.gui_creatures_list import CreaturesListModal

class Renderer:
    def __init__(self, world, app):
        # ...
        self.creatures_list_modal = CreaturesListModal()
```

### 2️⃣ Обработка событий
```python
def _handle_keyboard_creatures_list(self, event):
    """Обработка клавиш: UP/DOWN, HOME/END, ESC"""
    creatures_count = len(self.world.creatures)
    
    if event.key == pygame.K_UP:
        self.creatures_list_modal.move_selection_up(creatures_count)
    elif event.key == pygame.K_DOWN:
        self.creatures_list_modal.move_selection_down(creatures_count)
    elif event.key == pygame.K_HOME:
        self.creatures_list_modal.move_selection_home()
    elif event.key == pygame.K_END:
        self.creatures_list_modal.move_selection_end(creatures_count)
    elif event.key in (pygame.K_ESCAPE, pygame.K_F1):
        self.set_state('main')
```

### 3️⃣ Отрисовка
```python
def _draw_creatures_list(self, render_state):
    """Одна строка!"""
    self.creatures_list_modal.draw(self.screen, render_state)
```

## Архитектура v3dto ✅

```
CreaturesListModal
├─ Constants: позиция, размер, цвета, шрифт
├─ __init__(): инициализация (NO PARAMETERS!)
├─ draw(screen, render_state): отрисовка
├─ Navigation methods: move_selection_*()
└─ Isolated: ZERO singletons!
```

## Клавиши управления

| Клавиша | Действие |
|---------|----------|
| ⬆️ UP | Выделение на строку вверх |
| ⬇️ DOWN | Выделение на строку вниз |
| Home | Прыжок на первое существо |
| End | Прыжок на последнее существо |
| ESC / F1 | Закрытие окна |

## Столбцы таблицы

```
ID  Age  X      Y      Energy  Speed  Gen
─────────────────────────────────────────
0   100  10.0   20.0   80.0    1.00   2
1   50   15.0   25.0   60.0    0.80   1
```

## v3dto Паттерны

### ✅ Constants Configuration
```python
POPUP_WIDTH = 600
COLORS = {'bg': (5, 41, 158), ...}
FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
```

### ✅ Zero-Dependency Init
```python
def __init__(self):
    # НЕ принимает параметры
    # НЕ обращается к синглтонам
```

### ✅ draw() Method
```python
def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO'):
    # Все данные из render_state
    creatures = render_state.world.creatures
```

### ✅ DTO Isolation
```
Старая версия:        Новая версия:
╔═══════════════╗     ╔════════════════════╗
║ CreaturesPopup║     ║ CreaturesListModal║
║  + world      │────▶│  + render_state    │
╚═══════════════╝     ╚════════════════════╝
   (зависит)         (изолирован)
```

## Состояние машины Renderer

```
          F1
    ┌─────────┐
    ▼         │
main ◄────────┤ creatures_list
     ESC/F1   │
    ▲         │
    └─────────┘
```

## Методы для вызова из Renderer

```python
# Навигация
modal.move_selection_up(creatures_count)
modal.move_selection_down(creatures_count)
modal.move_selection_home()
modal.move_selection_end(creatures_count)

# Состояние
modal.reset()  # Сброс при открытии

# Отрисовка
modal.draw(screen, render_state)

# Получение данных
id = modal.get_selected_creature_id(creatures_count)
```

## Жизненный цикл

```
1. F1 нажата
   └─▶ set_state('creatures_list')
   
2. _on_state_enter() вызвана
   └─▶ modal.reset()
   
3. User пользуется навигацией
   └─▶ modal.move_selection_*()
   
4. draw() каждый фрейм
   └─▶ modal.draw(screen, render_state)
   
5. ESC нажата
   └─▶ set_state('main')
   
6. Окно закрыто
   └─▶ Больше не рисуется
```

## Проверка ✅

- [x] Создан v3dto виджет
- [x] Интегрирован в Renderer
- [x] Обработка клавиатуры
- [x] Отрисовка
- [x] Состояние машины
- [x] Документация
- [ ] Протестировано в runtime

## Быстрые проверки

**Открывается ли окно?**
```python
# F1 нажато → set_state('creatures_list') → draw() вызывает _draw_creatures_list()
```

**Работает ли навигация?**
```python
# UP/DOWN → move_selection_*() → scroll_offset/selected_index обновлены
```

**Видны ли данные?**
```python
# render_state.world.creatures содержит CreatureDTO объекты
```

## Будущие возможности

- [ ] Enter для выбора существа
- [ ] Сортировка по столбцам (S)
- [ ] Поиск по ID (Ctrl+F)
- [ ] Фильтрация по энергии
- [ ] Экспорт в CSV

## Контактные лица

- **Разработчик**: GitHub Copilot
- **Дата миграции**: 2026-01-16
- **Версия**: 1.0 (v3dto)
- **Статус**: ✅ Ready for use

---

**Начните отсюда**: [CREATURES_LIST_MIGRATION.md](CREATURES_LIST_MIGRATION.md)  
**Примеры**: [CREATURES_LIST_EXAMPLES.md](CREATURES_LIST_EXAMPLES.md)
