# -*- coding: utf-8 -*-
"""DTO для визуализации эксперимента с норками."""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from experiments.base.dto import ExperimentCreatureStateDTO, ExperimentWorldStateDTO


@dataclass
class BurrowExperimentDTO:
    creature_id: int
    is_running: bool
    current_stage: int
    stage_run_counter: int
    world: ExperimentWorldStateDTO
    burrow_mask: np.ndarray
    creature_state: Optional[ExperimentCreatureStateDTO]
    outcomes: dict[str, int]
    total_runs: int
    ticks_in_run: int
    entry_tick: Optional[int]
    burrow_stay_ticks: int
    current_run_outcome: Optional[str]
    awaiting_parameter_selection: bool
