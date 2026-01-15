# Архитектурный анализ Renderer: изоляция данных

## 📋 Текущее состояние: Проблемы с утечками данных

### 1. **Диагноз проблемы**

Renderer и его виджеты страдают от **тесной связанности** с источниками данных:

```
┌─────────────────────────────────────────────────────────┐
│ Renderer & Widgets (Presentation Layer)                 │
├─────────────────────────────────────────────────────────┤
│ ✗ Получает world напрямую                               │
│ ✗ Обращается к world.creatures[] прямо                 │
│ ✗ Читает из singleton debug в нескольких виджетах       │
│ ✗ Читает из singleton logme в SelectedCreatureHistory   │
│ ✗ Может писать в world.map напрямую                     │
└─────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    ┌────────┐          ┌─────────┐         ┌──────────┐
    │ world  │          │ debug   │         │ logme    │
    │ (data) │          │(global) │         │(global)  │
    └────────┘          └─────────┘         └──────────┘
```

**Последствия:**
- Сложно тестировать виджеты отдельно от world
- Трудно поменять источник данных (e.g., сохранённую игру)
- Синглтоны создают скрытые зависимости
- Изменение структуры world ломает renderer

---

## 2. **Точки утечки данных в коде**

### 📍 **Viewport** (`gui_viewport.py:8`)
```python
from service.debugger.debugger import debug

# Использование:
debug.set("raycast_dots", raycast_dots)  # Пишет в синглтон
```
**Проблема:** Viewport зависит от глобального состояния для отладки

---

### 📍 **VariablesPanel** (`gui_variablespanel.py:44-45`)
```python
def __init__(self, world):
    self.world = world  # Жёсткая зависимость от конкретного world
```
**Проблема:** Прямой доступ к world для чтения/изменения параметров

---

### 📍 **SelectedCreaturePanel** (`gui_selected_creature.py:44-45`)
```python
def __init__(self, world):
    self.world = world  # Получает существо по ID через world
    
def draw(self, screen, selected_creature_id):
    selected_creature = self.world.get_creature_by_id(selected_creature_id)
```
**Проблема:** Зависит от world для получения данных существа

---

### 📍 **SelectedCreatureHistory** (`gui_selected_creature_history.py:15, 69`)
```python
from service.logger.logger import logme

def draw(self, screen, selected_creature_id):
    selected_creature = self.world.get_creature_by_id(selected_creature_id)  # world
    # ... потом использует logme напрямую
```
**Проблема:** Прямой доступ к глобальному logme синглтону

---

### 📍 **Renderer** (`renderer.py:21`)
```python
from service.logger.logger import logme

# Получает world в __init__
self.world = world
```
**Проблема:** Координатор получает world и пробрасывает его виджетам

---

## 3. **Архитектурное решение: Паттерн Data Contracts**

### 🎯 Идея: Изолировать Presentation от Domain

Вместо того, чтобы Renderer получал `world` и синглтоны, он должен работать с **контрактами данных** (Data Transfer Objects / DTO):

```
┌──────────────────────────────────────┐
│ Application Layer                    │
│ (знает о world, debugger, logger)    │
└──────────────────────────────────────┘
           ↓
    ┌────────────────────┐
    │ Data Contracts     │  ← Отформатированные данные
    │ (DTO/View Models)  │
    └────────────────────┘
           ↓
┌──────────────────────────────────────┐
│ Renderer & Widgets                   │
│ (работают только с contracts)        │
│ (не знают о world/debug/logger)      │
└──────────────────────────────────────┘
```

---

## 4. **Реализация: Пошаговый план**

### **Этап 1: Создать Data Contracts (dto.py)**

```python
# renderer/v2/dto.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class CreatureDTO:
    """Данные существа для отображения"""
    id: int
    x: float
    y: float
    angle: float
    energy: float
    age: int
    # ... остальные поля, которые нужны для рендеринга

@dataclass
class WorldStateDTO:
    """Снимок состояния мира для рендеринга"""
    map: Any  # numpy array
    width: int
    height: int
    creatures: List[CreatureDTO]
    foods: List[tuple]  # (x, y)
    tick: int

@dataclass
class CreatureHistoryDTO:
    """История и события существа"""
    creature_id: int
    energy_history: List[float]
    events: List[Dict[str, Any]]  # [{tick, type, value}, ...]
    
@dataclass
class DebugDataDTO:
    """Debug информация"""
    raycast_dots: Any  # numpy array
    all_visions: Any   # numpy array
    all_outs: Any      # numpy array
    # ... и т.д.
```

---

### **Этап 2: Создать View Models в Renderer**

Renderer получает world, но преобразует его в DTO:

