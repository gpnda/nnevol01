# V3DTO Widget Architecture - Visual Diagrams

Визуальные диаграммы архитектуры v3dto и процессов.

---

## 1. DTO Изоляция - Общая Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│  (Application управляет главным циклом)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                             │
│  (Singletons - world, logger, debugger, simparams)         │
│  ✓ Полная власть над состоянием                            │
│  ✓ Изменяют друг друга                                     │
│  ✓ Сложные interdependencies                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
                    [DTO FACTORY]
                     │
           ┌─────────┼─────────┬──────────┐
           ↓         ↓         ↓          ↓
      WorldStateDTO ParamsDTO DebugDTO SelectedCreatureDTO
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              RenderStateDTO (КОНТЕЙНЕР ДАННЫХ)              │
│  ✓ Чистые данные                                            │
│  ✓ БЕЗ методов                                              │
│  ✓ БЕЗ side effects                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        ↓            ↓            ↓              ↓
    Widget1     Widget2      Widget3         Widget4
  (Viewport)  (SelectedCtx)  (Variables)    (History)
        │            │            │              │
        └────────────┴────────────┴──────────────┘
                     │
                     ↓
              [PYGAME SCREEN]
                Display!

┌─────────────────────────────────────────────────────────────┐
│  КЛЮЧЕВАЯ ОСОБЕННОСТЬ: Widgets НЕ ЗНАЮТ о Singletons!    │
│  Они работают ТОЛЬКО с DTO данными                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Данные Течение (Data Flow) - За Один Frame

```
                    START OF FRAME
                         │
        ┌────────────────┴────────────────┐
        │                                 │
    ┌───▼──────────────┐      ┌──────────▼─────┐
    │ Simulation Loop  │      │ Render Loop     │
    │ (world.update()) │      │                 │
    └────────┬─────────┘      │                 │
             │                │                 │
    Game state changes        │                 │
    (creatures move,          │                 │
     energy changes)          │                 │
             │                │                 │
             │        ┌───────▼────────┐       │
             │        │ Renderer.draw()│       │
             │        └────┬───────────┘       │
             │             │                   │
             │    ┌────────▼─────────┐         │
             │    │Prepare DTO Layer:│         │
             │    │                  │         │
             │    │WorldStateDTO()   │ ← world
             │    │ParamsDTO()       │ ← simparams
             │    │DebugDTO()        │ ← debugger
             │    │HistoryDTO()      │ ← logger
             │    └────┬──────────────┘         │
             │         │                        │
             │    ┌────▼──────────────────┐    │
             │    │ RenderStateDTO        │    │
             │    │ (главный контейнер)   │    │
             │    └────┬──────────────────┘    │
             │         │                        │
             │    ┌────┴───────┬────────┬────────┐
             │    │            │        │        │
             │    ▼            ▼        ▼        ▼
             │  Widget1    Widget2  Widget3  Widget4
             │    │            │        │        │
             │    │ Рисуют на свой surface (БЕЗ побочных эффектов)
             │    │            │        │        │
             │    └────┬───────┴────────┴────────┘
             │         │
             │    ┌────▼──────────────┐
             │    │ pygame.display.flip()
             │    │ (обновить экран) │
             │    └───────────────────┘
             │
        ┌────▼────────────────┐
        │ Process Input Events│
        │ (keyboard, mouse)   │
        └────────┬────────────┘
                 │
        State changes from events
        (pause, parameter changes)
                 │
                 ▼
         END OF FRAME (FPS limited)
```

---

## 3. Структура RenderStateDTO

