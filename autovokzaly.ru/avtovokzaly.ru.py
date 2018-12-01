import asyncio
import aiohttp
import os
import time
import logging
import lxml.html
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from contextlib import suppress
from mysql.connector import MySQLConnection, Error

all = []

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

url_main = ["https://www.avtovokzaly.ru/"]

# url_main = ["https://www.avtovokzaly.ru/avtobus/saransk-nizhnij"]

error = []
error_code = []


#Костыль, предназначен для удаления названия найденного блока, чтобы сохранить, например список с Html-тегами
def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

async def request(client, url):
    global limit, headers
    for i in range(15):
        async with limit:
            try:
                async with client.get(url, headers=headers) as r:
                    log.info('Запрос: %s', url)
                    global error_code
                    if(r.status == 200):
                        return await r.text()
                    else:
                        if(r.status == 500):
                            break
                        log.info("Ошибка статус: %s", r.status)
                        await asyncio.sleep(i)
            except:
                await asyncio.sleep(i)
    error_code.append([r.status, url])

#метод преобзования ответа от сервера в дерево DOM
def get_html (request):
    return BeautifulSoup(request, 'lxml')

#Метод для вывода html, только для этапа разработки
def print_html(html):
    print(lxml.html.tostring(html, encoding='unicode', pretty_print=True))

