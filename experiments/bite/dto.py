# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from experiments.base.dto import ExperimentWorldStateDTO, ExperimentCreatureStateDTO


@dataclass
class BiteExperimentDTO:
    """DTO для BiteExperiment - максимальная изоляция виджета от логики.
    
    Содержит все необходимые данные для отрисовки эксперимента:
    - world: тестовый мир (карта)
    - creature_state: состояние существа (vision_input, nn_outputs, raycast_dots, позиция, угол)
    
    Виджет остается полностью изолирован и не имеет доступа к основной логике.
    """
    creature_id: int
    is_running: bool
    current_stage: int
    stage_run_counter: int
    num_runs_this_stage: int
    world: ExperimentWorldStateDTO
    
    # Состояние существа для визуализации - через DTO для полной изоляции
    creature_state: Optional[ExperimentCreatureStateDTO] = None
    
    summary: Optional[Dict[str, Any]] = None  # результаты stats.get_summary()