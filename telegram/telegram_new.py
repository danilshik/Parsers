# -*- coding: utf-8 -*-
import logging
from telethon import TelegramClient, utils, sync, errors
from telethon.tl.types import PeerUser, PeerChat
from telethon import functions, types
import pandas as pd
import time
import re

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

api_id = 510183                  # API ID (получается при регистрации приложения на my.telegram.org)
api_hash = "deafc7e8b314702bdefc032177ad74c9"              # API Hash (оттуда же)
phone_number = "+79872487132"    # Номер телефона аккаунта, с которого будет выполняться код

output_filename_excel = "project_for_export_no_formulas_31_10_18.xlsx"
output_filename_txt = "number.txt"


def load_excel(output_filename):
    names_canal = []
    data = pd.read_excel(output_filename, 'Projects', dtype=str)
    for item in data["Telegram link"]:
        if(item.find("https://telegram.me/share") != -1):
            continue
        if(item == "https://t.me/uquid?utm_source=website"):
            continue
        if((item.find("https://t.me") != -1) or (item.find("https://telegram.me")!= -1) or (item.find("https://tele.click") != -1)):
            if(item.find("joinchat") != -1):
                continue
            if item != "nan":
                if(item.find("@") != -1):
                    item = item.replace("@", "")
                #Убираем крайний справа /
                text_search = re.search("\/$", item)
                if (text_search != None):
                    index = item.rfind("/")
                    item = item[:index]
                if(item == "https://t.me/rixfoundation Rix"):
                    continue
                index = item.rfind("/")
                print(item , "@"+ item[index + 1:])
                names_canal.append("@"+ item[index + 1:])

    return names_canal


def main():

    canals = load_excel(output_filename_excel)
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    canals = ["@BlockchainSchoolRu"]
    for canal in canals:
        try:
            # entity = client.get_entity(canal)
            # print(entity)
            result = client(functions.channels.GetFullChannelRequest(
                channel=canal
            ))
            print(result.stringify())
        except errors.FloodWaitError:
            print("Задержка")
        except ValueError:
            print("Не найден пользователь")
        except errors.UsernameInvalidError:
            print("Не найден пользователь")



        # for message in client.iter_messages(canal):
        #     print(utils.get_display_name(message.sender) + ":", message.message)


    client.disconnect()

if __name__ == '__main__':
    start = time.time()
    main()
    log.info("Время работы: %s", time.time() - start)