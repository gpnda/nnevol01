# -*- coding: utf-8 -*-
"""Base DTOs для экспериментов."""

from dataclasses import dataclass
import numpy as np
from typing import Tuple



@dataclass
class ExperimentWorldStateDTO:
    """Data Transfer Object для состояния мира.
    
    Содержит снимок состояния мира (map, creatures, foods) в момент времени.
    Используется для отрисовки viewport и других виджетов.
    """
    map: np.ndarray  # numpy array [height, width] с значениями: 0=пусто, 1=стена, 2=еда, 3=существо
    width: int
    height: int

@dataclass
class ExperimentCreatureStateDTO:
    x: float
    y: float
    angle: float
    vision_input: np.ndarray  # [45] - входной вектор зрения (3 луча × 15 элементов)
    nn_outputs: Tuple[float, float, float]  # (angle_delta, speed_delta, bite_output)
    raycast_dots: np.ndarray  # [[x1, y1], [x2, y2], ...] - координаты точек луча