```
┌─────────────────────────────────────────────────────────┐
│                  RenderStateDTO                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ world: WorldStateDTO                             │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ ├─ map: np.ndarray[height, width]              │   │
│ │ │   (0=empty, 1=wall, 2=food, 3=creature)      │   │
│ │ ├─ width, height: int                           │   │
│ │ ├─ creatures: List[CreatureDTO]                 │   │
│ │ │   ├─ id, x, y, angle, energy, age            │   │
│ │ │   ├─ speed, generation, bite_effort          │   │
│ │ │   └─ vision_distance, bite_range              │   │
│ │ └─ foods: List[FoodDTO]                         │   │
│ │     └─ x, y, energy                             │   │
│ │                                                  │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ params: SimulationParamsDTO                      │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ ├─ mutation_probability: float                  │   │
│ │ ├─ food_amount: int                             │   │
│ │ ├─ reproduction_ages: List[int]                 │   │
│ │ ├─ energy_cost_*: float (movement, rotate, etc)│   │
│ │ └─ energy_gain_from_food: float                 │   │
│ │                                                  │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ debug: DebugDataDTO                              │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ ├─ raycast_dots: Dict[creature_id, List]       │   │
│ │ └─ visions: Dict[creature_id, List]             │   │
│ │                                                  │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ selected_creature: Optional[SelectedCreaturePanelDTO]│
│ ├──────────────────────────────────────────────────┤   │
│ │ ├─ creature: CreatureDTO (данные существа)     │   │
│ │ └─ history: CreatureHistoryDTO                  │   │
│ │     ├─ energy_history: List[float]              │   │
│ │     └─ events: List[CreatureEventDTO]           │   │
│ │                                                  │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ current_state: str ('main', 'popup', etc)       │   │
│ │ tick: int                                        │   │
│ │ fps: int                                         │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ ВАЖНО: Никаких методов, только данные!               │
│ ВАЖНО: Все виджеты получают один и тот же DTO!       │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Жизненный Цикл Виджета

```
┌──────────────────────────────────────────────────────────┐
│              ИНИЦИАЛИЗАЦИЯ (программа стартует)         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Renderer.__init__(world, app):                         │
│      self.my_widget = MyWidget()  ← БЕЗ параметров!    │
│                                                          │
│  MyWidget.__init__(self):                               │
│      self.rect = pygame.Rect(...)                       │
│      self.surface = pygame.Surface(...)                 │
│      self.font = pygame.font.Font(...) ← с fallback!   │
│      self.state = (если нужно)                          │
│                                                          │
│  [Виджет готов к использованию]                        │
│                                                          │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────────┐
│          ИГРОВОЙ ЦИКЛ (каждый frame, 60 FPS)            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ Этап 1: Подготовка Данных                          │
│  │   Renderer._prepare_render_state_dto()               │
│  │       ├─ world → WorldStateDTO                       │
│  │       ├─ simparams → SimulationParamsDTO             │
│  │       ├─ logger → CreatureHistoryDTO                 │
│  │       └─ debugger → DebugDataDTO                     │
│  │   RenderStateDTO (контейнер всех DTO)               │
│  │                                                       │
│  ├─ Этап 2: Отрисовка                                  │
│  │   Renderer.draw(screen):                             │
│  │       self.my_widget.draw(screen, render_state)      │
│  │                                                       │
│  │   MyWidget.draw(screen, render_state):               │
│  │       self.surface.fill(COLORS['background'])        │
│  │       ├─ Получить данные из render_state            │
│  │       ├─ Нарисовать на self.surface                  │
│  │       └─ screen.blit(self.surface, (x, y))          │
│  │                                                       │
│  │   [Виджет не создаёт побочные эффекты!]            │
│  │                                                       │
│  ├─ Этап 3: Обновление Дисплея                         │
│  │   pygame.display.flip()                              │
│  │                                                       │
│  └─ Этап 4: Обработка Событий                          │
│      Renderer.control_run():                            │
│          for event in pygame.event.get():              │
│              if event.type == KEYDOWN:                  │
│                  if my_widget.handle_keydown(event):   │
│                      # Виджет обработал событие        │
│                                                       │
│              if event.type == MOUSEBUTTONDOWN:         │
│                  if my_widget.handle_mousebuttondown(): │
│                      # Виджет обработал событие        │
│                                                       │
│  [Повторяется каждый frame]                            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 5. Взаимодействие Виджетов и Renderer'а

