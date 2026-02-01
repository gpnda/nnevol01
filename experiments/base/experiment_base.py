# -*- coding: utf-8 -*-
"""
Абстрактный базовый класс для всех экспериментов.

Все конкретные эксперименты должны наследоваться от ExperimentBase
и реализовать обязательные методы.
"""

from abc import ABC, abstractmethod


class ExperimentBase(ABC):
    """
    Абстрактный базовый класс для экспериментов.
    
    Определяет интерфейс, который должны реализовать все конкретные эксперименты.
    """
    
    @abstractmethod
    def start(self) -> None:
        """
        Запустить эксперимент.
        
        Вызывается один раз при инициализации эксперимента.
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Остановить эксперимент.
        
        Вызывается при завершении эксперимента.
        """
        pass
    
    @abstractmethod
    def update(self) -> None:
        """
        Основной метод обновления эксперимента.
        
        Вызывается каждый фрейм из application.run() если experiment_mode == True.
        Здесь должна быть логика сбора статистики и мониторинга.
        """
        pass
    
    @abstractmethod
    def get_dto(self) -> object:
        """
        Получить собственный DTO этого эксперимента.
        
        Каждый эксперимент определяет свой собственный DTO для передачи данных в widget.
        Например, SpambiteExperiment возвращает SpambiteExperimentDTO.
        
        Returns:
            object: Собственный DTO эксперимента (SpambiteExperimentDTO, и т.д.)
        """
        pass
