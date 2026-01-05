# Архитектура расширяемого Renderer с поддержкой модальных окон

## Обзор текущего состояния

Ваша текущая реализация уже очень хорошо организована. Предлагаемые улучшения **не требуют кардинальной переделки** — это дополнения, которые будут расширять систему постепенно.

---

## 1. Система управления видимостью виджетов

### Проблема
Сейчас все виджеты отрисовываются и слушают события независимо от того, должны ли они быть видны. Для модальных окон нужно управлять их видимостью централизованно.

### Решение: Минимальные изменения

#### 1.1 Добавить реестр виджетов в Renderer.__init__()

```python
def __init__(self, world, app):
    # ... существующий код ...
    
    # РЕЕСТР ВИДЖЕТОВ
    # Структура: {widget_name: {'instance': widget, 'always_visible': bool}}
    self.widgets = {
        # Постоянно видимые виджеты
        'viewport': {'instance': self.viewport, 'always_visible': True},
        'variables_panel': {'instance': self.variables_panel, 'always_visible': True},
        'func_keys_panel': {'instance': self.func_keys_panel, 'always_visible': True},
        'selected_creature_panel': {'instance': self.selected_creature_panel, 'always_visible': True},
        'world_stats_panel': {'instance': self.world_stats_panel, 'always_visible': True},
        
        # Модальные окна (видны по условию)
        'creatures_popup': {'instance': self.creatures_popup, 'always_visible': False},
        'settings_modal': {'instance': self.settings_modal, 'always_visible': False},
        'creature_inspector': {'instance': self.creature_inspector, 'always_visible': False},
        'experiment_modal': {'instance': self.experiment_modal, 'always_visible': False},
        'logs_popup': {'instance': self.logs_popup, 'always_visible': False},
    }
```

#### 1.2 Рефакторить handle_event()

```python
def _handle_keyboard(self, event: pygame.event.Event) -> bool:
    """
    Обработка клавиатурных событий.
    События сначала идут в видимые модальные окна, потом в остальные.
    """
    # ПРИОРИТЕТ 1: Видимые модальные окна (они захватывают события)
    for widget_name, widget_info in self.widgets.items():
        widget = widget_info['instance']
        is_always_visible = widget_info['always_visible']
        
        # Пропускаем, если виджет не видим и не всегда видим
        if not is_always_visible and not getattr(widget, 'is_visible', True):
            continue
        
        # Проверяем есть ли метод handle_event
        if hasattr(widget, 'handle_event') and callable(getattr(widget, 'handle_event')):
            if widget.handle_event(event):
                return False
    
    # ПРИОРИТЕТ 2: Глобальные команды Renderer
    if event.key == pygame.K_SPACE:
        self.app.toggle_run()
    elif event.key == pygame.K_a:
        self.app.toggle_animate()
    
    return False
```

#### 1.3 Рефакторить draw()

```python
def draw(self) -> None:
    """Отрисовка всех видимых компонентов."""
    # Очистка экрана
    self.screen.fill(self.COLORS['background'])
    
    # ОТРИСОВКА: Сначала постоянно видимые, потом модальные окна
    for widget_name, widget_info in self.widgets.items():
        widget = widget_info['instance']
        is_always_visible = widget_info['always_visible']
        
        # Пропускаем невидимые модальные окна
        if not is_always_visible and not getattr(widget, 'is_visible', True):
            continue
        
        # Проверяем есть ли метод draw
        if hasattr(widget, 'draw'):
            # Для viewport нужен шрифт
            if widget_name == 'viewport':
                widget.draw(self.screen, self.font)
            else:
                widget.draw(self.screen)
    
    # Обновление дисплея
    pygame.display.flip()
```

---

## 2. Соглашения для новых виджетов

### 2.1 Требуемый интерфейс

Каждый модальный виджет **должен иметь**:

```python
class MyModalWidget:
    def __init__(self, world=None, app=None):
        """Инициализация. Принимаем world и app если нужны."""
        self.is_visible = False  # ОБЯЗАТЕЛЬНО: флаг видимости
        self.world = world
        self.app = app
        # ... остальная инициализация ...
    
    def toggle(self) -> None:
        """Переключить видимость."""
        self.is_visible = not self.is_visible
    
    def open(self) -> None:
        """Явно открыть окно."""
        self.is_visible = True
    
    def close(self) -> None:
        """Явно закрыть окно."""
        self.is_visible = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обработка событий.
        Возвращаем True если событие обработано и нужно блокировать другие обработчики.
        """
        if not self.is_visible:
            return False
        
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_ESCAPE:
            self.close()
            return True
        
        # ... остальная обработка ...
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовка окна.
        Вызывается только если is_visible == True.
        """
        if not self.is_visible:
            return
        
        # ... отрисовка ...
```

