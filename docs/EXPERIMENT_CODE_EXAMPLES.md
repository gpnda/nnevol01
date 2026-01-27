# 💻 Примеры кода: Как Tick передается на экран

## Пример 1: Увеличение Tick в ExperimentState

**Файл**: `service/experiments/experiment_manager.py`

```python
class ExperimentState:
    def __init__(self, world_snapshot, duration_ticks: int):
        self.current_tick = 0  # ← НАЧАЛЬНО: 0
        self.duration_ticks = duration_ticks  # ← 500
    
    def tick(self) -> bool:
        """Один тик эксперимента."""
        self.current_tick += 1  # ← УВЕЛИЧЕНИЕ! 0 → 1 → 2 → 42 → ...
        
        if self.current_tick >= self.duration_ticks:  # ← ЕСЛИ 42 < 500
            self.is_alive = False
            return False
        
        self._update_snapshot()
        self._collect_metrics()
        return True
```

## Пример 2: Возврат результата с Tick в ExperimentResultDTO

**Файл**: `service/experiments/experiment_manager.py`

```python
@dataclass
class ExperimentResultDTO:
    """DTO с tick для передачи в UI."""
    status: str
    current_tick: int          # ← НАША ПЕРЕМЕННАЯ!
    total_ticks: int           # ← 500
    is_alive: bool
    current_energy: float
    current_position: tuple
    
    @property
    def progress_percent(self) -> float:
        """Прогресс в процентах (0-100)."""
        if self.total_ticks <= 0:
            return 0.0
        return (self.current_tick / self.total_ticks) * 100.0  # ← 8.4%

class ExperimentManager:
    def _prepare_result_dto(self) -> ExperimentResultDTO:
        """Создать DTO с текущим состоянием."""
        exp = self.active_experiment
        
        return ExperimentResultDTO(
            status="running",
            current_tick=exp.current_tick,      # ← БЕРЕМ CURRENT_TICK!
            total_ticks=exp.duration_ticks,     # ← 500
            is_alive=exp.is_alive,
            current_energy=sum(...),
            current_position=(avg_x, avg_y),
        )
```

## Пример 3: Передача в RenderStateDTO через Renderer

**Файл**: `renderer/v3dto/renderer.py`

```python
class Renderer:
    def _prepare_render_state_dto(self) -> RenderStateDTO:
        """Собрать полный DTO для всех виджетов."""
        world_dto = self._prepare_world_dto()
        params_dto = self._prepare_simulation_params_dto()
        debug_dto = self._prepare_debug_dto()
        selected_creature_dto = self._prepare_selected_creature_dto(world_dto)
        
        # ← ПОЛУЧИТЬ РЕЗУЛЬТАТ ЭКСПЕРИМЕНТА
        experiment_result = None
        if self.app.experiment_manager.is_active():
            experiment_result = self.app.experiment_manager.get_current_result()
        
        # ← ВСТАВИТЬ В RenderStateDTO
        return RenderStateDTO(
            world=world_dto,
            params=params_dto,
            debug=debug_dto,
            selected_creature=selected_creature_dto,
            experiment_result=experiment_result,  # ← ДОБАВИЛИ!
            current_state=self.current_state,
            tick=self.world.tick,
            fps=self.fps,
        )
```

## Пример 4: Отображение Tick в ExperimentModal

**Файл**: `renderer/v3dto/gui_experiment.py`

```python
class ExperimentModal:
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        """Отрисовка модального окна."""
        # ... отрисовка фона и заголовка ...
        
        if self.selected_creature_id is None:
            msg = self.font.render("No creature selected", True, self.COLORS['text'])
            screen.blit(msg, (content_x, content_y))
        else:
            # ← ОСНОВНАЯ ЛОГИКА
            lines = [
                f"Selected Creature ID:",
                f"  {self.selected_creature_id}",
                f"",
                f"Experiment Status: {'RUNNING' if self.experiment_running else 'IDLE'}",
            ]
            
            # ← ПРОВЕРИТЬ ЕСТЬ ЛИ РЕЗУЛЬТАТ ЭКСПЕРИМЕНТА
            if render_state.experiment_result is not None:
                exp = render_state.experiment_result
                # ← ДОБАВИТЬ ИНФОРМАЦИЮ О TICK
                lines.extend([
                    f"Progress: {exp.current_tick} / {exp.total_ticks} ticks ({exp.progress_percent:.1f}%)",
                    f"Energy: {exp.current_energy:.2f}",
                ])
            else:
                lines.append(f"Duration: {self.default_duration} ticks")
            
            lines.extend([
                f"",
                f"Controls:",
                f"  S - Start experiment",
                f"  X - Stop experiment",
            ])
            
            # ← ОТРИСОВАТЬ ВСЕ СТРОКИ
            for line in lines:
                if line.startswith("  "):
                    text_surface = self.font.render(line, True, self.COLORS['value'])
                elif line.startswith("Experiment Status"):
                    color = self.COLORS['value'] if self.experiment_running else self.COLORS['text']
                    text_surface = self.font.render(line, True, color)
                else:
                    text_surface = self.font.render(line, True, self.COLORS['label'])
                
                screen.blit(text_surface, (content_x, content_y))
                content_y += self.LINE_HEIGHT
```

## Пример 5: Полный Flow за один кадр

