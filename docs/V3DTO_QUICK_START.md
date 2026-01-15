# V3DTO - Краткое резюме архитектуры

## 📦 Что создано

### 1. **dto.py** - Полная иерархия DTO классов
```
CreatureDTO              ← Отдельное существо
FoodDTO                  ← Отдельная пища
WorldStateDTO            ← Снимок мира (creatures, foods, map)
  ├── get_creature_by_id()
  └── get_creature_at_position()

CreatureEventDTO         ← Событие в истории существа
CreatureHistoryDTO       ← История энергии + события
  ├── energy_min
  ├── energy_max
  ├── energy_current
  └── lifespan

DebugDataDTO            ← Отладочные данные (raycast_dots, visions, outs)
SimulationParamsDTO     ← Все параметры симуляции

SelectedCreaturePanelDTO ← Комбо: creature + history для выбранного существа

RenderStateDTO          ← ГЛАВНЫЙ DTO: полный снимок для всех виджетов
  ├── world: WorldStateDTO
  ├── params: SimulationParamsDTO
  ├── debug: DebugDataDTO
  ├── selected_creature: SelectedCreaturePanelDTO
  ├── current_state: str
  ├── tick: int
  ├── fps: int
  └── Свойства: population_count, food_count, is_selected_alive
```

### 2. **renderer.py** - Renderer с архитектурой DTO

#### Factory методы для преобразования:
```python
_prepare_creature_dto()          # Creature → CreatureDTO
_prepare_food_dto()              # Food → FoodDTO
_prepare_world_dto()             # world → WorldStateDTO
_prepare_debug_dto()             # debug синглтон → DebugDataDTO
_prepare_simulation_params_dto()  # simparams → SimulationParamsDTO
_prepare_creature_history_dto()   # logger → CreatureHistoryDTO
_prepare_selected_creature_dto()  # комбо → SelectedCreaturePanelDTO
_prepare_render_state_dto()       # ВСЕ ДАННЫЕ → RenderStateDTO
```

#### Главный метод:
```python
draw() → _prepare_render_state_dto() → передает в виджеты
```

---

## 🏗️ Архитектурная разница: v2 vs v3dto

### v2 (текущая - ПЛОХО):
```
world ──┐
debugger├─→ Renderer ──┐
logger ──┤            ├─→ viewport.draw(world, debugger, logger)
                      ├─→ panel.draw(world)
                      └─→ history.draw(logger)

Проблемы:
❌ Виджеты прямо зависят от world/debugger/logger
❌ Невозможно тестировать виджеты отдельно
❌ Синглтоны создают скрытые зависимости
❌ Сложно менять источник данных
```

### v3dto (новая - ХОРОШО):
```
world ──┐
debugger├─→ Renderer._prepare_*_dto() ──→ RenderStateDTO ──┐
logger ──┤                                                  ├─→ viewport.draw(render_state)
                                                           ├─→ panel.draw(render_state)
                                                           └─→ history.draw(render_state)

Преимущества:
✅ Виджеты работают только с DTO
✅ Виджеты полностью тестируемы
✅ Явные контракты между слоями
✅ Легко менять источник данных
```

---

## 📍 Расположение файлов

```
renderer/
├── v2/                  ← Старая версия (работает как раньше)
│   ├── renderer.py
│   ├── gui_viewport.py
│   ├── gui_variablespanel.py
│   └── ...
│
├── v3dto/              ← НОВАЯ версия (с DTO архитектурой)
│   ├── __init__.py     ← Экспорт публичного API
│   ├── dto.py          ← Все DTO классы
│   ├── renderer.py     ← Главный Renderer с factory методами
│   │
│   ├── gui_viewport.py          ← TODO: переписать для DTO
│   ├── gui_variablespanel.py    ← TODO: переписать для DTO
│   ├── gui_selected_creature.py ← TODO: переписать для DTO
│   └── gui_selected_creature_history.py ← TODO: переписать для DTO
│
└── mock/               ← Mock renderer для тестирования
```

---

## 🚀 Как это использовать

### Вариант 1: Переключиться на v3dto (когда виджеты готовы)
```python
# application.py
from renderer.v3dto.renderer import Renderer  # Вместо v2

app = Application()
app.run()
```

