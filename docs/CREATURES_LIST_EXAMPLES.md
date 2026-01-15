# CreaturesListModal - Примеры использования

## Архитектура v3dto и CreaturesListModal

### Полная цепочка взаимодействия

```
Пользователь нажимает F1
    ↓
Renderer._handle_keyboard_main()
    ↓
renderer.set_state('creatures_list')
    ↓
Renderer._on_state_enter('creatures_list')
    ↓
self.creatures_list_modal.reset()
    ↓
[Окно модально открыто, состояние 'creatures_list']
    ↓
Пользователь нажимает UP
    ↓
Renderer._handle_keyboard_creatures_list()
    ↓
self.creatures_list_modal.move_selection_up(creatures_count)
    ↓
[Выделение переместилось на одну строку вверх]
    ↓
Renderer.draw()
    ↓
RenderStateDTO подготовлен
    ↓
Renderer._draw_creatures_list(render_state)
    ↓
self.creatures_list_modal.draw(self.screen, render_state)
    ↓
[Окно перерисовано с новым положением]
```

## Пример 1: Базовое использование

### Инициализация в Renderer.__init__()

```python
from renderer.v3dto.gui_creatures_list import CreaturesListModal

class Renderer:
    def __init__(self, world, app):
        # ... другой код ...
        
        # Инициализация модального окна
        self.creatures_list_modal = CreaturesListModal()
        
        # Всё! Больше ничего не нужно
```

### Обработка входа в состояние

```python
def _on_state_enter(self, state_name: str) -> None:
    """Вызывается при входе в новое состояние."""
    if state_name == 'creatures_list':
        # Сбрасываем навигацию при открытии списка существ
        self.creatures_list_modal.reset()
        print(f"✓ Creatures list modal opened")
```

## Пример 2: Обработка событий клавиатуры

### Полная реализация в _handle_keyboard_creatures_list()

```python
def _handle_keyboard_creatures_list(self, event: pygame.event.Event) -> bool:
    """Обработка событий в окне списка существ.
    
    Навигация:
    - UP/DOWN: движение вверх/вниз по списку
    - HOME/END: прыжок в начало/конец списка
    - ESC/F1: закрытие окна
    """
    if event.type != pygame.KEYDOWN:
        return False
    
    # Выход из модального окна
    if event.key == pygame.K_ESCAPE or event.key == pygame.K_F1:
        print("✓ Closing creatures list modal")
        self.set_state('main')  # Возвращаемся в основное состояние
        return True
    
    # Получаем количество существ для проверок границ
    creatures_count = len(self.world.creatures)
    
    # Если нет существ, ничего не делаем
    if creatures_count == 0:
        return False
    
    # НАВИГАЦИЯ
    if event.key == pygame.K_UP:
        self.creatures_list_modal.move_selection_up(creatures_count)
        print(f"✓ Selection moved up to {self.creatures_list_modal.selected_index}")
        return True
    
    elif event.key == pygame.K_DOWN:
        self.creatures_list_modal.move_selection_down(creatures_count)
        print(f"✓ Selection moved down to {self.creatures_list_modal.selected_index}")
        return True
    
    elif event.key == pygame.K_HOME:
        self.creatures_list_modal.move_selection_home()
        print(f"✓ Selection moved to home (0)")
        return True
    
    elif event.key == pygame.K_END:
        self.creatures_list_modal.move_selection_end(creatures_count)
        print(f"✓ Selection moved to end ({creatures_count - 1})")
        return True
    
    # Возможные будущие расширения:
    # elif event.key == pygame.K_RETURN:
    #     creature_id = self.creatures_list_modal.get_selected_creature_id(creatures_count)
    #     self.selected_creature_id = creature_id
    #     print(f"✓ Creature selected: {creature_id}")
    #     return True
    
    return False
```

## Пример 3: Отрисовка в Renderer.draw()

### Состояние 'creatures_list'

```python
def _draw_creatures_list(self, render_state: RenderStateDTO) -> None:
    """Отрисовка окна списка существ.
    
    Это очень просто благодаря v3dto архитектуре:
    1. Render state уже подготовлен Renderer'ом
    2. Передаём его виджету
    3. Виджет отрисовывает себя
    """
    # Всё что нужно - одна строка!
    self.creatures_list_modal.draw(self.screen, render_state)
```

