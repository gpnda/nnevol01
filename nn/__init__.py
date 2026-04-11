# -*- coding: utf-8 -*-
# Единая точка переключения нейросети.
# Меняй NN_BACKEND здесь — больше нигде ничего менять не надо.
#
# Доступные варианты:
#   'ff'         — nn/my_handmade_ff.py  (feedforward, numba)
#   'rnn'        — nn/rnn.py             (RNN, кастомный)
#   'torch_rnn'  — nn/nn_torch_rnn.py   (RNN, PyTorch)

NN_BACKEND = 'rnn'

if NN_BACKEND == 'ff':
    from nn.my_handmade_ff import NeuralNetwork
elif NN_BACKEND == 'rnn':
    from nn.rnn import NeuralNetwork
elif NN_BACKEND == 'torch_rnn':
    from nn.nn_torch_rnn import NeuralNetwork
else:
    raise ImportError(f"Unknown NN_BACKEND: '{NN_BACKEND}'. Choose 'ff', 'rnn', or 'torch_rnn'.")

__all__ = ['NeuralNetwork', 'NN_BACKEND']
