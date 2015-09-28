# -*- coding: utf-8 -*-

import pymongo
import csv
import re

# Имя базы данных
DB_NAME = 'change-price-sauna-test'

# Предобработка csv файлов
FILENAME = 'price/'+'01_eos_1-4.csv'
ARTICLE = 1
PRICE = 4

# Подключение к базе. Не забыть прокинуть SSH туннель,
# если MongoDB не на локальной машине.
client = pymongo.MongoClient('localhost', 27017)
db = client[DB_NAME]


# Функция, которая очищает поле цены от символов.
def onlynum(val):
    result = re.findall('(\d+)', val)
    result = ''.join(result)
    return result


# Создаем словарь из двух полей, артикула и цены.
def makedic(FILENAME, ARTICLE, PRICE):
    with open(FILENAME, 'rb') as f:
        reader = csv.reader(f, dialect='excel', delimiter=';')
        mydict = {rows[ARTICLE]: onlynum(rows[PRICE]) for rows in reader}
        return mydict

maindict = makedic(FILENAME, ARTICLE, PRICE)

# Отладка.
# for k in maindict:
#     v = maindict[k]
#     print k, v


# Здесь начинаем брать кажду строку из csv и искать артикуль в базе.
for k in maindict:
    # Длинный RAW запрос. Ищет соответствие поля и
    # в вывод идет только id и этот артикул
    checkart = db.card.find({'properties': {'$elemMatch': {'article': str(k)}}}, {'_id': 1, 'properties.$.price': 1})

    # Костылек, потому что если не указать for,
    # будет просто cursor. Проникаем внутрь запроса.
    for i in checkart:
        # Определяем название товара.
        id_of_card = i['_id']

        # Условие для того, что бы не вызывало ошибку. когда нет цены.
        # Первый в списке, '0', указываем потому что
        # там будет только один элемент. И так сойдет :)
        if 'price' in i['properties'][0]:
            # Определяет значение цены, которое в базе MongoDB на данный момент.
            price_in_base = i['properties'][0]['price']

            # Если цены не совпадают, то меняем запись в базе.
            if str(price_in_base) != str(maindict[k]):
                print id_of_card+u' Нужная цена: '+maindict[k]+' '+u'Цена в базе: '+str(price_in_base)+u' Изменяем.'
                db.card.update({'_id': id_of_card, 'properties.article':str(k)},{'$set': {'properties.$.price': int(maindict[k])}})

                # Отладка
                # print i
                # print id_of_card
                # print str(k)
                # print maindict[k]

            # Если цены совпадают выводим в консоль сообщение
            elif str(price_in_base) == str(maindict[k]):
                print u'Цена та же: '+i['_id']
                # Этот запрос раскомичивать не надо, потому что по
                # факту цены одинаковые. Раскоммитить только если по каким-то
                # причинам надо перезаписать.В моем случае,
                # я случайно перезаписал все в str, а лучше оставить всё в int

                # db.card.update({'_id': id_of_card, 'properties.article':str(k)},{'$set': {'properties.$.price': int(maindict[k])}})

            # Если ошибка
            else:
                print 'Error! Something go wrong.'

        # Случай, когда у товара нет ещё цены в базе.
        # Просто добавляем тем же способом.
        else:
            print u'Добавление цены товару: '+i['_id']
            db.card.update({'_id': id_of_card, 'properties.article':str(k)},{'$set': {'properties.$.price': int(maindict[k])}})
