from bs4 import BeautifulSoup
import requests
import MySQLdb

url_site="https://www.gismeteo.ru"
url_main="https://www.gismeteo.ru/catalog/russia"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
urls_phone = []
test=[]
region=subsubject=subject_region=None
country="Россия"
def regions():
    global region, subject_region,subsubject, country, country_id, region_id
    #Подключение к БД
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="project")
        conn.set_character_set('utf8')
        cursor = conn.cursor()
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        conn.autocommit(True)
        sql="""SELECT id from country WHERE name=%s"""
        param=(country,)
        cursor.execute(sql,param)
        row=cursor.fetchone()
        try:
            country_id=row[0]
            print("Cтрана"+country+" уже существует в бд под номером "+str(country_id))
        except TypeError:
            print("Отсутствует страна")
            sql = """INSERT INTO country (name) VALUES (%s)"""
            cursor.execute(sql, param)
            country_id = cursor.lastrowid
            print("Добавление страны"+country+" под номером "+str(country_id))
    except MySQLdb.Error as err:
        print("Ошибка соединения {}".format(err))

    r = requests.get(url_main, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(r.content, 'lxml')
    catalog_side=soup.find("div", "catalog_sides").contents[0]
    catalog_list=catalog_side.find_all("div","catalog_list")
    for catalog_list in catalog_list:
        catalog_item=catalog_list.find_all("div","catalog_item")
        for catalog_item in catalog_item:
            global region
            region_a=catalog_item.find("a")
            region_link=url_site+region_a.get("href")
            region=region_a.get_text().strip()
            try:
                #Проверка наличия региона в БД
                sql = """SELECT id from region WHERE name=%s"""
                param = (region,)
                cursor.execute(sql, param)
                row = cursor.fetchone()
                try:
                    region_id = row[0]
                    print("Регион "+region," уже существует в бд под номером "+str(region_id))
                except TypeError:
                    print("Отсутствует регион")
                    #Добавление региона
                    sql = """INSERT INTO region (name, country_id) VALUES (%s,%s)"""
                    data=[(region, country_id)]
                    cursor.executemany(sql, data)
                    region_id = cursor.lastrowid
                    print("Регион " + region, "в бд добавился под номером" + str(region_id))
            except MySQLdb.Error as err:
                print("Ошибка соединения {}".format(err))
            #Переход на города и районы региона
            r=requests.get(region_link, headers={'User-Agent': user_agent})
            soup1=BeautifulSoup(r.content, 'lxml')
            region_catalog_side = soup1.find("div", "catalog_sides").contents[0]
            region_catalog_list=region_catalog_side.find_all("div","catalog_list")
            for region_catalog_list in region_catalog_list:
                region_catalog_item=region_catalog_list.find_all("div","catalog_item")
                for region_catalog_item in region_catalog_item:
                    subject_region_a = region_catalog_item.find("a")  #Субъект региона : город или район
                    subject_region_link=url_site+subject_region_a.get("href")
                    subject_region=subject_region_a.get_text().strip()
                    try:
                        # Добавление административной территориальной единицы
                        sql = """INSERT INTO region_atu (name, region_id) VALUES (%s,%s)"""
                        data = [(subject_region, region_id)]
                        cursor.executemany(sql, data)
                        subject_region_id = cursor.lastrowid
                        print("Административно-территориальная единица "+subject_region+" добавлена в бд под номером "+str(subject_region_id))
                    except MySQLdb.Error as err:
                        print("Ошибка соединения {}".format(err))

                    r = requests.get(subject_region_link, headers={'User-Agent': user_agent})
                    soup2 = BeautifulSoup(r.content, 'lxml')
                    catalog_sides = soup2.find("div", "catalog_sides")
                    catalog_list = catalog_sides.find_all("div", "catalog_list")
                    for catalog_list in catalog_list:
                        subsubjects=catalog_list.find_all("a")                             #села, деревни в районе
                        for subsubjects in subsubjects:
                            if(len(subsubjects.contents)==1):
                                subsubject=subsubjects.get_text().strip()
                                try:
                                    sql = """INSERT INTO nasal (name, region_atu_id) VALUES (%s,%s)"""
                                    data = [(subsubject, subject_region_id)]
                                    cursor.executemany(sql, data)
                                    subsubject_id = cursor.lastrowid
                                    print("Населенный пункт " + subsubject + " добавлен в бд под номером " + str(subsubject_id))


                                except MySQLdb.Error as err:
                                    print("Ошибка соединения {}".format(err))
                                subsubject = None
                    subject_region =None
            region =None

if __name__ == "__main__":
    regions()