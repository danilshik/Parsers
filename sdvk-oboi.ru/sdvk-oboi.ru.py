import asyncio
import aiohttp
import os
import time
import logging
import lxml.html
import httplib2
import random
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import re
import json
log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
len_count_product = 0
count_thread = os.cpu_count()

limit = asyncio.Semaphore(2)  #Количество одновременных запросов, которые были отправлены серверы, но еще не получен от них ответ. Не означает одновременную отправку 10 запросов
count_request_product = 0
proxy_list = []
headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

# url_main = ["https://sdvk-oboi.ru/oboi/Zambaiti_Parati/Canto_2017/54948/"]
url_main = ["https://sdvk-oboi.ru/sitemap.xml"]

type_http = "https:"
#Костыль, предназначен для удаления названия найденного блока, чтобы сохранить, например список с Html-тегами
def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

def download_image(url):
    # Скачивание изображения
    h = httplib2.Http('cache')
    response, content = h.request(url)
    out = open('image/' + url, 'wb')
    out.write(content)
    out.close()

async def request(client, url):
    global limit, headers,  len_count_product, count_request_product
    async with limit:
        for i in range(50):
            try:
                async with client.get(url, headers=headers) as r:
                    log.info('Запрос: %s', url)
                    log.info("Статус: %s", r.status)
                    if(r.status == 404):
                        break
                    if(r.status == 200):
                        count_request_product = count_request_product + 1
                        log.info("Количество запросов: %s", str(count_request_product))
                        return await r.content.read()
                    else:
                        log.info("Ошибка статус: %s", r.status)
                        log.info("Задержка: %s", i)
                        await asyncio.sleep(1)
            except Exception as e:
                print(e)
                log.info("Задержка: %s", i)
                await  asyncio.sleep(1)

#метод преобзования ответа от сервера в дерево DOM
def get_html (request):
    return lxml.html.fromstring(request)

def parse_xml(page_text):
    return etree.XML(page_text)

#Метод для вывода html, только для этапа разработки
def print_html(html):
    print(lxml.html.tostring(html, encoding='unicode', pretty_print=True))

def parse(page_text):
    global len_count_product, proxy_list, type_http
    urls = []
    html = get_html(page_text)
    try:
        block = html.cssselect("urlset")[0]
        type = "main"
    except IndexError:
        type = "product"
    if(type == "main"):
        for url in html.cssselect('url>loc'):
            #Регулярка для поиска товаров
            text = re.search("\/[0-9]+\/$", url.text)
            if (text != None):
                urls.append(url.text)

    elif(type == "product"):
        try:
            name = html.cssselect("h1[itemprop='name']")[0].text
        except:
            name = None
        print(name)
        try:
            price = html.cssselect('#item-price')[0].text
        except:
            price = None
        print(price)

        ul = html.cssselect('ul.list-options')[0]
        print_html(ul)
        try:
            url_main_photo = type_http + html.cssselect("div.main-photo ")[0].get("data-fancybox-href")
        except:
            url_main_photo = None
        print(url_main_photo)
        download_image(url_main_photo)

        urls_image_list = []
        block_images = html.cssselect('#collection_photo>div>a')
        for block in block_images:
            urls_image_list.append(type_http + block.get("href"))

        print(urls_image_list)


    # len_count_product = len(urls)
    print(len_count_product)
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
        loop.run_until_complete(start_main(url_main))
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks():
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
    finally:
        loop.close()
    print("Время работы парсера:", time.time() - start_time)

    # pd.DataFrame(all).to_excel(r'products.xlsx', index=False, encoding='utf-8')
