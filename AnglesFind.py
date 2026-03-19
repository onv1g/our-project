import math
import json
#работает для любого количества точек внутри массивов координат => для любого количества сегментов
firstx_arr = [2] #массив для координаты х1

secondx_arr = [5] #массив для координаты x2

firsty_arr = [2] #массив для координаты y1

secondy_arr = [6] #массив для координаты y2

def tangles2(firstx_arr, secondx_arr, firsty_arr, secondy_arr):
    pre_final = []
    if len(secondy_arr) == 1:
        if firstx_arr[0] == secondx_arr[0]:
            pre_final.append(180)
        elif firsty_arr[0] == secondy_arr[0]:
            pre_final.append(90)
        else:
            tan = ((secondy_arr[0]) - (firsty_arr[0])) // ((secondx_arr[0]) - (firstx_arr[0])) #тот же процесс что ниже только для случая когда разлом состоит из одного сегмента
            tangle = abs(math.degrees(math.atan(tan)))
            rounded = math.floor(tangle)
            pre_final.append(rounded)
    else:
        for i in range(-1, len(secondy_arr)-1):
            if firstx_arr[i+1] == secondx_arr[i+1]:
                pre_final.append(180)
            elif firsty_arr[i+1] == secondy_arr[i+1]:
                pre_final.append(90)
            else:
                tan = ((secondy_arr[i+1]) - (firsty_arr[i+1])) // ((secondx_arr[i+1]) - (firstx_arr[i+1])) #нахождение сторон треугольника разностью координат затем отношение сторон(тангенс) затем арктангенс который и является углом
                tangle = abs(math.degrees(math.atan(tan))) #модуль и первод угла из радианов в градусы
                rounded = math.floor(tangle) #округление угла до целого
                pre_final.append(rounded) #добавление i'того угла в массив всех углов внутри одного разлома
    final_result = math.floor(sum(pre_final) / len(pre_final))  #среднее арифметическое углов в разломе => финальный угол для любого количества сегментов
    return final_result


YOUR_DATA = [
    # Группа 1 (один сегмент)
    [tangles2(firstx_arr, secondx_arr, firsty_arr, secondy_arr), [firstx_arr[0], secondx_arr[0], firsty_arr[0], secondy_arr[0], tangles2(firstx_arr, secondx_arr, firsty_arr, secondy_arr)]],

    # # Группа 2 (один сегмент)
    # [45, [21, 31, 70, 50, 45]],
    #
    # # Группа 3 (два сегмента)
    # [47, [21, 31, 70, 50, 45], [70, 50, 79, 60, 50]],
    # # [50, [10, 10, 30, 20, 45]],                    # один сегмент
    # # [52, [0, 0, 25, 15, 48], [25, 15, 50, 30, 52]], # два сегмента
    # # [55, [5,5,15,15,45], [15,15,30,25,50], [30,25,45,35,55]], # три сегмента
]

def generate_json(data, filename):
    result = {}
    for i, gap in enumerate(data, 1):
        gap_data = {
            "number_of_the_gap": i,
            "final_beta": gap[0]
        }
        for j, segment in enumerate(gap[1:], 1):
            x1, y1, x2, y2, beta = segment
            gap_data[f"segment{j}"] = {
                "number": j,
                "beta": beta,
                "x_1": x1,
                "y_1": y1,
                "x_2": x2,
                "y_2": y2
            }
        result[f"gap_{i}"] = gap_data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)



generate_json(YOUR_DATA, 'gaps.json')
