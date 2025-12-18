# -*- coding: utf-8 -*-
"""
Запуск теста mutate() с красивым форматированием.

Использование:
  python tests/test_mutate.py
"""

import sys
import os

# Добавляем корневую директорию в path чтобы импортировать nn модуль
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_mutate import test_mutate

if __name__ == "__main__":
    test_mutate()
