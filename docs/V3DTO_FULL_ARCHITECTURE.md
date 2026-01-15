# V3DTO - Полная архитектура и структура

## 📂 Структура файлов

```
c:\WORK\evol\
├── renderer/
│   ├── v2/                          ← СТАРАЯ версия (оставляем как есть)
│   │   ├── renderer.py
│   │   ├── gui_viewport.py
│   │   ├── gui_variablespanel.py
│   │   ├── gui_selected_creature.py
│   │   └── gui_selected_creature_history.py
│   │
│   └── v3dto/                       ← НОВАЯ версия (БЕЗ зависимостей от world/debug/logger)
│       ├── __init__.py              ✅ Экспорт публичного API
│       ├── dto.py                   ✅ Все DTO классы (8 основных классов)
│       ├── renderer.py              ✅ Renderer с factory методами для создания DTO
│       │
│       ├── gui_viewport_example.py  ✅ ПРИМЕР как переписать Viewport
│       ├── gui_viewport.py          ⏳ TODO: скопировать логику и переписать
│       ├── gui_variablespanel.py    ⏳ TODO: переписать для DTO
│       ├── gui_selected_creature.py ⏳ TODO: переписать для DTO
│       └── gui_selected_creature_history.py ⏳ TODO: переписать для DTO
│
├── docs/
│   ├── ARCHITECTURE_ANALYSIS.md         ← Полный анализ проблем
│   ├── V3DTO_MIGRATION_GUIDE.md         ← Полный гайд по миграции
│   ├── V3DTO_QUICK_START.md            ← Краткое резюме
│   └── V3DTO_FULL_ARCHITECTURE.md       ← ТЫ СЕЙЧАС ЧИТАЕШЬ ЭТО
│
└── tests/
    ├── test_viewport_v3dto.py       ⏳ TODO: юнит тесты для Viewport с DTO
    └── test_dto_classes.py          ⏳ TODO: юнит тесты для DTO
```

---

## 🏗️ Архитектурное решение

### Проблема (в v2)
```
Render слой (GUI):
├─ Viewport
│  ├─ Импортирует: from service.debugger.debugger import debug  ❌
│  ├─ Получает: world объект                                    ❌
│  └─ Знает о: внутренних структурах world                     ❌
│
├─ VariablesPanel
│  ├─ Импортирует: ничего, но получает world параметром       ❌
│  └─ Зависит от: изменения параметров в world                ❌
│
├─ SelectedCreaturePanel
│  ├─ Получает: world объект                                    ❌
│  └─ Вызывает: world.get_creature_by_id()                     ❌
│
└─ SelectedCreatureHistory
   ├─ Импортирует: from service.logger.logger import logme     ❌
   └─ Вызывает: logme.get_creature_energy_history()           ❌

Domain Layer (бизнес-логика):
├─ World (содержит creatures, foods, map)
├─ Debugger (синглтон с отладочными данными)
└─ Logger (синглтон с историей событий)

ПРОБЛЕМА: Render слой ТЕСНО привязан к Domain слою!
Невозможно тестировать Viewport без реального world и debugger.
```

### Решение (в v3dto)
```
Render слой (GUI):
├─ Viewport
│  ├─ Импортирует: DTO классы только                           ✅
│  ├─ Получает: RenderStateDTO параметром                      ✅
│  └─ Знает о: ТОЛЬКО структуре DTO                             ✅
│
├─ VariablesPanel
│  ├─ Импортирует: DTO классы только                           ✅
│  ├─ Получает: RenderStateDTO                                 ✅
│  └─ Зависит от: Callbacks система (не direct world access)   ✅
│
├─ SelectedCreaturePanel
│  ├─ Импортирует: DTO классы только                           ✅
│  ├─ Получает: RenderStateDTO                                 ✅
│  └─ Вызывает: только методы DTO                              ✅
│
└─ SelectedCreatureHistory
   ├─ Импортирует: DTO классы только                           ✅
   ├─ Получает: RenderStateDTO.selected_creature.history       ✅
   └─ БЕЗ импорта logger синглтона                             ✅

       ↑ DTO Layer (преобразование данных)
       │
Renderer (медиатор между Domain и Render)
├─ _prepare_world_dto()              ← world → WorldStateDTO
├─ _prepare_debug_dto()              ← debug → DebugDataDTO
├─ _prepare_simulation_params_dto()  ← simparams → SimulationParamsDTO
├─ _prepare_creature_history_dto()   ← logger → CreatureHistoryDTO
└─ _prepare_render_state_dto()       ← ВСЕ ДАННЫЕ → RenderStateDTO

Domain Layer (бизнес-логика):
├─ World (содержит creatures, foods, map)
├─ Debugger (синглтон с отладочными данными)
└─ Logger (синглтон с историей событий)

ПРЕИМУЩЕСТВО: Render слой ПОЛНОСТЬЮ отделен от Domain слоя!
Можно тестировать Viewport с mock DTO без реального world.
```

