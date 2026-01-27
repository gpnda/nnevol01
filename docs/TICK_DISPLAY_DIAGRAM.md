# 🎯 Быстрая шпаргалка: Как Tick попадает на экран

## Один рисунок говорит больше чем тысяча слов:

```
┌─────────────────────────────────────────────────────────────────┐
│                     LIFECYCLE ЭКСПЕРИМЕНТА                      │
└─────────────────────────────────────────────────────────────────┘

┌─ СЛОЙ 1: ЯДРО (Core Logic) ──────────────────────────────────┐
│                                                                 │
│  service/experiments/experiment_manager.py                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ExperimentManager (singleton)                            │ │
│  │  - active_experiment: ExperimentState                    │ │
│  │                                                           │ │
│  │  update() ─→ {                                           │ │
│  │    active_experiment.tick()  ← TICK УВЕЛИЧИВАЕТСЯ!      │ │
│  │    return _prepare_result_dto()                          │ │
│  │  }                                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          ↑                                      │
│                    (имеется в                                   │
│                     Application)                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ExperimentState (во время эксперимента)                 │ │
│  │  - current_tick: int = 0                                 │ │
│  │  - duration_ticks: int = 500                             │ │
│  │                                                           │ │
│  │  tick() ─→ {                                             │ │
│  │    self.current_tick += 1  ← ВОТ ЗДЕСЬ!                 │ │
│  │    self._update_snapshot()                               │ │
│  │    self._collect_metrics()                               │ │
│  │  }                                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          ↓ (возвращает)                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ExperimentResultDTO (data only)                          │ │
│  │  - status: str = "running"                               │ │
│  │  - current_tick: int = 42  ← НАШЕ ЗНАЧЕНИЕ!             │ │
│  │  - total_ticks: int = 500                                │ │
│  │  - current_energy: float = 1250.50                       │ │
│  │  - progress_percent: float = 8.4%                        │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─ СЛОЙ 2: ПЕРЕДАЧА ДАННЫХ (DTO Layer) ────────────────────────┐
│                                                                 │
│  renderer/v3dto/dto.py                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ RenderStateDTO (полный снимок состояния)                │ │
│  │  - world: WorldStateDTO                                  │ │
│  │  - params: SimulationParamsDTO                           │ │
│  │  - debug: DebugDataDTO                                   │ │
│  │  - selected_creature: SelectedCreaturePanelDTO           │ │
│  │  - experiment_result: Optional[ExperimentResultDTO]  ← ЗДЕСЬ!
│  │  - current_state: str = 'main'                           │ │
│  │  - tick: int                                              │ │
│  │  - fps: int                                               │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          ↑ (заполняется в)                     │
│  renderer/v3dto/renderer.py                                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Renderer._prepare_render_state_dto()                     │ │
│  │                                                           │ │
│  │  experiment_result = None                                │ │
│  │  if self.app.experiment_manager.is_active():             │ │
│  │    experiment_result = self.app.experiment_manager       │ │
│  │                        .get_current_result()             │ │
│  │                                                           │ │
│  │  return RenderStateDTO(                                  │ │
│  │    ...                                                    │ │
│  │    experiment_result=experiment_result,  ← ВСТАВЛЯЕМ!    │ │
│  │    ...                                                    │ │
│  │  )                                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          ↓ (передается в)                      │
└─────────────────────────────────────────────────────────────────┘

┌─ СЛОЙ 3: ВИДЖЕТ (GUI Widget) ────────────────────────────────┐
│                                                                 │
│  renderer/v3dto/gui_experiment.py                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ExperimentModal.draw(screen, render_state)              │ │
│  │                                                           │ │
│  │  if render_state.experiment_result is not None:          │ │
│  │    exp = render_state.experiment_result                  │ │
│  │    lines = [                                              │ │
│  │      f"Progress: {exp.current_tick} / {exp.total_ticks}"│ │
│  │      f"({exp.progress_percent:.1f}%)",  ← ОТОБРАЖАЕМ!    │ │
│  │      f"Energy: {exp.current_energy:.2f}",                │ │
│  │    ]                                                      │ │
│  │    for line in lines:                                    │ │
│  │      text_surface = self.font.render(line, True, ...)   │ │
│  │      screen.blit(text_surface, (x, y))  ← НА ЭКРАН!      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  РЕЗУЛЬТАТ НА ЭКРАНЕ:                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Experiment Status: RUNNING                               │ │
│  │ Progress: 42 / 500 ticks (8.4%)  ← ВИДИМ TICK!          │ │
│  │ Energy: 1250.50                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─ TIMING: Когда это все происходит? ──────────────────────────┐
│                                                                 │
│  Application.run() ─→ каждый frame:                           │
│                                                                 │
│  Tick 1:                                                       │
│  │  world.update()                                             │
│  │  if experiment_running:                                    │
│  │    exp_manager.update()                                    │
│  │      └─ exp_state.tick()  current_tick: 0 → 1             │
│  │  renderer.draw()                                            │
│  │    └─ _prepare_render_state_dto()                         │
│  │      └─ experiment_result.current_tick = 1  ← ОБНОВЛЕНО   │
│  │    └─ experiment_modal.draw(screen, render_state)          │
│  │      └─ выводит "Progress: 1 / 500"  ← НА ЭКРАН           │
│  │  pygame.display.flip()                                     │
│  │                                                             │
│  Tick 2:                                                       │
│  │  current_tick: 1 → 2                                       │
│  │  выводит "Progress: 2 / 500"                              │
│  │                                                             │
│  Tick 42:                                                      │
│  │  current_tick: 41 → 42                                     │
│  │  выводит "Progress: 42 / 500 (8.4%)"  ← ЭТО МЫ ВИДИМ     │
│  │                                                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Самое важное:

| Вопрос | Ответ |
|--------|--------|
| **Где увеличивается tick?** | `ExperimentState.tick()`, строка 107: `self.current_tick += 1` |
| **Как он передается в UI?** | Через `ExperimentResultDTO` → `RenderStateDTO.experiment_result` |
| **Как он отображается?** | `ExperimentModal.draw()` читает `render_state.experiment_result.current_tick` и выводит на экран |
| **Как часто обновляется?** | Каждый тик симуляции (когда Application.run() вызывает experiment_manager.update()) |
| **Что видит пользователь?** | `Progress: 42 / 500 ticks (8.4%)` |

## 🔗 Связь компонентов:

```
Application
    ↓ has
experiment_manager: ExperimentManager
    ↓ calls
experiment_manager.update()
    ↓ calls
active_experiment.tick()
    ↓ updates
current_tick += 1
    ↓ returns
ExperimentResultDTO(current_tick=42, ...)
    ↓ collected in
Renderer._prepare_render_state_dto()
    ↓ passed to
RenderStateDTO(experiment_result=...)
    ↓ used in
ExperimentModal.draw(screen, render_state)
    ↓ displays
"Progress: 42 / 500 ticks"
```

## 💡 Паттерн v3dto сохранен:

✅ Виджет (ExperimentModal) НЕ знает о ExperimentManager
✅ Виджет получает данные только через RenderStateDTO
✅ Управление через callback паттерн (like VariablesPanel)
✅ Полная тестируемость в изоляции (mock RenderStateDTO)
