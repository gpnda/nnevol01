# Архитектура Экспериментов (Experiment Manager + GUI Widget)

## 🔗 Связь компонентов

```
Application (singleton)
    ↓ имеет
ExperimentManager (singleton)
    ↓ управляет
ExperimentState (временный)
    ↓ ведет
ExperimentResultDTO (data only)
    ↓ передается в
RenderStateDTO (DTO для виджетов)
    ↓ используется в
ExperimentModal (v3dto widget)
    ↓ callback на
Renderer._on_experiment_*()
    ↓ запускает
ExperimentManager.start_experiment()
```

## 📊 Поток данных: Запуск эксперимента

```
User нажимает S в ExperimentModal
    ↓
ExperimentModal.handle_keydown() → вызывает on_start_experiment(duration)
    ↓
Renderer._on_experiment_start(duration) (callback)
    ↓
self.app.experiment_manager.start_experiment(self.world, duration)
    ↓
ExperimentManager создает deepcopy(world) + ExperimentState
    ↓
ExperimentState.current_tick = 0 (инициализация)
```

## 📊 Поток данных: Каждый тик

```
Application.run() (основной loop)
    ↓ if experiment_running:
ExperimentManager.update()
    ↓
ExperimentState.tick()
    ↓
self.current_tick += 1  ← ВОТ ГДЕ TICK УВЕЛИЧИВАЕТСЯ!
    ↓
self._update_snapshot() → world.update()
    ↓
return should_continue
    ↓
ExperimentManager._prepare_result_dto()
    ↓ возвращает
ExperimentResultDTO(
    current_tick=exp.current_tick,
    total_ticks=exp.duration_ticks,
    ...
)
```

## 📊 Поток данных: Отрисовка информации о тиках

```
Renderer.draw()
    ↓
_prepare_render_state_dto()
    ↓
if self.app.experiment_manager.is_active():
    experiment_result = self.app.experiment_manager.get_current_result()
    ↓ (ExperimentResultDTO с current_tick и total_ticks)
    ↓
RenderStateDTO(experiment_result=experiment_result)
    ↓
ExperimentModal.draw(screen, render_state)
    ↓
if render_state.experiment_result is not None:
    exp = render_state.experiment_result
    lines.append(f"Progress: {exp.current_tick} / {exp.total_ticks}")
    lines.append(f"Energy: {exp.current_energy:.2f}")
    ↓
screen.blit(lines)  ← ОТОБРАЖЕНИЕ TICK'а НА ЭКРАНЕ!
```

## 🔑 Ключевые файлы и места

### 1. **ExperimentManager** (`service/experiments/experiment_manager.py`)
- **Класс**: `ExperimentManager`
- **Основной метод**: `update()` → вызывает `tick()`
- **Где увеличивается tick**: `ExperimentState.tick()` строка 107
  ```python
  def tick(self) -> bool:
      self.current_tick += 1  # ← УВЕЛИЧЕНИЕ TICK
      if self.current_tick >= self.duration_ticks:
          self.is_alive = False
  ```
- **Возврат результата**: `_prepare_result_dto()` → `ExperimentResultDTO`

### 2. **RenderStateDTO** (`renderer/v3dto/dto.py`)
- **Поле**: `experiment_result: Optional[Any] = None`
- **Тип**: `ExperimentResultDTO` из experiment_manager.py
- **Где заполняется**: `Renderer._prepare_render_state_dto()` строка 446

### 3. **Renderer** (`renderer/v3dto/renderer.py`)
- **Метод**: `_prepare_render_state_dto()` строка 432
- **Что делает**:
  ```python
  experiment_result = None
  if self.app.experiment_manager.is_active():
      experiment_result = self.app.experiment_manager.get_current_result()
  
  return RenderStateDTO(
      experiment_result=experiment_result,
      ...
  )
  ```

