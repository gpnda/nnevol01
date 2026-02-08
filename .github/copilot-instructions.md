# AI Agent Instructions - Evolutionary Simulation

## Project Overview

This is a **neural network-based evolutionary simulation** written in Python with Pygame visualization. Creatures with artificial neural networks compete, eat food, and reproduce in a 2D grid-based world. The architecture is actively being refactored toward clean separation of concerns.

## Core Architecture

### 1. **Application Layer** (`application.py`)
- **Single entry point**: `Application` class manages the main loop
- Controls simulation state: `is_running` (toggle with Space), `animate_flag` (toggle with A)
- Coordinates: `world.update()` → `world.update_map()` → `renderer.draw()` → `renderer.control_run()`
- Key methods: `toggle_run()`, `toggle_animate()`, `terminate()`

### 2. **World Simulation** (`world.py`, `world_generator.py`)
- **World**: Grid-based 2D map (width × height) containing creatures, food, walls
  - `map`: current visible state (numpy array) - values: 0=empty, 1=wall, 2=food, 3=creature
  - `walls_map`: static terrain layer (never changes after generation)
  - `creatures[]`: list of living Creature objects
  - `foods[]`: list of Food objects
- **Key methods**:
  - `update_map()`: rebuilds visual map from creatures/food positions (called before each frame)
  - `get_cell(x,y)`, `set_cell(x,y,value)`: direct map access
  - `update()`: main simulation tick for all creatures (perception, decision, movement, reproduction)

### 3. **Creature AI** (`creature.py`, `nn/my_handmade_ff.py`)
- **Creature**: Individual agent with neural network brain
  - Properties: `x, y` (position), `angle` (rotation), `energy`, `age`, `speed`
  - `nn`: NeuralNetwork instance (custom feedforward network with mutation)
  - `vision_distance`: raycast range (~20 cells)
  - `birth_ages[]`: reproduction trigger points
- **Reproduction**: `reprodCreature()` creates 3 babies via deepcopy + mutation of parent NN
- **Update cycle** (in `world.update()`):
  1. Perception: raycast vision → collect local cell data
  2. Decision: NN processes perception → outputs (movement, rotation, bite)
  3. Energy costs: base metabolism, movement, rotation
  4. Aging & reproduction check

### 4. **Rendering Architecture** (v3dto - DTO Isolation Pattern)

#### **DTO System** (`renderer/v3dto/dto.py`) - Data Layer
- **Purpose**: Complete isolation of widgets from domain logic
- **Key DTOs**:
  - `CreatureDTO`: creature data (id, x, y, angle, energy, age, speed, generation)
  - `WorldStateDTO`: map snapshot (map array, creatures[], foods[], tick)
  - `CreatureHistoryDTO`: creature energy history + events
  - `DebugDataDTO`: debug visualization data (raycast_dots, visions)
  - `SimulationParamsDTO`: all simulation parameters
  - `RenderStateDTO`: complete render context (world, selected_creature, debug, params)
- **Benefits**: Widgets have zero knowledge of World, Logger, Debugger

#### **Renderer** (`renderer/v3dto/renderer.py`) - Main Coordinator
- **Role**: Pygame manager + DTO factory + state machine
- **Responsibilities**:
  - Initialize pygame window and clock
  - Manage state machine (main, popup_simparams, creatures_list, logs)
  - Handle keyboard/mouse events and state transitions
  - Transform domain objects → DTOs (world→WorldStateDTO, logger→HistoryDTO)
  - Coordinate all widget drawing via RenderStateDTO
  - Handle parameter changes from VariablesPanel via callbacks
- **Key methods**:
  - `control_run()`: main event loop + state dispatcher
  - `draw()`: orchestrates widget drawing via RenderStateDTO
  - `set_state(state_name)`: state machine transitions
  - `_prepare_*_dto()`: DTO factory methods
  - `_on_parameter_change(param, value)`: callback handler for VariablesPanel

