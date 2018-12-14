
import time
import logging
import lxml.html


import requests


from mysql.connector import MySQLConnection, Error

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

import re

list_database_product = None
change_list_database = True
count_add = 0
no_count_add = 0
list_many_optimization = []
count_many_optimization = 0



db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"
gpus = []
cpus = []
headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

urls_main = ["https://browser.geekbench.com/processor-benchmarks", "https://browser.geekbench.com/opencl-benchmarks"]

id_brenchmark_gpu = ""
id_brenchmark_cpu = ""


#Костыль, предназначен для удаления названия найденного блока, чтобы сохранить, например список с Html-тегами
def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

def request(url):
    global limit, headers
    while True:
        try:
            r = requests.get(url, headers=headers)
            log.info('Запрос: %s', url)
            if(r.status_code == 200):
                return r.text
            else:
                log.info("Ошибка статус:", r.status)
                time.sleep(1)
        except Exception as e:
            time.sleep(1)
            print("Ошибка:", e)

#метод преобзования ответа от сервера в дерево DOM
def get_html (request):
    return lxml.html.fromstring(request)

#Метод для вывода html, только для этапа разработки
def print_html(html):
    print(lxml.html.tostring(html, encoding='unicode', pretty_print=True))

def select_database(sql, data):
    try:
        conn = MySQLConnection(user = db_user, password = db_password, host = db_host, database = db_bd)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql, data)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print("Ошибка:", e)

def insert_database(sql, data):
    try:
        conn = MySQLConnection(user = db_user, password = db_password, host = db_host, database = db_bd)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql, data)
        lastrowid = cursor.lastrowid
        cursor.close()
        conn.close()
        return lastrowid
    except Error as e:
        print("Ошибка:", e)

def update_database(sql, data):
    try:
        conn = MySQLConnection(user = db_user, password = db_password, host = db_host, database = db_bd)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql, data)
        lastrowid = cursor.lastrowid
        cursor.close()
        conn.close()
        return lastrowid
    except Error as e:
        print("Ошибка:", e)

def get_cpu_benchmark_id(name):
    sql_query = "SELECT cpu_benchmark_id FROM cpu_benchmarks WHERE name = %s"
    data = (name,)
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        print("Отсутствует Id бенчмаркета в таблице.")
        exit(0)

def get_gpu_benchmark_id(source_name, test_name):
    sql_query = "SELECT gpu_benchmark_id FROM gpu_benchmarks WHERE source_name = %s and test_name = %s"
    data = (source_name, test_name)
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        print("Отсутствует Id бенчмаркета в таблице.")
        exit(0)

def add_cpu_benchmark_one_thread(cpu_id, id_benchmark, single_thread):

    sql_query = "SELECT row_id FROM cpu_benchmarks_values WHERE cpu_id = %s and cpu_benchmark_id = %s and single_core_value = %s LIMIT 1"
    data = (cpu_id, id_benchmark, single_thread)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "INSERT INTO cpu_benchmarks_values(cpu_id, cpu_benchmark_id, single_core_value) VALUES (%s, %s, %s)"
            return insert_database(sql_query, data)

def add_cpu_benchmark_multi_thread(cpu_id, id_benchmark, multi_thread):
    sql_query = "SELECT row_id FROM cpu_benchmarks_values WHERE cpu_id = %s and cpu_benchmark_id = %s and multi_core_value = %s LIMIT 1"
    data = (cpu_id, id_benchmark, multi_thread)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    elif(len(rows) == 0):

        sql_query = "SELECT row_id FROM cpu_benchmarks_values WHERE cpu_id = %s and cpu_benchmark_id = %s LIMIT 1"
        data = (cpu_id, id_benchmark)
        rows = select_database(sql_query, data)
        if(len(rows) == 1):
            sql_query = "UPDATE cpu_benchmarks_values SET multi_core_value = %s WHERE cpu_id = %s"
            data = (multi_thread, cpu_id)
            update_database(sql_query, data)
        else:
            if(len(rows) == 0):
                sql_query = "INSERT INTO cpu_benchmarks_values(cpu_id, cpu_benchmark_id, multi_core_value) VALUES (%s, %s, %s)"
                data = (cpu_id, id_brenchmark_cpu, multi_thread)
                return insert_database(sql_query, data)
            else:
                print("Ошибка")

