import random
import copy
import time


class Creature():
    
    def __init__(self):
        self.energy = 1.0
        self.age = random.randint(0,500)
        self.birth_ages = [
            random.randint(90, 110), 
            random.randint(190, 210), 
            random.randint(290, 310)
            ]
    
    def reprodCreature(self):
        cr_babies = []
        print ("начало цикла по рождению детей")
        for j in range(0, 3):
            c = Creature()
            c.age = 0
            c.energy = 1.0
            c.birth_ages = [
            random.randint(90, 110), 
            random.randint(190, 210), 
            random.randint(290, 310),
            random.randint(490, 510),
            ]
            cr_babies.append(c)
        return cr_babies    


def is_population_not_overcrowd(arr):
    if len(arr)>500:
        return False
    else:
        return True

if __name__ == "__main__":
    arr = []
    for i in range(70):
        arr.append(Creature())

    tick = 0
    while True:
        tick += 1
        # Существа живут и тратят энергию каким-то образом 1.0/0,003 = 333 - средняя продолжительность жизни
        for cr in arr:

            # каждый тик увеличиваем возраст существа
            cr.age += 1

            # равномерные затраты энергии
            cr.energy -= random.random()*0.015

            # спорадричсеские моменты когда существо питается и пополняет энергию
            if random.random() < 0.02:
                cr.energy += 0.1
        
        # Удалим умерших
        new_arr = []
        for creature in arr:
            if creature.energy >= 0 and creature.age < 500:
                new_arr.append(creature)
        arr = new_arr

        if is_population_not_overcrowd(arr):
            for i in filter(lambda c:c.age in c.birth_ages, arr):
                arr += i.reprodCreature()
                print("Добавлено 3 существа----------------------------------------")
        
        print("Tick: " + str(tick) + "|   Размер популяции: " + str(len(arr)))
        #time.sleep(0.05)