#### **Viewport** (`renderer/v3dto/gui_viewport.py`) - Map Visualization
- **Role**: Camera system + grid renderer (fully isolated via DTO)
- **Features**:
  - Pan: left-mouse drag
  - Zoom: mouse wheel (CAMERA_SCALE_MIN=7, MAX=50)
  - Reset: R key (camera to default)
  - Receives data exclusively via RenderStateDTO
- **Key methods**:
  - `draw(screen, render_state, font)`: render map + debug overlay
  - `screen_to_map(screen_pos)`: screen pixel → world cell
  - `map_to_viewport(map_pos)`: world cell → viewport pixel
  - `get_visible_range()`: visible cells (min_x, max_x, min_y, max_y)
  - `handle_mouse_drag/wheel()`: camera control
- **Design**: Zero dependency on world, logger, debugger (all data via RenderStateDTO)

#### **SelectedCreaturePanel** (`renderer/v3dto/gui_selected_creature.py`)
- **Role**: Display selected creature information (stateless widget)
- **Features**: Shows ID, age, energy, generation, angle, speed, vision data
- **Design**: Pure presentation, receives CreatureDTO from RenderStateDTO
- **Key method**: `draw(screen, render_state)` → extracts creature from state

#### **SelectedCreatureHistory** (`renderer/v3dto/gui_selected_creature_history.py`)
- **Role**: Timeline graph of creature energy + events
- **Features**: Energy history line, event markers (EAT_FOOD, CREATE_CHILD)
- **Design**: Receives CreatureHistoryDTO from RenderStateDTO
- **Key method**: `draw(screen, render_state)` → renders graph + events

#### **VariablesPanel** (`renderer/v3dto/gui_variablespanel.py`)
- **Role**: Interactive parameter editor (stateful widget)
- **Features**: Edit mutation_probability, food_amount, reproduction_ages, energy_cost_*, etc.
- **Communication**: Bidirectional via callback `on_parameter_change(param_name, value)`
- **Design**: Manages own state (editing, selected_index, input_buffer)
- **Key method**: `draw(screen)` → renders panel, calls callback on parameter change
- **Important**: Callback → Renderer._on_parameter_change() → applies changes to world/SimParams

## Critical Data Flows

### Simulation Update Cycle (per frame):
```
Application.run():
  if is_running:
    world.update()           # All creatures decide/move
    world.update_map()       # Rebuild visual map from dynamic positions
  if animate_flag:
    renderer.draw()          # Render via DTO system
      ├─ Prepare WorldStateDTO from world
      ├─ Prepare CreatureHistoryDTO from logger
      ├─ Prepare DebugDataDTO from debugger
      └─ Assemble RenderStateDTO
  renderer.control_run()     # Process input events + state machine
```

### Rendering Pipeline (v3dto - DTO Based):
```
Renderer.draw():
  1. PREPARE DTOs
     ├─ world → WorldStateDTO (creatures[], foods[], map)
     ├─ logger → CreatureHistoryDTO (energy history, events)
     ├─ debugger → DebugDataDTO (raycast, visions)
     └─ simparams → SimulationParamsDTO (all params)
     
  2. CREATE RenderStateDTO
     └─ RenderStateDTO(world=world_dto, selected_creature=..., debug=...)
     
  3. RENDER WIDGETS (all receive RenderStateDTO)
     ├─ viewport.draw(screen, render_state, font)
     ├─ selected_creature_panel.draw(screen, render_state)
     ├─ selected_creature_history.draw(screen, render_state)
     └─ variables_panel.draw(screen)  # Callback-based
     
  4. DISPLAY
     └─ pygame.display.flip()
```

### Widget Isolation Architecture:
```
Renderer
  ├─ Has: world, logger, debugger, simparams (singletons)
  └─ Converts to: RenderStateDTO (data only)
       ↓
    Widgets
      ├─ Have: RenderStateDTO (data)
      ├─ Zero knowledge of: world, logger, debugger, simparams
      └─ Fully testable in isolation (can mock RenderStateDTO)
```

## Design Patterns & Conventions

