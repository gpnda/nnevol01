import numpy as np
import time

arr = np.random.rand(1000, 1000)  # Большой массив для теста

# Метод 1: copy()
start = time.time()
for i in range (1000):
	copy1 = arr.copy()
time1 = time.time() - start


# Метод 2: np.copy()
start = time.time()
for i in range (1000):
	copy2 = np.copy(arr)
time2 = time.time() - start


# Метод 3: срез [:]
start = time.time()
for i in range (1000):
	copy3 = arr[:]
time3 = time.time() - start

print (time1)
print (time2)
print (time3)


# (.venv) albert@albert-lenovo:~/!___WORK/evol/2025-11-22$ python test_numpy_copy.py 
# 1.4046869277954102
# 1.390671968460083
# 0.00044798851013183594
# (.venv) albert@albert-lenovo:~/!___WORK/evol/2025-11-22$ python test_numpy_copy.py 
# 1.3804302215576172
# 1.430504322052002
# 0.0004634857177734375
# (.venv) albert@albert-lenovo:~/!___WORK/evol/2025-11-22$ python test_numpy_copy.py 
# 1.4216599464416504
# 1.4084696769714355
# 0.0004582405090332031
# (.venv) albert@albert-lenovo:~/!___WORK/evol/2025-11-22$ python test_numpy_copy.py 
# 1.3873963356018066
# 1.3756370544433594
# 0.00042366981506347656
