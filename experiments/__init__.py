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
from experiments.dummy import DummyExperiment, DummyExperimentWidget

# Registry экспериментов
# При добавлении нового эксперимента просто добавьте запись в этот словарь
EXPERIMENTS = {
    'dummy': {
        'experiment_class': DummyExperiment,
        'widget_class': DummyExperimentWidget,
        'name': 'Dummy Experiment',
        'description': 'Наблюдение за одним существом',
    },
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
    'EXPERIMENTS',
]