### 1. **Refactoring Strategy - DTO Isolation Pattern**
- **Current state**: v3dto renderer with complete DTO isolation
- **Architecture**: Domain objects (world, logger, debugger) → DTO → Widgets
- **Philosophy**: 
  - Each widget is fully isolated (zero knowledge of singletons)
  - Renderer is the only component touching singletons
  - All data flows through strongly-typed DTOs
  - Widgets are fully testable in isolation (mock RenderStateDTO)
- **Benefits**:
  - ✓ Loose coupling between presentation and domain
  - ✓ Widgets can be reused in different contexts
  - ✓ Easy to add new widgets (follow pattern)
  - ✓ Full test coverage without singletons

### 2. **Configuration via Class Constants** (v3dto Widget Pattern)
- **Every widget defines**:
  - Geometry: `WIDGET_X`, `WIDGET_Y`, `WIDTH`, `HEIGHT`
  - Font: `FONT_SIZE`, `FONT_PATH` with safe try-except fallback
  - Colors: `COLORS = {'background': (...), 'border': (...), 'text': (...)}`
- **Benefits**: Zero magic numbers, easy layout adjustments, consistent widget styling
- **All 4 widgets follow this pattern** (96.5% similarity):
  - Viewport, SelectedCreaturePanel, SelectedCreatureHistory, VariablesPanel
- **Example**:
  ```python
  class MyWidget:
      WIDGET_X = 10
      WIDGET_Y = 10
      WIDTH = 200
      HEIGHT = 100
      FONT_SIZE = 14
      COLORS = {'background': (20,20,20), 'text': (200,200,200)}
      
      def __init__(self):
          self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, self.WIDTH, self.HEIGHT)
          self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
          try:
              self.font = pygame.font.Font('./tests/Ac437_Siemens_PC-D.ttf', self.FONT_SIZE)
          except:
              self.font = pygame.font.Font(None, self.FONT_SIZE)
  ```

### 3. **World Map Structure**
- **cell values**: 0=empty, 1=wall, 2=food, 3=creature
- Always check `if cell_value == 0: continue` to skip empty cells (optimization)
- `walls_map` is read-only after generation, never modified during simulation

### 4. **Event Handling & State Management**
- **State Machine**: Renderer manages application states
  - `main`: normal simulation + widgets
  - `popup_simparams`: modal parameter window (pauses simulation)
  - `creatures_list`: modal creatures list (pauses simulation)
  - `logs`: modal logs window (pauses simulation)
- **Event Flow**:
  - `Renderer.control_run()`: pygame event dispatcher + state transitions
  - `Viewport.handle_mouse_drag/wheel()`: camera pan/zoom (reads events internally)
  - `VariablesPanel.handle_keydown()`: parameter editing
  - Modal windows: handle their own keyboard/mouse within modal state
- **Callback Pattern** (unique to VariablesPanel):
  - VariablesPanel calls callback: `on_parameter_change(param_name, value)`
  - Renderer handles: `_on_parameter_change()` applies changes to world/SimParams
  - Prevents circular dependencies (widgets never directly touch singletons)

## Development Workflow

### Running the Simulation:
```bash
python nnevol.py
```
Keyboard shortcuts:
- **Space**: Pause/resume simulation
- **A**: Toggle animation (rendering)
- **R**: Reset camera to default position
- **Mouse drag**: Pan map
- **Mouse wheel**: Zoom in/out

### Adding New Features:
1. **New visual component** (e.g., info panel):
   - Create new file `gui_component.py` with your class
   - Add initialization in `Renderer.__init__()`
   - Add drawing in `Renderer.draw()` (look for TODO comments)
   - Add event handling in `Renderer._handle_keyboard/mouse()` if needed

2. **Modify Viewport** (camera, rendering):
   - Edit `gui_viewport.py` constants first (geometry, colors)
   - Keep world→viewport coordinate conversion methods clean
   - Always call `screen_to_map()` and `map_to_viewport()` for consistency

3. **Modify Creature AI**:
   - Change `creature.update()` for decision logic
   - Modify `nn/my_handmade_ff.py` for NN architecture
   - Remember: NN outputs drive (movement, rotation, bite) - 3 actions

