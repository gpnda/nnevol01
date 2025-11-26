import numpy as np
from numba import jit


@jit(nopython=True)
def bad_example_append():
    arr=[]
    arr.append([[1,2,3,4,5],[1,2,3,4,5]])
    arr.append([[1,2,3,4,5],[1,2,3,4,5]])
    arr.append([[1,2,3,4,5],[1,2,3,4,5]])

    nparr = np.zeros((4, 2, 5)) # Сразу создаем zerofill массив
    nparr[:3] = np.array(arr)
    
    # Просто заполняем массив другими значениями (вместо нулей)
    nparr[3] = np.array([[7,7,7,7,7], [7,7,7,7,7]])
    return nparr

print (type(bad_example_append()))
print (bad_example_append())