```python
# renderer/v2/renderer.py

class Renderer:
    def __init__(self, world, app):
        self.world = world  # Храним, но НЕ пробрасываем виджетам
        self.app = app
        
        # Виджеты получают None по умолчанию
        self.viewport = Viewport()
        self.variables_panel = VariablesPanel()
        self.selected_creature_panel = SelectedCreaturePanel()
        
    def draw(self):
        """Главный цикл отрисовки - конвертирует data в contracts"""
        
        # 1. Собрать данные из world в DTO
        world_dto = self._prepare_world_dto()
        debug_dto = self._prepare_debug_dto()
        history_dto = self._prepare_history_dto(self.selected_creature_id) if self.selected_creature_id else None
        
        # 2. Передать DTO виджетам (они не знают о world)
        self.viewport.draw(screen, world_dto)
        self.variables_panel.draw(screen, world_dto)
        if history_dto:
            self.selected_creature_panel.draw(screen, self.selected_creature_id, world_dto)
            self.selected_creature_history.draw(screen, history_dto)
    
    # DTO factories
    def _prepare_world_dto(self) -> WorldStateDTO:
        """Собрать снимок world в DTO"""
        creatures_dto = [
            CreatureDTO(
                id=c.id, x=c.x, y=c.y, angle=c.angle,
                energy=c.energy, age=c.age, ...
            )
            for c in self.world.creatures
        ]
        return WorldStateDTO(
            map=self.world.map,
            width=self.world.width,
            height=self.world.height,
            creatures=creatures_dto,
            foods=[(f.x, f.y) for f in self.world.foods],
            tick=self.world.tick
        )
    
    def _prepare_debug_dto(self) -> DebugDataDTO:
        """Собрать debug data из синглтона в DTO"""
        return DebugDataDTO(
            raycast_dots=debug.get("raycast_dots"),
            all_visions=debug.get("all_visions"),
            all_outs=debug.get("all_outs")
        )
    
    def _prepare_history_dto(self, creature_id: int) -> CreatureHistoryDTO:
        """Собрать историю из logger в DTO"""
        return CreatureHistoryDTO(
            creature_id=creature_id,
            energy_history=logme.get_creature_energy_history(creature_id),
            events=logme.get_creature_events(creature_id)
        )
```

---

### **Этап 3: Переписать виджеты, чтобы они принимали DTO**

**Viewport:**
```python
# renderer/v2/gui_viewport.py
class Viewport:
    def __init__(self):
        """Инициализация без world!"""
        self.camera_offset = ...
        self.camera_scale = ...
    
    def draw(self, screen: pygame.Surface, world_dto: WorldStateDTO, debug_dto: Optional[DebugDataDTO] = None):
        """Отрисовка получает данные через DTO"""
        # Используем world_dto.map, world_dto.creatures вместо self.world
        map_data = world_dto.map
        creatures = world_dto.creatures
        
        # Если есть debug данные, используем их для отладки
        if debug_dto and debug_dto.raycast_dots is not None:
            self._draw_debug_raycasts(debug_dto.raycast_dots)
```

**VariablesPanel:**
```python
# renderer/v2/gui_variablespanel.py
class VariablesPanel:
    def __init__(self):
        """Инициализация без world!"""
        self.variables = {...}
    
    def draw(self, screen: pygame.Surface, world_dto: WorldStateDTO):
        """Отрисовка получает данные через DTO"""
        # Отрисовываем переменные
        # При изменении пользователем - возвращаем callback
        pass
    
    def on_variable_changed(self, name: str, value: Any) -> Callable:
        """Возвращает callback, который Application'я должен обработать"""
        return lambda: self._on_change_callback(name, value)
```

**SelectedCreaturePanel:**
```python
# renderer/v2/gui_selected_creature.py
class SelectedCreaturePanel:
    def __init__(self):
        """Инициализация без world!"""
        pass
    
    def draw(self, screen: pygame.Surface, creature_id: int, world_dto: WorldStateDTO):
        """Отрисовка получает данные через DTO"""
        # Находим существо в DTO
        creature = next((c for c in world_dto.creatures if c.id == creature_id), None)
        if not creature:
            return
        # Отрисовываем информацию
```

**SelectedCreatureHistory:**
```python
# renderer/v2/gui_selected_creature_history.py
class SelectedCreatureHistory:
    def __init__(self):
        """Инициализация без world и logger!"""
        pass
    
    def draw(self, screen: pygame.Surface, history_dto: CreatureHistoryDTO):
        """Отрисовка получает данные через DTO"""
        # Используем history_dto.energy_history и history_dto.events
        # Больше нет зависимости от logme синглтона!
```

---

## 5. **Альтернативные архитектуры (Сравнение)**

### ❌ **Текущая архитектура (Tight Coupling)**
- **Преимущества:** Просто реализовать быстро
- **Недостатки:** 
  - Невозможно тестировать виджеты отдельно
  - Синглтоны создают скрытые зависимости
  - Сложно менять источник данных

### ✅ **Рекомендуемая (DTO/Data Contracts)**
- **Преимущества:**
  - Полная изоляция Presentation от Domain
  - Легко тестировать (подсунуть mock DTO)
  - Явные зависимости
  - Легко менять источник данных
- **Недостатки:** Нужно создать DTO классы (~100 строк кода)

