#Отличие от lazer7.py только в числе каналов и их исходный координат
import matplotlib.pyplot as plt
import numpy as np
from random import random
import scipy.special
import math
import cmath


#Начальные неизвестные фазы у лазера
phases = list(0 * math.pi*2 for i in range(4))

#Функции для поиска наилучшей интенсивности по сдвигам фаз
maximum_intensivity = 0
def check_intensivity(deltas):
    global phases
    for i in range(0, len(phases)):
        phases[i] -= deltas[i]
    now = intensivity(0, 0) 
    #print(now)   
    for i in range(len(phases)):
        phases[i] += deltas[i]
    return now
indexes=list(0 for i in range(len(phases)))
def rec(prevs: list):
    global adds_possible, maximum_intensivity
    if (len(prevs) == len(phases)):
        
        intens = check_intensivity(prevs)
        if (intens > maximum_intensivity):
            maximum_intensivity = intens
            indexes.clear()
            for i in prevs:
                indexes.append(i)
        return
    else:
        for i in adds_possible[len(prevs)]:
            prevs.append(i)
            rec(prevs)
            prevs.remove(i)
    
#Для упрощения рассматриваем плоскость на расстоянии 1    
z=1

#координаты центров каналов
x_n = (2, -2, -2, 2)
y_n = (2, 2, -2, -2)

#Функция Бесселя
def J(x):
    return scipy.special.j1(x)

#Возвращает интенсивность для точки (x,y)
def intensivity(x, y):
    global phases, x_n, y_n, z
    ans = 0
    C = cmath.exp(complex(0, (x**2+y**2)/2/z))
    
    for i in range(4):
        zphase = complex(math.cos(phases[i]), math.sin(phases[i])) 
        if (x!=0 or y!=0):
            ans+= (math.pi*C*zphase*cmath.exp(complex(0, x/z*x_n[i]+y/z*y_n[i]))*2*J(math.sqrt(x**2/z**2+y**2/z**2))/math.sqrt(x**2/z**2+y**2/z**2)).real
        else:
            ans+= (math.pi*C*zphase).real
        
    return ans**2

width = 100  # Ширина изображения
height = 100  # Высота изображения
k = 10 #Коэффциент отдаления

#Возвращает картинку с текущим лазером
def simulate_laser():
    global width, height,k
    maxvalue = 0
    # Создаем пустое изображение
    image = np.zeros((2*height, width*2))
    I_center = 0
    # Моделируем поведение лазера
    for x in range(-width, width):
        for y in range(-height, height):
            
            # Расчет интенсивности с использованием фазы
            intensity = intensivity(x/width*k, y/height*k)
            
            # Записываем интенсивность в изображение
            image[y+height, x+width] = intensity.real
            if ((x==0) and (y ==0)):
                I_center = intensity.real
                #print("INTENSE: ", intensity)
            maxvalue = max(maxvalue, intensity.real)
    for x in range(-width, width):
        for y in range(-height, height):
            
            # Записываем интенсивность в изображение
            image[y+height, x+width] = image[y+height, x+width]/maxvalue
    return image, I_center

#Добавляет фазу к одному из каналов
def add_phase(index, delta):
    global phases
    phases[index] += delta

#Вычисляет интенсивность в ближней зоне
def intensivity_bl(x, y):
    global phases, x_n, y_n
    z=0.000000000000001
    ans = 0
    C = cmath.exp(complex(0, (x**2+y**2)/2/z))
    
    for i in range(4):
        zphase = complex(math.cos(phases[i]), math.sin(phases[i])) 
        if (x!=0 or y!=0):
            ans+= (math.pi*C*zphase*cmath.exp(complex(0, x/z*x_n[i]+y/z*y_n[i]))*2*J(math.sqrt(x**2/z**2+y**2/z**2))/math.sqrt(x**2/z**2+y**2/z**2)).real
        else:
            ans+= (math.pi*C*zphase).real
        
    return ans**2
