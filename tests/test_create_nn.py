from pathlib import Path
import sys
import numpy as np

# Ensure imports work no matter where this script is launched from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from creature import Creature


# Fixed float format for all numpy arrays: #.####
np.set_printoptions(formatter={"float_kind": lambda x: f"{x:.4f}"})
# np.set_printoptions(formatter={"float_kind": lambda x: f"{int(x)}"})


def main() -> None:
    creature = Creature(x=0, y=0)

    print(f"Creature id={creature.id}, generation={creature.generation}")
    print()

    print("w1:")
    print(creature.nn.w1)
    print("b1:")
    print(creature.nn.b1)
    print()

    print("w2:")
    print(creature.nn.w2)
    print("b2:")
    print(creature.nn.b2)
    print()

    print("w3:")
    print(creature.nn.w3)
    print("b3:")
    print(creature.nn.b3)


if __name__ == "__main__":
    main()
