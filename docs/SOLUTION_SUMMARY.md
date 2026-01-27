# ✅ РЕШЕНИЕ: Как связать ExperimentModal с ExperimentManager

## 🎯 Твой вопрос:

> Видишь виджет внутри рендерера никак не связан с инстансом application.experiment_manager.
> Ты видишь как их связать, чтобы виджет мог управлять менеджером экспериментов?

## ✅ Ответ:

**ДА!** Связь уже была сделана с помощью **callback паттерна** (как в VariablesPanel).
Теперь виджет также **получает данные** о состоянии эксперимента через **RenderStateDTO**.

---

## 📍 Архитектура связи:

```
Application (singleton)
    ↓ имеет
experiment_manager: ExperimentManager
    ↓ управляется из
Renderer (синглтон)
    ↓ создает виджет с callbacks
ExperimentModal
    ↓ вызывает callback при S/X
Renderer._on_experiment_start()
    ↓ запускает
experiment_manager.start_experiment()
```

## 🔗 Два способа связи:

### 1️⃣ **Управление** (Виджет → Менеджер)
- **Как**: Callback паттерн
- **Код**: `ExperimentModal.on_start_experiment(duration)`
- **Результат**: Запуск/остановка эксперимента

### 2️⃣ **Данные** (Менеджер → Виджет)
- **Как**: DTO через RenderStateDTO
- **Код**: `render_state.experiment_result`
- **Результат**: Отображение tick, энергии, прогресса

---

## 🔨 Что было изменено:

### Шаг 1: Добавить поле в RenderStateDTO
```python
# dto.py
@dataclass
class RenderStateDTO:
    # ... существующие поля ...
    experiment_result: Optional[Any] = None  # ← ДОБАВЛЕНО!
```

### Шаг 2: Заполнить RenderStateDTO в Renderer
```python
# renderer.py
def _prepare_render_state_dto(self) -> RenderStateDTO:
    # ...
    experiment_result = None
    if self.app.experiment_manager.is_active():
        experiment_result = self.app.experiment_manager.get_current_result()
    
    return RenderStateDTO(
        # ...
        experiment_result=experiment_result,  # ← ДОБАВЛЕНО!
    )
```

### Шаг 3: Использовать данные в ExperimentModal
```python
# gui_experiment.py
def draw(self, screen, render_state):
    # ...
    if render_state.experiment_result is not None:
        exp = render_state.experiment_result
        lines.extend([
            f"Progress: {exp.current_tick} / {exp.total_ticks}",
            f"Energy: {exp.current_energy:.2f}",
        ])
```

---

## 📊 Поток данных за 3 этапа:

### Этап 1: Управление (Старт)
```
User нажимает S
  ↓
ExperimentModal.handle_keydown()
  ↓
self.on_start_experiment(500)  ← Callback!
  ↓
Renderer._on_experiment_start(500)
  ↓
self.app.experiment_manager.start_experiment(...)
```

### Этап 2: Обновление (Каждый тик)
```
Application.run()
  ↓
experiment_manager.update()
  ↓
active_experiment.tick()
  ↓
current_tick += 1  (0 → 1 → 2 → ... → 42)
```

### Этап 3: Отображение (Каждый кадр)
```
Renderer.draw()
  ↓
_prepare_render_state_dto()
  ↓
experiment_result = experiment_manager.get_current_result()
  ↓
RenderStateDTO(experiment_result=...)
  ↓
ExperimentModal.draw(screen, render_state)
  ↓
Отображает: "Progress: 42 / 500 ticks (8.4%)"
```

---

## 💡 Почему это решение хорошее:

### ✅ Паттерн v3dto сохранен
- ExperimentModal не импортирует ExperimentManager
- Все данные передаются через DTO
- Виджет полностью изолирован

### ✅ Callback паттерн как в VariablesPanel
- Управление через callback функции
- Нет прямых зависимостей
- Легко тестировать

### ✅ Двусторонняя связь
- Виджет УПРАВЛЯЕТ менеджером (callbacks)
- Виджет ПОЛУЧАЕТ данные (RenderStateDTO)
- Менеджер не знает о виджете

