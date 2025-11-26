import numpy as np
from numba import jit


@jit(nopython=True)
def fast_get_all_visions(map, creatures_pos):
    step = 0.9 # шаг перемещения взгляда (для raycast - дистанция на котороую двигаем вперед указатель)
    resolution = 15 # разрешение взгляда - по сути сколько лучше отправит raycast?
    angleofview = 1.04719 # это примерно 60 градусов
    anglestep = 1.04719 / resolution
    distance_of_view = creatures_pos[0,3]
    dots_in_ray = int(distance_of_view/step)
    n_creatures = creatures_pos.shape[0] # Выясним сколько существ в массиве creatures_pos
    
    raycast_dots = np.zeros((n_creatures*resolution*dots_in_ray, 2), dtype='int') # тут хранятся просто точки, и двойка тут означает просто X,Y
    all_visions = np.zeros((n_creatures, resolution), dtype='int') # ВСЕГДА ОДИНАКОВЫЙ РАЗМЕР. 15 пикселов для 5 существ
    
    # ... Теперь тут надо писать дальше эту функцию на базе numpy

    return all_visions, raycast_dots

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
print ("================================")
map = np.zeros((30, 30), dtype='int')
creatures_pos =  np.zeros((5, 4), dtype='float') # 5 существ, по 4 значения на каждое существо: x,y,ange,distane_of_view
creatures_pos[:3] = 21
print (fast_get_all_visions(map , creatures_pos))


