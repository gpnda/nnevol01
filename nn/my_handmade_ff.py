# -*- coding: utf-8 -*-

import math  # подключить бибилиотеку математических функций. Обращение через math.XXX
import random  # подключить бибилиотеку случайных чисел Обращение через random.XXX
import numpy as np
from numba import jit, prange
from typing import Tuple


# Конфигурация - жестко зашито 
INPUT_SIZE = 45
HIDDEN1_SIZE = 50
HIDDEN2_SIZE = 10
OUTPUT_SIZE = 3


class NeuralNetwork:  # класс нейронной сети
    def __init__(self):
        # Инициализация как раньше
        limit1 = np.sqrt(6.0 / (INPUT_SIZE + HIDDEN1_SIZE))
        self.w1 = np.random.uniform(-limit1, limit1, (INPUT_SIZE, HIDDEN1_SIZE)).astype(np.float32)
        self.b1 = np.zeros(HIDDEN1_SIZE, dtype=np.float32)
        
        limit2 = np.sqrt(6.0 / (HIDDEN1_SIZE + HIDDEN2_SIZE))
        self.w2 = np.random.uniform(-limit2, limit2, (HIDDEN1_SIZE, HIDDEN2_SIZE)).astype(np.float32)
        self.b2 = np.zeros(HIDDEN2_SIZE, dtype=np.float32)
        
        limit3 = np.sqrt(6.0 / (HIDDEN2_SIZE + OUTPUT_SIZE))
        self.w3 = np.random.uniform(-limit3, limit3, (HIDDEN2_SIZE, OUTPUT_SIZE)).astype(np.float32)
        self.b3 = np.zeros(OUTPUT_SIZE, dtype=np.float32)


    @staticmethod
    def prepare_calc(creatures):
        # creatures_nns = NeuralNetwork.prepare_calc(self.creatures)
		# эта функция склеивает все сетки в векторизованные массивы: l1_weights, l2_weights, l1_bias, l2_bias)
		# , но на выход она выдает обычный python кортеж (или если не получится, то список), 
		# содержащий эти самые numpy ndarray: l1_weights, l2_weights, l1_bias, l2_bias ...
        
        n_creatures = len(creatures)

        w1 = np.zeros((n_creatures, INPUT_SIZE, HIDDEN1_SIZE), dtype='float') 
        b1 = np.zeros((n_creatures, HIDDEN1_SIZE), dtype='float')
        w2 = np.zeros((n_creatures, HIDDEN1_SIZE, HIDDEN2_SIZE), dtype='float')
        b2 = np.zeros((n_creatures, HIDDEN2_SIZE), dtype='float')
        w3 = np.zeros((n_creatures, HIDDEN2_SIZE, OUTPUT_SIZE), dtype='float')
        b3 = np.zeros((n_creatures, OUTPUT_SIZE), dtype='float')

        for index, cr in enumerate(creatures):
            w1[index] = cr.nn.w1
            b1[index] = cr.nn.b1
            w2[index] = cr.nn.w2
            b2[index] = cr.nn.b2
            w3[index] = cr.nn.w3
            b3[index] = cr.nn.b3
        
        return w1, b1, w2, b2, w3, b3


    @staticmethod
    def make_all_decisions(all_visions_normalized, creatures_nns):
        """
        Эта функция просто пасует данные в быструю функцию, 
        разбирая List (или кортеж) на элементы
        """
        return NeuralNetwork.fast_calc_all_outs(
            all_visions_normalized, 
            creatures_nns[0], 
            creatures_nns[1], 
            creatures_nns[2], 
            creatures_nns[3],
            creatures_nns[4], 
            creatures_nns[5]
            )

    
    @staticmethod
    def fast_calc_all_outs(all_inputs: np.ndarray,
                        all_w1: np.ndarray, all_b1: np.ndarray,
                        all_w2: np.ndarray, all_b2: np.ndarray,
                        all_w3: np.ndarray, all_b3: np.ndarray) -> np.ndarray:
        """
        Прямой проход для нескольких существ ОДНОВРЕМЕННО
        all_inputs: [n_creatures, 45] входы всех существ
        all_w1: [n_creatures, 50, 45] и т.д.
        возвращает: [n_creatures, 3] решения всех существ
        """
        n_nets = all_inputs.shape[0]
        outputs = np.zeros((n_nets, OUTPUT_SIZE), dtype=np.float32)

        # Параллельно обрабатываем всех существ
        for i in prange(n_nets):
            x = all_inputs[i]
            w1 = all_w1[i]
            b1 = all_b1[i]
            w2 = all_w2[i]
            b2 = all_b2[i]
            w3 = all_w3[i]
            b3 = all_b3[i]
            
            # Первый слой
            z1 = np.zeros(HIDDEN1_SIZE, dtype=np.float32)
            for j in range(HIDDEN1_SIZE):
                sum_val = np.float32(0.0)
                for k in range(INPUT_SIZE):
                    sum_val += w1[j, k] * x[k]
                z1[j] = math.tanh(sum_val + b1[j])
            
            # Второй слой
            z2 = np.zeros(HIDDEN2_SIZE, dtype=np.float32)
            for j in range(HIDDEN2_SIZE):
                sum_val = np.float32(0.0)
                for k in range(HIDDEN1_SIZE):
                    sum_val += w2[j, k] * z1[k]
                z2[j] = math.tanh(sum_val + b2[j])
            
            # Третий слой
            for j in range(OUTPUT_SIZE):
                sum_val = np.float32(0.0)
                for k in range(HIDDEN2_SIZE):
                    sum_val += w3[j, k] * z2[k]
                outputs[i, j] = sum_val + b3[j]

        return outputs




    @staticmethod
    @jit(nopython=True, fastmath=True, cache=True)
    def fast_tanh(x: np.float32) -> np.float32:
        """Быстрая аппроксимация tanh"""
        x2 = x * x
        return x * (27.0 + x2) / (27.0 + 9.0 * x2)