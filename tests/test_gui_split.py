#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест новой структуры GUI с разделением на два класса"""

import pygame
from gui import BIOSStyleGUI, VariablesPanel, FunctionKeysPanel


def test_variables_panel():
    """Тест панели переменных"""
    print("Testing VariablesPanel...")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    panel = VariablesPanel(screen, font_size=24, line_height=30)
    
    # Проверка добавления переменных
    panel.add_variable("Speed", 50, min_val=0, max_val=100)
    panel.add_variable("Power", 75.5, float, 0.0, 100.0)
    
    # Проверка получения переменной
    assert panel.get_variable("Speed") == 50, "Speed should be 50"
    assert panel.get_variable("Power") == 75.5, "Power should be 75.5"
    
    # Проверка установки переменной
    panel.set_variable("Speed", 100)
    assert panel.get_variable("Speed") == 100, "Speed should be 100 after set"
    
    # Проверка границ
    panel.set_variable("Speed", 200)
    assert panel.get_variable("Speed") == 100, "Speed should be capped at 100"
    
    print("✓ VariablesPanel tests passed")
    pygame.quit()


def test_function_keys_panel():
    """Тест панели функциональных клавиш"""
    print("Testing FunctionKeysPanel...")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    panel = FunctionKeysPanel(screen, font_size=24)
    
    call_count = [0]
    
    def callback():
        call_count[0] += 1
    
    # Проверка добавления функциональных клавиш
    panel.add_function_key("F1", "Test", callback)
    panel.add_function_key("F2", "Test2", callback)
    
    assert len(panel.function_keys) == 2, "Should have 2 function keys"
    
    print("✓ FunctionKeysPanel tests passed")
    pygame.quit()


def test_bios_gui():
    """Тест комбинированного GUI"""
    print("Testing BIOSStyleGUI...")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    gui = BIOSStyleGUI(screen, font_size=24, line_height=30)
    
    # Проверка добавления переменных через основной класс
    gui.add_variable("Speed", 50, min_val=0, max_val=100)
    gui.add_variable("Power", 75.5, float, 0.0, 100.0)
    
    # Проверка добавления функциональных клавиш через основной класс
    gui.add_function_key("F1", "Test", lambda: None)
    
    # Проверка что переменные доступны
    assert gui.get_variable("Speed") == 50, "Speed should be 50 through GUI"
    
    # Проверка установки через основной класс
    gui.set_variable("Speed", 75)
    assert gui.get_variable("Speed") == 75, "Speed should be 75 after set through GUI"
    
    print("✓ BIOSStyleGUI tests passed")
    pygame.quit()


def test_constants():
    """Проверка что константы вынесены правильно"""
    print("Testing constants...")
    
    # VariablesPanel константы
    assert VariablesPanel.MAX_VISIBLE_VARS == 15
    assert VariablesPanel.PANEL_X == 0
    assert VariablesPanel.PANEL_Y == 0
    assert VariablesPanel.PANEL_WIDTH == 0  # 0 = весь экран
    assert VariablesPanel.PANEL_HEIGHT == 0  # 0 = весь экран минус нижняя панель
    assert VariablesPanel.FUNC_KEYS_PANEL_HEIGHT == 80
    assert VariablesPanel.PADDING_X == 10
    assert VariablesPanel.PADDING_Y == 10
    
    # FunctionKeysPanel константы
    assert FunctionKeysPanel.MAX_FUNC_KEYS == 8
    assert FunctionKeysPanel.FUNC_KEYS_PER_ROW == 4
    assert FunctionKeysPanel.PANEL_HEIGHT == 80
    assert FunctionKeysPanel.SEPARATOR_HEIGHT == 20
    
    print("✓ Constants tests passed")


if __name__ == "__main__":
    print("Running GUI split tests...\n")
    
    try:
        test_variables_panel()
        test_function_keys_panel()
        test_bios_gui()
        test_constants()
        
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
