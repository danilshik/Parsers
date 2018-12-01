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
login = "frank.zuver@gmail.com"
password = "Acronis123!!!"   #Пароль

filename = "links_basic.txt"
main_url = "https://www.ebay.com/"
sign_url = "https://signin.ebay.com/ws/eBayISAPI.dll"

def load_data(filename):
    with open(filename, "r") as file:
        urls = file.read().split("\n")
    return urls

def init_driver():
    ff = "install/chromedriver.exe"
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


def main(urls_list):
    print("Запуск браузера")
    driver = init_driver()
    print("Переход на страницу Авторизации")
    driver.get(sign_url)



    print("Ввод логина")
    input_userid = driver.find_element_by_css_selector('#userid')
    input_userid.send_keys(login)

    print("Ввод пароля")
    input_password = driver.find_element_by_css_selector('#pass')
    input_password.send_keys(password)

    #Авторизация
    button_sign = driver.find_element_by_css_selector('#sgnBt')
    button_sign.click()


    for url in urls_list:
        print(url)
        try:
            print("Переход на страницу запроса")
            driver.get(url)
        except WebDriverException:
            print("Программа неправильно определила ссылку, конец программы.")
            exit(0)


        try:
            count_result = int(driver.find_element_by_css_selector("h1.rsHdr>span.rcnt").text)
            try:
                searchfor = driver.find_element_by_css_selector("h1.rsHdr>span.kwcat>b").text
                type = 0
            except NoSuchElementException:
                type = 2



        except NoSuchElementException:
            try:
                count_result_text = driver.find_element_by_css_selector("h1.srp-controls__count-heading").text.split(" ")[0]
                count_result = int(count_result_text.replace(",",""))
                type = 1
            except:
                print("Ошибка определения количества результатов. Обратитесь к разработчику парсера")
        print("Количество результатов:", count_result)
        print("Тип:",type)


        # try:
        #     banner = driver.find_element_by_css_selector("span.page-notice__status")
        #     banner = True
        # except NoSuchElementException:
        #     banner = False
        # print(banner)
        if(count_result != 0):

            if(type == 0):
                # count_items_in_page = int(driver.find_element_by_css_selector("div.srp-ipp__control--legacy>span").text)
                # print(count_items_in_page)
                # if(count_items_in_page != None):

                # count_page = count_result // 200
                # print("Количество страниц с товаром:", count_page)
                # last_count_result = count_result % 200
                # print("Количество товаров на последней странице:", last_count_result)
                count_item_traversed = 0
                # # for index in range(count_page):


                while True:
                    items = driver.find_elements_by_css_selector('#ListViewInner>li')
                    for index, item in enumerate(items):
                        if(item.get_attribute("class") =="lvresult clearfix li"):
                            items = items[:index]
                            break
                    print("Количество элементов на странице:", len(items))


                    for item in items:
                        try:
                            title = item.find_element_by_css_selector("h3.lvtitle>a").text
                        except:
                            print("Ошибка нахождения названия. Остановка программы", url)
                            exit(0)
                        print("Title:", title)

                        try:
                            url = item.find_element_by_css_selector("h3.lvtitle>a").get_attribute("href")
                        except:
                            print("Ошибка нахождения ссылки на товар. Остановка программы", url)
                            exit(0)
                        print("URL:", url)

                        try:
                            shipping = item.find_element_by_css_selector("span.ship>span").text
                        except:
                            shipping = None
                            print("Ошибка нахождения shipping. Остановка программы", url)
                            # exit(0)
                        print("Shipping:", shipping)

                        try:
                            pic = item.find_element_by_css_selector('img.img').get_attribute('src')
                        except:
                            pic = None
                            # print("Ошибка нахождения картинки. Остановка программы", urllist)
                            # exit(0)
                        print("Картинка:", pic)

                        try:
                            span_bids = item.find_element_by_css_selector("span.s-item__bids.s-item__bidCount").text
                        except:
                            span_bids = None

                        try:
                            span_best_offer = item.find_element_by_css_selector("span.s-item__purchase-options.s-item__purchaseOptions").text
                        except:
                            try:
                                span_best_offer = item.find_element_by_css_selector("li.lvformat>span").text

                            except:
                                span_best_offer = None
                        dealtype = ""
                        if(span_bids != None):
                            dealtype = span_bids + " "
                        if(span_best_offer != None):
                            dealtype = dealtype + span_best_offer

                        print("Dealtype:", dealtype)


                        print("Searchfor:", searchfor)

                        count_item_traversed = count_item_traversed + 1
                        print("Количество найденных элементов:", count_item_traversed)




                    #Добавлять в бд до этого блока кода
                    try:
                        a_next = driver.find_element_by_css_selector("td.pagn-next>a")
                        if(a_next.get_attribute("aria-disabled")=="true"):
                            break
                        a_next.click()
                    except NoSuchElementException:
                        break

    driver.close()





