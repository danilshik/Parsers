from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
import time
import requests
import logging
import lxml.html
import MySQLdb
param = []
from string import printable
from bs4 import BeautifulSoup
import json
from lxml.cssselect import CSSSelector as cssselect
import re
count_lose = 0
count_succes=0
count_thread = 20
param = []
list_urls=[]
object_urls=[]
cities= []
cities_data = []
url_main="https://www.mvideo.ru"
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

id_chain_stores = None

alternative_name = color = price_old = price_current = url = name_shop = address_shop = None

def parse_list_object(list_object):
    #global alternative_name, color, price_old, price_current, url, name_shop, address_shop
    print(list_object)

    start = time.time()
    url=list_object
    log.info("Парсинг list: %s",url)
    r=request(url)
    html=get_html(r)

    for elem in html.xpath(".//div[@class='c-product-tile sel-product-tile-main ']"):
        link_object=url_main+elem.xpath(".//h4[@class='e-h4 u-pb-0']/a")[0].get("href")
        object_urls.append(link_object)
        log.info(link_object)
    end = time.time()
    log.info("Количество object %s",len(object_urls))
    log.info("Спарсен за %s", end-start)

def repeat_while(param):
    if(len(param)>1):
        return param[:-1]
    else:
        return None

def parse_shop(object):
    city = object[0]
    city_name = object [2]



    url = "https://www.mvideo.ru/sitebuilder/blocks/browse/store/locator/storePickerList.json.jsp?page=1&tab=list&viewAll=true&cityId="+city
    r = request_json(url)
    log.info("Начала парсинга магазинов| %s", url)
    html = get_html_json(r["storeList"])
    li = html.cssselect('li.store-locator-list-item')
    for li in li:
        city_id = object[1]
        div_name_shop = li.cssselect('div.name')[0]
        name_shop = str(div_name_shop.cssselect('h3')[0].text.strip())
        print(name_shop)
        address_shop = str(div_name_shop.cssselect('p')[0].text.strip())
        li_id=li.get("id")
        print(li_id)

        url_shop=url_main+li.cssselect('div.store > a')[0].get("href")
        print(url_shop)

        if (address_shop.find("обл.") != -1):
            address_shop = address_shop.replace("обл.", "область")
        if (address_shop.find("МО") != -1):
            address_shop = address_shop.replace("МО", "Московская область")
        if (address_shop.find("р-н") != -1):
            address_shop = address_shop.replace("р-н", "район")
        if (address_shop.find("Всеволжский район") != -1):
            address_shop = address_shop.replace("Всеволжский район", "Всеволожский район")

        index_space = address_shop.find(",")
        city_address_shop = address_shop[:index_space]

        param1 = city_address_shop
        test_address_shop = address_shop[index_space + 2:]
        index_space2 = test_address_shop.find(",")
        param2 = test_address_shop[:index_space2]
        if (param2.find("пос") != -1):
            param2 = param2.replace("пос ", "")
        test_address_shop = test_address_shop[index_space2 + 2:]
        index_space3 = test_address_shop.find(",")
        param3 = test_address_shop[:index_space3]
        if ((name_shop.find("Пункт выдачи") == -1) and (address_shop.find("Пункт выдачи") == -1)):
            print("1:", name_shop, "2:", address_shop)

            # Проверка на уже существования магазина по параметрам
            company = "М.Видео"
            sql = """SELECT id FROM shop WHERE chain_stores_id=%s and name=%s and address=%s"""
            data = [(id_chain_stores, name_shop, address_shop)]
            row = select_request_db(sql, data)
            if (len(row) == 0):
                repeat = True
                if (city_name != city_address_shop):

                    if (name_shop.find("Мытищи") != -1):
                        sql = """SELECT id from locality where region=%s and area=%s and city=%s"""
                        data = [("Московская область", "Мытищинский район", "Мытищи")]
                        row = select_request_db(sql, data)
                        if (len(row) == 1):
                            city_id = row[0]
                            repeat = False
                    else:  #

                        if (param3.find("аул") != -1):
                            param3 = param3.replace("аул ", "")
                        print("param1", param1)
                        print("param2", param2)
                        print("param3", param3)
                        if (repeat):
                            # Попытка добавить сразу
                            sql = """SELECT id from locality where city=%s and city_2 is null"""
                            data = [(param1,)]
                            row = select_request_db(sql, data)
                            if (len(row) == 1):
                                city_id = row[0]
                                repeat = False
                        if (repeat):
                            if ((param1.find("автономн") != -1) or (param1 == "Корякский округ") or (param1 == "Камчатский край")):
                                print("Код 1")
                                exit(0)
                            else:
                                if (repeat):
                                    if (param2.find("район") != -1):
                                        start_param3 = param3
                                        while True:
                                            sql = """select id from locality where region=%s and area=%s and city like %s"""
                                            data = [(param1, param2, start_param3)]
                                            row = select_request_db(sql, data)
                                            if (len(row) == 1):
                                                city_id = row[0]
                                                repeat = False
                                                break
                                            else:
                                                if (len(row) > 0):
                                                    break
                                                else:
                                                    start_param3 = repeat_while(start_param3)
                                                    print(start_param3)
                                                    if (start_param3 == None):
                                                        break

                                        if (repeat):
                                            start_param3 = param3
                                            while True:
                                                sql = """select id from locality where region=%s and area=%s and city like %s and city_2 is null"""
                                                data = [(param1, param2, start_param3)]
                                                row = select_request_db(sql, data)
                                                if (len(row) == 1):
                                                    city_id = row[0]
                                                    repeat = False
                                                    break
                                                else:
                                                    if (len(row) > 0):
                                                        break
                                                    else:
                                                        start_param3 = repeat_while(start_param3)
                                                        print(start_param3)
                                                        if (start_param3 == None):
                                                            break
                                        if (repeat):
                                            sql = """select id from locality where region=%s and area=%s and city is null"""
                                            data = [(param1, param2)]
                                            row = select_request_db(sql, data)
                                            if (len(row) == 1):
                                                city_id = row[0]
                                                repeat = False
                                            else:
                                                print("Код 1212")
                                    else:
                                        if (repeat):
                                            start_param2 = param2
                                            while True:
                                                sql = """select id from locality where region=%s and area is null and city like %s"""
                                                data = [(param1, start_param2)]
                                                row = select_request_db(sql, data)
                                                if (len(row) == 1):
                                                    city_id = row[0]
                                                    repeat = False
                                                    break
                                                else:
                                                    if (len(row) > 0):
                                                        break
                                                    else:
                                                        start_param2 = repeat_while(start_param2)
                                                        print(start_param2)
                                                        if (start_param2 == None):
                                                            break

                                        if (repeat):
                                            start_param2 = param2
                                            while True:
                                                sql = """select id from locality where region=%s and area is null and city like %s and city_2 is null"""
                                                data = [(param1, start_param2)]
                                                row = select_request_db(sql, data)
                                                if (len(row) == 1):
                                                    city_id = row[0]
                                                    repeat = False
                                                    break
                                                else:
                                                    if (len(row) > 0):
                                                        break
                                                    else:
                                                        start_param2 = repeat_while(start_param2)
                                                        print(start_param2)
                                                        if (start_param2 == None):
                                                            break

                                        if (repeat):
                                            if ((param2.find("мкр.") != -1) or (param2.find("пос.") != -1) or (param2.find("ул.") != -1) or (
                                                    param2.find("пр-т") != -1) or (param2.find("пр-д") != -1) or (param2.find("б-р") != -1) or (
                                                    param2.find("ш.") != -1) or (param2.find("проезд") != -1) or (param2.find("шоссе") != -1) or (
                                                    param2.find("пер.") != -1)):
                                                sql = """SELECT region, autonom from locality where id=%s"""
                                                data = [(city_id,)]
                                                row_old_city = select_request_db(sql, data)
                                                start_param1 = param1
                                                while True:
                                                    sql = """SELECT id from locality where region=%s and autonom=%s and city like %s and city_2 is null"""
                                                    data = [(row_old_city[0], row_old_city[1], start_param1)]
                                                    if (row_old_city[1] == None):
                                                        sql = """SELECT id from locality where region=%s and autonom is null and city like %s and city_2 is null"""
                                                        data = [(row_old_city[0], start_param1)]
                                                    if (row_old_city[0] == None):
                                                        sql = """SELECT id from locality where region is null and autonom=%s and city like %s and city_2 is null"""
                                                        data = [(row_old_city[1], start_param1)]
                                                    print("Код 9999")
                                                    row = select_request_db(sql, data)
                                                    if (len(row) == 1):
                                                        city_id = row[0]
                                                        repeat = False
                                                        break
                                                    else:
                                                        if (len(row) > 0):
                                                            break
                                                        else:
                                                            start_param1 = repeat_while(start_param1)
                                                            print(start_param1)
                                                            if (start_param1 == None):
                                                                break
                                        if (repeat):
                                            if (city_name == "Москва"):
                                                if ((param2.find("мкр.") != -1) or (param2.find("пос.") != -1) or (param2.find("ул.") != -1) or (
                                                        param2.find("пр-т") != -1) or (param2.find("пр-д") != -1) or (param2.find("б-р") != -1) or (
                                                        param2.find("ш.") != -1) or (param2.find("проезд") != -1) or (param2.find("шоссе") != -1) or (
                                                        param2.find("пер.") != -1)):

                                                    start_param1 = param1
                                                    while True:
                                                        sql = """SELECT id from locality where region=%s and autonom is null and city like %s and city_2 is null"""
                                                        data = [("Московская область", start_param1)]
                                                        row = select_request_db(sql, data)
                                                        if (len(row) == 1):
                                                            city_id = row[0]
                                                            repeat = False
                                                            break
                                                        else:
                                                            if (len(row) > 0):
                                                                break
                                                            else:
                                                                start_param1 = repeat_while(start_param1)
                                                                print(start_param1)
                                                                if (start_param1 == None):
                                                                    break

                                        if (repeat):
                                            if (city_name == "Москва"):
                                                if ((param2.find("мкр.") != -1) or (param2.find("пос.") != -1) or (param2.find("ул.") != -1) or (
                                                        param2.find("пр-т") != -1) or (param2.find("пр-д") != -1) or (param2.find("б-р") != -1) or (
                                                        param2.find("ш.") != -1) or (param2.find("проезд") != -1) or (param2.find("шоссе") != -1) or (
                                                        param2.find("пер.") != -1)):
                                                    start_param1 = param1
                                                    while True:
                                                        sql = """SELECT id from locality where region=%s and autonom is null and area is null and city like %s and city_2 is null"""
                                                        data = [("Московская область", start_param1)]
                                                        row = select_request_db(sql, data)
                                                        if (len(row) == 1):
                                                            city_id = row[0]
                                                            repeat = False
                                                            break
                                                        else:
                                                            if (len(row) > 0):
                                                                break
                                                            else:
                                                                start_param1 = repeat_while(start_param1)
                                                                print(start_param1)
                                                                if (start_param1 == None):
                                                                    break
                    if (repeat):
                        print("Ошибка")
                        # exit(0)
                if (repeat):
                    sql = """SELECT id from locality where region=%s and city =%s and city_2 is null"""
                    data = [(param1, param2)]
                    row = select_request_db(sql, data)
                    if (len(row) == 1):
                        city_id = row[0]
                        repeat = False

                print(city_id)


                url_coordinate_shops="https://www.mvideo.ru/sitebuilder/blocks/browse/store/locator/store.json.jsp?storeId="+str(li_id)+"&hideBtn=true&skuId="
                data_shop = request_json(url_coordinate_shops)
                store_data_shop = data_shop['stores'][0]
                latitude_shop = store_data_shop['latitude']
                longitude_shop = store_data_shop['longitude']

                mode_work = li.cssselect('div.hours>p>span')[0].text.strip()
                log.info("Название: %s, Адрес: %s, Режим работы: %s", name_shop, address_shop, mode_work)
                #

                # data_unit_param=div_map.get("data-init-param")
                # print(data_unit_param)

                sql = """SELECT id FROM shop WHERE chain_stores_id=%s and name=%s and address=%s and locality_id=%s"""
                data = [(id_chain_stores, name_shop, address_shop, city_id)]
                print(data)
                row = select_request_db(sql, data)
                log.info("Выборка")
                if (len(row) == 1):
                    shop_id = row[0]
                else:
                    if (len(row) == 0):
                        sql = """INSERT INTO shop(chain_stores_id, name, address, locality_id, mode_work, url, latitude,longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                        data = [(id_chain_stores, name_shop, address_shop, city_id, mode_work, url_shop, latitude_shop, longitude_shop)]
                        shop_id = insert_request_db(sql, data)
                        log.info("Добавление")
                    else:
                        print("Ошибка")
                        exit(0)

            else:
                shop_id = row[0]
            print("ID магазина", shop_id)

def parse_object(object):
    repeat = True
    for city_data in cities:
        if (repeat == False):
            break
        url = object
        city = city_data[0]
        city_id=city_data[1]
        city_name=city_data[2]
        alternative_name = color = price_old = name = ram = rom = material= price_current = name_shop = address_shop = None
        url = url+"/shopdirections?cityId=" + city
        r = request(url)
        html = get_html(r)
        log.info("Парсинг %s",url)
        try:
            count_shops=int(html.xpath('.//li[@class="c-tabs__menu-item active"]/a/span/text()')[0])
            print(count_shops)
        except:
            count_shops=None
        if((count_shops!=None) and(count_shops>0)):
            span_showcase = html.xpath('.//span[@class="fl-embedded-wrapper"]')
            if (span_showcase != []):
                print("Тута")
                continue
            div_old = html.xpath('.//div[@class="c-pdp-price__old"]')
            if (div_old != []):
                price_old = div_old[0].text
                price_old = ''.join(filter(str.isdecimal, price_old))
                price_old=float(price_old)
                print("Старая цена:", price_old)
            price_current = html.xpath('.//div[@class="c-pdp-price__current sel-product-tile-price"]/text()')[0]
            price_current = ''.join(filter(str.isdecimal, price_current))
            price_current=float(price_current)
            print("Текущая цена:", price_current)
            code = html.xpath('.//p[@class="c-product-code"]')[0].text
            print("Код товара:", code)
            brand = html.xpath("//ul[@class='c-breadcrumbs__list']")[0].xpath("li")[-1].xpath("a/span/text()")[0]
            print("Brand", brand)

            #Парсинг параметров объекта
            url_new = url + "/specification?ssb_block=descriptionTabContentBlock&cityId=" + city
            r = request(url_new)
            html = html_bs4(r)


            div_characteristic = html.find_all('div', {"class": "product-details-tables-holder sel-characteristics-table"})[0]
            characteristic_h3 = div_characteristic.find_all("h3")
            characteristic_table = div_characteristic.find_all("table")
            count_parameters = 5
            count_current = 0
            color_repeat = False
            for i, val in enumerate(characteristic_h3):
                if (count_current < count_parameters):
                    # if (count_current < count_parameters):
                    #     if (val.text == "Корпус"):
                    #         tr = characteristic_table[i].tbody.find_all("td")
                    #         for i, value in enumerate(tr):
                    #             if (value.span.get_text().strip() == "Материал корпуса"):
                    #                 material = tr[i + 1].span.get_text().strip()
                    #                 if (material.find("/") != -1):
                    #                     material = material.replace("/", ",")
                    #                 material = material.title()
                    #                 count_current += 1
                    #                 print(material)
                    if (count_current < count_parameters):
                        if (val.text == "Серия модели"):
                            tr = characteristic_table[i].tbody.find_all("td")
                            for i, value in enumerate(tr):
                                if (value.span.get_text().strip() == "Серия"):
                                    name = brand+" "+tr[i + 1].span.get_text().strip()
                                    count_current += 1
                    if (count_current < count_parameters):
                        if (val.text == "Цвет, размеры и вес"):
                            tr = characteristic_table[i].tbody.find_all("td")
                            for i, value in enumerate(tr):
                                if (value.span.get_text().strip() == "Цвет"):
                                    color = tr[i + 1].span.get_text().strip()
                                    if(color.find("/")!=-1):
                                        color_repeat = True
                                    else:
                                        color = color.capitalize()
                                        if (color.find("Золотистый") != -1):
                                            color = "Золотой"
                                        if (color.find("Серый") != -1):
                                            color = "Серый"
                                        count_current += 1
                                        print("Цвет:",color)
                    if (count_current < count_parameters):
                        if (val.text == "Модель"):
                            tr = characteristic_table[i].tbody.find_all("td")
                            for i, value in enumerate(tr):
                                if (value.span.get_text().strip() == "Модель"):
                                    alternative_name = tr[i + 1].span.get_text().strip()
                                    alternative_name = alternative_name.upper()
                                    count_current += 1
                                    print("Альтернативное имя:",alternative_name)
                    if (count_current < count_parameters):
                        if (val.text == "Память"):
                            tr = characteristic_table[i].tbody.find_all("td")
                            for i, value in enumerate(tr):
                                if (value.span.get_text().strip() == "Оперативная память (RAM)"):
                                    ram = tr[i + 1].span.get_text().strip()
                                    ram = ram.upper()
                                    index_ram = ram.find(" ")
                                    ram = float(ram[:index_ram]) * 1024
                                    count_current += 1
                                    print("RAM:",ram)
                                if (value.span.get_text().strip() == "Встроенная память (ROM)"):
                                    rom = tr[i + 1].span.get_text().strip()
                                    rom = rom.upper()
                                    index_rom = rom.find(" ")
                                    rom = float(rom[:index_rom]) * 1024
                                    count_current += 1
                                    print("ROM:",rom)
                    if (count_current < count_parameters):
                        if (val.text == "Память"):
                            tr = characteristic_table[i].tbody.find_all("td")
                            for i, value in enumerate(tr):
                                if (value.span.get_text().strip() == "Оперативная память (RAM)"):
                                    ram = tr[i + 1].span.get_text().strip()
                                    ram = ram.upper()
                                    index_ram = ram.find(" ")
                                    ram = float(ram[:index_ram]) * 1024
                                    count_current += 1
                                    print("Ram:",ram)
                                if (value.span.get_text().strip() == "Встроенная память (ROM)"):
                                    rom = tr[i + 1].span.get_text().strip()
                                    rom = rom.upper()
                                    index_rom = rom.find(" ")
                                    rom = float(rom[:index_rom]) * 1024
                                    count_current += 1
                                    print("Rom",rom)
                    if (color_repeat):
                        if(count_current < count_parameters):
                            if (val.text == "Служебная информация"):
                                tr = characteristic_table[i].tbody.find_all("td")
                                for i, value in enumerate(tr):
                                    if (value.span.get_text().strip() == "Базовый цвет"):
                                        color = tr[i + 1].span.get_text().strip()
                                        if (color.find("/") != -1):
                                            print()
                                            #exit(0)

                                        else:
                                            color = color.capitalize()
                                            if(color.find("Золотистый")!=-1):
                                                color="Золотой"
                                            if(color.find("Серый")!=-1):
                                                color="Серый"
                                            count_current += 1
                                            print("Цвет",color)





                else:
                    break

            # request список магазинов

            log.info("%s - Имя: %s | Цвет: %s | Альтернативное имя: %s | Текущая цена: %s | Старая цена: %s",code, name, color, alternative_name, price_current, price_old)
            url_shops = 'https://www.mvideo.ru/sitebuilder/blocks/browse/product-detail/tabs/availableStoresTable.jsp?productId=' + code + '&tab=list&cityId=' + city + '&ajax=true&json=true&take-today=&page=1&viewAll=true'
            #url = 'https://www.mvideo.ru/sitebuilder/blocks/browse/product-detail/tabs/availableStoresTable.jsp?productId=30028814&tab=list&cityId=CityCZ_2246&ajax=true&json=true&take-today=&page=1&viewAll=true'

            r = request_json(url_shops)

            log.info("Начала парсинга магазинов| %s",url)
            html = get_html_json(r["storeList"])

            li = html.cssselect('li.store-locator-list-item')
            for li in li:
                city_id = object[2]
                div_pickup = li.cssselect('div.pickup')[0]
                try:
                    hours = div_pickup.cssselect('p>span')[0].text.strip()
                except IndexError:
                    continue
                try:
                    div_stock=li.cssselect('div.stock>i')[0].get('class')
                except IndexError:
                    continue

                if((div_stock.find("ico-stock-level-out-of")!=-1) or (div_stock.find("ico-stock-level-showcase")!=-1)):
                    continue
                if (hours.find("Через час") != -1):
                    div_name_shop = li.cssselect('div.name')[0]
                    name_shop = str(div_name_shop.cssselect('h3>a')[0].text.strip())
                    split_name_shop = name_shop.split(", ")
                    address_shop = str(div_name_shop.cssselect('p')[0].text.strip())
                    if(address_shop.find("обл.")!=-1):
                        address_shop=address_shop.replace("обл.", "область")
                    if(address_shop.find("МО")!=-1):
                        address_shop=address_shop.replace("МО","Московская область")
                    if(address_shop.find("р-н")!=-1):
                        address_shop=address_shop.replace("р-н", "район")
                    if(address_shop.find("Всеволжский район")!=-1):
                        address_shop=address_shop.replace("Всеволжский район", "Всеволожский район")
                    print(address_shop)
                    print(name_shop)
                    try:
                        count = li.cssselect('i.ico')[0].get("data-title")
                    except:
                        count=None
                    if((count!=None) and (count!="Привезем под заказ") and(name_shop.find("Пункт выдачи") == -1) and (address_shop.find("Пункт выдачи")==-1)):
                        print("1:",name_shop,"2:",address_shop)


                        #Проверка на уже существования магазина по параметрам
                        company = "М.Видео"
                        sql = """SELECT id FROM shop WHERE name=%s and address=%s and chain_stores_id=%s"""
                        data = [(name_shop, address_shop, 1)]
                        row = select_request_db(sql, data)
                        if(len(row)==1):
                            shop_id = row[0]
                        else:
                            print("Ошибка")
                            exit(0)

                        print("ID магазина", shop_id)

                        sql = """SELECT product.id from product where product.name=%s and product.color = %s and product.ram = %s and product.rom=%s"""
                        data = [(name, color, ram, rom)]
                        print(data)
                        row = select_request_db(sql, data)
                        print("Ответ", row)
                        if(len(row)==1):
                            product_id = row[0]
                            print("PRODUCT VARIANTION_ID",product_id)
                            try:
                                sql ="""INSERT INTO price(shop_id, product_id, price_current, price_old, status_sales,url) VALUES (%s, %s, %s, %s, %s,%s)"""
                                data = [(shop_id, product_id, price_current, price_old, 1,url)]
                                date = insert_request_db(sql, data)
                                global count_succes
                                count_succes+=1
                                print("Количество добавленных объектов", count_succes)
                            except Exception as e:
                                print("Ошибка",e)
                                print("Данные ошибки",data)
                                print("Тута")
                                exit(0)

                        else:
                            global count_lose
                            count_lose=count_lose+len(cities)
                            print("Количество недобавленных объектов",count_lose)
                            repeat = False
                            break

def start_parse_shop():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parse_shop, cities):
            pass



def start_parse_list_object():
    with ThreadPoolExecutor(count_thread) as executor1:
        for _ in executor1.map(parse_list_object, list_urls):
            pass

def start_parse_object():
    with ThreadPoolExecutor(count_thread) as executor2:
        for _ in executor2.map(parse_object, object_urls):
            pass

    # with Pool(count_thread) as p:
    #     p.map(parse_object, object_urls)

    # pool = ThreadPool(count_thread)
    # results = pool.map(parse_object, object_urls)
    # pool.close()
    # pool.join()

def update_db():
    sql = """UPDATE price, shop SET price.status_sales = 0 WHERE price.status_sales = 1 and price.shop_id = shop.id and shop.chain_stores_id = %s"""

    data = [(id_chain_stores,)]
    print(data)
    update_request_db(sql, data)

def request(url):
    while True:
        try:
            r=requests.get(url)
            if r.status_code != 200:
                log.info("Ошибка, Код ответа: %s", r.status_code)
                time.sleep(1)
                continue
            else:
                return r
        except Exception as e:
            log.info("Ошибка ConnectionError")
            time.sleep(1)

def request_json(url):
    while True:
        try:
            r = requests.get(url)
            if r.status_code != 200:
                log.info("Ошибка, Код ответа: %s", r.status_code)
                time.sleep(1)
                continue
            else:
                return r.json()
        except Exception as e:
            log.info("Ошибка ConnectionError")
            time.sleep(1)


def get_html(request):
    return lxml.html.fromstring(request.text)

def parse_city():
    r = request_json("https://www.mvideo.ru/sitebuilder/blocks/regionSelection.json.jsp?pageId=homepage&pageUrl=/&")
    #soup=BeautifulSoup(r,'lxml')
    #print(soup)
    log.info('Запрос страницы городов')
    html = lxml.html.fromstring(r["htmlContent"])
    log.info('Получение html')
    form=html.xpath("//form[@id='city-radio-from']")[0]
    li_list = form.xpath("//li")
    for li in li_list:
        elem=li.xpath("input[@name='/com/mvideo/domain/RegionSelectionFormHandler.cityId']")[0]
        city=elem.get("value")
        if(city!=""):
            log.info(city)
            city_name=li.xpath(".//label[@class='label-radio']")[0].xpath("text()")[1].strip()
            #Получение Id городов
            sql = """SELECT id FROM locality WHERE region LIKE %s and autonom is NULL and area is NULL and city is NULL AND city_2 is NULL"""
            data=[(city_name,)]
            row=select_request_db(sql,data)
            if(len(row)==1):
                city_id=row[0]
            else:
                if(len(row)==0):
                    sql = """SELECT id FROM locality WHERE city=%s and city_2 is null and area is null """
                    row=select_request_db(sql,data)
                    if(len(row)==1):
                        city_id=row[0]
                    else:
                        exit(0)

            print(city_id)
            cities.append([city, city_id,city_name])

def get_id_chain_stores():
    global id_chain_stores
    sql = """SELECT id from chain_stores where name = %s"""
    data = [("М.Видео",)]
    row = select_request_db(sql, data)
    if(len(row)==1):
        id_chain_stores = row[0]
    else:
        log.info("Ошибка получения id торговой сети")
        exit(0)

def first_list():
    print("Проблема")
    url="https://www.mvideo.ru/smartfony-i-svyaz/smartfony-205/f/page=" + str(1)
    r = request(url)
    log.info("Переход на 1 страницу")
    html = get_html(r)
    count_list = html.xpath("//a[@class='c-pagination__num c-btn c-btn_white ']/text()")[0]
    log.info("Парсинг list %s| %s",url,count_list)
    for i in range(1,int(count_list)+1):
        list_urls.append("https://www.mvideo.ru/smartfony-i-svyaz/smartfony-205/f/page=" + str(i))

def get_html_json(r):
    return lxml.html.fromstring(r)

def insert_request_db(sql,data):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="project")
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    conn.autocommit(True)
    cursor.executemany(sql, data)
    last_row_id= cursor.lastrowid
    conn.close()
    return last_row_id
def update_request_db(sql, data):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="project")
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    conn.autocommit(True)
    cursor.executemany(sql, data)
    conn.close()
def select_request_db(sql, data):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="project")
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    conn.autocommit(True)
    cursor.executemany(sql,data)
    row = cursor.fetchall()
    conn.close()

    text = list(sum(row, ()))
    return text

def html_bs4(request):
    soup = BeautifulSoup(request.text, 'lxml')
    return soup

if __name__ == "__main__":
    start_main=time.time()

    log.info('start')
    get_id_chain_stores()
    parse_city()
    start_parse_shop()
    first_list()
    start_parse_list_object()
    update_db()
    start_parse_object()
    print("Количество недобавленных телефонов",count_lose)
    print("Количество добавленных телефонов",count_succes)
    print("Процент добавленных",int(count_succes)/(int(count_succes)+int(count_lose)))
    # url=[]
    # url.append("https://www.mvideo.ru/products/smartfon-samsung-galaxy-s9-64gb-chernyi-brilliant-30032351")
    # url.append("CityCZ_2030")
    # url.append("25637")
    # url.append("Екатеринбург")
    # object=[]
    # object.append(url)
    # parse_object(object[0])
    # for i in param:
    #     print(i)

    log.info('end')
    log.info("Время работы парсера: %s",time.time()-start_main)

