import math
#работает для любого количества точек внутри массивов координат => для любого количества сегментов
firstx_arr = [2] #массив для координаты х12

secondx_arr = [2] #массив для координаты x25

firsty_arr = [5] #массив для координаты y12

secondy_arr = [6] #массив для координаты y26

def tangles2(firstx_arr, secondx_arr, firsty_arr, secondy_arr):
    pre_final = []
    if len(secondy_arr) == 1:
        if firstx_arr[0] == secondx_arr[0] == firsty_arr[0] == secondy_arr[0]:
            print(" Такого угла не существует ")
        elif firstx_arr[0] == secondx_arr[0]:
            print(90)
        elif firsty_arr[0] == secondy_arr[0]:
            print(0)
        else:
            tan = ((secondy_arr[0]) - (firsty_arr[0])) // ((secondx_arr[0]) - (firstx_arr[0])) #тот же процесс что ниже только для случая когда разлом состоит из одного сегмента
            tangle = abs(math.degrees(math.atan(tan)))
            rounded = math.floor(tangle)
            pre_final.append(rounded)
    elif len(secondy_arr) != 1:
        for i in range(-1, len(secondy_arr)-1):
            if firstx_arr[i+1] == secondx_arr[i+1] == firsty_arr[i+1] == secondy_arr[i+1]:
                print(" Такого угла не существует ")
            elif firstx_arr[i+1] == secondx_arr[i+1]:
                print(90)
            elif firsty_arr[i+1] == secondy_arr[i+1]:
                print(0)
            else:
                tan = ((secondy_arr[i+1]) - (firsty_arr[i+1])) // ((secondx_arr[i+1]) - (firstx_arr[i+1])) #нахождение сторон треугольника разностью координат затем отношение сторон(тангенс) затем арктангенс который и является углом
                tangle = abs(math.degrees(math.atan(tan))) #модуль и первод угла из радианов в градусы
                rounded = math.floor(tangle) #округление угла до целого
                pre_final.append(rounded) #добавление i'того угла в массив всех углов внутри одного разлома
    final_result = math.floor(sum(pre_final) / len(pre_final))  #среднее арифметическое углов в разломе => финальный угол для любого количества сегментов
    print(final_result)


tangles2(firstx_arr, secondx_arr, firsty_arr, secondy_arr)

