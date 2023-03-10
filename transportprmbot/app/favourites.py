# import asyncio

# from app.modules.db import db
from app.modules.db.config_db import USER_COLLECTION
from app.constants import BUS, TRAMWAY, TAXI


async def add_user(user_id, chat_id):
    ids = []
    for cursor in USER_COLLECTION.find({}, {'_id': 1}):
        for i in cursor.values():
            ids.append(i)
    if user_id not in ids:
        USER_COLLECTION.insert_one(
            {
                '_id': user_id,
                'chat_id': chat_id,
                'bus': [],
                'tramway': [],
                'taxi': []
            }
            )


async def add_routes(user_id, user_data):
    transport = user_data['TRANSPORT_STATE']
    route_number = user_data['ROUTES_STATE']
    if transport == BUS:
        transport_add = 'bus'
    elif transport == TRAMWAY:
        transport_add = 'tramway'
    else:
        transport_add = 'taxi'
    USER_COLLECTION.update_one(
        {'_id': user_id},
        {'$addToSet': {transport_add: route_number}}
        )
    return ('Добавлено!')


async def get_route_numbers(user_id):
    favourites = []
    buses = [BUS, []]
    trams = [TRAMWAY, []]
    taxi = [TAXI, []]
    for routes in USER_COLLECTION.find({'_id': user_id}):
        if routes.setdefault('bus'):
            buses[1] += routes['bus']
        if routes.setdefault('tramway'):
            trams[1] += routes['tramway']
        if routes.setdefault('taxi'):
            taxi[1] += routes['taxi']
    favourites.append(buses)
    favourites.append(trams)
    favourites.append(taxi)
    return favourites


async def get_favorites_data(user_id, transport, number):
    favourites = []
    for f_route in USER_COLLECTION.find({'_id': user_id}):
        if transport == BUS:
            favourites += f_route.get('bus')
        elif transport == TRAMWAY:
            favourites += f_route.get('tramway')
        else:
            favourites += f_route.get('taxi')
    if number not in favourites:
        return True


async def delete_favorites_routes(user_id, message):
    if message['DELETE_TYPE_FAVOURITES_STATE'] == BUS:
        transport = 'bus'
    elif message['DELETE_TYPE_FAVOURITES_STATE'] == TRAMWAY:
        transport = 'tramway'
    else:
        transport = 'taxi'
    route_numbers = message['DELETE_ROUTE_FAVOURITES_STATE'].split(', ')
    collection_find = USER_COLLECTION.find_one(
                {'_id': user_id},
                {'_id': 0, transport: 1}
            )
    if set(route_numbers).issubset(collection_find[transport]):
        USER_COLLECTION.update_one(
            {'_id': user_id},
            {'$pullAll': {transport: route_numbers}}
        )
        text = 'Удалено!'
    else:
        text = 'Введен номер маршрута, которого нет в избранных!'
    return text