---

## 🎯 Основные DTO классы

### 1. **CreatureDTO** - Данные одного существа
```python
@dataclass
class CreatureDTO:
    id: int
    x: float
    y: float
    angle: float
    energy: float
    age: int
    speed: float
    generation: int
    bite_effort: float
    vision_distance: float
    bite_range: float
```
**Используется в:** SelectedCreaturePanel, Viewport (для отрисовки)

### 2. **WorldStateDTO** - Снимок состояния мира
```python
@dataclass
class WorldStateDTO:
    map: np.ndarray
    width: int
    height: int
    creatures: List[CreatureDTO]
    foods: List[FoodDTO]
    tick: int
    
    # Методы для поиска
    get_creature_by_id(creature_id)
    get_creature_at_position(x, y, radius)
```
**Используется в:** Viewport, (в будущем) FunctionKeysPanel

### 3. **CreatureHistoryDTO** - История существа
```python
@dataclass
class CreatureHistoryDTO:
    creature_id: int
    energy_history: List[float]
    events: List[CreatureEventDTO]
    
    # Свойства
    energy_min, energy_max, energy_current, lifespan
```
**Используется в:** SelectedCreatureHistory

### 4. **DebugDataDTO** - Отладочные данные
```python
@dataclass
class DebugDataDTO:
    raycast_dots: Optional[np.ndarray]
    all_visions: Optional[np.ndarray]
    all_outs: Optional[np.ndarray]
    
    # Методы
    is_empty() → bool
```
**Используется в:** Viewport (при отладке)

### 5. **SimulationParamsDTO** - Параметры симуляции
```python
@dataclass
class SimulationParamsDTO:
    mutation_probability: float
    mutation_strength: float
    creature_max_age: int
    food_amount: int
    # ... и еще 10+ параметров
    is_running: bool
    is_animating: bool
    is_logging: bool
```
**Используется в:** VariablesPanel

### 6. **RenderStateDTO** - ГЛАВНЫЙ DTO для всех виджетов
```python
@dataclass
class RenderStateDTO:
    world: WorldStateDTO
    params: SimulationParamsDTO
    debug: DebugDataDTO
    selected_creature: Optional[SelectedCreaturePanelDTO]
    current_state: str
    tick: int
    fps: int
    
    # Свойства
    population_count, food_count, is_selected_alive
```
**Используется в:** Все виджеты (главная точка входа)

---

## 📊 Поток преобразования данных

