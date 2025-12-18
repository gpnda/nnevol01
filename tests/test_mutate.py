# -*- coding: utf-8 -*-
"""
Тест для метода NeuralNetwork.mutate()

Выводит исходные веса и веса после мутации с подсвечиванием изменённых элементов.
"""

import numpy as np
from nn.my_handmade_ff import NeuralNetwork


# ANSI цветовые коды для терминала
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'


def format_weight(value, is_changed=False):
    """Форматирует вес с подсвечиванием если он изменился."""
    text = f"{value:6.2f}"
    if is_changed:
        return f"{Colors.RED}{Colors.BOLD}{text}{Colors.RESET}"
    return text


def print_matrix_as_grid(name: str, original: np.ndarray, mutated: np.ndarray, 
                        tolerance: float = 1e-6):
    """
    Выводит матрицы вертикально: исходная матрица, затем мутированная.
    Изменённые элементы в мутированной матрице выделены красным.
    
    Args:
        name: Имя параметра (w1, b1, и т.д.)
        original: Исходный массив
        mutated: Мутированный массив
        tolerance: Минимальное изменение для выделения
    """
    print(f"\n{'='*100}")
    print(f"{Colors.BOLD}{name}{Colors.RESET}")
    print(f"{'='*100}")
    
    # Вычисляем какие элементы изменились
    changed_mask = np.abs(original - mutated) > tolerance
    changed_count = np.sum(changed_mask)
    
    # Для матриц
    if len(original.shape) == 2:
        rows, cols = original.shape
        print(f"Shape: {rows}×{cols}\n")
        
        # ИСХОДНАЯ МАТРИЦА
        print(f"{Colors.BOLD}ORIGINAL:{Colors.RESET}")
        for i in range(rows):
            row_str = "  ".join([f"{original[i, j]:6.2f}" for j in range(cols)])
            print(f"[{i:2d}]  {row_str}")
        
        # МУТИРОВАННАЯ МАТРИЦА (с подсветкой)
        print(f"\n{Colors.BOLD}MUTATED (changed values highlighted in red):{Colors.RESET}")
        for i in range(rows):
            row_items = []
            for j in range(cols):
                if changed_mask[i, j]:
                    row_items.append(f"{Colors.RED}{Colors.BOLD}{mutated[i, j]:6.2f}{Colors.RESET}")
                else:
                    row_items.append(f"{mutated[i, j]:6.2f}")
            row_str = "  ".join(row_items)
            print(f"[{i:2d}]  {row_str}")
        
        print(f"\n{Colors.GREEN}Total changed: {changed_count}/{rows*cols} ({100*changed_count/(rows*cols):.1f}%){Colors.RESET}")
    
    # Для векторов (bias)
    elif len(original.shape) == 1:
        size = original.shape[0]
        print(f"Size: {size}\n")
        
        # ИСХОДНЫЙ ВЕКТОР
        print(f"{Colors.BOLD}ORIGINAL:{Colors.RESET}")
        items_per_row = 10
        for i in range(0, size, items_per_row):
            end_idx = min(i + items_per_row, size)
            indices = " ".join([f"[{j:2d}]" for j in range(i, end_idx)])
            values = "  ".join([f"{original[j]:6.2f}" for j in range(i, end_idx)])
            print(f"  {indices}")
            print(f"  {values}")
        
        # МУТИРОВАННЫЙ ВЕКТОР (с подсветкой)
        print(f"\n{Colors.BOLD}MUTATED (changed values highlighted in red):{Colors.RESET}")
        for i in range(0, size, items_per_row):
            end_idx = min(i + items_per_row, size)
            indices = " ".join([f"[{j:2d}]" for j in range(i, end_idx)])
            
            value_items = []
            for j in range(i, end_idx):
                if changed_mask[j]:
                    value_items.append(f"{Colors.RED}{Colors.BOLD}{mutated[j]:6.2f}{Colors.RESET}")
                else:
                    value_items.append(f"{mutated[j]:6.2f}")
            values = "  ".join(value_items)
            print(f"  {indices}")
            print(f"  {values}")
        
        print(f"\n{Colors.GREEN}Total changed: {changed_count}/{size} ({100*changed_count/size:.1f}%){Colors.RESET}")


