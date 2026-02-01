# -*- coding: utf-8 -*-
"""
SpambiteExperiment - эксперимент наблюдения за поиском пищи.

Назначение:
- Создать изолированный мир 50x50 с одним существом и одной пищей
- Отслеживать успешные попытки (укусы пищи) и неудачи (потеря пищи из виду)
- Провести 20 итераций тестирования поведения существа
- Вывести итоговую статистику успехов/неудач
"""

from experiments.base import ExperimentBase
from experiments.spambite.dto import SpambiteExperimentDTO
from renderer.v3dto.dto import CreatureDTO
import random
import math
from creature import Creature
from food import Food
from world_generator import WorldGenerator


class SpambiteExperiment(ExperimentBase):
    """
    Эксперимент для тестирования поведения существа при поиске пищи.
    
    Логика:
    - Целевое существо копируется в изолированный мир 50x50
    - В каждой итерации спавнится одна пища
    - Существо пытается найти и съесть пищу
    - Успех: существо кусает пищу
    - Неудача: существо теряет пищу из виду или достигнут лимит кадров
    - 20 итераций максимум
    """
    
    # ============================================================================
    # Константы конфигурации
    # ============================================================================
    
    # Размер временного мира
    TEMP_WORLD_WIDTH = 50
    TEMP_WORLD_HEIGHT = 50
    
    # Итерации
    MAX_ITERATIONS = 20
    
    # Лимит кадров на одну итерацию
    MAX_FRAMES_PER_ITERATION = 300
    
    # Расстояние, после которого считаем, что существо потеряло пищу из виду
    VISION_DISTANCE = 20
    
    # Энергия для существа в начале итерации
    INITIAL_ENERGY = 1000
    
    # Диапазон спавна пищи (не на краях, где могут быть стены)
    FOOD_SPAWN_MIN = 10
    FOOD_SPAWN_MAX = 40
    
    # ============================================================================
    # Инициализация
    # ============================================================================
    
    def __init__(self, experiment_type: str, target_creature_id: int, creatures_list: list):
        """
        Инициализация SpambiteExperiment.
        
        Args:
            experiment_type: Тип эксперимента (должен быть "spambite")
            target_creature_id: ID целевого существа
            creatures_list: Список всех существ из основного мира
        
        Raises:
            ValueError: Если существо с заданным ID не найдено
        """
        self.experiment_type = experiment_type
        
        # Создать CreatureDTO из target_creature_id через фабричный метод
        self.target_creature_dto = CreatureDTO.from_creature_id(target_creature_id, creatures_list)
        
        # Состояние эксперимента
        self.is_running = False
        self.current_iteration = 0
        self.frames_in_iteration = 0
        
        # Статистика
        self.successes = 0
        self.failures = 0
        
        # Данные мира
        self.temp_world = None
        self.creature = None
        self.current_food = None
        
        print(f"[EXPERIMENT] SpambiteExperiment initialized")
        print(f"  Type: {experiment_type}")
        print(f"  Target creature ID: {target_creature_id}")
        print(f"  Max iterations: {self.MAX_ITERATIONS}")
    
    # ============================================================================
    # ExperimentBase интерфейс
    # ============================================================================
    
    def start(self) -> None:
        """Запустить эксперимент."""
        print(f"[EXPERIMENT] Starting SpambiteExperiment")
        print(f"  Will run {self.MAX_ITERATIONS} iterations")
        print(f"  Vision distance: {self.VISION_DISTANCE} cells")
        print(f"  Max frames per iteration: {self.MAX_FRAMES_PER_ITERATION}")
        
        # 1. Создать существо из DTO
        self._create_creature_from_dto()
        
        # 2. Создать временный мир
        self._create_temp_world()
        
        # 3. Спавнить первую пищу
        self._spawn_food()
        
        # 4. Инициализировать счетчики
        self.is_running = True
        self.current_iteration = 1
        self.frames_in_iteration = 0
        self.successes = 0
        self.failures = 0
        
        print(f"[EXPERIMENT] SpambiteExperiment started successfully")
        print(f"  Creature: ID={self.creature.id}, pos=({self.creature.x}, {self.creature.y})")
        print(f"  Food: pos=({self.current_food.x}, {self.current_food.y})")
        print(f"  World: {self.TEMP_WORLD_WIDTH}x{self.TEMP_WORLD_HEIGHT}")
    
    def stop(self) -> None:
        """
        Остановить эксперимент и вывести результаты.
        
        Этот метод вызывается когда:
        1. Все 20 итераций завершены
        2. Ручной выход из эксперимента (ESC)
        
        Процесс:
        1. Остановить симуляцию (set is_running = False)
        2. Вывести финальную статистику
        3. Очистить все ссылки на объекты (memory cleanup)
        """
        print(f"\n[EXPERIMENT] Stopping SpambiteExperiment...")
        print(f"  Current iteration: {self.current_iteration} / {self.MAX_ITERATIONS}")
        
        self.is_running = False
        self._print_results()
        
        # Очистить все ссылки на объекты для освобождения памяти
        self.temp_world = None
        self.creature = None
        self.current_food = None
        
        print(f"[EXPERIMENT] SpambiteExperiment stopped. Memory cleaned.")
    
    def update(self) -> None:
        """
        Основной метод обновления эксперимента.
        
        Вызывается каждый фрейм из application.run() если experiment_mode == True.
        
        Логика:
        1. Запустить симуляцию временного мира
        2. Проверить успех - пища съедена
        3. Проверить неудачу - существо потеряло пищу из виду
        4. Проверить лимит кадров - достигнут максимум
        5. Управлять итерациями и переходом к следующей или завершению
        """
        if not self.is_running or self.temp_world is None:
            return
        
        # ========== 1. Запустить симуляцию ==========
        self.temp_world.update()  # Все существа двигаются, едят, и т.д.
        self.temp_world.update_map()  # Обновить визуальную карту
        self.frames_in_iteration += 1
        
        # ========== 2. Проверить успех - пища съедена ==========
        if len(self.temp_world.foods) == 0:
            self.successes += 1
            self.current_iteration += 1
            self.frames_in_iteration = 0
            
            # Проверить конец эксперимента
            if self.current_iteration <= self.MAX_ITERATIONS:
                self._spawn_food()  # Спавнить новую пищу
            else:
                self.stop()  # Конец эксперимента
            return
        
        # ========== 3. Проверить неудачу - потеря пищи из виду ==========
        if self.current_food is not None:
            distance = math.sqrt(
                (self.creature.x - self.current_food.x) ** 2 +
                (self.creature.y - self.current_food.y) ** 2
            )
            
            if distance > self.VISION_DISTANCE:
                self.failures += 1
                self.current_iteration += 1
                self.frames_in_iteration = 0
                
                # Проверить конец эксперимента
                if self.current_iteration <= self.MAX_ITERATIONS:
                    self._spawn_food()  # Спавнить новую пищу
                else:
                    self.stop()  # Конец эксперимента
                return
        
        # ========== 4. Проверить лимит кадров ==========
        if self.frames_in_iteration >= self.MAX_FRAMES_PER_ITERATION:
            self.failures += 1
            self.current_iteration += 1
            self.frames_in_iteration = 0
            
            # Проверить конец эксперимента
            if self.current_iteration <= self.MAX_ITERATIONS:
                self._spawn_food()  # Спавнить новую пищу
            else:
                self.stop()  # Конец эксперимента
            return
    

    
    # ============================================================================
    # Внутренние методы
    # ============================================================================
    
    def _create_creature_from_dto(self) -> None:
        """
        Создать новое существо на основе DTO.
        
        Создаем существо с той же NN генерацией (копируем через deepcopy).
        Позиция будет установлена в центр карты.
        """
        # Создать новое существо в центре карты
        self.creature = Creature(
            x=self.TEMP_WORLD_WIDTH // 2,
            y=self.TEMP_WORLD_HEIGHT // 2
        )
        
        # Скопировать параметры из DTO
        # Примечание: Мы копируем только важные параметры из DTO
        self.creature.generation = self.target_creature_dto.generation
        self.creature.energy = self.INITIAL_ENERGY
        self.creature.speed = self.target_creature_dto.speed
        self.creature.vision_distance = self.target_creature_dto.vision_distance
        self.creature.bite_range = self.target_creature_dto.bite_range
        self.creature.bite_effort = self.target_creature_dto.bite_effort
        
        # TODO: Необходимо скопировать NN из оригинального существа
        # Текущий подход: используем новый NN от base Creature
        # Улучшение: передавать NN через DTO или отдельный параметр
    
    def _create_temp_world(self) -> None:
        """
        Создать временный изолированный мир 50x50.
        
        Использует WorldGenerator для создания пустого мира с указанными параметрами.
        """
        # Создать генератор с нужными параметрами
        gen = WorldGenerator()
        
        # Генерировать мир
        # Параметры: ширина, высота, стены, еда, существа
        self.temp_world = gen.generate_world(
            width=self.TEMP_WORLD_WIDTH,
            height=self.TEMP_WORLD_HEIGHT,
            wall_count=50,  # Стены для интересной карты
            food_count=0,   # Без еды, добавим сами
            creatures_count=0  # Без существ, добавим сами
        )
        
        # Добавить наше существо в мир
        self.temp_world.creatures = [self.creature]
    
    def _spawn_food(self) -> None:
        """
        Спавнить одну пищу в случайное место на карте.
        
        Пища спавнится в диапазоне FOOD_SPAWN_MIN-FOOD_SPAWN_MAX,
        чтобы не оказаться на краях карты (где могут быть стены).
        """
        # Генерировать случайные координаты
        while True:
            food_x = random.randint(self.FOOD_SPAWN_MIN, self.FOOD_SPAWN_MAX)
            food_y = random.randint(self.FOOD_SPAWN_MIN, self.FOOD_SPAWN_MAX)
            
            # Проверить, что ячейка пустая (не стена, не существо)
            cell_value = self.temp_world.get_cell(food_x, food_y)
            if cell_value == 0:  # 0 = пусто
                self.current_food = Food(food_x, food_y)
                self.temp_world.foods.append(self.current_food)
                break
    
    def _print_results(self) -> None:
        """
        Вывести итоговые результаты эксперимента.
        
        Выводит:
        - Количество успешных итераций (существо съело пищу)
        - Количество неудачных итераций (потеря пищи или лимит кадров)
        - Процент успешности
        - Интерпретация результатов
        """
        total_tests = self.successes + self.failures
        success_rate = (self.successes / total_tests * 100) if total_tests > 0 else 0
        
        # Определить интерпретацию
        if success_rate >= 80:
            interpretation = "EXCELLENT - существо очень хорошо ищет пищу"
        elif success_rate >= 60:
            interpretation = "GOOD - существо хорошо ищет пищу"
        elif success_rate >= 40:
            interpretation = "MODERATE - существо средне ищет пищу"
        elif success_rate >= 20:
            interpretation = "POOR - существо плохо ищет пищу"
        else:
            interpretation = "VERY POOR - существо почти не ищет пищу"
        
        # Вывести результаты в красивом формате
        print(f"\n{'='*60}")
        print(f"[EXPERIMENT] SpambiteExperiment FINAL RESULTS")
        print(f"{'='*60}")
        print(f"  Target creature ID:     {self.target_creature_dto.id}")
        print(f"  Target creature gen:    {self.target_creature_dto.generation}")
        print(f"  World size:             {self.TEMP_WORLD_WIDTH}x{self.TEMP_WORLD_HEIGHT}")
        print(f"  Vision distance:        {self.VISION_DISTANCE} cells")
        print(f"  Max frames per iter:    {self.MAX_FRAMES_PER_ITERATION}")
        print(f"-" * 60)
        print(f"  Total iterations:       {total_tests} / {self.MAX_ITERATIONS}")
        print(f"  Successes:              {self.successes}")
        print(f"  Failures:               {self.failures}")
        print(f"  Success rate:           {success_rate:.1f}%")
        print(f"-" * 60)
        print(f"  Interpretation:         {interpretation}")
        print(f"{'='*60}\n")
    
    def get_dto(self) -> SpambiteExperimentDTO:
        """
        Получить DTO эксперимента для передачи в виджет.
        
        Returns:
            SpambiteExperimentDTO: Данные для визуализации в widget
        """
        # Подготовить список позиций пищи
        food_positions = []
        if self.current_food is not None:
            food_positions.append((self.current_food.x, self.current_food.y))
        
        # Подготовить DTO мира если мир активен
        world_dto = None
        if self.temp_world is not None:
            from renderer.v3dto.dto import WorldStateDTO, FoodDTO
            creatures_dto = []
            if self.creature is not None:
                creatures_dto.append(
                    self._prepare_creature_dto(self.creature)
                )
            
            foods_dto = [FoodDTO(x=self.current_food.x, y=self.current_food.y, energy=self.current_food.nutrition)]
            
            world_dto = WorldStateDTO(
                map=self.temp_world.map,
                width=self.temp_world.width,
                height=self.temp_world.height,
                creatures=creatures_dto,
                foods=foods_dto,
                tick=self.temp_world.tick,
            )
        
        return SpambiteExperimentDTO(
            world_state=world_dto,
            creature_dto=self.target_creature_dto,
            food_positions=food_positions,
            current_iteration=self.current_iteration,
            total_iterations=self.MAX_ITERATIONS,
            successes=self.successes,
            failures=self.failures,
            frames_in_iteration=self.frames_in_iteration,
            debug_message=f"Iteration {self.current_iteration}/{self.MAX_ITERATIONS}",
        )
    
    # def get_dto(self) -> SpambiteExperimentDTO:
    #     """
    #     Получить DTO для передачи данных в виджет.
        
    #     Преобразует текущее состояние эксперимента в DTO для отрисовки.
        
    #     Returns:
    #         SpambiteExperimentDTO с данными текущего состояния
    #     """
    #     if self.temp_world is None or self.creature is None:
    #         # Если мир не инициализирован, вернуть пустой DTO
    #         return SpambiteExperimentDTO(
    #             world_state=None,
    #             creature_dto=None,
    #             food_positions=[],
    #             current_iteration=self.current_iteration,
    #             total_iterations=self.MAX_ITERATIONS,
    #             successes=self.successes,
    #             failures=self.failures,
    #             frames_in_iteration=self.frames_in_iteration,
    #         )
        
    #     # Преобразовать temp_world в WorldStateDTO
    #     from renderer.v3dto.dto import CreatureDTO, FoodDTO, WorldStateDTO
        
    #     # Создать WorldStateDTO из temp_world
    #     creatures_dto = []
    #     for c in self.temp_world.creatures:
    #         creature_dto = CreatureDTO(
    #             id=c.id,
    #             x=c.x,
    #             y=c.y,
    #             angle=c.angle,
    #             energy=c.energy,
    #             age=c.age,
    #             speed=c.speed,
    #             generation=c.generation,
    #             bite_effort=c.bite_effort,
    #             vision_distance=c.vision_distance,
    #             bite_range=c.bite_range,
    #         )
    #         creatures_dto.append(creature_dto)
        
    #     foods_dto = []
    #     for f in self.temp_world.foods:
    #         food_dto = FoodDTO(
    #             x=f.x,
    #             y=f.y,
    #             energy=f.nutrition,
    #         )
    #         foods_dto.append(food_dto)
        
    #     world_state_dto = WorldStateDTO(
    #         map=self.temp_world.map.copy(),
    #         width=self.temp_world.width,
    #         height=self.temp_world.height,
    #         creatures=creatures_dto,
    #         foods=foods_dto,
    #         tick=0,  # TODO: если нужно отслеживать тики эксперимента
    #     )
        
    #     # Создать CreatureDTO для целевого существа
    #     creature_dto = CreatureDTO(
    #         id=self.creature.id,
    #         x=self.creature.x,
    #         y=self.creature.y,
    #         angle=self.creature.angle,
    #         energy=self.creature.energy,
    #         age=self.creature.age,
    #         speed=self.creature.speed,
    #         generation=self.creature.generation,
    #         bite_effort=self.creature.bite_effort,
    #         vision_distance=self.creature.vision_distance,
    #         bite_range=self.creature.bite_range,
    #     )
        
    #     return SpambiteExperimentDTO(
    #         world_state=world_state_dto,
    #         creature_dto=creature_dto,
    #         food_positions=[(f.x, f.y) for f in self.temp_world.foods],
    #         current_iteration=self.current_iteration,
    #         total_iterations=self.MAX_ITERATIONS,
    #         successes=self.successes,
    #         failures=self.failures,
    #         frames_in_iteration=self.frames_in_iteration,
    #     )
    
    def _prepare_creature_dto(self, creature):
        """Вспомогательный метод для преобразования Creature в CreatureDTO."""
        from renderer.v3dto.dto import CreatureDTO
        return CreatureDTO(
            id=creature.id,
            x=creature.x,
            y=creature.y,
            angle=creature.angle,
            energy=creature.energy,
            age=creature.age,
            speed=creature.speed,
            generation=creature.generation,
            bite_effort=creature.bite_effort,
            vision_distance=creature.vision_distance,
            bite_range=creature.bite_range,
        )
