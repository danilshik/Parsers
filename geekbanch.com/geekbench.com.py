
import time
import logging
import lxml.html


import requests


from mysql.connector import MySQLConnection, Error

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import difflib
import csv
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

error_cpu = []
error_gpu = []
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
    sql_query = "SELECT name, id FROM gpu"
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
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        if(len(rows)==0):
            sql_query = "INSERT INTO cpu_benchmark (name) VALUES(%s)"
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

def add_cpu_benchmark_one_thread(cpu_id, id_benchmark, single_thread):

    sql_query = "SELECT id FROM cpu_benchmark_value WHERE cpu_id = %s and cpu_benchmark_id = %s and single_core_value = %s LIMIT 1"
    data = (cpu_id, id_benchmark, single_thread)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "INSERT INTO cpu_benchmark_value(cpu_id, cpu_benchmark_id, single_core_value) VALUES (%s, %s, %s)"
            return insert_database(sql_query, data)

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
    else:
        if(len(rows) == 0):
            name_list = []
            for i in range(len(name) + 1):
                for index in range(0, i):
                    name_text = (name[index:i])
                    name_list.append(name_text)
            name_list = sorted(name_list, reverse=True, key=len)
            for name_text in name_list:
                data = (name_text,)
                rows = select_database(sql_query, data)
                if(len(rows) == 1):
                    return rows[0][0]
                else:
                    if (type == "cpu"):
                        sql_query = "SELECT id FROM cpu WHERE name LIKE %s"
                    else:
                        if (type == "gpu"):
                            sql_query = "SELECT id FROM gpu WHERE name LIKE %s"
                    data = ("%" + name_text + "%",)
                    rows = select_database(sql_query, data)
                    if (len(rows) == 1):
                        return rows[0][0]




def parse(url):
    global id_brenchmark_cpu, id_brenchmark_gpu
    r = request(url)
    html = get_html(r)

    tbodies = html.cssselect('tbody')
    print(len(tbodies))
    if(len(tbodies) == 2):
        type = "cpu"
    else:
        type = "gpu"
    for index, tbody in enumerate(tbodies):
        trs = tbody.cssselect('tr')
        print(len(trs))
        for tr in trs:
            if(type == "gpu"):
                tr_div = tr.cssselect('td.name>div')[0]
                tr_div.tail
                name = tr.cssselect('td.name')[0].text.strip()
                value = tr.cssselect('td.score')[0].text.strip()
                gpus.append([name, value])
                # id_gpu = get_product_id(name, type)
                # if(id_gpu != None):
                #     id_gpu_brenchmark_value = add_gpu_benchmark(id_gpu, id_brenchmark_gpu, value)
                #     log.info("%s, %s, %s", id_gpu, name, value)
                # else:
                #     error_gpu.append(name)

            else:
                if(type == "cpu"):
                    single_core_value = ""
                    multi_core_value = ""
                    name = tr.cssselect('td.name>a')[0].text.strip()
            #         id_cpu = get_product_id(name, type)
            #
            #         if(id_cpu != None):
                    if(index == 0):
                        single_core_value = tr.cssselect('td.score')[0].text.strip()
                        # id_cpu_brenchmark_value_one = add_cpu_benchmark_one_thread(id_cpu, id_brenchmark_cpu, single_core_value)
                        # log.info("%s, %s, %s", id_cpu, name, single_core_value)

                    else:
                        if(index == 1):
                            multi_core_value = tr.cssselect('td.score')[0].text.strip()
                            # id_cpu_brenchmark_value_multi = add_cpu_benchmark_multi_thread(id_cpu, id_brenchmark_cpu,
                            #                                                            multi_core_value)
                            # log.info("%s, %s, %s", id_cpu, name, multi_core_value)

                    temp = [name, single_core_value, multi_core_value]
                    cpus.append(temp)

            #         else:
            #             error_cpu.append(name)









def main():
    for url_main in urls_main:
        parse(url_main)
    global cpus, gpus
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
    # gpus_name = []
    # for gpu in gpus:
    #     gpus_name.append(gpu[0])
    #
    # gpus_database = get_gpu_database()
    # test = []
    #
    # for gpu_database in gpus_database:
    #     max = 0
    #     max_value = ""
    #     # print(gpu_database[0], "-", difflib.get_close_matches(gpu_database[0], gpus_name))
    #     for gpu_name in gpus_name:
    #         ratio = fuzz.ratio(gpu_database[0], gpu_name)
    #         print(ratio, gpu_name)
    #         if(ratio>max):
    #             max = ratio
    #             max_value =  gpu_name
    #     test.append([gpu_database, max, max_value])
    # for tes in test:
    #     print(tes)
    #     # products = print(gpu_database[0], "-", max(process.extract(gpu_database[0], gpus_name)))

    import csv
    #
    with open("geekbranch_gpu.com.txt", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(gpus)
    with open("geckbranch_cpu.com.txt", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(cpus)



if __name__ == '__main__':
    start_time = time.time()
    id_brenchmark_gpu = get_gpu_benchmark_id("Geekbench", "OpenCL")
    id_brenchmark_cpu = get_cpu_benchmark_id("Geekbench 4")
    main()
