# import asyncio

# from app.modules.db import db
from app.modules.db.config_db import USER_COLLECTION
from app.constants import BUS, TRAMWAY, TAXI


async def check_user(user_id, chat_id):
    id_list = []
    for cursor in USER_COLLECTION.find({}, {'_id': 1}):
        for i in cursor.values():
            id_list.append(i)
    if user_id not in id_list:
        USER_COLLECTION.insert_one(
            {
                '_id': user_id,
                'chat_id': chat_id,
                'bus': [],
                'tramway': [],
                'taxi': []
            }
            )


async def add_favourites(user_id, user_data):
    transport = user_data['TRANSPORT_STATE']
    route_number = user_data['ROUTES_STATE']
    transport_add = ''
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


async def get_numbers_favourites(user_id):
    favourites_list = []
    favourites_bus_list = [BUS, []]
    favourites_tramway_list = [TRAMWAY, []]
    favourites_taxi_list = [TAXI, []]
    for favourites_route in USER_COLLECTION.find({'_id': user_id}):
        if favourites_route.setdefault('bus'):
            favourites_bus_list[1] += favourites_route['bus']
        if favourites_route.setdefault('tramway'):
            favourites_tramway_list[1] += favourites_route['tramway']
        if favourites_route.setdefault('taxi'):
            favourites_taxi_list[1] += favourites_route['taxi']
    favourites_list.append(favourites_bus_list)
    favourites_list.append(favourites_tramway_list)
    favourites_list.append(favourites_taxi_list)
    return favourites_list


async def check_favourites(user_id, choice_transport, choice_number):
    list_check_favourites = []
    for favourites_route in USER_COLLECTION.find({'_id': user_id}):
        if choice_transport == BUS:
            list_check_favourites += favourites_route.get('bus')
        elif choice_transport == TRAMWAY:
            list_check_favourites += favourites_route.get('tramway')
        else:
            list_check_favourites += favourites_route.get('taxi')
    if choice_number not in list_check_favourites:
        return True


async def delete_routes(user_id, message):
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
