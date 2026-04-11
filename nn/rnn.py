# -*- coding: utf-8 -*-

import numpy as np


# Config must match FF network
INPUT_SIZE = 50
HIDDEN1_SIZE = 50
HIDDEN2_SIZE = 10
OUTPUT_SIZE = 3


class NeuralNetwork:
    """Elman RNN with two recurrent hidden layers."""

    def __init__(self):
        limit1 = np.sqrt(6.0 / (INPUT_SIZE + HIDDEN1_SIZE))
        self.w1_x = np.random.uniform(-limit1, limit1, (INPUT_SIZE, HIDDEN1_SIZE)).astype(np.float32)
        self.w1_h = np.random.uniform(-limit1, limit1, (HIDDEN1_SIZE, HIDDEN1_SIZE)).astype(np.float32)
        self.b1 = np.zeros(HIDDEN1_SIZE, dtype=np.float32)

        limit2 = np.sqrt(6.0 / (HIDDEN1_SIZE + HIDDEN2_SIZE))
        self.w2_x = np.random.uniform(-limit2, limit2, (HIDDEN1_SIZE, HIDDEN2_SIZE)).astype(np.float32)
        self.w2_h = np.random.uniform(-limit2, limit2, (HIDDEN2_SIZE, HIDDEN2_SIZE)).astype(np.float32)
        self.b2 = np.zeros(HIDDEN2_SIZE, dtype=np.float32)

        limit3 = np.sqrt(6.0 / (HIDDEN2_SIZE + OUTPUT_SIZE))
        self.w3 = np.random.uniform(-limit3, limit3, (HIDDEN2_SIZE, OUTPUT_SIZE)).astype(np.float32)
        self.b3 = np.zeros(OUTPUT_SIZE, dtype=np.float32)

        # Hidden states are per-creature memory.
        self.h1_state = np.zeros(HIDDEN1_SIZE, dtype=np.float32)
        self.h2_state = np.zeros(HIDDEN2_SIZE, dtype=np.float32)

    def get_states(self) -> list:
        return [self.h1_state, self.h2_state]

    def set_states(self, states: list) -> None:
        self.h1_state = states[0]
        self.h2_state = states[1]

    def print_nn_parameters(self):
        print("w1_x:", self.w1_x)
        print("w1_h:", self.w1_h)
        print("b1:", self.b1)
        print("w2_x:", self.w2_x)
        print("w2_h:", self.w2_h)
        print("b2:", self.b2)
        print("w3:", self.w3)
        print("b3:", self.b3)
        print("h1_state:", self.h1_state)
        print("h2_state:", self.h2_state)

    @staticmethod
    def copy(original_nn):
        new_nn = NeuralNetwork()
        new_nn.w1_x = original_nn.w1_x.copy()
        new_nn.w1_h = original_nn.w1_h.copy()
        new_nn.b1 = original_nn.b1.copy()
        new_nn.w2_x = original_nn.w2_x.copy()
        new_nn.w2_h = original_nn.w2_h.copy()
        new_nn.b2 = original_nn.b2.copy()
        new_nn.w3 = original_nn.w3.copy()
        new_nn.b3 = original_nn.b3.copy()
        # Keep newborn states zeroed.
        return new_nn

    def serialize(self) -> dict:
        return {
            '__type__': 'rnn',
            'w1_x': self.w1_x.tolist(),
            'w1_h': self.w1_h.tolist(),
            'b1': self.b1.tolist(),
            'w2_x': self.w2_x.tolist(),
            'w2_h': self.w2_h.tolist(),
            'b2': self.b2.tolist(),
            'w3': self.w3.tolist(),
            'b3': self.b3.tolist(),
            'h1_state': self.h1_state.tolist(),
            'h2_state': self.h2_state.tolist(),
        }

    def deserialize(self, data: dict) -> None:
        self.w1_x = np.array(data['w1_x'], dtype=np.float32)
        self.w1_h = np.array(data['w1_h'], dtype=np.float32)
        self.b1 = np.array(data['b1'], dtype=np.float32)
        self.w2_x = np.array(data['w2_x'], dtype=np.float32)
        self.w2_h = np.array(data['w2_h'], dtype=np.float32)
        self.b2 = np.array(data['b2'], dtype=np.float32)
        self.w3 = np.array(data['w3'], dtype=np.float32)
        self.b3 = np.array(data['b3'], dtype=np.float32)
        self.h1_state = np.array(data['h1_state'], dtype=np.float32)
        self.h2_state = np.array(data['h2_state'], dtype=np.float32)

    def mutate(self, mutation_probability: float, mutation_strength: float) -> None:
        params = [self.w1_x, self.w1_h, self.b1, self.w2_x, self.w2_h, self.b2, self.w3, self.b3]
        for param in params:
            if mutation_probability > 0:
                mask = (np.random.rand(*param.shape) < mutation_probability).astype(np.float32)
                random_changes = mutation_strength * (2 * np.random.rand(*param.shape).astype(np.float32) - 1)
                param += random_changes * mask

    @staticmethod
    def prepare_calc(creatures) -> tuple:
        n = len(creatures)

        w1_x = np.empty((n, INPUT_SIZE, HIDDEN1_SIZE), dtype=np.float32)
        w1_h = np.empty((n, HIDDEN1_SIZE, HIDDEN1_SIZE), dtype=np.float32)
        b1 = np.empty((n, HIDDEN1_SIZE), dtype=np.float32)
        w2_x = np.empty((n, HIDDEN1_SIZE, HIDDEN2_SIZE), dtype=np.float32)
        w2_h = np.empty((n, HIDDEN2_SIZE, HIDDEN2_SIZE), dtype=np.float32)
        b2 = np.empty((n, HIDDEN2_SIZE), dtype=np.float32)
        w3 = np.empty((n, HIDDEN2_SIZE, OUTPUT_SIZE), dtype=np.float32)
        b3 = np.empty((n, OUTPUT_SIZE), dtype=np.float32)
        h1 = np.empty((n, HIDDEN1_SIZE), dtype=np.float32)
        h2 = np.empty((n, HIDDEN2_SIZE), dtype=np.float32)

        for i, cr in enumerate(creatures):
            nn = cr.nn
            w1_x[i] = nn.w1_x
            w1_h[i] = nn.w1_h
            b1[i] = nn.b1
            w2_x[i] = nn.w2_x
            w2_h[i] = nn.w2_h
            b2[i] = nn.b2
            w3[i] = nn.w3
            b3[i] = nn.b3
            h1[i] = nn.h1_state
            h2[i] = nn.h2_state

        return w1_x, w1_h, b1, w2_x, w2_h, b2, w3, b3, h1, h2

    @staticmethod
    def make_all_decisions(all_inputs: np.ndarray, creatures, creatures_nns: tuple) -> np.ndarray:
        if all_inputs.dtype != np.float32:
            all_inputs = all_inputs.astype(np.float32)

        n = all_inputs.shape[0]
        if n == 0:
            return np.zeros((0, OUTPUT_SIZE), dtype=np.float32)

        w1_x, w1_h, b1, w2_x, w2_h, b2, w3, b3, h1, h2 = creatures_nns

        # Layer 1: h1_new = tanh(x @ W1_x + h1_prev @ W1_h + b1)
        new_h1 = np.tanh(
            np.einsum("ni,nij->nj", all_inputs, w1_x)
            + np.einsum("ni,nij->nj", h1, w1_h)
            + b1
        ).astype(np.float32)

        # Layer 2: h2_new = tanh(h1_new @ W2_x + h2_prev @ W2_h + b2)
        new_h2 = np.tanh(
            np.einsum("ni,nij->nj", new_h1, w2_x)
            + np.einsum("ni,nij->nj", h2, w2_h)
            + b2
        ).astype(np.float32)

        # Output: out = tanh(h2_new @ W3 + b3), then clamp to [-1, 1]
        outputs = np.clip(
            np.tanh(np.einsum("ni,nij->nj", new_h2, w3) + b3),
            -1.0,
            1.0,
        ).astype(np.float32)

        for i, cr in enumerate(creatures):
            cr.nn.h1_state = new_h1[i]
            cr.nn.h2_state = new_h2[i]

        return outputs
