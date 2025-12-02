import numpy as np

INPUT_SIZE = 45
HIDDEN1_SIZE = 50
HIDDEN2_SIZE = 10
OUTPUT_SIZE = 3


limit1 = 0.1
aaa = np.zeros((1, INPUT_SIZE, HIDDEN1_SIZE), dtype='float') 
bbb = np.random.uniform(-limit1, limit1, (HIDDEN1_SIZE, INPUT_SIZE)).astype(np.float32)

print(aaa.shape)
print(aaa.shape)

