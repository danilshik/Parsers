# encoding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.common.exceptions import NoSuchElementException
import json
import time
import io
text_login = "79824665686"
text_password = ""   #Пароль
text_login = text_login[1:]
main_url = "https://qiwi.com/"




def init_driver():
    ff = "install/geckodriver.exe"
    # chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("headless")
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_option.add_experimental_option("prefs", prefs)


    try:
        driver = webdriver.Firefox(executable_path=ff)
        # driver = webdriver.Chrome(executable_path=ff, chrome_options=chrome_option, service_args=service_args)
    except SessionNotCreatedException:
        print "Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера"

    return driver

def main():
    print "Запуск браузера"
    driver = init_driver()
    print "Переход на главную страницу Qiwi"
    driver.get(main_url)
    print "Захват кнопки входа в личный кабинет"
    select = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.button-self-32.button-minor-35.button-brand-36")))

    select.click()
    print "Определения окна логина"
    dialog_window = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.dialog-content-277.dialog-content-transition-self-320.dialog-content-transition-entered-322")))
    # time.sleep(2)
    print "Ввод логина"
    input_phone_number = dialog_window.find_element_by_class_name("phone-input-form-field-input-control-text-self-353")
    input_phone_number.send_keys(text_login)
    print "Ввод пароля"
    input_password = dialog_window.find_element_by_class_name("password-input-form-field-input-control-self-379")
    input_password.send_keys(text_password)
    print "Нажатие кнопки входа"
    button_send_login_and_password = dialog_window.find_element_by_css_selector("button.button-self-32.button-normal-34.button-brand-36")
    button_send_login_and_password.click()

    WebDriverWait(driver, 15).until(EC.invisibility_of_element_located(dialog_window))
    print "Переход на страницу историй"
    driver.get("https://qiwi.com/history")

    main_block = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/section/section/div[2]")))

    WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/section/section/div[2]/div")))
    try:
        button_next = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div/section/section/div[2]/div/div[2]/div[5]")))
        # button_next = main_block.find_elements_by_xpath("/html/body/div/section/section/div[2]/div/div[2]/div[5]")
        button_next.click()
    except:
        print "Кнопка загрузки последних 10 транзакций не найдена"

    scroll(driver)

    json_str = []
    history_blocks = main_block.find_elements_by_xpath("/html/body/div/section/section/div[2]/div[1]/div[2]/div")[1:-1]


    for history_block in history_blocks:
        # date = history_block.find_element_by_css_selector("/html/body/div/section/section/div[2]/div[1]/div[2]/div[2]/div[1]/span").text
        date = history_block.find_element_by_xpath("div[1]/span").text
        print date


    #     items = history_block.find_elements_by_css_selector("div.history-item-self-101.history-item-success-128")
        items = history_block.find_elements_by_xpath("div[2]/div")
        items_list = []

        for item in items:
            result = []

            # total = item.find_element_by_css_selector("span.history-item-header-sum-amount-118").text[:-2]
            total = item.find_element_by_xpath("div[2]/div[3]/div/span").text[:-2]
            total = total.replace(" ", "")
            total_list = list(total)
            if(total_list[0] != "+"):
                total = "-" + total

            print total
            result.append(["total", total])

            item.click()



    #         history_item_header = item.find_element_by_css_selector("div.history-item-header-109")
    #
            history_item_header = item.find_element_by_xpath("div[2]")
            logo = history_item_header.find_element_by_xpath("div")
            try:
                image = logo.find_element_by_css_selector("img").get_attribute("src").strip()
            except NoSuchElementException:
                image = None
            print image
            result.append(["image", image])


            history_item_header_info = history_item_header.find_element_by_xpath("div[2]")
            try:
                name = history_item_header_info.find_element_by_xpath("span").text.strip()
            except:
                name = None
            print name
            result.append(["name", name])

            tables = item.find_elements_by_css_selector("table")

            for index, table in enumerate(tables):
                # if():
                trs = table.find_elements_by_css_selector("tr")
                for tr in trs:
                    tds = tr.find_elements_by_css_selector("td")

                    if(index == 0):
                        #Бесконечный цикл для уменьшения времени выполнения скрипта. Ниже такой же
                        while True:
                            one_block = tds[0].text.strip()
                            try:
                                two_block = tds[1].text.strip()[:-2]
                            except StaleElementReferenceException:
                                two_block = ""
                            if((one_block != "") and (two_block != "")):
                                break
                    else:
                        while True:
                            one_block = tds[0].text.strip()
                            try:
                                two_block = tds[1].text.strip()
                            except StaleElementReferenceException:
                                two_block = ""
                            if ((one_block != "") or (two_block != "")):
                                break
                    result.append([one_block, two_block])

            history_data_dict = dict(result)
            items_list.append(history_data_dict)

        history_date = {"date": date, "histories": items_list}
        print history_date
        json_str.append(history_date)

    account_exit = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "/html/body/div/section/header/div/div[2]/div")))
    account_exit.click()

    button_exit = WebDriverWait(driver, 15).until(EC.visibility_of_element_located(
        (By.XPATH, "/html/body/div/section/header/div/div[2]/div/div[3]/div/div[4]/a[3]")))
    button_exit.click()
    print "Вышли из аккаунта"

    "Закрытие браузера"
    driver.quit()

    print "Формирование Json"
    with io.open(text_login+'.json', 'w', encoding="utf-8") as fp:
        s = json.dumps(json_str, ensure_ascii=False)
        fp.write(s)



def scroll(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

if __name__ == '__main__':
    start_time = time.time()
    main()
    print "Время выполнения скрипта:", time.time() - start_time