### 2.2 Паттерн для постоянно видимых виджетов

```python
class AlwaysVisibleWidget:
    def __init__(self, world=None, app=None):
        self.world = world
        self.app = app
        # Для постоянно видимых НЕ нужна переменная is_visible
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий (всегда слушает)."""
        # ... обработка ...
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка (всегда видим)."""
        # ... отрисовка ...
```

---

## 3. Структура файлов и организация кода

### 3.1 Рекомендуемая структура папки renderer/

```
renderer/
├── v1/
│   ├── __init__.py
│   ├── renderer.py              # ГЛАВНЫЙ ФАЙЛ - управление и координация
│   │
│   ├── # Постоянно видимые виджеты
│   ├── gui_viewport.py          # Карта мира (всегда видим)
│   ├── gui_variablespanel.py    # Панель переменных (всегда видим)
│   ├── gui_functionalkeys.py    # Панель функциональных клавиш (всегда видим)
│   ├── gui_selected_creature.py # Панель выбранного существа (всегда видим)
│   ├── gui_world_stats.py       # График изобилия/популяции (всегда видим)
│   │
│   ├── # Модальные окна
│   ├── gui_creatures_popup.py   # F1: Список существ (модальное)
│   ├── gui_settings_modal.py    # F3: Настройки приложения (модальное)
│   ├── gui_creature_inspector.py # Инспектор существа (модальное)
│   ├── gui_experiment_modal.py  # Окно экспериментов (модальное)
│   ├── gui_logs_popup.py        # F12: Логи приложения (модальное)
│   │
│   └── __pycache__/
```

### 3.2 Инициализация в renderer.__init__()

**Правило простоты**: Добавляйте новые виджеты в том же стиле, как существующие.

```python
def __init__(self, world, app):
    # ... pygame init ...
    
    # ЯРУС 1: Постоянно видимые компоненты
    self.viewport = Viewport(world=self.world)
    self.variables_panel = VariablesPanel(world=self.world)
    self.func_keys_panel = FunctionKeysPanel(app=self.app)
    self.selected_creature_panel = SelectedCreaturePanel(world=self.world, app=self.app)
    self.world_stats_panel = WorldStatsPanel(world=self.world)
    
    # ЯРУС 2: Модальные окна
    self.creatures_popup = CreaturesPopup(world=self.world)
    self.settings_modal = SettingsModal(world=self.world, app=self.app)
    self.creature_inspector = CreatureInspector(world=self.world, app=self.app)
    self.experiment_modal = ExperimentModal(world=self.world, app=self.app)
    self.logs_popup = LogsPopup(app=self.app)
    
    # РЕЕСТР ВИДЖЕТОВ (см. раздел 1.1)
    self.widgets = { ... }
```

---

## 4. Паттерны использования для типичных сценариев

### 4.1 Открытие модального окна при нажатии клавиши

**В renderer._handle_keyboard():**
```python
# Глобальные команды - открытие модальных окон
if event.key == pygame.K_F12:
    self.logs_popup.toggle()
```

**Альтернативно - через виджет:**
```python
# Если логи открываются из другого виджета:
# widget вызывает: self.app.renderer.logs_popup.open()
```

### 4.2 Остановка основного цикла при открытии модального окна

Если эксперимент должен полностью остановить основной цикл:

```python
# В application.py
def run(self):
    while self.is_running:
        # Проверяем находимся ли в режиме эксперимента
        if hasattr(self.renderer, 'experiment_modal'):
            if self.renderer.experiment_modal.is_visible:
                # Запускаем локальный цикл эксперимента
                self.renderer.experiment_modal.run_experiment()
                continue
        
        # Обычный цикл
        if self.is_running:
            self.world.update()
            self.world.update_map()
        
        if self.animate_flag:
            self.renderer.draw()
        
        if self.renderer.control_run():
            break
```

### 4.3 Передача данных между виджетами

```python
# В creatures_popup при выборе существа:
if selected_creature:
    # Открываем инспектор и передаем существо
    self.app.renderer.creature_inspector.set_creature(selected_creature)
    self.app.renderer.creature_inspector.open()

# В creature_inspector:
def set_creature(self, creature):
    self.selected_creature = creature
    self.refresh_data()
```

---

## 5. Практические рекомендации

### 5.1 Не добавляйте лишние абстракции

✅ **ХОРОШО**: Реестр виджетов как обычный dict
```python
self.widgets = {
    'name': {'instance': widget, 'always_visible': bool}
}
```

❌ **ПЛОХО**: Создавать базовый класс WidgetBase, регистратор виджетов и т.д.

### 5.2 Метод handle_event() — фильтр событий

Каждый виджет решает сам:
- Обработать ли событие
- Вернуть True (заблокировать событие для других)
- Вернуть False (пропустить дальше)