def parse(page_text):
    try:
        urls = []
        html = get_html(page_text)
        block = html.find("div", {"id":"cities"})
        if(block != None):
            divs_list_cities = block.find_all('div', {'class': 'city-list'})
            for div_list_cities in divs_list_cities:
                urls_cities = div_list_cities.find('div').find('ul').find_all('li')
                for url_cities in urls_cities:
                    a = url_cities.find('a').get('href')
                    print(a)
                    urls.append(a)
        else:
            block = html.find('div',{'class':'city-stations half-mt'})
            if(block != None):
                trs = block.find_all('tr', {'class': 'point-data'})
                for tr in trs:
                    tds = tr.find_all('td')
                    a = tds[0].find('a').get('href')
                    urls.append(a)
                    print(a)
            else:
                block = html.find('div',{'class':'departure-list'})
                if(block != None):
                    trs = block.find_all('tr')
                    for tr in trs:
                        tds = tr.find_all('td')
                        if (len(tds) == 5):
                            a = tds[0].find('a').get('href')
                            print(a)
                            urls.append(a)
                else:
                    block = html.find('section',{'class':'js-direct-section'})
                    if(block != None):
                        temp = []
                        hash = {}
                        url = html.find('meta',{'property':'og:url'}).get("content")
                        temp.append(["url", url])
                        h1 = html.find('h1',{'class':'white'}).text  #Поработать над этим?
                        temp.append(["h1", h1])

                        print(url, h1)
                        tbodies = block.find_all('tbody',{'class':'direction-departure-row'})
                        spans = block.find_all('span')
                        for span in spans:
                            if(span.get("data-content-hash")):
                                if(span.text!= ""):
                                    hash[span.get("data-content-hash")] = span.text.strip()
                        for tbody in tbodies:
                            time_departure = tbody.find('td',{'class':'rp-from va-top'}).find('div').find('span').text.strip()
                            time_arrival = tbody.find('td',{'class':'rp-to va-top'}).find('div').find('span').text.strip()
                            temp.append(["Время отправления", time_departure])
                            print("Время отправления:", time_departure)
                            try:
                                next_day = tbody.find('td',{'class':'rp-to va-top'}).find('div').find('span',{'class':'rp-date secondary-text cursor-help'}).text.strip()
                            except AttributeError:
                                next_day = None
                            if(next_day != None):
                                time_arrival = time_arrival + " " + next_day

                            print("Время прибытия:", time_arrival)
                            temp.append(["Время прибытия", time_arrival])
                            try:
                                duration = tbody.find('td',{'class':'duration'}).find('div', {'class':''}).text.strip()
                            except AttributeError:
                                duration = None
                            temp.append(["Время в пути", duration])
                            print("Время в пути:", duration)

                            days_departure = tbody.find('td',{'class':'js-regularity c-regularity'}).find('span').text.strip()
                            temp.append(["Дни отправления", days_departure])
                            print("Дни отправления:", days_departure)

                            route = tbody.find('td', {'class':'to-route'}).find('span').text.strip()

                            print("Маршрут:", route)
                            temp.append(["Маршрут", route])
                            try:
                                price = tbody.find('td',{'class':'price-info text-center'}).find('div').text.strip()
                            except AttributeError:
                                price = None
                            print("Цена:", price)
                            temp.append(["Цены", price])
                            trs_address_block = tbody.find('tr', {'class':'dd-additional-info without-padding-vertical'})
                            if(trs_address_block == None):
                                trs_address_block = tbody.find('tr', {'class':'dd-additional-info'})

                            td_departure = trs_address_block.find('td',{'class':'rp-from'})
                            ".find('div',{'class':'point-desc'}).find('div',{'class':'secondary-text'})"
                            try:
                                td_arrival = trs_address_block.find('td',{'class':'rp-to'}).find('div',{'class':'point-desc'}).find('div',{'class':'secondary-text'})
                            except AttributeError:
                                td_arrival = None
                            address_arrival = ""
                            address_departure = ""
                            if(td_departure != None):
                                address_test = td_departure.find('span')
                                if(address_test != None):
                                    try:
                                        address_departure_hash = address_test.get("data-content-hash").strip()
                                    except AttributeError:
                                        address_departure = ""
                                    address_departure = hash[address_departure_hash]
                            if(td_arrival != None):
                                address_test = td_arrival.find('span')
                                try:
                                    address_arrival_hash = address_test.get("data-content-hash").strip()
                                except AttributeError:
                                    address_arrival = ""
                                address_arrival = hash[address_arrival_hash]
                            try:
                                place_departure = tbody.find('td',{'class':'rp-from va-top'}).find('div',{'class':'point-desc small-mt'}).find('span').text.strip()
                                if(place_departure == ""):
                                    place_departure = tbody.find('td',{'class':'rp-from va-top'}).find('div',{'class':'point-desc small-mt'}).find('a').text.strip()
                            except AttributeError:
                                place_departure = ""
                            place_departure = place_departure + "\n" + address_departure
                            print("Место отправления:", place_departure)
                            temp.append(["Место отправления", place_departure])

                            try:
                                place_arrival  = tbody.find('td',{'class':'rp-to va-top'}).find('div',{'class':'point-desc small-mt'}).find('span').text.strip()
                                if(place_arrival == ""):
                                    place_arrival = tbody.find('td',{'class':'rp-to va-top'}).find('div',{'class':'point-desc small-mt'}).find('a').text.strip()
                            except AttributeError:
                                place_arrival = ""
                            place_arrival = place_arrival + "\n" + address_arrival
                            print("Место прибытия:", place_arrival)
                            temp.append(["Место прибытия", place_arrival])
                            try:
                                transport_company = (tbody.find('tr', {
                                'class': 'last-for-compact without-padding-top with-bottom-border '})).find('td').find('div', {'class':'compact-company-name display-table full-width'}).find('div',{'class':'table-cell va-middle'}).text.strip()
                            except AttributeError:
                                try:
                                    transport_company = (tbody.find('tr', {
                                        'class': 'last-for-compact without-padding-top with-bottom-border sale-enabled'})).find(
                                        'td').find('div', {'class': 'compact-company-name display-table full-width'}).find(
                                        'div', {'class': 'table-cell va-middle'}).text.strip()
                                except AttributeError:
                                    transport_company = tbody.find('tr',{'class':'last-for-compact without-padding-top with-bottom-border validate-expired '}).find('div',{'class':'table-cell va-middle'}).text.strip()
                            print("Транспортная компания:", transport_company)
                            temp.append(["Транспортная компания", transport_company])

                            try:
                                departure_numbers = tbody.find_all('tr', {'class':'dd-additional-info without-padding-vertical'})[-1].find('td',{'class':'rp-from va-top'}).find_all('div', {'class':'departure-phone-info'})
                            except IndexError:
                                departure_numbers = None
                            except AttributeError:
                                departure_numbers = None
                            departure_full = ""
                            if(departure_numbers != None):
                                for departure_number_text in departure_numbers:
                                    departure_number_full = departure_number_text.find('div').find('span')

                                    departure_number_hash = departure_number_full.get("data-content-hash").strip()
                                    departure_number = hash[departure_number_hash]

                                    departure_full = departure_full + "\n" + departure_number


                                    departure_number_full_address = departure_number_text.find('div', {
                                        'class': 'phone-desc secondary-text'}).find('span')
                                    if(departure_number_full_address != None):
                                        departure_number_address_hash = departure_number_full_address.get(
                                            'data-content-hash').strip()
                                        departure_number_address = hash[departure_number_address_hash]
                                        departure_number_address = "(" + departure_number_address + ")"
                                        departure_full = departure_full + "\n"+ departure_number_address

                            print("Телефон отбытия:", departure_full)
                            temp.append(["Телефон отбытия", departure_full])


                            all.append(dict(temp))


                            print("---------------------------------------------------------------------------------------------")
    except:
        print("Ошибка Х",url)
        exit(0)




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

    pd.DataFrame(all).to_excel(r'products.xlsx', index=False, encoding='utf-8')
    log.info('Время работы: %s', time.time() - start_time)
    for err in error_code:
        print("Код:", err)