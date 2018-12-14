from mysql.connector import MySQLConnection, Error
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time

db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"

urls = []
numbers = []
count_thread = 1  #Количество потоков
output_filename_excel = "project_for_export_no_formulas_31_10_18.xlsx"
output_filename_txt = "number.txt"

url_main =  [ "https://compubench.com/result.jsp?benchmark=compu15d" ]

def load_excel(output_filename):
    urls = []
    data = pd.read_excel(output_filename, 'Projects', dtype=str)
    for item in data["Telegram link"]:
        if item != "nan":
            urls.append(item)

def load_numbers(output_filename):
    numbers = []
    for item in pd.read_csv(output_filename, sep="\n", header=None)[0]:
        numbers.append(item)
    return numbers






def init_driver():
    ff = "../install/chromedriver.exe"
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("headless")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_option.add_experimental_option("prefs", prefs)


    try:
        # driver = webdriver.Firefox(executable_path=ff)
        driver = webdriver.Chrome(executable_path=ff, options=chrome_option)
        # driver = webdriver.Chrome(executable_path=ff, chrome_options=chrome_option, service_args=service_args)
    except SessionNotCreatedException:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера")

    return driver

def sign_in(number):
    driver = init_driver()
    driver.get("https://www.web-telegram.ru/#/login")
    window_sign_in= WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.login_page")))
    block_login = window_sign_in.find_element_by_css_selector("div.login_phone_groups_wrap.clearfix")
    code_number_phone = block_login.find_element_by_css_selector("div.md-input-group.login_phone_code_input_group.md-input-has-value.md-input-animated > input")
    code_number_phone.click()
    code_number_phone.clear()
    code_number_phone.send_keys("+"+str(number)[0])

    number_phone = block_login.find_element_by_css_selector("div.md-input-group.login_phone_num_input_group.md-input-animated > input")
    number_phone.click()
    number_phone.clear()
    number_phone.send_keys(str(number)[1:])

    a_login_head_submit_btn = driver.find_element_by_css_selector('a.login_head_submit_btn')
    a_login_head_submit_btn.click()

    block_confirmation_phone =  WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content.modal-content-animated")))
    button_confirmation_phone = block_confirmation_phone.find_element_by_css_selector("button.btn.btn-md.btn-md-primary")
    time.sleep(2)
    button_confirmation_phone.click()
    time.sleep(50)


def main():
    global urls, numbers, count_thread
    print("Чтение Excel")
    urls = load_excel(output_filename_excel)
    print("Чтение номеров телефона")
    numbers = load_numbers(output_filename_txt)
    print(numbers[0])
    sign_in(numbers[0])















if __name__ == '__main__':
    start = time.time()
    main()

    print("Время работы:", time.time() - start)
