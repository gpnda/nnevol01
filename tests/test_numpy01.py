import numpy as np

a = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
b = np.zeros(15,dtype='int')
b[0:15] = a
print (a)
print (b)













# -----------------------

# creatures = np.array([[1.0, 2.0, 3.0, 10.0],
#                       [4.0, 5.0, 6.0, 10.0]])

# print("До:")
# print(creatures)

# rotation_step = 0.1
# for creature in creatures:
#     creature[2] -= rotation_step  # НЕ изменяет оригинальный массив!

# print("После (ничего не изменилось):")
# print(creatures)

# -------------

# raycast_dots = np.zeros((10, 2), dtype='int')
# raycast_dots_idx=0

# raycast_dots[raycast_dots_idx] = np.array(
#     [11,11]
#     )
# raycast_dots_idx+=1

# raycast_dots[raycast_dots_idx] = [22,22]
# raycast_dots_idx+=1

# raycast_dots[raycast_dots_idx] = [33,33]
# raycast_dots_idx+=1

# print(raycast_dots)
