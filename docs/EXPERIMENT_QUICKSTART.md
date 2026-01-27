# 🚀 Experiment Manager + ExperimentModal: Быстрый старт

## Что было сделано?

Связали виджет **ExperimentModal** с менеджером экспериментов **ExperimentManager**, чтобы отображать текущий номер tick при запущенном эксперименте.

## 4 файла были изменены:

### 1️⃣ `renderer/v3dto/dto.py`
**Добавлено поле**: `experiment_result: Optional[Any] = None` в `RenderStateDTO`
- Позволяет передавать данные эксперимента в виджеты через DTO

### 2️⃣ `renderer/v3dto/renderer.py`
**Обновлен метод**: `_prepare_render_state_dto()`
- Получает `experiment_result` из `experiment_manager`
- Вставляет в `RenderStateDTO`

### 3️⃣ `renderer/v3dto/gui_experiment.py`
**Обновлен метод**: `draw()`
- Проверяет `render_state.experiment_result`
- Отображает `current_tick / total_ticks` на экране

### 4️⃣ `service/experiments/experiment_manager.py`
**Убрана строка**: Отладочное сообщение из `update()`
- Было замусориваю консоль выводом каждый тик

## 📊 Где tick увеличивается:

```
service/experiments/experiment_manager.py
  ↓
ExperimentState.tick()  (строка 101-128)
  ↓
self.current_tick += 1  (строка 107) ← ВЫЧИСЛЕНИЕ TICK
```

## 📺 Что видит пользователь:

Когда эксперимент запущен:
```
Experiment Status: RUNNING
Progress: 42 / 500 ticks (8.4%)
Energy: 1250.50
```

- **42** - текущий tick (увеличивается каждый тик)
- **500** - максимум тиков (задается при start)
- **8.4%** - прогресс (вычисляется автоматически)
- **1250.50** - энергия всех существ

## 🔄 Поток данных за 5 шагов:

1. **Tick увеличивается**: `ExperimentState.current_tick += 1`
2. **Собирается DTO**: `ExperimentManager._prepare_result_dto()` → `ExperimentResultDTO`
3. **Передается в UI**: `Renderer._prepare_render_state_dto()` → `RenderStateDTO(experiment_result=...)`
4. **Виджет получает**: `ExperimentModal.draw(screen, render_state)`
5. **Отображается**: `render_state.experiment_result.current_tick` → на экран

## 🎮 Как запустить:

```bash
python nnevol.py
# 1. Клик на существо
# 2. F2 (открыть эксперимент)
# 3. S (стартовать)
# 4. Видишь: "Progress: 0 / 500", "Progress: 1 / 500", ...
# 5. X (остановить)
```

## ✅ Архитектура:

- ✅ **v3dto паттерн сохранен**: Виджет использует только DTO
- ✅ **Нет прямых зависимостей**: ExperimentModal не импортирует ExperimentManager
- ✅ **Callback паттерн**: Управление как в VariablesPanel
- ✅ **Zero coupling**: Полная изоляция

## 📚 Подробная документация:

- `docs/EXPERIMENT_ARCHITECTURE.md` - Полная архитектура
- `docs/TICK_DISPLAY_DIAGRAM.md` - Визуальная схема потока данных
- `docs/EXPERIMENT_CHANGES_SUMMARY.md` - Что точно изменилось

## 🔑 Ключевые файлы:

| Файл | Класс | Метод | Что |
|------|-------|-------|-----|
| `service/experiments/experiment_manager.py` | `ExperimentState` | `tick()` | Увеличивает `current_tick` |
| `renderer/v3dto/renderer.py` | `Renderer` | `_prepare_render_state_dto()` | Получает результат и вставляет в DTO |
| `renderer/v3dto/dto.py` | `RenderStateDTO` | - | Содержит `experiment_result` поле |
| `renderer/v3dto/gui_experiment.py` | `ExperimentModal` | `draw()` | Отображает `current_tick` на экране |

## 🧪 Для тестирования:

```python
# Проверить что tick увеличивается:
# В application.run() добавить print:
if self.is_running and self.experiment_manager.is_active():
    result = self.experiment_manager.update()
    if result:
        print(f"Tick: {result.current_tick} / {result.total_ticks}")

# Видишь вывод: Tick: 1 / 500, Tick: 2 / 500, ...
# Значит все работает!
```

## 💾 Версионирование:

Все файлы обновлены:
- ✅ Компилируются без ошибок
- ✅ Следуют v3dto паттерну
- ✅ Готовы к использованию
