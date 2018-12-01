import time
import logging

from mysql.connector import MySQLConnection, Error
from selenium import webdriver
from selenium.common.exceptions import *
import csv
db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

count_cpu = 0
count_zero = 0
add = 0
no_add = 0
all = []

url_main = "https://www.cpubenchmark.net/CPU_mega_page.html"

def add_no_one():
    global count_no_one
    count_no_one += 1

def add_zero():
    global count_zero
    count_zero += 1


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

def get_product_id(name):
    name_text = name
    sql_query = "SELECT id FROM cpu WHERE name = %s"

    data = (name_text,)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            for i in range(len(name) + 1):
                for index in range(0, i):
                    name_text = (name[index:i])

                    # print(name_text)
                    data = (name_text,)
                    rows = select_database(sql_query, data)
                    #Если ответ равен 1, то возвращаем id
                    if(len(rows) == 1):
                        return rows[0][0]
            sql_query = "SELECT id FROM cpu WHERE name LIKE %s"
            for i in range(len(name) + 1):
                for index in range(0, i):
                    name_text = (name[index:i])

                    # print(name_text)
                    data = ("%"+name_text+"%",)
                    rows = select_database(sql_query, data)
                    #Если ответ равен 1, то возвращаем id
                    if(len(rows) == 1):
                        return rows[0][0]
            add_zero()

def add_cpu_benchark(cpu_id, id_benchmark, single_thread, multi_thread):

    sql_query = "SELECT id FROM cpu_benchmark_value WHERE cpu_id = %s and cpu_benchmark_id = %s and multi_core_value = %s and single_core_value = %s LIMIT 1"
    data = (cpu_id, id_benchmark, multi_thread, single_thread)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "INSERT INTO cpu_benchmark_value (cpu_id, cpu_benchmark_id, multi_core_value, single_core_value) VALUES (%s, %s, %s, %s)"
            return insert_database(sql_query, data)



def init_driver():
    ff = "chromedriver.exe"
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



def main(url):
    global add, no_add
    global count_cpu
    name_benchmark = "Passmark"
    id_benchmark = get_cpu_benchmark_id(name_benchmark)
    print("ID Benchmark:", id_benchmark)
    print("Запуск браузера")
    driver = init_driver()
    print("Переход на страницу:", url)
    driver.get(url)
    trs = driver.find_elements_by_css_selector('table>tbody>tr[style = "display: table-row;"')
    count_cpu = len(trs)
    print(count_cpu)
    for index, tr in enumerate(trs):
        tds = tr.find_elements_by_css_selector('td')
        name_cpu = tds[0].find_elements_by_css_selector('a')[1].text
        if(name_cpu.find("Intel Core2") != -1):
            name_cpu = name_cpu.replace("Intel Core2", "Intel Core 2")
        id_processor = get_product_id(name_cpu)
        # print("ID_cpu:", id_processor)

        if(id_processor != None):
            add += 1
        else:
            no_add += 1
        single_thread = tds[4].text
        if(single_thread =="NA"):
            single_thread = None


        multi_thread = tds[2].text
        temp = [name_cpu, single_thread, multi_thread]
        print(temp)
        # global all
        # all.append(temp)
        # temp = []
            # id_benchmark_value = add_cpu_benchark(id_processor, id_benchmark, single_thread, multi_thread)
            # log.info("%s, %s, %s|%s", index + 1, name_cpu, single_thread, multi_thread)



    driver.close()





if __name__ == '__main__':
    start_time = time.time()
    main(url_main)
    # with open("cpubenchmark.net.txt", "w", newline="") as file:
    #     writer = csv.writer(file)
    #     writer.writerows(all)
    #
    # print("Время выполнения скрипта:", time.time() - start_time)
    print("Количество недобавленных процессоров:", str(add))
    print("Количество добавленных процессоров:", str(no_add))
