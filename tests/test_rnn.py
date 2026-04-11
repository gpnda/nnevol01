import sys, traceback
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from nn.rnn import NeuralNetwork
    import numpy as np

    nn1 = NeuralNetwork()
    print('init OK, h1_state sum:', nn1.h1_state.sum())

    nn2 = NeuralNetwork.copy(nn1)
    nn1.h1_state[:] = 99.0
    print('copy isolates states:', nn2.h1_state.sum() == 0.0)

    nn2.mutate(0.1, 0.1)
    print('mutate OK')

    class FakeCr:
        def __init__(self): self.nn = NeuralNetwork()

    creatures = [FakeCr() for _ in range(5)]
    creatures_nns = NeuralNetwork.prepare_calc(creatures)
    print('prepare_calc len:', len(creatures_nns))

    all_inputs = np.random.rand(5, 50).astype(np.float32)
    outputs = NeuralNetwork.make_all_decisions(all_inputs, creatures, creatures_nns)
    print('outputs shape:', outputs.shape)
    print('h1_state non-zero after tick:', creatures[0].nn.h1_state.sum() != 0.0)

    # int64 входы (как в реальной симуляции: np.concatenate(all_visions[int], all_other_inputs[float32]))
    creatures_nns2 = NeuralNetwork.prepare_calc(creatures)
    all_inputs_int = np.zeros((5, 50), dtype=np.int64)
    outputs2 = NeuralNetwork.make_all_decisions(all_inputs_int, creatures, creatures_nns2)
    print('int64 input handled OK, outputs shape:', outputs2.shape)

    print('ALL OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