### Полный цикл рисования

```python
def draw(self) -> None:
    """Главный метод рисования, вызывается один раз за фрейм.
    
    Порядок:
    1. Очистка экрана
    2. Подготовка DTO
    3. Отрисовка в зависимости от состояния
    4. Обновление дисплея
    """
    # 1. Очистка
    self.screen.fill(self.COLORS['background'])
    
    # 2. Подготовка данных
    render_state = self._prepare_render_state_dto()
    # render_state содержит:
    # - world (карта, список существ)
    # - params (все параметры симуляции)
    # - debug (отладочные данные)
    # - selected_creature (информация о выбранном существе)
    # - current_state, tick, fps
    
    # 3. Отрисовка в зависимости от состояния
    if self.current_state == 'creatures_list':
        self._draw_creatures_list(render_state)
    
    # 4. Обновление дисплея
    pygame.display.flip()
    self.clock.tick(60)
```

## Пример 4: Тестирование виджета

### Изолированное тестирование (без Renderer)

```python
"""
Благодаря v3dto архитектуре, виджет полностью изолирован и легко тестируется.
"""

import pytest
import pygame
from renderer.v3dto.gui_creatures_list import CreaturesListModal
from renderer.v3dto.dto import RenderStateDTO, WorldStateDTO, CreatureDTO, SimulationParamsDTO, DebugDataDTO

def test_creatures_list_modal_initialization():
    """Тест инициализации."""
    modal = CreaturesListModal()
    assert modal.scroll_offset == 0
    assert modal.selected_index == 0
    assert modal.font is not None
    assert modal.font_title is not None


def test_creatures_list_modal_navigation():
    """Тест навигации."""
    modal = CreaturesListModal()
    
    # Изначально выбран первый элемент
    assert modal.selected_index == 0
    assert modal.scroll_offset == 0
    
    # Движение вниз
    modal.move_selection_down(10)
    assert modal.selected_index == 1
    
    # Движение вверх
    modal.move_selection_up(10)
    assert modal.selected_index == 0
    
    # Прыжок на Home
    modal.selected_index = 5
    modal.move_selection_home()
    assert modal.selected_index == 0
    assert modal.scroll_offset == 0


def test_creatures_list_modal_reset():
    """Тест сброса состояния."""
    modal = CreaturesListModal()
    
    # Устанавливаем произвольное состояние
    modal.selected_index = 10
    modal.scroll_offset = 5
    
    # Сбрасываем
    modal.reset()
    
    # Проверяем, что вернулось в начало
    assert modal.selected_index == 0
    assert modal.scroll_offset == 0


@pytest.mark.pygame
def test_creatures_list_modal_draw():
    """Тест отрисовки с mock RenderStateDTO.
    
    Это демонстрирует силу v3dto архитектуры:
    мы можем протестировать отрисовку без симуляции world!
    """
    pygame.init()
    screen = pygame.display.set_mode((1250, 600))
    
    # Создаём mock RenderStateDTO
    creatures = [
        CreatureDTO(
            id=0, x=10.0, y=20.0, angle=0.5, energy=80.0, age=100,
            speed=1.0, generation=2, bite_effort=1.0,
            vision_distance=20.0, bite_range=1.0
        ),
        CreatureDTO(
            id=1, x=15.0, y=25.0, angle=1.0, energy=60.0, age=50,
            speed=0.8, generation=1, bite_effort=1.0,
            vision_distance=20.0, bite_range=1.0
        ),
    ]
    
    world_dto = WorldStateDTO(
        map=np.zeros((100, 100)),
        width=100,
        height=100,
        creatures=creatures,
        foods=[],
        tick=1000
    )
    
    render_state = RenderStateDTO(
        world=world_dto,
        params=SimulationParamsDTO(...),  # Заполняем минимум
        debug=DebugDataDTO(),
    )
    
    # Теперь можем протестировать отрисовку
    modal = CreaturesListModal()
    modal.draw(screen, render_state)  # Не должно быть исключений
    
    pygame.quit()
```

## Пример 5: Расширение виджета

