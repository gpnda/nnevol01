import numpy as np
from numba import jit
import math


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
    raycast_dots_idx=0
    all_visions = np.zeros((n_creatures, resolution*3), dtype='int') # ВСЕГДА ОДИНАКОВЫЙ РАЗМЕР. 15 пикселов для 5 существ
    
    for index, cr in enumerate(creatures_pos):
        visionRed = np.zeros(15, dtype='int')
        visionGreen = np.zeros(15, dtype='int')
        visionBlue = np.zeros(15, dtype='int')
        vision_idx = 0

        for a in range(resolution):
            adelta = -1*angleofview/2 + a*anglestep # угол текущего луча
            d = 0 # длина текущего луча, которую постепенно увеличиваем
            cur_vision = 0
            while d < cr[3]:
                d += step
                x = cr[0] + d*math.cos(cr[2]+adelta)
                y = cr[1] + d*math.sin(cr[2]+adelta)
                if int(x) == int(cr[0]) and int(y) == int(cr[1]):
                    continue # Если смотрит на свое тело, то пропустим эту итерацию
                if True: #index == 0
                    # сохраним точку в массив точек
                    raycast_dots[raycast_dots_idx] = np.array([x,y])
                    raycast_dots_idx+=1
                
                dot = 0
                ix = int(x)
                iy = int(y)
                mw = map.shape[1]
                mh = map.shape[0]
                if ix < 0 or ix >= mw or iy < 0 or iy >= mh:
                    # за пределами карты → чёрный
                    visionRed[vision_idx] = 0
                    visionGreen[vision_idx] = 0
                    visionBlue[vision_idx] = 0
                    vision_idx += 1
                    break
                else:
                    dot = map[iy,ix]

                # Если взгляд во что-то уперся, то Сохраняем цвет точки и Прерываем raycast
                if dot > 0:
                    cur_vision = dot
                    # Сюда надо вставлять опреденений цветов и разложение на каналы.
                    dotColor = np.zeros(3, dtype='int')
                    if dot == 1:
                        dotColor = np.array([100,100,100])
                    elif dot == 2:
                        dotColor = np.array([255,0,0])
                    elif dot == 3:
                        dotColor = np.array([0,0,255])
                    else:
                        dotColor = np.array([0,0,0])

                    # Сюда вставляем искажение цвета, в зависимости от дистанции
                    # Условие нужно, потому что иногда d улетает больше чем self.viewdistance, 
                    # тогда цвет станет больше 255
                    # if d < self.viewdistance:
                    #     dotColor = Creature.__fadeColors(dotColor , d/self.viewdistance )


                    # тут переменная dotColor содержит RGB Представление цвета
                    visionRed[vision_idx] = dotColor[0]
                    visionGreen[vision_idx] = dotColor[1]
                    visionBlue[vision_idx] = dotColor[2]
                    vision_idx += 1
                    break
            else:
                # В этой ветке обслуживаем ситуацию, когда Raycast достиг 
                # максимальной дистанции взгляда и ничего не увидел
                visionRed[vision_idx] = 0
                visionGreen[vision_idx] = 0
                visionBlue[vision_idx] = 0
                vision_idx += 1

        # Превратим массив элементами карты в массив с цветами
        # далее - ручная конкатенация трех массивов в один
        visionRGB = np.empty(resolution*3, dtype='int')
        # Копирую вручную (JIT это любит!)
        visionRGB[0:15] = visionRed
        visionRGB[15:30] = visionGreen
        visionRGB[30:45] = visionBlue
        # print("visionRed: " + str(visionRed))
        # print("visionGreen: " + str(visionGreen))
        # print("visionBlue: " + str(visionBlue))

        all_visions[index] = visionRGB
        
    # print("Длина массива all_visions: " + str(len(all_visions)))
    # for index,v in enumerate(all_visions):
    #   print("Длина " + str(index) + " массива vision: " + str(len(v)))
    return all_visions, raycast_dots


    






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


