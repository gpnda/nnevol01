# -*- coding: utf-8 -*-
"""World persistence service - сохранение и загрузка состояния мира через JSON.GZ"""

import json
import gzip
from pathlib import Path
from typing import Optional
import numpy as np
from simparams import sp
from datetime import datetime


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
            save_path = self.SAVES_DIR / f"{filename}.world.gz"
            
            # Вычисляем метаинформацию для сохранения
            max_generation = max(
                (c.generation for c in world.creatures),
                default=0
            )
            created_at = datetime.now().isoformat()

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
        Загружает состояние мира из JSON.GZ файла
        
        Args:
            world: World объект для применения загруженных данных
            filename: Имя файла (без расширения)
            
        Returns:
            True если успешно, False если ошибка
        """
        try:
            load_path = self.SAVES_DIR / f"{filename}.world.gz"
            
            if not load_path.exists():
                print(f"✗ Файл не найден: {load_path}")
                return False
            
            # Читаем и распаковываем файл
            with open(load_path, 'rb') as f:
                compressed_data = f.read()
            
            json_bytes = gzip.decompress(compressed_data)
            json_str = json_bytes.decode('utf-8')
            world_data = json.loads(json_str)
            
            # Применяем загруженные данные в world
            world.width = world_data['metadata']['width']
            world.height = world_data['metadata']['height']
            world.tick = world_data['metadata']['tick']
            
            world.walls_map = np.array(world_data['walls_map'], dtype='int')
            world.creatures = self._deserialize_creatures(world_data['creatures'])
            world.foods = self._deserialize_foods(world_data['foods'])
            
            # Восстанавливаем параметры симуляции (если они сохранены)
            if 'simparams' in world_data:
                self._restore_simparams(world_data['simparams'])
            
            # Пересчитываем карту после загрузки
            world.update_map()
            
            creatures_count = len(world.creatures)
            foods_count = len(world.foods)
            
            print(f"✓ Мир загружен: {load_path}")
            print(f"  Существ: {creatures_count}, Еды: {foods_count}, Тик: {world.tick}")
            return True
            
        except Exception as e:
            print(f"✗ Ошибка при загрузке мира: {e}")
            return False
    
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
                'age': int(creature.age),
                'speed': int(creature.speed),
                'angle': float(creature.angle),
                'bite_effort': float(creature.bite_effort),
                'vision_distance': int(creature.vision_distance),
                'bite_range': float(creature.bite_range),
                'birth_ages': [int(age) for age in creature.birth_ages],
                'nn': self._serialize_nn(creature.nn),
            }
            data.append(creature_data)
        return data
    
    def _serialize_nn(self, nn) -> dict:
        """Конвертирует NeuralNetwork в сохраняемый формат"""
        nn_data = {
            'w1': nn.w1.tolist(),
            'b1': nn.b1.tolist(),
            'w2': nn.w2.tolist(),
            'b2': nn.b2.tolist(),
            'w3': nn.w3.tolist(),
            'b3': nn.b3.tolist(),
        }
        return nn_data
    
    def _serialize_foods(self, foods) -> list:
        """Конвертирует foods в сохраняемый формат"""
        data = []
        for food in foods:
            food_data = {
                'x': int(food.x),
                'y': int(food.y),
                'nutrition': float(food.nutrition),
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
        """Восстанавливает creatures из сохранённых данных"""
        from creature import Creature
        from nn.my_handmade_ff import NeuralNetwork
        
        creatures = []
        for creature_data in creature_data_list:
            # Создаём базовое существо
            creature = Creature(creature_data['x'], creature_data['y'])
            
            # Восстанавливаем все атрибуты
            creature.id = creature_data['id']
            creature.generation = creature_data['generation']
            creature.energy = creature_data['energy']
            creature.age = creature_data['age']
            creature.speed = creature_data['speed']
            creature.angle = creature_data['angle']
            creature.bite_effort = creature_data['bite_effort']
            creature.vision_distance = creature_data['vision_distance']
            creature.bite_range = creature_data['bite_range']
            creature.birth_ages = creature_data['birth_ages']
            
            # Восстанавливаем веса нейросети
            creature.nn = self._deserialize_nn(creature_data['nn'])
            
            creatures.append(creature)
        
        # Обновляем счётчик ID для новых существ
        if creatures:
            Creature._id_counter = max(c.id for c in creatures)
        
        return creatures
    
    def _deserialize_nn(self, nn_data) -> 'NeuralNetwork':
        """Восстанавливает NeuralNetwork из сохранённых данных"""
        from nn.my_handmade_ff import NeuralNetwork
        
        nn = NeuralNetwork()
        nn.w1 = np.array(nn_data['w1'], dtype=np.float32)
        nn.b1 = np.array(nn_data['b1'], dtype=np.float32)
        nn.w2 = np.array(nn_data['w2'], dtype=np.float32)
        nn.b2 = np.array(nn_data['b2'], dtype=np.float32)
        nn.w3 = np.array(nn_data['w3'], dtype=np.float32)
        nn.b3 = np.array(nn_data['b3'], dtype=np.float32)
        
        return nn
    
    def _deserialize_foods(self, food_data_list) -> list:
        """Восстанавливает foods из сохранённых данных"""
        from food import Food
        
        foods = []
        for food_data in food_data_list:
            food = Food(food_data['x'], food_data['y'])
            food.nutrition = food_data['nutrition']
            foods.append(food)
        
        return foods



    def get_save_slots(self) -> list:
        """
        Получить список слотов сохранения из папки ./saves
        
        Returns:
            Список dict с информацией о каждом слоте:
            [{
                'name': 'test',
                'created_at': '2024-12-15T12:30:00',
                'creatures_count': 450,
                'max_generation': 125,
                'tick': 5234,
                'file_size_kb': 45.3,
            }, ...]
        """
        slots = []
        
        if not self.SAVES_DIR.exists():
            return slots
        
        try:
            # Сканируем все .world.gz файлы в папке
            for file_path in sorted(self.SAVES_DIR.glob('*.world.gz')):
                slot_info = self._extract_slot_info_from_file(file_path)
                if slot_info is not None:
                    slots.append(slot_info)
        except Exception as e:
            print(f"✗ Ошибка при сканировании папки сохранений: {e}")
        
        return slots

    def _extract_slot_info_from_file(self, file_path: Path) -> Optional[dict]:
        """
        Извлечь информацию о слоте из файла сохранения
        
        Args:
            file_path: Path к файлу .world.gz
            
        Returns:
            dict с информацией о слоте или None если ошибка
        """
        try:
            # Читаем и распаковываем файл
            with open(file_path, 'rb') as f:
                compressed_data = f.read()
            
            json_bytes = gzip.decompress(compressed_data)
            json_str = json_bytes.decode('utf-8')
            world_data = json.loads(json_str)
            
            # Извлекаем метаинформацию
            metadata = world_data.get('metadata', {})
            
            slot_info = {
                'name': file_path.stem.replace('.world', ''),  # Имя файла без расширения
                'created_at': metadata.get('created_at', 'N/A'),
                'creatures_count': metadata.get('creatures_count', 0),
                'max_generation': metadata.get('max_generation', 0),
                'tick': metadata.get('tick', 0),
                'file_size_kb': round(file_path.stat().st_size / 1024, 1),
            }
            
            return slot_info
            
        except Exception as e:
            print(f"⚠ Ошибка при чтении метаинформации из {file_path.name}: {e}")
            return None
        
# Singleton instance
world_persistence = WorldPersistenceService()
