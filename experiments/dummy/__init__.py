# -*- coding: utf-8 -*-
"""
Dummy Experiment - простой базовый эксперимент для тестирования системы.

Содержит:
- experiment.py: Логика dummy эксперимента
- widget.py: Визуальный интерфейс (v3dto изолированный)
"""

from experiments.dummy.experiment import DummyExperiment
from experiments.dummy.widget import DummyExperimentWidget

__all__ = ['DummyExperiment', 'DummyExperimentWidget']
