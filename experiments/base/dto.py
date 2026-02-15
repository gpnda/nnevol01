# -*- coding: utf-8 -*-
"""Base DTOs для экспериментов."""

from dataclasses import dataclass
import numpy as np


@dataclass
class ExperimentWorldStateDTO:
    """Data Transfer Object для состояния мира.
    
    Содержит снимок состояния мира (map, creatures, foods) в момент времени.
    Используется для отрисовки viewport и других виджетов.
    """
    map: np.ndarray  # numpy array [height, width] с значениями: 0=пусто, 1=стена, 2=еда, 3=существо
    width: int
    height: int