if __name__ == '__main__':
    start_time = time.time()
    urls = load_data(filename)
    main(urls)
    print("Время выполнения скрипта:", time.time() - start_time)



    # count_page = count_result // 100
    # print("Количество страниц с товаром:", count_page)
    # last_count_result = count_result % 100
    # print("Количество товаров на последней странице:", last_count_result)
    # count_page_traversed = 0
    # for index in range(count_page):
    #     try:
    #         ul_list_li = driver.find_element_by_css_selector("#ListViewInner")
    #     except NoSuchElementException:
    #         try:
    #             ul_list_li = driver.find_element_by_css_selector("ul.srp-results.srp-list.clearfix")
    #         except:
    #             print("Ошибка нахождения ul.")
    #             exit(0)
    #
    #     items = ul_list_li.find_elements_by_css_selector('li.s-item')
    #     if(len(items) == 0):
    #         items = ul_list_li.find_elements_by_css_selector('li.sresult.lvresult.clearfix.li')
    #     print(len(items))
    #     for item in items:
    #         try:
    #             title = item.find_element_by_css_selector("h3.s-item__title").text
    #         except:
    #             try:
    #                 title = item.find_element_by_css_selector("h3.lvtitle>a").text
    #             except:
    #                 print("Ошибка нахождения названия. Остановка программы", url_list)
    #                 exit(0)
    #         print(title)
    #
    #         try:
    #             url = item.find_element_by_css_selector("a.s-item__link").get_attribute("href")
    #         except:
    #             try:
    #                 url = item.find_element_by_css_selector("h3.lvtitle>a").get_attribute("href")
    #             except:
    #                 print("Ошибка нахождения ссылки на товар. Остановка программы", url_list)
    #                 exit(0)
    #         print(url)
    #
    #         try:
    #             shipping = item.find_element_by_css_selector("span.s-item__shipping.s-item__logisticsCost").text
    #         except:
    #             try:
    #                 shipping = item.find_element_by_css_selector("span.ship>span").text
    #             except:
    #                 try:
    #                     shipping = item.find_element_by_css_selector("span.ship>span>span").text
    #                 except:
    #                     print("Ошибка нахождения shipping. Остановка программы", url_list)
    #                     exit(0)
    #         print(shipping)
    #
    #         try:
    #             pic = item.find_element_by_css_selector('img.s-item__image-img').get_attribute('src')
    #         except:
    #             try:
    #                 pic = item.find_element_by_css_selector('img.img').get_attribute('src')
    #             except:
    #                 print("Ошибка нахождения картинки. Остановка программы", url_list)
    #                 exit(0)
    #         print("Картинка:", pic)
    #
    #         try:
    #             span_bids = item.find_element_by_css_selector("span.s-item__bids.s-item__bidCount").text
    #         except:
    #             span_bids = None
    #
    #         try:
    #             span_best_offer = item.find_element_by_css_selector("span.s-item__purchase-options.s-item__purchaseOptions").text
    #         except:
    #             try:
    #                 # span_best_offer = item.find_element_by_css_selector("li.lvformat>span").text
    #                 span_best_offer = None
    #             except:
    #                 span_best_offer = None
    #         dealtype = ""
    #         if(span_bids != None):
    #             dealtype = span_bids + " "
    #         if(span_best_offer != None):
    #             dealtype = dealtype + span_best_offer
    #
    #         print("dealtype:", dealtype)
    #
    #         searchfor = None