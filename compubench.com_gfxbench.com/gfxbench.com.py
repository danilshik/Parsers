import time
import logging
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

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)
count_cpu = 0
count_zero = 0
url_main = ["https://gfxbench.com/result.jsp?benchmark=gfx40"]

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

def get_gpu_benchmark_id(source_name, test_name, score_name):
    sql_query = "SELECT gpu_benchmark_id FROM gpu_benchmarks WHERE source_name = %s and test_name = %s and score_name = %s"
    data = (source_name, test_name, score_name)
    rows = select_database(sql_query, data)
    if(len(rows)==1):
        return rows[0][0]
    else:
        print("Отсутствует Id бенчмаркета в таблице.")
        exit(0)

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
    # text = re.search("IGP$", item)
    # if (text != None):
    #     item = item.replace(text.group(0), "")
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
    if (item.find(",") != -1):
        item = item.replace(",", "")
    if (item.find("Adapter") != -1):
        item = item.replace("Adapter", "")
    if (item.find("(FireGL)") != -1):
        item = item.replace("(FireGL)", "")
    #
    # #cpu
    if (item.find("Processor") != -1):
        item = item.replace("Processor", "")
    if (item.find("Compute Engine") != -1):
        item = item.replace("Compute Engine", "") ##
    if (item.find("(Desktop)") != -1):
        item = item.replace("(Desktop)", "")
    if (item.find("Design") != -1):
        item = item.replace("Design", "") #?
    # if (item.find("ATI") != -1):
    #     item = item.replace("ATI", "") #?
    if (item.find("Graphics") != -1):
        item = item.replace("Graphics", "") #?
    # if (item.find("GMA") != -1):
    #     item = item.replace("GMA", "") #?
    if (item.find("®") != -1):
        item = item.replace("®", "")
    if (item.find("™") != -1):
        item = item.replace("™", "")
    if (item.find("CPU") != -1):
        item = item.replace("CPU", "")
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
    if (item.find("radeon") != -1):
        item = item.replace("radeon", "")
    if (item.find("ati") != -1):
        item = item.replace("ati", "")

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
    source_name = "GFXBench 4.0"
    selected = ["Car Chase Offscreen", "Manhattan", "T-Rex"]
    global count_cpu, count_add, count_no_add
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
        id_brenchmark_gpu_frames = get_gpu_benchmark_id(source_name, select, "Frames")
        id_brenchmark_gpu_fps = get_gpu_benchmark_id(source_name, select, "Fps")
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
            value = lis[5].find_element_by_css_selector('span.value').text
            if(value == "Failed / Not supported"):
                value = None
            fps = lis[5].find_element_by_css_selector('span.fps').text
            if(fps == "Failed / Not supported"):
                fps = None
            if(fps.find(")") != -1):
                fps = fps.replace(")", "")
            if (fps.find("(") != -1):
                fps = fps.replace("(", "")
            fps = fps[:-3]


            id_product = get_product_id(name, "gpu")
            if (id_product != None):
                add_gpu_benchmark(id_product, id_brenchmark_gpu_frames, value)
                add_gpu_benchmark(id_product, id_brenchmark_gpu_fps, fps)
                count_add += 1
                print("Добавлен в БД:", [id_product, id_brenchmark_gpu_frames, value])
                print("Добавлен в БД:", [id_product, id_brenchmark_gpu_fps, fps])
            else:
                id_product = search_best_conformity(name, "gpu")
                if (id_product != None):
                    add_gpu_benchmark(id_product, id_brenchmark_gpu_frames, value)
                    add_gpu_benchmark(id_product, id_brenchmark_gpu_fps, fps)
                    count_add += 1
                    print("Добавлен в БД:", [id_product, id_brenchmark_gpu_frames, value])
                    print("Добавлен в БД:", [id_product, id_brenchmark_gpu_fps, fps])
                else:
                    count_no_add += 1
                    gpus.append([name])
                    print("Добавлен в список недобавленных:", [name, value])


def main():
    global gpus, id_brenchmark_gpu, list_many_optimization, count_many_optimization, count_add, count_no_add, change_list_database
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