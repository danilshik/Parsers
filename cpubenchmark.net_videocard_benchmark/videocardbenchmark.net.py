import time
import logging
import csv
from mysql.connector import MySQLConnection, Error
from selenium import webdriver
from selenium.common.exceptions import *

db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

count_gpu = 0
count_zero = 0

url_main = "https://www.videocardbenchmark.net/GPU_mega_page.html"

all = []

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

def get_gpu_id(name):
    name_text = "%"+name+"%"

    sql_query = "SELECT id FROM gpu WHERE name LIKE %s"
    data = (name_text,)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            name_list = name.split(" ")
            for i in range(len(name_list)):
                name_text = ""
                for name_per in name_list[:-i]:
                    name_text = name_text + name_per
                    name_text = name_text +" "
                #Удаляем лишний пробел
                name_text = name_text.strip()
                name_text = "%"+name_text+"%"

                print(name_text)
                data = (name_text,)
                rows = select_database(sql_query, data)
                #Если ответ равен 1, то возвращаем id
                if(len(rows) == 1):
                    return rows[0][0]

            add_zero()


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
    global count_gpu
    id_G3D_mark = get_gpu_benchmark_id("PassMark", "G3D Mark")
    print("ID G3D_mark:", id_G3D_mark)
    id_G2D_mark = get_gpu_benchmark_id("PassMark", "G2D Mark")
    print("ID G2D_mark:", id_G2D_mark)
    print("Запуск браузера")
    driver = init_driver()
    print("Переход на страницу:", url)
    driver.get(url)
    trs = driver.find_elements_by_css_selector('table>tbody>tr[style = "display: table-row;"')
    count_gpu = len(trs)
    for index, tr in enumerate(trs):
        tds = tr.find_elements_by_css_selector('td')
        name_gpu = tds[0].find_elements_by_css_selector('a')[1].text
        # id_gpu = get_gpu_id(name_gpu)

        # if(id_gpu != None):
        G3D_Mark = tds[2].text
        G2D_Mark = tds[4].text

        # id_benchmark_value = add_gpu_benchmark(id_gpu, id_G3D_mark, G3D_Mark)
        # log.info("%s, %s, %s", id_gpu, id_G3D_mark, G3D_Mark)
        #
        # id_benchmark_value = add_gpu_benchmark(id_gpu, id_G2D_mark, G2D_Mark)
        # log.info("%s, %s, %s", id_gpu, id_G2D_mark, G2D_Mark)
        temp = [name_gpu, G3D_Mark, G2D_Mark]
        print(temp)
        global all
        all.append(temp)



    driver.close()





if __name__ == '__main__':
    start_time = time.time()
    main(url_main)
    with open("videocardbenchmark.net.txt", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(all)
    print("Время выполнения скрипта:", time.time() - start_time)
    print("Количество недобавленных видеокарт:", count_zero )
    print("Количество добавленных видеокарт:", str(count_gpu - count_zero))
