import time
import logging
import csv
from mysql.connector import MySQLConnection, Error
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"

source_name = "CompuBench 1.5 Desktop"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

count_cpu = 0
count_zero = 0

all = []
url_main = "https://gfxbench.com/result.jsp?benchmark=gfx40"

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

def get_product_id(name):
    name_text = name
    sql_query = "SELECT id FROM gpu WHERE name = %s"

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
            sql_query = "SELECT id FROM gpu WHERE name LIKE %s"
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
    selected = ["Car Chase Offscreen", "Manhattan", "T-Rex"]
    # selected = ["Face Detection","Ocean Surface Simulation", "T-Rex", "Video Composition"]
    global count_cpu
    print("Запуск браузера")
    driver = init_driver()
    print("Переход на страницу:", url)
    driver.get(url)

    tickets_per_page_top_control_selectSelectBoxIt = driver.find_element_by_css_selector(
        '#tickets-per-page-top-control-selectSelectBoxIt').click()
    tickets_per_page_top_control_selectSelectBoxItOptions = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#tickets-per-page-top-control-selectSelectBoxItOptions")))
    lis = tickets_per_page_top_control_selectSelectBoxItOptions.find_elements_by_css_selector('li')
    for li in lis:
        if (li.find_element_by_css_selector('a').text == "Show all"):
            li.click()
            break

    for select in selected:
        global source_name
        # id_brenchmark = get_gpu_benchmark_id(source_name, select)
        # window_result =  WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.results-list")))
        testSelectBoxItContainer = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#testSelectBoxItContainer'))).click()
        testSelectBoxItOptions = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#testSelectBoxItOptions")))
        lis = testSelectBoxItOptions.find_elements_by_css_selector('li')
        for li in lis:
            text = li.find_element_by_css_selector('a').text
            if(text == select):
                li.click()
                break
        div_results_list = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.results-list")))
        items = div_results_list.find_elements_by_css_selector("#result-list-container>a>ul")
        print(len(items))
        for index, item in enumerate(items):
            lis = item.find_elements_by_css_selector("li")
            name = lis[1].text
            # id_product = get_product_id(name)
            # if(id_product != None):
            value = lis[5].find_element_by_css_selector('span').text
            if(value == "Failed / Not supported"):
                value = None
            print([select, name, value])
            all.append([select, name, value])
                # add_gpu_benchmark(id_product, id_brenchmark, value)



        time.sleep(2)







if __name__ == '__main__':
    start_time = time.time()
    main(url_main)
    with open("gfxbench.com.txt", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(all)
    print("Время выполнения скрипта:", time.time() - start_time)
    print("Количество недобавленных процессоров:", count_zero )
    print("Количество добавленных процессоров:", str(count_cpu - count_zero))