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
from experiments.spambite.dto import SpambiteExperimentDTO

__all__ = [
    'SpambiteExperiment',
    'SpambiteExperimentWidget',
    'SpambiteExperimentDTO',
]
