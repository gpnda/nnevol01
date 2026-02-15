# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Dict, Any

from experiments.base.dto import ExperimentWorldStateDTO


@dataclass
class BiteExperimentDTO:
    creature_id: int
    is_running: bool
    current_stage: int
    stage_run_counter: int
    num_runs_this_stage: int
    world: ExperimentWorldStateDTO
    summary: Optional[Dict[str, Any]] = None  # результаты stats.get_summary()