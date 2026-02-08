# -*- coding: utf-8 -*-
"""
DummyExperimentDTO - Data Transfer Object для Dummy Experiment.

Описывает объект данных, который используется для передачи информации о состоянии эксперимента в виджет.
Декоратор @dataclass используется для автоматической генерации методов __init__, __repr__, __eq__ и других,
что упрощает создание и использование DTO. То есть под капотом это просто класс с обычными полями экземпляра,
но декоратор прячет от нас эту стуруктуру.

Специфичен для Dummy Experiment и содержит только необходимые поля для отображения 
конкретно этого эксперимента.
Позволяет изолировать widget от данных мира и логики эксперимента, обеспечивая чистую архитектуру.
"""

from dataclasses import dataclass


@dataclass
class DummyExperimentDTO:
    """Data Transfer Object для Dummy Experiment.
    
    Содержит минимальный набор данных для визуализации эксперимента Dummy.
    """
    creature_id: int
    experiment_type: str = 'dummy'
    is_running: bool = False
    tick_counter: int = 0