### Вариант 2: Тестировать отдельный виджет БЕЗ world
```python
# tests/test_viewport_dto.py
import pytest
from renderer.v3dto.dto import WorldStateDTO, RenderStateDTO
from renderer.v3dto.gui_viewport import Viewport  # Когда переписана

# Создаем mock DTO (совсем без world!)
world_dto = WorldStateDTO(
    map=np.zeros((10, 10)),
    creatures=[CreatureDTO(...)],
    foods=[],
    ...
)

render_state = RenderStateDTO(world=world_dto, ...)

viewport = Viewport()  # БЕЗ параметров!
viewport.draw(screen, render_state)  # Работает!
```

---

## 📊 Статус готовности

| Компонент | Статус | Описание |
|-----------|--------|---------|
| **DTO классы** | ✅ ГОТОВО | Все DTO определены в dto.py |
| **Renderer** | ✅ ГОТОВО | Все factory методы реализованы |
| **Viewport** | ⏳ NEXT | Нужно переписать для RenderStateDTO |
| **VariablesPanel** | ⏳ TODO | Нужна система callbacks |
| **SelectedCreaturePanel** | ⏳ TODO | Простая переписка |
| **SelectedCreatureHistory** | ⏳ TODO | Убрать импорт logger |

---

## 🎯 Следующие шаги (по приоритету)

### 1. Переписать Viewport (CRITICAL)
- Файл: `renderer/v3dto/gui_viewport.py`
- Изменения:
  - Удалить: `from service.debugger.debugger import debug`
  - Изменить: `__init__(self)` без параметров
  - Изменить: `draw(screen, render_state)` вместо `draw(screen, font, world=...)`
  - Все `self.world.*` → `render_state.world.*`
  - Все `debug.get()` → `render_state.debug.*`

### 2. Переписать SelectedCreatureHistory
- Файл: `renderer/v3dto/gui_selected_creature_history.py`
- Изменения:
  - Удалить: `from service.logger.logger import logme`
  - Используемые данные: `render_state.selected_creature.history`

### 3. Переписать SelectedCreaturePanel
- Файл: `renderer/v3dto/gui_selected_creature.py`
- Изменения:
  - Используемые данные: `render_state.selected_creature.creature`

### 4. Переписать VariablesPanel (СЛОЖНАЯ)
- Файл: `renderer/v3dto/gui_variablespanel.py`
- Изменения:
  - Система callbacks для изменения параметров
  - Используемые данные: `render_state.params`

### 5. Интеграция
- Обновить `application.py` использовать v3dto.Renderer
- Удалить v2 когда v3dto полностью готова

---

## 💡 Ключевые идеи

### 1. Renderer - Медиатор между Domain и Presentation
```python
# Renderer получает данные из Domain Layer
world, debugger, logger

# Преобразует их в Presentation Layer контракты
render_state = RenderStateDTO

# Передает в виджеты (которые не знают о Domain)
viewport.draw(render_state)
```

### 2. RenderStateDTO - Единая точка входа
```python
# Вместо:
viewport.draw(screen, font, world, debugger, logger, selected_id, ...)

# Пишем:
viewport.draw(screen, render_state)
# render_state содержит ВСЕ необходимые данные
```

### 3. Полная тестируемость
```python
# Может тестировать Viewport БЕЗ world!
world_dto = create_mock_world_dto()
render_state = RenderStateDTO(world=world_dto, ...)
viewport.draw(screen, render_state)

# Никаких побочных эффектов, никаких синглтонов
```

---

## 📚 Документация

- [ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md) - Полный анализ проблем и решений
- [V3DTO_MIGRATION_GUIDE.md](V3DTO_MIGRATION_GUIDE.md) - Полный гайд по миграции каждого виджета

---

## ✨ Преимущества этого подхода

1. **Слабая связанность** - Виджеты не знают о world/debugger/logger
2. **Тестируемость** - Легко создавать mock DTO для тестирования
3. **Явные контракты** - RenderStateDTO четко определяет что нужно виджету
4. **Гибкость** - Легко менять источник данных (e.g., replay, save/load)
5. **Масштабируемость** - Легко добавить новые виджеты и параметры
6. **Производительность** - Преобразование в DTO можно оптимизировать отдельно
7. **Поддержка** - Явные типы (dataclass) помогают IDE и mypy

---

## 🔗 Связанные файлы

- `/renderer/v3dto/dto.py` - Определения всех DTO
- `/renderer/v3dto/renderer.py` - Renderer с factory методами
- `/renderer/v3dto/__init__.py` - Публичный API
- `/docs/ARCHITECTURE_ANALYSIS.md` - Полный анализ
- `/docs/V3DTO_MIGRATION_GUIDE.md` - Гайд по миграции
