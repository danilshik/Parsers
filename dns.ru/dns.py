import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from bs4 import BeautifulSoup
import selenium.common.exceptions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
urls_phone=[]
wait_long=5
wait_mean=3
url_main="https://www.dns-shop.ru"
url_group="https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/"
def init_driver():
    ff = "../../install/chromedriver"
    chrome_option = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_option.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(executable_path=ff,chrome_options=chrome_option)
    #driver = webdriver.Chrome(executable_path=ff)
    driver.wait = WebDriverWait(driver,0)
    return driver

def parsing():
    print("Парсинг страницы")
    # url = driver.get(url_group)
    # url = driver.get("https://www.dns-shop.ru/catalog/17a8a01d16404e77/smartfony/?p=10&i=1")

    catalog_items_list = driver.find_element_by_class_name("catalog-items-list")
    items = catalog_items_list.find_elements_by_class_name("item")
    for item in items:
        webdriver.ActionChains(driver).move_to_element(item).perform();
        try:
            accessibility = item.find_element_by_class_name("pseudo-link")
        except NoSuchElementException:
            accessibility=None
        if(accessibility!=None):
            if (accessibility.text.find("магаз") != -1):
                print("Парсинг данных")
                title = item.find_element_by_tag_name("h3").text
                index_smatrphone = title.find("Смартфон")
                # 9 - это длина слова 'Смартфон ' + пробел
                index_GB = title.find("ГБ")
                text = title[index_smatrphone + 9:]
                opa = title[index_smatrphone + 9:index_GB - 1]
                index_space = opa.rfind(" ")
                name = text[:index_space]
                print("Название телефона:", name)
                color = title[index_GB + 3:]
                print("Цвет:", color)
                variant = title[len(name) + index_smatrphone + 10:index_GB + 2]
                print("Разновидность:", variant)


                price = item.find_element_by_xpath("*//span[@data-of='price-total' and @data-product-param='price']").get_attribute("data-value")
                print("цена", price)

                div_title = item.find_element_by_class_name("title")
                link = div_title.find_element_by_tag_name("a").get_attribute("href")
                print("Ссылка", link)
                try:
                    previous_price_s = item.find_element_by_class_name('prev-price-total')
                except (NoSuchElementException):
                    previous_price_s = None
                if (previous_price_s != None):
                    previous_price_s = previous_price_s.text
                    previous_price = previous_price_s.replace(" ", "")
                    print("Предыдущая цена:", previous_price)
                    discount = item.find_element_by_xpath("*//span[@class='percent']").text[-2:-1]
                    print("Скидка:", discount)
                id_accessibility=accessibility.get_attribute('data-product-id')
                print(id_accessibility)
                accessibility.click()
                shop_flters_id="shop-filters-list-"+id_accessibility
                window_div_text="avails-modal-"+id_accessibility
                print(shop_flters_id)
                div_shop_filters_list=WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, shop_flters_id)))
                window = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, window_div_text)))
                div_avails_list_shown=window.find_element_by_class_name("avails-list")
                shops = div_avails_list_shown.find_elements_by_xpath("*//div[(@class='avails-item row' or @class='avails-item row ') and @data-is-avail='1']")

                print(" ---------------Количество----",len(shops))
                if(len(shops)==0):
                    time.sleep(1000)
                for shop in shops:
                    shop_latitude = shop.get_attribute('data-latitude')
                    shop_longitude = shop.get_attribute('data-longitude')
                    shop_name_text = shop.find_element_by_class_name('shop-name')
                    shop_name = shop_name_text.find_element_by_tag_name('a').text
                    shop_address = shop_name_text.find_elements_by_tag_name('p')[1].text
                    count_phone_text = shop.find_element_by_xpath("div[contains(@class,'col col-3 available')]").text
                    count_phone = re.findall('(\d+)', count_phone_text)
                    print(shop_name, shop_address, shop_latitude, shop_longitude,count_phone)
                btn_close = window.find_element_by_class_name("modal-close-btn")
                btn_close.click()
                WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.ID, window_div_text)))
                    # WebDriverWait(driver, 15).until(EC.invisibility_of_element_located(window))
                #time.sleep(1)



def scrolling_object(object):
    webdriver.ActionChains(driver).move_to_element(object).perform();

def lookup_main_url(driver):
    select_category(driver)
    parsing()



def select_category(driver):
    driver.get(url_group)
    #
if __name__ == "__main__":
    start_time=time.time()
    driver = init_driver()
    lookup_main_url(driver)

    print(time.time()-start_time)
    driver.quit()



