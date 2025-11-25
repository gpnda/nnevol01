import numpy as np

creatures = np.array([[1.0, 2.0, 3.0, 10.0],
                      [4.0, 5.0, 6.0, 10.0]])

print("До:")
print(creatures)

rotation_step = 0.1
for creature in creatures:
    creature[2] -= rotation_step  # НЕ изменяет оригинальный массив!

print("После (ничего не изменилось):")
print(creatures)