4. **Debug**:
   - Use `debugger.py` singleton: `from debugger import debug; debug.set("key", value)`
   - Viewport shows scale/offset/visible_range automatically
   - Check `world.map` directly for verification: `world.map[y, x]`

## Dependencies & Environment

- **Python 3.9+**
- **Core**: numpy (2.2.6), pygame (2.6.1), numba (0.62.1)
- **Font**: './tests/Ac437_Siemens_PC-D.ttf' (will fallback to system font if missing)
- **NN backend**: Switchable between `nn/my_handmade_ff.py` (current) or `nn/nn_torch_rnn.py` (commented in `creature.py`)

## Key Files Reference

| File | Purpose | Key Classes |
|------|---------|------------|
| `nnevol.py` | Entry point | - |
| `application.py` | Main loop controller | `Application` |
| `world.py` | Simulation grid + state | `World` |
| `world_generator.py` | Map generation | `WorldGenerator` |
| `creature.py` | Individual AI agent | `Creature` |
| `renderer.py` | Pygame coordinator | `Renderer` |
| `gui_viewport.py` | Map camera & view | `Viewport` |
| `debugger.py` | Singleton debug utility | `Debugger` |
| `food.py` | Food objects | `Food` |
| `nn/my_handmade_ff.py` | Neural network | `NeuralNetwork` |

## Common Pitfalls & Solutions

1. **Viewport not updating**: Remember `world.update_map()` must be called after `world.update()`
2. **Mouse coordinates wrong**: Use `viewport.screen_to_map()`, not raw event.pos
3. **Rendering off-screen**: Check `get_visible_range()` respects world bounds (min/max clamping)
4. **Camera math**: Camera offset + scale system expects world cells, not pixels; use constants for layout changes
5. **Creature stuck**: Check `world.update()` in creature loop - may need world bounds checks

## Future Refactoring Notes

- [x] Extract GUI panels (`Viewport`, `SelectedCreaturePanel`, `SelectedCreatureHistory`, `VariablesPanel`) - **DONE** (v3dto)
- [x] Implement DTO isolation system - **DONE**
- [x] Implement state machine for modal windows - **DONE**
- [x] Implement callback pattern for parameter changes - **DONE**
 pattern
- [ ] Add configuration file for world parameters (width, height, creature count, mutation rates)
- [ ] Consider making modal windows full components with their own state management
- [ ] Performance: optimize `_draw_cells()` with spatial indexing (grid sectors) if scaling to large maps
- [ ] Add more visualization layers (selection box, creature rays, energy heatmap)

## Widget Development Guide

When adding a new widget to v3dto renderer, follow this pattern:

```python
# -*- coding: utf-8 -*-
"""Widget description and v3dto isolation note."""
import pygame
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from renderer.v3dto.dto import RenderStateDTO

class NewWidget:
    # 1. Configuration Constants
    WIDGET_X, WIDGET_Y = 10, 10
    WIDTH, HEIGHT = 200, 100
    FONT_SIZE = 14
    FONT_PATH = './tests/Ac437_Siemens_PC-D.ttf'
    COLORS = {'background': (20,20,20), 'text': (200,200,200)}
    
    # 2. Initialization (zero params or callback only)
    def __init__(self):
        self.rect = pygame.Rect(self.WIDGET_X, self.WIDGET_Y, self.WIDTH, self.HEIGHT)
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        try:
            self.font = pygame.font.Font(self.FONT_PATH, self.FONT_SIZE)
        except:
            self.font = pygame.font.Font(None, self.FONT_SIZE)
    
    # 3. Drawing (receives RenderStateDTO)
    def draw(self, screen: pygame.Surface, render_state: 'RenderStateDTO') -> None:
        self.surface.fill(self.COLORS['background'])
        # ... use render_state data, never import world/logger/debugger ...
        screen.blit(self.surface, (self.rect.x, self.rect.y))

# In Renderer.__init__():
#   self.new_widget = NewWidget()
# In Renderer.draw():
#   self.new_widget.draw(self.screen, render_state)
```