### 🔄 **Альтернатива 1: Dependency Injection + Interfaces**
```python
class IWorldDataProvider:
    def get_creatures(self) -> List[CreatureDTO]: pass
    def get_map(self) -> np.ndarray: pass

# Renderer инъектирует provider в виджеты
viewport = Viewport(data_provider=world_provider)
```
- **Плюсы:** Гибче чем DTO, но сложнее
- **Минусы:** Более объёмный код

### 📊 **Альтернатива 2: Event-Driven Architecture**
```python
# Вместо "Renderer спрашивает world"
# "World отправляет events, которые слушает Renderer"

event_bus.subscribe("creature_moved", viewport.on_creature_moved)
event_bus.subscribe("food_spawned", viewport.on_food_spawned)
```
- **Плюсы:** Максимальная развязка
- **Минусы:** Сложнее отладить, overhead на события

---

## 6. **Рекомендация по Приоритету Реализации**

### 🥇 **Приоритет 1: Viewport** (самый критичный)
- Использует `debug` синглтон для raycast_dots
- Частая отрисовка → большой overhead
- **Реализация:** Убрать `from service.debugger.debugger import debug`

```python
# ДО:
class Viewport:
    def _draw_cells(self, ...):
        debug.set("raycast_dots", ...)

# ПОСЛЕ:
class Viewport:
    def _draw_cells(self, screen, world_dto: WorldStateDTO, debug_dto: DebugDataDTO = None):
        if debug_dto:
            # Используем debug_dto.raycast_dots
```

### 🥈 **Приоритет 2: VariablesPanel**
- Зависит от world для чтения/изменения параметров
- Нужны callbacks в Application

### 🥉 **Приоритет 3: SelectedCreatureHistory**
- Зависит от logger синглтона
- Менее критично для основного цикла

---

## 7. **Примеры миграции кода**

### ✅ Правильно (с DTO)
```python
# renderer.py
def draw(self):
    world_dto = self._prepare_world_dto()
    self.viewport.draw(screen, world_dto)
    
# viewport.py
def draw(self, screen, world_dto):
    for creature in world_dto.creatures:
        self._render_creature(creature)
```

### ❌ Неправильно (старый способ)
```python
# renderer.py
self.viewport = Viewport(world=self.world)

# viewport.py
class Viewport:
    def __init__(self, world):
        self.world = world  # Tight coupling!
```

---

## 8. **Миграционная стратегия**

### **Шаг 1: Параллельная разработка** (Низкий риск)
```
v2_new/
├── dto.py                    ← Новая функциональность
├── renderer_new.py           ← Новый renderer (с DTO)
├── gui_viewport_new.py       ← Новый viewport (без world)
└── ...

v2/                           ← Старая функциональность (работает как есть)
├── renderer.py
├── gui_viewport.py
└── ...
```

### **Шаг 2: Постепенная миграция**
1. Реализовать DTO для каждого типа данных
2. Создать factory методы в Renderer для преобразования
3. Переписать виджеты один за другим
4. Удалить старые файлы

### **Шаг 3: Тестирование**
```python
# tests/test_viewport_with_dto.py
def test_viewport_renders_creatures():
    world_dto = WorldStateDTO(
        map=np.zeros((10, 10)),
        creatures=[CreatureDTO(id=1, x=5, y=5, ...)],
        # ...
    )
    viewport = Viewport()
    screen = pygame.Surface((100, 100))
    viewport.draw(screen, world_dto)  # Не нужен реальный world!
```

---

## 9. **Checklist для реализации**

- [ ] Создать `renderer/v2/dto.py` с классами DTO
- [ ] Добавить factory методы в `renderer.py` для создания DTO
- [ ] Переписать `gui_viewport.py` чтобы принимать DTO
- [ ] Убрать `from service.debugger.debugger import debug` из viewport
- [ ] Переписать `gui_variablespanel.py` чтобы принимать DTO
- [ ] Переписать `gui_selected_creature.py` чтобы принимать DTO
- [ ] Переписать `gui_selected_creature_history.py` чтобы принимать DTO + history_dto
- [ ] Убрать `from service.logger.logger import logme` из widgets
- [ ] Обновить все вызовы `widget.draw()` в `renderer.py`
- [ ] Добавить юнит-тесты для виджетов

---

## 10. **Дополнительные улучшения**

### 💡 Параллельно можно реализовать:

1. **State Management** - Renderer как state manager
2. **Observer Pattern** - для сообщения об изменениях из виджетов
3. **Dependency Container** - для инъекции зависимостей

---

## Вывод

**Основная идея:** Renderer должен быть "глупым" - работать только с данными в форме контрактов (DTO), а не обращаться напрямую к world и синглтонам. Application (или специальный слой Data Aggregation) отвечает за:

1. Получение данных из world
2. Чтение из синглтонов (debug, logger)
3. Преобразование в DTO
4. Передача DTO в Renderer/виджеты

Это даст вам:
- ✅ Полную тестируемость
- ✅ Слабую связанность
- ✅ Лёгкую поддержку
- ✅ Возможность менять источник данных
- ✅ Явные контракты между слоями