```
┌─────────────────────────────────────────────────────┐
│ Application.run()                                    │
│ ├─ world.update()                                   │
│ ├─ world.update_map()                               │
│ └─ renderer.draw()  ← Вызывает рендеринг            │
└─────────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────┐
│ Renderer.draw()                                      │
│ ├─ _prepare_render_state_dto()  ← ГЛАВНОЕ ПРЕОБРАЗО │
│ │  ├─ _prepare_world_dto()                          │
│ │  │  └─ world → WorldStateDTO                      │
│ │  ├─ _prepare_debug_dto()                          │
│ │  │  └─ debug singleton → DebugDataDTO             │
│ │  ├─ _prepare_simulation_params_dto()              │
│ │  │  └─ simparams → SimulationParamsDTO            │
│ │  └─ _prepare_selected_creature_dto()              │
│ │     └─ logger + world → CreatureHistoryDTO        │
│ │                                                    │
│ │  ⚠️ ТОЛЬКО ЗДЕСЬ происходит доступ к world/      │
│ │     debug/logger синглтонам!                      │
│ │                                                    │
│ └─→ RenderStateDTO (готов к передаче)              │
│                                                     │
├─ if state == 'main':                                │
│  └─ _draw_main(render_state)                        │
│     ├─ viewport.draw(screen, render_state)         │
│     ├─ selected_creature_panel.draw(...)           │
│     └─ selected_creature_history.draw(...)         │
│                                                     │
└─────────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────┐
│ Viewport.draw(screen, render_state)                 │
│ ├─ world_dto = render_state.world                   │
│ ├─ debug_dto = render_state.debug                   │
│ ├─ _draw_cells(world_dto)                           │
│ ├─ _draw_raycasts(debug_dto.raycast_dots)          │
│ └─ pygame.display.flip()                            │
│                                                     │
│ ⚠️ Viewport НЕ знает о world/debug синглтонах!      │
│    Только работает с DTO параметром                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Ключевые преимущества DTO архитектуры

### 1. **Слабая связанность (Loose Coupling)**
```python
# ❌ v2: Viewport прямо зависит от world
class Viewport:
    def __init__(self, world):
        self.world = world  # Tight coupling!

# ✅ v3dto: Viewport зависит только от DTO
class Viewport:
    def __init__(self):
        pass  # No dependency!
    
    def draw(self, screen, render_state):
        # Используем render_state.world, не self.world
```

### 2. **Полная тестируемость (100% Testability)**
```python
# ❌ v2: Нужен реальный world для тестирования Viewport
def test_viewport_v2():
    world = WorldGenerator.generate_world(100, 50, ...)  # Долго!
    viewport = Viewport(world)
    viewport.draw(screen, font)

# ✅ v3dto: Можно использовать mock DTO
def test_viewport_v3dto():
    mock_world_dto = WorldStateDTO(
        map=np.zeros((10, 10)),
        creatures=[CreatureDTO(id=1, x=5, y=5, ...)],
        foods=[],
        ...
    )
    render_state = RenderStateDTO(world=mock_world_dto, ...)
    
    viewport = Viewport()
    viewport.draw(screen, render_state)  # Быстро!
```

### 3. **Явные контракты (Explicit Contracts)**
```python
# ❌ v2: Непонятно какие данные нужны Viewport
def draw(self, screen, font, selected_creature_id=None, ...):
    # Какие еще параметры могут быть?

# ✅ v3dto: Явно видно что нужно Viewport
def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
    # IDE подскажет все доступные поля в render_state
    render_state.world.creatures
    render_state.world.foods
    render_state.debug.raycast_dots
    # ... и т.д.
```

### 4. **Гибкость источника данных (Data Source Flexibility)**
```python
# ❌ v2: Viewport жестко привязан к world объекту
class Viewport:
    def __init__(self, world):
        self.world = world  # Только мир, ничего больше

# ✅ v3dto: Можно легко менять источник данных
# Вариант 1: Реальный мир
world_dto = renderer._prepare_world_dto()

# Вариант 2: Сохраненная игра
saved_world_dto = load_from_file("game.save")

# Вариант 3: Replay
replay_world_dto = replay_manager.get_world_at_tick(50)

# Все работает с одним и тем же Viewport!
viewport.draw(screen, RenderStateDTO(world=world_dto, ...))
```

### 5. **Масштабируемость (Scalability)**
```python
# ❌ v2: Каждый виджет добавляет зависимость
class MyNewWidget:
    def __init__(self, world, debugger, logger, app, ...):
        self.world = world
        self.debugger = debugger
        self.logger = logger
        self.app = app
        # Много скрытых зависимостей!

# ✅ v3dto: Каждый виджет получает один параметр
class MyNewWidget:
    def __init__(self):
        pass  # Никаких зависимостей
    
    def draw(self, screen, render_state):
        # render_state содержит ВСЕ что нужно
        pass
```

---

## 🔄 Миграция с v2 на v3dto

### Шаг 1: Параллельная разработка
```python
# v2 остается работать как есть
from renderer.v2.renderer import Renderer as RendererV2

# v3dto разрабатывается отдельно
from renderer.v3dto.renderer import Renderer as RendererV3DTO

# В application.py используем конфиг
if USE_V3DTO:
    renderer = RendererV3DTO(world, app)
