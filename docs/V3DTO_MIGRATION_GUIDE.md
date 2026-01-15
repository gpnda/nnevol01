# V3DTO - Миграция виджетов на DTO архитектуру

## 📋 Статус

**v3dto/renderer.py**: ✅ Создан - работает как v2, но преобразует все данные в DTO  
**v3dto/dto.py**: ✅ Создан - все DTO классы для изоляции данных  
**v3dto/__init__.py**: ✅ Создан - экспорт публичного API  

**Виджеты**: ⏳ Следующий этап - переписать для работы с DTO

---

## 🎯 Архитектура v3dto

### Текущий поток данных (старый - v2):
```
world → Renderer → Viewport(world)
              ↓
          VariablesPanel(world)
              ↓
        SelectedCreaturePanel(world)
              
debugger → [множество виджетов]
logger → [множество виджетов]
```

### Новый поток данных (v3dto):
```
world ──┐
debugger├─→ Renderer._prepare_*_dto() ──→ RenderStateDTO
logger ──┤                                      ↓
         └────────────→ Viewport(render_state)
                       VariablesPanel(render_state)
                       SelectedCreaturePanel(render_state)
                       ... и т.д.
```

### Ключевые улучшения:
- ✅ **Изоляция**: Виджеты НЕ знают о world, debugger, logger
- ✅ **Явные контракты**: RenderStateDTO - единая точка входа
- ✅ **Тестируемость**: Можно создавать mock DTO без реального world
- ✅ **Гибкость**: Легко менять источник данных (e.g., сохраненная игра)

---

## 📐 DTO классы (в dto.py)

### Основные DTO:

| DTO | Используется | Описание |
|-----|-------------|---------|
| **WorldStateDTO** | Viewport | Снимок мира (map, creatures, foods) |
| **CreatureDTO** | SelectedCreaturePanel | Данные одного существа |
| **CreatureHistoryDTO** | SelectedCreatureHistory | История энергии + события |
| **DebugDataDTO** | Viewport (отладка) | raycast_dots, all_visions, all_outs |
| **SimulationParamsDTO** | VariablesPanel | Все параметры симуляции |
| **RenderStateDTO** | Все виджеты | ПОЛНЫЙ снимок состояния |

### Главная идея - RenderStateDTO:

```python
render_state = renderer._prepare_render_state_dto()

# Теперь передаем render_state ВСЕ виджетам:
viewport.draw(screen, render_state)
variables_panel.draw(screen, render_state)
selected_creature_panel.draw(screen, render_state)
```

---

## 🔧 Как переписать виджет для DTO

### Пример: Переписать Viewport

#### ДО (v2):
```python
# gui_viewport.py (v2)
from service.debugger.debugger import debug

class Viewport:
    def __init__(self, world=None):
        self.world = world  # ❌ Прямая зависимость от world
    
    def draw(self, screen, font, selected_creature_id=None):
        # Используем self.world напрямую
        for creature in self.world.creatures:
            self._render_creature(creature)
        
        # Используем debug синглтон напрямую
        raycast_dots = debug.get("raycast_dots")
```

#### ПОСЛЕ (v3dto):
```python
# gui_viewport.py (v3dto)
# ✅ НЕТ импорта debugger!
# ✅ НЕТ импорта world!

from renderer.v3dto.dto import RenderStateDTO, WorldStateDTO

class Viewport:
    def __init__(self):  # ✅ НЕ принимает world
        # Только UI параметры
        self.camera_offset = ...
        self.camera_scale = ...
    
    def draw(self, screen, render_state: RenderStateDTO):
        # ✅ Данные из DTO, не из world
        world_dto = render_state.world
        
        for creature in world_dto.creatures:
            self._render_creature(creature)
        
        # ✅ Debug данные из DTO, не из синглтона
        if render_state.debug.raycast_dots is not None:
            self._draw_debug_raycasts(render_state.debug.raycast_dots)
```

### Ключевые изменения:

1. **Удалить импорты синглтонов**:
   ```python
   # ❌ Удалить
   from service.debugger.debugger import debug
   from service.logger.logger import logme
   ```

