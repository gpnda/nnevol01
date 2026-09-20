# -*- coding: utf-8 -*-
"""World persistence service - сохранение и загрузка состояния мира через JSON.GZ"""

import json
import gzip
import re
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import numpy as np
from simparams import sp
from datetime import datetime


@dataclass
class LoadedSnapshot:
    """Нейтральный носитель данных загрузки: не знает про World, готов к применению."""
    metadata: dict
    walls_map: np.ndarray
    zones_arr: Optional[np.ndarray]
    creatures: list
    foods: list
    simparams: dict = field(default_factory=dict)


class WorldPersistenceService:
    """Singleton для сохранения/загрузки мира в JSON.GZ формате"""
    
    _instance = None
    SAVES_DIR = Path("./saves")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.SAVES_DIR.mkdir(exist_ok=True)
        self._initialized = True
    
    def save_world(self, world, filename: str) -> bool:
        """
        Сохраняет мир в JSON.GZ файл
        
        Args:
            world: World объект
            filename: Имя файла (без расширения)
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Вычисляем метаинформацию
            max_generation = max(
                (c.generation for c in world.creatures),
                default=0
            )
            created_at = datetime.now().isoformat()

            # Определяем итоговое имя файла (с encoded-суффиксом, без коллизий)
            stem = self._resolve_save_stem(filename, world)
            save_path = self.SAVES_DIR / f"{stem}.world.gz"

            # Подготавливаем данные о мире
            world_data = {
                'metadata': {
                    'width': world.width,
                    'height': world.height,
                    'tick': world.tick,
                    'creatures_count': len(world.creatures),
                    'max_generation': int(max_generation),
                    'created_at': created_at,
                },
                'walls_map': world.walls_map.tolist(),
                'zones_map': world.zones_map.zones_map.tolist(),
                'creatures': self._serialize_creatures(world.creatures),
                'foods': self._serialize_foods(world.foods),
                'simparams': self._serialize_simparams(),
            }
            
            # Преобразуем в JSON и сжимаем
            json_str = json.dumps(world_data, indent=2)
            json_bytes = json_str.encode('utf-8')
            compressed_data = gzip.compress(json_bytes, compresslevel=9)
            
            # Сохраняем в файл
            with open(save_path, 'wb') as f:
                f.write(compressed_data)
            
            file_size_kb = save_path.stat().st_size / 1024
            creatures_count = len(world.creatures)
            foods_count = len(world.foods)
            
            print(f"✓ Мир сохранен: {save_path}")
            print(f"  Существ: {creatures_count}, Еды: {foods_count}, Размер: {file_size_kb:.1f} KB")
            return True
            
        except Exception as e:
            print(f"✗ Ошибка при сохранении мира: {e}")
            return False
    
    def load_world(self, world, filename: str) -> bool:
        """
        Загружает состояние мира из JSON.GZ файла (полная замена world).

        Атомарность входа: если чтение файла или сборка snapshot падает —
        world не тронут вообще. Мутация world происходит только в apply_full_load,
        когда snapshot уже полностью провалидирован.

        Args:
            world: World объект для применения загруженных данных
            filename: Имя файла (без расширения)

        Returns:
            True если успешно, False если ошибка
        """
        try:
            world_data = self._read_save_file(filename)
        except FileNotFoundError as e:
            print(f"✗ {e}")
            return False
        except Exception as e:
            print(f"✗ Ошибка при загрузке мира: {e}")
            return False

        try:
            snapshot = self.build_snapshot(world_data)
        except Exception as e:
            print(f"✗ Ошибка при загрузке мира: {e}")
            return False

        try:
            self.apply_full_load(world, snapshot)
        except Exception as e:
            print(f"✗ Ошибка при применении загруженного мира: {e}")
            return False

        print(f"✓ Мир загружен: {filename}")
        print(f"  Существ: {len(world.creatures)}, Еды: {len(world.foods)}, Тик: {world.tick}")
        return True

    def load_creatures_only(self, world, filename: str) -> bool:
        """
        Загружает из сохранения только существ и добавляет их в текущий мир.

        Отличия от load_world():
        - не меняет размеры мира, walls_map, zones_map, foods, tick, simparams
        - каждому загруженному существу назначает новый уникальный id
        - размещает существ на случайных свободных клетках текущего мира
        """
        try:
            world_data = self._read_save_file(filename)
        except FileNotFoundError as e:
            print(f"✗ {e}")
            return False
        except Exception as e:
            print(f"✗ Ошибка при загрузке существ из мира: {e}")
            return False

        try:
            snapshot = self.build_snapshot(world_data)
        except Exception as e:
            print(f"✗ Ошибка при загрузке существ из мира: {e}")
            return False

        try:
            added_count, requested_count = self.apply_creatures_only(world, snapshot)
        except Exception as e:
            print(f"✗ Ошибка при применении загруженных существ: {e}")
            return False

        skipped_count = requested_count - added_count
        print(f"✓ Существа загружены из {filename}")
        print(
            f"  Запрошено: {requested_count}, Добавлено: {added_count}, "
            f"Пропущено (нет места): {skipped_count}"
        )
        return True

    # ============================================================================
    # LAYER A — I/O (файл → dict, ничего не знает про World)
    # ============================================================================

    def _read_save_file(self, filename: str) -> dict:
        """Читает, распаковывает и парсит файл сохранения. Не трогает world."""
        load_path = self.SAVES_DIR / f"{filename}.world.gz"

        if not load_path.exists():
            raise FileNotFoundError(f"Файл не найден: {load_path}")

        with open(load_path, 'rb') as f:
            compressed_data = f.read()

        json_bytes = gzip.decompress(compressed_data)
        json_str = json_bytes.decode('utf-8')
        return json.loads(json_str)

    # ============================================================================
    # LAYER B — Десериализация (чистая, dict → LoadedSnapshot, без мутации world)
    # ============================================================================

    def build_snapshot(self, world_data: dict) -> 'LoadedSnapshot':
        """
        Собирает LoadedSnapshot из сырых данных файла с полной валидацией.

        Вся проверка форм/типов (shape mismatch, несовместимый NN backend)
        происходит здесь — apply_* получает уже гарантированно консистентный snapshot.
        """
        metadata = dict(world_data['metadata'])
        height = metadata['height']
        width = metadata['width']

        walls_map = np.array(world_data['walls_map'], dtype='int')
        if walls_map.shape != (height, width):
            raise ValueError(
                f"walls_map shape {walls_map.shape} не соответствует размерам мира ({height}, {width})"
            )

        zones_arr = None
        if 'zones_map' in world_data:
            zones_arr = np.array(world_data['zones_map'], dtype='int')
            if zones_arr.shape != (height, width):
                raise ValueError(
                    f"zones_map shape {zones_arr.shape} не соответствует размерам мира ({height}, {width})"
                )

        creatures = self._deserialize_creatures(world_data['creatures'])
        foods = self._deserialize_foods(world_data['foods'])
        simparams = dict(world_data.get('simparams', {}))

        return LoadedSnapshot(
            metadata=metadata,
            walls_map=walls_map,
            zones_arr=zones_arr,
            creatures=creatures,
            foods=foods,
            simparams=simparams,
        )

    # ============================================================================
    # LAYER C — Политики применения (мутируют world из уже валидного snapshot)
    # ============================================================================

    def apply_full_load(self, world, snapshot: 'LoadedSnapshot') -> None:
        """Полная замена состояния world данными из snapshot."""
        from creature import Creature

        height = snapshot.metadata['height']
        width = snapshot.metadata['width']

        world.width = width
        world.height = height
        world.tick = snapshot.metadata['tick']
        world.map = np.zeros((height, width), dtype='int')
        world.walls_map = snapshot.walls_map

        if snapshot.zones_arr is not None:
            world.zones_map.width = width
            world.zones_map.height = height
            world.zones_map.zones_map = snapshot.zones_arr
            world.zones_map._build_pixel_caches()

        world.creatures = snapshot.creatures
        world.foods = snapshot.foods
        if snapshot.creatures:
            Creature._id_counter = max(c.id for c in snapshot.creatures)

        if snapshot.simparams:
            self._restore_simparams(snapshot.simparams)

        world.update_map()
        if world.map.shape != (height, width):
            raise ValueError(f"Ошибка после update_map: map shape {world.map.shape} != ({height}, {width})")

    def _place_creatures_on_free_cells(self, world, creatures: list) -> tuple:
        """Размещает список существ на свободные клетки карты мира.
        
        Переопределяет id каждому существу, обновляет x/y.
        Обновляет Creature._id_counter и вызывает world.update_map().
        
        Args:
            world: World объект
            creatures: List of Creature объектов для размещения
        
        Returns:
            (added_count, requested_count)
        """
        from creature import Creature

        requested_count = len(creatures)

        existing_creature_positions = {
            (int(c.x), int(c.y))
            for c in world.creatures
        }
        existing_food_positions = {
            (int(f.x), int(f.y))
            for f in world.foods
        }

        free_cells = []
        for y in range(world.height):
            for x in range(world.width):
                if world.walls_map[y, x] == 1:
                    continue
                if (x, y) in existing_creature_positions:
                    continue
                if (x, y) in existing_food_positions:
                    continue
                free_cells.append((x, y))

        random.shuffle(free_cells)

        existing_max_id = max((c.id for c in world.creatures), default=0)
        next_id = max(existing_max_id, Creature._id_counter)

        added_count = 0
        for creature in creatures:
            if not free_cells:
                break

            x, y = free_cells.pop()
            next_id += 1

            creature.id = next_id
            creature.x = x
            creature.y = y
            world.creatures.append(creature)
            added_count += 1

        Creature._id_counter = max(Creature._id_counter, next_id)
        world.update_map()

        return added_count, requested_count
    
    def apply_creatures_only(self, world, snapshot: 'LoadedSnapshot') -> tuple:
        """Добавляет существ из snapshot в текущий world, переназначая id.

        Returns:
            (added_count, requested_count)
        """
        loaded_creatures = snapshot.creatures
        return self._place_creatures_on_free_cells(world, loaded_creatures)
    
    def transfer_population_to_world(self, world, snapshot: 'LoadedSnapshot') -> tuple:
        """Переносит текущую популяцию на карту из snapshot (вариант Б).
        
        Алгоритм:
        1. Сохраняет текущих существ
        2. Загружает карту/стены/еду/параметры (apply_full_load создаёт существ из snapshot)
        3. Очищает существ из snapshot (нам нужна ТОЛЬКО карта)
        4. Расселяет ТЕКУЩИХ существ на новой карте
        
        Returns:
            (added_count, requested_count)
        """
        old_creatures = list(world.creatures)  # Копируем список текущих существ
        requested_count = len(old_creatures)
        
        # Применяем новый мир (стены, еда, параметры симуляции)
        self.apply_full_load(world, snapshot)
        
        # Очищаем creatures из snapshot — нам нужна ТОЛЬКО карта, существа из snapshot игнорируются
        world.creatures = []
        
        # Расселяем старых существ на новой карте
        added_count, _ = self._place_creatures_on_free_cells(world, old_creatures)
        
        return added_count, requested_count
    
    def _serialize_creatures(self, creatures) -> list:
        """Конвертирует creatures в сохраняемый формат (list of dicts)"""
        data = []
        for creature in creatures:
            creature_data = {
                'id': int(creature.id),
                'generation': int(creature.generation),
                'x': float(creature.x),
                'y': float(creature.y),
                'energy': float(creature.energy),
                'health': float(creature.health),
                'age': int(creature.age),
                'speed': int(creature.speed),
                'angle': float(creature.angle),
                'bite_effort': float(creature.bite_effort),
                'vision_distance': int(creature.vision_distance),
                'bite_range': float(creature.bite_range),
                'birth_ages': [int(age) for age in creature.birth_ages],
                'input_hurting': float(creature.input_hurting),
                'input_starving': float(creature.input_starving),
                'input_wayblocked': float(creature.input_wayblocked),
                'input_bite_success': float(creature.input_bite_success),
                'nn': self._serialize_nn(creature.nn),
            }
            data.append(creature_data)
        return data
    
    def _serialize_nn(self, nn) -> dict:
        """Конвертирует NeuralNetwork в сохраняемый формат"""
        return nn.serialize()
    
    def _serialize_foods(self, foods) -> list:
        """Конвертирует foods в сохраняемый формат"""
        data = []
        for food in foods:
            food_data = {
                'x': int(food.x),
                'y': int(food.y),
                'nutrition': float(food.nutrition),
                'food_age': int(food.food_age),
            }
            data.append(food_data)
        return data
    
    def _serialize_simparams(self) -> dict:
        """Сохраняет текущие параметры симуляции для справки"""
        params = {}
        for attr in dir(sp):
            if not attr.startswith('_') and attr[0].islower():
                value = getattr(sp, attr)
                if not callable(value):
                    try:
                        # Пытаемся сериализовать значение
                        json.dumps(value)
                        params[attr] = value
                    except (TypeError, ValueError):
                        # Пропускаем несериализуемые значения
                        pass
        return params
    
    def _restore_simparams(self, saved_params: dict) -> None:
        """
        Восстанавливает параметры симуляции из сохраненных данных.
        
        Логика:
        - Проходит по всем сохраненным параметрам
        - Для каждого параметра проверяет, существует ли он в текущей SimParams
        - Применяет значение, если параметр найден
        - Учитывает особые параметры (например, reproduction_ages - это строка)
        
        Args:
            saved_params: dict с сохраненными параметрами из JSON
        """
        restored_count = 0
        skipped_count = 0
        
        for param_name, param_value in saved_params.items():
            if hasattr(sp, param_name):
                try:
                    setattr(sp, param_name, param_value)
                    restored_count += 1
                except Exception as e:
                    print(f"⚠ Не удалось восстановить параметр '{param_name}': {e}")
                    skipped_count += 1
            else:
                skipped_count += 1
        
        print(f"✓ Параметры симуляции восстановлены: {restored_count} параметров")
        if skipped_count > 0:
            print(f"  (пропущено {skipped_count} неизвестных параметров)")
    
    def _deserialize_creatures(self, creature_data_list) -> list:
        """Восстанавливает creatures из сохранённых данных (чистая функция, id не трогает счётчик)"""
        from creature import Creature
        from nn import NeuralNetwork
        
        creatures = []
        for creature_data in creature_data_list:
            # Создаём базовое существо
            creature = Creature(creature_data['x'], creature_data['y'])
            
            # Восстанавливаем все атрибуты
            creature.id = creature_data['id']
            creature.generation = creature_data['generation']
            creature.energy = creature_data['energy']
            creature.health = creature_data['health']
            creature.age = creature_data['age']
            creature.speed = creature_data['speed']
            creature.angle = creature_data['angle']
            creature.bite_effort = creature_data['bite_effort']
            creature.vision_distance = creature_data['vision_distance']
            creature.bite_range = creature_data['bite_range']
            creature.birth_ages = creature_data['birth_ages']
            creature.input_hurting = creature_data['input_hurting']
            creature.input_starving = creature_data['input_starving']
            creature.input_wayblocked = creature_data['input_wayblocked']
            creature.input_bite_success = creature_data['input_bite_success']
            
            # Восстанавливаем веса нейросети
            # Если десериализация прошла с ошибкой - перешагнем это существо
            try:
                creature.nn = self._deserialize_nn(creature_data['nn'])
            except Exception as e:
                print(f"Ошибка при восстановлении нейросети существа с ID {creature.id}: {e}")
                continue
            
            creatures.append(creature)

        return creatures
    
    def _deserialize_nn(self, nn_data):
        """Восстанавливает NeuralNetwork из сохранённых данных"""
        from nn import NeuralNetwork, NN_BACKEND
        saved_type = nn_data.get('__type__')
        if saved_type is not None and saved_type != NN_BACKEND:
            raise ValueError(
                f"Несовместимый тип нейросети: сохранялка создана с '{saved_type}', "
                f"а сейчас активен '{NN_BACKEND}'. "
                f"Измени NN_BACKEND в nn/__init__.py на '{saved_type}' и перезапусти."
            )
        nn = NeuralNetwork()
        nn.deserialize(nn_data)
        return nn
    
    def _deserialize_foods(self, food_data_list) -> list:
        """Восстанавливает foods из сохранённых данных"""
        from food import Food
        
        foods = []
        for food_data in food_data_list:
            food = Food(food_data['x'], food_data['y'])
            food.nutrition = food_data['nutrition']
            food.food_age = food_data['food_age']
            foods.append(food)
        
        return foods

    # ============================================================================
    # FILENAME ENCODING HELPERS
    # ============================================================================

    @staticmethod
    def _build_encoded_stem(base: str, world) -> str:
        """Возвращает stem вида 'base__c{N}_g{G}_{W}x{H}'."""
        max_gen = max((c.generation for c in world.creatures), default=0)
        return f"{base}__c{len(world.creatures)}_g{int(max_gen)}_{world.width}x{world.height}"

    def _resolve_save_stem(self, base: str, world) -> str:
        """
        Возвращает stem без расширения, не конфликтующий с существующими файлами.
        Если 'base__*.world.gz' уже существует, пробует 'base01__...', 'base02__...' и т.д.
        """
        stem = self._build_encoded_stem(base, world)
        if not list(self.SAVES_DIR.glob(f"{base}__*.world.gz")):
            return stem
        for i in range(1, 100):
            candidate_base = f"{base}{i:02d}"
            if not list(self.SAVES_DIR.glob(f"{candidate_base}__*.world.gz")):
                return self._build_encoded_stem(candidate_base, world)
        # крайний случай — перезаписываем base99
        return self._build_encoded_stem(f"{base}99", world)

    @staticmethod
    def _parse_filename_metadata(stem: str):
        """
        Парсит stem файла и извлекает закодированные метаданные.

        Ожидаемый формат: 'name__c{N}_g{G}_{W}x{H}'

        Returns:
            (display_name, creatures_count, max_generation, map_w, map_h)
            Если формат не распознан — (stem, None, None, None, None)
        """
        m = re.search(r'^(.+)__c(\d+)_g(\d+)_(\d+)x(\d+)$', stem)
        if m:
            return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        return stem, None, None, None, None

    # ============================================================================

    def get_save_slots(self) -> list:
        """
        Получить список слотов сохранения из папки ./saves.

        Метаданные читаются ТОЛЬКО из имени файла и stat() файловой системы —
        без распаковки архивов.

        Returns:
            Список dict:
            [{
                'filename': 'foo__c450_g125_512x256',  # полный stem для load_world()
                'name':     'foo',                      # чистое имя для отображения
                'modified_at': '2026-04-09 14:30',
                'creatures_count': 450,   # int или None
                'max_generation':  125,   # int или None
                'map_size': '512x256',    # str или 'N/A'
                'file_size_kb': 45.3,
            }, ...]
        """
        slots = []

        if not self.SAVES_DIR.exists():
            return slots

        try:
            for file_path in sorted(self.SAVES_DIR.glob('*.world.gz')):
                stem = file_path.name[:-9]  # убираем '.world.gz'
                display_name, creatures_count, max_gen, map_w, map_h = \
                    self._parse_filename_metadata(stem)

                stat = file_path.stat()
                modified_at = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                map_size = f"{map_w}x{map_h}" if map_w is not None else 'N/A'

                slots.append({
                    'filename': stem,
                    'name': display_name,
                    'modified_at': modified_at,
                    'creatures_count': creatures_count,
                    'max_generation': max_gen,
                    'map_size': map_size,
                    'file_size_kb': round(stat.st_size / 1024, 1),
                })
        except Exception as e:
            print(f"✗ Ошибка при сканировании папки сохранений: {e}")

        return slots
        
# Singleton instance
world_persistence = WorldPersistenceService()