else:
    renderer = RendererV2(world, app)
```

### Шаг 2: Постепенная переписка виджетов
1. Переписать Viewport (самый критичный)
2. Переписать SelectedCreatureHistory (убрать logger)
3. Переписать SelectedCreaturePanel (простая переписка)
4. Переписать VariablesPanel (самый сложный)

### Шаг 3: Полная замена
```python
# Когда все виджеты переписаны:
from renderer.v3dto.renderer import Renderer

# Удалить v2
# rm -r renderer/v2
```

---

## 📝 Обязательные файлы для v3dto

| Файл | Статус | Описание |
|------|--------|---------|
| `__init__.py` | ✅ ГОТОВО | Публичный API v3dto |
| `dto.py` | ✅ ГОТОВО | Все DTO классы (CreatureDTO, WorldStateDTO, и т.д.) |
| `renderer.py` | ✅ ГОТОВО | Главный Renderer с factory методами |
| `gui_viewport_example.py` | ✅ ГОТОВО | ПРИМЕР как переписать Viewport |
| `gui_viewport.py` | ⏳ TODO | Viewport с поддержкой RenderStateDTO |
| `gui_variablespanel.py` | ⏳ TODO | VariablesPanel с системой callbacks |
| `gui_selected_creature.py` | ⏳ TODO | SelectedCreaturePanel с DTO |
| `gui_selected_creature_history.py` | ⏳ TODO | SelectedCreatureHistory с DTO |

---

## 🚀 Следующие шаги (для тебя)

### Сейчас (инфраструктура готова):
1. ✅ Создана папка v3dto
2. ✅ Созданы все DTO классы (dto.py)
3. ✅ Создан Renderer с factory методами (renderer.py)
4. ✅ Создан пример переписки Viewport (gui_viewport_example.py)
5. ✅ Написана полная документация

### Дальше (переписка виджетов):
1. Скопировать логику из gui_viewport.py (v2) в v3dto/gui_viewport.py
2. Заменить `self.world` на `render_state.world`
3. Заменить `debug.get()` на `render_state.debug.*`
4. Удалить импорты debugger синглтона
5. Тестировать

### Затем (интеграция):
1. Обновить renderer.py чтобы использовать переписанные виджеты
2. Обновить application.py использовать v3dto.Renderer
3. Удалить v2 если она больше не нужна

---

## 💡 Важные моменты

### 1. Renderer - это медиатор
```python
# Renderer получает "грязные" данные из Domain Layer
world      # Сложный объект с множеством методов
debug      # Синглтон с случайными данными
logger     # Синглтон с историей

# Преобразует их в "чистые" DTO для Presentation Layer
RenderStateDTO(
    world=WorldStateDTO(...),      # Только необходимые данные
    debug=DebugDataDTO(...),       # Структурированные данные
    ...
)
```

### 2. Виджеты - это "тупые" визуализаторы
```python
# Старый способ (v2):
# Viewport должна уметь: найти creatures в world, получить raycast из debug, и т.д.
# Viewport обязана знать о внутренней структуре world

# Новый способ (v3dto):
# Viewport только отрисовывает то что ей дано в render_state
# Viewport не знает как получить эти данные
```

### 3. RenderStateDTO - единая точка входа
```python
# Вместо того, чтобы передавать множество параметров:
viewport.draw(screen, font, world, debugger, selected_id, app, ...)

# Передаем один параметр, который содержит ВСЕ необходимое:
viewport.draw(screen, render_state)
```

---

## 📚 Связанная документация

- **[ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md)** - Полный анализ проблем
- **[V3DTO_MIGRATION_GUIDE.md](V3DTO_MIGRATION_GUIDE.md)** - Пошаговый гайд по миграции каждого виджета
- **[V3DTO_QUICK_START.md](V3DTO_QUICK_START.md)** - Краткое резюме архитектуры

---

## ✅ Итого

✨ **v3dto - это полная переработка архитектуры рендеринга с целью:**
- Полной изоляции Domain Logic от Presentation Logic
- Использования DTO для явных контрактов между слоями
- Полной тестируемости виджетов без зависимостей
- Гибкости для смены источников данных

💪 **Инфраструктура полностью готова, остается только переписать виджеты!**
