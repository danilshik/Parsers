from concurrent.futures import ThreadPoolExecutor
import time
import requests, requests.utils, pickle
import logging
import lxml.html
param = []
count_lose = 0
count_succes = 0
count_thread = 25
count_games = 0
list_games = []
url_games = []
time_time = []
dlc_url = []
set_url = []
isFirst = True
url_main="https://store.steampowered.com/search/?sort_by=Released_DESC&tags=-1&category1=998&page="
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


platform_errors = []


headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

cookies = dict(mature_content = '1', birthtime ='220906801')

game_features = []

def to_string(node):
    return lxml.html.tostring(node, encoding='unicode')

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
        time.sleep(5)
        return request(url)
    else:
        return r

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

def get_html_request(request):
    return lxml.html.fromstring(request)

def parse_list_games(url):
    print("Текущий",url)
    r = request(url)
    html = get_html(r)
    left_panel = html.cssselect('div.leftcol')[0]
    search_result_container = left_panel.cssselect('#search_result_container')[0]
    item = search_result_container.cssselect('a.search_result_row')
    for item in item:
        href = item.get('href')
        url_games.append(href)
        name = item.cssselect('span.title')[0].text
        log.info("Название: %s - %s", name, href)
    print("Количество игр: ",str(len(url_games)))


def parse_game(url):
    global count_succes, count_games
    tags = []
    developers = []
    publishers = []
    images = []
    genres = []
    languages = []
    platforms = []
    apps_in_set = []
    release_data = None
    log.info("url: %s",url)
    r = request(url)
    html = get_html(r)
    try:
        game_area_dlc_bubble = html.cssselect('div.game_area_dlc_bubble')[0]
        type = 'dlc'
    except IndexError:
        try:
            game_area_purchase_game_wrapper = html.cssselect('div.game_area_purchase_game_wrapper')[0]
            type = 'game'
        except IndexError:
            type = 'set'

    print("Тип:", type)
    if ((type != 'game') and (isFirst)):
        if(type =='dlc'):
            dlc_url.append(url)
            count_games = count_games + 1
            log.info('Добавление в dlc. Количество: %s', len(dlc_url))
        elif(type == 'set'):
            set_url.append(url)
            count_games = count_games + 1
            log.info('Добавление в set. Количество: %s', len(set_url))
    else:
        game_area_details = html.cssselect('#category_block>div>a')
        for details in game_area_details:
            if ((details.text != "Steam собирает информацию об этой игре ") and (
                    details.text != 'Steam собирает информацию об этом дополнительном контенте ')):
                game_features.append(details.text)
        print("Особенности", game_features)

        if (type == 'dlc'):
            game_main = game_area_dlc_bubble.cssselect('div.content>p>a')[0].text.strip()
            print("Главная игра:", game_main)

        if((type == 'game') or (type == 'dlc')):

            apphub_AppName = html.cssselect('div.apphub_AppName')[0]
            name = apphub_AppName.text.strip()
            print("Имя: ",name)
            try:
                image_temp = []
                image_url = html.cssselect('img.game_header_image_full')[0].get('src')
                image_temp.append(image_url)
                image_temp.append("main")
                images.append(image_temp)
            except IndexError as e:
                print()

            highlight_strip_scroll = html.cssselect("#highlight_strip_scroll")[0]
            images_list = highlight_strip_scroll.cssselect('div.highlight_strip_screenshot>img')
            for image in images_list:
                image_temp = []

                image_src = image.get('src')
                image_temp.append(image_src)
                image_temp.append('small')
                images.append(image_temp)

                image_temp = []
                image_src = image_src.replace('.116x65', '')
                image_temp.append(image_src)
                image_temp.append('full')
                images.append(image_temp)

            tags_list = html.cssselect('div.glance_tags>a')
            for tag in tags_list:
                tags.append(tag.text.strip())
            print('Метки:', tags)




            try:
                table_language = html.cssselect('table.game_language_options')[0]
                trs = table_language.cssselect('tr')[1:]

                for tr in trs:
                    languages_temp = []
                    for index, td in enumerate(tr.cssselect('td')):
                        if (index == 0):
                            languages_temp.append(td.text.strip())
                        else:
                            try:
                                image = td.cssselect('img')[0]
                                languages_temp.append(True)
                            except:
                                languages_temp.append(False)
                    languages.append(languages_temp)
            except:
                print()
            print(languages)



            try:
                game_area_purchase_platform_span = html.cssselect('div.game_area_purchase_platform')[0].cssselect(
                    'span')
            except:
                game_area_purchase_platform_span = None

            if (game_area_purchase_platform_span != None):
                for game_platform in game_area_purchase_platform_span:
                    platform = game_platform.get('class')
                    platform = platform.replace('platform_img ', '')
                    if (platform == 'win'):
                        platforms.append('Windows')
                    elif (platform == 'mac'):
                        platforms.append('Mac OS')
                    elif (platform == 'linux'):
                        platforms.append('Linux')
                    elif (platform == 'htcvive'):
                        platforms.append('HTC Vive')
                    elif (platform == 'oculusrift'):
                        platforms.append('Oculus Rift')
                    elif (platform == 'hmd_separator'):
                        print('пропуск')
                    else:
                        platform_errors.append(platform)
                print('Платформы:', platforms)




                block_content_inner = html.cssselect('div.block_content_inner')[0]

                genres = [genre_list.text for genre_list in
                          block_content_inner.cssselect('div.details_block:first-child > a')]
                for genre in genres:
                    if (genre == 'Ранний доступ'):
                        early_access = True
                        print('Ранний доступ:', early_access)
                        genres.remove(genre)
                        break

                print('Жанры:', genres)




            try:
                user_reviews = html.cssselect('div.user_reviews')[0]
            except:
                user_reviews = None
            try:
                release_data = user_reviews.cssselect('div.release_date>div.date')[0].text

            except:
                release_data = None
            print("Дата релиза:", release_data)

            try:
                developers_list = user_reviews.cssselect('#developers_list>a')
                for developer_list in developers_list:
                    developers.append(developer_list.text)
            except:
                developers = []
            print("Разработчик:", developers)

            try:
                publishers_list = user_reviews.cssselect('div.dev_row')[1].cssselect('div.summary>a')

                for publisher_list in publishers_list:
                    publishers.append(publisher_list.text)
            except:
                publishers = None
            print("Издатель:", publishers)

        elif (type == 'set'):
            name = html.cssselect('div.page_title_area>h2')[0].text
            print(name)



            app_in_set = html.cssselect('div.tab_item ')
            for app in app_in_set:
                apps_in_set.append(app.get('data-ds-appid'))

            print('ID app, включенных в SET:',apps_in_set)

            details_block_p = html.cssselect('div.game_details>div>div.details_block>p')[0]

            children = [items for items in details_block_p.iterchildren()]

            for index, value in enumerate(children):
                if(value.text == 'Жанр:'):
                    i = index
                    while True:
                        i = i + 1
                        print(i)
                        if(children[i].tag != 'a'):
                            break

                        genres.append(children[i].text.strip())
                elif(value.text =='Разработчик:'):
                    i = index
                    while True:
                        i = i + 1
                        if (children[i].tag != 'a'):
                            break
                        developers.append(children[i].text.strip())

                elif(value.text =='Издатель:'):
                    i = index
                    while True:
                        i = i + 1
                        if (children[i].tag != 'a'):
                            break
                        publishers.append(children[i].text.strip())
                elif(value.text == 'Дата выхода:'):
                    release_data = children[index + 1].text
                    print('Дата выхода:',release_data)






            print('Жанры:', genres)
            print('Разработчик:', developers)
            print('Издатель:', publishers)

        #Добавление в БД
    count_succes = count_succes + 1
    log.info("Количество спарсенных %s/%s - %s",str(count_succes), count_games, str(count_succes*100/count_games))