def get_product_database(type):
    global id_brenchmark_gpu, id_brenchmark_cpu
    if(type == "gpu"):
        "(cpu_benchmarks_values.cpu_benchmark_id = %s and cpu_benchmarks_values.multi_core_value is null)"
        sql_query = "SELECT gpu.id, gpu.name from gpu LEFT JOIN gpu_benchmarks_values ON gpu.id = gpu_benchmarks_values.gpu_id WHERE gpu_benchmarks_values.gpu_benchmark_id != %s OR gpu_benchmarks_values.gpu_benchmark_id is null"
        data = (id_brenchmark_gpu, )
    if(type == "cpu"):
        sql_query = "SELECT cpu.id, cpu.name from cpu LEFT JOIN cpu_benchmarks_values ON cpu.id = cpu_benchmarks_values.cpu_id WHERE cpu_benchmarks_values.cpu_benchmark_id != %s OR cpu_benchmarks_values.cpu_benchmark_id is null OR cpu_benchmarks_values.multi_core_value is null"
        data = (id_brenchmark_cpu,)

    rows = select_database(sql_query, data)
    return rows

def add_gpu_benchmark(gpu_id, id_benchmark, mark):

    sql_query = "SELECT row_id FROM gpu_benchmarks_values WHERE gpu_id = %s and gpu_benchmark_id = %s and value = %s"
    data = (gpu_id, id_benchmark, mark)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "INSERT INTO gpu_benchmarks_values (gpu_id, gpu_benchmark_id, value) VALUES (%s, %s, %s)"
            return insert_database(sql_query, data)

def get_product_id(name, type):
    global list_database_product
    name_text = name
    if(type == "cpu"):
        sql_query = "SELECT id FROM cpu WHERE name = %s"
    else:
        if(type == "gpu"):
            sql_query = "SELECT id FROM gpu WHERE name = %s"

    data = (name_text,)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]

def parse(url):
    global id_brenchmark_cpu, id_brenchmark_gpu
    global count_add, no_count_add
    r = request(url)
    html = get_html(r)

    tbodies = html.cssselect('tbody')
    if(len(tbodies) == 2):
        type = "cpu"
    else:
        type = "gpu"
    for index, tbody in enumerate(tbodies):
        trs = tbody.cssselect('tr')
        for tr in trs:
            if(type == "gpu"):
                tr_div = tr.cssselect('td.name>div')[0]
                tr_div.tail
                name = tr.cssselect('td.name')[0].text.strip()
                value = tr.cssselect('td.score')[0].text.strip()
                id_product = get_product_id(name, type)
                if (id_product != None):
                    count_add += 1
                    add_gpu_benchmark(id_product, id_brenchmark_gpu, value)
                else:
                    id_product = search_best_conformity(name, type)
                    if (id_product != None):
                        count_add += 1
                        add_gpu_benchmark(id_product, id_brenchmark_gpu, value)

                    else:
                        no_count_add += 1
                        gpus.append([name, value])
            else:
                if(type == "cpu"):
                    single_core_value = ""
                    multi_core_value = ""
                    name = tr.cssselect('td.name>a')[0].text.strip()
                    if(name.find("/") != -1):
                        name_list = name_in_list(name)
                    else:
                        name_list = [name]
                    for name in name_list:
                        id_product = get_product_id(name, type)
                        if (id_product != None):
                            count_add += 1
                            if (index == 0):
                                single_core_value = tr.cssselect('td.score')[0].text.strip()
                                id_cpu_brenchmark_value_one = add_cpu_benchmark_one_thread(id_product, id_brenchmark_cpu,
                                                                                           single_core_value)

                            else:
                                if (index == 1):
                                    multi_core_value = tr.cssselect('td.score')[0].text.strip()
                                    id_cpu_brenchmark_value_multi = add_cpu_benchmark_multi_thread(id_product,
                                                                                                   id_brenchmark_cpu,
                                                                                                   multi_core_value)
                        else:
                            id_product = search_best_conformity(name, type)
                            if (id_product != None):
                                count_add += 1
                                if (index == 0):
                                    single_core_value = tr.cssselect('td.score')[0].text.strip()
                                    id_cpu_brenchmark_value_one = add_cpu_benchmark_one_thread(id_product, id_brenchmark_cpu,
                                                                                               single_core_value)

                                else:
                                    if (index == 1):
                                        multi_core_value = tr.cssselect('td.score')[0].text.strip()
                                        id_cpu_brenchmark_value_multi = add_cpu_benchmark_multi_thread(id_product,
                                                                                                       id_brenchmark_cpu,
                                                                                                       multi_core_value)
                            else:
                                no_count_add += 1
                                cpus.append([name, single_core_value, multi_core_value])

def name_in_list(text):
    new_list = []
    text_list = text.split("/")
    index_left = text_list[0].rfind(" ")
    index_rigth = text_list[-1].find(" ")
    text_left = text_list[0][:index_left + 1]
    text_right = text_list[-1][index_rigth :]

    if (index_rigth == -1):
        index_rigth = len(text_list[-1])
        text_right = ""
    for index, item in enumerate(text_list):
        # print("rgirg", item)
        if(index == 0):
            new_list.append(item + text_right)
        else:
            if index == (len(text_list) - 1):
                new_list.append(text_left + item)
            else:
                new_list.append(text_left + item + text_right)
    return new_list