```
┌───────────────────────────────────────────────────────────┐
│                    RENDERER                               │
│  (Единственный компонент, имеющий access к Singletons)   │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Has: world, app, logger, debugger, simparams     │    │
│  │      (singletons)                                │    │
│  │                                                  │    │
│  │ draw():                                          │    │
│  │   ├─ Prepare DTO from singletons                │    │
│  │   └─ Call each widget.draw(screen, render_state)│    │
│  │                                                  │    │
│  │ control_run():                                  │    │
│  │   ├─ Get events                                 │    │
│  │   └─ Call each widget.handle_*(event)           │    │
│  │                                                  │    │
│  │ _on_parameter_change(param, value):            │    │
│  │   └─ Modify singleton state (side effects!)    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│       ↓                    ↓                   ↓          │
│  ┌────────┐         ┌─────────────┐     ┌──────────┐    │
│  │Widget1 │         │Widget2      │     │Widget3   │    │
│  │(View)  │         │(Interactive)│     │(Modal)   │    │
│  │        │         │             │     │          │    │
│  │Has:    │         │Has:         │     │Has:      │    │
│  │- rect  │         │- rect       │     │- rect    │    │
│  │- surface         │- surface    │     │- surface │    │
│  │- state │         │- state      │     │- state   │    │
│  │        │         │             │     │          │    │
│  │Knows:  │         │Knows:       │     │Knows:    │    │
│  │- DTO   │         │- DTO        │     │- DTO     │    │
│  │- pygame│         │- pygame     │     │- pygame  │    │
│  │        │         │- callback   │     │- keyboard│    │
│  │        │         │             │     │- events  │    │
│  │        │         │             │     │          │    │
│  │NO:     │         │NO:          │     │NO:       │    │
│  │- world │         │- world      │     │- world   │    │
│  │- logger│         │- logger     │     │- logger  │    │
│  │- ...   │         │- ...        │     │- ...     │    │
│  └────────┘         └─────────────┘     └──────────┘    │
│                                                            │
│  ↓ (draw)            ↓ (events)        ↓ (callbacks)     │
│  pygame.Surface      bool              None              │
│  ↓                   ↓                  ↓                 │
│  Renderer.screen     Renderer.*()       Renderer._on_*() │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## 6. Макет Экрана (v3dto)

```
┌─────────────────────────────────────────────────────────────────┐
│ (0, 0)                                              (1250, 600) │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────┐  ┌─────────────────┐ │
│  │                                     │  │ VariablesPanel  │ │
│  │          VIEWPORT                   │  │ (275, 35)       │ │
│  │         (5, 5)                      │  │ 700x420         │ │
│  │        1240x500                     │  │ Editable        │ │
│  │                                     │  │ Parameters      │ │
│  │     Shows world map                 │  │                 │ │
│  │     - Grid cells                    │  │                 │ │
│  │     - Creatures (blue)              │  │                 │ │
│  │     - Food (red)                    │  │                 │ │
│  │     - Walls (gray)                  │  │                 │ │
│  │     - Debug rays (if enabled)       │  │                 │ │
│  │                                     │  │                 │ │
│  └─────────────────────────────────────┘  └─────────────────┘ │
│                                                                  │
│  ┌────────────────┐                                             │
│  │ Selected       │                                             │
│  │ Creature       │                                             │
│  │ Panel          │                                             │
│  │ (35, 150)      │                                             │
│  │ 250x300        │                                             │
│  │                │                                             │
│  │ Shows:         │                                             │
│  │ - ID           │                                             │
│  │ - Age          │                                             │
│  │ - Energy       │                                             │
│  │ - Generation   │                                             │
│  │ - Angle/Speed  │                                             │
│  │ - Vision data  │                                             │
│  │                │                                             │
│  └────────────────┘                                             │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ SelectedCreatureHistory / PopulationChart (4, 505)        │  │
│ │ 1243x65                                                    │  │
│ │                                                            │  │
│ │ Shows graph of:                                           │  │
│ │ - Energy history OR Population size                       │  │
│ │ - Event markers (eat, breed)                              │  │
│ │ - Min/Max/Current values                                  │  │
│ │                                                            │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. Обработка События Клавиатуры

```
pygame event (KEYDOWN)
         │
         ↓
Renderer.control_run()
         │
         ↓
Renderer._handle_keyboard(event)
         │
         ├─→ if state == 'main':
         │        └─→ _handle_keyboard_main(event)
         │             │
         │             ├─→ widget1.handle_keydown(event) → bool
         │             ├─→ widget2.handle_keydown(event) → bool
         │             └─→ widget3.handle_keydown(event) → bool
         │
         ├─→ if state == 'popup_simparams':
         │        └─→ _handle_keyboard_popup(event)
         │             │
         │             └─→ variables_panel.handle_keydown(event) → bool
         │
         ├─→ if state == 'creatures_list':
         │        └─→ _handle_keyboard_creatures_list(event)
         │             │
         │             └─→ creatures_list_modal.handle_keydown(event) → bool
         │
         └─→ ... other states ...

Результат:
  ✓ Виджет обработал событие (вернул True)
    ↓
    Прекратить обработку, использовать результат
  
  ✗ Виджет не обработал (вернул False)
    ↓
    Продолжить обработку следующим виджетом
```