2. **Удалить параметр world из __init__**:
   ```python
   # ❌ ДО
   def __init__(self, world=None):
       self.world = world
   
   # ✅ ПОСЛЕ
   def __init__(self):
       pass
   ```

3. **Изменить сигнатуру draw()**:
   ```python
   # ❌ ДО
   def draw(self, screen, font, ...):
       ...
   
   # ✅ ПОСЛЕ
   def draw(self, screen, render_state: RenderStateDTO):
       world_dto = render_state.world
       debug_dto = render_state.debug
       params_dto = render_state.params
       # ... используем DTO вместо синглтонов
   ```

4. **Использовать DTO вместо мира**:
   ```python
   # ❌ ДО
   for creature in self.world.creatures:
   
   # ✅ ПОСЛЕ
   for creature in render_state.world.creatures:
   ```

---

## 📝 Порядок миграции виджетов

### Рекомендуемый порядок (по приоритету):

### 1️⃣ **Viewport** (Приоритет 1 - КРИТИЧНЫЙ)
   - **Сложность**: Средняя
   - **Импакт**: Самый критичный (главная отрисовка)
   - **Зависимости**: 
     - ❌ `from service.debugger.debugger import debug`
     - ❌ `self.world` (для creatures, foods, map)
   - **Тестирование**: Легко создать mock WorldStateDTO
   - **Файл**: `gui_viewport.py`

### 2️⃣ **SelectedCreatureHistory** (Приоритет 2)
   - **Сложность**: Средняя
   - **Импакт**: Важно для выбранного существа
   - **Зависимости**:
     - ❌ `from service.logger.logger import logme`
     - ❌ `self.world.get_creature_by_id()`
   - **Тестирование**: Легко создать mock CreatureHistoryDTO
   - **Файл**: `gui_selected_creature_history.py`

### 3️⃣ **SelectedCreaturePanel** (Приоритет 3)
   - **Сложность**: Простая
   - **Импакт**: Среднее
   - **Зависимости**:
     - ❌ `self.world.get_creature_by_id()`
   - **Тестирование**: Очень легко
   - **Файл**: `gui_selected_creature.py`

### 4️⃣ **VariablesPanel** (Приоритет 4)
   - **Сложность**: Сложная
   - **Импакт**: Важно, но не критично
   - **Зависимости**:
     - ❌ `self.world` (для изменения пищи)
     - ❌ Callbacks для изменения параметров
   - **Дополнительно**: Нужна система callbacks для Application
   - **Файл**: `gui_variablespanel.py`

---

## 📖 Пример полной миграции Viewport

### Шаг 1: Импорты

```python
# gui_viewport.py (v3dto)

import pygame
from typing import Optional
import numpy as np

# ❌ УДАЛИТЬ:
# from service.debugger.debugger import debug
# from service.logger.logger import logme

# ✅ ДОБАВИТЬ:
from renderer.v3dto.dto import RenderStateDTO, WorldStateDTO, DebugDataDTO
```

### Шаг 2: __init__

```python
class Viewport:
    # ... константы (геометрия, цвета, параметры камеры) - БЕЗ ИЗМЕНЕНИЙ ...
    
    # ❌ ДО:
    # def __init__(self, world=None):
    #     self.world = world
    #     self.rect = ...
    #     self.surface = ...
    #     self.camera_offset = ...
    #     self.camera_scale = ...
    
    # ✅ ПОСЛЕ:
    def __init__(self):
        """Инициализация Viewport БЕЗ зависимости от world."""
        # Геометрия viewport на экране
        self.rect = pygame.Rect(self.VIEWPORT_X, self.VIEWPORT_Y, 
                                self.VIEWPORT_WIDTH, self.VIEWPORT_HEIGHT)
        
        # Поверхность для отрисовки карты
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        
        # Параметры камеры
        self.camera_offset = self.CAMERA_OFFSET_DEFAULT.copy()
        self.camera_scale = self.CAMERA_SCALE_DEFAULT
        
        # Состояние перетаскивания карты
        self.is_dragging = False
        self.drag_start_pos = pygame.Vector2(0, 0)
        self.drag_start_offset = pygame.Vector2(0, 0)
```

