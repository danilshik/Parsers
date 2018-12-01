import pandas as pd
import time
from itertools import groupby
from collections import defaultdict
from glob import  glob
import os
#Каталог из которого будем брать изображения
directory = 'data'


def open(directory):
    os.chdir(directory)
    files = glob('*.xlsx')
    files.extend(glob('*.csv'))
    for file in files:
        processing(file)

def is_positive_negative_or_zero(n):
    if n[0] - n[1] > 0: return 1
    if n[0] - n[1] < 0: return -1
    return 0

def processing(fileinput):
    count_zero_global = 0
    count_ups_global = 0
    count_downs_global = 0

    start = time.time()

    d = defaultdict(list)

    print("Открытие файла", fileinput)
    if(fileinput.find("xlsx") != -1):
        data = pd.read_excel(fileinput)
    else:
        if(fileinput.find("csv") != -1):
            data = pd.read_csv(fileinput, delimiter=";")

    rows = data.values
    len_rows = len(rows)
    print("Количество строчек:", len_rows)


    for k, g in groupby(rows, key=is_positive_negative_or_zero):
        d[len(list(g))].append(k)

    items = sorted(d.items())

    for item in items:
        count_zero = 0
        count_ups = 0
        count_downs = 0
        values = item[1]
        for value in values:
            if value == -1:
                count_ups += 1
            else:
                if (value == 1):
                    count_downs += 1
                else:
                    count_zero += 1


        count_downs_global += count_downs
        count_zero_global += count_zero
        count_ups_global += count_ups
    for item in items:
        count_zero = 0
        count_ups = 0
        count_downs = 0
        key = item[0]
        values = item[1]
        for value in values:
            if value == -1:
                count_ups += 1
            else:
                if(value == 1):
                    count_downs += 1
                else:
                    count_zero += 1
        sum = count_downs + count_zero + count_ups
        if(count_ups_global == 0):
            print(str(key) + " UP: "+str(count_ups)+"("+ "{:.2%}".format(count_ups/len_rows)+")", "DOWN : "+str(count_downs) + "("+ "{:.2%}".format(count_downs/len_rows)+"-" + "{:.2%}".format(count_downs/count_downs_global)+ ")","ZERO :" + str(count_zero) + "("+ "{:.2%}".format(count_zero/len_rows)+ " - "+ "{:.2%}".format(count_zero/count_zero_global) + ")", "Всего:", str(sum))
        else:
            if(count_downs_global == 0):
                print(str(key) + " UP: "+str(count_ups)+"("+ "{:.2%}".format(count_ups/len_rows)+ "-" + "{:.2%}".format(count_ups/count_ups_global) +")", "DOWN : "+str(count_downs) + "("+ "{:.2%}".format(count_downs/len_rows)+ ")","ZERO :" + str(count_zero) + "("+ "{:.2%}".format(count_zero/len_rows)+ " - "+ "{:.2%}".format(count_zero/count_zero_global) + ")", "Всего:", str(sum))
            else:
                if(count_zero_global == 0):
                    print(str(key) + " UP: "+str(count_ups)+"("+ "{:.2%}".format(count_ups/len_rows)+ "-" + "{:.2%}".format(count_ups/count_ups_global) +")", "DOWN : "+str(count_downs) + "("+ "{:.2%}".format(count_downs/len_rows)+"-" + "{:.2%}".format(count_downs/count_downs_global)+ ")","ZERO :" + str(count_zero) + "("+ "{:.2%}".format(count_zero/len_rows) + ")", "Всего:", str(sum))
                else:
                    print(str(key) + " UP: "+str(count_ups)+"("+ "{:.2%}".format(count_ups/len_rows)+ "-" + "{:.2%}".format(count_ups/count_ups_global) +")", "DOWN : "+str(count_downs) + "("+ "{:.2%}".format(count_downs/len_rows)+"-" + "{:.2%}".format(count_downs/count_downs_global)+ ")","ZERO :" + str(count_zero) + "("+ "{:.2%}".format(count_zero/len_rows)+ " - "+ "{:.2%}".format(count_zero/count_zero_global) + ")", "Всего:", str(sum))
    print("Время обработки файла:", fileinput, time.time() - start)



if __name__ == '__main__':
    start_time = time.time()
    open(directory)
    print("Общее время выполнение скрипта:", time.time() - start_time)