---

## 8. Callback Pattern (для интерактивных виджетов)

```
┌─────────────────────────────────────────────────────────┐
│           ИНТЕРАКТИВНЫЙ ВИДЖЕТ                          │
│         (EditableParameterPanel)                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  __init__(self, param_name, initial_value,            │
│           on_parameter_change: Callable):             │
│      self.on_parameter_change = on_parameter_change   │
│      self.param_name = param_name                     │
│      self.value = initial_value                       │
│      self.is_editing = False                          │
│                                                         │
│  handle_keydown(event):                               │
│      if event.key == RETURN and self.is_editing:      │
│          new_value = float(self.input_buffer)         │
│          self.value = new_value                       │
│                                                         │
│          # ← CALLBACK СЮДА                             │
│          self.on_parameter_change(                    │
│              self.param_name,  # "mutation_prob"      │
│              new_value         # 0.5                  │
│          )                                             │
│          self.is_editing = False                      │
│          return True                                   │
│      return False                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│              RENDERER (Callback Handler)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  __init__(world, app):                                │
│      self.edit_panel = EditableParameterPanel(        │
│          "mutation_probability", 0.1,                 │
│          on_parameter_change=self._on_parameter_change│
│      )  ← Передать callback                           │
│                                                         │
│  _on_parameter_change(param_name, value):            │
│      from simparams import sp                         │
│      setattr(sp, param_name, value)                  │
│      print(f"✓ {param_name} = {value}")              │
│                                                         │
│      # ← ПОБОЧНЫЙ ЭФФЕКТ ЗДЕСЬ (в Renderer!)         │
│      if param_name == "food_amount":                  │
│          world.change_food_capacity()                │
│                                                         │
└─────────────────────────────────────────────────────────┘

КЛЮЧЕВАЯ ИДЕЯ:
  Виджет уведомляет об изменении через callback
  Renderer обрабатывает побочные эффекты
  Виджет остаётся ЧИСТЫМ (no side effects)
```

---

## 9. Состояние Виджета (State Management)

```
┌──────────────────────────────────────────────────────┐
│         СОСТОЯНИЕ ВИДЖЕТА (Attributes)              │
│  (сохраняется между frames, НО не в render_state!)  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  class EditablePanel:                               │
│      def __init__(self):                            │
│          # ← СОСТОЯНИЕ ЗДЕСЬ (instance attributes) │
│          self.is_editing = False                    │
│          self.input_buffer = ""                     │
│          self.selected_index = 0                    │
│          self.scroll_offset = 0                     │
│                                                      │
│      def draw(self, screen, render_state):          │
│          # Используй state для отрисовки           │
│          if self.is_editing:                        │
│              bg_color = COLORS['highlight']         │
│          # ...                                       │
│                                                      │
│      def handle_keydown(self, event):               │
│          # Обновляй state на события               │
│          if event.key == K_UP:                      │
│              self.selected_index -= 1 ← Изменить   │
│              return True                            │
│          return False                               │
│                                                      │
│      def handle_mousebuttondown(self, event):       │
│          # Обновляй state на события               │
│          if self.rect.collidepoint(event.pos):     │
│              self.is_editing = not self.is_editing ← Изменить
│              return True                            │
│          return False                               │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ВАЖНО: Состояние виджета (self.*) ≠ RenderStateDTO│
│                                                      │
│  RenderStateDTO:                                    │
│    ├─ Данные от singletons (world, logger, etc.)  │
│    ├─ Одна копия на все виджеты                    │
│    ├─ Читается в draw()                            │
│    ├─ Не модифицируется виджетами                  │
│    └─ Пересоздаётся каждый frame                   │
│                                                      │
│  State Виджета:                                     │
│    ├─ Состояние самого виджета                    │
│    ├─ Персональное для каждого виджета             │
│    ├─ Используется в draw() и handle_*()           │
│    ├─ Модифицируется в handle_*()                  │
│    └─ Сохраняется между frames                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 10. Чек-Лист Архитектурной Проверки

```
┌────────────────────────────────────────────────────────────┐
│  АРХИТЕКТУРНАЯ ПРОВЕРКА (перед коммитом)                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Инициализация (__init__):                                │
│   ☐ Нет параметров сверх простых типов/callback          │
│   ☐ Нет синглтонов (world, logger, debugger, simparams)  │
│   ☐ Есть self.rect и self.surface                        │
│   ☐ Есть self.font с try-except fallback                 │
│   ☐ Есть внутреннее состояние (если нужно)               │
│                                                            │
│ Отрисовка (draw):                                        │
│   ☐ Сигнатура: draw(self, screen, render_state)          │
│   ☐ Использует только render_state для данных            │
│   ☐ Рисует на self.surface (не на screen)                │
│   ☐ Заканчивается screen.blit(self.surface, ...)         │
│   ☐ Нет побочных эффектов (не меняет состояние)          │
│                                                            │
│ События (handle_*):                                      │
│   ☐ Возвращает bool (True если обработано)               │
│   ☐ Обновляет внутреннее состояние при событиях          │
│   ☐ Вызывает callback если нужно (return True)            │
│   ☐ Возвращает False если не обработано                  │
│                                                            │
│ Конфигурация (Class Constants):                          │
│   ☐ WIDGET_X, WIDGET_Y (позиция)                         │
│   ☐ WIDTH, HEIGHT (размер)                               │
│   ☐ COLORS (словарь цветов)                              │
│   ☐ Все прочие размеры как constants                      │
│   ☐ Нет "магических чисел" в коде                        │
│                                                            │
│ Интеграция (Renderer):                                   │
│   ☐ Импортирован в renderer.py                           │
│   ☐ Инициализирован в __init__()                         │
│   ☐ Вызван draw() в нужном _draw_*()                     │
│   ☐ Обработчики событий вызваны в _handle_*()            │
│   ☐ Callback обработан в _on_*() если нужен              │
│                                                            │
│ Тестирование:                                            │
│   ☐ Виджет отображается                                   │
│   ☐ Данные обновляются корректно                          │
│   ☐ События обрабатываются                                │
│   ☐ Нет ошибок в консоли                                  │
│   ☐ Не ломает существующие виджеты                        │
│                                                            │
│ ✅ ЕСЛИ ВСЕ ГАЛОЧКИ - ГОТОВО К КОММИТУ!                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 11. Диаграмма Зависимостей

