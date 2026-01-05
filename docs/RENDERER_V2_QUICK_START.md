# Renderer v2 + Viewport — Быстрый старт

## Что создано

```
renderer/v2/
├── __init__.py           # Инициализация пакета
├── renderer.py           # Главный класс (система состояний)
└── gui_viewport.py       # Виджет карты мира
```

## Ключевые изменения

### 1. Viewport расширена на всю ширину

```python
# Старые размеры (v1)
VIEWPORT_X = 230
VIEWPORT_WIDTH = 700

# Новые размеры (v2)
VIEWPORT_X = 5
VIEWPORT_WIDTH = 1240  # Почти вся ширина экрана
VIEWPORT_HEIGHT = 500  # Высота без изменений
```

### 2. Viewport интегрирована в Renderer v2

```python
# В renderer.py
from renderer.v2.gui_viewport import Viewport

class Renderer:
    def __init__(self, world, app):
        # ... инициализация pygame ...
        self.viewport = Viewport(world=self.world)
    
    def _handle_mouse(self, event):
        if self.current_state == 'main':
            self.viewport.handle_event(event)  # Обработка пан/зум
    
    def _draw_main(self):
        self.viewport.draw(self.screen, self.font)  # Отрисовка карты
```

### 3. Новый метод handle_event() в Viewport

Для удобства все события мыши обрабатываются одним методом:

```python
def handle_event(self, event: pygame.event.Event) -> bool:
    """Обработка событий мыши."""
    if event.type == pygame.MOUSEBUTTONDOWN:
        self.handle_mouse_down(event)
    elif event.type == pygame.MOUSEBUTTONUP:
        self.handle_mouse_up(event)
    elif event.type == pygame.MOUSEMOTION:
        self.handle_mouse_motion(event)
    return False
```

## Как использовать

### Из application.py

```python
from renderer.v2.renderer import Renderer

class Application:
    def __init__(self, world):
        self.renderer = Renderer(world=world, app=self)
    
    def run(self):
        while self.is_running:
            # Основной цикл работает ТОЛЬКО в основном состоянии
            if self.renderer.is_main_state():
                self.world.update()
                self.world.update_map()
            
            # Отрисовка
            if self.animate_flag:
                self.renderer.draw()
            
            # Обработка событий
            if self.renderer.control_run():
                break
```

## Функциональность Viewport

### Панорамирование
- **ЛКМ + Drag**: Переместить карту

### Масштабирование  
- **Колесико ↑**: Приблизить (до 50x)
- **Колесико ↓**: Отдалить (до 7x)

### Отладка
- Автоматически показывает масштаб, смещение камеры и видимые клетки

### Методы

```python
viewport.reset_camera()                  # Сброс к параметрам по умолчанию
viewport.screen_to_map(screen_pos)       # Экран → координаты карты
viewport.map_to_viewport(map_pos)        # Карта → координаты экрана
viewport.get_visible_range()             # Диапазон видимых клеток
```

## Система состояний Renderer

### Текущие состояния

```python
'main'           # Основное окно (работает цикл)
'creatures_list' # Список существ (пауза)
'logs'           # Логи (пауза)
'experiment'     # Эксперимент (пауза)
```

### Переключение

```python
renderer.set_state('creatures_list')    # Открыть список
renderer.set_state('main')              # Вернуться в основное

# Проверка
if renderer.is_main_state():
    pass  # Основное состояние

if renderer.is_modal_state():
    pass  # Модальное окно открыто
```

## TODO

В renderer.py есть TODO комментарии для остальных виджетов:

```python
# self.variables_panel = VariablesPanel(world=self.world)
# self.func_keys_panel = FunctionKeysPanel(app=self.app)
# self.creatures_popup = CreaturesPopup(world=self.world)
# self.logs_popup = LogsPopup(app=self.app)
# self.experiment_modal = ExperimentModal(world=self.world, app=self.app)
```

Раскомментируйте и реализуйте по одному при необходимости.

## Отличия от v1

| Функция | v1 | v2 |
|---------|----|----|
| Система | Видимость (is_visible) | Состояния (State Machine) |
| Viewport ширина | 700px | 1240px |
| Контроль цикла | Нет | `is_main_state()` |
| События | По виджетам | По состояниям |
| Модальные окна | Условная отрисовка | Отдельные состояния |

## Документация

- [RENDERER_V2_STATE_MACHINE.md](../docs/RENDERER_V2_STATE_MACHINE.md) — Полное описание архитектуры
