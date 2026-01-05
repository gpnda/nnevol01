# Архитектура обработки открытия/закрытия модальных окон

## Вопрос: Где обрабатывать переходы между состояниями?

Есть два подхода:

### Вариант 1: Обработка в Renderer (выбранный подход) ✅

**Где обрабатывается:**
- Открытие по F9: `_handle_keyboard_main()` → `self.set_state('popup_simparams')`
- Закрытие по Escape: `_handle_keyboard_popup_simparams()` → `self.set_state('main')`

**Код:**
```python
# В renderer._handle_keyboard_main()
if event.key == pygame.K_F9:
    self.set_state('popup_simparams')

# В renderer._handle_keyboard_popup_simparams()
if event.key == pygame.K_ESCAPE or event.key == pygame.K_F9:
    self.set_state('main')
```

**Преимущества:**
- ✅ Все переходы между состояниями видны в одном месте (renderer.py)
- ✅ Легко отследить логику навигации
- ✅ Глобальные клавиши (F1, F9, F12) управляются централизованно
- ✅ Renderer — единая точка управления всеми состояниями
- ✅ Виджет не нужно знать о существовании других состояний

**Недостатки:**
- Renderer немного раздувается (но это нормально, это его задача)

---

### Вариант 2: Обработка в Виджете (не выбран)

**Где обрабатывается:**
```python
# В gui_variablespanel.py
def handle_event(self, event):
    if event.key == pygame.K_ESCAPE or event.key == pygame.K_F9:
        # Сигнал в renderer: пожалуйста, переключись в 'main'
        self.on_close_requested()  # Callback
```

**Преимущества:**
- Виджет самодостаточен (знает как себя закрывать)
- Меньше кода в renderer

**Недостатки:**
- ❌ Нужно использовать callbacks/сигналы (усложнение)
- ❌ Логика переходов размазана по файлам
- ❌ Сложнее отследить где открывается/закрывается окно
- ❌ Виджет должен знать о глобальных клавишах (связанность)

---

## Рекомендация: Гибридный подход ✅

**Используйте вариант 1 (в Renderer), но с правилом:**

### Правило

| Кто обрабатывает | Что | Пример |
|---|---|---|
| **Renderer** | Глобальные клавиши, переходы между состояниями | F1, F9, F12 |
| **Виджет** | Локальная логика, навигация внутри окна | UP/DOWN в списке, Enter для выбора |

### Схема

```
Пользователь нажимает F9
    ↓
Renderer._handle_keyboard_main() перехватывает
    ↓
set_state('popup_simparams') ← Renderer управляет переходом
    ↓
VariablesPanel становится активен
    ↓
Пользователь нажимает UP/DOWN
    ↓
VariablesPanel.handle_event() обрабатывает локальную навигацию
    ↓
Пользователь нажимает Escape
    ↓
Renderer._handle_keyboard_popup_simparams() перехватывает
    ↓
set_state('main') ← Renderer управляет переходом
```

---

## Текущая реализация (popup_simparams)

### В Renderer

```python
# 1. Открытие из основного состояния
def _handle_keyboard_main(self, event):
    if event.key == pygame.K_F9:
        self.set_state('popup_simparams')  # ← Открыть

# 2. Обработка событий внутри popup
def _handle_keyboard_popup_simparams(self, event):
    if event.key == pygame.K_ESCAPE or event.key == pygame.K_F9:
        self.set_state('main')  # ← Закрыть

# 3. Отрисовка
def draw(self):
    if self.current_state == 'popup_simparams':
        self._draw_popup_simparams()

def _draw_popup_simparams(self):
    # TODO: self.variables_panel.draw(self.screen)
```

### В Виджете (VariablesPanel)

```python
# Только локальная обработка
def handle_event(self, event):
    if event.key == pygame.K_UP:
        self.move_selection_up()
    elif event.key == pygame.K_DOWN:
        self.move_selection_down()
    elif event.key == pygame.K_RETURN:
        self.edit_selected()
    # Escape/F9 обрабатываются renderer'ом, не виджетом
```

---

## Когда нарушить правило?

Есть ситуации, когда виджет может обрабатывать переходы:

### 1. Внутренние переходы в виджете (подэкраны)

```python
# Если у VariablesPanel есть разные режимы
def handle_event(self, event):
    if self.mode == 'normal':
        # Обработка навигации
    elif self.mode == 'editing':
        # Обработка редактирования
        if event.key == pygame.K_RETURN:
            self.mode = 'normal'  # Переход внутри виджета
```

### 2. Cascade close (когда нужно закрыть несколько окон)

```python
# Если при закрытии popup нужно остановить эксперимент
# renderer может проверить состояние других виджетов

def set_state(self, state_name):
    if state_name == 'main':
        # При возврате в main закрываем все подчиненные окна
        if self.experiment_modal.is_running:
            self.experiment_modal.stop()
```

---

## Итого

**Используйте текущую реализацию (Renderer управляет переходами):**
- ✅ Чистая архитектура
- ✅ Легко добавлять новые состояния
- ✅ Логика навигации в одном месте
- ✅ Виджеты независимы от системы состояний

**Когда добавите VariablesPanel:**
1. Раскомментируйте import
2. Инициализируйте в `__init__()`
3. Добавьте отрисовку в `_draw_popup_simparams()`
4. Обработка событий будет в `_handle_keyboard_popup_simparams()`
5. Сам виджет обрабатывает только локальные события (UP/DOWN и т.д.)

Всё остальное будет работать автоматически!