#Возвращает картинку в дальней зоне
def simulate_laser_bl():
    height = 200
    width = 200
    k = 0.00000000000001
    maxvalue = 0
    # Создаем пустое изображение
    image = np.zeros((2*height, width*2))
    # Моделируем поведение лазера
    for x in range(-width, width):
        for y in range(-height, height):
            
            # Расчет интенсивности с использованием фазы
            intensity = intensivity_bl(x/width*k, y/height*k)
            
            # Записываем интенсивность в изображение
            image[y+height, x+width] = intensity.real
            maxvalue = max(maxvalue, intensity.real)
    for x in range(-width, width):
        for y in range(-height, height):
            
            # Записываем интенсивность в изображение
            image[y+height, x+width] = image[y+height, x+width]/maxvalue
    plt.imshow(image, extent = [-1, 1, -1, 1], cmap='hot', interpolation='nearest', origin="lower")
    plt.colorbar()
    plt.title("Ближняя зона лазера")
    plt.show()

simulate_laser_bl()
adds_possible = list()
image, I_0 = simulate_laser()

plt.imshow(image, extent = [-1, 1, -1, 1], cmap='hot', interpolation='nearest', origin="lower")
plt.colorbar()
plt.title("Исходный лазер")
plt.show()
prev = I_0
while(True):
    adds_possible.clear()
    image, I_0 = simulate_laser()
    #Решаем уравнения, ищем возможные исходные фазы
    for i in range(len(phases)):
        delta = math.pi
        add_phase(i, delta)
        image, I_1 = simulate_laser()
        tmp = list()
        tmp.append(0)
        if (abs(math.sqrt(I_1)-math.sqrt(I_0))/(2*math.pi) <= 1):
            tmp.append(math.asin((math.sqrt(I_1)-math.sqrt(I_0))/(2*math.pi)))
            tmp.append(math.asin((math.sqrt(I_1)-math.sqrt(I_0))/(2*math.pi))+math.pi/2)
        if (abs(math.sqrt(I_1)+math.sqrt(I_0))/(2*math.pi) <= 1):
            
            tmp.append(math.asin((math.sqrt(I_1)+math.sqrt(I_0))/(2*math.pi)))
            tmp.append(math.asin((math.sqrt(I_1)+math.sqrt(I_0))/(2*math.pi))+math.pi/2)
        if (abs(-math.sqrt(I_1)-math.sqrt(I_0))/(2*math.pi) <= 1):
            
            tmp.append(math.asin((-math.sqrt(I_1)-math.sqrt(I_0))/(2*math.pi)))
            tmp.append(math.asin((-math.sqrt(I_1)-math.sqrt(I_0))/(2*math.pi))+math.pi/2)
        if (abs(-math.sqrt(I_1)+math.sqrt(I_0))/(2*math.pi) <= 1):
            
            tmp.append(math.asin((-math.sqrt(I_1)+math.sqrt(I_0))/(2*math.pi)))
            tmp.append(math.asin((-math.sqrt(I_1)+math.sqrt(I_0))/(2*math.pi))+math.pi/2)
            
        adds_possible.append(tmp)
        add_phase(i, -delta)
    x = list()
    rec(x)
    if (abs(maximum_intensivity - prev)<=0.01):
        image, I_1 = simulate_laser()
        plt.imshow(image, extent = [-1, 1, -1, 1], cmap='hot', interpolation='nearest', origin="lower")
        plt.colorbar()
        plt.title("Финально сфазированный лазер")
        plt.show()
        exit(0)
    for i in range(0, len(phases)):
        phases[i] -= indexes[i]
    '''Идеальный вариант
    for i in range(len(phases)):
        add_phase(i, -phases[i])'''
    image, I_1 = simulate_laser() 
    plt.imshow(image, extent = [-1, 1, -1, 1], cmap='hot', interpolation='nearest', origin="lower")
    plt.colorbar()
    plt.title("Сфазированный лазер")
    plt.show()
    print("NOW: ", I_1) #Выводим текущую интенсивность в центре
    prev = I_1



