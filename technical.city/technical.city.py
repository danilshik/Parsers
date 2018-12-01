import asyncio
import aiohttp
import os
import time
import logging
import lxml.html
import json
from concurrent.futures import ThreadPoolExecutor

from contextlib import suppress
from mysql.connector import MySQLConnection, Error

db_bd = "technical_city"
db_user = "root"
db_password = ""
db_host = "localhost"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

count_thread = os.cpu_count()
limit = asyncio.Semaphore(50)  #Количество одновременных запросов, которые были отправлены серверы, но еще не получен от них ответ. Не означает одновременную отправку 10 запросов

headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

url_main_list = ["https://technical.city/en/cpu/history", "https://technical.city/en/video/history"]

main_type = "https://technical.city"

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

def add_device(name, type, url):
    sql_query = "SELECT id FROM device WHERE name = %s and type = %s LIMIT 1"
    data = (name, type)
    rows = select_database(sql_query, data)
    if(len(rows) == 1):
        return rows[0][0]
    else:
        if(len(rows) == 0):
            sql_query = "INSERT INTO device (name, type) VALUES (%s, %s)"
            return insert_database(sql_query, data)

def add_device_variables(name, group_variables):
    sql_query = "SELECT id FROM device_variables WHERE name = %s and block = %s LIMIT 1"
    data = (name, group_variables)
    rows = select_database(sql_query, data)
    if (len(rows) == 1):
        return rows[0][0]
    else:
        if (len(rows) == 0):
            sql_query = "INSERT INTO device_variables (name, block) VALUES (%s, %s)"
            return insert_database(sql_query, data)

def add_device_value(device_id, device_variables_id, value):
    sql_query = "SELECT id FROM device_values WHERE device_id = %s and device_variables_id = %s and value =%s LIMIT 1"
    data = (device_id, device_variables_id, value)
    rows = select_database(sql_query, data)
    if (len(rows) == 1):
        return rows[0][0]
    else:
        if (len(rows) == 0):
            sql_query = "INSERT INTO device_values (device_id, device_variables_id, value) VALUES (%s, %s, %s)"
            return insert_database(sql_query, data)

#Костыль, предназначен для удаления названия найденного блока, чтобы сохранить, например список с Html-тегами
def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

async def request(client, url):
    global limit, headers
    while True:
        async with limit:
            try:
                async with client.get(url, headers=headers) as r:
                    log.info('Запрос: %s', url)
                    if(r.status == 200):
                        return await r.text()
                    else:
                        log.info("Ошибка статус:", r.status)
                        time.sleep(0.01)
            except:
                time.sleep(0.01)

#метод преобзования ответа от сервера в дерево DOM
def get_html (request):
    return lxml.html.fromstring(request)

#Метод для вывода html, только для этапа разработки
def print_html(html):
    print(lxml.html.tostring(html, encoding='unicode', pretty_print=True))

def parse(page_text):
    urls = []
    html = get_html(page_text)
    url = html.cssselect('link[rel = "canonical"]')[0].get('href')
    print("URL:", url)
    breadcrumbs = html.cssselect('div.breadcrumbs>span.almost_bold')[0].text
    if (breadcrumbs == "History"):
        pagination = int(html.cssselect('div.rating_pagination.pagination>span')[0].text)
        if(pagination == 1):
            rating_pagination = html.cssselect("div.rating_pagination.pagination")[0]
            a_list = rating_pagination.cssselect('div.rating_pagination.pagination>a')
            for a in a_list:
                urls.append(main_type + a.get("href"))
        href_list = []
        a_list = html.cssselect('table.rating.responsive>tr:not([class])>td[style="text-align:left"]>a')
        for a in a_list:
            href_list.append(main_type + a.get("href"))

        href_list = list(set(href_list))
        for href in href_list:
            urls.append(href)
    else:
        type = html.cssselect('div.breadcrumbs>span[itemprop = "itemListElement"]')[1].cssselect('a')[0].get('title')
        group_list = html.cssselect('div.tbt2.row_heading>div>h2')[1:]
        title = html.cssselect('meta[property = "og:title"]')[0].get("content")
        # print("Название", title)
        id_device = add_device(title, type, url)
        # print("Идентификатор продукта", id_device)
        tables = html.cssselect('div.tbt1.single>div.table')
        # print(len(tables))
        for index, table in enumerate(tables):
            group = group_list[index].text
            tbts = table.cssselect('div.tbt5')
            for tbt in tbts:
                divs = tbt.cssselect('div')
                one_block = divs[1].text
                #Прерываем ошибочные таблицs
                if(one_block == None):
                    # add = False
                    break
                two_block = divs[2].text
                if(two_block == None):
                    try:
                        two_block = divs[2].cssselect('span')[0].text
                    except:
                        two_block = divs[2].cssselect('a')[0].text
                if(two_block == "+"):
                    two_block = 1
                else:
                    if(two_block == "-"):
                        two_block = 0
                # print("Группа:", group)
                id_device_variables = add_device_variables(one_block, group)
                # print("Идентификатор VARIABLE:", id_device_variables)
                id_device_value = add_device_value(id_device, id_device_variables, two_block)

    return urls


async def crawl(future, client, pool):
    futures = []
    # Получаем из футуры ссылки
    urls = await future
    # Выгребаем для каждой ссылки разметку страницы
    for request_future in asyncio.as_completed([request(client, url) for url in urls]):
        # Передаём парсинг разметки в пул потоков
        parse_future = loop.run_in_executor(pool, parse, (await request_future))
        # parse_future = loop.run_in_executor(pool, parse, (await request_future))
        # Рекурсивно вызываем себя для парсинга новой порции ссылок
        futures.append(asyncio.ensure_future(crawl(parse_future, client, pool)))
    # Это нужно только для того, чтобы знать
    # когда завершать цикл событий
    if futures:
        await asyncio.wait(futures)

async def start_main(root_urls):
    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    # Создаём пул потоков по количеству процессоров
    # with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
    with ThreadPoolExecutor(count_thread) as pool:
        # Создаём клиентскую сессию
        async with aiohttp.ClientSession() as client:
            # Создаём корневую футуру
            initial_future = loop.create_future()
            # Помещаем в неё ссылки, с которых начнём парсить
            initial_future.set_result(root_urls)
            # Передаём эту футуру в сопрограмму обхода ссылок
            # вместе с пулом потоков и клиентской сессией
            await crawl(initial_future, client, pool)


if __name__ == '__main__':
    start_time = time.time()

    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    try:
        loop.run_until_complete(start_main(url_main_list))
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks():
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
    finally:
        loop.close()
    log.info('Время работы: %s', time.time() - start_time)