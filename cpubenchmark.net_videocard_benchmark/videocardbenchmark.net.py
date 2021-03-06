import time
import logging
from mysql.connector import MySQLConnection, Error
from selenium import webdriver
from selenium.common.exceptions import *
import re

db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

list_database_product = None
change_list_database = True
count_add = 0
count_no_add = 0
list_many_optimization = []
count_many_optimization = 0

all = []
id_brenchmark_gpu = ""
id_brenchmark_cpu = ""

gpus = []
url_main = ["https://www.videocardbenchmark.net/GPU_mega_page.html"]
id_G3D_mark = None
id_G2D_mark = None


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

def get_gpu_benchmark_id(source_name, test_name):
    sql_query = "SELECT gpu_benchmark_id FROM gpu_benchmarks WHERE source_name = %s and test_name = %s"
    data = (source_name, test_name)
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        print("Отсутствует Id бенчмаркета в таблице.")
        exit(0)
        # if(len(rows)==0):
        #     sql_query = "INSERT INTO gpu_benchmarks (source_name, test_name) VALUES(%s, %s)"
        #     return insert_database(sql_query, data)
        # else:
        #     print("Неизвестная ошибка БД. Остановка программы.")
        #     print(len(rows))
        #     exit(0)

def get_product_database(type):
    global id_brenchmark_gpu
    if(type == "gpu"):
        sql_query = "SELECT gpu.id, gpu.name from gpu LEFT JOIN gpu_benchmarks_values ON gpu.id = gpu_benchmarks_values.gpu_id WHERE gpu_benchmarks_values.gpu_benchmark_id != %s OR gpu_benchmarks_values.gpu_benchmark_id is null"
        data = (id_brenchmark_gpu,)
        rows = select_database(sql_query, data)
        return rows

def get_product_id(name, type):
    global list_database_product
    name_text = name
    if(type == "cpu"):
        sql_query = "SELECT id FROM gpu WHERE name = %s"
    else:
        if(type == "gpu"):
            sql_query = "SELECT id FROM gpu WHERE name = %s"

    data = (name_text,)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]


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

def optimization(item):
    # if (item.find("APU") != -1):
    #     item = item.replace("APU", "")
    text = re.search("IGP$", item)
    if (text != None):
        item = item.replace(text.group(0), "")
    # text = re.search("[a-zA-Z]{3,}-Core", item)
    # if (text != None):
    #     item = item.replace(text.group(0), "")
    # text = re.search("^Mobile", item)
    # if (text != None):
    #     item = item.replace(text.group(0), "")
    #
    # text = re.search("SOC$", item)
    # if (text != None):
    #     item = item.replace(text.group(0), "")
    #
    # text = re.search("Athlon Dual Core [0-9]{4}[a-zA-Z]", item)
    # if (text != None):
    #     item = item.replace(text.group(0), "")
    # text = re.search("[+]$", item)
    # if (text != None):
    #     item = item.replace(text.group(0), "")
    # if (item.find("Mobility Pro Graphics") != -1):
    #         item = item.replace("Mobility Pro Graphics", "")
    # if (item.find("FireGL V") != -1):
    #         item = item.replace("FireGL V", "")
    # if (item.find("(TM)") != -1):
    #     item = item.replace("(TM)", "")
    # if (item.find("(R)") != -1):
    #     item = item.replace("(R)", "")
    # if (item.find("Black Edition") != -1):
    #     item = item.replace("Black Edition", "BE")
    # if (item.find("V-Series") != -1):
    #     item = item.replace("V-Series", "")
    # if (item.find("Compute Engine") != -1):
    #     item = item.replace("Compute Engine", "")
    if (item.find("Adapter") != -1):
        item = item.replace("Adapter", "")
    #
    # #cpu
    # if (item.find("Processor") != -1):
    #     item = item.replace("Processor", "")
    # if (item.find("Gold") != -1):
    #     item = item.replace("Gold", "")
    # if (item.find("Dual Core") != -1):
    #     item = item.replace("Dual Core", "X2") ##
    # if (item.find("Mobile") != -1):
    #     item = item.replace("Mobile", "")
    if(item.find("with") != -1):
        item = item.replace("with", "")
    if (item.find("Design") != -1):
        item = item.replace("Design", "") #?
    if (item.find("ATI") != -1):
        item = item.replace("ATI", "") #?
    if (item.find("Graphics") != -1):
        item = item.replace("Graphics", "") #?
    if (item.find("GMA") != -1):
        item = item.replace("GMA", "") #?
    if (item.find("Family") != -1):
        item = item.replace("Family", "")

    if (item.find("-") != -1):
        item = item.replace("-", "") #?
    if (item.find(" ") != -1):
        item = item.replace(" ", "")
    if (item.find("(") != -1):
        item = item.replace("(", "")
    if (item.find(")") != -1):
        item = item.replace(")", "")
    if (item.find("+") != -1):
        item = item.replace("+", "")

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
    # if (item.find("radeon") != -1):
    #     item = item.replace("radeon", "")

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


