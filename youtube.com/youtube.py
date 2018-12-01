# encoding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import time


filename = "teskit.txt"

def load_data(filename):
    with open(filename, "r") as file:
        urls = file.read().split("\n")
    return urls

def init_driver():
    ff = "install/geckodriver.exe"
    try:
        profile = webdriver.FirefoxProfile('C:\\Users\Danilshik\AppData\Roaming\Mozilla\Firefox\Profiles\oifkhban.selenium')
    except FileNotFoundError:
        print("Профиль Firefox не найден. Проверьте ссылку")
        exit(0)
    try:
        driver = webdriver.Firefox(executable_path=ff, firefox_profile=profile)
    except SessionNotCreatedException:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера")

    return driver

def main():
    print("Запуск браузера")
    driver = init_driver()
    print("Открытие текстового файла")
    items = load_data(filename)
    for item in items:
        item_block = item.split(";")
        url = item_block[0]
        time_full = item_block[1].split(":")
        try:
            hours = int(time_full[-3])
        except IndexError:
            hours = 0
        try:
            minute = int(time_full[-2])
        except IndexError:
            minute = 0
        second = int(time_full[-1])
        print("Ссылка:", url)
        print("Количество часов:", hours)
        print("Количество минут:", minute)
        print("Количество секунд:", second)
        sleep = hours * 3600 + minute * 60 + second
        print("Время задержки в секундах:", sleep)

        print("Переход на страницу:", url)
        try:
            driver.get(url)
        except WebDriverException as e:
            print("Ошибка запроса страница. Возможно страница недоступна")
            continue
        if(url.find("youtube")!= -1):
            try:
                error = driver.find_element_by_css_selector('div.reason.style-scope.yt-player-error-message-renderer')
                continue
            except NoSuchElementException:
                print("Элемент недоступности видео не найдено. Продолжаем")


        for i in range(sleep):
            print("Ожидание: "+str(sleep)+" c. Осталось "+ str(sleep - i))
            time.sleep(1)
    driver.close()
    print("Ссылки закончились. Закрытие браузера. Конец программы")


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("Время выполнения скрипта:", time.time() - start_time)