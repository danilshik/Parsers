from mysql.connector import MySQLConnection, Error
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.support.select import Select
import re
import time
import logging
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


url_main = ["https://www.notebookcheck.net/Computer-Games-on-Laptop-Graphics-Cards.13849.0.html"]

cpus = []


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



def get_product_database(type):
    global id_brenchmark_cpu
    if(type == "cpu"):
        sql_query = "SELECT cpu.id, cpu.name from cpu LEFT JOIN cpu_benchmarks_values ON cpu.id = cpu_benchmarks_values.cpu_id WHERE cpu_benchmarks_values.cpu_benchmark_id != %s OR cpu_benchmarks_values.cpu_benchmark_id is null"
        data = (id_brenchmark_cpu,)
        rows = select_database(sql_query, data)
        return rows




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



def optimization(item):
    if (item.find("APU") != -1):
        item = item.replace("APU", "")
    text = re.search("@\s[0-9].[0-9]{2}GHz", item)
    if (text != None):
        item = item.replace(text.group(0), "")
    text = re.search("[a-zA-Z]{3,}-Core", item)
    if (text != None):
        item = item.replace(text.group(0), "")
    text = re.search("^Mobile", item)
    if (text != None):
        item = item.replace(text.group(0), "")

    text = re.search("SOC$", item)
    if (text != None):
        item = item.replace(text.group(0), "")

    text = re.search("Athlon Dual Core [0-9]{4}[a-zA-Z]", item)
    if (text != None):
        item = item.replace(text.group(0), "")
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
    # if (item.find("Graphics Adapter") != -1):
    #     item = item.replace("Graphics Adapter", "")
    #
    # #cpu
    # if (item.find("Processor") != -1):
    #     item = item.replace("Processor", "")
    # if (item.find("Gold") != -1):
    #     item = item.replace("Gold", "")
    if (item.find("Dual Core") != -1):
        item = item.replace("Dual Core", "X2") ##
    if (item.find("Mobile") != -1):
        item = item.replace("Mobile", "")
    if(item.find("GHz") != -1):
        item = item.replace("GHz", "")
    if (item.find("MHz") != -1):
        item = item.replace("MHz", "")
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
    #
    item = item.lower()
    # if (item.find("series") != -1):
    #     item = item.replace("series", "")
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

def init_driver():
    ff = "../install/chromedriver.exe"
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("headless")
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
    global count_add, count_no_add, cpus
    print("Запуск браузера")
    driver = init_driver()
    print("Переход на страницу:", url)
    driver.get(url)
    select_deskornote = driver.find_element_by_css_selector('select[name = "deskornote"]')
    select_deskornote.click()
    options = select_deskornote.find_elements_by_css_selector('option')
    for option in options:
        if(option.text == "Show all GPUs"):
            option.click()
            break

    select_professional = driver.find_element_by_css_selector('select[name = "professional"]')
    select_professional.click()
    options = select_professional.find_elements_by_css_selector('option')
    for option in options:
        if (option.text == "Consumer and Professional GPUs"):
            option.click()
            break

    select_multiplegpus = driver.find_element_by_css_selector('select[name = "multiplegpus"]')
    select_multiplegpus.click()
    options = select_multiplegpus.find_elements_by_css_selector('option')
    for option in options:
        if (option.text == "Single and multiple GPUs"):
            option.click()
            break

    select_games = Select(driver.find_element_by_css_selector('#bl_gameselect'))
    select_games.all_selected_options()

    input_button = driver.find_element_by_css_selector('input[type="submit"]').click()

    time.sleep(20)
    # trs = driver.find_elements_by_css_selector('table>tbody>tr[style = "display: table-row;"')
    # count_cpu = len(trs)
    # print(count_cpu)
    # for index, tr in enumerate(trs):
    #     tds = tr.find_elements_by_css_selector('td')
    #     name_cpu = tds[0].find_elements_by_css_selector('a')[1].text
    #     if(name_cpu.find("Intel Core2") != -1):
    #         name_cpu = name_cpu.replace("Intel Core2", "Intel Core 2")
    #     single_thread = tds[4].text
    #     if (single_thread == "NA"):
    #         single_thread = None
    #
    #     multi_thread = tds[2].text
    #
    #     id_product = get_product_id(name_cpu, "cpu")
    #     if(id_product != None):
    #         add_cpu_benchmark(id_product, id_brenchmark_cpu, single_thread,multi_thread)
    #         count_add += 1
    #         print("Добавлен в БД:",[id_product, id_brenchmark_cpu, single_thread,multi_thread])
    #     else:
    #         id_product = search_best_conformity(name_cpu, "cpu")
    #         if (id_product != None):
    #
    #             id_cpu_brenchmark_value_one = add_cpu_benchmark(id_product, id_brenchmark_cpu, single_thread, multi_thread)
    #             count_add += 1
    #             print("Добавлен в БД:", [name_cpu, single_thread, multi_thread])
    #         else:
    #             count_no_add += 1
    #             cpus.append([name_cpu, single_thread, multi_thread])
    #             print("Добавлен в список недобавленных:", [name_cpu, single_thread, multi_thread])

    driver.close()

def main():
    global cpus, id_brenchmark_cpu, list_many_optimization, count_many_optimization, count_add, count_no_add, change_list_database
    start_time = time.time()
    for url in url_main:
        change_list_database = True
        parse(url)


        for list_many_optimization in list_many_optimization:
            print(list_many_optimization)


    print("------------------------Недобавленные  CPUS-----------------------------")
    for cpu in cpus:
        print(cpu)
    print("Количество add:", count_add)
    print("Количество no_add:", count_no_add)
    print("Количество 2 и более значений:", count_many_optimization)
    print("Время работы:", time.time() - start_time)



if __name__ == '__main__':
    main()