def print_html(html):
    print(lxml.html.tostring(html, pretty_print=True, encoding='utf-8').decode('utf-8'))

def get_html_json(r):
    return lxml.html.fromstring(r)

def start_parse_list_games():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parse_list_games, list_games):
            pass
#
def start_parse_games():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parse_game, url_games):
            pass

def start_parse_dlc():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parse_game, dlc_url):
            pass

def start_parse_set():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parse_game, set_url):
            pass

if __name__ == "__main__":
    log.info('start')

    start_main = time.time()
    parse_url_list_games()    #1 поток
    #
    # # list_games.append("https://store.steampowered.com/search/?sort_by=Released_DESC&tags=-1&category1=996%2C998")
    start_parse_list_games()

    # url_games.append("https://store.steampowered.com/app/737040/Warhammer_Vermintide_2__Collectors_Edition_Upgrade/")
    # url_games.append("https://store.steampowered.com/app/485460/The_Banner_Saga_3/")
    # url_games.append("https://store.steampowered.com/sub/259129/")
    # # url_games.append("https://store.steampowered.com/app/517210/Bad_Pad/")
    count_games = len(url_games)
    start_parse_games()
    isFirst = False

    start_parse_dlc()
    start_parse_set()
    #
    # platform_errors = list(set(platform_errors))
    # for error in platform_errors:
    #     print(error)


    #
    # log.info('end')
    # log.info("Время работы парсера: %s",time.time()-start_main)

