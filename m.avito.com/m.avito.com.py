from bs4 import BeautifulSoup
import time
import requests

headers = {'Accept': 'text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}

url_data = "links.txt"

main_url = "https://m.avito.ru/"
def request(url):
    global headers
    while True:
        try:
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print("Ошибка, Код ответа:", r.status_code)
                time.sleep(1)
                continue
            else:
                return r.text
        except Exception as e:
            print("Ошибка ConnectionError", e)
            time.sleep(1)


def get_html (request):
    return BeautifulSoup(request, "lxml")


def load_data(url_data):
    with open(url_data, "r") as file:
        urls = file.read().split("\n")

        return urls

def parsing(url):
    r = request(url)
    html = get_html(r)

    blocks = html.find_all("article", {"class": "b-item js-catalog-item-enum "})
    for block in blocks:
        try:
            image = str(block.find("div", {"class": "item-img "}).find("span").get("style"))
            image = image.replace("background-image: url(","")
            image = "https:"+image.replace(");","")
        except AttributeError:
            image = None


        name = block.find("h3",{"class": "item-header"}).find("span", {"class": "header-text"}).text.strip()


        price = block.find("div", {"class": "item-price"}).find("span", {"class": "item-price-value"}).text.strip()


        item_info = block.find("div", {"class": "item-info"})
        try:
            metro = item_info.find("span", {"class": "info-text info-metro-district"}).text.strip()
        except AttributeError:
            metro = None


        date = block.find("div", {"class": "info-date info-text"}).text.strip()

        a = main_url + str(block.find("a", {"class": "item-link item-link-visited-highlight"})["href"])


        print(name, image, price, metro, date, a)

if __name__ == '__main__':
    start_time = time.time()
    urls = load_data(url_data)
    for url in urls:
        parsing(url)

    print("Время работы скрипта:", time.time() - start_time)