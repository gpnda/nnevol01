# -*- coding: utf-8 -*-
"""
Система экспериментов - архитектура на основе модулей.

Структура:
- base/: Абстрактные классы и интерфейсы
- dummy/: Dummy эксперимент (логика + виджет)
- [другие]/: Будущие эксперименты

Registry:
- Каждый эксперимент регистрируется в EXPERIMENTS
- Renderer использует EXPERIMENTS для загрузки виджетов
- Application использует EXPERIMENTS для загрузки логики
"""

from experiments.base import ExperimentBase
from experiments.bite.experiment import BiteExperiment
from experiments.bite.widget import BiteExperimentWidget
from experiments.dummy import DummyExperiment, DummyExperimentWidget
# from experiments.spambite import SpambiteExperiment, SpambiteExperimentWidget

# Registry экспериментов
# При добавлении нового эксперимента просто добавьте запись в этот словарь
EXPERIMENTS = {
    'dummy': {
        'experiment_class': DummyExperiment,
        'widget_class': DummyExperimentWidget,
        'name': 'Dummy Experiment',
        'description': 'Dummy for all future experiments',
    },
    'bite': {
        'experiment_class': BiteExperiment,
        'widget_class': BiteExperimentWidget,
        'name': 'BiteExperiment',
        'description': 'Test creature behavior on finding food with success/failure tracking',
    },
    # 'spambite': {
    #     'experiment_class': SpambiteExperiment,
    #     'widget_class': SpambiteExperimentWidget,
    #     'name': 'SpambiteExperiment',
    #     'description': 'Test creature behavior on finding food with success/failure tracking',
    # },
    # Добавляйте новые эксперименты сюда:
    # 'advanced': {
    #     'experiment_class': AdvancedExperiment,
    #     'widget_class': AdvancedExperimentWidget,
    #     'name': 'Advanced Experiment',
    #     'description': 'Описание',
    # },
}

__all__ = [
    'ExperimentBase',
    'DummyExperiment',
    'DummyExperimentWidget',
    # 'SpambiteExperiment',
    # 'SpambiteExperimentWidget',
    'EXPERIMENTS',
    'BiteExperiment',
    'BiteExperimentWidget',
]