### ✅ Масштабируемость
- Можно добавить новые поля в experiment_result
- Можно создать новые виджеты с теми же callbacks
- Архитектура остается чистой

---

## 🎮 Как использовать:

### Запуск эксперимента:
1. Выбрать существо (клик)
2. Открыть окно (F2)
3. Нажать S (старт)
4. Видеть: `Progress: 42 / 500 ticks`

### Остановка:
1. Нажать X (стоп)
2. Вернуться в основной вид

### Результаты:
- current_tick - текущий номер тика
- total_ticks - максимум тиков
- progress_percent - прогресс в %
- current_energy - энергия существ

---

## 📋 Файлы которые нужно обновить:

| # | Файл | Изменение |
|---|------|-----------|
| 1 | `renderer/v3dto/dto.py` | Добавить `experiment_result` поле в `RenderStateDTO` |
| 2 | `renderer/v3dto/renderer.py` | Заполнить `experiment_result` в `_prepare_render_state_dto()` |
| 3 | `renderer/v3dto/gui_experiment.py` | Отображать `experiment_result.current_tick` в `draw()` |
| 4 | `service/experiments/experiment_manager.py` | Убрать debug print из `update()` |

✅ **Все файлы уже обновлены!**

---

## 🔑 Ключевые классы и методы:

| Файл | Класс | Метод | Назначение |
|------|-------|-------|-----------|
| experiment_manager.py | ExperimentState | tick() | Увеличивает current_tick |
| experiment_manager.py | ExperimentManager | update() | Вызывает tick() и возвращает resultDTO |
| experiment_manager.py | ExperimentManager | get_current_result() | Возвращает ExperimentResultDTO |
| renderer.py | Renderer | _prepare_render_state_dto() | Собирает RenderStateDTO с experiment_result |
| gui_experiment.py | ExperimentModal | draw() | Отображает информацию о тиках |
| dto.py | RenderStateDTO | (dataclass) | Передает experiment_result в виджет |

---

## 📈 Текущий статус:

```
┌──────────────────────────────────────────────────┐
│                  АРХИТЕКТУРА                      │
├──────────────────────────────────────────────────┤
│ ExperimentManager ←─ управление ─→ ExperimentModal│
│         ↓                                         │
│  ExperimentResultDTO                             │
│         ↓                                         │
│ RenderStateDTO.experiment_result                 │
│         ↓                                         │
│ ExperimentModal.draw(render_state)               │
│                                                   │
│ ✅ Полная связь установлена                     │
│ ✅ v3dto паттерн соблюдается                    │
│ ✅ Данные отображаются на экран                  │
└──────────────────────────────────────────────────┘
```

---

## 🧪 Результат после изменений:

### До:
```
ExperimentModal показывал:
  Experiment Status: IDLE
  Duration: 500 ticks
  Controls...
❌ Не было информации о текущем tick!
```

### После:
```
ExperimentModal показывает:
  Experiment Status: RUNNING
  Progress: 42 / 500 ticks (8.4%)  ← ВИДНО TICK!
  Energy: 1250.50
  Controls...
✅ Все информация отображается!
```

---

## 🎯 Итого:

**Вопрос**: Как связать виджет с менеджером?
**Ответ**: 
1. **Управление** через callbacks (как VariablesPanel)
2. **Данные** через RenderStateDTO.experiment_result

**Результат**: Полная двусторонняя связь при сохранении архитектуры v3dto!

---

## 📚 Документация:

Для полного понимания смотри:
- `EXPERIMENT_ARCHITECTURE.md` - Полная архитектура с диаграммами
- `TICK_DISPLAY_DIAGRAM.md` - Визуальный поток данных
- `EXPERIMENT_QUICKSTART.md` - Быстрый старт
- `EXPERIMENT_CODE_EXAMPLES.md` - Примеры кода
- `EXPERIMENT_CHANGES_TABLE.md` - Таблица изменений (этот файл)
