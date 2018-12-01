import time
from bs4 import BeautifulSoup
import requests
import math
import httplib2
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import MySQLdb

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
count_thread=20

# главная ссылка
mainUrl = "https://www.kimovil.com/ru/compare-smartphones/page."

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
urls_phone = []  # спиоск ссылок на телефоны

type_request = "add"


proxies = {
    "http": "217.30.254.118:3130",
    "https": "217.30.254.118:3130",
}


def request_id_category(parametr):
    sql = """SELECT id from category where name = %s"""
    data = [(parametr,)]
    id_category = select_request_db(sql, data)
    if(len(id_category)==1):
        return id_category[0]
    else:
        exit(0)


def request(url):
    while True:
        try:
            r = requests.get(url, headers={'User-Agent': user_agent})
            if r.status_code != 200:
                log.info("Ошибка, Код ответа: %s", r.status_code)
                time.sleep(1)
                continue
            else:
                return r
        except Exception as e:
            log.info("Ошибка ConnectionError")
            time.sleep(1)

def convert_boolean(param):
    if(param==True):
        return 1
    if(param==False):
        return 0

def change_user_agent():
    global user_agent
    user_agent = UserAgent().chrome

def get_html(request):
    return BeautifulSoup(request.content, 'lxml')

def lookup():
    url_id = 1
    while True:
        global user_agent
        current_time_list_phone = time.time()
        # Загружаем страницу
        url = mainUrl + str(url_id)
        # r=requests.get(url,headers={'User-Agent':user_agent},proxies=proxies)
        r = request(url)
        soup = get_html(r)
        a_phone = soup.find_all("a", {"class": "result-info"})
        if (a_phone == []):
            break
        for href in a_phone:
            link = href.get("href")
            urls_phone.append(link)
            print(link)
        log.info("  %s | Время прогрузки раздела: %s", url_id, time.time() - current_time_list_phone)
        url_id += 1



def request_db(sql,data):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="project")
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    conn.autocommit(True)
    cursor.executemany(sql, data)
    last_row_id = cursor.lastrowid
    conn.close()
    return last_row_id

def select_request_db(sql,data):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="project")
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    conn.autocommit(True)
    cursor.executemany(sql, data)
    row = cursor.fetchall()
    conn.close()

    text = list(sum(row, ()))
    return text