```python
# application.py - Application.run()
class Application:
    def run(self):
        while self.is_running:
            # Обновить симуляцию
            if self.is_running:
                self.world.update()
                self.world.update_map()
            
            # ← ОБНОВИТЬ ЭКСПЕРИМЕНТ (ЕСЛИ АКТИВЕН)
            if self.experiment_manager.is_active():
                result = self.experiment_manager.update()
                # result.current_tick == 42 (например)
            
            # Отрисовать
            if self.animate_flag:
                self.renderer.draw()  # ← ИСПОЛЬЗУЕТ experiment_result ДЛЯ ОТРИСОВКИ
            
            self.renderer.control_run()
            self.clock.tick(self.max_fps)
```

## Пример 6: Шаг за шагом - что происходит

```python
# Tick 1 (на экране: Progress: 0 / 500)
ExperimentState.current_tick = 0
tick() → current_tick = 1

# Tick 2 (на экране: Progress: 1 / 500)
tick() → current_tick = 2

# ...

# Tick 42 (на экране: Progress: 41 / 500 (8.2%))
tick() → current_tick = 42

# Что-то
Renderer.draw():
    _prepare_render_state_dto():
        experiment_result = experiment_manager.get_current_result()
        # experiment_result.current_tick = 42
        return RenderStateDTO(experiment_result=...)
    
    experiment_modal.draw(screen, render_state):
        if render_state.experiment_result is not None:
            exp = render_state.experiment_result
            lines.append(f"Progress: {exp.current_tick} / {exp.total_ticks}")
            # lines.append("Progress: 42 / 500 (8.4%)")
            screen.blit(line)  # ← НА ЭКРАН!
```

## Пример 7: RenderStateDTO изменилось

**Было**:
```python
@dataclass
class RenderStateDTO:
    world: WorldStateDTO
    params: SimulationParamsDTO
    debug: DebugDataDTO
    selected_creature: Optional[SelectedCreaturePanelDTO] = None
    current_state: str = 'main'
    tick: int = 0
    fps: int = 0
```

**Стало**:
```python
@dataclass
class RenderStateDTO:
    world: WorldStateDTO
    params: SimulationParamsDTO
    debug: DebugDataDTO
    selected_creature: Optional[SelectedCreaturePanelDTO] = None
    experiment_result: Optional[Any] = None  # ← ДОБАВЛЕНО!
    current_state: str = 'main'
    tick: int = 0
    fps: int = 0
```

## Пример 8: Как запустить эксперимент из виджета

```python
# renderer/v3dto/gui_experiment.py
class ExperimentModal:
    def __init__(self, 
                 on_start_experiment: Optional[Callable[[int], None]] = None,
                 on_stop_experiment: Optional[Callable[[], None]] = None):
        self.on_start_experiment = on_start_experiment or (lambda x: None)
        self.on_stop_experiment = on_stop_experiment or (lambda: None)
    
    def handle_keydown(self, event: pygame.event.Event) -> bool:
        if event.key == pygame.K_s:  # S - Start
            self.on_start_experiment(self.default_duration)  # ← CALLBACK!
            return True

# renderer/v3dto/renderer.py
class Renderer:
    def __init__(self, app, world):
        self.app = app
        self.world = world
        
        # ← ПЕРЕДАТЬ CALLBACKS В ВИДЖЕТ
        self.experiment_modal = ExperimentModal(
            on_start_experiment=self._on_experiment_start,
            on_stop_experiment=self._on_experiment_stop
        )
    
    def _on_experiment_start(self, duration_ticks: int):
        """Callback из ExperimentModal - запустить эксперимент."""
        self.app.experiment_manager.start_experiment(
            self.world, 
            duration_ticks
        )
    
    def _on_experiment_stop(self):
        """Callback из ExperimentModal - остановить эксперимент."""
        self.app.experiment_manager.stop_experiment()
```

## Пример 9: Проверка что все работает

```python
# Добавить в application.py для отладки:
class Application:
    def run(self):
        while self.is_running:
            self.world.update()
            self.world.update_map()
            
            if self.experiment_manager.is_active():
                result = self.experiment_manager.update()
                # ← ПРОВЕРИТЬ ЧТО TICK УВЕЛИЧИВАЕТСЯ
                print(f"Experiment tick: {result.current_tick} / {result.total_ticks}")
            
            if self.animate_flag:
                self.renderer.draw()
            
            self.renderer.control_run()
            self.clock.tick(self.max_fps)

# Вывод в консоль будет:
# Experiment tick: 1 / 500
# Experiment tick: 2 / 500
# Experiment tick: 3 / 500
# ...
# Experiment tick: 42 / 500
# ...
```

## Итого: Как это работает

```
┌─────────────────────────────────────┐
│ ExperimentState.tick()              │
│ self.current_tick += 1 (0 → 1 → 42) │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ ExperimentResultDTO                 │
│ current_tick = 42                   │
│ total_ticks = 500                   │
│ progress_percent = 8.4%             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ RenderStateDTO                      │
│ experiment_result = ResultDTO        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ ExperimentModal.draw()              │
│ render_state.experiment_result      │
│ .current_tick                       │
│         ↓                           │
│ "Progress: 42 / 500 (8.4%)"        │
└─────────────────────────────────────┘
              ↓
         НА ЭКРАН!
```
