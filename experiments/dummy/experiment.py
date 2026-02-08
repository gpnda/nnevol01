# -*- coding: utf-8 -*-
"""
Dummy Experiment - простой базовый минимальный пример эксперимента.
Основа для всех будущих экспериментов, которые будут строиться на этой же архитектуре.

Назначение:
- Демонстрация архитектуры эксперимента с полной изоляцией данных через DTO
- Логика не знает про визуализацию. Визуализация не знает про логику. 
  Все данные из логики для визуализации передаются через DTO.
- Логика эксперимента: вывод в виджет эксперимента: id существа и счетчика тиков
"""

from experiments.base import ExperimentBase
from experiments.dummy.dto import DummyExperimentDTO


class DummyExperiment(ExperimentBase):
    """
    Базовый шаблон эксперимент.
    
    Логика:
    - Выбирается одно существо target_creature_id, его id выводится в окне
    - бизнес логика: каждый тик инкрементирует счетчик тиков
    - данные для отрисовки виджета эксперимента передаются через DummyExperimentDTO,
    - который содержит ID существа, статус (запущен/остановлен) и счетчик тиков.
    - конструктор эксперимента получает на вход ID существа и объект world для 
      доступа к данным мира. В конструкторе можно извлечь из world все необходимые данные о существе 
      и сохранить их в аттрибутах объекта эксперимента для дальнейшего использования 
      в логике эксперимента. Конструктор эксперимента вызываемый при создании экземпляра эксперимента, 
      - это единственное место, где эксперимент имеет доступ к данным мира. 
      Дальше эксперимент работает только с сохраненными данными, не имея больше доступа к app и world.

    """
    
    def __init__(self, target_creature_id: int, world :object):
        """
        Инициализация dummy эксперимента.
        
        Args:
            target_creature_id: ID существа для наблюдения
            world: Объект World из основного мира
        
        Raises:
            ValueError: Если существо с заданным ID не найдено
        """
        
        # Тут единственное место, когда эксперимент получает возможность получить данные из основного мира - через конструктор.
        # Все что потребуется для эксперимента следует забрать из world и сохранить в виде аттрибутов объекта experiment, 
        # чтобы дальше эксперимент работал только с этими данными.
        # В данном случае мы просто сохраняем X и Y координаты существа, а также его начальную энергию. 
        # В других экспериментах может потребоваться больше данных, например, список соседних существ,
        # рядом расположенной пищи, список последних действий существ и так далее
        
        self.creature_id = target_creature_id
        self.exapmle_creature_x = world.get_creature_by_id(target_creature_id).x
        self.exapmle_creature_y = world.get_creature_by_id(target_creature_id).y

        # Тут аттрибуты эксперимента, каждый эксперимент может иметь свои аттрибуты для хранения данных, 
        # которые ему нужны для логики эксперимента. В данном случае это просто счетчик тиков и статус 
        # запущен/остановлен,
        self.tick_counter = 0
        self.is_running = False
        
        print(f"[EXPERIMENT] Dummy experiment initialized")
        print(f"  Target creature: {target_creature_id}")
    
    def start(self) -> None:
        """Запустить эксперимент."""
        self.is_running = True
        self.tick_counter = 0
        print(f"[EXPERIMENT] Starting dummy experiment on creature {self.creature_id}")
    
    def stop(self) -> None:
        """Остановить эксперимент."""
        self.is_running = False
        print(f"[EXPERIMENT] Stopping dummy experiment")
        self._print_stats()
    
    def update(self) -> None:
        """
        Основной метод обновления эксперимента.
        
        Вызывается каждый фрейм из application.run() если experiment_mode == True.
        Здесь должна быть основная логика эксперимента.
        """
        if not self.is_running:
            return
        
        self.tick_counter += 1
        
    
    def _print_stats(self) -> None:
        """Вывести статистику эксперимента."""
        print(f"[EXPERIMENT] Dummy experiment stats:")
        print(f"  Total ticks: {self.tick_counter}")
        print(f"  Target creature: {self.creature_id}")
        print(f"  Status: {'COMPLETED' if self.tick_counter > 0 else 'NOT STARTED'}")
    
    def get_experiment_dto(self) -> DummyExperimentDTO:
        """
        Получить DTO эксперимента для передачи в виджет.
        Класс experiment поддерживает этот метод для того, чтобы через него передавать данные в 
        виджет эксперимента, при этом полностью изолируя виджет от данных мира и логики эксперимента.
        Этот метод вызывается из renderer.py чтобы получить данные для визуализации в виджете эксперимента.
             Нет ли здесь утечки памяти? Ведь мы каждый раз какбы создает новый инстанс DummyExperimentDTO, не будет ли это проблемой?
             На самом деле нет, так как Python использует сборщик мусора для управления памятью, 
             и объекты, которые больше не используются, автоматически удаляются из памяти.
        Returns:
            DummyExperimentDTO: Данные для визуализации в widget
        """
        return DummyExperimentDTO(
            creature_id=self.creature_id,
            is_running=self.is_running,
            tick_counter=self.tick_counter,
        )