### Шаг 3: draw() метод

```python
# ❌ ДО (v2):
def draw(self, screen, font, selected_creature_id=None):
    # Используем self.world
    for food in self.world.foods:
        self._render_food(food)
    
    for creature in self.world.creatures:
        self._render_creature(creature)
    
    # Используем debug синглтон
    raycast_dots = debug.get("raycast_dots")
    if raycast_dots is not None:
        self._draw_raycasts(raycast_dots)

# ✅ ПОСЛЕ (v3dto):
def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
    """Отрисовка viewport с данными из RenderStateDTO.
    
    Args:
        screen: Pygame surface для отрисовки
        render_state: RenderStateDTO со всеми данными
    """
    # Получаем данные из DTO
    world_dto = render_state.world
    debug_dto = render_state.debug
    
    # Очистка поверхности
    self.surface.fill(self.COLORS['bg'])
    
    # Отрисовка пищи из DTO
    for food in world_dto.foods:
        self._render_food(food)
    
    # Отрисовка существ из DTO
    for creature in world_dto.creatures:
        self._render_creature(creature)
    
    # Отрисовка раёмок выбранного существа
    if render_state.selected_creature:
        self._draw_selection_frame(render_state.selected_creature.creature)
    
    # Отрисовка raycast точек из DTO
    if debug_dto.raycast_dots is not None:
        self._draw_raycasts(debug_dto.raycast_dots)
    
    # Блит viewport поверхности на экран
    screen.blit(self.surface, self.rect)
    
    # Отрисовка рамки
    pygame.draw.rect(screen, self.COLORS['border'], self.rect, 2)
    
    # Отрисовка отладочной информации
    self._draw_debug_info(screen, render_state.tick)
```

### Шаг 4: Вспомогательные методы

```python
# ❌ ДО (v2):
def get_creature_at_position(self, screen_pos):
    # Преобразуем экран → мир
    map_pos = self.screen_to_map(screen_pos)
    if map_pos is None:
        return None
    
    # Ищем в self.world
    for creature in self.world.creatures:
        if abs(creature.x - map_pos.x) < 1 and abs(creature.y - map_pos.y) < 1:
            return creature.id
    return None

# ✅ ПОСЛЕ (v3dto):
def get_creature_at_position(self, screen_pos, render_state: RenderStateDTO):
    """Найти ID существа в позиции экрана.
    
    Args:
        screen_pos: (x, y) координаты экрана
        render_state: RenderStateDTO со всеми существами
        
    Returns:
        ID существа или None
    """
    map_pos = self.screen_to_map(screen_pos)
    if map_pos is None:
        return None
    
    # Используем метод из WorldStateDTO
    return render_state.world.get_creature_at_position(
        int(map_pos.x), int(map_pos.y), radius=1.0
    )

def _render_creature(self, creature_dto: CreatureDTO) -> None:
    """Отрисовка одного существа."""
    viewport_pos = self.map_to_viewport(pygame.Vector2(creature_dto.x, creature_dto.y))
    # ... рисуем creature_dto
```

---

## 🧪 Тестирование (когда виджеты переписаны)

### Юнит тест для Viewport с DTO:

```python
# tests/test_viewport_v3dto.py

import pytest
import pygame
from renderer.v3dto.dto import (
    WorldStateDTO, CreatureDTO, FoodDTO, DebugDataDTO, RenderStateDTO
)
from renderer.v3dto.gui_viewport import Viewport

def test_viewport_renders_with_dto():
    """Viewport может отрисовывать только с DTO, без world."""
    
    # Создаем mock DTO (БЕЗ реального world!)
    world_dto = WorldStateDTO(
        map=np.zeros((10, 10), dtype=int),
        width=10,
        height=10,
        creatures=[
            CreatureDTO(
                id=1, x=5, y=5, angle=0, energy=0.5,
                age=100, speed=0.1, generation=0,
                bite_effort=0, vision_distance=20, bite_range=0.5
            )
        ],
        foods=[FoodDTO(x=3, y=3, energy=0.5)],
        tick=50,
    )
    
    debug_dto = DebugDataDTO()  # Пусто, т.к. отладки нет
    
    render_state = RenderStateDTO(
        world=world_dto,
        params=None,  # Для Viewport не нужны параметры
        debug=debug_dto,
    )
    
    # Инициализируем Viewport БЕЗ world!
    viewport = Viewport()
    
    # Отрисовываем с DTO
    screen = pygame.Surface((800, 600))
    viewport.draw(screen, render_state)
    
    # Проверяем что не было ошибок
    assert viewport.surface is not None
```

