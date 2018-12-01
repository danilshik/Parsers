from concurrent.futures import ThreadPoolExecutor
# from multiprocessing.dummy import Pool as ThreadPool
# from multiprocessing import Pool
import time
import requests, requests.utils
import logging
import lxml.html
count_thread = 50
count_games = 0
list_games = []

url_games = []
url_main="https://store.steampowered.com/search/?sort_by=Released_DESC&tags=-1&category1=996%2C998&page="
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

cookies = dict(mature_content = '1', birthtime ='220906801')


def parse_url_list_games():
    r = request(url_main+str(1))
    html = get_html(r)

    navigation = html.cssselect('div.search_pagination_right')[0]
    navigation_a = navigation.cssselect('a')[-2].text

    for i in range(1, int(navigation_a) + 1):
        list_games.append(url_main+str(i))

    for i in list_games:
        print(i)






def request(url):
    global cookies, headers
    try:
        r = requests.get(url, cookies=cookies, headers=headers)
        assert (r.status_code == 200), ("Ошибка, Код ответа: ", r.status_code, url)
    except Exception as e:
        print(e)
        time.sleep(1)
        return request(url)
    else:
        return r


def get_html(request):
    return lxml.html.fromstring(request.text)

def parse_list_games(url):
    print("Текущий",url)
    r = request(url)
    html = get_html(r)

    left_panel = html.cssselect('div.leftcol')[0]
    search_result_container = left_panel.cssselect('#search_result_container')[0]
    items = search_result_container.cssselect('a.search_result_row')
    for item in items:

        href = item.get('href')
        url_games.append(href)
        name = item.cssselect('span.title')[0].text
        div_block_price_discount = item.cssselect('div.search_price_discount_combined')[0]
        try:
            discount = div_block_price_discount.cssselect('div.search_discount>span')[0].text[1:-1]
        except IndexError:
            discount = None
        price_block = div_block_price_discount.cssselect('div.search_price')[0]
        try:
            price_old_rub = price_block.cssselect('span>strike')[0].text[:-5]
        except IndexError:
            price_old_rub = None
        if(price_block.text.strip()==""):
            price_current_rub = None
        else:
            price_current_rub = price_block.text.strip()[:-5]

        app_id = item.get('data-ds-appid')
        log.info(" %s - Название: %s, Текущая цена: %s, Старая цена: %s, Скидка: %s - %s", app_id, name, price_current_rub, price_old_rub, discount, href)


    print("Количество игр: ",str(len(url_games)))


def print_html(html):
    print(lxml.html.tostring(html, pretty_print=True, encoding='utf-8').decode('utf-8'))

def get_html_json(r):
    return lxml.html.fromstring(r)

def start_parse_list_games():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parse_list_games, list_games):
            pass




if __name__ == "__main__":

    start_main = time.time()
    parse_url_list_games()    #1 поток

    # list_games.append("https://store.steampowered.com/search/?sort_by=Released_DESC&tags=-1&category1=996%2C998")
    start_parse_list_games()


    log.info('start')

    log.info('end')
    log.info("Время работы парсера: %s",time.time()-start_main)