### Добавление новой функциональности

```python
class CreaturesListModal:
    # ... существующий код ...
    
    def select_creature(self, creatures_count: int) -> int:
        """НОВАЯ: Выбрать текущее существо и вернуть его ID."""
        if creatures_count > 0 and self.selected_index < creatures_count:
            return self.selected_index
        return -1
    
    def get_selected_creature_info(self, render_state: 'RenderStateDTO') -> Optional[CreatureDTO]:
        """НОВАЯ: Получить информацию о выбранном существе."""
        creatures = render_state.world.creatures
        if self.selected_index < len(creatures):
            return creatures[self.selected_index]
        return None
    
    def search_by_id(self, creature_id: int, creatures_count: int) -> bool:
        """НОВАЯ: Найти существо по ID.
        
        Returns:
            True если найдено, False если нет
        """
        if creature_id < 0 or creature_id >= creatures_count:
            return False
        self.selected_index = creature_id
        # Автоскролл к найденному существу
        if creature_id < self.scroll_offset:
            self.scroll_offset = creature_id
        elif creature_id >= self.scroll_offset + self.MAX_VISIBLE_ROWS:
            self.scroll_offset = creature_id - self.MAX_VISIBLE_ROWS + 1
        return True
```

### Использование в Renderer

```python
def _handle_keyboard_creatures_list(self, event: pygame.event.Event) -> bool:
    # ... существующий код ...
    
    # НОВОЕ: Выбор существа по Enter
    elif event.key == pygame.K_RETURN:
        selected_id = self.creatures_list_modal.select_creature(creatures_count)
        if selected_id >= 0:
            self.selected_creature_id = selected_id
            print(f"✓ Creature selected: id={selected_id}")
        return True
    
    # НОВОЕ: Поиск по начальным символам ID
    elif event.key in (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                       pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
        # Простой поиск по ID (можно расширить)
        digit = event.key - pygame.K_0
        found = self.creatures_list_modal.search_by_id(digit, creatures_count)
        if found:
            print(f"✓ Creature {digit} found")
        return True
    
    return False
```

## Пример 6: Состояние машины Renderer

### Полная диаграмма переходов

```
                 F1
           ┌─────────┐
           │         ▼
           │    ┌──────────────────┐
    ┌──────┴────►│ creatures_list   │
    │            │   (MODAL)        │
    │            └──────────────────┘
    │                    │
    │              ESC/F1│
    │                    ▼
    │            ┌──────────────┐
    ├───────────◄│    main      │─────┐
    │ F9         │  (MAIN VIEW) │     │ F9
    │            └──────────────┘     │
    │                    ▲             │
    │                    │             ▼
    │            ┌──────────────────┐
    └────────────│popup_simparams   │
                 │   (MODAL)        │
                 └──────────────────┘

Другие состояния (logs, experiment) - аналогично
```

## Проблемы и решения

### Проблема: Окно не отображается

**Причина**: Неправильное состояние машины.

**Решение**:
```python
# Убедитесь, что:
1. self.set_state('creatures_list') был вызван
2. Renderer.draw() вызывает _draw_creatures_list()
3. _on_state_enter() был вызван (для reset())
```

### Проблема: Навигация не работает

**Причина**: События не достигают `_handle_keyboard_creatures_list()`.

**Решение**:
```python
# Убедитесь, что:
1. self.current_state == 'creatures_list' в control_run()
2. _handle_keyboard() делегирует в правильный обработчик
3. event.type == pygame.KEYDOWN
```

### Проблема: Данные существ не отображаются

**Причина**: RenderStateDTO не подготовлен правильно.

**Решение**:
```python
# В _prepare_render_state_dto() убедитесь:
1. world_dto.creatures содержит CreatureDTO объекты
2. Все поля заполнены (id, x, y, energy, age, speed, generation)
3. render_state передаётся в draw()
```

## Заключение

`CreaturesListModal` - это чистый, хорошо структурированный v3dto компонент, который:
- Полностью изолирован от синглтонов
- Легко тестируется
- Легко расширяется
- Следует установленным паттернам v3dto

Используйте эти примеры как шаблон при создании новых модальных окон (logs, experiment и т.д.).
