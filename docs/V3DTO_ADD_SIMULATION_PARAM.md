# Добавление нового параметра симуляции

Пример: параметр `teleport_probability` (вероятность телепортации существа в каждом тике).

Добавление параметра состоит из двух независимых частей:

1. **Основное приложение** — параметр объявлен, хранится и используется в логике симуляции.
2. **Renderer и DTO** — параметр пробрасывается в `SimulationParamsDTO` и редактируется из окна параметров, которое открывается клавишей **F9**.

Часть 2 нужна только для управления параметром из UI. Без неё параметр работает, но меняется только правкой `simparams.py`.

---

## Часть 1. Вмешательство в основное приложение

### 1.1. Объявить параметр в `simparams.py`

Файл: `simparams.py`, класс `SimParams`, метод `__init__`. Поместите строку в подходящую группу:

```python
# === Параметры существа ===
# Вероятность телепортации существа в каждом тике (0.0 .. 1.0)
self.teleport_probability = 0.0
```

- Значение по умолчанию `0.0` сохраняет текущее поведение симуляции.
- Комментарий нужен, потому что смысл параметра не очевиден из имени.

### 1.2. Использовать параметр в логике симуляции

Параметр читается через глобальный синглтон:

```python
from simparams import sp

if random.random() < sp.teleport_probability:
    ...  # логика телепортации
```

Место размещения зависит от того, что меняется:

| Что меняется | Где читать параметр |
|---|---|
| Поведение отдельного существа | `creature.py`, метод `update()` |
| Мир, еда, стены | `world.py`, метод `update()` |
| Генерация мира | `world_generator.py` |

Ориентир: в `world.py` вероятность штрафа зон проверяется как `random.random() > sp.zones_penalty_probability`.

### 1.3. Сохранение и загрузка мира

Отдельных действий не требуется:

- `_serialize_simparams()` в `service/world_persistence/world_persistence.py` сохраняет все публичные атрибуты `sp` автоматически.
- `_restore_simparams()` восстанавливает только те параметры, которые существуют в `sp`.
- Старые сохранения, в которых параметра нет, загружаются со значением по умолчанию.

---

## Часть 2. Вмешательство в renderer и DTO (управление с F9)

Цепочка данных для параметра:

```
simparams.sp ──► Renderer._prepare_simulation_params_dto() ──► SimulationParamsDTO
                                                                      │
                                                                      ▼
                                                     RenderStateDTO.params
                                                                      │
                                                                      ▼
   VariablesPanel.update_from_render_state()  ◄───────────────────────┘
          │
          │ пользователь вводит значение (F9)
          ▼
   VariablesPanel callback ──► Renderer._on_parameter_change() ──► setattr(sp, ...)
```

### 2.1. Добавить поле в `SimulationParamsDTO`

Файл: `renderer/v3dto/dto.py`, класс `SimulationParamsDTO`. Поле без значения по умолчанию:

```python
# Телепортация
teleport_probability: float
```

### 2.2. Заполнить поле в фабричном методе

Файл: `renderer/v3dto/renderer.py`, метод `_prepare_simulation_params_dto()`:

```python
teleport_probability=sp.teleport_probability,
```

Если поле есть в DTO, но не передано в конструктор, будет `TypeError`.

### 2.3. Зарегистрировать параметр в `VariablesPanel`

Файл: `renderer/v3dto/gui_variablespanel.py`.

**a) В `__init__`** добавить переменную с типом, границами и комментарием:

```python
self.add_variable("teleport_probability", float, min_val=0.0, max_val=1.0,
                  comment="Probability of a creature teleporting each tick")
```

**b) В `update_from_render_state()`** добавить копирование значения из DTO:

```python
self.variables['teleport_probability']['value'] = params_dto.teleport_probability
```

Если пропустить пункт (b), панель покажет пустое значение.

### 2.4. Обработка изменения в `Renderer._on_parameter_change()`

Файл: `renderer/v3dto/renderer.py`.

- Метод уже универсален: проверяет `hasattr(sp, param_name)` и делает `setattr(sp, param_name, value)`.
- Для параметра без побочных эффектов **ничего добавлять не нужно**.
- Ветку `if param_name == ...` добавляют только при побочном эффекте. Примеры в коде:
  - `food_amount` → `world.change_food_capacity()`;
  - `reproduction_ages` → пересчёт `creature.birth_ages` у всех существ.

### 2.5. Окно параметров по F9

Клавиша открывает состояние `popup_simparams` (`Renderer._handle_keyboard_main`, `K_F9`). Закрывается клавишами **Esc** или **F9**. Во время открытого окна симуляция на паузе.

---

## Проверка

1. Запустите приложение: `python nnevol.py`.
2. Нажмите **F9**: должно открыться окно параметров.
3. Найдите `teleport_probability`: значение должно быть `0.0`.
4. Измените значение и подтвердите. В консоли должна появиться строка:
   `✓ Parameter updated: teleport_probability = ...`
5. Закройте окно (Esc или F9) и убедитесь, что логика из пункта 1.2 использует новое значение.
6. Сохраните мир, загрузите его и проверьте, что значение восстановилось.

---

## Чек-лист

**Основное приложение**
- [ ] Параметр объявлен в `SimParams.__init__` с значением по умолчанию и комментарием
- [ ] Параметр используется в логике через `sp.<имя>`

**Renderer и DTO**
- [ ] Поле добавлено в `SimulationParamsDTO`
- [ ] Поле заполнено в `Renderer._prepare_simulation_params_dto()`
- [ ] Переменная добавлена в `VariablesPanel.__init__` через `add_variable`
- [ ] Значение копируется в `VariablesPanel.update_from_render_state()`
- [ ] При необходимости добавлен побочный эффект в `Renderer._on_parameter_change()`

---

## Связанные документы

- [V3DTO_QUICK_START.md](./V3DTO_QUICK_START.md) — общая схема DTO
- [V3DTO_WIDGET_DEVELOPMENT_MANUAL.md](./V3DTO_WIDGET_DEVELOPMENT_MANUAL.md) — правила разработки виджетов
- [V3DTO_WIDGET_VISUAL_ARCHITECTURE.md](./V3DTO_WIDGET_VISUAL_ARCHITECTURE.md) — callback-паттерн
