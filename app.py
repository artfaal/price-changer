# -*- coding: utf-8 -*-

import pymongo
import csv
import re

client = pymongo.MongoClient('localhost', 27017)
db = client['testsauna']

card = db.card


# Предобработка csv файлов
FILENAME = '02_lux_0-5.csv'
ARTICLE = 0
PRICE = 5


def onlynum(val):
    # Убирает из строчки все посторонние штуки, и оставляет
    # только цифры, соединяя их.
    result = re.findall('(\d+)', val)
    result = ''.join(result)
    return result


def makedic(FILENAME, ARTICLE, PRICE):
    # Создает словарь из двух полей, артикула и цены.
    with open('price/'+FILENAME, 'rb') as f:
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
    checkart = db.card.find({'properties': {'$elemMatch': {'article': str(k)}}}, {'_id': 1, 'properties.$.price': 1})
    # Костылек, потому что если не указать фор, будет просто cursor
    for i in checkart:
        # Условие для того, что бы не вызывало ошибку. когда нет цены.
        if 'price' in i['properties'][0]:
            # Определяет значение цены, которое в базе
            price_in_base = i['properties'][0]['price']
            id_of_card = i['_id']
            # Если цены не совпадают
            if str(price_in_base) != str(maindict[k]):
                print 'Нужная цена: '+maindict[k]+' '+'Цена в базе: '+str(price_in_base)+u'Изменяем.'
                # print i
                # print id_of_card
                # print str(k)
                # print maindict[k]

                # db.card.update({'_id': id_of_card, 'properties.article':str(k)},{'$set': {'properties.$.price': int(maindict[k])}})
            # Если цены совпадают
            elif str(price_in_base) == str(maindict[k]):
                print u'Цена та же: '+i['_id']
                # db.card.update({'_id': id_of_card, 'properties.article':str(k)},{'$set': {'properties.$.price': int(maindict[k])}})
            # Если ошибка
            else:
                print 'чет не то'
        # Случай, когда у товара нет ещё цены в базе
        else:
            id_of_card = i['_id']
            # db.card.update({'_id': id_of_card, 'properties.article':str(k)},{'$set': {'properties.$.price': int(maindict[k])}})
            print u'Добавление цены товару: '+i['_id']

# Что бы апдейтнуть
# db.card.update({'_id': 'Thermat', 'properties.article':'944822'},{'$set': {'properties.$.price': 888888888888}})

# Для теста в промте монго
# db.card.update({_id: 'Thermat', 'properties.article':'944821'},{'$set': {'properties.$.price': 123123123)}})
# Вот идеально работает
# db.card.update({'_id': 'Thermat', 'properties.article':'944820'},{'$set': {'properties.$.price': 'sdfsdfsdfsdf'}})

# ffff = db.card.find({'properties': {'$elemMatch': {'article': '944820'}}}, {'_id': 1, 'properties.$.price': 1})