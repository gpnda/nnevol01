# -*- coding: utf-8 -*-
"""
SpambiteExperiment - эксперимент на пищу (Spambite).

Структура:
- experiment.py: SpambiteExperiment логика
- widget.py: SpambiteExperimentWidget визуализация
- dto.py: SpambiteExperimentDTO передача данных
"""

from experiments.spambite.experiment import SpambiteExperiment
from experiments.spambite.widget import SpambiteExperimentWidget

__all__ = [
    'SpambiteExperiment',
    'SpambiteExperimentWidget',
]
