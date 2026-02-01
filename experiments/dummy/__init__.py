# -*- coding: utf-8 -*-
"""
Dummy Experiment - простой базовый эксперимент для тестирования системы.

Содержит:
- experiment.py: Логика dummy эксперимента
- widget.py: Визуальный интерфейс (v3dto изолированный)
- dto.py: Data Transfer Object для передачи данных в widget
"""

from experiments.dummy.experiment import DummyExperiment
from experiments.dummy.widget import DummyExperimentWidget
from experiments.dummy.dto import DummyExperimentDTO

__all__ = ['DummyExperiment', 'DummyExperimentWidget', 'DummyExperimentDTO']