def init_driver():
    ff = "../install/chromedriver.exe"
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument("headless")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_option.add_experimental_option("prefs", prefs)


    try:
        # driver = webdriver.Firefox(executable_path=ff)
        driver = webdriver.Chrome(executable_path=ff, chrome_options=chrome_option)
        # driver = webdriver.Chrome(executable_path=ff, chrome_options=chrome_option, service_args=service_args)
    except SessionNotCreatedException:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера")

    return driver



def parse(url):
    global count_gpu
    global count_add, count_no_add, count_gpus, id_G2D_mark,id_G3D_mark

    print("Запуск браузера")
    driver = init_driver()
    print("Переход на страницу:", url)
    driver.get(url)
    trs = driver.find_elements_by_css_selector('table>tbody>tr[style = "display: table-row;"')
    count_gpu = len(trs)
    for index, tr in enumerate(trs):
        tds = tr.find_elements_by_css_selector('td')
        name_gpu = tds[0].find_elements_by_css_selector('a')[1].text

        G3D_Mark = float(tds[2].text)
        G2D_Mark = float(tds[4].text)

        id_product = get_product_id(name_gpu, "gpu")
        if (id_product != None):
            add_gpu_benchmark(id_product, id_G3D_mark, G3D_Mark)
            add_gpu_benchmark(id_product, id_G2D_mark, G2D_Mark)
            count_add += 1
            print("Добавлен в БД:", [id_product, id_brenchmark_gpu, G3D_Mark])
            print("Добавлен в БД:", [id_product, id_brenchmark_gpu, G2D_Mark])
        else:
            id_product = search_best_conformity(name_gpu, "gpu")
            if (id_product != None):
                add_gpu_benchmark(id_product, id_G3D_mark, G3D_Mark)
                add_gpu_benchmark(id_product, id_G2D_mark, G2D_Mark)
                count_add += 1
                print("Добавлен в БД:", [id_product, id_G3D_mark, G3D_Mark])
                print("Добавлен в БД:", [id_product, id_G2D_mark, G2D_Mark])
            else:
                count_no_add += 1
                gpus.append([name_gpu])
                print("Добавлен в список недобавленных:", [name_gpu, G3D_Mark, G2D_Mark])




    driver.close()


def main():
    global gpus, id_brenchmark_gpu, list_many_optimization, count_many_optimization, count_add, count_no_add, change_list_database, id_G3D_mark, id_G2D_mark
    id_G3D_mark = int(get_gpu_benchmark_id("PassMark", "G3D Mark"))
    print("ID G3D_mark:", id_G3D_mark)
    id_G2D_mark = int(get_gpu_benchmark_id("PassMark", "G2D Mark"))
    print("ID G2D_mark:", id_G2D_mark)
    start_time = time.time()
    for url in url_main:
        change_list_database = True
        parse(url)

        #
        # for list_many_optimization in list_many_optimization:
        #     print(list_many_optimization)


    print("------------------------Недобавленные  GPUS-----------------------------")
    for gpu in gpus:
        print(gpu)
    print("Количество add:", count_add)
    print("Количество no_add:", count_no_add)
    print("Количество 2 и более значений:", count_many_optimization)
    print("Время работы:", time.time() - start_time)



if __name__ == '__main__':
    main()
