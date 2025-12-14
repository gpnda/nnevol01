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

### 4. **Rendering Architecture** (Refactoring in Progress)

#### **Renderer** (`renderer.py`) - Main Coordinator
- **Role**: Manages pygame window, event handling, component coordination
- **Responsibilities**:
  - Initialize pygame, screen, clock
  - Handle keyboard (Space=toggle_run, A=toggle_animate, R=reset_camera)
  - Handle mouse events (delegation to Viewport)
  - Coordinate drawing of all visual components
  - Call `viewport.draw()` each frame
- **Key methods**:
  - `control_run()`: main event loop (returns True to quit)
  - `draw()`: orchestrates all component drawing
  - `_handle_keyboard()`, `_handle_mouse()`: event routing

#### **Viewport** (`gui_viewport.py`) - Map Visualization
- **Role**: Camera system for viewing the world map
- **Features**:
  - Pan: left-mouse drag
  - Zoom: mouse wheel (constrained between `CAMERA_SCALE_MIN=7` and `MAX=50`)
  - Reset: R key
  - Debug info: scale, offset, visible cell count
- **Coordinate Systems** (critical):
  - `screen_to_map(screen_pos)`: converts screen pixel → world cell coordinates
  - `map_to_viewport(map_pos)`: converts world cell → viewport surface pixel
  - `get_visible_range()`: returns (min_x, max_x, min_y, max_y) of visible cells
- **Initialization**: requires `world` object for cell access

#### **Future GUI Components** (Planned)
- `VariablesPanel` / `BIOSStyleGUI`: status display (see `!OLD_gui.py` for reference)
- Will be initialized in `Renderer.__init__()` with TODO comments marking insertion points

## Critical Data Flows

### Simulation Update Cycle (per frame):
```
Application.run():
  if is_running:
    world.update()           # All creatures decide/move
    world.update_map()       # Rebuild visual map from dynamic positions
  if animate_flag:
    renderer.draw()          # Render map + GUI components
  renderer.control_run()     # Process input events
```

### Rendering Pipeline:
```
Renderer.draw():
  Clear screen (black background)
  → Viewport.draw(screen, font)
      ├─ Clear viewport surface
      ├─ _draw_cells()          # Iterate visible range, render grid squares
      ├─ Blit viewport to screen at (VIEWPORT_X, VIEWPORT_Y)
      ├─ Draw border rect
      └─ _draw_debug_info()     # Camera scale, offset, cell count
  → [TODO: GUI components draw here]
  flip display
```

### Coordinate System (Important!):
- **World**: (0,0) at top-left, cells are 1×1 units
- **Viewport screen rect**: (210, 5) to (910, 505)
- **Viewport surface**: local (0,0) to (700, 500)
- **Camera offset**: world cell position at top-left of viewport
- **Camera scale**: pixels per world cell (7-50)

## Design Patterns & Conventions

### 1. **Refactoring Strategy - Incremental Component Extraction**
- Current: `Renderer` is main coordinator, `Viewport` is isolated map viewer
- Future: Add GUI panels (`VariablesPanel`, `FunctionKeysPanel`) as separate modules
- **Philosophy**: Keep each component focused, coordinate via `Renderer`
- **TODO markers**: Look for `# TODO:` comments in renderer.py for integration points

### 2. **Configuration via Class Constants**
- All layout/sizing defined as `SCREEN_WIDTH`, `VIEWPORT_X`, `CAMERA_SCALE_MIN`, etc.
- Colors in `COLORS` dictionary (keys: 'bg', 'border', 'wall', 'food', 'creature')
- This makes layout adjustments trivial (no magic numbers scattered in code)

### 3. **World Map Structure**
- **cell values**: 0=empty, 1=wall, 2=food, 3=creature
- Always check `if cell_value == 0: continue` to skip empty cells (optimization)
- `walls_map` is read-only after generation, never modified during simulation

### 4. **Event Handling Hierarchy**
- `Application`: decides which components update/render
- `Renderer.control_run()`: dispatches keyboard/mouse events
- `Viewport.handle_mouse_*()`: handles pan/zoom independently
- **Pattern**: avoid monolithic event handler, delegate to components

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

- [ ] Extract GUI panels (`VariablesPanel`, `FunctionKeysPanel`) with proper module structure
- [ ] Add configuration file for world parameters (width, height, creature count, mutation rates)
- [ ] Consider making `Viewport` a full component that handles its own rendering (less delegation to Renderer)
- [ ] Performance: optimize `_draw_cells()` with spatial indexing (grid sectors) if scaling to large maps
- [ ] Add more visualization layers (selection box, creature rays, energy heatmap)
