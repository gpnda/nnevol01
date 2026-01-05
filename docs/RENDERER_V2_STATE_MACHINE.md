# Renderer v2 — Система состояний

## Обзор

Новая версия Renderer использует **систему состояний (State Machine)** для управления несколькими экранами/окнами. Одно состояние активно в любой момент времени, и оно определяет:

- **Какие элементы отрисовываются**
- **Какие события обрабатываются**
- **Работает ли основной игровой цикл**

---

## Состояния

### 1. `'main'` — Основное окно с картой
- **Описание**: Основной экран с картой мира и всеми постоянными виджетами
- **Работает ли цикл**: ✅ ДА (основной цикл работает нормально)
- **Отрисовка**: 
  - Viewport (карта)
  - VariablesPanel (переменные)
  - FunctionKeysPanel (функциональные клавиши)
  - SelectedCreaturePanel (информация о существе)
  - WorldStatsPanel (статистика мира)
- **События**: All keyboard events are processed normally
- **Горячие клавиши**:
  - `Space`: Пауза/возобновление
  - `A`: Вкл/выкл отрисовку
  - `F1`: Переход в `creatures_list`
  - `F12`: Переход в `logs`

### 2. `'creatures_list'` — Список существ (модальное)
- **Описание**: Модальное окно со списком всех существ
- **Работает ли цикл**: ❌ НЕТ (основной цикл на паузе)
- **Отрисовка**:
  - CreaturesPopup (окно со списком)
  - (Остальное НЕ отрисовывается)
- **События**: Только для CreaturesPopup (UP/DOWN для навигации)
- **Горячие клавиши**:
  - `Escape` или `F1`: Возврат в `main`

### 3. `'logs'` — Логи в полный экран (модальное)
- **Описание**: Модальное окно с логами приложения
- **Работает ли цикл**: ❌ НЕТ (основной цикл на паузе)
- **Отрисовка**:
  - LogsPopup (окно с логами)
  - (Остальное НЕ отрисовывается)
- **События**: Только для LogsPopup (UP/DOWN для скролла, фильтры и т.д.)
- **Горячие клавиши**:
  - `Escape` или `F12`: Возврат в `main`

### 4. `'experiment'` — Окно эксперимента (модальное)
- **Описание**: Модальное окно для проведения экспериментов
- **Работает ли цикл**: ❌ НЕТ (основной цикл полностью остановлен, запускается локальный цикл эксперимента)
- **Отрисовка**:
  - ExperimentModal (окно с экспериментом)
  - (Остальное НЕ отрисовывается)
- **События**: Только для ExperimentModal
- **Горячие клавиши**:
  - `Escape`: Возврат в `main` (отмена эксперимента)

---

## Архитектура

### Переключение состояния

```python
# Текущее состояние
renderer.current_state  # 'main', 'creatures_list' и т.д.

# Переключение
renderer.set_state('creatures_list')

# Проверка
if renderer.is_main_state():
    # Основное состояние
    pass

if renderer.is_modal_state():
    # Модальное окно открыто
    pass
```

### Обработка событий

События маршрутизируются в зависимости от состояния:

```python
_handle_keyboard(event)
    ├─ if state == 'main':
    │   └─ _handle_keyboard_main(event)
    │       ├─ VariablesPanel.handle_event()
    │       ├─ FunctionKeysPanel.handle_event()
    │       └─ Viewport.handle_event()
    │
    ├─ if state == 'creatures_list':
    │   └─ _handle_keyboard_creatures_list(event)
    │       └─ CreaturesPopup.handle_event()
    │
    ├─ if state == 'logs':
    │   └─ _handle_keyboard_logs(event)
    │       └─ LogsPopup.handle_event()
    │
    └─ if state == 'experiment':
        └─ _handle_keyboard_experiment(event)
            └─ ExperimentModal.handle_event()
```

### Отрисовка

Отрисовка также зависит от состояния:

```python
draw()
    ├─ if state == 'main':
    │   └─ _draw_main()
    │       ├─ Viewport.draw()
    │       ├─ VariablesPanel.draw()
    │       ├─ FunctionKeysPanel.draw()
    │       ├─ SelectedCreaturePanel.draw()
    │       └─ WorldStatsPanel.draw()
    │
    ├─ if state == 'creatures_list':
    │   └─ _draw_creatures_list()
    │       └─ CreaturesPopup.draw()
    │
    ├─ if state == 'logs':
    │   └─ _draw_logs()
    │       └─ LogsPopup.draw()
    │
    └─ if state == 'experiment':
        └─ _draw_experiment()
            └─ ExperimentModal.draw()
```

---

## Интеграция с application.py

### Основной цикл (application.py)

```python
def run(self):
    while self.is_running:
        # Основной игровой цикл ТОЛЬКО в основном состоянии
        if self.renderer.is_main_state():
            self.world.update()
            self.world.update_map()
        
        # Отрисовка (если enabled)
        if self.animate_flag:
            self.renderer.draw()
        
        # Обработка событий (работает всегда)
        if self.renderer.control_run():
            break
```

### Модальное окно эксперимента с локальным циклом

