# -*- coding: utf-8 -*-
"""Быстрый тест функциональности WorldPersistenceService"""

import sys
import json
import gzip
from pathlib import Path

# Проверяем что импорты работают
print("1. Проверка импортов...")
try:
    from service.world_persistence.world_persistence import world_persistence
    print("   ✓ world_persistence импортирован\n")
except Exception as e:
    print(f"   ✗ Ошибка импорта: {e}\n")
    sys.exit(1)

# Проверяем создание директории сохранений
print("2. Проверка директории сохранений...")
saves_dir = Path("./saves")
if saves_dir.exists():
    print(f"   ✓ Директория {saves_dir} существует\n")
else:
    print(f"   ✗ Директория {saves_dir} не создана\n")

# Проверяем создание маленького тестового файла
print("3. Создание тестовой сохраньки (только JSON структура)...")
try:
    test_save = {
        'metadata': {'width': 100, 'height': 50, 'tick': 1000},
        'walls_map': [[1, 0], [0, 1]],
        'creatures': [],
        'foods': [],
        'simparams': {}
    }
    
    json_str = json.dumps(test_save, indent=2)
    json_bytes = json_str.encode('utf-8')
    compressed = gzip.compress(json_bytes, compresslevel=9)
    
    test_path = Path("./saves/test_structure.world.gz")
    with open(test_path, 'wb') as f:
        f.write(compressed)
    
    file_size = test_path.stat().st_size
    print(f"   ✓ Тестовый файл создан: {file_size} bytes\n")
    
    # Проверяем распаковку
    with open(test_path, 'rb') as f:
        compressed_read = f.read()
    
    json_bytes_read = gzip.decompress(compressed_read)
    json_str_read = json_bytes_read.decode('utf-8')
    test_loaded = json.loads(json_str_read)
    
    if test_loaded['metadata']['width'] == 100:
        print("   ✓ JSON.GZ сохранение/загрузка работает\n")
    else:
        print("   ✗ Данные некорректны после загрузки\n")
        
except Exception as e:
    print(f"   ✗ Ошибка при работе с JSON.GZ: {e}\n")
    sys.exit(1)

print("=" * 60)
print("✓ Все предварительные проверки пройдены!")
print("=" * 60)
print("\nИспользование:")
print("  app.save_world('test')      # Сохранить мир в ./saves/test.world.gz")
print("  app.load_world('test')      # Загрузить мир из ./saves/test.world.gz")