### 4. **ExperimentModal** (`renderer/v3dto/gui_experiment.py`)
- **Метод**: `draw(screen, render_state)` строка 141
- **Что отображает**:
  ```python
  if render_state.experiment_result is not None:
      exp = render_state.experiment_result
      lines.append(f"Progress: {exp.current_tick} / {exp.total_ticks}")
      lines.append(f"Energy: {exp.current_energy:.2f}")
  ```

## 🎮 Управление из виджета

### Callback паттерн:
```python
# В ExperimentModal.__init__():
self.on_start_experiment = on_start_experiment or (lambda x: None)
self.on_stop_experiment = on_stop_experiment or (lambda: None)

# Когда пользователь нажимает S:
def handle_keydown(event):
    if event.key == pygame.K_s:
        self.on_start_experiment(self.default_duration)  # Callback!

# В Renderer.__init__():
self.experiment_modal = ExperimentModal(
    on_start_experiment=self._on_experiment_start,
    on_stop_experiment=self._on_experiment_stop
)
```

## 📈 Пример вывода на экране

```
Experiment Status: RUNNING
Progress: 42 / 500 ticks (8.4%)
Energy: 1250.50
```

- **42** - текущий tick (увеличивается каждый тик)
- **500** - общее количество тиков (задается при старте)
- **8.4%** - прогресс (вычисляется автоматически из current_tick/total_ticks)
- **1250.50** - текущая энергия всех существ в эксперименте

## 🔄 Жизненный цикл эксперимента

```
1. IDLE (0 тиков)
   ↓
2. start_experiment(500) → ExperimentState.current_tick = 0
   ↓
3. RUNNING: Application.run() → ExperimentManager.update()
   - Каждый тик: current_tick += 1
   - Отображение: "Progress: 0 / 500", "Progress: 1 / 500", ...
   ↓
4. COMPLETED (когда current_tick >= 500 или нет существ)
   - Отображение: "Progress: 500 / 500 (100%)"
   - ExperimentManager.active_experiment = None
   ↓
5. IDLE (ожидание нового старта)
```

## ⚙️ Технические детали

### Где tick увеличивается?
**Файл**: `service/experiments/experiment_manager.py`
**Класс**: `ExperimentState`
**Метод**: `tick()` (строка 101-128)
**Строка**: `self.current_tick += 1` (строка 107)

### Как tick передается в UI?
1. `ExperimentState.current_tick` хранится в `ExperimentState`
2. `ExperimentManager.get_current_result()` создает `ExperimentResultDTO` с `current_tick`
3. `Renderer._prepare_render_state_dto()` добавляет `experiment_result` в `RenderStateDTO`
4. `ExperimentModal.draw()` получает `render_state.experiment_result.current_tick` и отображает его

### Что за ExperimentResultDTO?
```python
@dataclass
class ExperimentResultDTO:
    status: str                    # "running", "completed", "stopped"
    current_tick: int              # ← ТЕКУЩИЙ TICK
    total_ticks: int               # ← ВСЕГО ТИКОВ
    is_alive: bool
    current_energy: float
    current_position: tuple
    energy_history: List[float]
    position_history: List[tuple]
    
    @property
    def progress_percent(self) -> float:
        return (self.current_tick / self.total_ticks) * 100.0  # Автоматический подсчет %
```

## 🎯 Итого

**Вопрос**: Где увеличивается tick?
**Ответ**: `service/experiments/experiment_manager.py`, класс `ExperimentState`, метод `tick()`, строка 107

**Вопрос**: Как он отображается на экране?
**Ответ**: 
1. Увеличивается в ExperimentState.tick()
2. Собирается в ExperimentResultDTO._prepare_result_dto()
3. Передается через RenderStateDTO.experiment_result
4. Отображается в ExperimentModal.draw()

**Вопрос**: Как виджет управляет менеджером?
**Ответ**: Через callback паттерн (как VariablesPanel):
- ExperimentModal вызывает `self.on_start_experiment(duration)`
- Renderer передает callback: `on_start_experiment=self._on_experiment_start`
- Renderer вызывает `self.app.experiment_manager.start_experiment()`