```
КАТЕГОРИИ КОМПОНЕНТОВ:

┌─────────────────────────────────────────────────────────┐
│ DOMAIN LAYER (Синглтоны)                                │
├─────────────────────────────────────────────────────────┤
│  world  ←→  logger                                      │
│    ↕         ↕                                           │
│  debugger ←→ simparams                                  │
│                                                         │
│ Характеристики:                                         │
│ ✓ Полная власть друг над другом                        │
│ ✓ Сложные циклические зависимости                      │
│ ✓ Часто изменяют состояние друг друга                  │
│ ✓ НЕ ВИДНЫ виджетам!                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│ DTO FACTORY (Renderer)                                  │
├─────────────────────────────────────────────────────────┤
│  Читает: world, logger, debugger, simparams             │
│  Пишет: DTO объекты (чистые данные)                    │
│                                                         │
│ Характеристики:                                         │
│ ✓ Единственный компонент с доступом к синглтонам      │
│ ✓ Преобразует сложное в простое (DTO)                  │
│ ✓ Обрабатывает побочные эффекты (callbacks)            │
│ ✓ Координирует все виджеты                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER (Виджеты)                            │
├─────────────────────────────────────────────────────────┤
│  Читают: RenderStateDTO (только данные!)                │
│  Не видят: world, logger, debugger, simparams          │
│                                                         │
│ Характеристики:                                         │
│ ✗ НЕТ циклических зависимостей                         │
│ ✗ НЕТ побочных эффектов (pure UI)                      │
│ ✗ НЕТ синглтонов                                       │
│ ✓ Полностью тестируемы (мокируем DTO)                  │
│ ✓ Независимы друг от друга                             │
│ ✓ Переиспользуемы в других контекстах                  │
│                                                         │
└─────────────────────────────────────────────────────────┘

ЗАВИСИМОСТИ:
  Domain → DTO ← Widgets
          (однонаправленные!)

РЕЗУЛЬТАТ:
  ✅ Слабая связанность
  ✅ Легко тестировать
  ✅ Легко менять
  ✅ Явные контракты
```

---

**Версия:** 1.0  
**Дата:** 2026-01-18  
**Архитектура:** v3dto (DTO-based isolation)