def test_mutate():
    """Основной тест для метода mutate()."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}")
    print(f"NeuralNetwork.mutate() TEST")
    print(f"{'='*80}{Colors.RESET}\n")
    
    # Параметры теста
    mutation_probability = 0.01  # 30% весов будут мутированы
    mutation_strength = 0.5     # Сила мутации
    
    print(f"{Colors.BOLD}Parameters:{Colors.RESET}")
    print(f"  Mutation probability: {mutation_probability * 100}%")
    print(f"  Mutation strength: {mutation_strength}")
    
    # Создаём исходную сеть
    print(f"\n{Colors.BOLD}1. Creating original network...{Colors.RESET}")
    original_nn = NeuralNetwork()
    
    # Копируем веса для сравнения
    original_w1 = original_nn.w1.copy()
    original_b1 = original_nn.b1.copy()
    original_w2 = original_nn.w2.copy()
    original_b2 = original_nn.b2.copy()
    original_w3 = original_nn.w3.copy()
    original_b3 = original_nn.b3.copy()
    
    print(f"Network created with layers:")
    print(f"  Layer 1: {original_nn.w1.shape} weights + {original_nn.b1.shape} bias")
    print(f"  Layer 2: {original_nn.w2.shape} weights + {original_nn.b2.shape} bias")
    print(f"  Layer 3: {original_nn.w3.shape} weights + {original_nn.b3.shape} bias")
    
    # Применяем мутацию
    print(f"\n{Colors.BOLD}2. Applying mutation...{Colors.RESET}")
    original_nn.mutate(mutation_probability, mutation_strength)
    print(f"Mutation applied!")
    
    # Выводим результаты (только изменённые)
    print(f"\n{Colors.BOLD}3. Comparison Results:{Colors.RESET}")
    
    print_matrix_as_grid("Weights Layer 1 (w1)", original_w1, original_nn.w1)
    print_matrix_as_grid("Bias Layer 1 (b1)", original_b1, original_nn.b1)
    
    print_matrix_as_grid("Weights Layer 2 (w2)", original_w2, original_nn.w2)
    print_matrix_as_grid("Bias Layer 2 (b2)", original_b2, original_nn.b2)
    
    print_matrix_as_grid("Weights Layer 3 (w3)", original_w3, original_nn.w3)
    print_matrix_as_grid("Bias Layer 3 (b3)", original_b3, original_nn.b3)
    
    # Статистика
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}{Colors.RESET}")
    
    total_params = (original_w1.size + original_b1.size + 
                   original_w2.size + original_b2.size + 
                   original_w3.size + original_b3.size)
    
    changed_count = (
        np.sum(np.abs(original_w1 - original_nn.w1) > 1e-6) +
        np.sum(np.abs(original_b1 - original_nn.b1) > 1e-6) +
        np.sum(np.abs(original_w2 - original_nn.w2) > 1e-6) +
        np.sum(np.abs(original_b2 - original_nn.b2) > 1e-6) +
        np.sum(np.abs(original_w3 - original_nn.w3) > 1e-6) +
        np.sum(np.abs(original_b3 - original_nn.b3) > 1e-6)
    )
    
    print(f"Total parameters: {total_params}")
    print(f"Changed parameters: {changed_count}")
    print(f"Change rate: {100 * changed_count / total_params:.2f}%")
    print(f"Expected rate: {100 * mutation_probability:.2f}%")
    
    # Проверка
    if abs(100 * changed_count / total_params - 100 * mutation_probability) < 5:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ TEST PASSED{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Deviation from expected mutation rate{Colors.RESET}")
    
    print(f"\n")


if __name__ == "__main__":
    test_mutate()
