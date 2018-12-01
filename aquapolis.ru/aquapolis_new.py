# encoding: utf-8
import requests
import time
import logging
import lxml.html
from lxml.cssselect import CSSSelector as cssselect
import numpy as np
import pandas as pd
import csv

errors = []
categories_data = []
filename_category = "category.csv"
url_data = "error.txt"


log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)


headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

url_page_category = "https://aquapolis.ru/catalog/seo_sitemap/category/"
url_page_product = "https://aquapolis.ru/catalog/seo_sitemap/product/"


categories = None
count_index_category = 0
count_request_product = 0

#Метод для определения количества отправленных запросов к серверу, служит для отображения процента выполненных запросов
def count_request_product_add():
    global count_request_product
    count_request_product = count_request_product + 1
    return count_request_product

#Инициализация файла с категориями, в будущем изменю на более элегантное решение
def initialization():
    global categories_data
    headers = ["CATEGORY_ID", "PARENT_CATEGORY_ID", "CATEGORY_NAME", "CATEGORY_URL"]
    categories_data.append(headers)

#Общий счетчик индексов категорий,
def index_add():
    global count_index_category
    count_index_category = count_index_category +1
    return count_index_category

#Костыль, предназначен для удаления названия найденного блока, чтобы сохранить, например список с Html-тегами
def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

#Метод для отправки http-запросов
def request(url):
    global cookies, headers
    try:
        r = requests.get(url, headers=headers)
        assert (r.status_code == 200), ("Ошибка, Код ответа: ", r.status_code, url)
    except Exception as e:
        print(e)
        time.sleep(5)
        return request(url)
    else:
        return r.text

#метод преобзования ответа от сервера в дерево DOM
def get_html (request):
    return lxml.html.fromstring(request)



#Метод для вывода html, только для этапа разработки
def print_html(html):
    print(lxml.html.tostring(html, encoding='unicode', pretty_print=True))

#метод парсинга главной страницы с категориями
def parsing_main_list_category(url):
    urls = []
    r = request(url)
    html = get_html(r)
    div_number_list = html.cssselect('div.pages.gen-direction-arrows1')[0]
    count_pagination = div_number_list.cssselect('ol>li>a')[-2].text
    log.info('Количество страниц категорий: %s', count_pagination)
    for i in range(1,int(count_pagination)+1):
        url = 'https://aquapolis.ru/catalog/seo_sitemap/category/?p='+str(i)
        log.info('Страница с категориями: %s', url)
        urls.append(url)
    return urls

#Асинхронный метод парсинга главной страницы с продуктами
def parsing_main_list_product(url):
    result = []
    r = request(url)
    html = get_html(r)
    div_number_list = html.cssselect('div.pages.gen-direction-arrows1')[0]
    count_pagination = div_number_list.cssselect('ol>li>a')[-2].text
    log.info('Количество страниц c продуктами: %s', count_pagination)
    for i in range(1, int(count_pagination) + 1):
        url = 'https://aquapolis.ru/catalog/seo_sitemap/product/?p=' + str(i)
        log.info('Страница с продуктами: %s', url)
        result.append(url)
    return result


