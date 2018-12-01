import os
import time
import logging
import lxml.html
from collections import OrderedDict
import csv
import requests

from contextlib import suppress
from mysql.connector import MySQLConnection, Error

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

count_add = 0
no_count_add = 0

db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"
headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

urls_main = ["https://benchmarks.ul.com/compare/best-cpus", "https://benchmarks.ul.com/compare/best-gpus"]

id_brenchmark_gpu = ""
id_brenchmark_cpu = ""

gpus = []
cpus = []

name_list = []
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
        exit(0)

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
    sql_query = "SELECT id FROM cpu_benchmark WHERE name = %s"
    data = (name,)
    sql_query = "INSERT INTO cpu_benchmark (name) VALUES(%s)"
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        if(len(rows)==0):
            return insert_database(sql_query, data)
        else:
            print("Неизвестная ошибка БД. Остановка программы.")
            print(len(rows))
            exit(0)

def get_gpu_benchmark_id(source_name, test_name):
    sql_query = "SELECT id FROM gpu_benchmark WHERE source_name = %s and test_name = %s"
    data = (source_name, test_name)
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        if(len(rows)==0):
            sql_query = "INSERT INTO gpu_benchmark (source_name, test_name) VALUES(%s, %s)"
            return insert_database(sql_query, data)
        else:
            print("Неизвестная ошибка БД. Остановка программы.")
            print(len(rows))
            exit(0)



def add_cpu_benchmark_multi_thread(cpu_id, id_benchmark, multi_thread):

    sql_query = "SELECT id FROM cpu_benchmark_value WHERE cpu_id = %s and cpu_benchmark_id = %s and multi_core_value = %s LIMIT 1"
    data = (cpu_id, id_benchmark, multi_thread)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "SELECT id FROM cpu_benchmark_value WHERE cpu_id = %s and cpu_benchmark_id = %s LIMIT 1"
            data = (cpu_id, id_benchmark)
            rows = select_database(sql_query, data)
            if(len(rows) == 1):
                sql_query = "UPDATE cpu_benchmark_value SET multi_core_value = %s WHERE id = %s"
                data = (multi_thread, cpu_id)
                return update_database(sql_query, data)
            else:
                if(len(rows) == 0):
                    sql_query = "INSERT INTO cpu_benchmark_value(cpu_id, cpu_benchmark_id, multi_core_value) VALUES (%s, %s, %s)"
                    data = (cpu_id, id_brenchmark_cpu, multi_thread)
                    return insert_database(sql_query, data)
def get_cpu_database():
    sql_query = "SELECT name,id FROM cpu"
    try:
        conn = MySQLConnection(user = db_user, password = db_password, host = db_host, database = db_bd)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print("Ошибка:", e)
        exit(0)

def get_gpu_database():
    sql_query = "SELECT name, id FROM gpu "
    try:
        conn = MySQLConnection(user = db_user, password = db_password, host = db_host, database = db_bd)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print("Ошибка:", e)
        exit(0)

def add_gpu_benchmark(gpu_id, id_benchmark, mark):

    sql_query = "SELECT id FROM gpu_benchmark_value WHERE gpu_id = %s and gpu_benchmark_id = %s and value = %s "
    data = (gpu_id, id_benchmark, mark)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "INSERT INTO gpu_benchmark_value (gpu_id, gpu_benchmark_id, value) VALUES (%s, %s, %s)"
            return insert_database(sql_query, data)

def get_product_id(name, type):
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
def search_best():
    print()
def parse(url):
    global  count_add, no_count_add
    r = request(url)
    html = get_html(r)
    text_type = html.cssselect('h1')[0].text
    if(text_type.find('Processors') != -1):
        type = "cpu"
    else:
        if(text_type.find('Graphics') != -1):
            type = "gpu"
    trs = html.cssselect('tbody>tr')
    for tr in trs:
        tds = tr.cssselect('td')

        name = tds[1].cssselect('a')[0].text

        value = tds[3].cssselect('div>div>span')[0].text.strip()
        if(type == "gpu"):
            id_product = get_product_id(name, type)
            if (id_product != None):
                count_add += 1
                add_gpu_benchmark(id_product, id_brenchmark_gpu, value)
            else:
                no_count_add += 1
                gpus.append([name, value])
        else:
            if(type == "cpu"):
                # id_product = get_product_id(name, type)
                # if (id_product != None):
                #     count_add += 1
                #
                # else:
                #     no_count_add += 1
                # print(name)
                cpus.append([name, value])


def get_database_gpus():
    sql = "SELECT gpu.id, gpu.name FROM gpu, gpu_benchmark_value WHERE gpu.id = gpu_becnhmark_value.gpu_id"

def main():
    global cpus
    for url_main in urls_main:
        parse(url_main)
    print("Количество add:", count_add)
    print("Количество no_add:", no_count_add)
    # cpus_name = []
    # for cpu in cpus:
    #     cpus_name.append(cpu[0])
    #
    # # print(cpus_name)
    #
    # cpus_database = get_cpu_database()
    # test = []
    #
    # for cpu_database in cpus_database:
    #     # print(cpus_database[0])
    #     test.append(cpu_database[0])
    # print(test)
    #     products = print(max(process.extract(cpu_database[0], cpus_name)))
    # with open("benchmark_gpu.net.txt", "w", newline="") as file:
    #     writer = csv.writer(file)
    #     writer.writerows(gpus)
    # with open("benchmark_cpu.net.txt", "w", newline="") as file:
    #     writer = csv.writer(file)
    #     writer.writerows(cpus)

    # gpus_database = get_gpu_database()
    # test = []

    # for gpu_database in gpus_database:
    #     print(gpu_database[0], "-", difflib.get_close_matches(gpu_database[0], gpus_name))
        # products = print(gpu_database[0], "-", max(process.extract(gpu_database[0], gpus_name)))
    # print(test)






if __name__ == '__main__':
    start_time = time.time()
    id_brenchmark_gpu = get_gpu_benchmark_id("3D Mark", "Graphics Score")
    print(id_brenchmark_gpu)
    # id_brenchmark_cpu = get_cpu_benchmark_id("3DMark Physics Score")

    main()
    for gpu in gpus:
        print(gpu)



    print("Время работы:", time.time() - start_time)