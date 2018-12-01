import asyncio
import aiohttp
import os
import time
import logging
import lxml.html
from collections import OrderedDict

import  requests

from contextlib import suppress
from mysql.connector import MySQLConnection, Error

db_bd = "hardware"
db_user = "root"
db_password = ""
db_host = "localhost"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

# logging.basicConfig(level=logging.DEBUG)


headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

url_main_list = ["https://technical.city/en/cpu/history", "https://technical.city/en/video/history"]

main_url = "https://technical.city"

urls_product = []

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

def add_device(name, type):
    if(type == "Video Cards"):
        sql_query = "SELECT id FROM gpu WHERE name = %s LIMIT 1"
    else:
        sql_query = "SELECT id FROM cpu WHERE name = %s LIMIT 1"
    data = (name,)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            if(type == "Video Cards"):
                sql_query = "INSERT INTO gpu (name) VALUES (%s)"
            else:
                sql_query = "INSERT INTO cpu (name) VALUES (%s)"
            return insert_database(sql_query, data)

def add_device_variables(name, group_variable, type, type_variables):
    if (type == "Video Cards"):
        sql_query = "SELECT id FROM gpu_variable WHERE name = %s and group_name = %s LIMIT 1"
    else:
        sql_query = "SELECT id FROM cpu_variable WHERE name = %s and group_name = %s LIMIT 1"
    data = (name, group_variable)
    rows = select_database(sql_query, data)
    if (len(rows) == 1):
        return rows[0][0]
    else:
        if (len(rows) == 0):
            if (type == "Video Cards"):
                sql_query = "INSERT INTO gpu_variable (name, group_name, type) VALUES (%s, %s, %s)"
            else:
                sql_query = "INSERT INTO cpu_variable (name, group_name, type) VALUES (%s, %s, %s)"
            data = (name, group_variable, type_variables)
            return insert_database(sql_query, data)

def add_device_value(gpu_id, gpu_variable_id, value, type):
    if (type == "Video Cards"):
        sql_query = "SELECT id FROM gpu_value WHERE gpu_id = %s and gpu_variable_id = %s and value =%s LIMIT 1"
    else:
        sql_query = "SELECT id FROM cpu_value WHERE cpu_id = %s and cpu_variable_id = %s and value =%s LIMIT 1"
    data = (gpu_id, gpu_variable_id, value)
    rows = select_database(sql_query, data)
    if (len(rows) == 1):
        return rows[0][0]
    else:
        if (len(rows) == 0):
            if (type == "Video Cards"):
                sql_query = "INSERT INTO gpu_value (gpu_id, gpu_variable_id, value) VALUES (%s, %s, %s)"
            else:
                sql_query = "INSERT INTO cpu_value (cpu_id, cpu_variable_id, value) VALUES (%s, %s, %s)"
            return insert_database(sql_query, data)

#Костыль, предназначен для удаления названия найденного блока, чтобы сохранить, например список с Html-тегами
def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

def request(url):
    global limit, headers
    while True:
        try:
            r = requests.get(url, headers=headers)
            log.info('Запрос: %s', url)
            if(r.status_code == 200):
                return r.text
            else:
                log.info("Ошибка статус:", r.status)
                time.sleep(1)
        except Exception as e:
            time.sleep(1)
            print("Ошибка:", e)

#метод преобзования ответа от сервера в дерево DOM
def get_html (request):
    return lxml.html.fromstring(request)

#Метод для вывода html, только для этапа разработки
def print_html(html):
    print(lxml.html.tostring(html, encoding='unicode', pretty_print=True))

def parse(url_current, type_parse):
    global urls_product
    r = request(url_current)
    html = get_html(r)
    if(type_parse == "main"):
        a_list = html.cssselect('div.rating_pagination.pagination>a')
        urls = [main_url + a_list[0].get("href")[:-1] + str(1)]
        for a in a_list:
            urls.append(main_url + a.get("href"))
            log.info("Тип страницы: %s, URL: %s", "Страница со списком продуктов", url_current)
        for url in urls:
            parse(url, "list")
    else:
        if(type_parse == "list"):
            href_list = []
            tds = html.cssselect('td[style="text-align:left"]')
            for td in tds:
                a = td.cssselect('a')[-1]
                href_list.append(main_url + a.get("href"))
            href_list = list(dict.fromkeys(href_list))
            for href in href_list:
                log.info("Тип страницы: %s, URL: %s", "Страница товара", href)
                urls_product.append(href)
        else:
            if(type_parse == "product"):
                type = html.cssselect('div.breadcrumbs>span[itemprop = "itemListElement"]')[1].cssselect('a')[0].get('title')
                group_list = html.cssselect('div.tbt2.row_heading>div>h2')[1:]
                title = html.cssselect('meta[property = "og:title"]')[0].get("content")
                # print("Название", title)
                id_device = add_device(title, type)
                # print("Идентификатор продукта", id_device)
                tables = html.cssselect('div.tbt1.single>div.table')
                # print(len(tables))
                for index, table in enumerate(tables):
                    group = group_list[index].text
                    tbts = table.cssselect('div.tbt5')
                    for tbt in tbts:
                        divs = tbt.cssselect('div')
                        one_block = divs[1].text
                        type_text = ""
                        #Прерываем ошибочные таблицs
                        if(one_block == None):
                            break
                        two_block = divs[2].text
                        if(two_block == None):
                            try:
                                two_block = divs[2].cssselect('span')[0].text
                            except:
                                two_block = divs[2].cssselect('a')[0].text
                        if(two_block == "+"):
                            two_block = 1
                            type_text = "bool"
                        else:
                            if(two_block == "-"):
                                two_block = 0
                                type_text = "bool"
                        if(type_text !="bool"):
                            try:
                                test_type = float(two_block)
                                type_text = "float"
                            except ValueError:
                                try:
                                    test_type = int(two_block)
                                    type_text = "int"
                                except ValueError:
                                    type_text = "string"


                        # print("Группа:", group)
                        id_device_variables = add_device_variables(one_block, group, type, type_text)
                        # print("Идентификатор VARIABLE:", id_device_variables)
                        id_device_value = add_device_value(id_device, id_device_variables, two_block, type)










if __name__ == '__main__':
    start_time = time.time()
    for url in url_main_list:
        parse(url, "main")

    #Обратный цикл
    len_list = len(urls_product)
    for index, url_product in enumerate(reversed(urls_product)):
        parse(url_product, "product")
        procent =  str(100 * (index + 1)/len_list)
        log.info("Тип страницы: %s, URL: %s - %s ", "Продукт", url_product, str(100 * (index + 1)/len_list))



    print("Время работы:", time.time() - start_time)
