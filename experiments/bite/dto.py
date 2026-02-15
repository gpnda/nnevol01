# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np

from experiments.base.dto import ExperimentWorldStateDTO


@dataclass
class BiteExperimentDTO:
    """DTO для BiteExperiment - максимальная изоляция виджета от логики.
    
    Содержит все необходимые данные для отрисовки эксперимента:
    - world: тестовый мир (карта)
    - vision_input: входной вектор зрения (45 элементов)
    - nn_outputs: выходы нейросетки (3 значения: angle, speed, bite)
    - raycast_dots: координаты точек raycast для отрисовки лучей
    
    Виджет остается полностью изолирован и не имеет доступа к основной логике.
    """
    creature_id: int
    is_running: bool
    current_stage: int
    stage_run_counter: int
    num_runs_this_stage: int
    world: ExperimentWorldStateDTO
    
    # Новые поля для визуализации - все через DTO для изоляции
    vision_input: Optional[np.ndarray] = None  # [45] входной вектор зрения
    nn_outputs: Optional[Tuple[float, float, float]] = None  # (angle_delta, speed_delta, bite_output)
    raycast_dots: Optional[np.ndarray] = None  # [(x, y), ...] координаты raycast точек
    
    summary: Optional[Dict[str, Any]] = None  # результаты stats.get_summary()