# -*- coding: utf-8 -*-

import pymongo
import csv
import re

client = pymongo.MongoClient('localhost', 27017)
db = client['testsauna']

card = db.card


# Предобработка csv файлов
FILENAME = 'test.csv'
ARTICLE = 1
PRICE = 4


def onlynum(val):
    # Убирает из строчки все посторонние штуки, и оставляет
    # только цифры, соединяя их.
    result = re.findall('(\d+)', val)
    result = ''.join(result)
    return result


def makedic(FILENAME, ARTICLE, PRICE):
    # Создает словарь из двух полей, артикула и цены.
    with open(FILENAME, 'rb') as f:
        reader = csv.reader(f, dialect='excel', delimiter=';')
        mydict = {rows[ARTICLE]: onlynum(rows[PRICE]) for rows in reader}
        return mydict

# Отладочная часть
maindict = makedic(FILENAME, ARTICLE, PRICE)
# for k in maindict:
#     v = maindict[k]
#     print k, v

# Здесь начинаем брать кажду строку из csv и искать артикуль в базе
for k in maindict:
    checkart = card.find({'properties': {'$elemMatch': {'article': str(k)}}}, {'_id': 1, 'properties': 1})
    # Костылек, потому что если не указать фор, будет просто cursor
    for i in checkart:
        # Условие для того, что бы не вызывало ошибку. когда нет цены.
        if 'price' in i['properties'][0]:
            # Определяет значение цены, которое в базе
            price_in_base = i['properties'][0]['price']
            id_of_card = i['_id']
            # Если цены не совпадают
            if str(price_in_base) != str(maindict[k]):
                print 'Нужная цена: '+maindict[k]+' '+'Цена в базе: '+str(price_in_base)
            # Если цены совпадают
            elif str(price_in_base) == str(maindict[k]):
                print 'Цена та же!'
            # Если ошибка
            else:
                print 'чет не то'
        # Случай, когда у товара нет ещё цены в базе
        else:
            print u'............У товара: '+i['_id']+u' нет цены'

# Что бы апдейтнуть
# db.card.update({'_id': 'Thermat', 'properties.article':'944822'},{'$set': {'properties.$.price': 888888888888}})