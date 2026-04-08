# -*- coding: utf-8 -*-
"""Тест полного цикла WorldPersistenceService: save → load → update"""

import sys
import os
# Добавляем корень проекта в sys.path, чтобы тест работал при запуске из tests/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import gzip
from pathlib import Path

SAVE_NAME = "_pytest_persistence"
SAVES_DIR = Path("./saves")


def check(condition: bool, msg_ok: str, msg_fail: str):
    if condition:
        print(f"   ✓ {msg_ok}")
    else:
        print(f"   ✗ {msg_fail}")
        sys.exit(1)


# ---------------------------------------------------------------------------
print("1. Импорты...")
try:
    from world_generator import WorldGenerator
    from service.world_persistence.world_persistence import world_persistence
    print("   ✓ OK\n")
except Exception as e:
    print(f"   ✗ Ошибка: {e}\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
print("2. Создание тестового мира (50×50, из CSV-карты)...")
try:
    world = WorldGenerator.generate_world(
        width=50, height=50,
        wall_count=30, food_count=20, creatures_count=10,
        border_walls=True,
    )
    check(len(world.creatures) > 0, f"Существ: {len(world.creatures)}", "Нет существ")
    check(len(world.foods) > 0, f"Еды: {len(world.foods)}", "Нет еды")
    check(len(world.zones_map.indoor_pixels) > 0, "indoor_pixels кэш заполнен", "Пустой indoor_pixels")
    check(len(world.zones_map.outdoor_pixels) > 0, "outdoor_pixels кэш заполнен", "Пустой outdoor_pixels")
    print()
except Exception as e:
    print(f"   ✗ Ошибка: {e}\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
print("3. Изменяем поля здоровья и возраст еды для проверки восстановления...")
world.creatures[0].health = 0.42
world.creatures[0].input_hurting = 0.11
world.creatures[0].input_starving = 0.77
world.creatures[0].input_wayblocked = 0.33
world.creatures[0].input_bite_success = 0.99
world.foods[0].food_age = 88
saved_tick = world.tick
saved_creatures_count = len(world.creatures)
saved_foods_count = len(world.foods)
print(f"   tick={saved_tick}, creatures={saved_creatures_count}, foods={saved_foods_count}\n")

# ---------------------------------------------------------------------------
print("4. Сохранение мира...")
result = world_persistence.save_world(world, SAVE_NAME)
check(result, "save_world вернул True", "save_world вернул False")

save_path = SAVES_DIR / f"{SAVE_NAME}.world.gz"
check(save_path.exists(), f"Файл создан: {save_path}", "Файл не создан")

# Проверяем что zones_map попал в файл
with open(save_path, 'rb') as f:
    raw = gzip.decompress(f.read())
saved_json = json.loads(raw.decode('utf-8'))
check('zones_map' in saved_json, "zones_map присутствует в файле", "zones_map ОТСУТСТВУЕТ в файле")
check('health' in saved_json['creatures'][0], "health присутствует в creature", "health ОТСУТСТВУЕТ в creature")
check('input_hurting' in saved_json['creatures'][0], "input_hurting присутствует", "input_hurting ОТСУТСТВУЕТ")
check('input_starving' in saved_json['creatures'][0], "input_starving присутствует", "input_starving ОТСУТСТВУЕТ")
check('input_wayblocked' in saved_json['creatures'][0], "input_wayblocked присутствует", "input_wayblocked ОТСУТСТВУЕТ")
check('input_bite_success' in saved_json['creatures'][0], "input_bite_success присутствует", "input_bite_success ОТСУТСТВУЕТ")
check('food_age' in saved_json['foods'][0], "food_age присутствует в food", "food_age ОТСУТСТВУЕТ в food")
print()

# ---------------------------------------------------------------------------
print("5. Загрузка мира в новый объект...")
from world import World
world2 = World(10, 10)  # намеренно другой размер — должен исправиться при load
result = world_persistence.load_world(world2, SAVE_NAME)
check(result, "load_world вернул True", "load_world вернул False")
check(world2.width == world.width and world2.height == world.height,
      f"Размеры восстановлены: {world2.width}×{world2.height}",
      f"Размеры неверны: {world2.width}×{world2.height}")
check(world2.map.shape == (world.height, world.width),
      f"world.map shape корректен: {world2.map.shape}",
      f"world.map shape некорректен: {world2.map.shape}")
check(world2.walls_map.shape == (world.height, world.width),
      f"walls_map shape корректен",
      f"walls_map shape некорректен: {world2.walls_map.shape}")
check(world2.tick == saved_tick, f"tick восстановлен: {world2.tick}", f"tick неверен: {world2.tick}")
check(len(world2.creatures) == saved_creatures_count,
      f"creatures восстановлены: {len(world2.creatures)}",
      f"creatures неверно: {len(world2.creatures)}")
check(len(world2.foods) == saved_foods_count,
      f"foods восстановлены: {len(world2.foods)}",
      f"foods неверно: {len(world2.foods)}")
print()

# ---------------------------------------------------------------------------
print("6. Проверка восстановленных полей...")
cr0 = world2.creatures[0]
check(abs(cr0.health - 0.42) < 1e-5, f"health={cr0.health:.4f}", f"health неверен: {cr0.health}")
check(abs(cr0.input_hurting - 0.11) < 1e-5, f"input_hurting={cr0.input_hurting:.4f}", f"input_hurting неверен")
check(abs(cr0.input_starving - 0.77) < 1e-5, f"input_starving={cr0.input_starving:.4f}", f"input_starving неверен")
check(abs(cr0.input_wayblocked - 0.33) < 1e-5, f"input_wayblocked={cr0.input_wayblocked:.4f}", f"input_wayblocked неверен")
check(abs(cr0.input_bite_success - 0.99) < 1e-5, f"input_bite_success={cr0.input_bite_success:.4f}", f"input_bite_success неверен")
check(world2.foods[0].food_age == 88, f"food_age={world2.foods[0].food_age}", f"food_age неверен: {world2.foods[0].food_age}")
print()

# ---------------------------------------------------------------------------
print("7. Проверка zones_map кэшей после загрузки...")
check(len(world2.zones_map.indoor_pixels) > 0,
      f"indoor_pixels кэш заполнен ({len(world2.zones_map.indoor_pixels)} px)",
      "indoor_pixels ПУСТОЙ после загрузки — зоны недоступны")
check(len(world2.zones_map.outdoor_pixels) > 0,
      f"outdoor_pixels кэш заполнен ({len(world2.zones_map.outdoor_pixels)} px)",
      "outdoor_pixels ПУСТОЙ после загрузки — зоны недоступны")
print()

# ---------------------------------------------------------------------------
print("8. 2 тика симуляции после загрузки (проверка отсутствия исключений)...")
try:
    world2.update()
    world2.update_map()
    world2.update()
    world2.update_map()
    print("   ✓ 2 тика прошли без исключений\n")
except Exception as e:
    print(f"   ✗ Исключение при update: {e}\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
print("9. get_save_slots включает тестовый слот...")
slots = world_persistence.get_save_slots()
names = [s['name'] for s in slots]
check(SAVE_NAME in names, f"Слот '{SAVE_NAME}' найден", f"Слот не найден. Слоты: {names}")
print()

# ---------------------------------------------------------------------------
print("10. Удаляем тестовый файл...")
save_path.unlink(missing_ok=True)
check(not save_path.exists(), "Тестовый файл удалён", "Файл не удалён")
print()

print("=" * 60)
print("✓ Все проверки пройдены успешно!")
print("=" * 60)
