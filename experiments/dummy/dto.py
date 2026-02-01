# -*- coding: utf-8 -*-
"""
DummyExperimentDTO - Data Transfer Object для Dummy Experiment.

Передает данные эксперимента в widget без доступа к основным синглтонам.
"""

from dataclasses import dataclass


@dataclass
class DummyExperimentDTO:
    """Data Transfer Object для Dummy Experiment.
    
    Содержит минимальный набор данных для визуализации эксперимента.
    """
    creature_id: int
    experiment_type: str = 'dummy'
    is_running: bool = False
    tick_counter: int = 0
    start_energy: float = None
    max_energy: float = None
    min_energy: float = None