def optimization(item):
    if(item.find("(Desktop)") != -1):
        item = item.replace("(Desktop)", "")


    text = re.search("PRO\s[0-9]{4}$", item)
    if (text != None):
        item = item.replace(text.group(0), text.group(0)[-5:-1]+" PRO")
    text = re.search("Graphics$", item)
    if (text != None):
        item = item.replace(text.group(0), "")
    text = re.search("[+]$", item)
    if (text != None):
        item = item.replace(text.group(0), "")
    if (item.find("Mobility Pro Graphics") != -1):
            item = item.replace("Mobility Pro Graphics", "")
    if (item.find("FireGL V") != -1):
            item = item.replace("FireGL V", "")
    if (item.find("(TM)") != -1):
        item = item.replace("(TM)", "")
    if (item.find("(R)") != -1):
        item = item.replace("(R)", "")
    if (item.find("Black Edition") != -1):
        item = item.replace("Black Edition", "BE")
    if (item.find("V-Series") != -1):
        item = item.replace("V-Series", "")
    if (item.find("Compute Engine") != -1):
        item = item.replace("Compute Engine", "")
    if (item.find("Graphics Adapter") != -1):
        item = item.replace("Graphics Adapter", "")

    #cpu
    if (item.find("Processor") != -1):
        item = item.replace("Processor", "")
    if (item.find("Gold") != -1):
        item = item.replace("Gold", "")
    if (item.find("with") != -1):
        item = item.replace("with", "")
    if (item.find("Design") != -1):
        item = item.replace("Design", "")



    if (item.find("-") != -1):
        item = item.replace("-", "") #?
    if (item.find(" ") != -1):
        item = item.replace(" ", "")
    if (item.find("(") != -1):
        item = item.replace("(", "")
    if (item.find(")") != -1):
        item = item.replace(")", "")

    item = item.lower()
    if (item.find("series") != -1):
        item = item.replace("series", "")
    if (item.find("gtx") != -1):
        item = item.replace("gtx", "")
    if (item.find("nvidia") != -1):
        item = item.replace("nvidia", "")
    if (item.find("amd") != -1):
        item = item.replace("amd", "")
    if (item.find("intel") != -1):
        item = item.replace("intel", "")
    if (item.find("radeon") != -1):
        item = item.replace("radeon", "")

    return item

def search_best_conformity(product, type):
    global list_many_optimization
    global change_list_database, list_database_product
    # if(change_list_database):
    list_database_product = get_product_database(type)
    change_list_database = False

    name_product_list = [i[1] for i in list_database_product]
    index_product_list = [i[0] for i in list_database_product]
    list_new = []
    for name in name_product_list:
        list_new.append(optimization(name))
    new_product = optimization(product)
    count_optimization = 0
    memory_index = -1
    many_optimization = []
    for index, new in enumerate(list_new):
        # print(new,"---", new_product)
        if(new == new_product):
            many_optimization.append(name_product_list[index])
            count_optimization += 1
            memory_index = index
    if(count_optimization == 1):
        print("Оптимизировалось:", name_product_list[memory_index], index_product_list[memory_index])
        change_list_database = True
        return index_product_list[memory_index]
    if(count_optimization > 0):
        global count_many_optimization
        count_many_optimization+= 1
        list_many_optimization.append(many_optimization)





def main():
    global cpus, id_brenchmark_gpu, id_brenchmark_cpu, list_many_optimization, count_many_optimization, count_add, no_count_add, change_list_database
    start_time = time.time()
    id_brenchmark_gpu = get_gpu_benchmark_id("Geekbench", "OpenCL")
    id_brenchmark_cpu = get_cpu_benchmark_id("Geekbench 4")
    print("Идентификатор бенчмаркета:", id_brenchmark_gpu)
    print("Идентификатор бенчмаркета:", id_brenchmark_cpu)
    for url_main in urls_main:
        change_list_database = True
        parse(url_main)

        print("Количество add:", count_add)
        print("Количество no_add:", no_count_add)
        print("Количество 2 и более значений:", count_many_optimization)
        for list_many_optimization in list_many_optimization:
            print(list_many_optimization)

        count_add = 0
        count_many_optimization = 0
        no_count_add = 0
    print("------------------------Недобавленные  GPUS-----------------------------")
    for gpu in gpus:
        print(gpu)
    print("------------------------Недобавленные  CPUS-----------------------------")
    for cpu in cpus:
        print(cpu)
    print("Время работы:", time.time() - start_time)


if __name__ == '__main__':
    main()
