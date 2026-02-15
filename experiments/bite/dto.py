# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class BiteExperimentDTO:
    creature_id: int
    is_running: bool
    current_stage: int
    stage_run_counter: int
    # summary: dict  # результаты stats.get_summary()
    random_value: float  # для демонстрации изменения состояния в каждой стадии