---

## 🔄 Как использовать v3dto в application.py

### Вариант 1: Переключиться полностью на v3dto

```python
# application.py

# Вместо:
# from renderer.v2.renderer import Renderer

# Используем:
from renderer.v3dto.renderer import Renderer

class Application():
    def __init__(self):
        self.world = WorldGenerator.generate_world(...)
        self.renderer = Renderer(self.world, self)  # Точно такой же API
    
    def run(self):
        while not self.quit_flag:
            if self.is_running:
                self.world.update()
                self.world.update_map()
            
            if self.animate_flag:
                self.renderer.draw()  # Использует внутри DTO
            
            self.renderer.control_run()
```

### Вариант 2: Параллельно запускать v2 и v3dto

```python
# Для сравнения и отладки
from renderer.v2.renderer import Renderer as RendererV2
from renderer.v3dto.renderer import Renderer as RendererV3DTO

# В конфиге:
USE_V3DTO = True  # Переключатель

if USE_V3DTO:
    renderer = RendererV3DTO(world, app)
else:
    renderer = RendererV2(world, app)
```

---

## ✅ Checklist для полной миграции

### Phase 1: Инфраструктура (DONE ✅)
- [x] Создать v3dto папку
- [x] Создать dto.py с классами
- [x] Создать renderer.py с factory методами
- [x] Создать __init__.py

### Phase 2: Viewport (NEXT)
- [ ] Переписать gui_viewport.py для работы с RenderStateDTO
- [ ] Убрать импорт debugger
- [ ] Переписать все _draw_* методы
- [ ] Тестирование

### Phase 3: SelectedCreatureHistory
- [ ] Переписать gui_selected_creature_history.py
- [ ] Убрать импорт logger
- [ ] Использовать CreatureHistoryDTO

### Phase 4: SelectedCreaturePanel
- [ ] Переписать gui_selected_creature.py
- [ ] Использовать CreatureDTO из RenderStateDTO

### Phase 5: VariablesPanel (СЛОЖНАЯ)
- [ ] Переписать gui_variablespanel.py
- [ ] Реализовать callback систему для изменений параметров
- [ ] Использовать SimulationParamsDTO

### Phase 6: Интеграция
- [ ] Обновить renderer.py чтобы использовать переписанные виджеты
- [ ] Обновить application.py чтобы использовать v3dto.Renderer
- [ ] Полное тестирование

---

## 📚 Дополнительные ресурсы

- [ARCHITECTURE_ANALYSIS.md](ARCHITECTURE_ANALYSIS.md) - Полный архитектурный анализ
- [Примеры DTO](dto.py) - Все определения DTO в одном файле
- [Renderer v3dto](renderer.py) - Полная реализация преобразования в DTO

---

## 💡 Советы и трюки

### 1. Использовать IDE для автодополнения
```python
# IDE подскажет все поля:
render_state: RenderStateDTO
render_state.world.creatures  # ✅ IDE знает тип
render_state.world.creatures[0].energy  # ✅ IDE знает тип
```

### 2. Временная совместимость
```python
# На переходный период можно оставить старые методы:
def draw_old(self, screen, world):
    """Старый API (v2)"""
    pass

def draw(self, screen, render_state):
    """Новый API (v3dto)"""
    pass
```

### 3. Отладка DTO
```python
# Легко печатать DTO для отладки:
print(render_state.world)  # Выведет все поля
print(render_state.selected_creature)  # Выведет структуру
```

### 4. Type hints для удобства
```python
# Всегда указывайте типы!
def draw(self, screen: pygame.Surface, render_state: RenderStateDTO) -> None:
    # IDE и mypy помогут поймать ошибки
```