#Парсинг страницы категории
def parsing_category(urls_category):
    global categories_data, filename_category
    for url_category in urls_category:
        parent_category_one = 0
        parent_category_two = 0
        r = request(url_category)
        log.info("Запрос страницы с категориями: %s", url_category)
        html = get_html(r)

        ul = html.cssselect('ul.sitemap')[0]
        li_list = ul.cssselect('li')
        for li in li_list:
            li_class = li.get('class')
            if(li_class=='level-0'):
                parent_category = 0
                a = li.cssselect('a')[0]
                category_name = a.text
                category_url = a.get('href')

                temp = [index_add(), parent_category, category_name, category_url]

                categories_data.append(temp)
                parent_category_one = categories_data[-1][0]

                log.info('PARENT_CATEGORY_ID: %s, CATEGORY_NAME: %s, CATEGORY_URL: %s', parent_category, category_name, category_url)
            else:
                if(li_class == "level-1"):
                    a = li.cssselect('a')[0]
                    parent_category = parent_category_one

                    category_name = a.text
                    category_url = a.get('href')

                    temp = [index_add(), parent_category, category_name, category_url]

                    categories_data.append(temp)
                    parent_category_two = categories_data[-1][0]
                else:
                    if(li_class == "level-2"):

                        parent_category = parent_category_two

                        a = li.cssselect('a')[0]

                        category_name = a.text
                        category_url = a.get('href')

                        temp = [index_add(), parent_category, category_name, category_url]

                        categories_data.append(temp)

    with open(filename_category, "w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(categories_data)

#Парсинг страницы с продуктами
def parsing_list_product(urls):
    result = []
    for url in urls:
        r = request(url)
        html = get_html(r)
        a_list = html.cssselect('ul.sitemap>li>a')
        for a in a_list:
            href = a.get('href')
            result.append(href)
            log.info('Ссылка на товар:%s', href)
    print(len(result))
    return result

#Получения индекса у добавленной категории
def get_index_category(words):
    global categories_data
    for item in categories_data:
        if(item[2] == words):
            return item[0]

#Служит для получения ссылки на страницу с какими либо ошибками, с помощью lxml не удалось получить, пришлось с Beautiful Sotp


#Парсинг продукта
def parsing_product(urls_product):
    count = 0
    len_url = len(urls_product)
    all_products = []

    for url_product in urls_product:
        count = count + 1
        temp = []
        product_data = []

        r = request(url_product)
        html = get_html(r)


        url = url_product
        product_data.append(["URL", url])

        try:
            li_category = html.cssselect('div.grid-full.breadcrumbs>ul>li')[-3].cssselect('a>i')[0].text
        except:
            errors.append([6, url])       #Что тут делать? Определить категорию
            li_category = None
        if(li_category != None):
            product_data.append(["CATEGORY_ID", int(get_index_category(li_category))])
            sku = html.cssselect('div.sku')[0]
            sku_span = sku.cssselect('span')[0]
            sku = sku_span.tail
            product_data.append(["SKU", sku])

            #Определение типа страницы
            try:
                product_group_block = html.cssselect('#super-product-table')[0]
                product_group = True
            except:
                product_group = False

            #Общая часть
            image_list = html.cssselect('a.cloud-zoom-gallery.lightbox-group')
            images_url = []
            for image in image_list:
                images_url.append(image.get('href'))
            try:
                image = images_url[0]
            except:
                image = None
            try:
                images = images_url[1:]
            except:
                images = None
            product_data.append(["IMAGE", image])
            product_data.append(["IMAGES", images])

            table_additional_information = html.cssselect('#product-attribute-specs-table>tbody')[0]
            tr_list = table_additional_information.cssselect('tr')
            for index, tr in enumerate(tr_list):
                one_block = tr.cssselect('th')[0].text
                two_block = tr.cssselect('td')[0]
                if(one_block == "Производитель"):
                    manufacturer = two_block.text
                    product_data.append(["MANUFACTURER", manufacturer])
                    continue
                if(one_block == "Страна производитель"):
                    country_of_origin = two_block.text
                    product_data.append(["COUNTRY_OF_ORIGIN", country_of_origin])
                    continue
                if(one_block == "Скачиваемые материалы"):
                    try:
                        download_materials = two_block.cssselect('a')[0].get("href")

                    except IndexError:
                        download_materials = None

                    product_data.append(["Скачиваемые материалы", download_materials])
                    continue
                ul_two_block = two_block.cssselect('ul')
                if (len(ul_two_block) == 0):
                    two_block = two_block.text
                else:
                    two_block = ''.join(to_string(child) for child in two_block.iterchildren())
                product_data.append([one_block, two_block])
            try:
                description = html.cssselect('div.short-description>div')[0].text
            except IndexError:
                description = None
            product_data.append(["DESCRIPTION", description])
            try:
                description_feature_block = html.cssselect('div.short-description>div>ul')[0]
                description_feature = (''.join(to_string(child) for child in description_feature_block.iterchildren()))
            except:
                description_feature = None
            product_data.append(["DESCRIPTION_FEATURE", description_feature])

            if(product_group):
                table_products = html.cssselect('#super-product-table>tbody')[0]
                tr_list = table_products.cssselect('tr')
                for index,tr in enumerate(tr_list):
                    product_data_temp = []
                    td_list = tr.cssselect('td')
                    name = td_list[0].text
                    product_data_temp.append(["NAME", name])
                    try:
                        price = td_list[1].cssselect('span.regular-price>span.price')[0].text.strip()[:-5]
                    except:
                        try:
                            price = td_list[1].cssselect('p.special-price>span.price')[0].text.strip()[:-5]
                        except:
                            price = None
                    product_data_temp.append(["PRICE", price])
                    try:
                        stock_status = td_list[1].cssselect('span.ampreorder_note')[0].text
                    except:

                        try:

                            stock_status = td_list[2].cssselect('input')[0].get('value')

                            if stock_status == "0":
                                stock_status = "Доступен под заказ"
                            if stock_status == "1":
                                stock_status = "Есть в наличии"
                        except:
                            try:
                                stock_status = td_list[2].cssselect('p.availability>span')[0].text
                            except:
                                stock_status = None

                    product_data_temp.append(["STOCK_STATUS", stock_status])
                    product_data_temp = product_data_temp + product_data  #Конструкция для слияния общих характеристик и
                    # индивидуальных характеристик каждого товара в группе
                    product_data_dict = dict(product_data_temp)
                    temp.append(product_data_dict)


                    all_products.append(product_data_dict)

            else:
                name = html.cssselect('div.product-name>h1')[0].text.strip()
                product_data.append(["NAME", name])
                product_type_data = html.cssselect('div.product-type-data')[0]
                try:
                    price = product_type_data.cssselect('span.regular-price>span')[0].text.strip()[:-5]
                except:
                    try:
                        price = product_type_data.cssselect('p.special-price>span.price')[0].text.strip()[:-5]
                    except:
                        price = None
                product_data.append(["PRICE", price])
                try:
                    stock_status = product_type_data.cssselect('p.availability>span>link')[0].get('itemprop')
                    if(stock_status == "availability"):
                        stock_status = "Есть в наличии"
                    else:
                        errors.append([11, url, stock_status])
                except IndexError:
                    try:
                        stock_status = product_type_data.cssselect('p.availability>span')[0].text
                    except:
                        errors.append([10, url]) #Нужно тоже разобраться с этим
                        stock_status = None
                product_data.append(["STOCK_STATUS", stock_status])
                product_data_dict = dict(product_data)
                all_products.append(product_data_dict)
            log.info("Обработка страницы: %s : %s",url, str(count/len_url * 100))
    return all_products

#Асинхронный метод для запуска процессов парсинга, короутин, потоков
def start_main():
    results = []
    urls_list_category = parsing_main_list_category(url_page_category)
    parsing_category(urls_list_category)

    urls_list_product = parsing_main_list_product(url_page_product)
    print ("jhjhjh")
    urls_product = parsing_list_product(urls_list_product)
    print("gfhgfhg")
    all_products = parsing_product(urls_product)

    pd.DataFrame(all_products).to_csv(r'products.csv', index=False, encoding='utf-8')


if __name__ == '__main__':
    start_time = time.time()
    initialization()
    start_main()
    #Сохранение страниц с ошибками в файл
    with open("error.txt", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(errors)

    print("Количество неправильных url:", len(errors))
    log.info('Время работы: %s',time.time() - start_time)