```python
# В ExperimentModal:
def run_experiment(self):
    """Локальный цикл для эксперимента (блокирует основной цикл)."""
    while self.is_running and self.is_visible:
        # Локальное обновление (только для эксперимента)
        self.experiment_creature.do_something()
        
        # Отрисовка
        self.draw(renderer.screen)
        pygame.display.flip()
        
        # Обработка событий (Escape для выхода)
        for event in pygame.event.get():
            if self.handle_event(event):
                break

# В application.py
def run(self):
    while self.is_running:
        # Проверяем находимся ли в эксперименте
        if self.renderer.current_state == 'experiment':
            # Локальный цикл эксперимента полностью блокирует основной
            self.renderer.experiment_modal.run_experiment()
            continue
        
        # Обычный основной цикл
        if self.renderer.is_main_state():
            self.world.update()
            self.world.update_map()
        
        if self.animate_flag:
            self.renderer.draw()
        
        if self.renderer.control_run():
            break
```

---

## Добавление нового состояния

### Шаг 1: Добавить в реестр состояний

```python
# В renderer.__init__():
self.states = {
    'main': 'Основное окно с картой',
    'creatures_list': 'Список существ (модальное)',
    'logs': 'Логи в полный экран (модальное)',
    'experiment': 'Окно эксперимента (модальное)',
    'my_new_state': 'Описание нового состояния',  # ← НОВОЕ
}
```

### Шаг 2: Добавить обработку в _handle_keyboard()

```python
def _handle_keyboard(self, event: pygame.event.Event) -> bool:
    # ... существующий код ...
    
    elif self.current_state == 'my_new_state':  # ← НОВОЕ
        return self._handle_keyboard_my_new_state(event)
    
    return False
```

### Шаг 3: Реализовать обработчик событий

```python
def _handle_keyboard_my_new_state(self, event: pygame.event.Event) -> bool:
    """Обработка событий в новом состоянии."""
    if event.type != pygame.KEYDOWN:
        return False
    
    if event.key == pygame.K_ESCAPE:
        self.set_state('main')
        return True
    
    # Обработка событий для вашего виджета
    # if self.my_widget.handle_event(event):
    #     return True
    
    return False
```

### Шаг 4: Добавить отрисовку в draw()

```python
def draw(self) -> None:
    # ... очистка экрана ...
    
    if self.current_state == 'main':
        self._draw_main()
    # ... другие состояния ...
    elif self.current_state == 'my_new_state':  # ← НОВОЕ
        self._draw_my_new_state()
    
    pygame.display.flip()
```

### Шаг 5: Реализовать метод отрисовки

```python
def _draw_my_new_state(self) -> None:
    """Отрисовка нового состояния."""
    # self.my_widget.draw(self.screen)
```

---

## Контрольный список для нового состояния

- [ ] Добавить в `self.states` словарь
- [ ] Добавить ветку в `_handle_keyboard()`
- [ ] Реализовать `_handle_keyboard_my_state()`
- [ ] Добавить ветку в `draw()`
- [ ] Реализовать `_draw_my_state()`
- [ ] Проверить переходы между состояниями
- [ ] Проверить закрытие окна (Escape)

---

## Преимущества системы состояний

✅ **Ясная логика**: Каждый экран полностью отделен от других
✅ **Простота отладки**: Известно какое состояние активно в любой момент
✅ **Контроль цикла**: Легко управлять, работает ли основной цикл
✅ **Масштабируемость**: Добавление нового состояния — это 5 строк кода
✅ **Нет утечек событий**: События не "просачиваются" между экранами
✅ **Нет утечек отрисовки**: Экраны не рисуют друг на друге

---

## Отличия от v1 (система видимости)

| Аспект | v1 (видимость) | v2 (состояния) |
|--------|---|---|
| **Логика** | Много условий `if is_visible` | Чистые ветки по состоянию |
| **События** | Циклы по виджетам | Маршрутизация по состоянию |
| **Контроль цикла** | Не контролируется | `is_main_state()` |
| **Новый экран** | Добавить to реестр + if-else | Добавить состояние + 5 методов |
| **Сложность** | Средняя | Низкая |
| **Расширяемость** | Хорошая | Отличная |

---

## Вопросы и ответы

**Q: Что если мне нужны подсостояния (например, разные режимы эксперимента)?**

A: Используйте дополнительную переменную:
```python
self.current_state = 'experiment'
self.experiment_mode = 'cone'  # 'cone', 'enemy', 'wall'
```

**Q: Как передать данные между состояниями?**

A: Сохраните на уровне renderer:
```python
# При открытии инспектора
self.selected_creature = creature
self.set_state('creature_inspector')
```

**Q: Можно ли иметь несколько активных состояний?**

A: Нет, это нарушает принцип State Machine. Если нужно, используйте вложенные состояния или подсостояния.

**Q: Что если модальное окно нужно оставить полупрозрачным поверх основного?**

A: Отрисуйте основной экран, потом поверх него:
```python
def _draw_my_overlay(self):
    self._draw_main()  # Рисуем основное
    self.my_overlay.draw(self.screen)  # Поверх него оверлей
```