def parsing_phone(url):
    name =  phone_version = material = name_alternative = brand = represented = state = width = height = thickness = ratio_side = weight = surface_use = certificate_resistance = diagonal = display_type = display_subtype = count_pixels_x = count_pixels_y = density_pixels = display_capacitive = multitouch = display_25d_surved_glass = display_brightness = display_protective_glass = forcetouch = display_ogs = display_scratch_resistance = display_oleophobic_lipophobic_coating = display_ltps = display_zero_air_gap = display_triluminos = display_xReality = display_contrast_ratio = always_on_display = processor_model = processor_CPU = processor_count_core = processor_frequency = processor_64_bits = graphics_GPU = ram = antutu = rom = rom_expandable = fingerprint = fingerprint_location = accelerometer = compas = sensor_gravity = gyroscope = sensor_hall = magnetometer = pedometer = sensor_light = sensor_proximity = led_notification = camera_resolution = camera_sensor = camera_sensor_type = camera_opening = video_4K = camera_autofocus = camera_serial_shooting = camera_digital_zoom = camera_exposure_ompensation = camera_face_detection = camera_geographic_tags = camera_hdr_shooting = camera_setting_ISO = camera_manual_focus = camera_optical_stabilization = camera_panoramic_shooting = camera_RAW = camera_scene_mode = camera_selftimer = camera_touch_focus = camera_settings_balance_white = camera_video_slow_motion = camera_video_slow_motion_fps = camera_video_optical_stabilization = camera_frontal_resolution = net_4G = net_4G_frequency = net_3G_frequency = net_2G_frequency = sim_card_count = sim_card_modework = sim_card_type = WIFI_support_standart = WIFI_mode_dualBand = WIFI_Direct = WIFI_Display = WIFI_Hotspot = WIFI_MiMO = bluetooth_version = bluetooth_LE = bluetooth_mode_A2DP = bluetooth_mode_AVRCP = bluetooth_mode_GAP = bluetooth_mode_GAVDP = bluetooth_mode_HDP = bluetooth_mode_HFP = bluetooth_mode_HID = bluetooth_mode_HSP = bluetooth_mode_MAP = bluetooth_mode_OPP = bluetooth_mode_PAN = bluetooth_mode_PBAP_PAB = bluetooth_mode_SPP = satellite_nafigation_AGPS = satellite_nafigation_Beidou = satellite_nafigation_Glonass = satellite_nafigation_GPS = satellite_nafigation_Galileo = usb_charging = usb_host = usb_mass_charger = usb_OTG = usb_type_C = audio_jack = FM_Radio = computer_synchronization = DLNA = infrared_port = NFS = OTA_synchronization = tethering = VoLTE = battery_capacity = battery_type = battery_fast_charging = battery_withdral = operation_system = None

    colors = []
    print("Начало парсинга",url)
    time_parsing = time.time()
    r = requests.get(url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(r.content, "lxml")

    # Нахождение и определение ссылки на изображение
    imagening = soup.find("img", "main-photo")["src"]
    name_image = imagening.split("/")[-1]
    print(name_image)
    url_image = "https:" + imagening
    timeParsingImage = time.time()
    # Скачивание изображения
    h = httplib2.Http('../../cache')
    response, content = h.request(url_image)
    out = open('../../image/smartphone/' + name_image, 'wb')
    out.write(content)
    out.close()
    
    timeDownloadImage = time.time() - timeParsingImage
    print("Время загрузки изображения:", timeDownloadImage)
    image_path = "image/smartphone/" + name_image
    print("Путь изображения:", image_path)

    # Блок basics
    basics = soup.find("div", "description", "clear")

    h1Basics = basics.find("h1")
    # ---------------------------------------------------------------------------------
    name = h1Basics.contents[2].strip()
    if(name.rfind("+")):
        name = name.replace("+"," Plus")
    if(name.find("(")!=-1):
        name=name.replace("(","")
    if (name.find(")") != -1):
        name = name.replace(")", "")
    print("Название телефона:", name)

    if(basics.find("div","other-devices-list-version")!=None):
        list_other_devices=basics.find("div","other-devices-list-version")
        list_other_devices_list_item_active=list_other_devices.find("li","item active",)
        phone_version=list_other_devices_list_item_active.contents[0].contents[0].string.strip()
        print("Версия продукта", phone_version)


    div_main=soup.find("div", {"id": "device-profile"})
    mainBlock = div_main.find_all("section", "clear")
    mainBlock.remove(mainBlock[-1])  # Удаляем последнюю секцию сравнения
    print(len(mainBlock))
    for block in mainBlock:
        nameBlock = block["id"]
        tableBlock = block.find("div", "table")
        sectionTableBlock = tableBlock.find_all("div", "row")
        for sectionTableBlock in sectionTableBlock:
            nameSection = sectionTableBlock.contents[1].contents[1].contents[0].string.strip()
            dlSection = sectionTableBlock.find("dl")
            if (dlSection != None):
                dtSection_all = dlSection.find_all("dt")
                i = 1
                for dtSection in dtSection_all:
                    parametr = dlSection.contents[i].get_text().strip()
                    if ((dlSection.contents[i + 2].name == "dt") or (dlSection.contents[
                                                                         i + 2].get_text() == "")):  # Обработка ошибки отсутсвия значения в строке Тип для ссылки https://www.kimovil.com/ru/where-to-buy-sony-xperia-xzs
                        # 2 условие для dl, где всего 1 пара значений dt dd,где dd присутствует, но у когорого нет значения, видимо из-за пропуска в базе данных
                        variantAnswer = None
                        answer = None
                        i = i - 2
                    else:
                        answer = dlSection.contents[i + 2]
                        variantAnswer = answer.contents[0].string.strip()
                    # Раздел O
                    if (nameBlock == "about"):
                        # Раздел Бренд
                        if (nameSection == "Бренд"):
                            if (parametr == "Бренд"):
                                brand = variantAnswer
                                print(parametr + ": ", brand)
                            if (parametr == "Другие названия"):
                                if ((variantAnswer == "") or (variantAnswer == " ")):
                                    name_alternative = None
                                else:
                                    text_name_alternative = answer.contents
                                    name_alternative = ""
                                    for test in text_name_alternative:
                                        test = test.string.strip()
                                        name_alternative = name_alternative + test
                                    name_alternative = name_alternative.replace(",", ", ")

                                print("Альтернативное название" + ": ", name_alternative)
                        if (nameSection == "Представление"):
                            # Представление
                            if (parametr == "Представлено"):
                                represented = variantAnswer[:-1]
                                print(parametr + ": " + represented)
                            if (parametr == "Состояние"):
                                state = variantAnswer
                                print(parametr + ": " + state)
                    if (nameBlock == "design"):
                        # Подраздел Структура
                        if (nameSection == "Структура"):
                            if (parametr == "Размер"):
                                width = variantAnswer
                                print("Ширина:", width)
                                height = answer.contents[2][3:].strip()
                                print("Высота:", height)
                                thickness = answer.contents[4][3:].strip()
                                print("Толщина:", thickness)
                            if (parametr == "Соотношение сторон"):
                                ratio_side = variantAnswer
                                print(parametr + ": " + ratio_side)
                            if (parametr == "Вес"):
                                weight = variantAnswer
                                print("Вес:", weight)
                            if (parametr == "Поверхность использования"):
                                surface_use = variantAnswer
                                print(parametr + ": " + surface_use)
                            if (parametr == "Материалы"):
                                materials = answer.contents
                                material = ""
                                for test in materials:
                                    test = test.string.strip()
                                    if (test.find("алюминиевый") != -1):
                                        test = test.replace("алюминиевый сплав","Алюминий")
                                    if (test.find(",") != -1):
                                        test = test.replace(",", ", ")
                                    if (test.find("углеродного") != -1):
                                        test = "Углеродные волокна"
                                    material = material + test
                                print(parametr + ": ", material)
                            if (parametr == "Сертификат сопротивления (пыль, Вода)"):
                                certificate_resistance = variantAnswer
                                print(parametr + ": " + certificate_resistance)
                            if (parametr == "Цвета"):
                                colors_answer = answer
                                print(colors_answer)
                                for color in colors_answer.find_all("div", "color-sep"):
                                    color = color.contents[1].string.strip()
                                    color = color.capitalize()
                                    if(color.find("Rose-gold")!=-1):
                                        color="Розовое золото"
                                    colors.append(color)
                                print("Цвет", colors)

                        # Подраздел Экран
                        if (nameSection == "Экран"):
                            if (parametr == "Диагональ"):
                                diagonal = variantAnswer[:-1]
                                print(parametr + ": " + diagonal)
                            if (parametr == "Тип"):
                                display_type = variantAnswer
                                print(parametr + ": ", display_type)
                                if (variantAnswer != None):
                                    if (len(answer) == 2):
                                        if (answer.contents[
                                            1].string != None):  # Заглушка для пустого span, пример https://www.kimovil.com/ru/where-to-buy-lenovo-k900
                                            display_subtype = answer.contents[1].string.strip()
                                            print("Подтип экрана:", display_subtype)
                            if (parametr == "Разрешение"):
                                indexX = variantAnswer.find("x")
                                count_pixels_x = variantAnswer[:indexX - 1]
                                print("Количество пикселей по горизонтали:", count_pixels_x)
                                count_pixels_y = variantAnswer[indexX + 2:]
                                print("Количество пикселей по вертикали:", count_pixels_y)
                                density_pixels = math.sqrt(int(count_pixels_x) ** 2 + int(count_pixels_y) ** 2) / float(diagonal)
                                print("Плотность точек:", density_pixels)
                            if (parametr == "Другие"):
                                other = answer
                                for other in other.find_all("span", "item"):
                                    other = other.contents[0].strip()
                                    if (other != ""):
                                        if (other == "Ёмкостный"):
                                            display_capacitive = 1

                                            print("Емкостный дисплей:", display_capacitive)
                                        if (other == "Мультитач"):
                                            multitouch = 1
                                            print("Мультитач:", multitouch)
                                        if (other == "Экран из гнутого стекла 2.5D"):
                                            display_25d_surved_glass = 1
                                            print("Экран из гнутого стекла 2.5D:", display_25d_surved_glass
                                                  )
                                        if (other.find("cd/m2") != -1):
                                            indexC = other.find("cd/m2")
                                            display_brightness = other[:indexC - 1]
                                            display_brightness = int(display_brightness)
                                            print("Яркость экрана:", display_brightness)
                                        if ((other.find("Glass") != -1) or (other.find("glass") != -1)):
                                            print(other.find("от компании"))
                                            if (other == "Dragontrail glass"):
                                                display_protective_glass = "Dragontrail Glass"
                                            else:
                                                if ((other.find("Gorilla") != -1) and (other.find("от компании") != -1)):
                                                    indexOT = other.find("от компании")
                                                    indexGorilla = other.find("Gorilla")
                                                    display_protective_glass = other[indexGorilla:indexOT - 1]
                                            print("Защитное стекло:", display_protective_glass)
                                        if (other == "Форстач"):
                                            forcetouch = 1
                                            print("Force Touch (3D Touch):", forcetouch)
                                        if ((other.find("OGS") != -1) or (other == "Full Lamination Technology")):
                                            display_ogs = 1
                                            print("OGS (One Glass Solution):", display_ogs)
                                        if (other == "Устойчивость к царапинам"):
                                            display_scratch_resistance = 1
                                            print("Устойчивость к царапинам", display_scratch_resistance)
                                        # if (other.find("NTSC")!=-1):
                                        #     displayntsc=1
                                        #     print("Цветовое простанство NTSC:",ntsc)
                                        #     if(other.find("%")!=-1):
                                        #         indexNTSC=other.find("NTSC")
                                        #         countNts=other[:indexNTSC-1]
                                        #         print("Количество NTSC:",countNts)
                                        if (other == "Oleophobic (lipophobic) coating"):
                                            display_oleophobic_lipophobic_coating = 1
                                            print("Олеофобное (липофобное покрытие:", display_oleophobic_lipophobic_coating)
                                        if (other.find("LTPS") != -1):
                                            display_ltps = 1
                                            print("LTPS", display_ltps)
                                        if (other == "Zero Air Gap technology"):
                                            display_zero_air_gap = 1
                                            print("Zero Air Gap technology:", display_zero_air_gap)
                                        if (other.find("Triluminos") != -1):
                                            display_triluminos = 1
                                            print("Triluminos display:", display_triluminos)
                                        if (other.find("X-Reality") != -1):
                                            display_xReality = 1
                                            print("X-Reality:", display_xReality)
                                        if (other.find("Степень контрастности") != -1):
                                            display_contrast_ratio = other[21:]
                                            print("Степень контрастности:", display_contrast_ratio)
                                        if (other == "Always-On Display"):
                                            always_on_display = 1
                                            print("Always-On Display:", always_on_display)

                                            # Раздел мощность и оборудование
                    # Подраздел процессор
                    if (nameBlock == "hardware"):
                        if (nameSection == "Процессор"):
                            if (parametr == "Модель"):
                                processor_model = variantAnswer
                                print(parametr + ": " + processor_model)
                            if (parametr == "CPU"):
                                processor_CPU = variantAnswer
                                if (processor_CPU == ""):
                                    processor_CPU = None
                                print(parametr + ": ", processor_CPU)
                            if (parametr == "Тип"):
                                if (variantAnswer == "Single-Core"):
                                    processor_count_core = 1
                                if (variantAnswer == "Dual-Core"):
                                    processor_count_core = 2
                                if (variantAnswer == "Quad-Core"):
                                    processor_count_core = 4
                                if (variantAnswer == "Hexa-Core"):
                                    processor_count_core = 6
                                if (variantAnswer == "Octa-Core"):
                                    processor_count_core = 8
                                if (variantAnswer == "Deca-Core"):
                                    processor_count_core = 10
                                print("Количество ядер:", processor_count_core)
                            if (parametr == "Частота"):
                                processor_frequency = variantAnswer
                                print(parametr + ": " + processor_frequency)
                            if (parametr == "64 Bits"):
                                bool64Bits = variantAnswer
                                processor_64_bits = bool64Bits == "Да"
                                processor_64_bits = convert_boolean(processor_64_bits)
                                print(parametr + ":", processor_64_bits)
                            # Подраздел графики
                        if (nameSection == "Графика"):
                            if (parametr == "GPU"):
                                graphics_GPU = variantAnswer
                                print(parametr + ": ", graphics_GPU)
                            # Подраздел RAM
                        if (nameSection == "RAM"):
                            if (parametr == "RAM"):
                                ram = variantAnswer
                                unit_ram = answer.contents[1].string.strip()
                                if (unit_ram == "GB"):
                                    ram = float(ram) * 1024
                                print(parametr + ": " + str(ram))
                            # Подраздел Antutu
                        if (nameSection == "Antutu"):
                            if (parametr == "Оценка"):
                                antutu = answer.contents[0].string.strip()
                                antutu = float(antutu) * 1000
                                print("Antutu: ", antutu)
                            # Подраздел хранение
                        if (nameSection == "Хранение"):
                            if (parametr == "Вместимость"):
                                rom = variantAnswer
                                rom = float(rom) * 1024
                                print(parametr + ": " + str(ram))
                            if (parametr == "Возможность расширения? (Слот SD)"):
                                boolExpansionMemory = variantAnswer
                                rom_expandable = boolExpansionMemory == "Да"
                                rom_expandable = convert_boolean(rom_expandable)
                                print(parametr + ": ", rom_expandable)
                            # Подраздел безопасность
                        if (nameSection == "Безопасность"):
                            if (parametr == "Отпечатки пальцев"):
                                if (len(variantAnswer) != 3):
                                    indexComma = variantAnswer.find(",")
                                    fingerprint = variantAnswer[:indexComma] == "Да"
                                    fingerprint = convert_boolean(fingerprint)
                                    fingerprint_location = variantAnswer[indexComma + 2:]
                                    if (fingerprint_location == "на передней"):
                                        fingerprint_location == "спереди"
                                    print("Расположение панели отпечатков пальцев:", fingerprint_location)
                                else:
                                    fingerprint = 0
                                print(parametr + ":", fingerprint)

                            # Подраздел Сенсоры
                        if (nameSection == "Сенсоры"):
                            if (parametr == "Акселерометр"):
                                accelerometer = variantAnswer == "Да"
                                accelerometer = convert_boolean(accelerometer)
                                print("Акселерометр:", accelerometer)
                            if (parametr == "Компас"):
                                compas = variantAnswer == "Да"
                                compas = convert_boolean(compas)
                                print("Компас:", compas)
                            if (parametr == "Датчик гравитации"):
                                sensor_gravity = variantAnswer == "Да"
                                sensor_gravity = convert_boolean(sensor_gravity)
                                print("Датчик гравитации:", sensor_gravity)
                            if (parametr == "Гироскоп"):
                                gyroscope = variantAnswer == "Да"
                                gyroscope = convert_boolean(gyroscope)
                                print("Гироскоп:", gyroscope)
                            if (parametr == "Hall"):
                                sensor_hall = variantAnswer == "Да"
                                sensor_hall = convert_boolean(sensor_hall)
                                print("Датчик Холла:", sensor_hall)
                            if (parametr == "Магнетометр"):
                                magnetometer = variantAnswer == "Да"
                                magnetometer = convert_boolean(magnetometer)
                                print("Магнетометр:", magnetometer)
                            if (parametr == "шагометр"):
                                pedometer = variantAnswer == "Да"
                                pedometer = convert_boolean(pedometer)
                                print("Шагометр:", pedometer)
                            if (parametr == "Датчик освещения"):
                                sensor_light = variantAnswer == "Да"
                                sensor_light = convert_boolean(sensor_light)
                                print("Датчик освещения:", sensor_light)
                            if (parametr == "Датчик приближения"):
                                sensor_proximity = variantAnswer == "Да"
                                sensor_proximity = convert_boolean(sensor_proximity)
                                print("Датчик приближения:", sensor_proximity)
                            # Подраздел Прочее в оборудовании
                        if (nameSection == "Прочее"):
                            if (parametr == "Уведомления LED"):
                                led_notification = variantAnswer
                                if (led_notification == "Нет"):
                                    led_notification = 0
                                else:
                                    if (led_notification.find("Цвет") != -1):
                                        led_notification = led_notification.replace("Цвет", "Цветное")

                                print(parametr + ": ", led_notification)
                    if (nameBlock == "camera"):
                        if (nameSection == "Главная"):
                            if (parametr == "Разрешение"):
                                camera_resolution = variantAnswer
                                print("Разрешение камеры:", camera_resolution)
                            if (parametr == "Сенсор"):
                                camera_sensor = variantAnswer
                                if (camera_sensor.find("Unknown") != -1):
                                    camera_sensor = None
                                print("Сенсор камеры:", camera_sensor)
                            if (parametr == "Тип"):
                                camera_sensor_type = variantAnswer
                                if (camera_sensor_type.find("Unknown") != -1):
                                    camera_sensor_type = None
                                print("Тип сенсора камеры:", camera_sensor_type)
                            if (parametr == "Открытие"):
                                camera_opening = answer.contents[2].string.strip()
                                if (camera_opening.find("known") != -1):
                                    camera_opening = None
                                else:
                                    if (camera_opening.find(",") != -1):
                                        camera_opening = camera_opening.replace(",", ".")
                                    if (camera_opening.find(".") != -1):
                                        index = camera_opening.find(".")
                                        camera_opening = camera_opening[index - 1:index + 2]
                                        camera_opening = float(camera_opening)
                                    if (camera_opening == "?"):
                                        camera_opening = None

                                print("Открытие:", str(camera_opening))
                            if (parametr == "Вспышка"):
                                flashCamera = variantAnswer
                                print("Вспышка камеры:", flashCamera)
                            if (parametr == "Особенности"):
                                features = answer
                                for features in features.find_all("span", "item"):
                                    featuresCamera = features.contents[0].strip()
                                    if (featuresCamera == "4K видео"):
                                        video_4K = 1
                                        print("Видео в разрешении 4К:", video_4K)
                                    if (featuresCamera == "Автофо́кус"):
                                        camera_autofocus = 1
                                        print("Автофокус:", camera_autofocus)
                                    if (featuresCamera == "Серийная съемка"):
                                        camera_serial_shooting = 1
                                        print("Cерийная съемка:", camera_serial_shooting)
                                    if (featuresCamera == "Цифровой зум"):
                                        camera_digital_zoom = 1
                                        print("Цифровой зум:", camera_digital_zoom)
                                    if (featuresCamera == "Компенсация экспозиции"):
                                        camera_exposure_ompensation = 1
                                        print("Компенсация экспозиции:", camera_exposure_ompensation)
                                    if (featuresCamera == "Распознавание лиц"):
                                        camera_face_detection = 1
                                        print(featuresCamera + ": ", camera_face_detection)
                                    if (featuresCamera == "Географические метки"):
                                        camera_geographic_tags = 1
                                        print(featuresCamera + ": ", camera_geographic_tags)
                                    if (featuresCamera == "HDR съёмка"):
                                        camera_hdr_shooting = 1
                                        print(featuresCamera + ": ", camera_hdr_shooting)
                                    if (featuresCamera == "Настройка ISO"):
                                        camera_setting_ISO = 1
                                        print(featuresCamera + ": ", camera_setting_ISO)
                                    if (featuresCamera == "Manual focus"):
                                        camera_manual_focus = 1
                                        print("Ручной фокус: ", camera_manual_focus)
                                    if (featuresCamera == "Оптическая стабилизация"):
                                        camera_optical_stabilization = 1
                                        print(featuresCamera + ": ", camera_optical_stabilization)
                                    if (featuresCamera == "Оптическая стабилизация изображения"):
                                        opticalStabilizationImage = 1
                                        print(featuresCamera + ": ", opticalStabilizationImage)
                                    if (featuresCamera == "Панорамная съёмка"):
                                        camera_panoramic_shooting = 1
                                        print(featuresCamera + ": ", camera_panoramic_shooting)
                                    if (featuresCamera == "RAW"):
                                        camera_RAW = 1
                                        print(featuresCamera + ": ", camera_RAW)
                                    if (featuresCamera == "Scene mode"):
                                        camera_scene_mode = 1
                                        print("Режим сцены: ", camera_scene_mode)
                                    if (featuresCamera == "Автоспуск"):
                                        camera_selftimer = 1
                                        print(featuresCamera + ": ", camera_selftimer)
                                    if (featuresCamera == "Сенсорная фокусировка"):
                                        camera_touch_focus = 1
                                        print(featuresCamera + ": ", camera_touch_focus)
                                    if (featuresCamera == "White balance settings"):
                                        camera_settings_balance_white = 1
                                        print("Баланс белого и серого: ", camera_settings_balance_white)

                            if (parametr == "Видео Замедленная съемка"):
                                camera_video_slow_motion = variantAnswer == "Да"
                                camera_video_slow_motion = convert_boolean(camera_video_slow_motion)
                                print(parametr + ": ", camera_video_slow_motion)
                                if (variantAnswer == "Да"):
                                    camera_video_slow_motion_fps = answer.contents[1].string.strip()
                                    camera_video_slow_motion_fps = camera_video_slow_motion_fps[2:-4]
                                    print("Количество кадров замедленной съемки:", camera_video_slow_motion_fps)
                            if (parametr == "Оптическая стабилизация"):
                                camera_video_optical_stabilization = variantAnswer == "Да"
                                camera_video_optical_stabilization = convert_boolean(camera_video_optical_stabilization)
                                print("Оптическая стабилизация:", camera_video_optical_stabilization)
                            # Подраздел Селфи
                        if (nameSection == "Селфи"):
                            camera_frontal_resolution = variantAnswer
                            print("Разрешение Селфи:", camera_frontal_resolution)
                    if (nameBlock == "connectivity"):
                        if (nameSection == "сеть"):
                            if (parametr == "4G LTE"):
                                net_4G = 1
                                print("Поддержка 4G:", net_4G)
                                net_4G_frequency = answer.get_text()[:-4]
                                net_4G_frequency = ' '.join(net_4G_frequency.split())
                                print(parametr + ": " + net_4G_frequency)
                            if (parametr == "3G"):
                                net_3G_frequency = answer.get_text()[:-4]
                                net_3G_frequency = ' '.join(net_3G_frequency.split())
                                print(parametr + ": " + net_3G_frequency)
                            if (parametr == "2G"):
                                net_2G_frequency = answer.get_text()[:-4]
                                net_2G_frequency = ' '.join(net_2G_frequency.split())
                                print(parametr + ": " + net_2G_frequency)
                            # Подраздел Sim-карта
                        if (nameSection == "SIM-карта"):
                            answer.p.decompose()
                            sim_text = answer.get_text().strip()
                            if (sim_text.find("SIM") != -1):
                                Sim = sim_text.split()
                                if (Sim[0] == "Single"):
                                    sim_card_count = 1
                                if (Sim[0] == "Dual"):
                                    sim_card_count = 2
                                if (Sim[0] == "Triple"):
                                    sim_card_count = 3
                                print("Количество SIM-карт:", sim_card_count)
                                if (len(Sim) >= 4):
                                    sim_card_modework = Sim[2] + " " + Sim[3]
                                    print("Режим работы SIM-карт:", sim_card_modework)
                                print(len(Sim))
                                if (sim_text.find("(") != -1):
                                    index = sim_text.find("(")
                                    sim_card_type = sim_text[index + 1:-1]
                                    print(sim_card_type)

                        # Подраздел Wifi
                        if (nameSection == "Wi-fi"):
                            if (parametr == "Поддерживаемые стандарты"):
                                WIFI_support_standart = answer.get_text()
                                WIFI_support_standart = ' '.join(WIFI_support_standart.split())
                                print("Поддерживаемые стандарты:", WIFI_support_standart)
                            if (parametr == "Прочее"):
                                otherWifi = answer
                                for otherWifi in otherWifi.find_all("span", "item"):
                                    supportWifi = otherWifi.contents[0].strip()
                                    if (supportWifi == "Dual band"):
                                        WIFI_mode_dualBand = 1
                                        print("Режим Dual Band:", WIFI_mode_dualBand)
                                    if (supportWifi == "Wi-Fi Direct"):
                                        WIFI_Direct = 1
                                        print("Режим Wi-Fi Direct:", WIFI_Direct)
                                    if (supportWifi == "Wi-Fi Display"):
                                        WIFI_Display = 1
                                        print("Режим Wi-Fi Display:", WIFI_Display)
                                    if (supportWifi == "Wi-Fi Hotspot"):
                                        WIFI_Hotspot = 1
                                        print("Режим Wi-Fi Hotspot:", WIFI_Hotspot)
                                    if (supportWifi == "Wi-Fi MiMO"):
                                        WIFI_MiMO = 1
                                        print("Режим Wi-Fi MiMO", WIFI_MiMO)
                            # Подраздел Bluetooth
                        if (nameSection == "Bluetooth"):
                            if (parametr == "Версия"):
                                bluetooth_version = variantAnswer
                                bluetooth_version = ' '.join(bluetooth_version.split())
                                if (bluetooth_version[len(bluetooth_version) - 2:] == "LE"):
                                    bluetooth_version = bluetooth_version[:-2]
                                    bluetooth_LE = 1
                                    print("Bluetooth LE:", bluetooth_LE)
                                print("Версия Bluetooth:", bluetooth_version)
                            if (parametr == "Режимы"):
                                modeBluetooth = answer
                                for modeBluetooth in modeBluetooth.find_all("span", "item"):
                                    modeBluetooth = modeBluetooth.contents[0].strip()
                                    if (modeBluetooth == "A2DP"):
                                        bluetooth_mode_A2DP = 1
                                        print("Режим A2DP:", bluetooth_mode_A2DP)
                                    if (modeBluetooth == "AVRCP"):
                                        bluetooth_mode_AVRCP = 1
                                        print("Режим AVRCP:", bluetooth_mode_AVRCP)
                                    if (modeBluetooth == "GAP"):
                                        bluetooth_mode_GAP = 1
                                        print("Режим GAP:", bluetooth_mode_GAP)
                                    if (modeBluetooth == "GAVDP"):
                                        bluetooth_mode_GAVDP = 1
                                        print("Режим GAVDP:", bluetooth_mode_GAVDP)
                                    if (modeBluetooth == "HDP"):
                                        bluetooth_mode_HDP = 1
                                        print("Режим HDP:", bluetooth_mode_HDP)
                                    if (modeBluetooth == "HFP"):
                                        bluetooth_mode_HFP = 1
                                        print("Режим HFP:", bluetooth_mode_HFP)
                                    if (modeBluetooth == "HID"):
                                        bluetooth_mode_HID = 1
                                        print("Режим HID:", bluetooth_mode_HID)
                                    if (modeBluetooth == "HSP"):
                                        bluetooth_mode_HSP = 1
                                        print("Режим HSP:", bluetooth_mode_HSP)
                                    if (modeBluetooth == "MAP"):
                                        bluetooth_mode_MAP = 1
                                        print("Режим MAP:", bluetooth_mode_MAP)
                                    if (modeBluetooth == "OPP"):
                                        bluetooth_mode_OPP = 1
                                        print("Режим OPP:", bluetooth_mode_OPP)
                                    if (modeBluetooth == "PAN"):
                                        bluetooth_mode_PAN = 1
                                        print("Режим PAN:", bluetooth_mode_PAN)
                                    if (modeBluetooth == "PBAP/PAB"):
                                        bluetooth_mode_PBAP_PAB = 1
                                        print("Режим PBAP/PAB:", bluetooth_mode_PBAP_PAB)
                                    if (modeBluetooth == "SPP"):
                                        bluetooth_mode_SPP = 1
                                        print("Режим SPP:", bluetooth_mode_SPP)

                            # Подраздел спутниковая навигация
                        if (nameSection == "Спутниковая навигация"):
                            supportSatelliteNavigation = answer.get_text()
                            supportSatelliteNavigation = supportSatelliteNavigation.replace(",", "")
                            supportSatelliteNavigation = ' '.join(supportSatelliteNavigation.split())
                            supportSatelliteNavigation = supportSatelliteNavigation.split()
                            for satteliteNavigation in supportSatelliteNavigation:
                                if (satteliteNavigation == "A-GPS"):
                                    satellite_nafigation_AGPS = 1
                                    print("A-GPS:", satellite_nafigation_AGPS)
                                if (satteliteNavigation == "Бэйдоу"):
                                    satellite_nafigation_Beidou = 1
                                    print("Бэйдоу:", satellite_nafigation_Beidou)
                                if (satteliteNavigation == "ГЛОНАСС"):
                                    satellite_nafigation_Glonass = 1
                                    print("Глонасс:", satellite_nafigation_Glonass)
                                if (satteliteNavigation == "GPS"):
                                    satellite_nafigation_GPS = 1
                                    print("GPS:", satellite_nafigation_GPS)
                                if (satteliteNavigation == "Galileo"):
                                    satellite_nafigation_Galileo = 1
                                    print("GPS:", satellite_nafigation_Galileo)
                            # Подраздел USB
                        if (nameSection == "USB"):
                            if ((parametr == "Зарядка") and (variantAnswer == "Да")):
                                usb_charging = 1
                                print(parametr + ": ", usb_charging)
                            if ((parametr == "Хост") and (variantAnswer == "Да")):
                                usb_host = 1
                                print(parametr + ": ", usb_host)
                            if ((parametr == "Массовое ЗУ") and (variantAnswer == "Да")):
                                usb_mass_charger = 1
                                print(parametr + ": ", usb_mass_charger)
                            if ((parametr == "USB на ходу (OTG)") and (variantAnswer == "Да")):
                                usb_OTG = 1
                                print(parametr + ": ", usb_OTG)
                            if ((parametr == "USB Тип C") and (variantAnswer == "Да")):
                                usb_type_C = 1
                                print(parametr + ": ", usb_type_C)
                            # Подсекция прочее
                        if (nameSection == "Прочее"):
                            if ((parametr == "Audio Jack") and (variantAnswer == "Да")):
                                audio_jack = 1
                                print(parametr + ":", audio_jack)
                            if ((parametr == "FM-радио") and (variantAnswer == "Да")):
                                FM_Radio = 1
                                print(parametr + ":", FM_Radio)
                            if ((parametr == "Computer sync") and (variantAnswer == "Да")):
                                computer_synchronization = 1
                                print(parametr + ":", computer_synchronization)
                            if ((parametr == "DLNA") and (variantAnswer == "Да")):
                                DLNA = 1
                                print(parametr + ":", DLNA)
                            if ((parametr == "Infrared") and (variantAnswer == "Да")):
                                infrared_port = 1
                                print(parametr + ": ", infrared_port)
                            if ((parametr == "NFC") and (variantAnswer == "Да")):
                                NFS = 1
                                print(parametr + ":", NFS)
                            if ((parametr == "OTA sync") and (variantAnswer == "Да")):
                                OTA_synchronization = 1
                                print(parametr + ":", OTA_synchronization)
                            if ((parametr == "Tethering") and (variantAnswer == "Да")):
                                tethering = 1
                                print(parametr + ":", tethering)
                            if ((parametr == "VoLTE") and (variantAnswer == "Да")):
                                VoLTE = 1
                                print(parametr + ": ", VoLTE)
                    if (nameBlock == "battery"):
                        # Подраздел батареи
                        if (nameSection == "Аккумулятор"):
                            if (parametr == "Емкость"):
                                battery_capacity = variantAnswer
                                print("Емкость батареи:", battery_capacity)
                            if (parametr == "Тип"):
                                battery_type = variantAnswer
                                if (battery_type == "Unknown"):
                                    battery_type = None
                                print("Тип батареи", battery_type)
                            if (parametr == "Прочее"):
                                otherBattery = answer
                                if (len(otherBattery) == 5):
                                    fastChargingBattery = otherBattery.contents[0].strip()
                                    if (fastChargingBattery == "Быстрая зарядка"):
                                        battery_fast_charging = 1
                                        print("Быстрая зарядка:", battery_fast_charging)
                                    battery_withdral = otherBattery.contents[2].strip()
                                else:
                                    battery_withdral = otherBattery.contents[0].strip()
                                if (battery_withdral == "Несъемный"):
                                    battery_withdral = 0
                                else:
                                    battery_withdral = 1
                                print("Съемность батареи:", battery_withdral)
                    if (nameBlock == "software"):
                        if (nameSection == "программное обеспечение"):
                            if (parametr == "Операционная система"):
                                operation_system = variantAnswer
                                print("Операционная система:", operation_system)

                    i = i + 4
    print("Спарсено: ", url, "-", "Время парсинга страницы",time.time() - time_parsing)

    if(type_request=="add"):
        sql = """INSERT INTO product (material,name, category_id, name_alternative,url,image_path,brand,represented,state,width,height,thickness,ratio_side,weight,surface_use,certificate_resistance,diagonal,display_type,display_subtype,count_pixels_x, count_pixels_y, density_pixels, display_capacitive, multitouch, display_25d_surved_glass, display_brightness, display_protective_glass, forcetouch, display_ogs, display_scratch_resistance, display_oleophobic_lipophobic_coating, display_ltps, display_zero_air_gap, display_triluminos, display_xReality, display_contrast_ratio,always_on_display,
                    processor_model,processor_CPU,processor_count_core, processor_frequency, processor_64_bits, graphics_GPU, ram, antutu, rom, rom_expandable, fingerprint, fingerprint_location, accelerometer, compas, sensor_gravity, gyroscope, sensor_hall, magnetometer, pedometer, sensor_light, sensor_proximity, led_notification, camera_resolution, camera_sensor, camera_sensor_type, camera_opening, video_4K,camera_autofocus, camera_serial_shooting,camera_digital_zoom, camera_exposure_ompensation,camera_face_detection, camera_geographic_tags, camera_hdr_shooting,
                    camera_setting_ISO, camera_manual_focus, camera_optical_stabilization, camera_panoramic_shooting, camera_RAW, camera_scene_mode, camera_selftimer, camera_touch_focus, camera_settings_balance_white, camera_video_slow_motion, camera_video_slow_motion_fps, camera_video_optical_stabilization, camera_frontal_resolution, net_4G, net_4G_frequency,net_3G_frequency, net_2G_frequency, sim_card_count, sim_card_modework, sim_card_type, WIFI_support_standart, WIFI_mode_dualBand, WIFI_Direct, WIFI_Display, WIFI_Hotspot, WIFI_MiMO, bluetooth_version, bluetooth_LE,
                    bluetooth_mode_A2DP, bluetooth_mode_AVRCP, bluetooth_mode_GAP, bluetooth_mode_GAVDP, bluetooth_mode_HDP, bluetooth_mode_HFP, bluetooth_mode_HID, bluetooth_mode_HSP, bluetooth_mode_MAP, bluetooth_mode_OPP, bluetooth_mode_PAN, bluetooth_mode_PBAP_PAB, bluetooth_mode_SPP, satellite_nafigation_AGPS, satellite_nafigation_Beidou, satellite_nafigation_Glonass, satellite_nafigation_GPS, satellite_nafigation_Galileo, usb_charging, usb_host, usb_mass_charger, usb_OTG, usb_type_C, audio_jack, FM_Radio, computer_synchronization, DLNA, infrared_port, NFS, OTA_synchronization,
                    tethering, VoLTE, battery_capacity, battery_type, battery_fast_charging, battery_withdral, operation_system)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        data = [(material, name, category_id, name_alternative, url, image_path, brand, represented, state, width, height, thickness, ratio_side, weight,
                 surface_use, certificate_resistance, diagonal, display_type, display_subtype, count_pixels_x, count_pixels_y, density_pixels,
                 display_capacitive, multitouch, display_25d_surved_glass, display_brightness, display_protective_glass, forcetouch, display_ogs,
                 display_scratch_resistance, display_oleophobic_lipophobic_coating, display_ltps, display_zero_air_gap, display_triluminos,
                 display_xReality, display_contrast_ratio, always_on_display,
                 processor_model, processor_CPU, processor_count_core, processor_frequency, processor_64_bits, graphics_GPU, ram, antutu, rom,
                 rom_expandable, fingerprint, fingerprint_location, accelerometer, compas, sensor_gravity, gyroscope, sensor_hall, magnetometer,
                 pedometer, sensor_light, sensor_proximity, led_notification, camera_resolution, camera_sensor, camera_sensor_type, camera_opening,
                 video_4K, camera_autofocus, camera_serial_shooting, camera_digital_zoom, camera_exposure_ompensation, camera_face_detection,
                 camera_geographic_tags, camera_hdr_shooting,
                 camera_setting_ISO, camera_manual_focus, camera_optical_stabilization, camera_panoramic_shooting, camera_RAW, camera_scene_mode,
                 camera_selftimer, camera_touch_focus, camera_settings_balance_white, camera_video_slow_motion, camera_video_slow_motion_fps,
                 camera_video_optical_stabilization, camera_frontal_resolution, net_4G, net_4G_frequency, net_3G_frequency, net_2G_frequency,
                 sim_card_count, sim_card_modework, sim_card_type, WIFI_support_standart, WIFI_mode_dualBand, WIFI_Direct, WIFI_Display, WIFI_Hotspot,
                 WIFI_MiMO, bluetooth_version, bluetooth_LE,
                 bluetooth_mode_A2DP, bluetooth_mode_AVRCP, bluetooth_mode_GAP, bluetooth_mode_GAVDP, bluetooth_mode_HDP, bluetooth_mode_HFP,
                 bluetooth_mode_HID, bluetooth_mode_HSP, bluetooth_mode_MAP, bluetooth_mode_OPP, bluetooth_mode_PAN, bluetooth_mode_PBAP_PAB,
                 bluetooth_mode_SPP, satellite_nafigation_AGPS, satellite_nafigation_Beidou, satellite_nafigation_Glonass, satellite_nafigation_GPS,
                 satellite_nafigation_Galileo, usb_charging, usb_host, usb_mass_charger, usb_OTG, usb_type_C, audio_jack, FM_Radio,
                 computer_synchronization, DLNA, infrared_port, NFS, OTA_synchronization,
                 tethering, VoLTE, battery_capacity, battery_type, battery_fast_charging, battery_withdral, operation_system)]
        product_id = request_db(sql, data)
        print("product_id", product_id)
        for color in colors:
            sql = """INSERT INTO product_variantion(product_id, version,color) VALUES (%s, %s, %s)"""
            data = [(product_id, phone_version,  color)]
            product_variantion_id = request_db(sql, data)
    if(type_request=="update"):
        sql = """UPDATE product SET name = %s, material = %s, category_id = %s, name_alternative = %s,  image_path = %s, brand = %s, represented = %s, state = %s, width = %s, height = %s, thickness = %s, ratio_side = %s, weight = %s, surface_use = %s, certificate_resistance = %s, diagonal = %s, display_type = %s, display_subtype = %s, count_pixels_x = %s,  count_pixels_y = %s,  density_pixels = %s,  display_capacitive = %s,  multitouch = %s,  display_25d_surved_glass = %s,  display_brightness = %s,  display_protective_glass = %s,  forcetouch = %s,  display_ogs = %s,  display_scratch_resistance = %s,  display_oleophobic_lipophobic_coating = %s,  display_ltps = %s,  display_zero_air_gap = %s,  display_triluminos = %s,  display_xReality = %s,  display_contrast_ratio = %s, always_on_display = %s, 
                            processor_model = %s, processor_CPU = %s, processor_count_core = %s,  processor_frequency = %s,  processor_64_bits = %s,  graphics_GPU = %s,  ram = %s,  antutu = %s,  rom = %s,  rom_expandable = %s,  fingerprint = %s,  fingerprint_location = %s,  accelerometer = %s,  compas = %s,  sensor_gravity = %s,  gyroscope = %s,  sensor_hall = %s,  magnetometer = %s,  pedometer = %s,  sensor_light = %s,  sensor_proximity = %s,  led_notification = %s,  camera_resolution = %s,  camera_sensor = %s,  camera_sensor_type = %s,  camera_opening = %s,  video_4K = %s, camera_autofocus = %s,  camera_serial_shooting = %s, camera_digital_zoom = %s,  camera_exposure_ompensation = %s, camera_face_detection = %s,  camera_geographic_tags = %s,  camera_hdr_shooting = %s, 
                            camera_setting_ISO = %s,  camera_manual_focus = %s,  camera_optical_stabilization = %s,  camera_panoramic_shooting = %s,  camera_RAW = %s,  camera_scene_mode = %s,  camera_selftimer = %s,  camera_touch_focus = %s,  camera_settings_balance_white = %s,  camera_video_slow_motion = %s,  camera_video_slow_motion_fps = %s,  camera_video_optical_stabilization = %s,  camera_frontal_resolution = %s,  net_4G = %s,  net_4G_frequency = %s, net_3G_frequency = %s,  net_2G_frequency = %s,  sim_card_count = %s,  sim_card_modework = %s,  sim_card_type = %s,  WIFI_support_standart = %s,  WIFI_mode_dualBand = %s,  WIFI_Direct = %s,  WIFI_Display = %s,  WIFI_Hotspot = %s,  WIFI_MiMO = %s,  bluetooth_version = %s,  bluetooth_LE = %s, 
                            bluetooth_mode_A2DP = %s,  bluetooth_mode_AVRCP = %s,  bluetooth_mode_GAP = %s,  bluetooth_mode_GAVDP = %s,  bluetooth_mode_HDP = %s, bluetooth_mode_HFP = %s,  bluetooth_mode_HID = %s,  bluetooth_mode_HSP = %s,  bluetooth_mode_MAP = %s,  bluetooth_mode_OPP = %s,  bluetooth_mode_PAN = %s,  bluetooth_mode_PBAP_PAB = %s,  bluetooth_mode_SPP = %s,  satellite_nafigation_AGPS = %s,  satellite_nafigation_Beidou = %s,  satellite_nafigation_Glonass = %s,  satellite_nafigation_GPS = %s,  satellite_nafigation_Galileo = %s,  usb_charging = %s,  usb_host = %s,  usb_mass_charger = %s,  usb_OTG = %s,  usb_type_C = %s,  audio_jack = %s,  FM_Radio = %s,  computer_synchronization = %s,  DLNA = %s,  infrared_port = %s,  NFS = %s,  OTA_synchronization = %s, 
                            tethering = %s,  VoLTE = %s,  battery_capacity = %s,  battery_type = %s,  battery_fast_charging = %s,  battery_withdral = %s,  operation_system  = %s  where url = %s"""
        data = [(name, material, category_id,  name_alternative, image_path, brand, represented, state, width, height, thickness, ratio_side, weight,
                 surface_use, certificate_resistance, diagonal, display_type, display_subtype, count_pixels_x, count_pixels_y, density_pixels,
                 display_capacitive, multitouch, display_25d_surved_glass, display_brightness, display_protective_glass, forcetouch, display_ogs,
                 display_scratch_resistance, display_oleophobic_lipophobic_coating, display_ltps, display_zero_air_gap, display_triluminos,
                 display_xReality, display_contrast_ratio, always_on_display,
                 processor_model, processor_CPU, processor_count_core, processor_frequency, processor_64_bits, graphics_GPU, ram, antutu, rom,
                 rom_expandable, fingerprint, fingerprint_location, accelerometer, compas, sensor_gravity, gyroscope, sensor_hall, magnetometer,
                 pedometer, sensor_light, sensor_proximity, led_notification, camera_resolution, camera_sensor, camera_sensor_type, camera_opening,
                 video_4K, camera_autofocus, camera_serial_shooting, camera_digital_zoom, camera_exposure_ompensation, camera_face_detection,
                 camera_geographic_tags, camera_hdr_shooting,
                 camera_setting_ISO, camera_manual_focus, camera_optical_stabilization, camera_panoramic_shooting, camera_RAW, camera_scene_mode,
                 camera_selftimer, camera_touch_focus, camera_settings_balance_white, camera_video_slow_motion, camera_video_slow_motion_fps,
                 camera_video_optical_stabilization, camera_frontal_resolution, net_4G, net_4G_frequency, net_3G_frequency, net_2G_frequency,
                 sim_card_count, sim_card_modework, sim_card_type, WIFI_support_standart, WIFI_mode_dualBand, WIFI_Direct, WIFI_Display, WIFI_Hotspot,
                 WIFI_MiMO, bluetooth_version, bluetooth_LE,
                 bluetooth_mode_A2DP, bluetooth_mode_AVRCP, bluetooth_mode_GAP, bluetooth_mode_GAVDP, bluetooth_mode_HDP, bluetooth_mode_HFP,
                 bluetooth_mode_HID, bluetooth_mode_HSP, bluetooth_mode_MAP, bluetooth_mode_OPP, bluetooth_mode_PAN, bluetooth_mode_PBAP_PAB,
                 bluetooth_mode_SPP, satellite_nafigation_AGPS, satellite_nafigation_Beidou, satellite_nafigation_Glonass, satellite_nafigation_GPS,
                 satellite_nafigation_Galileo, usb_charging, usb_host, usb_mass_charger, usb_OTG, usb_type_C, audio_jack, FM_Radio,
                 computer_synchronization, DLNA, infrared_port, NFS, OTA_synchronization,
                 tethering, VoLTE, battery_capacity, battery_type, battery_fast_charging, battery_withdral, operation_system, url)]
        product_id = request_db(sql, data)
        print("product_id", product_id)

    







def start_parsing_phones():
    with ThreadPoolExecutor(count_thread) as executor:
        for _ in executor.map(parsing_phone, urls_phone):
            pass



if __name__ == "__main__":
    start_main = time.time()

    log.info('start')
    category_id = request_id_category("Смартфон")
    print(category_id)
    type_request="add"
    lookup()

    #urls_phone.append("https://www.kimovil.com/ru/where-to-buy-lg-k10-2017-dual")
    #start_parsing_phones()
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8-plus")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-huawei-nova-2s6gb-128gb-al00")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-innjoo-max4-pro")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s84gb-64gb-g950fd")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8-plus4gb-64gb-g955fd")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-innjoo-fire2-lte")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-bsimb-g30-pro")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8-plus-g955k")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8-g950u")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-google-pixel-2128gb")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8-plus-g955u")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-google-pixel-2")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8-g950k")
    # urls_phone.append("https://www.kimovil.com/ru/where-to-buy-samsung-galaxy-s8")


    #Запрашиваем ссылки с бд
    # sql = """SELECT url FROM product where product_group=%s"""
    # data = [(product_group,)]
    # url_db = select_request_db(sql, data)
    # print("Количество записей в бд",len(url_db))
    # print("Количество записей",len(urls_phone))
    # set_db = set(url_db)
    # set_url = set(urls_phone)   #Текущие ссылки на телефон
    # urls_phone.clear()
    # urls_phone = list(set_url.difference(set_db)) #Разница
    # if(len(urls_phone)>0):
    #     start_parsing_phones()
    #     type_request="update"
    #     if(type_request=="update"):
    #         urls_phone.clear()
    #         urls_phone = list(set_db)
    #         start_parsing_phones()
    start_parsing_phones()
    log.info('end')
    log.info("Время работы парсера: %s", time.time() - start_main)




