#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интеграции SpambiteExperiment с Renderer.

Проверяет:
1. Импорты работают
2. RenderStateDTO имеет поле experiment_dto
3. SpambiteExperiment имеет метод get_dto()
4. SpambiteExperimentWidget имеет метод draw()
5. Логика получения DTO в renderer работает
"""

import sys
import pygame
import numpy as np

def test_imports():
    """Проверить что все импорты работают."""
    print("=" * 60)
    print("TEST 1: Проверка импортов")
    print("=" * 60)
    
    try:
        from experiments.spambite import SpambiteExperiment, SpambiteExperimentWidget
        print("✓ SpambiteExperiment импорт OK")
        print("✓ SpambiteExperimentWidget импорт OK")
        
        from experiments import EXPERIMENTS
        print(f"✓ EXPERIMENTS регистр OK. Экспериментов: {list(EXPERIMENTS.keys())}")
        
        from experiments.spambite.dto import SpambiteExperimentDTO
        print("✓ SpambiteExperimentDTO импорт OK")
        
        from renderer.v3dto.dto import RenderStateDTO
        print("✓ RenderStateDTO импорт OK")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_render_state_dto_structure():
    """Проверить что RenderStateDTO имеет поле experiment_dto."""
    print("\n" + "=" * 60)
    print("TEST 2: Проверка структуры RenderStateDTO")
    print("=" * 60)
    
    try:
        from renderer.v3dto.dto import RenderStateDTO
        import inspect
        
        # Получить параметры конструктора
        sig = inspect.signature(RenderStateDTO.__init__)
        params = list(sig.parameters.keys())
        
        if 'experiment_dto' in params:
            print("✓ RenderStateDTO имеет поле experiment_dto")
        else:
            print("✗ RenderStateDTO НЕ имеет поле experiment_dto")
            print(f"  Доступные поля: {params}")
            return False
        
        # Проверить что это dataclass
        if hasattr(RenderStateDTO, '__dataclass_fields__'):
            print("✓ RenderStateDTO - это dataclass")
        else:
            print("✗ RenderStateDTO - это НЕ dataclass")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_experiment_has_get_dto():
    """Проверить что SpambiteExperiment имеет метод get_dto()."""
    print("\n" + "=" * 60)
    print("TEST 3: Проверка метода SpambiteExperiment.get_dto()")
    print("=" * 60)
    
    try:
        from experiments.spambite import SpambiteExperiment
        
        if hasattr(SpambiteExperiment, 'get_dto'):
            print("✓ SpambiteExperiment имеет метод get_dto()")
        else:
            print("✗ SpambiteExperiment НЕ имеет метод get_dto()")
            return False
        
        # Проверить что это callable
        if callable(getattr(SpambiteExperiment, 'get_dto')):
            print("✓ get_dto() - это callable метод")
        else:
            print("✗ get_dto() - это НЕ callable")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_has_draw():
    """Проверить что SpambiteExperimentWidget имеет метод draw()."""
    print("\n" + "=" * 60)
    print("TEST 4: Проверка метода SpambiteExperimentWidget.draw()")
    print("=" * 60)
    
    try:
        from experiments.spambite import SpambiteExperimentWidget
        
        if hasattr(SpambiteExperimentWidget, 'draw'):
            print("✓ SpambiteExperimentWidget имеет метод draw()")
        else:
            print("✗ SpambiteExperimentWidget НЕ имеет метод draw()")
            return False
        
        # Проверить что это callable
        if callable(getattr(SpambiteExperimentWidget, 'draw')):
            print("✓ draw() - это callable метод")
        else:
            print("✗ draw() - это НЕ callable")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_renderer_integration():
    """Проверить что Renderer имеет необходимые методы."""
    print("\n" + "=" * 60)
    print("TEST 5: Проверка методов Renderer")
    print("=" * 60)
    
    try:
        from renderer.v3dto.renderer import Renderer
        
        if hasattr(Renderer, '_prepare_render_state_dto'):
            print("✓ Renderer имеет метод _prepare_render_state_dto()")
        else:
            print("✗ Renderer НЕ имеет метод _prepare_render_state_dto()")
            return False
        
        if hasattr(Renderer, '_draw_experiment'):
            print("✓ Renderer имеет метод _draw_experiment()")
        else:
            print("✗ Renderer НЕ имеет метод _draw_experiment()")
            return False
        
        if hasattr(Renderer, '_on_experiment_choose'):
            print("✓ Renderer имеет метод _on_experiment_choose()")
        else:
            print("✗ Renderer НЕ имеет метод _on_experiment_choose()")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Запустить все тесты."""
    print("\n\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " ТЕСТ ИНТЕГРАЦИИ SPAMBITE EXPERIMENT ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    
    results.append(("Импорты", test_imports()))
    results.append(("Структура RenderStateDTO", test_render_state_dto_structure()))
    results.append(("Метод SpambiteExperiment.get_dto()", test_experiment_has_get_dto()))
    results.append(("Метод SpambiteExperimentWidget.draw()", test_widget_has_draw()))
    results.append(("Методы Renderer", test_renderer_integration()))
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    print(f"Пройдено: {passed}/{total} тестов")
    print("=" * 60)
    
    return all(result for _, result in results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
