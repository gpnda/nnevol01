# VariablesPanel перенесена в Renderer v2 ✅

## Что произошло

Виджет `VariablesPanel` успешно перенесен из `renderer/v1/` в `renderer/v2/` и интегрирован в новую архитектуру состояний.

## Структура renderer/v2

```
renderer/v2/
├── __init__.py
├── renderer.py              # Главный класс (система состояний)
├── gui_viewport.py          # Карта мира
└── gui_variablespanel.py   # Параметры симуляции ✅ НОВОЕ
```

## Интеграция в renderer.py

### 1. Импорт
```python
from renderer.v2.gui_variablespanel import VariablesPanel
```

### 2. Инициализация в __init__()
```python
self.variables_panel = VariablesPanel(world=self.world)
```

### 3. Обработка событий в _handle_keyboard_popup_simparams()
```python
def _handle_keyboard_popup_simparams(self, event):
    if event.key == pygame.K_ESCAPE or event.key == pygame.K_F9:
        self.set_state('main')
        return True
    
    # Обработка локальных событий (UP/DOWN/Enter) для панели
    if self.variables_panel.handle_event(event):
        return True
```

### 4. Отрисовка в _draw_popup_simparams()
```python
def _draw_popup_simparams(self):
    self.variables_panel.draw(self.screen)
```

## Функциональность

### Горячие клавиши

| Клавиша | Действие | Контекст |
|---------|---------|---------|
| **F9** | Открыть/закрыть панель параметров | main ↔ popup_simparams |
| **Escape** | Закрыть панель | popup_simparams → main |
| **↑/↓** | Навигация по переменным | popup_simparams |
| **Enter** | Редактирование значения | popup_simparams |
| **Backspace** | Удалить символ | режим редактирования |
| **Цифры/точка/минус** | Ввод значения | режим редактирования |
| **Escape (при редактировании)** | Отменить ввод | режим редактирования |

### Автоматическая пауза

При открытии popup_simparams (F9):
- `app.is_running = False` (симуляция паузируется автоматически)
- При закрытии (Escape) симуляция сохраняет свое состояние

### Параметры, которые можно редактировать

1. `mutation_probability` (0.0 - 1.0)
2. `mutation_strength` (0.0 - 100.0)
3. `creature_max_age` (1 - 100000)
4. `food_amount` (1 - 100000)
5. `food_energy_capacity` (0.0 - 50.0)
6. `food_energy_chunk` (0.0 - 50.0)
7. `reproduction_ages` (строка формата `[100, 200, 300]`)
8. `reproduction_offsprings` (1 - 100)
9. `energy_cost_tick` (0.0 - 100.0)
10. `energy_cost_speed` (0.0 - 100.0)
11. `energy_cost_rotate` (-20.0 - 50.0)
12. `energy_cost_bite` (0.0 - 1.0)
13. `energy_gain_from_food` (0.0 - 1.0)
14. `energy_gain_from_bite_cr` (0.0 - 1.0)
15. `energy_loss_bitten` (0.0 - 1.0)
16. `energy_loss_collision` (0.0 - 1.0)

### Callbacks

Каждая переменная имеет callback функцию, которая вызывается при изменении значения. Callback обновляет `simparams` и выполняет необходимые действия (например, обновление пищи в мире).

## Разделение ответственности

| Компонент | Ответственность |
|-----------|---|
| **Renderer** | Переходы между состояниями (F9), автоматическая пауза |
| **VariablesPanel** | Локальная навигация (UP/DOWN), редактирование значений, отрисовка |

## Отличия от v1

### v1 (VariablesPanel в v1)
- Был расположен рядом с другими панелями в основном состоянии
- Отрисовывался всегда, параллельно с Viewport

### v2 (VariablesPanel в v2)
- ✅ Является модальным окном (открывается по F9)
- ✅ Ставит симуляцию на паузу при открытии
- ✅ Полностью изолирован от других компонентов
- ✅ Интегрирован в систему состояний

## Проверка

Для проверки работы:

```bash
cd c:\WORK\evol
python nnevol.py
```

Затем:
1. Нажмите **F9** — должна открыться панель параметров и симуляция остановиться
2. Нажмите **↑/↓** — навигация по переменным
3. Нажмите **Enter** — редактирование выбранной переменной
4. Введите новое значение и нажмите **Enter** — значение сохранится
5. Нажмите **Escape** или **F9** — закрытие панели и возобновление симуляции

## TODO

Осталось перенести:
- [ ] `FunctionKeysPanel` 
- [ ] `CreaturesPopup` (список существ)
- [ ] `LogsPopup` (логи)
- [ ] `ExperimentModal` (окно экспериментов)
- [ ] `SelectedCreaturePanel` (информация о выбранном существе)
- [ ] `WorldStatsPanel` (статистика мира)

Каждый следующий виджет можно добавить по такому же паттерну.