```python
# Пример: Список существ ловит UP/DOWN для навигации
def handle_event(self, event):
    if not self.is_visible:
        return False
    
    if event.key == pygame.K_UP:
        self.move_selection_up()
        return True  # Блокируем, чтобы viewport не прокручивался
    
    return False
```

### 5.3 Метод draw() — только отрисовка

Не добавляйте логику в draw(), она должна быть в update/handle_event:

```python
# ❌ ПЛОХО
def draw(self, screen):
    if self.is_visible:
        self.update_data()  # ПЛОХО
        self.render_image(screen)

# ✅ ХОРОШО
def draw(self, screen):
    if self.is_visible:
        self.render_image(screen)

def update(self):  # Или обновлять в handle_event
    self.update_data()
```

### 5.4 Явные зависимости между виджетами

Если виджет A зависит от виджета B, пробрасывайте эту зависимость явно:

```python
# В renderer.__init__():
self.creature_inspector = CreatureInspector(
    world=self.world, 
    app=self.app,
    creatures_popup=self.creatures_popup  # Явная зависимость
)
```

### 5.5 Логирование и отладка

Добавьте простой способ отслеживать состояние виджетов:

```python
# В renderer.py
def debug_widgets_state(self) -> str:
    """Вывести состояние всех виджетов для отладки."""
    state = []
    for name, info in self.widgets.items():
        widget = info['instance']
        is_visible = getattr(widget, 'is_visible', 'always')
        state.append(f"{name}: {is_visible}")
    return "\n".join(state)
```

---

## 6. Checklist для добавления нового модального окна

Когда вы создаете новый виджет, следуйте этому порядку:

- [ ] Создать файл `gui_my_widget.py`
- [ ] Реализовать требуемый интерфейс (is_visible, toggle, handle_event, draw)
- [ ] Импортировать в `renderer.py`
- [ ] Инициализировать в `__init__()` (решить: always_visible или нет)
- [ ] Добавить в реестр `self.widgets`
- [ ] Добавить горячую клавишу в `_handle_keyboard()` (если нужна)
- [ ] Тестировать взаимодействие с другими виджетами
- [ ] Обновить этот документ если понадобились новые паттерны

---

## 7. Пример: Добавление нового модального окна

### Шаг 1: Создать файл
```python
# renderer/v1/gui_settings_modal.py

class SettingsModal:
    def __init__(self, world=None, app=None):
        self.world = world
        self.app = app
        self.is_visible = False
        self.selected_index = 0
        # ... инициализация ...
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_visible:
            return False
        
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F3:
            self.close()
            return True
        
        # ... остальная логика ...
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_visible:
            return
        # ... отрисовка ...
    
    def toggle(self):
        self.is_visible = not self.is_visible
    
    def close(self):
        self.is_visible = False
```

### Шаг 2: Обновить renderer.py

```python
# В импортах:
from renderer.v1.gui_settings_modal import SettingsModal

# В __init__():
self.settings_modal = SettingsModal(world=self.world, app=self.app)

# В реестр добавить:
'settings_modal': {'instance': self.settings_modal, 'always_visible': False},

# В _handle_keyboard():
if event.key == pygame.K_F3:
    self.settings_modal.toggle()
```

### Шаг 3: Готово!

Теперь система автоматически:
- Не отрисовывает окно пока оно закрыто
- Не слушает события для закрытого окна
- Открывает по F3 и закрывает по Escape

---

## 8. Возможные будущие эволюции (без кардинальной переделки)

Если в будущем понадобится:

**Блокировка событий для фона при открытом модальном окне:**
```python
def _handle_keyboard(self, event):
    # Если есть открытое модальное окно - блокируем события для background
    modal_open = any(
        not widget_info['always_visible'] and getattr(widget_info['instance'], 'is_visible', False)
        for widget_info in self.widgets.values()
    )
    
    if modal_open:
        # Только модальные окна обрабатывают события
        for name, info in self.widgets.items():
            if not info['always_visible']:
                if info['instance'].handle_event(event):
                    return False
        return False
```

**Анимация открытия/закрытия:**
```python
# Просто добавить в widget:
self.animation_progress = 0  # 0..1
```

**Вложенные модальные окна:**
```python
# Просто вложить одно модальное окно в другое
self.experiment_modal.contains(self.experiment_results_panel)
```

---

## Итоговая рекомендация

Ваша текущая архитектура уже близка к идеальному балансу между простотой и расширяемостью. 

**Добавьте:**
1. Реестр виджетов (словарь с информацией о видимости)
2. Цикл по реестру в handle_event() и draw()
3. Соглашение о is_visible для модальных окон

**Больше ничего не нужно.**

Это позволит вам добавлять новые окна, просто создавая файл, инициализируя в конструкторе и добавляя в реестр. Все остальное будет работать автоматически.
