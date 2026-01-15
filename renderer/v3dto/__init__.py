# -*- coding: utf-8 -*-
"""
Renderer v3dto - версия с полной изоляцией данных через Data Transfer Objects (DTO).

Основная философия:
- Renderer получает данные из world, logger, debugger, но НЕ пробрасывает их виджетам
- Вместо этого преобразует данные в специальные DTO (Data Transfer Objects)
- Виджеты работают только с DTO и полностью отделены от источников данных
- Это позволяет полностью тестировать виджеты, не создавая реальные объекты world и т.д.

Структура v3dto:
- dto.py: Определения всех DTO классов
- renderer.py: Главный Renderer с factory методами для создания DTO
- gui_viewport.py: Viewport (еще не переписан для DTO) - TODO
- gui_variablespanel.py: VariablesPanel (еще не переписан для DTO) - TODO
- gui_selected_creature.py: SelectedCreaturePanel (еще не переписан для DTO) - TODO
- gui_selected_creature_history.py: SelectedCreatureHistory (еще не переписан для DTO) - TODO

Использование в application.py:
    from renderer.v3dto.renderer import Renderer
    renderer = Renderer(world, app)
"""

from renderer.v3dto.dto import (
    CreatureDTO,
    WorldStateDTO,
    FoodDTO,
    CreatureEventDTO,
    CreatureHistoryDTO,
    DebugDataDTO,
    SimulationParamsDTO,
    SelectedCreaturePanelDTO,
    RenderStateDTO,
)

from renderer.v3dto.renderer import Renderer

__all__ = [
    'Renderer',
    'CreatureDTO',
    'WorldStateDTO',
    'FoodDTO',
    'CreatureEventDTO',
    'CreatureHistoryDTO',
    'DebugDataDTO',
    'SimulationParamsDTO',
    'SelectedCreaturePanelDTO',
    'RenderStateDTO',
]
